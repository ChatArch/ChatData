# ChatData 文档

ChatData 是 ChatArch 的数据库与数据管理工具。当前已实现的是免 sudo、免 Docker 的用户级 MySQL runtime：安装 MySQL 二进制、初始化实例、安装用户级 service、执行 ping/query/import，以及创建数据库。

<div class="grid cards" markdown>

-   **命令入口**

    ---

    从 [`CLI 树`](cli-tree.md) 查看当前真实命令面，或在本机运行：

    ```bash
    chatdata --tree
    ```

-   **MySQL 运行时**

    ---

    按 [`MySQL 用户级运行时`](operations/mysql-runtime.md) 完成安装、初始化、启动、查询和导入。

-   **新手认知**

    ---

    [`MySQL 快速认知与常见概念`](getting-started/mysql-basics.md) 面向第一次系统接触 MySQL 的用户。

-   **设计边界**

    ---

    [`MySQL 免 sudo 用户级运行时设计`](design/mysql-user-runtime.md) 说明目标、非目标和扩展方向。

</div>

## 本地预览

```bash
pip install -e ".[docs]"
mkdocs serve
```
