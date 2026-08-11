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

ChatArch 数据库与数据管理工具。当前实现聚焦用户级 MySQL runtime：安装 MySQL 二进制、初始化实例、管理用户级 service、执行 ping/query/import，并创建数据库。

## 快速开始

```bash
pip install ChatData
chatdata --version
chatdata --tree
chatdata mysql --help
```

开发本仓库时：

```bash
pip install -e ".[dev,docs]"
python -m pytest -q
python -m build
mkdocs build --strict
```

## CLI 入口

当前命令树来自真实 Click registry，可通过 `chatdata --tree` 回读；文档站也提供 [CLI 树](https://arch.gh.wzhecnu.cn/ChatData/cli-tree/) 页面。

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

## 文档

- 中文文档：https://arch.gh.wzhecnu.cn/ChatData/
- CLI 树：https://arch.gh.wzhecnu.cn/ChatData/cli-tree/
- English documentation: https://arch.gh.wzhecnu.cn/ChatData/en/

## 开发说明

扩展 CLI 前，先阅读 `DEVELOP.md` 和 `AGENTS.md`。新增命令时应同步测试、`chatdata --tree`、文档和 changelog。
