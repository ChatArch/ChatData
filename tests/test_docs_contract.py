from pathlib import Path

from chatdata.cli import main, render_cli_tree


PUBLIC_DOCS = (
    "README.md",
    "README.en.md",
    "docs/index.md",
    "docs/index.en.md",
    "docs/cli-tree.md",
    "docs/cli-tree.en.md",
)


def test_mkdocs_material_renderer_and_docs_metadata_contract():
    mkdocs = Path("mkdocs.yml").read_text(encoding="utf-8")
    pyproject = Path("pyproject.toml").read_text(encoding="utf-8")

    assert "site_url: https://arch.gh.wzhecnu.cn/ChatData/" in mkdocs
    assert "name: material" in mkdocs
    assert "mkdocs-material>=9.5,<10.0" in pyproject
    assert "pymdownx.emoji" in mkdocs
    assert "material.extensions.emoji.twemoji" in mkdocs
    assert "material.extensions.emoji.to_svg" in mkdocs
    assert 'Homepage = "https://arch.gh.wzhecnu.cn/ChatData/"' in pyproject
    assert 'Documentation = "https://arch.gh.wzhecnu.cn/ChatData/"' in pyproject
    assert 'Repository = "https://github.com/ChatArch/ChatData"' in pyproject


def test_public_docs_match_live_tree_and_no_material_literals():
    tree = render_cli_tree(main)
    required_lines = [
        "chatdata  # ChatArch database and data management toolkit.",
        "├── --tree  # Print the registered command tree.",
        "└── mysql  # Manage user-level MySQL runtimes and instances.",
        "    │   ├── start [--name <NAME>]  # Start a MySQL user service.",
        "    │   └── logs [--name <NAME>] [--lines <LINES>]  # Show MySQL user service journal logs.",
        "        └── create <DATABASE> [--name <NAME>] [--version <VERSION>] [--home <HOME>]  # Create a utf8mb4 database if it does not exist.",
    ]
    for rel in PUBLIC_DOCS:
        text = Path(rel).read_text(encoding="utf-8")
        assert ":material-" not in text, rel
        assert "template `hello`" not in text, rel
        assert "ChatData" in text, rel
    for rel in ("README.md", "README.en.md", "docs/cli-tree.md", "docs/cli-tree.en.md"):
        text = Path(rel).read_text(encoding="utf-8")
        for line in required_lines:
            assert line in text, f"{rel} missing {line!r}"
    assert tree in Path("docs/cli-tree.md").read_text(encoding="utf-8")
    assert tree in Path("docs/cli-tree.en.md").read_text(encoding="utf-8")
