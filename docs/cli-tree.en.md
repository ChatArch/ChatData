# CLI Tree

`chatdata --tree` renders the current executable command surface from the Click registry. This page lists implemented commands only; future commands in design notes are not part of the current CLI.

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

## Update Rules

- When CLI commands are added, removed, or renamed, update the `chatdata --tree` tests in the same change.
- The `--tree` output must come from the real Click command registry, not copied README or documentation examples.
- When a future database backend is implemented, register the real CLI command first and then refresh this page from `chatdata --tree`.
