# MySQL 用户级运行时

ChatData 第一版 MySQL 能力已经落到 `chatdata mysql ...`。它的定位是给 ChatArch/ChatTea 这类本机服务提供一个免 sudo、免 Docker 的数据库运行时。

## 目录布局

默认根目录来自 ChatEnv 的 ChatArch home：

```text
~/.chatarch/chatdata/
  downloads/                         # 官方 MySQL tarball 和校验文件
  runtimes/mysql/8.4.6/               # 解压后的 MySQL runtime
  runtimes/mysql/current -> 8.4.6
  instances/mysql/default/
    my.cnf
    data/
    run/mysql.sock
    run/mysqld.pid
    logs/error.log
    tmp/
```

第一版默认 MySQL 版本是 `8.4.6`，默认实例名是 `default`，默认端口是 `3307`，只监听 `127.0.0.1`。

## 安装 runtime

```bash
chatdata mysql doctor
chatdata mysql install --version 8.4.6
```

`install` 会从 MySQL 官方 archive 下载 generic Linux tarball，读取 `.md5` sidecar 做校验，安全解压到 `~/.chatarch/chatdata/runtimes/mysql/<version>`，然后运行 `mysqld --version` 做 smoke。

## 初始化并启动实例

```bash
chatdata mysql instance init --name default --version 8.4.6 --port 3307
chatdata mysql service install --name default --version 8.4.6
chatdata mysql service start --name default
chatdata mysql client ping --name default --version 8.4.6
chatdata mysql client query --name default --version 8.4.6 --sql 'SELECT VERSION();'
```

实例使用 `mysqld --initialize-insecure` 初始化，本地 root 默认空密码，适合作为本机开发/自托管服务的初版能力。默认只通过 localhost/socket 使用，不对公网开放。

## 数据库和导入

给 Gitea 这类服务创建 database：

```bash
chatdata mysql database create gitea --name default --version 8.4.6
```

默认使用：

```sql
CHARACTER SET utf8mb4 COLLATE utf8mb4_bin
```

`utf8mb4_bin` 是大小写敏感 collation，避免 Gitea 在启动/migrate 时提示 case-insensitive collation 风险。

实例名和 database 名会用于本地路径、systemd unit 名或 SQL identifier。第一版只接受字母、数字、点、下划线和短横线，避免路径穿越或意外 SQL 名称。

ChatData Python API 还提供 `ensure_database_user(...)`，用于上层工具创建业务用户并授予单库权限。ChatTea 的 `--mysql-user` / `--mysql-password-env` 就会调用这个 helper；密码通过 stdin 写给 `mysql` client，不会出现在命令行参数里。

导入 SQL：

```bash
chatdata mysql client import \
  --name default \
  --version 8.4.6 \
  --database gitea \
  --file gitea-db.sql
```

执行查询时也可以选择 database：

```bash
chatdata mysql client query \
  --name default \
  --version 8.4.6 \
  --database gitea \
  --sql 'SHOW TABLES;'
```

## 运维命令

```bash
chatdata mysql service status --name default
chatdata mysql service logs --name default --lines 100
chatdata mysql service restart --name default
chatdata mysql service stop --name default
```

`service install` 写入 user systemd unit：

```text
~/.config/systemd/user/chatdata-mysql-default.service
```

它只引用用户目录里的 runtime 和 instance，不写系统目录。
