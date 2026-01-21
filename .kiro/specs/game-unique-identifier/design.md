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
**Purpose**: こ�E機�Eは、Pyzree Game Launcherのゲームに、データベ�Eスの冁E��IDとは別にGUID�E�Elobally Unique Identifier�E�などのユニ�Eクな識別子を付与し、管琁E��ることを目皁E��します。これにより、ゲームの識別と操作�E柔軟性を高めます、E**Users**: LitheLauncher Game Launcherのユーザーは、ゲームの識別子がDBの冁E��IDに依存しなぁE��め、より堁E��なゲーム管琁E��享受できます、E**Impact**: ゲームチE�Eタに新しいユニ�Eク識別孁E(`unique_identifier`) フィールドが追加され、DBスキーマが更新されます。`GameService`と`GameRepository`にユニ�Eク識別子に基づく操作メソチE��が追加されます、E
### Goals
- 新規ゲーム登録時に、シスチE��が�E動的にGUIDを生成し、ゲームに割り当てること (Req 1.1)、E- 既存ゲームがロードされた際にGUIDがなぁE��合、シスチE��が�E動的にGUIDを生成し、割り当てること (Req 1.2)、E- 生�EされたGUIDがデータベ�Eスに永続的に保存されること (Req 2.1)、E- GUIDを使用してゲームを検索し、その詳細を取得、更新、削除できること (Req 3.1, 3.2, 3.3)、E
### Non-Goals
- 既存�EDB ID (`id`) を完�EにGUIDに置き換えること。`id`は引き続き冁E��皁E��プライマリキーとして機�Eします、E- ユーザーがGUIDを直接入力また�E編雁E��るUIを提供すること�E�生成�EシスチE��が�E動的に行います）、E
## Architecture

### Existing Architecture Analysis
LitheLauncher Game Launcherは、Service Layer、Repository Pattern、データベ�Eス抽象化レイヤーを持つモジュラーチE��インを採用してぁE��す、E- **GameService**: ビジネスロジチE��をカプセル化し、UIからの要求を処琁E��ます、E- **GameRepository**: ゲームチE�Eタの永続化を抽象化し、データベ�Eスとの直接皁E��めE��取りを担当します、E- **Database Module (`database.py`)**: SQLiteチE�Eタベ�Eスへの低レベルなアクセスを提供します、E本機�Eはこれら�E既存コンポ�Eネントを拡張し、新しい識別子�E管琁E��ジチE��を統合します、E
### Architecture Pattern & Boundary Map
既存�EモジュラーチE��インとサービス持E��のアーキチE��チャパターンを維持�E拡張します。新しい`unique_identifier`は、`Game`エンチE��チE��の属性として扱われ、サービス層とリポジトリ層を介して永続化されます、E
```mermaid
graph TD
    UI[UI Layer (e.g., GameDetailDialog)] --> GameService
    GameService -- calls --> GameRepository
    GameService -- generates --> UUIDModule[Python uuid module]
    GameRepository -- persists/retrieves --> Database[SQLite Database]

    subgraph "LitheLauncher Application Boundary"
        GameService
        GameRepository
        UUIDModule
        Database
    end
```

**Architecture Integration**:
- Selected pattern: **Modularity & Service-Oriented (Extension)**. 既存�Eサービス層とリポジトリ層に機�Eを追加し、`unique_identifier`のライフサイクル管琁E��統合します、E- Domain/feature boundaries: `GameService`は`unique_identifier`の生�EとゲームチE�Eタへの割り当て、およ�E識別子によるゲーム操作�EビジネスロジチE��を担当します。`GameRepository`は`unique_identifier`を含むゲームチE�Eタの永続化と、識別子をキーとしたDB操作を抽象化します、E- Existing patterns preserved: Service Layer, Repository Pattern, チE�Eタベ�Eス抽象化、E- New components rationale: ありません。既存�Eコンポ�Eネントを拡張します、E- Steering compliance: モジュラーチE��インと関忁E�E刁E��とぁE��原則を維持します、E
### Technology Stack

| Layer | Choice / Version | Role in Feature | Notes |
|-------|------------------|-----------------|-------|
| Backend / Services | Python 3.x (uuid module) | GUIDの生�E、ゲームチE�Eタの操作ロジチE��、E| `uuid.uuid4()` を使用、E|
| Data / Storage | SQLite (via `database.py`) | ゲームメタチE�Eタ�E�Eunique_identifier`�E��E永続化、E| `games`チE�Eブルに新しいカラムを追加、E|

## System Flows

### 1. ゲーム登録フローの更新
```mermaid
sequenceDiagram
    actor User
    participant UI as GameDetailDialog
    participant GS as GameService
    participant UUID as Python_uuid_module
    participant GR as GameRepository
    participant DB as Database

    User->>UI: 新規ゲームチE�Eタ入劁E    UI->>GS: register_game(game_data)
    activate GS
    GS->>UUID: uuid.uuid4()を呼び出しGUIDを生戁E    activate UUID
    UUID-->>GS: new_unique_identifier (GUID)
    deactivate UUID
    GS->>GR: add_game(game_data with new_unique_identifier)
    activate GR
    GR->>DB: INSERT INTO games (..., unique_identifier)
    activate DB
    DB-->>GR: 成功
    deactivate DB
    GR-->>GS: 成功
    deactivate GR
    GS-->>UI: 登録済みゲームチE�Eタ
    deactivate GS
    UI-->>User: ゲーム登録成功
```
**フローレベルの決宁E*: `GameService`は、`GameRepository`にゲームチE�Eタを渡す前に`unique_identifier`を生成します、E
### 2. 既存ゲームロード時のユニ�Eク識別子割り当てフロー
```mermaid
sequenceDiagram
    participant App as LitheLauncher_App
    participant GS as GameService
    participant GR as GameRepository
    participant DB as Database
    participant UUID as Python_uuid_module

    App->>GS: get_game_details(game_id) また�E get_game_list()
    activate GS
    GS->>GR: get_game(game_id) また�E get_all_games()
    activate GR
    GR->>DB: SELECT ... FROM games WHERE id = game_id
    activate DB
    DB-->>GR: game_data (possibly without unique_identifier)
    deactivate DB
    GR-->>GS: game_data
    deactivate GR
    GS->>GS: unique_identifierの有無を確誁E    alt unique_identifierが存在しなぁE��吁E        GS->>UUID: uuid.uuid4()を呼び出しGUIDを生戁E        activate UUID
        UUID-->>GS: new_unique_identifier (GUID)
        deactivate UUID
        GS->>GR: update_game(game_id, {"unique_identifier": new_unique_identifier})
        activate GR
        GR->>DB: UPDATE games SET unique_identifier = ... WHERE id = game_id
        activate DB
        DB-->>GR: 成功
        deactivate DB
        GR-->>GS: 成功
        deactivate GR
    end
    GS-->>App: game_data (unique_identifierを含む)
    deactivate GS
```
**フローレベルの決宁E*: GUIDの自動割り当ては、ゲームがシスチE��にロードされたタイミング�E�Eget_game_details`や`get_game_list`の後など�E�で透過皁E��行われます。これにより、古ぁE��ームチE�Eタも新しい識別子シスチE��に頁E��します、E
## Requirements Traceability

| Requirement | Summary | Components | Interfaces | Flows |
|-------------|---------|------------|------------|-------|
| 1.1 | 新規ゲーム登録時にGUIDを�E動生成�E割り当て | `GameService`, `Python uuid module`, `GameRepository` | `GameService.register_game` | ゲーム登録フローの更新 |
| 1.2 | 既存ゲームロード時にGUIDがなぁE��合、�E動生成�E割り当て | `GameService`, `Python uuid module`, `GameRepository` | `GameService.get_game_details`, `GameService.get_game_list`, `GameService.update_game` | 既存ゲームロード時のユニ�Eク識別子割り当てフロー |
| 1.3 | ユニ�Eク識別子�EGUIDまた�E同等なグローバルユニ�Eク斁E���Eであること | `GameService`, `Python uuid module` | N/A | N/A |
| 2.1 | ユニ�Eク識別子をチE�Eタベ�Eスに永続的に保孁E| `GameRepository`, `Database` | `GameRepository.add_game`, `GameRepository.update_game` | ゲーム登録フローの更新, 既存ゲームロード時のユニ�Eク識別子割り当てフロー |
| 2.2 | ゲームの詳細アクセス時にユニ�Eク識別子を取征E| `GameService`, `GameRepository`, `Database` | `GameService.get_game_details`, `GameService.get_game_list`, `GameRepository.get_game`, `GameRepository.get_all_games` | N/A |
| 3.1 | ユニ�Eク識別子でゲームの詳細を取征E| `GameService`, `GameRepository` | `GameService.get_game_by_unique_identifier` | N/A |
| 3.2 | ユニ�Eク識別子でゲームの詳細を更新 | `GameService`, `GameRepository` | `GameService.update_game_by_unique_identifier` | N/A |
| 3.3 | ユニ�Eク識別子でゲームを削除 | `GameService`, `GameRepository` | `GameService.delete_game_by_unique_identifier` | N/A |

## Components and Interfaces

### Service Layer

#### GameService

| Field | Detail |
|-------|--------|
| Intent | ゲームチE�Eタに関するビジネスロジチE��と、ユニ�Eク識別孁E`unique_identifier`)の生�E、割り当て、取得、検索、操作を管琁E��る、E|
| Requirements | 1.1, 1.2, 1.3, 2.1, 2.2, 3.1, 3.2, 3.3 |
| Owner / Reviewers | Core Logic Team |

**Responsibilities & Constraints**
- 新規ゲーム登録時に`unique_identifier`を�E動生成し、ゲームチE�Eタに割り当てる、E- 既存ゲームロード時に`unique_identifier`がなぁE��合、�E動生成し、永続化する、E- `unique_identifier`を使用してゲームの詳細を取得、更新、削除する機�Eを提供する、E- `GameRepository`を介してゲームチE�Eタを永続化する、E
**Dependencies**
- Outbound: `GameRepository`  EゲームチE�Eタの永続化と検索 (P0)
- External: `uuid` module (Python standard library)  EGUIDの生�E (P0)

**Contracts**: Service [X] / API [ ] / Event [ ] / Batch [ ] / State [ ]

##### Service Interface
```python
from pathlib import Path
from typing import Optional, Dict, Any

class GameService:
    # ... 既存�EメソチE�� ...

    def register_game(self, title: str, ..., executable_path: str = None) -> Dict[str, Any]:
        """
        新規ゲームを登録し、ユニ�Eク識別子を自動生成して割り当てる、E        """
        pass # ユニ�Eク識別子生成ロジチE��を追加

    def get_game_details(self, game_id: int) -> Dict[str, Any] | None:
        """
        ゲームIDに基づぁE��ゲームの詳細を取得し、忁E��に応じてユニ�Eク識別子を生�E・割り当てる、E        """
        pass # ユニ�Eク識別子生成�E割り当てロジチE��を追加

    def get_game_list(self) -> list[Dict[str, Any]]:
        """
        すべてのゲームを取得し、忁E��に応じてユニ�Eク識別子を生�E・割り当てる、E        """
        pass # ユニ�Eク識別子生成�E割り当てロジチE��を追加

    def get_game_by_unique_identifier(self, unique_id: str) -> Dict[str, Any] | None:
        """
        ユニ�Eク識別子に基づぁE��ゲームの詳細を取得する、E        """
        pass

    def update_game_by_unique_identifier(self, unique_id: str, **kwargs) -> Dict[str, Any] | None:
        """
        ユニ�Eク識別子に基づぁE��ゲームの詳細を更新する、E        """
        pass

    def delete_game_by_unique_identifier(self, unique_id: str) -> None:
        """
        ユニ�Eク識別子に基づぁE��ゲームを削除する、E        """
        pass
```
- Preconditions: 適刁E��`game_id`また�E`unique_id`が提供されること、E- Postconditions: ゲームチE�Eタに`unique_identifier`が含まれること。操作が成功した場合、更新されたゲームチE�Eタが返されること、E
**Implementation Notes**
- `register_game`、`get_game_details`、`get_game_list`冁E��の`unique_identifier`の生�Eと割り当てロジチE��は、既存�E処琁E��ローに統合されます、E- `uuid.uuid4()`を使用してGUIDを生成し、`str()`で斁E���Eとして保存します、E
### Data Access Layer

#### GameRepository

| Field | Detail |
|-------|--------|
| Intent | ゲームチE�Eタの永続化を抽象化し、DB IDおよび`unique_identifier`に基づくCRUD操作を提供する、E|
| Requirements | 2.1, 2.2, 3.1, 3.2, 3.3 |
| Owner / Reviewers | Core Logic Team |

**Responsibilities & Constraints**
- `unique_identifier`を含むゲームチE�Eタをデータベ�Eスに保存、更新、取得する、E- `unique_identifier`をキーとしてゲームを検索、更新、削除する、E
**Dependencies**
- Outbound: `Database` module (`database.py`)  E低レベルなDB操佁E(P0)

**Contracts**: Service [X] / API [ ] / Event [ ] / Batch [ ] / State [ ]

##### Service Interface
```python
from typing import Dict, Any, List

class GameRepository:
    # ... 既存�EメソチE�� ...

    def add_game(self, game_data: Dict[str, Any]) -> int:
        """
        ゲームチE�Eタをデータベ�Eスに追加し、DB IDを返す。unique_identifierを含む、E        """
        pass # unique_identifierカラムの挿入をサポ�EチE
    def get_game(self, game_id: int) -> Dict[str, Any] | None:
        """
        DB IDに基づぁE��ゲームチE�Eタを取得する。unique_identifierを含む、E        """
        pass

    def get_all_games(self) -> List[Dict[str, Any]]:
        """
        すべてのゲームチE�Eタを取得する。unique_identifierを含む、E        """
        pass

    def update_game(self, game_id: int, data: Dict[str, Any]) -> None:
        """
        DB IDに基づぁE��ゲームチE�Eタを更新する。unique_identifierも更新可能、E        """
        pass

    def delete_game(self, game_id: int) -> None:
        """
        DB IDに基づぁE��ゲームを削除する、E        """
        pass

    def get_game_by_unique_identifier(self, unique_id: str) -> Dict[str, Any] | None:
        """
        ユニ�Eク識別子に基づぁE��ゲームチE�Eタを取得する、E        """
        pass

    def update_game_by_unique_identifier(self, unique_id: str, data: Dict[str, Any]) -> None:
        """
        ユニ�Eク識別子に基づぁE��ゲームチE�Eタを更新する、E        """
        pass

    def delete_game_by_unique_identifier(self, unique_id: str) -> None:
        """
        ユニ�Eク識別子に基づぁE��ゲームを削除する、E        """
        pass
```
- Preconditions: 適刁E��`game_id`また�E`unique_id`、およ�E有効な`game_data`が提供されること、E- Postconditions: チE�Eタベ�EスのゲームチE�Eタが正しく操作されること、E
**Implementation Notes**
- SQLクエリを修正し、`unique_identifier`カラムの挿入、E��択、更新、検索をサポ�Eトします、E- `unique_identifier`カラムにはUNIQUE制紁E��NOT NULL制紁E��設定することを検討します、E
### Infrastructure Layer

#### Database Module (`database.py`)

| Field | Detail |
|-------|--------|
| Intent | SQLiteチE�Eタベ�Eスへの低レベルなアクセスとスキーマ管琁E��E|
| Requirements | 2.1 |
| Owner / Reviewers | Infrastructure Team |

**Responsibilities & Constraints**
- `games`チE�Eブルに`unique_identifier`カラムを追加するためのスキーマ�Eイグレーションを�E琁E��る、E
**Dependencies**
- Inbound: `GameRepository`  EDB操作要汁E(P0)

**Contracts**: Service [X] / API [ ] / Event [ ] / Batch [ ] / State [ ]

##### Service Interface
```python
# database.py 冁E�E initialize_database 関数を更新
def initialize_database(db_path: str):
    """
    チE�Eタベ�Eスを�E期化し、忁E��に応じてスキーマをマイグレーションする、E    """
    pass # unique_identifierカラム追加ロジチE��を追加
```
- Preconditions: チE�Eタベ�Eスファイルがアクセス可能であること、E
**Implementation Notes**
- `initialize_database`関数冁E��、`games`チE�Eブルに`unique_identifier TEXT UNIQUE`カラムを追加するSQL ALTER TABLE斁E��実行します。カラムが既に存在する場合�EスキチE�Eします、E
## Data Models

### Logical Data Model
**Structure Definition**:
- `Game` エンチE��チE��/チE�Eブル:
    - 既存�Eフィールドに加えて、`unique_identifier` (TEXT, UNIQUE, NOT NULL) カラムを追加します、E    - `id` カラム (INTEGER PRIMARY KEY AUTOINCREMENT) は引き続き冁E��皁E��主キーとして使用し、`unique_identifier` はビジネスロジチE��で使用する外部向けの一意識別子とします、E
**Consistency & Integrity**:
- `unique_identifier` カラムには `UNIQUE` 制紁E��設定し、すべてのゲームで識別子�E一意性を保証します、E- `NOT NULL` 制紁E��設定し、すべてのゲームがユニ�Eク識別子を持つことを保証します、E
## Error Handling

### Error Strategy
- **GameNotFound**: `unique_identifier` また�E `id` に基づぁE��ゲームが見つからなぁE��合に発生するカスタム例夁E(`GameNotFoundError`) を導�Eすることを検討します、E- **DatabaseError**: チE�Eタベ�Eス操作中のエラーは、既存�Eメカニズムを通じて処琁E��れます、E- **GUID生�Eエラー**: `uuid`モジュールの生�E中にエラーが発生する可能性は低いですが、発生した場合�Eログに記録し、E��刁E��エラー処琁E��行います、E
## Testing Strategy

### Unit Tests
- `GameService`:
    - `register_game`が新しいGUIDを生成し、ゲームに割り当てること (Req 1.1)、E    - `get_game_details`や`get_game_list`がGUIDがなぁE��ームにGUIDを割り当てること (Req 1.2)、E    - `get_game_by_unique_identifier`が正しいゲームを返すこと (Req 3.1)、E    - `update_game_by_unique_identifier`がゲームを更新すること (Req 3.2)、E    - `delete_game_by_unique_identifier`がゲームを削除すること (Req 3.3)、E- `GameRepository`:
    - `add_game`が`unique_identifier`を正しく保存すること (Req 2.1)、E    - `get_game`および`get_all_games`が`unique_identifier`を含むゲームチE�Eタを返すこと (Req 2.2)、E    - `get_game_by_unique_identifier`がデータベ�Eスから正しいゲームを取得すること (Req 3.1)、E    - `update_game_by_unique_identifier`がデータベ�Eスのゲームを更新すること (Req 3.2)、E    - `delete_game_by_unique_identifier`がデータベ�Eスからゲームを削除すること (Req 3.3)、E- `database.py`:
    - `initialize_database`が`unique_identifier`カラムを正しく追加すること、E
### Integration Tests
- `GameService`と`GameRepository`の統合テスチE
    - 新規ゲーム登録から、`unique_identifier`による検索までのエンドツーエンドフロー、E    - 既存ゲームをロードし、`unique_identifier`が割り当てられ、永続化されるフロー、E
---
