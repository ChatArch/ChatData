<div align="center">
    <a href="https://pypi.python.org/pypi/ChatData">
        <img src="https://img.shields.io/pypi/v/ChatData.svg" alt="PyPI version" />
    </a>
    <a href="https://github.com/ChatArch/ChatData/actions/workflows/ci.yml">
        <img src="https://github.com/ChatArch/ChatData/actions/workflows/ci.yml/badge.svg" alt="Tests" />
    </a>
    <a href="https://arch.gh.wzhecnu.cn/ChatData/">
        <img src="https://img.shields.io/badge/docs-mkdocs-blue.svg" alt="Documentation" />
    </a>
</div>

<div align="center">

[English](README.en.md) | [简体中文](README.md)
</div>

# ChatData

ChatArch database and data-management toolkit. The current implementation focuses on a user-level MySQL runtime: install MySQL binaries, initialize instances, manage user services, run ping/query/import, and create databases.

## Quick Start

```bash
pip install ChatData
chatdata --version
chatdata --tree
chatdata mysql --help
```

For repository development:

```bash
pip install -e ".[dev,docs]"
python -m pytest -q
python -m build
mkdocs build --strict
```

## CLI Entry Point

The current command tree is rendered from the real Click registry and can be read back with `chatdata --tree`; the documentation site also provides a [CLI Tree](https://arch.gh.wzhecnu.cn/ChatData/en/cli-tree/) page.

```text
chatdata  # ChatArch database and data management toolkit.
├── --help  # Show this help message.
├── --version  # Show the installed package version.
├── --tree  # Print the registered command tree.
└── mysql  # Manage user-level MySQL runtimes and instances.
    ├── doctor [--port <PORT>] [--bind-address <BIND-ADDRESS>] [--json-output]  # Check host compatibility for the user-level MySQL runtime.
    ├── install [--version <VERSION>] [--home <HOME>] [--force] [--json-output]  # Download, verify, and install a MySQL binary tarball under ChatData home.
    ├── runtime  # Inspect installed MySQL runtime paths.
    │   └── path [--version <VERSION>] [--home <HOME>] [--json-output]  # Show MySQL runtime and instance layout paths.
    ├── instance  # Manage MySQL instance directories and config.
    │   ├── init [--name <NAME>] [--version <VERSION>] [--home <HOME>] [--port <PORT>] [--bind-address <BIND-ADDRESS>] [--initialize/--no-initialize] [--force] [--json-output]  # Create a user-level MySQL instance and initialize its data directory.
    │   └── show [--name <NAME>] [--version <VERSION>] [--home <HOME>] [--json-output]  # Show MySQL instance layout paths.
    ├── service  # Manage user-level MySQL systemd services.
    │   ├── install [--name <NAME>] [--version <VERSION>] [--home <HOME>] [--json-output]  # Install a systemd user service for a MySQL instance.
    │   ├── start [--name <NAME>]  # Start a MySQL user service.
    │   ├── stop [--name <NAME>]  # Stop a MySQL user service.
    │   ├── restart [--name <NAME>]  # Restart a MySQL user service.
    │   ├── status [--name <NAME>] [--json-output]  # Show MySQL user service active state.
    │   └── logs [--name <NAME>] [--lines <LINES>]  # Show MySQL user service journal logs.
    ├── client  # Run MySQL client checks and SQL.
    │   ├── ping [--name <NAME>] [--version <VERSION>] [--home <HOME>] [--json-output]  # Run mysqladmin ping through the instance socket.
    │   ├── query [--name <NAME>] [--version <VERSION>] [--home <HOME>] [--database <DATABASE>] [--sql <SQL>]  # Execute one SQL statement through the instance socket.
    │   └── import [--name <NAME>] [--version <VERSION>] [--home <HOME>] [--database <DATABASE>] [--file <SQL-FILE>] [--json-output]  # Import a SQL file through the instance socket.
    └── database  # Manage databases on a MySQL instance.
        └── create <DATABASE> [--name <NAME>] [--version <VERSION>] [--home <HOME>]  # Create a utf8mb4 database if it does not exist.
```

## Documentation

- Chinese documentation: https://arch.gh.wzhecnu.cn/ChatData/
- CLI tree: https://arch.gh.wzhecnu.cn/ChatData/en/cli-tree/
- English documentation: https://arch.gh.wzhecnu.cn/ChatData/en/

## Development Notes

Read `DEVELOP.md` and `AGENTS.md` before expanding the CLI. New commands should update tests, `chatdata --tree`, documentation, and the changelog in the same change.
