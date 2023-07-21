import platform as platform_
from os import environ
from typing import Dict, List


def parse_command(commands: List[str]) -> str:
    return "-".join(commands).lower()


def parse_language(language: str, config: Dict) -> List[str]:
    """Return language list for page matching.

    If language is specified or configured, use it as only choice.
    Otherwise make the list based on env `LANG` and `LANGUAGE`.
    # pylint: disable=line-too-long
    For detailed logic, see https://github.com/tldr-pages/tldr/blob/main/CLIENT-SPECIFICATION.md#language
    """  # noqa: E501
    language = language or config.get("language", "")
    if language:
        if "_" in language:
            language, country = language.split("_", maxsplit=1)
            return ["_".join((language.lower(), country.upper()))]
        else:
            return [language.lower()]

    def extract(x: str) -> str:
        return x.split("_", maxsplit=1)[0].lower()

    lang = extract(environ.get("LC_ALL", "") or environ.get("LANG", ""))
    if not lang:
        return ["en"]
    languages = [item for item in environ.get("LANGUAGE", "").split(":") if item]
    if lang not in languages:
        languages.append(lang)
    if "en" not in languages:
        languages.append("en")
    return [language.lower() for language in languages]


def parse_platform(platform: str, config: Dict) -> str:
    if platform.lower() not in ["android", "linux", "osx", "macos", "sunos", "windows"]:
        platform = ""
    platform = platform or config.get("platform", "")
    if platform:
        platform = platform.lower()
    else:
        platform = guess_os()
    return "osx" if platform == "macos" else platform


def guess_os():
    system_to_platform = {
        "Linux": "linux",
        "Darwin": "osx",
        "Java": "sunos",
        "Windows": "windows",
        "Android": "android",
    }
    return system_to_platform.get(platform_.system(), "linux")
