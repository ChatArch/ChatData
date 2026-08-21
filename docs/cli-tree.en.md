# CLI Tree

ChatStyle renders the current executable command surface from the Click registry. `chatdata --tree` includes parameter signatures, while `chatdata --tree-brief` keeps the same nodes and descriptions without signatures. This page lists implemented commands only; future commands in design notes are not part of the current CLI.

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

## Update Rules

- When CLI commands are added, removed, or renamed, update the `chatdata --tree` and `chatdata --tree-brief` tests in the same change.
- Both tree outputs must be rendered by ChatStyle from the real Click command registry, not copied README or documentation examples.
- When a future database backend is implemented, register the real CLI command first and then refresh this page from `chatdata --tree`.
