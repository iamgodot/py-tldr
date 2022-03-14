from datetime import datetime
from pathlib import Path as LibPath
from zipfile import ZipFile

import requests
from click import secho, style
from requests.exceptions import ConnectionError as ConnectionError_
from requests.exceptions import HTTPError, Timeout


class PageCache:
    """PageCache intends to manage local cache data.

    It provides instant search among downloaded page files, while
    should not have direct interactions with PageFinder.

    Attributes:
        timeout: Number of hours to indicate TTL for cache data.
          Use integer for better understanding, but could be a decimal.
    """

    def __init__(
        self,
        timeout: int,
        location_base: LibPath,
        download_url: str,
        proxy_url: str = None,
    ):
        self.timeout = timeout
        self.location_base = location_base
        self.location = self.location_base / "pages"
        self.download_url = download_url
        self.proxy_url = proxy_url

    def _make_page_file(self, folder: str, name: str) -> LibPath:
        return self.location / folder / (name + ".md")

    def _validate_page_file(self, page_file: LibPath) -> bool:
        if page_file.exists():
            mtime_ts = page_file.lstat().st_mtime
            age = (
                datetime.now() - datetime.fromtimestamp(mtime_ts)
            ).total_seconds() / 3600
            return age <= self.timeout
        return False

    def get(self, name: str, platform: str) -> str:
        res = ""
        for pf in ["common", platform]:
            page_file = self._make_page_file(pf, name)
            if self._validate_page_file(page_file):
                with open(page_file, encoding="utf8") as f:
                    res = f.read()
        return res

    def set(self, name: str, platform: str, content: str):
        (self.location / platform).mkdir(parents=True, exist_ok=True)
        page_file = self._make_page_file(platform, name)
        with open(page_file, "w", encoding="utf8") as f:
            f.write(content)

    def update(self):
        """Download all latest pages."""
        tldr_zip = self.location_base / "tldr.zip"
        try:
            with open(tldr_zip, "wb", encoding="utf8") as f:
                resp = requests.get(
                    self.download_url, proxies={"https": self.proxy_url}, timeout=3
                )
                resp.raise_for_status()
                f.write(resp.content)
        except (ConnectionError_, HTTPError, Timeout):
            # FIXME: Do something useful
            return

        with ZipFile(tldr_zip, "r") as f:
            f.extractall(self.location_base)

        # Remove unnecessary files, like tldr.zip / index.json / LICENSE.md
        tldr_zip.unlink()
        for item in self.location_base.iterdir():
            if item.is_file():
                item.unlink()


class PageFinder:
    """PageFinder is to locate specific entries among tldr pages.

    It tries its best to find a corresponding page answer while is
    retricted to the given language and platform. This means it will
    not change towards other scopes (except `common`) in order to
    find a match.

    Attributes:
        source_url: Indicate where tldr pages are located.
        platform: `common` will be used together with this since tldr
          merges shared entries under it.
    """

    def __init__(
        self, source_url: str, platform: str, language: str = "", proxy_url: str = None
    ):
        self.language = "" if language == "en" else language
        self.source_url = ".".join([source_url, self.language]).strip(".")
        self.platform = platform
        self.proxy_url = proxy_url

    def _make_page_url(self, name: str, platform: str) -> str:
        return "/".join([self.source_url, platform, name + ".md"])

    def _query(self, url: str) -> str:
        proxies = {"https": self.proxy_url}
        result = ""
        try:
            resp = requests.get(url, proxies=proxies, timeout=3)
            resp.raise_for_status()
            result = resp.text
        except (ConnectionError_, HTTPError, Timeout):
            # FIXME: Do something useful
            pass
        return result

    def find(self, name: str) -> dict:
        result = self._query(self._make_page_url(name, "common"))
        for platform in ["common", self.platform]:
            result = self._query(self._make_page_url(name, platform))
            if result:
                return {"name": name, "content": result, "platform": platform}
        return {}


class Formatter:
    """Formatter decides how pages (or other prompts) are displayed.

    Attributes:
        buffer: Content will be split by lines and stored in this list
          before any other operations.
        start_with_new_line: Add extra new line in the begining.

    Methods:
        output: As a class method and should be the only interface to use
          Formatter. Raw content will be processed, rendered and print in
          order before the final result was output.
    """

    def __init__(
        self, content, is_page=False, indent_spaces=0, start_with_new_line=False
    ):
        self.content = content
        self.buffer = []
        self.is_page = is_page
        self.indent_spaces = indent_spaces
        self.start_with_new_line = start_with_new_line

    def process_content(self):
        for line in self.content.split("\n"):
            line = line.strip()
            if self.is_page:
                for sym in ("{{", "}}", "`"):
                    line = line.replace(sym, "")
            self.buffer.append(line)

    def render_text(self, **args):
        rendered_lines = []
        if not self.is_page:
            rendered_lines = [style(line, **args) for line in self.buffer]
        else:
            for line in self.buffer:
                if line == "":
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
                rendered_lines.append(line)
        self.buffer = rendered_lines

    def print(self, value=""):
        secho(f'{" "*self.indent_spaces}{value}')

    @classmethod
    def output(
        cls,
        content,
        indent_spaces=0,
        is_page=False,
        start_with_new_line=False,
        **args,
    ):
        if not isinstance(content, str):
            raise ValueError("Formatter only accept strings")
        if not content:
            return
        formatter = cls(content, is_page, indent_spaces, start_with_new_line)
        formatter.process_content()
        formatter.render_text(**args)
        if formatter.start_with_new_line:
            formatter.print()
        for line in formatter.buffer:
            formatter.print(line)
