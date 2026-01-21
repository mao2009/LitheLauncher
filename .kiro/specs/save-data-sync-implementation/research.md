# Research Log

## Summary
繧ｻ繝ｼ繝悶ョ繝ｼ繧ｿ蜷梧悄讖溯・縺ｮ險ｭ險医↓蜷代￠縺溯ｻｽ蠎ｦ縺ｪ隱ｿ譟ｻ繧貞ｮ滓命縺励∪縺励◆縲よ里蟄倥・LitheLauncher Game Launcher縺ｮ繧｢繝ｼ繧ｭ繝・け繝√Ε・・ameDetailDialog, GameService, LauncherService・峨∈縺ｮ邨ｱ蜷域婿豕輔→縲∵眠縺溘↑RemoteStorageService縺ｮ蟆主・縺ｫ繧医ｋ蠖ｱ髻ｿ縺ｫ辟ｦ轤ｹ繧貞ｽ薙※縺ｾ縺励◆縲ゆｸｻ縺ｫUI縲√ョ繝ｼ繧ｿ繝｢繝・Ν縲√し繝ｼ繝薙せ繝ｬ繧､繝､繝ｼ縺ｮ諡｡蠑ｵ縺悟ｿ・ｦ√→縺ｪ繧玖ｦ玖ｾｼ縺ｿ縺ｧ縺吶ゅヵ繧｡繧､繝ｫ繧ｷ繧ｹ繝・Β謫堺ｽ懊・Python讓呎ｺ匁ｩ溯・縺ｧ蟇ｾ蠢懷庄閭ｽ縺ｧ縺吶′縲√Μ繝｢繝ｼ繝医せ繝医Ξ繝ｼ繧ｸ縺ｨ縺ｮ騾｣謳ｺ縺ｫ縺ｯ蟆・擂逧・↓蜈ｷ菴鍋噪縺ｪ繝励Ο繝医さ繝ｫ縺ｫ蠢懊§縺溘Λ繧､繝悶Λ繝ｪ縺ｮ蟆主・縺梧ｱゅａ繧峨ｌ縺ｾ縺吶ょ酔譛滉ｸｭ縺ｮ繝・・繧ｿ謨ｴ蜷域ｧ縲√ロ繝・ヨ繝ｯ繝ｼ繧ｯ髫懷ｮｳ縲√ヵ繧｡繧､繝ｫ遶ｶ蜷医√ヱ繝輔か繝ｼ繝槭Φ繧ｹ縲√そ繧ｭ繝･繝ｪ繝・ぅ縺御ｸｻ隕√↑繝ｪ繧ｹ繧ｯ縺ｨ縺励※隴伜挨縺輔ｌ縺ｾ縺励◆縲・
## Research Topics

### 1. Existing Architecture Integration Points
- **Scope**: Identify where save data sync functionality will integrate into the LitheLauncher application.
- **Findings**:
    - **UI**: `src/game_detail_dialog.py` will require new UI elements for enabling/disabling sync, and input fields for local save folder and remote sync path.
    - **Data Model**: The `Game` entity (managed by `src/game_repository.py` and `src/game_service.py`) needs to store `sync_enabled` (boolean), `save_folder` (string/path), and `remote_sync_path` (string).
    - **Launcher Logic**: `src/launcher_service.py` is the central point for game launch and exit. It will be responsible for calling the sync logic before launch and after exit.
    - **New Service**: A dedicated `RemoteStorageService` (`src/remote_storage_service.py`) will abstract the actual remote storage interactions.
- **Implications**: Modifications to existing UI, service, and repository layers, plus the introduction of a new service.

### 2. Remote Storage Technology & Abstraction
- **Scope**: Determine how to abstract various remote storage solutions.
- **Findings**:
    - Current `src/remote_storage_service.py` is a mock. Actual implementation will depend on chosen remote storage (e.g., S3, FTP, WebDAV, custom API).
    - Python offers libraries for various protocols (e.g., `boto3` for AWS S3, `ftplib` for FTP, `requests` for HTTP-based APIs).
    - For initial design, the `RemoteStorageService` should provide a clear interface (`download_save_data`, `upload_save_data`) regardless of the backend technology.
- **Implications**: The design should allow for interchangeable remote storage backends without affecting core game logic.

### 3. Save Data Sync Logic & Strategy
- **Scope**: Define basic synchronization strategy.
- **Findings**:
    - **Bidirectional Sync**:
        - Before Launch: Download from remote to local (local path becomes primary for game session).
        - After Exit: Upload from local to remote (local changes propagate).
    - **File Identification**: Sync should handle entire directories/folders, not just single files.
    - **Conflict Resolution**: For simplicity in the initial version, a "last-write-wins" strategy will be assumed. More sophisticated conflict resolution (e.g., versioning, user prompt) can be added later.
    - **Error Handling**: Critical during network operations. Needs robust logging and user notification.
- **Implications**: `LauncherService` will coordinate these steps. `RemoteStorageService` will handle file transfers.

### 4. Identified Risks & Mitigation
- **Risk**: Data corruption due to crashes during sync.
    - **Mitigation**: Implement file integrity checks (e.g., checksums) if possible, or perform sync in temporary locations before committing to final local/remote paths. For initial version, ensure robust error handling and logging.
- **Risk**: Network latency/unavailability impacting user experience.
    - **Mitigation**: Implement timeouts and basic retry mechanisms. Inform user about ongoing syncs or failures.
- **Risk**: File conflicts (local vs. remote changes).
    - **Mitigation**: Initial strategy: last-write-wins. Log which version was kept. Future: offer user choice.
- **Risk**: Performance degradation for large save files/folders.
    - **Mitigation**: Consider async operations (e.g., separate thread for sync) for future enhancements. For initial version, ensure sync happens in a blocking manner to maintain data integrity during critical game launch/exit phases.
- **Risk**: Security of remote storage credentials.
    - **Mitigation**: Do not hardcode credentials. Use secure configuration management (e.g., environment variables, OS-specific credential stores). (Beyond current scope but noted for future implementation).

## Architecture Pattern Evaluation
- **Existing Pattern**: Service Layer, Repository Pattern.
- **Alignment**: The new functionality aligns well by extending existing services (`GameService`, `LauncherService`) and introducing a new service (`RemoteStorageService`) to maintain separation of concerns.
- **No new pattern**: No new architectural patterns are introduced.

## Design Decisions
- `RemoteStorageService` will be an interface (or abstract base class in Python terms) to allow for different remote storage implementations (e.g., local folder, FTP, S3).
- Sync will be blocking during game launch/exit to prioritize data integrity and simplify initial implementation.
- Basic "last-write-wins" for conflict resolution, with logging.
- UI elements for sync settings will be integrated into `GameDetailDialog`.
