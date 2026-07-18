# ChatData 文档

这里收纳 `ChatData` 的长期维护文档。

## 本地预览

```bash
pip install -e ".[docs]"
mkdocs serve
```

## 设计文档

- [MySQL 快速认知与常见概念](getting-started/mysql-basics.md)：面向新手理解 SQL 能力、MySQL 基础对象、服务/实例/端口/socket/事务/索引/备份等概念。
- [MySQL 用户级运行时](operations/mysql-runtime.md)：第一版 `chatdata mysql ...` 安装、初始化、启动、查询和导入流程。
- [MySQL 免 sudo 用户级运行时设计](design/mysql-user-runtime.md)：`chatdata mysql ...` 的第一版 runtime、实例、用户级 service 与验收方案。

英文版见：[index.en.md](index.en.md)。
