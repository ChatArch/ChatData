# Changelog

## YYYY-MM-DD

### Added

- Added first-version `chatdata mysql ...` user-level MySQL runtime commands for doctor, install, instance init, user systemd service, ping/query/import, and database create.
- Added a Python `ensure_database_user(...)` helper for upper layers that need to create a service user and grant database access without putting passwords in process arguments.
- Documented the MySQL runtime workflow under `docs/operations/mysql-runtime.md`.

### Changed

### Fixed

- Rejected unsafe MySQL instance and database names before they become local paths, systemd unit names, or SQL identifiers.
- Escaped MySQL string literals and `--database` client arguments more defensively before issuing helper SQL.
- Made forced instance initialization clear the existing data directory before running `mysqld --initialize-insecure`.
