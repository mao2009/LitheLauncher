# Research & Design Decisions: code-first-db-migration

---
**Purpose**: Capture discovery findings, architectural investigations, and rationale that inform the technical design for code-first DB migration.

---

## Summary
- **Feature**: `code-first-db-migration`
- **Discovery Scope**: Extension (Refactoring core database logic)
- **Key Findings**:
  - Current migration logic is procedural and embedded in `initialize_database`.
  - SQLite lacks comprehensive `ALTER TABLE` support (e.g., dropping columns), making physical backups essential for rollback.
  - Integration must handle existing "partially migrated" databases smoothly.

## Research Log

### SQLite Migration Best Practices
- **Context**: Ensuring atomicity and safety during schema changes.
- **Sources Consulted**: SQLite Documentation, general DB migration patterns.
- **Findings**:
  - `ALTER TABLE` is limited; complex changes often require creating a new table and copying data.
  - Transactions cover schema changes in SQLite, but a failed migration might still leave the file in a state that's hard to debug without a physical copy.
- **Implications**: Implementing a pre-migration backup (`.bak` file) is a high-priority safety requirement.

### Code-First Schema Definition in Python
- **Context**: Moving from raw SQL strings to structured code.
- **Sources Consulted**: SQLAlchemy, Alembic (for inspiration, not as dependencies).
- **Findings**: A dictionary-based approach mapping versions to SQL "up" scripts is sufficient for the current scale of LitheLauncher without adding heavy ORM dependencies.
- **Implications**: `DatabaseManager` will hold a `MIGRATIONS` map.

## Architecture Pattern Evaluation

| Option | Description | Strengths | Risks / Limitations | Notes |
|--------|-------------|-----------|---------------------|-------|
| Lightweight Manager | Dedicated class inside `database.py` | Low overhead, preserves module structure | File might become large | Recommended |
| Full Migration Engine | Separate module with CLI tools | Very clean separation | Overkill for a simple desktop app | Deferred |

## Design Decisions

### Decision: Version-Based Sequential Migration
- **Context**: Need to support upgrading from any previous version to the latest.
- **Selected Approach**: `schema_version` table + Sequential loop in Python.
- **Rationale**: Proven, simple pattern that handles incremental updates effectively.
- **Trade-offs**: Requires disciplined version incrementing in code.

### Decision: Physical File Backup
- **Context**: Safety during migration.
- **Selected Approach**: Copy `game_launcher.db` to `game_launcher.db.bak` before any write.
- **Rationale**: Provides a 100% reliable restore point regardless of SQLite's transaction state.

## Risks & Mitigations
- **Existing "V0" databases**  EMitigation: Logic to detect existing tables without `schema_version` and bootstrap them to the correct version.
- **Migration Failure**  EMitigation: Immediate rollback of transaction + logging + user notification.

## References
- [SQLite Schema Migrations](https://www.sqlite.org/lang_altertable.html)
