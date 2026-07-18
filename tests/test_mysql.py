from pathlib import Path

from click.testing import CliRunner

from chatdata.cli import main
from chatdata.mysql import (
    DEFAULT_MYSQL_VERSION,
    client_command,
    create_database,
    ensure_database_user,
    mysql_asset_urls,
    mysql_layout,
    render_my_cnf,
    render_service,
    service_name,
    sql_string_literal,
)


def test_mysql_help_lists_runtime_groups():
    result = CliRunner().invoke(main, ["mysql", "--help"])

    assert result.exit_code == 0
    for command in ["doctor", "install", "runtime", "instance", "service", "client", "database"]:
        assert command in result.output


def test_mysql_layout_uses_chatdata_home(tmp_path):
    layout = mysql_layout(name="demo", version="8.4.6", home=tmp_path / "chatdata")

    assert layout.runtime == tmp_path / "chatdata" / "runtimes" / "mysql" / "8.4.6"
    assert layout.config == tmp_path / "chatdata" / "instances" / "mysql" / "demo" / "my.cnf"
    assert layout.socket == tmp_path / "chatdata" / "instances" / "mysql" / "demo" / "run" / "mysql.sock"
    assert layout.service.name == "chatdata-mysql-demo.service"


def test_mysql_layout_rejects_unsafe_instance_names(tmp_path):
    for name in ["../demo", "demo/name", ""]:
        try:
            mysql_layout(name=name, version="8.4.6", home=tmp_path / "chatdata")
        except ValueError as exc:
            assert "Invalid instance name" in str(exc)
        else:
            raise AssertionError(f"unsafe name was accepted: {name!r}")


def test_mysql_asset_urls_default_to_official_archive():
    archive, checksum = mysql_asset_urls(DEFAULT_MYSQL_VERSION, platform_name="linux-glibc2.28-x86_64")

    assert archive == "https://cdn.mysql.com/archives/mysql-8.4/mysql-8.4.6-linux-glibc2.28-x86_64.tar.xz"
    assert checksum == archive + ".md5"


def test_render_my_cnf_and_service_reference_user_paths(tmp_path):
    layout = mysql_layout(name="demo", version="8.4.6", home=tmp_path / "chatdata")
    runtime = layout.runtime

    my_cnf = render_my_cnf(layout, runtime, port=3310, bind_address="127.0.0.1")
    service = render_service(layout, runtime, name="demo")

    assert f"basedir={runtime}" in my_cnf
    assert f"datadir={layout.data}" in my_cnf
    assert "port=3310" in my_cnf
    assert "bind-address=127.0.0.1" in my_cnf
    assert "collation-server=utf8mb4_bin" in my_cnf
    assert f"ExecStart={runtime / 'bin' / 'mysqld'} --defaults-file={layout.config}" in service
    assert f"ExecStop={runtime / 'bin' / 'mysqladmin'} --socket={layout.socket} shutdown" in service
    assert service_name("demo") == "chatdata-mysql-demo.service"


def test_mysql_runtime_path_cli_outputs_json(tmp_path):
    result = CliRunner().invoke(main, ["mysql", "runtime", "path", "--home", str(tmp_path / "chatdata"), "--json-output"])

    assert result.exit_code == 0
    assert '"home"' in result.output
    assert str(tmp_path / "chatdata") in result.output


def test_client_command_can_select_database(tmp_path):
    command = client_command(name="demo", version="8.4.6", home=tmp_path / "chatdata", database="gitea")

    assert command[-1] == "--database=gitea"
    assert any(part.startswith("--socket=") for part in command)


def test_client_command_rejects_unsafe_database_names(tmp_path):
    for database in ["", "--user=other", "../gitea"]:
        try:
            client_command(name="demo", version="8.4.6", home=tmp_path / "chatdata", database=database)
        except ValueError as exc:
            assert "Invalid database name" in str(exc)
        else:
            raise AssertionError(f"unsafe database was accepted: {database!r}")


def test_create_database_rejects_unsafe_database_names(tmp_path):
    for database in ["", "gitea;DROP", "../gitea"]:
        try:
            create_database(database, name="demo", version="8.4.6", home=tmp_path / "chatdata")
        except ValueError as exc:
            assert "Invalid database name" in str(exc)
        else:
            raise AssertionError(f"unsafe database was accepted: {database!r}")


def test_ensure_database_user_sends_password_via_stdin(monkeypatch, tmp_path):
    captured = {}

    def fake_run(command, input=None, check=False, capture_output=False, text=False):
        captured.update({"command": command, "input": input, "check": check, "capture_output": capture_output, "text": text})
        return "ok"

    monkeypatch.setattr("chatdata.mysql.subprocess.run", fake_run)

    ensure_database_user("gitea", user="gitea", password="secret\\'pw", name="demo", version="8.4.6", home=tmp_path / "chatdata")

    assert "secret" not in " ".join(captured["command"])
    assert sql_string_literal("secret\\'pw") == "'secret\\\\''pw'"
    assert "IDENTIFIED BY 'secret\\\\''pw'" in captured["input"]
    assert "GRANT ALL PRIVILEGES ON `gitea`.*" in captured["input"]
    assert captured["check"] is True
