from os import environ

import pytest

from py_tldr.parse import parse_command, parse_language, parse_platform


@pytest.mark.parametrize(
    "command, parsed",
    (
        [["git"], "git"],
        [["git", "log"], "git-log"],
        [["git-log"], "git-log"],
        [["apt-get"], "apt-get"],
        [["Git"], "git"],
        [["GIT", "Log"], "git-log"],
        [["gIt-loG"], "git-log"],
    ),
)
def test_parse_command(command, parsed):
    assert parse_command(command) == parsed


@pytest.mark.parametrize(
    "language, config, env_lang, env_language, parsed",
    (
        ["zh", {}, "", "", ["zh"]],
        ["", {"language": "zh"}, "", "", ["zh"]],
        ["", {}, "cz", "it:cz:de", ["it", "cz", "de", "en"]],
        ["", {}, "cz", "it:de:fr", ["it", "de", "fr", "cz", "en"]],
        ["", {}, "it", "", ["it", "en"]],
        ["", {}, "", "it:cz", ["en"]],
        ["", {}, "", "", ["en"]],
        ["ZH", {}, "", "", ["zh"]],
        ["", {"language": "ZH"}, "", "", ["zh"]],
        ["", {}, "Cz", "IT:cz:DE", ["it", "cz", "de", "en"]],
    ),
)
def test_parse_language(language, config, env_lang, env_language, parsed):
    environ["LC_ALL"] = environ["LANG"] = env_lang
    environ["LANGUAGE"] = env_language
    assert parse_language(language, config) == parsed


def test_lang_env_precedence():
    environ.pop("LANGUAGE")
    environ["LC_ALL"] = "zh_CN.GB2312"
    environ["LANG"] = "en_US.UTF-8"
    assert parse_language("", {}) == ["zh", "en"]
    environ.pop("LC_ALL")
    assert parse_language("", {}) == ["en"]


@pytest.mark.parametrize(
    "platform, parsed",
    (
        ["OSX", "osx"],
        ["macos", "osx"],
        ["macOS", "osx"],
    ),
)
def test_parse_platform(platform, parsed):
    assert parse_platform(platform) == parsed
