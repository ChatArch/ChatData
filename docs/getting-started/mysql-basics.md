# MySQL 快速认知与常见概念

这篇文档面向第一次系统接触 MySQL 的 ChatData 用户。目标不是教完整 SQL 课程，而是帮助你快速建立心智模型：MySQL 是什么、SQL 能做什么、常见名词是什么意思、未来 `chatdata mysql ...` 应该帮助你完成哪些任务。

## 核心模型

MySQL 可以先理解成三层：

```text
A. MySQL Server
   长期运行的数据库服务进程，负责保存数据、执行 SQL、管理账号、处理并发和事务。

B. Database / Schema / Table
   数据组织结构。一个 server 里有多个 database；database 里有多张 table；table 里有 column 和 row。

C. SQL
   和数据库沟通的语言。你用 SQL 创建表、写入数据、查询数据、修改数据、控制权限和事务。
```

ChatData 第一版 MySQL 能力也会按这个模型落地：

```text
chatdata mysql install        # 准备 MySQL Server runtime
chatdata mysql instance init  # 创建一个 database server 实例
chatdata mysql service start  # 启动这个实例
chatdata mysql client query   # 对实例执行 SQL
```

## SQL 和 MySQL 的区别

```text
SQL
  一门数据库查询和管理语言。
  多数关系型数据库都支持 SQL，例如 MySQL、PostgreSQL、SQLite、MariaDB、Oracle。

MySQL
  一个具体的关系型数据库系统。
  它支持 SQL，也提供自己的服务进程、账号权限、存储引擎、备份工具和运维方式。
```

所以：

- “写 SQL”通常是在操作表、数据和查询结果。
- “管理 MySQL”还包括安装 server、启动服务、管理用户、备份、查看日志和调性能。

## SQL 支持哪些核心能力

SQL 常见能力可以按任务分组。

### 1. 查询数据：SELECT

查询是 SQL 最常用的能力。

```sql
SELECT id, name, created_at
FROM users
WHERE status = 'active'
ORDER BY created_at DESC
LIMIT 20;
```

相关概念：

- `SELECT`：选择要看的列。
- `FROM`：从哪张表查。
- `WHERE`：过滤条件。
- `ORDER BY`：排序。
- `LIMIT`：限制返回数量。

ChatData 可以把这类能力包装成：

```text
chatdata mysql client query --sql "SELECT ..."
chatdata mysql schema inspect
```

### 2. 汇总和统计：GROUP BY / 聚合函数

用于回答“有多少”“总和是多少”“平均值是多少”。

```sql
SELECT status, COUNT(*) AS total
FROM orders
GROUP BY status;
```

常见聚合函数：

```text
COUNT(*)    计数
SUM(x)      求和
AVG(x)      平均值
MIN(x)      最小值
MAX(x)      最大值
```

这类能力适合后续做 ChatData 的“数据概览 / profiling”。

### 3. 多表关联：JOIN

真实业务数据通常分散在多张表。`JOIN` 用来把表连起来。

```sql
SELECT users.name, orders.total
FROM users
JOIN orders ON orders.user_id = users.id;
```

常见类型：

- `INNER JOIN`：只保留两边都匹配的数据。
- `LEFT JOIN`：左表都保留，右表没有则为空。
- `RIGHT JOIN`：右表都保留。

新手常见困惑：JOIN 不是“复制表”，而是按关联条件临时组合查询结果。

### 4. 写入和修改数据：INSERT / UPDATE / DELETE

```sql
INSERT INTO users (name, email) VALUES ('Alice', 'alice@example.com');

UPDATE users SET status = 'inactive' WHERE id = 1;

DELETE FROM users WHERE id = 1;
```

这些命令会改变数据。ChatData 后续做这类命令时应该默认更谨慎：

- 先显示影响范围。
- 支持 dry-run 或确认。
- 对危险操作要求 `--yes`。
- 重要操作前提示备份。

### 5. 定义结构：CREATE / ALTER / DROP

这类 SQL 管理数据库结构，常叫 DDL。

```sql
CREATE DATABASE app;

CREATE TABLE users (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(255) NOT NULL,
  email VARCHAR(255) UNIQUE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

ALTER TABLE users ADD COLUMN status VARCHAR(32);

DROP TABLE users;
```

常见对象：

- database / schema：数据库命名空间。
- table：表。
- column：列。
- index：索引。
- constraint：约束。
- view：视图。

ChatData 可以把这些包装成：

```text
chatdata mysql database list/create/drop
chatdata mysql schema inspect/ddl
```

### 6. 约束：让数据不乱

约束负责保证数据质量。

```text
PRIMARY KEY     主键，每行唯一身份
UNIQUE          唯一约束，例如 email 不能重复
NOT NULL        不能为空
DEFAULT         默认值
FOREIGN KEY     外键，表达表之间的关系
CHECK           检查约束，MySQL 新版本支持
```

新手理解：约束是数据库帮你守规则，不要只靠应用代码记得检查。

### 7. 索引：让查询更快

索引类似书的目录。没有索引时，数据库可能要扫整张表；有合适索引时，可以快速定位。

```sql
CREATE INDEX idx_users_email ON users(email);
```

索引的代价：

- 查询可能更快。
- 写入、更新、删除可能稍慢。
- 占用额外磁盘。

ChatData 后续可以做：

```text
chatdata mysql schema inspect
chatdata mysql query explain
```

帮助用户理解“哪些查询慢、是否缺索引”。

### 8. 事务：一组操作要么都成功，要么都失败

事务用于保护一致性。

```sql
START TRANSACTION;
UPDATE accounts SET balance = balance - 100 WHERE id = 1;
UPDATE accounts SET balance = balance + 100 WHERE id = 2;
COMMIT;
```

如果中间失败：

```sql
ROLLBACK;
```

四个常见词：

```text
BEGIN / START TRANSACTION  开始事务
COMMIT                     确认提交
ROLLBACK                   回滚
isolation level            隔离级别，控制并发可见性
```

新手理解：转账、库存扣减、订单创建这类多步操作通常需要事务。

### 9. 权限和用户：谁能做什么

MySQL 有自己的账号和权限系统。

```sql
CREATE USER 'app'@'localhost' IDENTIFIED BY '***';
GRANT SELECT, INSERT, UPDATE ON app.* TO 'app'@'localhost';
REVOKE DELETE ON app.* FROM 'app'@'localhost';
```

基本模型：

```text
user      用户名
host      允许从哪里连接，例如 localhost 或 %
privilege 权限，例如 SELECT / INSERT / CREATE / DROP
scope     权限范围，例如 *.* / app.* / app.users
```

ChatData 后续可以提供更安全的任务型命令：

```text
chatdata mysql user create
chatdata mysql user grant
chatdata mysql user password
```

密码必须来自 env 或 ChatEnv sensitive field，不应该放在命令行参数里。

### 10. 视图、存储过程、触发器和事件

这些是更高级的数据库内逻辑。

```text
VIEW              保存一个查询视角，像虚拟表
PROCEDURE          存储过程，一段数据库端逻辑
FUNCTION           存储函数，返回值
TRIGGER            表发生写入/更新/删除时自动执行
EVENT              定时任务，按时间执行 SQL
```

第一版 ChatData 不需要马上管理这些，但 `schema inspect` 后续应该能识别它们。

### 11. 查询计划和性能：EXPLAIN

`EXPLAIN` 用来理解数据库准备怎样执行查询。

```sql
EXPLAIN SELECT * FROM users WHERE email = 'alice@example.com';
```

常见用途：

- 是否用了索引？
- 是否扫了很多行？
- JOIN 顺序是否合理？
- 为什么查询慢？

ChatData 后续可以提供：

```text
chatdata mysql query explain
chatdata mysql doctor slow-query
```

## MySQL 常见概念

### Server / Instance

```text
server
  MySQL 服务程序本身，通常是 mysqld。

instance
  一个具体运行中的 MySQL 实例，包含自己的配置、数据目录、端口、socket 和日志。
```

同一个机器上可以跑多个实例，只要端口、socket、数据目录不同。

ChatData 里建议叫：

```text
chatdata mysql instance init --name default
chatdata mysql service start --name default
```

### Client / Server

```text
mysqld      服务端进程，长期运行，保存和处理数据
mysql       命令行客户端，用来连接 server 执行 SQL
mysqladmin  管理客户端，用来 ping、shutdown、看状态
```

ChatData 不应该让新手直接记所有二进制名字，而是封装成任务：

```text
chatdata mysql client ping
chatdata mysql client query
chatdata mysql service stop
```

### Port / Socket

MySQL 可以通过两种常见方式连接：

```text
TCP port
  例如 127.0.0.1:3307。适合跨进程、跨语言、也可远程连接。

Unix socket
  例如 ~/.chatarch/chatdata/instances/mysql/default/run/mysql.sock。
  只在本机使用，通常更安全、更直接。
```

ChatData 本地实例默认应该：

- 绑定 `127.0.0.1`，不暴露公网。
- 使用 `3307`，避免撞系统 3306。
- 提供 socket 路径，方便本机管理。

### Database / Schema

在 MySQL 里，`database` 和 `schema` 基本可以当成同义词。

```sql
CREATE DATABASE app;
USE app;
SHOW TABLES;
```

新手可以理解为：database 是一组表的命名空间。

### Table / Row / Column

```text
table   表，例如 users
row     行，一条记录
column  列，一个字段，例如 id/name/email
```

例子：

```text
users 表
+----+-------+-------------------+
| id | name  | email             |
+----+-------+-------------------+
| 1  | Alice | alice@example.com |
+----+-------+-------------------+
```

### Primary Key / Foreign Key

```text
primary key
  一张表里每一行的唯一 ID。

foreign key
  一张表引用另一张表的 ID，用来表达关系。
```

例如 `orders.user_id` 指向 `users.id`。

### Storage Engine

MySQL 的表背后由 storage engine 负责存储。

最常见的是：

```text
InnoDB
  默认主力引擎。支持事务、行级锁、外键，适合绝大多数场景。
```

第一版 ChatData 默认不需要让用户选择 storage engine，使用 MySQL 默认即可。

### Backup / Dump / Restore

```text
backup / dump
  把数据库内容导出成文件。

restore
  从备份文件恢复数据。
```

常见工具：

```text
mysqldump
  逻辑备份工具，导出 SQL 文件。
```

ChatData 后续要把备份做成安全任务：

```text
chatdata mysql backup dump
chatdata mysql backup restore
chatdata mysql backup verify
```

恢复和删除都应强确认。

### Logs

MySQL 常见日志：

```text
error log      启动失败、崩溃、配置错误
slow query log 慢查询
binary log     数据变更日志，用于复制和恢复，第一版可先不启用
```

ChatData 第一版至少应支持：

```text
chatdata mysql service logs
```

先看 error log，后续再加 slow query log。

## 从 ChatData 产品角度看功能分层

第一层：把 MySQL 跑起来。

```text
install -> instance init -> service start -> ping -> query -> stop
```

第二层：让用户能安全使用本地数据库。

```text
database create/list
user create/grant
schema inspect
backup dump/restore
```

第三层：帮助用户理解和优化数据库。

```text
query explain
slow-query report
index suggestion
schema drift check
```

第四层：扩展到其它数据库和数据处理。

```text
mariadb / postgres / sqlite / duckdb
import / export / profile / transform
```

## 新手常见误区

- SQL 不是 MySQL；SQL 是语言，MySQL 是系统。
- database 不是 server；一个 server 里可以有多个 database。
- table 不是文件；它是数据库内部管理的数据结构。
- index 不是越多越好；它加速查询，也增加写入和存储成本。
- `DELETE` 和 `DROP` 都危险；前者删数据，后者删结构。
- 事务不是自动万能；需要明确开始、提交、回滚，并理解隔离级别。
- root 用户不应该给应用长期使用；应用应有独立低权限用户。
- 本地测试默认只监听 `127.0.0.1`，不要轻易开放公网。
- 备份不是复制 data 目录这么简单；优先用明确的 dump/restore 流程。

## ChatData 第一版应该教会用户什么

第一版文档和 CLI 应让用户完成并理解这条链路：

```text
1. 我能在没有 sudo / Docker 的机器上安装 MySQL runtime。
2. 我能创建一个本地 MySQL 实例。
3. 我知道它的端口、socket、data dir、log dir 在哪里。
4. 我能用 user-level service 启停它。
5. 我能 ping 它，执行 SELECT VERSION();。
6. 我知道后续创建 database、user、backup、schema inspect 是在这个实例之上继续做。
```

这就是 `chatdata mysql ...` 第一阶段的产品边界。
