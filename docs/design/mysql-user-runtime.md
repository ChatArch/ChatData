# MySQL 免 sudo 用户级运行时设计

## 背景

`ChatData` 是 ChatArch 的数据库与数据管理工具。MySQL 是第一条落地的数据库后端能力，但不代表 `ChatData` 只服务于 MySQL。第一版目标是把 MySQL 作为一个可被 ChatData 管理的用户级 runtime：不用 sudo、不用 Docker、不污染系统目录，并能被普通用户通过 CLI 安装、初始化、启动、验证和停止。

本文是第一版设计，不包含实现代码。

## 设计目标

- 免 sudo：不写 `/usr`、`/etc`、系统 systemd unit 或系统用户。
- 免 Docker：直接使用官方二进制 tarball 运行 MySQL。
- 用户级运行：安装、实例、配置、数据、日志、socket 都放在用户可控目录。
- 可验证：每一步都有 `doctor` / `status` / `ping` / `query` 读回证据。
- 可扩展：MySQL 先落地，后续可加 MariaDB、Percona、PostgreSQL、SQLite、DuckDB 等。
- 面向非 DBA 用户：命令暴露任务意图，而不是只暴露底层参数。

## 非目标

- 第一版不做完整数据库平台。
- 第一版不默认暴露公网监听。
- 第一版不管理系统级 MySQL/MariaDB 服务。
- 第一版不做高可用、主从复制、集群或生产级安全审计。
- 第一版不自动修改防火墙、Nginx、systemd system unit 或 root-owned 目录。

## 推荐默认路径

第一版默认使用官方 MySQL Community Server Generic Linux tarball。

原因：

- 用户明确说的是 MySQL，默认应使用真正的 MySQL，而不是一开始用兼容实现替代。
- 官方通用 Linux tarball 可以解压到用户目录运行。
- Ubuntu 22.04 x86_64 + glibc 2.35 这类环境适合使用 `linux-glibc2.28-x86_64` 系列二进制。
- 目标机器应通过 `chatdata mysql doctor` 预先确认常见运行依赖：`libaio`、`libnuma`、OpenSSL、ncurses/tinfo、zlib。
- 若目标机器的 `systemctl --user` 可用，则优先使用用户级 service 管理。

MariaDB 和 Percona 作为后续可选 engine，不作为 v1 默认。

## 目录布局

默认根目录由 ChatEnv/配置决定，建议为：

```text
~/.chatarch/chatdata/
  downloads/
    mysql-8.4.6-linux-glibc2.28-x86_64.tar.xz
    manifests/
      mysql-8.4.6.json
  runtimes/
    mysql/
      8.4.6/
      current -> 8.4.6
  instances/
    mysql/
      default/
        my.cnf
        data/
        run/
          mysql.sock
          mysqld.pid
        logs/
          error.log
          slow.log
        tmp/
  services/
    systemd-user/
      chatdata-mysql-default.service
```

设计原则：

- `runtimes/` 保存解压后的不可变二进制 runtime。
- `instances/` 保存每个 MySQL 实例的配置、数据、日志与 socket。
- `services/` 保存 ChatData 生成的 user-level service 模板或副本。
- 一个 runtime 可以服务多个实例。
- 删除 runtime 前必须确认没有实例使用它。

## 默认实例设置

```text
instance: default
engine: mysql
version: 8.4.x LTS, pinned by manifest
port: 3307
bind-address: 127.0.0.1
socket: ~/.chatarch/chatdata/instances/mysql/default/run/mysql.sock
data: ~/.chatarch/chatdata/instances/mysql/default/data
logs: ~/.chatarch/chatdata/instances/mysql/default/logs
mysqlx: 默认关闭，后续需要时再启用 33060
```

端口默认用 `3307`，不是 `3306`，避免撞系统 MySQL。若用户明确要 3306，CLI 可以先检查端口空闲再允许。

## CLI 树

MySQL 直接作为 `chatdata` 的一级业务分支，因为 `mysql` 名称已经表达了数据库语义，不需要再加一层 `db`。

```text
chatdata
  doctor
  config
  data ...
  mysql
    doctor
    versions
    install
    runtime
      list
      current
      use
      remove
    instance
      init
      list
      show
      config
      remove
    service
      install
      uninstall
      start
      stop
      restart
      status
      logs
    client
      path
      ping
      shell
      query
    database
      list
      create
      drop
    user
      list
      create
      password
      grant
      revoke
    schema
      inspect
      ddl
    backup
      dump
      restore
      verify
```

## v1 命令范围

第一版只做完整闭环，不追求功能多：

```bash
chatdata mysql doctor
chatdata mysql install --version 8.4.6
chatdata mysql instance init --name default --port 3307
chatdata mysql service install --name default
chatdata mysql service start --name default
chatdata mysql service status --name default
chatdata mysql service logs --name default
chatdata mysql client ping --name default
chatdata mysql client query --name default --sql "SELECT VERSION();"
chatdata mysql service stop --name default
```

验收时必须证明：

- 未使用 sudo。
- 未使用 Docker。
- runtime 安装在 ChatData 用户目录。
- data/log/socket/config 都在 ChatData 管理目录。
- `systemctl --user` unit 可读回。
- `mysqladmin ping` 成功。
- `SELECT VERSION();` 成功。
- 最后状态可停止，或由用户明确要求保留运行。

## 安装流程

`chatdata mysql install` 负责下载、校验和解压 runtime：

1. 读取版本 manifest，确定 URL、文件名、预期 checksum。
2. 下载到 `downloads/` 临时文件。
3. 校验 checksum；无法校验时默认失败，除非用户显式允许不安全继续。
4. 安全解压：拒绝绝对路径、`..`、symlink/hardlink、非普通文件等危险 tar 成员。
5. 解压到 `runtimes/mysql/<version>` 的临时目录，完成后原子切换。
6. 更新 `current` symlink 或 manifest。
7. 运行 `mysqld --version` 做 runtime smoke。

## 实例初始化流程

`chatdata mysql instance init` 负责生成实例目录和 `my.cnf`：

1. 创建实例目录：`data/`、`logs/`、`run/`、`tmp/`。
2. 生成 `my.cnf`，写入 `basedir`、`datadir`、`socket`、`pid-file`、`log-error`、`port`、`bind-address`。
3. 检查端口、socket 路径长度、目录权限。
4. 调用 `mysqld --initialize-insecure` 或安全初始化策略。
5. 写入实例 manifest：runtime version、port、socket、created time。

第一版可以使用 `--initialize-insecure`，但必须满足：

- 默认只绑定 `127.0.0.1`。
- 默认本地 socket/localhost 使用。
- CLI 明确标记这是本地开发/实验实例。
- 后续提供 root 密码设置或凭据管理命令。

## 用户级 service

`chatdata mysql service install` 生成并安装 user-level systemd unit：

```text
~/.config/systemd/user/chatdata-mysql-default.service
```

unit 只引用用户目录中的 runtime 与 instance：

```ini
[Unit]
Description=ChatData MySQL instance default
After=network.target

[Service]
Type=simple
ExecStart=<runtime>/bin/mysqld --defaults-file=<instance>/my.cnf
ExecStop=<runtime>/bin/mysqladmin --socket=<instance>/run/mysql.sock shutdown
Restart=on-failure
WorkingDirectory=<instance>

[Install]
WantedBy=default.target
```

安装后执行：

```bash
systemctl --user daemon-reload
systemctl --user enable chatdata-mysql-default.service
```

`start/status/stop/logs` 分别封装 user systemd 和 MySQL 自身读回：

- `systemctl --user status ...`
- `journalctl --user -u ...`
- error log tail
- `mysqladmin ping`

## 安全与凭据

- 密码不能通过 argv 传入。
- 支持 `--root-password-env NAME` 或 ChatEnv sensitive field。
- 默认输出 mask 敏感信息。
- `drop/remove/restore` 类操作需要确认或 `--yes`。
- 删除实例前应提示备份。
- 默认只监听 localhost。

## 非 DBA 用户功能

后续高层能力应以任务命名：

- `doctor`：这台机器能不能免 sudo 跑 MySQL？缺什么？端口冲突吗？
- `install`：把 MySQL 安全放进 ChatArch 用户空间。
- `instance init`：创建一个本地数据库实例。
- `service start/status/stop/logs`：像管理应用一样管理 MySQL。
- `client query`：跑一条 SQL 验证可用。
- `database create/list/drop`：管理数据库。
- `user create/grant`：创建应用用户和权限。
- `backup dump/restore/verify`：避免误删数据。
- `schema inspect/ddl`：理解库里有哪些表、列、索引。

## 实现顺序

1. `mysql doctor`：检查 OS/arch/lib/port/systemd/path。
2. `mysql install`：下载、校验、安全解压官方 tarball。
3. `mysql instance init`：生成实例目录与 `my.cnf`，初始化 data dir。
4. `mysql service install/start/status/stop/logs`：用户级 systemd。
5. `mysql client ping/query`：证明实例可用。
6. 再扩展 `database`、`user`、`backup`、`schema`。

## 服务器原型计划

在进入正式代码实现前，可以先在本地任务工作区做一次 task-local 原型：

```text
<workspace>/projects/<chatdata-mysql-prototype>/playground/manual-runtime/
```

原型不写 `~/.chatarch/chatdata`，先证明下载、解压、初始化、启动、查询、停止的基本链路。成功后再把稳定路径提升为 `ChatData` CLI 实现。
