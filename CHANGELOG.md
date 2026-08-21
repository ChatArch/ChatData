# Changelog

## 0.1.4 - 2026-08-21

### Added

- Add `chatdata --tree-brief` for a compact view of the registered command surface.
- Add installed-console-script CI coverage for the brief tree contract.

### Changed

- Replace the package-local Click tree renderer with ChatStyle's shared `add_tree_option()` runtime.
- Align runtime dependencies with `chatstyle>=0.2.0,<0.3.0` and `chatenv>=0.2.10,<0.3.0`.
- Refresh bilingual CLI documentation from the shared full and brief tree renderer.

## 0.1.3 - 2026-08-12

### Added

- Add the MkDocs Material emoji renderer baseline so Material icon shorthand cannot leak into generated/live docs.
- Add docs and workflow contract tests for renderer config, README/live CLI tree alignment, publish guards, and installed CLI smoke.

### Changed

- Harden package publishing with a default-branch ancestry guard before OIDC PyPI publishing.
- Expand CI to Python 3.10 / 3.11 / 3.12 and smoke installed `chatdata --version` and `chatdata --tree` entry points.
- Point package homepage and documentation metadata at the ChatArch docs domain.
- Sync README / README.en CLI examples to the full live runtime tree.

## 0.1.2 - 2026-08-11

### Added

- Add runtime-generated `chatdata --tree` support backed by the registered Click command tree.
- Add CLI tests for `--help`, `--tree`, MySQL command coverage, and scaffold sample command absence.

### Changed

- Align package documentation metadata and MkDocs site URL with the ChatArch public docs domain.
- Bound Click and docs dependency windows for repeatable patch release gates.

## 2026-07-18

### Added

- Added first-version `chatdata mysql ...` user-level MySQL runtime commands for doctor, install, instance init, user systemd service, ping/query/import, and database create.
- Added a Python `ensure_database_user(...)` helper for upper layers that need to create a service user and grant database access without putting passwords in process arguments.
- Documented the MySQL runtime workflow under `docs/operations/mysql-runtime.md`.

### Changed

### Fixed

- Rejected unsafe MySQL instance and database names before they become local paths, systemd unit names, or SQL identifiers.
- Escaped MySQL string literals and `--database` client arguments more defensively before issuing helper SQL.
- Made forced instance initialization clear the existing data directory before running `mysqld --initialize-insecure`.
