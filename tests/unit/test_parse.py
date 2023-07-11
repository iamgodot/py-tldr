import pytest

from py_tldr.parse import parse_command


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
