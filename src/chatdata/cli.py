"""CLI entrypoint for chatdata."""

from __future__ import annotations

import json
from pathlib import Path

import click

from chatdata import __version__
from chatdata import mysql as mysql_ops


def _format_metavar(name: str) -> str:
    return name.replace("_", "-").upper()


def _format_argument(param: click.Argument) -> str:
    metavar = _format_metavar(param.name or "arg")
    if param.nargs == -1:
        value = f"<{metavar}>..."
    else:
        value = f"<{metavar}>"
    if not param.required:
        return f"[{value}]"
    return value


def _format_option(param: click.Option) -> str:
    primary = next((opt for opt in param.opts if opt.startswith("--")), param.opts[0] if param.opts else param.name)
    if param.secondary_opts:
        secondary = next((opt for opt in param.secondary_opts if opt.startswith("--")), param.secondary_opts[0])
        return f"[{primary}/{secondary}]"
    if param.is_flag or param.flag_value is not None:
        return f"[{primary}]"
    metavar = param.metavar or _format_metavar(param.name or "value")
    return f"[{primary} <{metavar}>]"


def _format_command_signature(command: click.Command) -> str:
    arguments: list[str] = []
    options: list[str] = []
    for param in command.params:
        if isinstance(param, click.Argument):
            arguments.append(_format_argument(param))
        elif isinstance(param, click.Option):
            options.append(_format_option(param))
    return " ".join(arguments + options)


def _command_purpose(command: click.Command) -> str:
    text = command.short_help or command.help or ""
    first_line = next((line.strip() for line in text.splitlines() if line.strip()), "No description.")
    return first_line.rstrip(".") + "."


def _visible_children(command: click.Command) -> list[tuple[str, click.Command]]:
    children = getattr(command, "commands", {})
    return [(name, child) for name, child in children.items() if not getattr(child, "hidden", False)]


def render_cli_tree(command: click.Command, root_name: str = "chatdata") -> str:
    """Render the registered Click command tree."""

    lines = [f"{root_name}  # {_command_purpose(command)}"]
    synthetic = [
        ("--help", "Show this help message."),
        ("--version", "Show the installed package version."),
        ("--tree", "Print the registered command tree."),
    ]
    nodes: list[tuple[str, str | click.Command]] = [(name, purpose) for name, purpose in synthetic]
    nodes.extend((name, child) for name, child in _visible_children(command))

    def walk(items: list[tuple[str, str | click.Command]] | list[tuple[str, click.Command]], prefix: str = "") -> None:
        for index, (name, value) in enumerate(items):
            is_last = index == len(items) - 1
            branch = "└── " if is_last else "├── "
            child_prefix = prefix + ("    " if is_last else "│   ")
            if isinstance(value, str):
                lines.append(f"{prefix}{branch}{name}  # {value}")
                continue
            signature = _format_command_signature(value)
            label = f"{name} {signature}".strip()
            lines.append(f"{prefix}{branch}{label}  # {_command_purpose(value)}")
            children = _visible_children(value)
            if children:
                walk(children, child_prefix)

    walk(nodes)
    return "\n".join(lines)


def _print_tree(ctx: click.Context, _param: click.Option, value: bool) -> None:
    if not value or ctx.resilient_parsing:
        return
    click.echo(render_cli_tree(ctx.command))
    ctx.exit()


def echo_payload(payload: object, json_output: bool = False) -> None:
    if json_output:
        click.echo(json.dumps(payload, ensure_ascii=False, indent=2))
        return
    if isinstance(payload, dict):
        for key, value in payload.items():
            if isinstance(value, dict):
                click.echo(f"{key}:")
                for sub_key, sub_value in value.items():
                    click.echo(f"  {sub_key}: {sub_value}")
            else:
                click.echo(f"{key}: {value}")
        return
    click.echo(str(payload))


@click.group(name="chatdata", context_settings={"help_option_names": ["-h", "--help"]})
@click.version_option(__version__, prog_name="chatdata")
@click.option("--tree", is_flag=True, is_eager=True, expose_value=False, callback=_print_tree, help="Print the registered command tree.")
def main() -> None:
    """ChatArch database and data management toolkit."""


@main.group(name="mysql")
def mysql_group() -> None:
    """Manage user-level MySQL runtimes and instances."""


@mysql_group.command(name="doctor")
@click.option("--port", default=mysql_ops.DEFAULT_MYSQL_PORT, show_default=True, type=int)
@click.option("--bind-address", default=mysql_ops.DEFAULT_MYSQL_BIND_ADDRESS, show_default=True)
@click.option("--json-output", is_flag=True)
def mysql_doctor(port: int, bind_address: str, json_output: bool) -> None:
    """Check host compatibility for the user-level MySQL runtime."""
    echo_payload(mysql_ops.mysql_doctor(port=port, bind_address=bind_address), json_output=json_output)


@mysql_group.command(name="install")
@click.option("--version", default=mysql_ops.DEFAULT_MYSQL_VERSION, show_default=True)
@click.option("--home", type=click.Path(path_type=Path), default=None)
@click.option("--force", is_flag=True)
@click.option("--json-output", is_flag=True)
def mysql_install(version: str, home: Path | None, force: bool, json_output: bool) -> None:
    """Download, verify, and install a MySQL binary tarball under ChatData home."""
    try:
        payload = mysql_ops.install_mysql(version=version, home=home, force=force)
    except Exception as exc:
        raise click.ClickException(str(exc)) from exc
    echo_payload(payload, json_output=json_output)


@mysql_group.group(name="runtime")
def mysql_runtime_group() -> None:
    """Inspect installed MySQL runtime paths."""


@mysql_runtime_group.command(name="path")
@click.option("--version", default=mysql_ops.DEFAULT_MYSQL_VERSION, show_default=True)
@click.option("--home", type=click.Path(path_type=Path), default=None)
@click.option("--json-output", is_flag=True)
def mysql_runtime_path(version: str, home: Path | None, json_output: bool) -> None:
    """Show MySQL runtime and instance layout paths."""
    echo_payload(mysql_ops.export_layout(version=version, home=home), json_output=json_output)


@mysql_group.group(name="instance")
def mysql_instance_group() -> None:
    """Manage MySQL instance directories and config."""


@mysql_instance_group.command(name="init")
@click.option("--name", default="default", show_default=True)
@click.option("--version", default=mysql_ops.DEFAULT_MYSQL_VERSION, show_default=True)
@click.option("--home", type=click.Path(path_type=Path), default=None)
@click.option("--port", default=mysql_ops.DEFAULT_MYSQL_PORT, show_default=True, type=int)
@click.option("--bind-address", default=mysql_ops.DEFAULT_MYSQL_BIND_ADDRESS, show_default=True)
@click.option("--initialize/--no-initialize", default=True, show_default=True, help="Run mysqld --initialize-insecure after writing directories/config.")
@click.option("--force", is_flag=True)
@click.option("--json-output", is_flag=True)
def mysql_instance_init(
    name: str,
    version: str,
    home: Path | None,
    port: int,
    bind_address: str,
    initialize: bool,
    force: bool,
    json_output: bool,
) -> None:
    """Create a user-level MySQL instance and initialize its data directory."""
    try:
        payload = mysql_ops.init_instance(name=name, version=version, home=home, port=port, bind_address=bind_address, initialize=initialize, force=force)
    except Exception as exc:
        raise click.ClickException(str(exc)) from exc
    echo_payload(payload, json_output=json_output)


@mysql_instance_group.command(name="show")
@click.option("--name", default="default", show_default=True)
@click.option("--version", default=mysql_ops.DEFAULT_MYSQL_VERSION, show_default=True)
@click.option("--home", type=click.Path(path_type=Path), default=None)
@click.option("--json-output", is_flag=True)
def mysql_instance_show(name: str, version: str, home: Path | None, json_output: bool) -> None:
    """Show MySQL instance layout paths."""
    echo_payload(mysql_ops.export_layout(name=name, version=version, home=home), json_output=json_output)


@mysql_group.group(name="service")
def mysql_service_group() -> None:
    """Manage user-level MySQL systemd services."""


@mysql_service_group.command(name="install")
@click.option("--name", default="default", show_default=True)
@click.option("--version", default=mysql_ops.DEFAULT_MYSQL_VERSION, show_default=True)
@click.option("--home", type=click.Path(path_type=Path), default=None)
@click.option("--json-output", is_flag=True)
def mysql_service_install(name: str, version: str, home: Path | None, json_output: bool) -> None:
    """Install a systemd user service for a MySQL instance."""
    try:
        payload = mysql_ops.install_service(name=name, version=version, home=home)
    except Exception as exc:
        raise click.ClickException(str(exc)) from exc
    echo_payload(payload, json_output=json_output)


@mysql_service_group.command(name="start")
@click.option("--name", default="default", show_default=True)
def mysql_service_start(name: str) -> None:
    """Start a MySQL user service."""
    result = mysql_ops.systemctl_user(name, "start")
    if result.returncode != 0:
        raise click.ClickException((result.stderr or result.stdout).strip())
    click.echo(f"started: {mysql_ops.service_name(name)}")


@mysql_service_group.command(name="stop")
@click.option("--name", default="default", show_default=True)
def mysql_service_stop(name: str) -> None:
    """Stop a MySQL user service."""
    result = mysql_ops.systemctl_user(name, "stop")
    if result.returncode != 0:
        raise click.ClickException((result.stderr or result.stdout).strip())
    click.echo(f"stopped: {mysql_ops.service_name(name)}")


@mysql_service_group.command(name="restart")
@click.option("--name", default="default", show_default=True)
def mysql_service_restart(name: str) -> None:
    """Restart a MySQL user service."""
    result = mysql_ops.systemctl_user(name, "restart")
    if result.returncode != 0:
        raise click.ClickException((result.stderr or result.stdout).strip())
    click.echo(f"restarted: {mysql_ops.service_name(name)}")


@mysql_service_group.command(name="status")
@click.option("--name", default="default", show_default=True)
@click.option("--json-output", is_flag=True)
def mysql_service_status(name: str, json_output: bool) -> None:
    """Show MySQL user service active state."""
    echo_payload(mysql_ops.service_status(name), json_output=json_output)


@mysql_service_group.command(name="logs")
@click.option("--name", default="default", show_default=True)
@click.option("--lines", default=100, show_default=True, type=int)
def mysql_service_logs(name: str, lines: int) -> None:
    """Show MySQL user service journal logs."""
    result = mysql_ops.journalctl_user(name, lines=lines)
    if result.stdout:
        click.echo(result.stdout)
    if result.stderr:
        click.echo(result.stderr, err=True)


@mysql_group.group(name="client")
def mysql_client_group() -> None:
    """Run MySQL client checks and SQL."""


@mysql_client_group.command(name="ping")
@click.option("--name", default="default", show_default=True)
@click.option("--version", default=mysql_ops.DEFAULT_MYSQL_VERSION, show_default=True)
@click.option("--home", type=click.Path(path_type=Path), default=None)
@click.option("--json-output", is_flag=True)
def mysql_client_ping(name: str, version: str, home: Path | None, json_output: bool) -> None:
    """Run mysqladmin ping through the instance socket."""
    payload = mysql_ops.ping(name=name, version=version, home=home)
    if not json_output and payload["ok"]:
        click.echo(payload["stdout"] or "mysqld is alive")
        return
    echo_payload(payload, json_output=json_output)


@mysql_client_group.command(name="query")
@click.option("--name", default="default", show_default=True)
@click.option("--version", default=mysql_ops.DEFAULT_MYSQL_VERSION, show_default=True)
@click.option("--home", type=click.Path(path_type=Path), default=None)
@click.option("--database", default=None, help="Optional database to select before running SQL.")
@click.option("--sql", required=True)
def mysql_client_query(name: str, version: str, home: Path | None, database: str | None, sql: str) -> None:
    """Execute one SQL statement through the instance socket."""
    try:
        click.echo(mysql_ops.query(sql, name=name, version=version, home=home, database=database), nl=False)
    except Exception as exc:
        raise click.ClickException(str(exc)) from exc


@mysql_client_group.command(name="import")
@click.option("--name", default="default", show_default=True)
@click.option("--version", default=mysql_ops.DEFAULT_MYSQL_VERSION, show_default=True)
@click.option("--home", type=click.Path(path_type=Path), default=None)
@click.option("--database", default=None, help="Optional database to select before importing SQL.")
@click.option("--file", "sql_file", type=click.Path(path_type=Path, exists=True), required=True)
@click.option("--json-output", is_flag=True)
def mysql_client_import(name: str, version: str, home: Path | None, database: str | None, sql_file: Path, json_output: bool) -> None:
    """Import a SQL file through the instance socket."""
    try:
        result = mysql_ops.query_file(sql_file, name=name, version=version, home=home, database=database)
    except Exception as exc:
        raise click.ClickException(str(exc)) from exc
    echo_payload({"file": str(sql_file), "returncode": result.returncode, "stderr": result.stderr.strip()}, json_output=json_output)


@mysql_group.group(name="database")
def mysql_database_group() -> None:
    """Manage databases on a MySQL instance."""


@mysql_database_group.command(name="create")
@click.argument("database")
@click.option("--name", default="default", show_default=True)
@click.option("--version", default=mysql_ops.DEFAULT_MYSQL_VERSION, show_default=True)
@click.option("--home", type=click.Path(path_type=Path), default=None)
def mysql_database_create(database: str, name: str, version: str, home: Path | None) -> None:
    """Create a utf8mb4 database if it does not exist."""
    try:
        mysql_ops.create_database(database, name=name, version=version, home=home)
    except Exception as exc:
        raise click.ClickException(str(exc)) from exc
    click.echo(f"database ready: {database}")


if __name__ == "__main__":
    main()
