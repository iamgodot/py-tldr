import pytest
from click import style

from py_tldr.core import Formatter


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
