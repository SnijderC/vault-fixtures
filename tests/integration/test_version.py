from typer.testing import CliRunner
from vault_fix import __version__
from vault_fix.__main__ import cli

runner = CliRunner(mix_stderr=False)


def test_app():
    result = runner.invoke(cli, "version")
    assert result.exit_code == 0
    assert result.stdout == f"vault-fix v{__version__}\n"
