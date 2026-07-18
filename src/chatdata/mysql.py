from __future__ import annotations

import ctypes.util
import hashlib
import json
import os
import platform
import shutil
import socket
import subprocess
import tarfile
import tempfile
import time
import urllib.request
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from chatenv import get_paths

DEFAULT_MYSQL_VERSION = "8.4.6"
DEFAULT_MYSQL_PLATFORM = "linux-glibc2.28-x86_64"
DEFAULT_MYSQL_PORT = 3307
DEFAULT_MYSQL_BIND_ADDRESS = "127.0.0.1"


@dataclass(frozen=True)
class MysqlLayout:
    home: Path
    downloads: Path
    runtimes: Path
    runtime: Path
    current: Path
    instances: Path
    instance: Path
    data: Path
    run: Path
    logs: Path
    tmp: Path
    config: Path
    socket: Path
    pid: Path
    error_log: Path
    service: Path


def default_chatdata_home() -> Path:
    return get_paths().home_dir / "chatdata"


def mysql_layout(name: str = "default", version: str = DEFAULT_MYSQL_VERSION, home: Path | None = None) -> MysqlLayout:
    root = (home or default_chatdata_home()).expanduser()
    instance = root / "instances" / "mysql" / name
    runtimes = root / "runtimes" / "mysql"
    return MysqlLayout(
        home=root,
        downloads=root / "downloads",
        runtimes=runtimes,
        runtime=runtimes / version,
        current=runtimes / "current",
        instances=root / "instances" / "mysql",
        instance=instance,
        data=instance / "data",
        run=instance / "run",
        logs=instance / "logs",
        tmp=instance / "tmp",
        config=instance / "my.cnf",
        socket=instance / "run" / "mysql.sock",
        pid=instance / "run" / "mysqld.pid",
        error_log=instance / "logs" / "error.log",
        service=Path("~/.config/systemd/user").expanduser() / f"chatdata-mysql-{name}.service",
    )


def detect_mysql_platform() -> str:
    system = platform.system().lower()
    machine = platform.machine().lower()
    if system == "linux" and machine in {"x86_64", "amd64"}:
        return DEFAULT_MYSQL_PLATFORM
    raise ValueError(f"Unsupported MySQL platform: {platform.system()} {platform.machine()}")


def mysql_asset_urls(version: str = DEFAULT_MYSQL_VERSION, platform_name: str | None = None) -> tuple[str, str]:
    platform_name = platform_name or detect_mysql_platform()
    filename = f"mysql-{version}-{platform_name}.tar.xz"
    base = f"https://cdn.mysql.com/archives/mysql-{version.rsplit('.', 1)[0]}/{filename}"
    return base, f"{base}.md5"


def _read_url(url: str) -> bytes:
    with urllib.request.urlopen(url, timeout=60) as response:
        return response.read()


def _download_url(url: str, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(url, timeout=60) as response, target.open("wb") as handle:
        shutil.copyfileobj(response, handle)


def _parse_md5(text: str) -> str:
    for token in text.replace("=", " ").split():
        lowered = token.strip().lower()
        if len(lowered) == 32 and all(ch in "0123456789abcdef" for ch in lowered):
            return lowered
    raise RuntimeError("Could not parse MySQL md5 checksum")


def verify_md5(path: Path, expected: str) -> str:
    actual = hashlib.md5(path.read_bytes()).hexdigest()  # nosec: official MySQL publishes md5 sidecar for archives.
    if actual.lower() != expected.lower():
        raise RuntimeError(f"Checksum mismatch for {path.name}")
    return actual


def _safe_member_path(root: Path, member_name: str) -> Path:
    candidate = (root / member_name).resolve()
    resolved_root = root.resolve()
    if candidate != resolved_root and resolved_root not in candidate.parents:
        raise RuntimeError(f"Unsafe tar path: {member_name}")
    return candidate


def safe_extract_tar(archive: Path, destination: Path) -> None:
    destination.mkdir(parents=True, exist_ok=True)
    with tarfile.open(archive, "r:xz") as tar:
        members = tar.getmembers()
        prefixes = {member.name.split("/", 1)[0] for member in members if member.name and not member.name.startswith("/")}
        strip_prefix = next(iter(prefixes)) if len(prefixes) == 1 else ""
        for member in members:
            if not member.name or member.name.startswith("/") or ".." in Path(member.name).parts:
                raise RuntimeError(f"Unsafe tar member: {member.name}")
            relative = member.name
            if strip_prefix and relative == strip_prefix:
                continue
            if strip_prefix and relative.startswith(strip_prefix + "/"):
                relative = relative[len(strip_prefix) + 1 :]
            if not relative:
                continue
            target = _safe_member_path(destination, relative)
            if member.isdir():
                target.mkdir(parents=True, exist_ok=True)
                continue
            if member.issym() or member.islnk():
                link_target = Path(member.linkname)
                if link_target.is_absolute() or ".." in link_target.parts:
                    raise RuntimeError(f"Unsafe tar link: {member.name} -> {member.linkname}")
                target.parent.mkdir(parents=True, exist_ok=True)
                if target.exists() or target.is_symlink():
                    target.unlink()
                os.symlink(member.linkname, target)
                continue
            if not member.isfile():
                raise RuntimeError(f"Unsupported tar member type: {member.name}")
            target.parent.mkdir(parents=True, exist_ok=True)
            source = tar.extractfile(member)
            if source is None:
                raise RuntimeError(f"Could not extract {member.name}")
            with source, target.open("wb") as handle:
                shutil.copyfileobj(source, handle)
            target.chmod(member.mode & 0o777)


def mysql_binary(version: str = DEFAULT_MYSQL_VERSION, home: Path | None = None, binary: str = "mysqld") -> Path:
    return mysql_layout(version=version, home=home).runtime / "bin" / binary


def install_mysql(
    version: str = DEFAULT_MYSQL_VERSION,
    home: Path | None = None,
    force: bool = False,
    platform_name: str | None = None,
) -> dict[str, Any]:
    layout = mysql_layout(version=version, home=home)
    mysqld = layout.runtime / "bin" / "mysqld"
    if mysqld.exists() and not force:
        return {"version": version, "runtime": str(layout.runtime), "binary": str(mysqld), "reused": True}

    url, md5_url = mysql_asset_urls(version, platform_name=platform_name)
    archive = layout.downloads / Path(url).name
    md5_path = layout.downloads / f"{archive.name}.md5"
    _download_url(url, archive)
    md5_text = _read_url(md5_url).decode("utf-8", "replace")
    md5_path.write_text(md5_text, encoding="utf-8")
    expected = _parse_md5(md5_text)
    actual = verify_md5(archive, expected)

    layout.runtimes.mkdir(parents=True, exist_ok=True)
    tmp = layout.runtimes / f".{version}.tmp-{int(time.time())}"
    if tmp.exists():
        shutil.rmtree(tmp)
    safe_extract_tar(archive, tmp)
    if layout.runtime.exists():
        if not force:
            shutil.rmtree(tmp)
            return {"version": version, "runtime": str(layout.runtime), "binary": str(mysqld), "reused": True}
        shutil.rmtree(layout.runtime)
    tmp.replace(layout.runtime)
    if layout.current.exists() or layout.current.is_symlink():
        layout.current.unlink()
    layout.current.symlink_to(layout.runtime, target_is_directory=True)
    version_output = subprocess.run([str(mysqld), "--version"], check=True, capture_output=True, text=True).stdout.strip()
    return {
        "version": version,
        "runtime": str(layout.runtime),
        "binary": str(mysqld),
        "download": str(archive),
        "md5": actual,
        "reused": False,
        "version_output": version_output,
    }


def check_port_free(host: str, port: int) -> bool:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.bind((host, port))
        return True
    except OSError:
        return False
    finally:
        sock.close()


def mysql_doctor(port: int = DEFAULT_MYSQL_PORT, bind_address: str = DEFAULT_MYSQL_BIND_ADDRESS) -> dict[str, Any]:
    libs = {name: ctypes.util.find_library(name) for name in ["aio", "numa", "ssl", "crypto", "ncurses", "tinfo", "z", "stdc++"]}
    missing = [name for name, value in libs.items() if value is None]
    return {
        "platform": detect_mysql_platform(),
        "port": port,
        "port_free": check_port_free(bind_address, port),
        "libraries": libs,
        "missing_libraries": missing,
        "systemd_user": shutil.which("systemctl") is not None,
    }


def render_my_cnf(
    layout: MysqlLayout,
    runtime: Path,
    port: int = DEFAULT_MYSQL_PORT,
    bind_address: str = DEFAULT_MYSQL_BIND_ADDRESS,
) -> str:
    return f"""[mysqld]
basedir={runtime}
datadir={layout.data}
socket={layout.socket}
pid-file={layout.pid}
log-error={layout.error_log}
tmpdir={layout.tmp}
port={port}
bind-address={bind_address}
mysqlx=0
skip_name_resolve=ON
character-set-server=utf8mb4
collation-server=utf8mb4_bin

[client]
socket={layout.socket}
port={port}
user=root
"""


def init_instance(
    name: str = "default",
    version: str = DEFAULT_MYSQL_VERSION,
    home: Path | None = None,
    port: int = DEFAULT_MYSQL_PORT,
    bind_address: str = DEFAULT_MYSQL_BIND_ADDRESS,
    initialize: bool = True,
    force: bool = False,
) -> dict[str, Any]:
    layout = mysql_layout(name=name, version=version, home=home)
    runtime = layout.runtime
    mysqld = runtime / "bin" / "mysqld"
    if not mysqld.exists():
        raise FileNotFoundError(f"MySQL runtime not installed: {mysqld}")
    if layout.data.exists() and any(layout.data.iterdir()) and not force:
        return {"name": name, "config": str(layout.config), "data": str(layout.data), "initialized": False, "reused": True}
    for child in [layout.data, layout.run, layout.logs, layout.tmp]:
        child.mkdir(parents=True, exist_ok=True)
    layout.config.write_text(render_my_cnf(layout, runtime, port=port, bind_address=bind_address), encoding="utf-8")
    layout.config.chmod(0o600)
    initialized = False
    if initialize:
        subprocess.run([str(mysqld), f"--defaults-file={layout.config}", "--initialize-insecure"], check=True)
        initialized = True
    manifest = {
        "name": name,
        "version": version,
        "port": port,
        "bind_address": bind_address,
        "socket": str(layout.socket),
        "config": str(layout.config),
        "data": str(layout.data),
        "runtime": str(runtime),
    }
    (layout.instance / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return {**manifest, "initialized": initialized, "reused": False}


def service_name(name: str = "default") -> str:
    return f"chatdata-mysql-{name}.service"


def render_service(layout: MysqlLayout, runtime: Path, name: str = "default") -> str:
    return f"""[Unit]
Description=ChatData MySQL instance {name}
After=network.target

[Service]
Type=simple
WorkingDirectory={layout.instance}
ExecStart={runtime / 'bin' / 'mysqld'} --defaults-file={layout.config}
ExecStop={runtime / 'bin' / 'mysqladmin'} --socket={layout.socket} shutdown
Restart=on-failure
RestartSec=5s
Environment=HOME={Path.home()}

[Install]
WantedBy=default.target
"""


def install_service(name: str = "default", version: str = DEFAULT_MYSQL_VERSION, home: Path | None = None) -> dict[str, Any]:
    layout = mysql_layout(name=name, version=version, home=home)
    runtime = layout.runtime
    layout.service.parent.mkdir(parents=True, exist_ok=True)
    layout.service.write_text(render_service(layout, runtime, name=name), encoding="utf-8")
    subprocess.run(["systemctl", "--user", "daemon-reload"], check=False, capture_output=True, text=True)
    subprocess.run(["systemctl", "--user", "enable", service_name(name)], check=False, capture_output=True, text=True)
    return {"name": name, "service": str(layout.service), "unit": service_name(name)}


def systemctl_user(name: str, action: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["systemctl", "--user", action, service_name(name)], check=False, capture_output=True, text=True)


def journalctl_user(name: str = "default", lines: int = 100) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["journalctl", "--user", "-u", service_name(name), "-n", str(lines), "--no-pager"], check=False, capture_output=True, text=True)


def service_status(name: str = "default") -> dict[str, Any]:
    result = systemctl_user(name, "is-active")
    return {"name": name, "unit": service_name(name), "active": result.stdout.strip(), "returncode": result.returncode}


def client_command(
    name: str = "default",
    version: str = DEFAULT_MYSQL_VERSION,
    home: Path | None = None,
    binary: str = "mysql",
    database: str | None = None,
) -> list[str]:
    layout = mysql_layout(name=name, version=version, home=home)
    command = [str(layout.runtime / "bin" / binary), f"--socket={layout.socket}", "-uroot"]
    if database:
        command.append(database)
    return command


def ping(name: str = "default", version: str = DEFAULT_MYSQL_VERSION, home: Path | None = None) -> dict[str, Any]:
    layout = mysql_layout(name=name, version=version, home=home)
    result = subprocess.run([str(layout.runtime / "bin" / "mysqladmin"), f"--socket={layout.socket}", "-uroot", "ping"], check=False, capture_output=True, text=True)
    return {"name": name, "ok": result.returncode == 0, "stdout": result.stdout.strip(), "stderr": result.stderr.strip()}


def query(sql: str, name: str = "default", version: str = DEFAULT_MYSQL_VERSION, home: Path | None = None, database: str | None = None) -> str:
    result = subprocess.run(
        [*client_command(name=name, version=version, home=home, database=database), "--batch", "--raw", "--execute", sql],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout


def query_file(path: Path, name: str = "default", version: str = DEFAULT_MYSQL_VERSION, home: Path | None = None, database: str | None = None) -> subprocess.CompletedProcess[str]:
    with path.expanduser().open("rb") as handle:
        return subprocess.run(client_command(name=name, version=version, home=home, database=database), stdin=handle, check=True, capture_output=True, text=True)


def create_database(database: str, name: str = "default", version: str = DEFAULT_MYSQL_VERSION, home: Path | None = None) -> str:
    escaped = database.replace("`", "``")
    sql = f"CREATE DATABASE IF NOT EXISTS `{escaped}` CHARACTER SET utf8mb4 COLLATE utf8mb4_bin;"
    return query(sql, name=name, version=version, home=home)


def export_layout(name: str = "default", version: str = DEFAULT_MYSQL_VERSION, home: Path | None = None) -> dict[str, str]:
    layout = mysql_layout(name=name, version=version, home=home)
    return {key: str(value) for key, value in asdict(layout).items()}
