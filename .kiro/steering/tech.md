# Technology Stack: LitheLauncher

## Architecture
- **Application Type**: Primarily a standalone desktop application.
- **Modularity**: Designed with a modular approach, separating concerns such as game management (`game_repository.py`, `game_service.py`), application launching (`launcher_service.py`), data storage (`database.py`), and UI components (`main_window.py`, `game_detail_dialog.py`).
- **Data Management**: Uses a local database for storing game information. Integration with remote storage (`remote_storage_service.py`) suggests potential for cloud-based save synchronization or game list management.

## Frontend
- **Framework**: Python-based GUI application using **PySide6** (Qt for Python).
## Performance Constraints
- **Startup Time**: Must be under **0.7s**. Splash screens are prohibited if this goal is met.
- **Data Scaling**: Must remain responsive with 1000+ game entries.
- **Monitoring**: `main.py` must include high-resolution timestamp logging for each initialization phase (QApp, Database, Services, MainWindow).

## Optimization Patterns
- **Asynchronous Initialization**: Heavy tasks (DB migration, image loading) should not block the main UI thread.
- **Async Sequential Grid Display**: Large game lists are loaded and displayed sequentially using chunks to minimize perceived startup time.
- **Async Image Decoding & Scaling**: Offloads heavy QImage creation and transformation to a background thread pool (`ImagePool`).
- **Request Integrity Pattern**: Uses unique `request_id`s to prevent stale data from overwriting current UI state during asynchronous operations.
- **QSS-driven UI States**: Utilizes custom Qt properties (e.g., `image_loading`) to drive visual state transitions (Loading/No Image) directly in CSS.
- **UI Virtualization**: `GameListController` manages a `WidgetPool` to reuse game card widgets, keeping the UI responsive even with 1000+ items.
- **Chunked Asynchronous Loading**: `GameListWorker` fetches data in variable-sized chunks (e.g., first 20 for immediate view, then 100s) and notifies the UI via signals.
- **Styling**: Qt Style Sheets (QSS) are used for customizing the appearance.
- **Service Communication**: Business logic services notify the UI using a **callback pattern**.
- **Conflict Resolution UI**: Background synchronization processes can pause and request user intervention via modal dialogs.
- **Language**: Full i18n support for English and Japanese via `LanguageService` and `QTranslator`.

## OS Integration
- **Framework**: `ctypes` for Windows `AppUserModelID` setting (LitheLauncher.GameLauncher.1.0).

## Data / Storage
- **Database**: SQLite (via `src/database.py`).
- **Migration**: Custom code-first migration engine with `BackupService`.

## Image Processing
- **Pattern**: Dedicated resource pool (`ImagePool`) for background processing.
- **Library**: Pillow (PIL) for metadata, PySide6 (`QImage`) for UI rendering.

## Development Environment
- **Language Version**: Python 3.x.
- **Testing**: `pytest`, `pytest-qt`, `Hypothesis`.

## Common Commands
- **Run Application**: `python main.py`
- **Run Tests**: `pytest`

## Technology Stack

| Layer | Choice / Version | Role in Feature | Notes |
|-------|------------------|-----------------|-----------------|
| ドキュメンテーション | Markdown | README.mdの記述形式 | GitHubのレンダリング標準 |
| Backend / Services | Python 3.x | `GameService`, `LauncherService` | Core logic. |
| Data / Storage | SQLite | Migration engine | Secure data management. |