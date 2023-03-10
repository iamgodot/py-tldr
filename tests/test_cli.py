from os import environ

import pytest
import toml

from py_tldr import core
from py_tldr.core import DEFAULT_CONFIG_EDITOR, DEFAULT_CONFIG_FILE, cli, get_languages
from py_tldr.page import DownloadError


def test_version(runner):
    result = runner.invoke(cli, ["-v"])
    assert result.exit_code == 0
    assert "tldr version" in result.output
    assert "client specification version" in result.output


class TestConfig:
    def _make_config_file(self, path, config):
        with open(path, "w", encoding="utf8") as f:
            toml.dump(config, f)

    def test_use_custom_config_file(self, tmp_path, mocker):
        config_customed = {"page_source": "foo", "cache": {"download_url": "bar"}}
        config_file = tmp_path / "config.toml"
        self._make_config_file(config_file, config_customed)
        mocker.patch.object(core, "DEFAULT_CONFIG_FILE", config_file)
        config = core.setup_config()
        assert config["page_source"] == config_customed["page_source"]
        assert config["cache"] == config_customed["cache"]

    @pytest.mark.parametrize(
        "config", ({"page_source": ""}, {"cache": ""}, {"cache": {"enabled": True}})
    )
    def test_config_validation(self, tmp_path, mocker, config):
        config_file = tmp_path / "config.toml"
        self._make_config_file(config_file, config)
        mocker.patch.object(core, "DEFAULT_CONFIG_FILE", config_file)
        with pytest.raises(SystemExit):
            core.setup_config()


class TestEditConfig:
    def test_create_default_config(self, tmp_path, mocker, runner):
        config_file = tmp_path / "config.toml"
        assert not config_file.exists()
        mocker.patch.object(core, "DEFAULT_CONFIG_FILE", config_file)
        runner.invoke(cli, ["tldr", "--edit-config"])
        assert config_file.exists()

    def test_default_open_editor(self, mocker, runner):
        patched_subprocess_call = mocker.patch("py_tldr.core.subprocess.call")
        environ.pop("EDITOR")
        runner.invoke(cli, ["tldr", "--edit-config"])
        patched_subprocess_call.assert_called_with(
            [DEFAULT_CONFIG_EDITOR, DEFAULT_CONFIG_FILE]
        )

    def test_respect_editor_env(self, mocker, runner):
        patched_subprocess_call = mocker.patch("py_tldr.core.subprocess.call")
        environ["EDITOR"] = editor = "vim"
        runner.invoke(cli, ["tldr", "--edit-config"])
        patched_subprocess_call.assert_called_with([editor, DEFAULT_CONFIG_FILE])


class TestCommand:
    def test_single(self, runner):
        result = runner.invoke(cli, ["tldr"])
        assert result.exit_code == 0
        assert "tldr" in result.output

    def test_multi(self, runner):
        result = runner.invoke(cli, ["git", "commit"])
        assert result.exit_code == 0
        assert "git commit" in result.output

    def test_with_update(self, mocker, runner):
        patched_update = mocker.patch("py_tldr.page.PageCache.update")
        result = runner.invoke(cli, ["--update", "tldr"])
        assert result.exit_code == 0
        assert "tldr" in result.output
        patched_update.assert_called_once()


class TestFailure:
    def test_sync_fail(self, mocker, runner):
        mocker.patch("py_tldr.page.PageFinder.sync", side_effect=DownloadError)
        result = runner.invoke(cli, ["--update"])
        assert result.exit_code == 1
        print(result.output)
        assert "failed" in result.output

    def test_find_page_fail(self, mocker, runner):
        mocker.patch("py_tldr.page.PageFinder.find", side_effect=DownloadError)
        result = runner.invoke(cli, ["tldr"])
        assert result.exit_code == 1
        assert "failed" in result.output

    def test_no_pages_found(self, mocker, runner):
        mocker.patch("py_tldr.page.PageFinder.find", return_value="")
        result = runner.invoke(cli, ["non-existed-cmd"])
        assert result.exit_code == 1
        assert "No result" in result.output


class TestGetLanguages:
    @pytest.mark.parametrize("language, languages", (["en", ["en"]], ["zh", ["zh"]]))
    def test_with_specified_lang(self, language, languages):
        assert get_languages(language) == languages

    @pytest.mark.parametrize(
        "env_lang, env_language, languages",
        (
            ["cz", "it:cz:de", ["it", "cz", "de", "en"]],
            ["cz", "it:de:fr", ["it", "de", "fr", "cz", "en"]],
            ["it", "", ["it", "en"]],
            ["", "it:cz", ["en"]],
            ["", "", ["en"]],
        ),
    )
    def test_from_env(self, env_lang, env_language, languages):
        environ["LANG"] = env_lang
        environ["LANGUAGE"] = env_language
        assert get_languages("") == languages
