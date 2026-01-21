# Research & Design Decisions: Smart Save Data Sync

## Summary
- **Feature**: smart-save-data-sync
- **Discovery Scope**: Extension
- **Key Findings**:
  - `os.walk` と `os.path.getmtime` を使用した再帰皁E��チE��レクトリ走査により、セーブフォルダ冁E�E最終更新日時を確実に取得できる、E  - 既存�E `RemoteStorageService` は単純なコピ�Eのみを行ってぁE��ため、比輁E��のユーチE��リチE��メソチE��を追加する忁E��がある、E  - 不整合時の手動選択�E `LauncherService` 冁E�� `QMessageBox` を利用して実裁E��能だが、テスト容易性のために UI への問い合わせを抽象化する余地がある、E
## Research Log

### チE��レクトリ冁E�E最新更新日時�E取征E- **Context**: セーブデータはチE��レクトリ形式であるため、単一のタイムスタンプではなくディレクトリ冁E�E全ファイルを老E�Eする忁E��がある、E- **Sources Consulted**: Python公式ドキュメンチE(`os`, `pathlib`), Stack Overflow
- **Findings**: `os.scandir` また�E `os.walk` を使用して全ファイルを走査し、各ファイルの `mtime` の最大値をとる�Eが最も正確、E- **Implications**: `RemoteStorageService` に `get_latest_mtime(path)` を実裁E��る、E
### 不整合（競合）時のユーザー対話
- **Context**: 要件 2.2�E�タイムスタンプ不整合時の手動選択）�E実現方法、E- **Findings**: `LauncherService` はすでに `PySide6.QtWidgets.QMessageBox` をインポ�Eトしており、実行時にダイアログを表示できる、E- **Implications**: 競合を検知した際、`LauncherService` がダイアログを表示し、ユーザーの選択（ローカル優允E/ リモート優允E/ 中断�E�に従って後続�E処琁E��決定する、E
## Design Decisions

### Decision: 同期判定ロジチE��の配置場所
- **Context**: タイムスタンプ比輁E��アクション選択をどこで行うか、E- **Alternatives Considered**:
  1. `RemoteStorageService` 冁E��完結させる、E  2. `LauncherService` が比輁E��果を取得し、制御フローを決定する、E- **Selected Approach**: オプション 2
- **Rationale**: `RemoteStorageService` はファイル操作�E抽象化に専念させ、`LauncherService` がビジネスロジチE���E�ユーザーへの問い合わせやバックアチE�Eの管琁E��を拁E��することで、既存�E役割刁E��を維持する、E- **Trade-offs**: `LauncherService` の `sync_save_data` メソチE��の責任篁E��が庁E��る、E
## Risks & Mitigations
- **不正確なタイムスタンチE*  E未来の日付などの不整合を検知した場合、強制皁E��手動選択ダイアログを表示する、E- **同期中の通信刁E��**  E既存�E例外�E琁E��ESaveDataSyncError`�E�とバックアチE�E復允E��ジチE��を活用し、データの安�E性を確保する、E
