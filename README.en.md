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
chatdata
├── --help
├── --version
├── --tree
└── mysql ...
```

## Documentation

- Chinese documentation: https://arch.gh.wzhecnu.cn/ChatData/
- CLI tree: https://arch.gh.wzhecnu.cn/ChatData/en/cli-tree/
- English documentation: https://arch.gh.wzhecnu.cn/ChatData/en/

## Development Notes

Read `DEVELOP.md` and `AGENTS.md` before expanding the CLI. New commands should update tests, `chatdata --tree`, documentation, and the changelog in the same change.
