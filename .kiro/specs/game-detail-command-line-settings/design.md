# Design Document Template

---
**Purpose**: Provide sufficient detail to ensure implementation consistency across different implementers, preventing interpretation drift.

**Approach**:
- Include essential sections that directly inform implementation decisions
- Omit optional sections unless critical to preventing implementation errors
- Match detail level to feature complexity
- Use diagrams and tables over lengthy prose

**Warning**: Approaching 1000 lines indicates excessive feature complexity that may require design simplification.
---

## Overview
**Purpose**: こ�E機�Eは、Pyzree Game Launcherのユーザーがゲームの詳細画面でコマンドライン引数を設定し、ゲームの起動をカスタマイズできるようにすることで、より高度な制御を提供します、E**Users**: PCゲーマ�Eは、ゲームの起動時に特定�EオプションめE��墁E��数が忁E��な場合にこ�E機�Eを利用します、E**Impact**: `GameDetailDialog` のUI、ゲームチE�Eタ (`Game` モチE��)、およ�E `LauncherService` のゲーム起動ロジチE��が変更されます、E
### Goals
- ゲームの詳細画面でコマンドライン設定�E入力フィールドを提供する、E- 入力されたコマンドライン設定をゲームのメタチE�Eタとして永続化する、E- `%command%` プレースホルダーをゲームの実行ファイルパスで適刁E��置換する、E- コマンドライン設定を適用してゲームを起動する、E- 不正なコマンドライン設定につぁE��ユーザーに警告する、E
### Non-Goals
- 高度なコマンドライン引数の自動生成また�E補完機�E、E- コマンドライン引数に含まれる環墁E��数の自動解決。ユーザーは忁E��に応じて完�Eな形式で入力する忁E��があります、E- コマンドライン引数の構文の完�Eな検証。基本皁E��構文エラーの警告に限定します、E
## Architecture

### Existing Architecture Analysis
*   **現在のアーキチE��チャパターンと制紁E*: Service Layer, Repository Pattern。UI (PySide6) -> `GameService` -> `GameRepository` -> SQLite DB、E*   **既存�Eドメイン墁E��**: `GameService` はビジネスロジチE��、`LauncherService` はゲーム起動ロジチE��、`game_detail_dialog.py` はUIプレゼンチE�Eション、E*   **統合�EインチE*: `GameDetailDialog` と `GameService`、`GameService` と `GameRepository`、`LauncherService`、E*   **技術的負債**: なし、E
### Architecture Pattern & Boundary Map
```mermaid
graph TD
    UI[GameDetailDialog (PySide6)] --> GS[GameService]
    GS --> GR[GameRepository]
    UI --> LS[LauncherService]
    LS --> OS[Operating System]
    GR --> DB[(SQLite Database)]

    subgraph "LitheLauncher Application Boundary"
        UI
        GS
        GR
        LS
        DB
        OS
    end

    style UI fill:#bbf,stroke:#33c,stroke-width:2px;
    style GS fill:#bfb,stroke:#3c3,stroke-width:2px;
    style GR fill:#fbb,stroke:#c33,stroke-width:2px;
    style LS fill:#fbf,stroke:#c3c,stroke-width:2px;
    style DB fill:#eee,stroke:#999,stroke-width:2px;
    style OS fill:#eef,stroke:#99c,stroke-width:2px;
```
**Architecture Integration**:
-   **Selected pattern**: ハイブリチE��アプローチ。既存�Eコンポ�Eネント！EGameDetailDialog`, `GameService`, `LauncherService`�E�を拡張し、新しい機�Eを追加します、E-   **Domain/feature boundaries**:
    *   `GameDetailDialog` は、ユーザーからのコマンドライン設定�E入力を受け取り、`GameService` に渡します、E    *   `GameService` は、ゲームメタチE�Eタの一部としてコマンドライン設定を永続化し、`LauncherService` にゲーム起動を持E��する際にそ�E設定を渡します、E    *   `LauncherService` は、コマンドライン設定文字�Eを�E琁E���Eレースホルダー置換、引数リストへの変換など�E�し、ゲームを起動します、E-   **Existing patterns preserved**: Service Layer, Repository Pattern, モジュラーチE��イン、E-   **New components rationale**: なし。既存コンポ�Eネントを拡張します、E-   **Steering compliance**: モジュラーチE��インと責務�E刁E��原則を維持します、E
### Technology Stack

| Layer | Choice / Version | Role in Feature | Notes |
|-------|------------------|-----------------|-------|
| Frontend | PySide6 | コマンドライン設定�E入力UI (`QLineEdit`) | `GameDetailDialog` の拡張 |
| Backend / Services | Python 3.x | ゲームメタチE�Eタ (`command_line_settings`) の管琁E��コマンドライン斁E���Eの処琁E| `GameService`, `LauncherService` の拡張 |
| Data / Storage | SQLite (via `src/database.py`) | ゲームメタチE�Eタ (`command_line_settings`) の永続化 | `Game` チE�Eブルに新しいカラムを追加 |
| Utilities | `shlex` (Python標準ライブラリ) | コマンドライン斁E���Eの安�Eなパ�Eス | `LauncherService` で利用 |

## System Flows
こ�E機�Eにおける主要なシスチE��フローは、ゲーム起動時のコマンドライン処琁E��す、E
```mermaid
sequenceDiagram
    actor User
    participant UI as GameDetailDialog
    participant GS as GameService
    participant GR as GameRepository
    participant LS as LauncherService
    participant OS as Operating System

    User->>UI: ゲーム詳細画面を開ぁE    UI->>GS: get_game_details(game_id)
    GS->>GR: get_game(game_id)
    GR-->>GS: game_data (command_line_settings含む)
    GS-->>UI: game_data
    UI-->>User: コマンドライン設定を表示

    User->>UI: コマンドライン設定を入劁E変更
    UI->>GS: save_game_details(game_id, new_settings)
    GS->>GR: update_game(game_id, new_settings)
    GR-->>GS: 成功
    GS-->>UI: 成功

    User->>LS: ゲームを起勁E    activate LS
    LS->>LS: コマンドライン設定�E取征E    LS->>LS: `%command%` プレースホルダー処琁E    LS->>LS: コマンドライン斁E���Eを引数リストにパ�Eス (shlex)
    LS->>OS: ゲームを実衁E(subprocess.Popen)
    deactivate LS
    OS-->>User: ゲームが起勁E```
**フローレベルの決宁E*: `GameDetailDialog` は設定�E入力と表示を担当し、`GameService` はチE�Eタの永続化を管琁E��ます。`LauncherService` は、保存されたコマンドライン設定に基づぁE��ゲームの起動コマンドを構築し、実行する責務を負ぁE��す、E
## Requirements Traceability

| Requirement | Summary | Components | Interfaces | Flows |
|-------------|---------|------------|------------|-------|
| 1.1 | コマンドライン設定�E力UIの表示 | `GameDetailDialog` | UI | ゲーム詳細画面を開くフロー |
| 1.2 | 入力された設定�E格紁E| `GameDetailDialog`, `GameService` | UI, Service | ゲーム詳細画面を開ぁE保存するフロー |
| 1.3 | 設定�E永続化 | `GameService`, `GameRepository` | Service, Repository | ゲーム詳細画面を保存するフロー |
| 1.4 | 既存設定�E表示 | `GameDetailDialog`, `GameService` | UI, Service | ゲーム詳細画面を開くフロー |
| 2.1 | `%command%`置揁E(存在する場吁E | `LauncherService` | Service | ゲーム起動フロー |
| 2.2 | `%command%`置揁E(存在しなぁE��吁E | `LauncherService` | Service | ゲーム起動フロー |
| 2.3 | コマンドライン斁E���EをOSへ渡ぁE| `LauncherService` | Service | ゲーム起動フロー |
| 3.1 | 設定�E取征E| `LauncherService`, `GameService` | Service | ゲーム起動フロー |
| 3.2 | 処琁E��み設定でのゲーム実衁E| `LauncherService` | Service | ゲーム起動フロー |
| 4.1 | 問題�Eある設定�E警呁E| `GameDetailDialog`, `LauncherService` | UI, Service | コマンドライン設定�E入劁E保孁E起動フロー |
| 4.2 | 警告があっても保存�E起動を許可 | `GameDetailDialog`, `LauncherService` | UI, Service | コマンドライン設定�E入劁E保孁E起動フロー |

## Components and Interfaces

| Component | Domain/Layer | Intent | Req Coverage | Key Dependencies (P0/P1) | Contracts |
|---|---|---|---|---|---|
| `GameDetailDialog` | UI | ゲーム詳細の表示、編雁E��コマンドライン設定�E入劁E| 1.1, 1.2, 1.3, 1.4, 4.1, 4.2 | `GameService` (P0) | UI状慁E|
| `GameService` | Backend / Service | ゲームのビジネスロジチE��、コマンドライン設定�E永続化 | 1.2, 1.3, 1.4 | `GameRepository` (P0) | Service |
| `GameRepository` | Data / Storage | ゲームチE�Eタの永続化 | 1.3 | `database.py` (P0) | Repository |
| `LauncherService` | Backend / Service | ゲームの起動、コマンドライン斁E���Eの処琁E| 2.1, 2.2, 2.3, 3.1, 3.2, 4.1, 4.2 | `subprocess` (P0), `shlex` (P0) | Service |

### UI Layer

#### GameDetailDialog

| Field | Detail |
|-------|--------|
| Intent | ゲームの登録および詳細編雁E�Eためのユーザーインターフェースを提供し、コマンドライン設定�E入力フィールドを追加する、E|
| Requirements | 1.1, 1.2, 1.3, 1.4, 4.1, 4.2 |

**Responsibilities & Constraints**
*   コマンドライン設定用の `QLineEdit` をUIに追加、E*   既存ゲームの編雁E��には、保存されたコマンドライン設定を `QLineEdit` に表示、E*   ユーザーが�E力したコマンドライン設定を `GameService` に渡す、E*   `LauncherService` からのバリチE�Eション警告をUIに表示する、E
**Dependencies**
*   Outbound: `GameService`  EゲームチE�Eタの取得�E保孁E(P0)
*   Outbound: `LauncherService`  Eコマンドライン設定�EバリチE�Eション (P0)

**Contracts**: State [x]

##### State Management
*   **State model**:
    *   `command_line_settings: str`�E��E力されたコマンドライン設定文字�E、E*   **Persistence & consistency**: ダイアログインスタンスの生存期間中のみチE�Eタを保持し、保存時に `GameService` を通じて永続化、E
**Implementation Notes**
*   **Integration**: `GameDetailDialog` のUIに新しい `QLineEdit` と関連するラベルを追加。`_update_ui_from_game_data` および `_get_game_data_from_ui` メソチE��を更新、E*   **Validation**: `QLineEdit` の `textChanged` シグナルめE`LauncherService` のバリチE�EションメソチE��に接続し、警告をUIに表示するロジチE��を追加、E*   **Risks**: ユーザー入力�E褁E��性により、リアルタイムバリチE�Eションが困難になる可能性。警告表示のUXを老E�Eする忁E��がある、E
### Backend / Service Layer

#### GameService

| Field | Detail |
|---|---|
| Intent | ゲームのビジネスロジチE��を管琁E��、コマンドライン設定を含むゲームメタチE�Eタを永続化する、E|
| Requirements | 1.2, 1.3, 1.4 |

**Responsibilities & Constraints**
*   `GameRepository` を介して、ゲームの `command_line_settings` を保存�E取得する、E*   `GameDetailDialog` から受け取ったコマンドライン設定を `Game` モチE��にマッピングし、永続化処琁E��調整する、E
**Dependencies**
*   Outbound: `GameRepository`  EゲームチE�Eタの永続化 (P0)

**Contracts**: Service [x]

##### Service Interface
```python
from typing import Dict, Any, Optional
from pathlib import Path

class GameService:
    # ... 既存メソチE�� ...
    def register_game(self, game_data: Dict[str, Any], temp_image_path: Path | None = None) -> Dict[str, Any]:
        """新規ゲームを登録し、コマンドライン設定を保存する、E""
        pass
    
    def update_game_details(self, game_id: int, updates: Dict[str, Any], temp_image_path: Path | None = None) -> Dict[str, Any]:
        """既存ゲームを更新し、コマンドライン設定を更新する、E""
        pass
```
*   **Preconditions**: `game_data` は有効なゲーム惁E��を含む。`updates` には `command_line_settings` が含まれる場合がある、E*   **Postconditions**: ゲームが登録・更新され、`command_line_settings` が適刁E��保存される、E
**Implementation Notes**
*   **Integration**: `register_game` および `update_game_details` メソチE��で `command_line_settings` を�E琁E��るよぁE��拡張、E*   **Validation**: `GameService` レベルでのコマンドライン設定�E直接皁E��バリチE�Eションは行わず、`LauncherService` に委譲、E
#### GameRepository

| Field | Detail |
|---|---|
| Intent | ゲームチE�Eタの永続化を抽象化し、`command_line_settings` を含むゲームチE�Eタをデータベ�EスとめE��取りする、E|
| Requirements | 1.3 |

**Responsibilities & Constraints**
*   `games` チE�Eブルから `command_line_settings` カラムを読み書きする、E
**Dependencies**
*   External: SQLite チE�Eタベ�Eス (P0)

**Contracts**: Repository [x]

##### Service Interface
```python
from typing import Dict, Any, List, Optional

class GameRepository:
    # ... 既存メソチE�� ...
    def add_game(self, game_data: Dict[str, Any]) -> Dict[str, Any]:
        """新しいゲームをデータベ�Eスに追加し、コマンドライン設定を保存する、E""
        pass

    def update_game(self, game_id: int, updates: Dict[str, Any]) -> None:
        """既存�Eゲームの惁E��を更新し、コマンドライン設定を更新する、E""
        pass

    def get_game(self, game_id: int) -> Optional[Dict[str, Any]]:
        """持E��されたIDのゲーム惁E��を取得し、コマンドライン設定を含む、E""
        pass
```
*   **Preconditions**: `game_data` また�E `updates` に `command_line_settings` キーが含まれる場合、値は斁E���Eである、E*   **Postconditions**: チE�Eタベ�Eス冁E�Eゲームレコードが `command_line_settings` を含めて更新される、E
**Implementation Notes**
*   **Integration**: `_execute_query` メソチE��を通じて、SQLクエリに `command_line_settings` カラムの処琁E��追加、E*   **Risks**: チE�Eタベ�Eススキーマ変更時�E互換性、E
#### LauncherService

| Field | Detail |
|---|---|
| Intent | ゲームの実行ファイルを起動し、ユーザー定義のコマンドライン設定を適用する。コマンドライン設定�EバリチE�Eションも行う、E|
| Requirements | 2.1, 2.2, 2.3, 3.1, 3.2, 4.1, 4.2 |

**Responsibilities & Constraints**
*   ゲームの実行ファイルパスとコマンドライン設定文字�Eを受け取る、E*   コマンドライン設定文字�Eをパースし、`%command%` プレースホルダーをゲームの実行ファイルパスで置換する、E*   結果として得られた引数リストを使用して `subprocess.Popen` を呼び出す、E*   コマンドライン設定�E基本皁E��バリチE�Eションを行い、潜在皁E��問題（不整合な引用符など�E�を検�Eする、E
**Dependencies**
*   External: `subprocess` (P0)  Eプロセス起勁E*   External: `shlex` (P0)  Eコマンドライン斁E���Eのパ�Eス

**Contracts**: Service [x]

##### Service Interface
```python
from pathlib import Path
from typing import List, Tuple

class LauncherService:
    # ... 既存メソチE�� ...
    def launch_game(self, game_executable_path: Path, command_line_settings: str = "") -> None:
        """持E��された実行ファイルとコマンドライン設定でゲームを起動する、E""
        pass

    def validate_command_line_settings(self, settings_string: str) -> Tuple[bool, Optional[str]]:
        """コマンドライン設定文字�Eの基本皁E��バリチE�Eションを行い、問題があれば警告メチE��ージを返す、E""
        pass
```
*   **Preconditions**: `game_executable_path` は有効な実行ファイルへのパスである。`command_line_settings` は斁E���Eである、E*   **Postconditions**: ゲームが起動される、また�EバリチE�Eション結果が返される、E*   **Invariants**: 実行ファイルパスは常に最初�E引数として含まれる、E
**Implementation Notes**
*   **Integration**: `launch_game` メソチE��を拡張し、`command_line_settings` を受け取るよぁE��する、E*   **Validation**: `validate_command_line_settings` メソチE��を実裁E��、`shlex.split` の例外捕捉などにより基本皁E��構文チェチE��を行う、E*   **Risks**: `subprocess.Popen` のシェルモーチE(`shell=True`) の使用は避ける。セキュリチE��リスクとプラチE��フォーム間�E差異のため。`shlex.split` を使用して引数をリストとして渡し、`shell=False` で実行する、E
## Data Models

### Logical Data Model

**Structure Definition**:
-   `Game` エンチE��チE��に新しい属性 `command_line_settings` を追加、E    *   `command_line_settings`: TEXT, NULLABLE (チE��ォルト�E空斁E���E)

**Consistency & Integrity**:
-   `command_line_settings` の値は、データベ�Eスによって特別な制紁E�E課されず、文字�Eとして扱われる、E
## Error Handling

### Error Strategy
*   `LauncherService.validate_command_line_settings` で検�Eされた構文エラーは、警告として `GameDetailDialog` に表示される、E*   ゲーム起動時の `subprocess.Popen` で発生したエラーは捕捉され、アプリケーションのロガーを通じて記録される。ユーザーには起動失敗�E通知が表示される、E
### Error Categories and Responses
*   **ユーザーエラー (4xx 相彁E**: 不正なコマンドライン構文、E    *   **対忁E*: `GameDetailDialog` に警告メチE��ージを表示。保存�E可能だが、ゲーム起動時に問題が発生する可能性があることを示唁E��E*   **シスチE��エラー (5xx 相彁E**: ゲーム起動失敁E(侁E 実行ファイルが見つからなぁE��権限不足)、E    *   **対忁E*: ログに詳細を記録し、ユーザーに「ゲームの起動に失敗しました」とぁE��メチE��ージを表示、E
## Testing Strategy

### Unit Tests
-   `GameDetailDialog`: コマンドライン設定�E力フィールド�E表示、データバインチE��ング、バリチE�Eション警告�E表示、E-   `GameService`: `command_line_settings` の保存と取得、E-   `GameRepository`: `command_line_settings` カラムのチE�Eタベ�Eス操作、E-   `LauncherService`:
    *   `launch_game`: `%command%` プレースホルダーの正しい置換、`%command%` がなぁE��合�E先頭への実行ファイル挿入、引数のパ�Eスと `subprocess.Popen` への渡し方、E    *   `validate_command_line_settings`: 有効/無効なコマンドライン斁E���Eに対する正しいバリチE�Eション結果、E
### Integration Tests
-   `GameDetailDialog` から `GameService` を経由したコマンドライン設定�E保存と読み込み、E-   `GameDetailDialog` から `LauncherService` を経由したコマンドライン設定付きゲームの起動、E-   不正なコマンドライン設定を入力した場合�E警告表示と、その状態でのゲーム起動試行�
