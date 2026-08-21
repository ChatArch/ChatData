from click.testing import CliRunner
from chatstyle import render_click_tree

from chatdata import __version__
from chatdata.cli import main


def test_version_option_reports_package_version():
    result = CliRunner().invoke(main, ["--version"])

    assert result.exit_code == 0
    assert f"chatdata, version {__version__}" in result.output


def test_help_mentions_tree_options():
    result = CliRunner().invoke(main, ["--help"])

    assert result.exit_code == 0
    assert "--tree" in result.output
    assert "--tree-brief" in result.output


def test_tree_option_reports_registered_mysql_tree_with_signatures():
    result = CliRunner().invoke(main, ["--tree"])

    assert result.exit_code == 0, result.output
    assert result.output.strip() == render_click_tree(main, root_name="chatdata")
    assert result.output.splitlines()[0] == "chatdata"
    assert result.output.splitlines().count("chatdata") == 1
    assert "--tree  # Print the registered CLI tree and exit." in result.output
    assert "--tree-brief  # Print the registered CLI tree without parameter signatures and exit." in result.output
    assert "└── mysql" in result.output
    assert "doctor [--port PORT] [--bind-address BIND-ADDRESS] [--json-output]" in result.output
    assert "database" in result.output
    assert "create <DATABASE>" in result.output
    assert "hello" not in result.output.lower()


def test_tree_brief_reports_same_surface_without_signatures():
    result = CliRunner().invoke(main, ["--tree-brief"])

    assert result.exit_code == 0, result.output
    assert result.output.strip() == render_click_tree(main, root_name="chatdata", brief=True)
    assert "mysql  # Manage user-level MySQL runtimes and instances." in result.output
    assert "doctor  # Check host compatibility for the user-level MySQL runtime." in result.output
    assert "create  # Create a utf8mb4 database if it does not exist." in result.output
    assert "<DATABASE>" not in result.output
    assert "[--port PORT]" not in result.output
    assert "[--json-output]" not in result.output


def test_tree_root_uses_public_console_command_in_module_mode():
    result = CliRunner().invoke(main, ["--tree"], prog_name="python -m chatdata.cli")

    assert result.exit_code == 0, result.output
    assert result.output.splitlines()[0] == "chatdata"
    assert "python -m chatdata.cli" not in result.output
