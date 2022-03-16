from click import style

from py_tldr.page import Formatter, PageFormatter


def test_indent_space():
    formatted = Formatter(indent_spaces=2).format("foobar")
    assert formatted == "  foobar\n"


def test_start_with_new_line():
    formatted = Formatter(start_with_new_line=True).format("foobar")
    assert formatted == "\nfoobar\n"


def test_format_multi_lines():
    formatted = Formatter().format("foo\n\nbar\nbat")
    assert formatted == "foo\n\nbar\nbat\n"


def test_format_page():
    formatted = PageFormatter(indent_spaces=0).format(
        """# Foo
           > See Foo from <https://foo.com>
           - Basic usage
           `Foo {{bar}}`""",
    )
    assert (
        formatted
        == "\n".join(
            [
                style("Foo", bold=True, fg="red"),
                style("See Foo from https://foo.com", fg="yellow", underline=True),
                style("\u2022 Basic usage", fg="green"),
                style("  Foo bar", fg="magenta"),
            ]
        )
        + "\n"
    )
