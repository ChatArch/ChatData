# CLI 树

ChatStyle 从 Click 注册表实时渲染当前可执行命令面。`chatdata --tree` 包含参数签名，`chatdata --tree-brief` 保留相同节点和说明但省略签名。这个页面只列已实现命令；设计文档里的未来命令不视为当前 CLI。

```text
chatdata
├── --help  # Show this message and exit.
├── --version  # Show the version and exit.
├── --tree  # Print the registered CLI tree and exit.
├── --tree-brief  # Print the registered CLI tree without parameter signatures and exit.
└── mysql  # Manage user-level MySQL runtimes and instances.
    ├── client  # Run MySQL client checks and SQL.
    │   ├── import [--name NAME] [--version VERSION] [--home HOME] [--database DATABASE] [--file SQL-FILE] [--json-output]  # Import a SQL file through the instance socket.
    │   ├── ping [--name NAME] [--version VERSION] [--home HOME] [--json-output]  # Run mysqladmin ping through the instance socket.
    │   └── query [--name NAME] [--version VERSION] [--home HOME] [--database DATABASE] [--sql SQL]  # Execute one SQL statement through the instance socket.
    ├── database  # Manage databases on a MySQL instance.
    │   └── create <DATABASE> [--name NAME] [--version VERSION] [--home HOME]  # Create a utf8mb4 database if it does not exist.
    ├── doctor [--port PORT] [--bind-address BIND-ADDRESS] [--json-output]  # Check host compatibility for the user-level MySQL runtime.
    ├── install [--version VERSION] [--home HOME] [--force] [--json-output]  # Download, verify, and install a MySQL binary tarball under ChatData home.
    ├── instance  # Manage MySQL instance directories and config.
    │   ├── init [--name NAME] [--version VERSION] [--home HOME] [--port PORT] [--bind-address BIND-ADDRESS] [--initialize] [--force] [--json-output]  # Create a user-level MySQL instance and initialize its data directory.
    │   └── show [--name NAME] [--version VERSION] [--home HOME] [--json-output]  # Show MySQL instance layout paths.
    ├── runtime  # Inspect installed MySQL runtime paths.
    │   └── path [--version VERSION] [--home HOME] [--json-output]  # Show MySQL runtime and instance layout paths.
    └── service  # Manage user-level MySQL systemd services.
        ├── install [--name NAME] [--version VERSION] [--home HOME] [--json-output]  # Install a systemd user service for a MySQL instance.
        ├── logs [--name NAME] [--lines LINES]  # Show MySQL user service journal logs.
        ├── restart [--name NAME]  # Restart a MySQL user service.
        ├── start [--name NAME]  # Start a MySQL user service.
        ├── status [--name NAME] [--json-output]  # Show MySQL user service active state.
        └── stop [--name NAME]  # Stop a MySQL user service.
```

## 更新规则

- 新增、删除或重命名 CLI 命令时，同步更新 `chatdata --tree` 和 `chatdata --tree-brief` 测试。
- 两种 tree 输出必须由 ChatStyle 从真实 Click command registry 渲染，不能从 README 或文档示例复制。
- 若后续新增数据库后端，先在 CLI 中注册真实命令，再让本页面跟随 `chatdata --tree` 输出更新。
