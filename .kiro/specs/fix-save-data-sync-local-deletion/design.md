# Technical Design Document: Fix Save Data Sync Local Deletion

---
**Purpose**: リモートにセーブデータがなぁE��合にローカルのセーブデータが意図せず削除される不�E合を修正し、セーブデータ同期処琁E�E堁E��性を向上させる、E
**Approach**:
- 既存�Eセーブデータ同期ロジチE��を特定し、問題�Eある挙動を修正する、E- チE�Eタの整合性を保つため、ダウンロード�E琁E��にローカルセーブデータのバックアチE�Eメカニズムを導�Eする、E- 同期失敗時のエラーハンドリングと、バチE��アチE�Eからの復旧ロジチE��を実裁E��る、E
## Overview
こ�E機�Eは、Pyzree Game Launcherのセーブデータ同期機�Eにおける既存�E不�E合を修正します。現在、リモートストレージにセーブデータが存在しなぁE��合にローカルのセーブデータが誤って削除される問題があります。本設計では、この問題を解決し、セーブデータ同期処琁E�E堁E��性と信頼性を向上させ、ユーザーのゲームセーブデータを保護することを目皁E��します、E
### Goals
- リモートストレージにセーブデータが存在しなぁE��合でも、ローカルのセーブデータが削除されなぁE��ぁE��する、E- セーブデータダウンロード�E琁E��に、既存�EローカルセーブデータのバックアチE�Eを�E動的に作�Eする、E- セーブデータダウンロード失敗時に、バチE��アチE�Eされたローカルセーブデータを復允E��る、E- セーブデータ同期処琁E��のエラーにつぁE��、ユーザーに適刁E��通知する、E- 全てのセーブデータ同期処琁E�Eログを詳細に出力する、E
### Non-Goals
- 新しいリモートストレージプロバイダのサポ�Eト追加、E- 既存�Eセーブデータ同期設定UIの変更、E- セーブデータ同期以外�E機�Eへの変更、E
## Architecture

### Existing Architecture Analysis
セーブデータ同期は、`LauncherService`が`RemoteStorageService`を呼び出すことで実行されます、E- `LauncherService.sync_save_data`: セーブデータ同期処琁E�Eトリガーと方向（ダウンローチEアチE�Eロード）を制御します、E- `RemoteStorageService.download_save_data`: リモートからローカルへのセーブデータダウンロードを処琁E��ます。ここでローカルパスを削除する`shutil.rmtree`が利用されており、リモートにチE�EタがなぁE��合にローカルチE�Eタが失われる原因となってぁE��す、E- `RemoteStorageService.upload_save_data`: ローカルからリモートへのセーブデータアチE�Eロードを処琁E��ます、E
### Architecture Pattern & Boundary Map
こ�E変更は、既存�EアーキチE��チャパターン�E�サービス層、リポジトリパターン�E�に沿って行われます。`LauncherService`と`RemoteStorageService`間�E墁E��は維持され、`RemoteStorageService`はより堁E��なチE�Eタ転送ロジチE��を提供し、`LauncherService`はそ�Eオーケストレーションを強化します、E
```mermaid
graph TD
    A[UI (GameDetailDialog)] --> B(LauncherService)
    B --> C(GameService)
    B -- sync_save_data(game_id, direction) --> D(RemoteStorageService)
    D -- (reads remote/local paths) --> E[File System]
    D -- (reads remote/local paths) --> F[Remote Storage (e.g., Cloud / Network Drive)]
```

**Architecture Integration**:
- Selected pattern: 既存�Eサービス持E��アーキチE��チャパターンを拡張、E- Domain/feature boundaries: `LauncherService`はオーケストレーションの責務を、`RemoteStorageService`は実際のチE�Eタ転送�E責務を維持します、E- Existing patterns preserved: サービス層による関忁E���E刁E��、E- New components rationale: なし。既存コンポ�Eネント�E機�E強化、E- Steering compliance: モジュール性と関忁E���E刁E��の原則を維持、E
### Technology Stack

| Layer | Choice / Version | Role in Feature | Notes |
|-------|------------------|-----------------|-------|
| Backend / Services | Python 3.x | 既存�E同期ロジチE��の修正と拡張。`shutil`, `os`, `pathlib`の利用、E| 新規ライブラリの追加なし、E|
| Data / Storage | File System | ローカルセーブデータのバックアチE�Eと復允E��E| |
| Messaging / Events | なぁE| | |
| Infrastructure / Runtime | なぁE| | |

## System Flows
**セーブデータダウンロード�E琁E��ローの変更点**

```mermaid
sequenceDiagram
    participant LS as LauncherService
    participant RSS as RemoteStorageService
    participant FS as File System
    
    LS->>FS: 1. ローカルセーブデータのバックアチE�E作�E (一時ディレクトリへ)
    activate LS
    LS->>RSS: 2. download_save_data(game_id, remote_path, local_path)
    activate RSS
    RSS->>FS: 2.1. リモートパスの存在チェチE��
    alt リモートパスが存在しなぁE        RSS-->>LS: 2.2. リモートデータなし、ローカル削除スキチE�Eを通知
    else リモートパスが存在する
        RSS->>FS: 2.2. ローカルパスの冁E��を削除 (既存データがあれ�E)
        RSS->>FS: 2.3. リモートからローカルへチE�Eタをコピ�E
        RSS-->>LS: 2.4. ダウンロード完亁E    end
    deactivate RSS
    alt ダウンロード失敁E        LS->>FS: 3. バックアチE�Eからローカルセーブデータを復允E        LS->>UI: 4. ユーザーへエラー通知
    else ダウンロード�E劁E        LS->>FS: 3. バックアチE�Eを削除
    end
    deactivate LS
```

## Requirements Traceability

| Requirement | Summary | Components | Interfaces | Flows |
|-------------|---------|------------|------------|-------|
| 1.1 | リモートデータ不在時�EローカルチE�Eタ保護 | RemoteStorageService | download_save_data | セーブデータダウンロード�E琁E��ロー |
| 1.2 | ダウンロード時のローカルセーブデータのバックアチE�E | LauncherService, File System | sync_save_data | セーブデータダウンロード�E琁E��ロー |
| 1.3 | ダウンロード失敗時のローカルセーブデータの復允E| LauncherService, File System | sync_save_data | セーブデータダウンロード�E琁E��ロー |
| 2.1 | ダウンロード失敗時のユーザー通知 | LauncherService | (UIへの通知メカニズム) | セーブデータダウンロード�E琁E��ロー |
| 2.2 | アチE�Eロード失敗時のユーザー通知 | LauncherService | (UIへの通知メカニズム) | |
| 2.3 | 同期処琁E�E詳細ログ出劁E| LauncherService, RemoteStorageService | 全ての公開メソチE�� | |
| 3.1 | ダウンロード�E琁E��のローカルチE�Eタ保護 | LauncherService, RemoteStorageService, File System | sync_save_data, download_save_data | セーブデータダウンロード�E琁E��ロー |
| 3.2 | アチE�Eロード�E琁E��のリモートデータ保護 | RemoteStorageService, File System | upload_save_data | |
| 3.3 | 同期関連例外�E適刁E�E琁E| LauncherService, RemoteStorageService | 全ての公開メソチE�� | |

## Components and Interfaces

### Backend / Services

#### LauncherService

| Field | Detail |
|-------|--------|
| Intent | ゲームの起動、前/後�E琁E��マンド�E実行、およ�Eセーブデータ同期のオーケストレーション |
| Requirements | 1.2, 1.3, 2.1, 2.2, 2.3, 3.1, 3.3 |
| Owner / Reviewers | 笹倁E大輁E|

**Responsibilities & Constraints**
- ゲームIDに基づぁE��`GameService`からゲーム詳細を取得、E- `RemoteStorageService`と連携し、セーブデータのダウンローチEアチE�Eロードを持E��、E- セーブデータダウンロード前にローカルセーブデータのバックアチE�Eと、ダウンロード失敗時の復允E��管琁E��E- 発生した例外を捕捉し、ユーザーに適刁E��エラーメチE��ージを表示、E- 全ての同期処琁E�Eログを詳細に出力、E
**Dependencies**
- Outbound: `GameService`  Eゲーム詳細取征E(P0)
- Outbound: `RemoteStorageService`  Eセーブデータ転送E(P0)

**Contracts**: Service [x]

##### Service Interface
```python
class LauncherService:
    # ...
    def sync_save_data(self, game_id: int, direction: str) -> bool:
        """
        持E��されたゲームIDのセーブデータを同期する、E        ダウンロード時には既存ローカルチE�EタのバックアチE�Eと復允E��ジチE��を含む、E
        Args:
            game_id: 同期対象のゲームID、E            direction: "download" また�E "upload"、E
        Returns:
            bool: 同期処琁E��成功した場吁ETrue、失敗した場吁EFalse、E        
        Raises:
            GameNotFoundError: 持E��されたゲームが見つからなぁE��合、E            ExecutableValidationError: 実行可能パスが無効な場合、E            CommandExecutionError: 前�E琁E後�E琁E��マンド�E実行に失敗した場合、E            SaveDataSyncError: セーブデータ同期処琁E��失敗した場合、E        """
        pass
    # ...
```
- Preconditions:
    - `game_id`は有効なゲームIDであること、E    - `direction`は"download"また�E"upload"であること、E- Postconditions:
    - `direction`ぁEdownload"の場合、リモート�Eセーブデータがローカルに存在するか、また�E既存�EローカルチE�Eタが保持されてぁE��こと、E    - `direction`ぁEupload"の場合、ローカルのセーブデータがリモートにアチE�EロードされてぁE��こと、E    - 同期処琁E�E結果がログに記録されてぁE��こと、E- Invariants:
    - セーブデータ同期処琁E�E成功/失敗に関わらず、ユーザーのローカルセーブデータは常に保護される（ダウンロード失敗時はバックアチE�Eから復允E��れる�E�、E
#### RemoteStorageService

| Field | Detail |
|-------|--------|
| Intent | リモートストレージとローカルファイルシスチE��間でセーブデータを安�Eに転送すめE|
| Requirements | 1.1, 2.3, 3.1, 3.2, 3.3 |
| Owner / Reviewers | 笹倁E大輁E|

**Responsibilities & Constraints**
- リモートストレージからローカルへのセーブデータダウンロード、E- ローカルからリモートストレージへのセーブデータアチE�Eロード、E- リモートパスが存在しなぁE��合、ローカルチE�Eタを削除しなぁE��E- 発生した例外を捕捉し、ロギングを行う、E
**Dependencies**
- External: File System (`shutil`, `os`, `pathlib`)  Eファイル/チE��レクトリ操佁E(P0)

**Contracts**: Service [x]

##### Service Interface
```python
class RemoteStorageService:
    # ...
    def download_save_data(self, game_id: int, remote_path: str, local_path: Path) -> None:
        """
        リモートストレージからローカルパスへセーブデータをダウンロードする、E        リモートパスが存在しなぁE��合、ローカルパスは削除されなぁE��E
        Args:
            game_id: 同期対象のゲームID、E            remote_path: リモートストレージのパス、E            local_path: ローカルの保存�Eパス (PathオブジェクチE、E        
        Raises:
            SaveDataSyncError: ダウンロード�E琁E��失敗した場合、E        """
        pass

    def upload_save_data(self, game_id: int, local_path: Path, remote_path: str) -> None:
        """
        ローカルパスからリモートストレージへセーブデータをアチE�Eロードする、E
        Args:
            game_id: 同期対象のゲームID、E            local_path: ローカルの転送�Eパス (PathオブジェクチE、E            remote_path: リモートストレージのパス、E
        Raises:
            SaveDataSyncError: アチE�Eロード�E琁E��失敗した場合、E        """
        pass
    # ...
```
- Preconditions:
    - `local_path`は有効なPathオブジェクトであること、E    - `remote_path`は有効な斁E���Eパスであること、E- Postconditions:
    - `download_save_data`成功時、`local_path`にリモート�Eセーブデータが存在するか、リモートデータが存在しなぁE��合�E`local_path`が削除されてぁE��ぁE��と、E    - `upload_save_data`成功時、`remote_path`にローカルのセーブデータが存在すること、E- Invariants:
    - 転送�E琁E�E結果がログに記録されてぁE��こと、E    - `download_save_data`時にリモートにチE�EタがなぁE��合でも、`local_path`は削除されなぁE��E
## Error Handling

### Error Strategy
セーブデータ同期中に発生するエラーは`SaveDataSyncError`として捕捉され、`LauncherService`の`sync_save_data`メソチE��で雁E��皁E��処琁E��れます。このエラーはユーザーインターフェースに伝播され、詳細なエラーメチE��ージとしてユーザーに表示されます。また、�Eての同期関連イベント�Eログに記録され、トラブルシューチE��ングに役立てられます、E
### Error Categories and Responses
- **SaveDataSyncError**:
    - **Context**: `RemoteStorageService`におけるファイル操作（コピ�E、削除�E��E失敗、また�Eリモートパスの存在チェチE��の失敗、E    - **Response**: `LauncherService`がエラーを捕捉し、ユーザーにエラーメチE��ージボックスを表示。メチE��ージにはエラーの種類と、可能な場合�E具体的な原因を含める。ログに`ERROR`レベルで詳細を記録。ダウンロード失敗時は、バチE��アチE�Eされたローカルセーブデータを復允E��る、E
## Testing Strategy

### Unit Tests
- `RemoteStorageService`:
    - `download_save_data`: リモートパスが存在する場合�E正常ダウンロード。リモートパスが存在しなぁE��合�Eローカルパス保護。ファイルコピ�E失敗時のエラーハンドリング、E    - `upload_save_data`: 正常アチE�Eロード。ファイルコピ�E失敗時のエラーハンドリング、E- `LauncherService`:
    - `sync_save_data`:
        - ダウンロード�E功時のバックアチE�E作�Eと削除、E        - ダウンロード失敗時のバックアチE�Eからの復允E��E        - リモートデータ不在時�E`RemoteStorageService`からの通知の適刁E�E琁E��E        - エラー発生時のユーザー通知とロギング、E
### Integration Tests
- `GameLauncher`の起動からゲームの選択、セーブデータ同期�E�ダウンローチEアチE�Eロード）を含むエンドツーエンド�EシナリオチE��ト、E- リモートストレージ�E�モチE��また�EチE��ト用チE��レクトリ�E�が空の場合�Eダウンロード挙動�E検証、E- 同期処琁E��のネットワーク障害�E�シミュレート）や権限エラー発生時の挙動の検証、E
