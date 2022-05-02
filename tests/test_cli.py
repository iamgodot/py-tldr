from os import environ

import pytest
import toml

from py_tldr import core
from py_tldr.core import cli, get_languages
from py_tldr.page import DownloadError


def test_version(runner):
    result = runner.invoke(cli, ["-v"])
    assert result.exit_code == 0
    assert "tldr version" in result.output
    assert "client specification version" in result.output


class TestConfig:
    def test_initialize_default_config_file(self, tmp_path, mocker, runner):
        tmp_file = tmp_path / "config.toml"
        mocker.patch.object(core, "DEFAULT_CONFIG_DIR", tmp_path)
        mocker.patch.object(core, "DEFAULT_CONFIG_FILE", tmp_file)

        result = runner.invoke(cli, [])
        assert result.exit_code == 0
        assert tmp_file.exists()
        with open(tmp_file, encoding="utf8") as f:
            config = toml.load(f)
            assert config == core.DEFAULT_CONFIG

    def _make_config_file(self, path, config):
        config_file = path / "config.toml"
        with open(config_file, "w", encoding="utf8") as f:
            toml.dump(config, f)
        return config_file

    def _make_ctx(self, mocker):
        ctx = mocker.Mock(spec=["resilient_parsing"])
        ctx.resilient_parsing = False
        return ctx

    def test_use_custom_config_file(self, tmp_path, mocker):
        config = {"page_source": "foo", "cache": {"download_url": "bar"}}
        config_file = self._make_config_file(tmp_path, config)
        ctx = self._make_ctx(mocker)
        assert core.setup_config(ctx, None, config_file) == config

    @pytest.mark.parametrize(
        "config", ({}, {"page_source": "foo"}, {"page_source": "foo", "cache": {}})
    )
    def test_config_validation(self, tmp_path, mocker, config):
        config_file = self._make_config_file(tmp_path, config)
        ctx = self._make_ctx(mocker)
        with pytest.raises(SystemExit):
            core.setup_config(ctx, None, config_file)


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
