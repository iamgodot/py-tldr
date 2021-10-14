from click.testing import CliRunner

from pytldr import cli


def test_cli():
    runner = CliRunner()
    result = runner.invoke(cli, [])
    assert result.exit_code == 0
    assert result.output == 'Hello world!\n'
