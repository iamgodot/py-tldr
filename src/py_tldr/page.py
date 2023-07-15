import json
from datetime import datetime
from http import HTTPStatus
from logging import getLogger
from pathlib import Path as LibPath
from typing import Dict, List, Tuple
from zipfile import ZipFile

import requests
from click import style
from requests.exceptions import ConnectionError as ConnectionError_
from requests.exceptions import HTTPError, Timeout

LOGGER = getLogger(__name__)


class PageCache:
    """PageCache intends to manage local cache data.

    It provides instant search among downloaded page files, while
    should not have direct interactions with PageFinder.

    Attributes:
        timeout: Number of hours to indicate TTL for cache data.
        Could be a decimal.
    """

    def __init__(
        self,
        timeout: float,
        location_base: LibPath,
        download_url: str,
        proxy_url: str = None,
    ):
        self.timeout = timeout
        self.location_base = location_base
        self.location = self.location_base / "pages"
        self.download_url = download_url
        self.proxy_url = proxy_url

    def _make_page_file(self, platform: str, name: str, language: str) -> LibPath:
        postfix_lang = f".{language}" if language != "en" else ""
        return LibPath(str(self.location) + postfix_lang) / platform / (name + ".md")

    def _validate_page_file(self, page_file: LibPath) -> bool:
        if page_file.exists():
            mtime_ts = page_file.lstat().st_mtime
            age = (
                datetime.now() - datetime.fromtimestamp(mtime_ts)
            ).total_seconds() / 3600
            return age <= self.timeout
        return False

    def get(self, name: str, platform: str, language: str = "en") -> str:
        page_file = self._make_page_file(platform, name, language)
        if not self._validate_page_file(page_file):
            return ""
        with open(page_file, encoding="utf8") as f:
            res = f.read()
        return res

    def set(self, name: str, platform: str, content: str, language: str = "en"):
        (self.location / platform).mkdir(parents=True, exist_ok=True)
        page_file = self._make_page_file(platform, name, language)
        with open(page_file, "w", encoding="utf8") as f:
            f.write(content)

    def update(self):
        """Download all latest pages."""
        data = download_data(self.download_url, proxies={"https": self.proxy_url})
        tldr_zip = self.location_base / "tldr.zip"
        with open(tldr_zip, "wb") as f:
            f.write(data)

        with ZipFile(tldr_zip, "r") as f:
            f.extractall(self.location_base)

        # Remove non-page files, such as tldr.zip, index.json and LICENSE.md
        tldr_zip.unlink()
        for item in self.location_base.iterdir():
            if item.is_file():
                item.unlink()

    @property
    def index_file(self) -> LibPath:
        return LibPath(self.location_base) / "index.json"

    def check_index(self) -> bool:
        return self._validate_page_file(self.index_file)

    def update_index(self) -> None:
        """Download newest index.json and restructure it for better searching."""
        data = download_data(
            "https://tldr.sh/assets/index.json", proxies={"https": self.proxy_url}
        )
        index, index_compact = json.loads(data), {}
        for command in index["commands"]:
            index_compact[command["name"]] = {
                "platforms": command["platform"],
                "languages": command["language"],
            }
        with open(self.index_file, "w") as f:
            json.dump(index_compact, f)


class DownloadError(Exception):
    def __init__(self, *args, status_code: int = 0, **kwargs):
        self.status_code = status_code
        super().__init__(*args, **kwargs)


def download_data(url, proxies: dict = None, timeout: int = 3) -> bytes:
    try:
        resp = requests.get(url, proxies=proxies, timeout=timeout)
        resp.raise_for_status()
        return resp.content
    except (ConnectionError_, HTTPError, Timeout) as exc:
        if exc.response is not None:
            err = DownloadError(status_code=exc.response.status_code)
        else:
            err = DownloadError()
        raise err


class PageFinder:
    """PageFinder is to locate specific entries among tldr pages.

    A page finder tries its best to according to the given language
    and platform. This means it will not expand such scope during
    the match process, except `common`, see find() method below.

    Attributes:
        source_url: Indicate where tldr pages are located.
    """

    def __init__(
        self,
        source_url: str,
        cache_timeout: int,
        cache_location: str,
        cache_download_url: str,
        cache_enabled: bool = True,
        proxy_url: str = None,
    ):
        self.source_url = source_url
        self.cache_timeout = cache_timeout
        self.cache_location = cache_location
        self.cache_enabled = cache_enabled
        self.proxy_url = proxy_url
        self.cache = PageCache(
            cache_timeout, cache_location, cache_download_url, proxy_url
        )

    def _make_page_url(self, name: str, platform: str, language: str) -> str:
        postfix_lang = f".{language}" if language != "en" else ""
        return "/".join([self.source_url + postfix_lang, platform, name + ".md"])

    def _query(self, url: str) -> str:
        try:
            LOGGER.debug("Query URL: %s", url)
            data = download_data(url, proxies={"https": self.proxy_url})
        except DownloadError as exc:
            if exc.status_code == HTTPStatus.NOT_FOUND:
                return ""
            raise exc
        return data.decode(encoding="utf8")

    def find(self, name: str, platform: str = "", languages: List[str] = None) -> str:
        """Find page content via local cache and source."""
        if not self.cache.check_index():
            self.cache.update_index()
        LOGGER.debug("Page find for: %s, %s, %s", name, platform, languages)
        name, platform, language = self.search(name, platform, languages)
        if not name or not platform or not language:
            return ""
        LOGGER.debug("Search result: %s, %s, %s", name, platform, language)
        if self.cache_enabled:
            content = self.cache.get(name, platform, language=language)
            if content:
                LOGGER.debug("Cache enabled and hit!")
                return content
        content = self._query(self._make_page_url(name, platform, language)) or ""
        if content and self.cache_enabled:
            self.cache.set(name, platform, content, language=language)
        return content

    def get_index(self) -> Dict:
        with open(self.cache.index_file) as f:
            return json.load(f)

    def search(
        self, name: str, platform: str = "", languages: List[str] = None
    ) -> Tuple[str, str, str]:
        """Search index for the best platform and language for the command."""
        index = self.get_index()
        info = index.get(name)
        if not info:
            return "", "", ""

        platforms = info["platforms"]
        if platform not in platforms:
            platform = "common" if "common" in platforms else platforms[0]

        language = ""
        languages_info = info["languages"]
        for lang in languages:
            if lang in languages_info:
                language = lang
                break
        return name, platform, language

    def sync(self) -> None:
        self.cache.update()
        self.cache.update_index()


class Formatter:
    """Formatter decides how text contents are displayed.

    Methods:
        format: This should be the only method to use a formatter. To each line
            in raw content, it will render and arrange them before returning
            everything in the buffer.
    """

    def __init__(
        self,
        *,
        indent_spaces: int = 0,
        start_with_new_line=False,
    ) -> None:
        self.indent_spaces = indent_spaces
        self.start_with_new_line = start_with_new_line
        self._buffer = []

    def _write(self, line: str) -> None:
        self._buffer.append(line)

    def format(self, content: str) -> str:
        for line in content.strip().split("\n"):  # Keep empty lines
            rendered = self.render(line.strip())
            arranged = self.arrange(rendered)
            self._write(arranged)

        formatted = "".join(self._buffer)
        if self.start_with_new_line:
            formatted = f"\n{formatted}"
        return formatted

    def render(self, line: str) -> str:
        return f"{line}\n"

    def arrange(self, line: str) -> str:
        if not line.strip():
            return line
        return " " * self.indent_spaces + line


class PageFormatter(Formatter):
    def render(self, line: str) -> str:
        # Remove token syntax symbols, check style guide for tldr pages
        # TODO: highlight tokens
        for sym in ("{{", "}}", "`"):
            line = line.replace(sym, "")

        # Render markdown texts
        if not line:
            pass
        elif line[0] == "#":
            line = style(line[2:], bold=True, fg="red")
        elif line[0] == ">":
            line = line[2:].replace("<", "").replace(">", "")
            line = style(line, fg="yellow", underline=True)
        elif line[0] == "-":
            line = style("\u2022" + line[1:], fg="green")
        else:
            line = style("  " + line, fg="magenta")
        return super().render(line)
