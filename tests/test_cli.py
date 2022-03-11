from datetime import datetime
from os import utime

import pytest
import toml
from click import style

from py_tldr import core
from py_tldr.core import Formatter, cli


def test_version(runner):
    result = runner.invoke(cli, ["-v"])
    assert result.exit_code == 0
    assert "tldr version" in result.output
    assert "client specification version" in result.output


class TestConfig:
    def test_initialize(self, tmp_path, mocker, runner):
        tmp_file = tmp_path / "config.toml"
        mocker.patch.object(core, "DEFAULT_CONFIG_DIR", tmp_path)
        mocker.patch.object(core, "DEFAULT_CONFIG_FILE", tmp_file)

        result = runner.invoke(cli, [])
        assert result.exit_code == 0
        assert tmp_file.exists()
        with open(tmp_file, encoding="utf8") as f:
            config = toml.load(f)
            assert config == core.DEFAULT_CONFIG

    def test_custom(self, tmp_path, mocker):
        config = {"foo": "bar"}
        config_file = tmp_path / "custom.toml"
        with open(config_file, "w", encoding="utf8") as f:
            toml.dump(config, f)

        ctx = mocker.Mock(spec=["resilient_parsing"])
        ctx.resilient_parsing = False
        assert core.setup_config(ctx, None, config_file) == config


class TestCache:
    def test_validation(self, tmp_path):
        page_file = tmp_path / "foo.md"
        page_file.touch()
        cache = core.PageCache(1, tmp_path, "")
        assert cache._validate_page_file(page_file) is True
        ts = datetime.now().timestamp() - 3601
        utime(page_file, (ts, ts))
        assert cache._validate_page_file(page_file) is False

    def test_update(self):
        pass


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
        patched_update = mocker.patch("py_tldr.core.PageCache.update")
        result = runner.invoke(cli, ["--update", "tldr"])
        assert result.exit_code == 0
        assert "tldr" in result.output
        patched_update.assert_called_once()


class TestPageGet:
    def test_by_cache(self, mocker, runner):
        patched_get = mocker.patch("py_tldr.core.PageCache.get", return_value="foobar")
        patched_find = mocker.patch("py_tldr.core.PageFinder.find")
        result = runner.invoke(cli, ["tldr"])
        assert result.exit_code == 0
        assert "foobar" in result.output
        patched_get.assert_called_once()
        patched_find.assert_not_called()

    def test_by_finder(self, mocker, runner):
        patched_get = mocker.patch("py_tldr.core.PageCache.get", return_value=None)
        patched_find = mocker.patch(
            "py_tldr.core.PageFinder.find",
            return_value={"name": "foo", "platform": "common", "content": "bar"},
        )
        result = runner.invoke(cli, ["tldr"])
        assert result.exit_code == 0
        assert "bar" in result.output
        patched_get.assert_called_once()
        patched_find.assert_called_once()

    def test_no_result(self, mocker, runner):
        mocker.patch("py_tldr.core.PageCache.get", return_value=None)
        mocker.patch("py_tldr.core.PageFinder.find", return_value={})
        result = runner.invoke(cli, ["foobar"])
        assert result.exit_code == 1
        assert "no available pages" in result.output


class TestFormatter:
    def test_process(self, capsys):
        with pytest.raises(ValueError):
            Formatter.output(b"foobar")
        Formatter.output("foobar")
        assert capsys.readouterr().out == "foobar\n"
        Formatter.output("foo\nbar")
        assert capsys.readouterr().out == "foo\nbar\n"

    def test_process_page(self):
        formatter = Formatter("foo \n {{bar}} \n `bat` \n", is_page=True)
        formatter.process_content()
        assert formatter.buffer == ["foo", "bar", "bat", ""]

    def test_render(self, mocker):
        patched_print = mocker.patch("py_tldr.core.Formatter.print")
        Formatter.output("foobar", bold=True, fg="red")
        patched_print.assert_called_with(style("foobar", bold=True, fg="red"))

    def test_render_page(self):
        formatter = Formatter(
            """# Foo
               > See Foo from <https://foo.com>
               - Basic usage
               Foo bar""",
            is_page=True,
        )
        formatter.process_content()
        formatter.render_text()
        assert formatter.buffer == [
            style("Foo", bold=True, fg="red"),
            style("See Foo from https://foo.com", fg="yellow", underline=True),
            style("\u2022 Basic usage", fg="green"),
            style("  Foo bar", fg="magenta"),
        ]

    def test_output_with_indent(self, capsys):
        Formatter.output("foobar", indent_spaces=2)
        assert capsys.readouterr().out == "  foobar\n"

    def test_output_with_new_line(self, capsys):
        Formatter.output("foobar", start_with_new_line=True)
        assert capsys.readouterr().out == "\nfoobar\n"
