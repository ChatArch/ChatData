# ChatData Documentation

ChatData is the ChatArch database and data-management toolkit. The current implemented scope is a no-sudo, no-Docker, user-level MySQL runtime: install MySQL binaries, initialize instances, install user services, run ping/query/import, and create databases.

<div class="grid cards" markdown>

-   **Command Surface**

    ---

    Read the current executable command surface in [`CLI Tree`](cli-tree.md), or run locally:

    ```bash
    chatdata --tree
    chatdata --tree-brief
    ```

-   **MySQL Runtime**

    ---

    Use [`MySQL user-level runtime`](operations/mysql-runtime.md) for install, init, service, query, and import workflows.

-   **Beginner Model**

    ---

    [`MySQL basics for beginners`](getting-started/mysql-basics.md) introduces the common SQL/MySQL concepts used by ChatData.

-   **Design Boundary**

    ---

    [`MySQL no-sudo user runtime design`](design/mysql-user-runtime.md) records goals, non-goals, and extension directions.

</div>

## Local Preview

```bash
pip install -e ".[docs]"
mkdocs serve
```
