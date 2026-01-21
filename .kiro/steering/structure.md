# Project Structure: LitheLauncher

## Root Directory Organization
- `src/`: Contains the primary source code, organized by functional responsibility (Services, UI, Data Access).
- `tests/`: Holds unit and integration tests, mirroring the `src/` structure with `test_` prefixes.
- `res/`: Stores application resources such as images, icons, and QSS stylesheets.
- `data/`: Application data, user-specific configurations, and temporary storage.
- `local/` / `remote/`: Mock storage directories for synchronization testing.
- `main.py`: The entry point of the LitheLauncher application. Includes critical performance timing logs.

## Subdirectory Patterns

### `src/` (Core Logic)
- **Services (`*_service.py`)**: Encapsulate business logic. Performance-critical services should support asynchronous operations and data streaming/chunking.
- **Repositories (`*_repository.py`)**: Abstract data access. Must handle large result sets efficiently using `LIMIT` and `OFFSET` for chunked retrieval.
- **Controllers (`*_controller.py`)**: Manage the state and virtualization logic for complex UI components (e.g., `GameListController` for grid virtualization).
- **Workers (`*_worker.py`)**: `QRunnable` or `QThread` based components that handle long-running tasks like data fetching (`GameListWorker`) in the background.
- **Resource Managers (`*_pool.py`)**: Dedicated thread pools or caches for specific heavy resources (e.g., `ImagePool`, `WidgetPool`).
- **UI Components (`*_dialog.py`, `*_widget.py`, `*_window.py`)**: PySide6-based interface. Large list displays require integration with Controllers for virtualization and Workers for non-blocking loading.
- **Infrastructure & Utils**: Database schema management (`database.py`), validation logic (`executable_validator.py`), and cross-cutting concerns like logging and exceptions.

### `tests/` (Verification)
- **Unit Tests**: Test individual modules in isolation, often using mocks for dependencies.
- **Integration Tests**: Verify the end-to-end flow between multiple services and UI components (e.g., `test_integration_save_data_sync.py`).
- **Property-based Tests**: Use `hypothesis` to test edge cases and invariants.

## Code Organization Patterns
- **Service-Repository Pattern**: Decouples business logic from data storage, facilitating testability and maintainability.
- **Callback Pattern**: Services notify the UI of progress or status changes without direct coupling to UI instances.
- **Request Integrity Pattern**: Use of unique IDs (e.g., `request_id`) in asynchronous callbacks to ensure that UI updates match the latest requested state, especially during widget reuse.
- **Test-Driven Development (TDD)**: The project maintains high test coverage, with new features requiring corresponding unit and integration tests.

## Key Architectural Principles
- **Separation of Concerns**: Strict division between UI, logic, and data layers.
- **Modularity**: Small, independent modules with clear interfaces.
- **Code-First Database Migration**: Declarative schema definitions with automated version tracking and backups.