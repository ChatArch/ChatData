from click.testing import CliRunner

from chatdata import __version__
from chatdata.cli import main, render_cli_tree


def test_version_option_reports_package_version():
    result = CliRunner().invoke(main, ["--version"])

    assert result.exit_code == 0
    assert f"chatdata, version {__version__}" in result.output


def test_help_mentions_tree_option():
    result = CliRunner().invoke(main, ["--help"])

    assert result.exit_code == 0
    assert "--tree" in result.output


def test_tree_option_reports_registered_mysql_tree():
    result = CliRunner().invoke(main, ["--tree"])

    assert result.exit_code == 0
    assert result.output.strip() == render_cli_tree(main)
    assert "chatdata  # ChatArch database and data management toolkit." in result.output
    assert "├── --tree  # Print the registered command tree." in result.output
    assert "└── mysql" in result.output
    assert "doctor [--port <PORT>] [--bind-address <BIND-ADDRESS>] [--json-output]" in result.output
    assert "database" in result.output
    assert "create <DATABASE>" in result.output
    assert "hello" not in result.output.lower()
