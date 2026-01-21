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
**Purpose**: こ�E機�Eは、ゲームチE�EタのチE�Eタベ�Eススキーマから既存�E「カバ�Eアートパス(旧)」フィールドとそ�E関連コードを削除し、シスチE��をクリーンアチE�Eします、E**Users**: 主に開発老E��メンチE��ンス拁E��老E��、クリーンなコード�Eースと最新のチE�EタモチE��の恩恵を受けます。エンドユーザーには直接皁E��影響はありませんが、アプリケーションの安定性と保守性の向上に貢献します、E**Impact**: `Game`チE�Eブルのスキーマを変更し、`game_repository.py`および`game_detail_dialog.py`冁E�E`cover_art_path`フィールドへの参�Eを削除また�E更新します、E
### Goals
- チE�Eタベ�Eススキーマから`cover_art_path`フィールドを完�Eに削除する、E- `cover_art_path`フィールドを参�EしてぁE��すべてのコードを削除また�E`image_path`フィールドへの参�Eに更新する、E- フィールド削除後もアプリケーションが正しく動作し、ゲームのカバ�Eアート表示およびゲーム起動機�Eに影響がなぁE��とを保証する、E
### Non-Goals
- 既存�E`image_path`フィールド�E機�E拡張めE��更、E- `cover_art_path`フィールドに格納されてぁE��チE�Eタの`image_path`フィールドへの移行（「旧」フィールドであり、データが不要また�E既に移行済みと想定されるため�E�、E- チE�Eタベ�EスマイグレーションチE�Eルの導�E、E
## Architecture

### Existing Architecture Analysis
既存�EアーキチE��チャでは、`database.py`で定義されたSQLiteチE�Eタベ�EスがゲームチE�Eタを永続化してぁE��す。`game_repository.py`はチE�Eタベ�Eス操作を抽象化し、`game_service.py`がビジネスロジチE��を提供します。`game_detail_dialog.py`はUIを通じてゲームチE�Eタの表示と編雁E��可能にし、`game_card_widget.py`はゲームカード�E視覚的表現を担当します。`cover_art_path`フィールド�E、これらのコンポ�Eネント間でゲームのカバ�Eアート�Eパスを管琁E��るために使用されてぁE��した、E
### Architecture Pattern & Boundary Map
**Architecture Integration**:
- Selected pattern: 既存�EレイヤードアーキチE��チャとリポジトリパターンを維持します、E- Domain/feature boundaries: `GameRepository`のチE�Eタ永続化墁E��、`GameDetailDialog`のUI墁E��、およ�EチE�Eタベ�Eススキーマ�E墁E��が影響を受けます、E- Existing patterns preserved: サービスレイヤー、リポジトリパターン、UIレイヤーの刁E��は維持されます、E- Steering compliance: モジュール性、E��忁E�E刁E��、テスト可能性の原則が維持されます、E
### Technology Stack

| Layer | Choice / Version | Role in Feature | Notes |
|-------|------------------|-----------------|-------|
| Backend / Services | Python 3.x | `game_repository.py`と`game_service.py`でのチE�EタモチE��更新と参�E削除 | |
| Data / Storage | SQLite (via `src/database.py`) | `Game`チE�Eブルの`cover_art_path`カラムの削除 | チE�Eタベ�Eススキーマ�E変更 |

## System Flows
こ�E機�Eは、褁E��なシスチE��フローの変更を伴ぁE��せん。主な流れは、データベ�Eススキーマ�E更新と、それに続くコード�EースのクリーンアチE�Eです、E
## Requirements Traceability

| Requirement | Summary | Components | Interfaces | Flows |
|-------------|---------|------------|------------|-------|
| 1.1 | 古ぁE��バ�Eアートパスフィールド�E削除 (DBスキーチE | `database.py`, `game_repository.py` | `GameRepository`のチE�EタモチE�� | - |
| 1.2 | 古ぁE��ィールドへのチE�Eタ保存停止 | `game_repository.py` | `GameRepository`のチE�EタモチE�� | - |
| 2.1 | 関連コード�E削除 | `game_repository.py`, `game_detail_dialog.py` | `GameRepository`のCRUDインターフェース, `GameDetailDialog`のチE�EタバインチE��ング | - |
| 2.2 | エラーの適刁E��処琁E| `game_repository.py`, `game_detail_dialog.py` | 例外�E琁E| - |
| 3.1 | カバ�Eアート表示の互換性 | `game_detail_dialog.py`, `game_card_widget.py`, `image_manager.py` | `GameDetailDialog`のUI更新, `GameCardWidget`の画像表示 | - |
| 3.2 | ゲーム起動�E互換性 | `launcher_service.py` (間接皁E, `main_window.py` (間接皁E | 全体的なアプリケーションの安定性 | - |

## Components and Interfaces

### Data Access Layer

#### `database.py`

| Field | Detail |
|-------|--------|
| Intent | SQLiteチE�Eタベ�Eススキーマ�E定義と管琁E|
| Requirements | 1.1 |
| Owner / Reviewers | - |

**Responsibilities & Constraints**
- `Game`チE�Eブルから`cover_art_path`カラムを削除する、E- チE�Eタベ�Eスのマイグレーションは手動で実行されることを前提とする�E��E動�EイグレーションチE�Eルは導�EしなぁE��、E
**Dependencies**
- Inbound: `game_repository.py`  EチE�Eタベ�Eススキーマ�E依孁E(P0)

**Contracts**: Service [ ] / API [ ] / Event [ ] / Batch [ ] / State [x]

##### State Management
- State model: `Game`チE�Eブルから`cover_art_path`カラムが削除された状慁E- Persistence & consistency: 変更後�EスキーマとチE�Eタの一貫性を手動で確認する、E
**Implementation Notes**
- 既存�E`Game`チE�Eブルのスキーマ定義を変更するSQL斁E��生�Eし、実行する忁E��がある、E
#### `game_repository.py`

| Field | Detail |
|-------|--------|
| Intent | ゲームチE�Eタの永続化と取得ロジチE�� |
| Requirements | 1.1, 1.2, 2.1, 2.2 |
| Owner / Reviewers | - |

**Responsibilities & Constraints**
- `Game`オブジェクト�ECRUD操作から`cover_art_path`フィールドへの参�Eを削除する、E- チE�Eタベ�Eス操作時に`cover_art_path`フィールドが存在しなぁE��とによるエラーを適刁E��処琁E��る、E
**Dependencies**
- Outbound: `database.py`  EチE�Eタベ�Eス操佁E(P0)

**Contracts**: Service [x] / API [ ] / Event [ ] / Batch [ ] / State [ ]

##### Service Interface
```python
class GameRepository:
    def get_all_games(self) -> List[Dict]:
        # cover_art_pathフィールドを含まなぁE��ータ構造を返す
        pass

    def get_game(self, game_id: int) -> Optional[Dict]:
        # cover_art_pathフィールドを含まなぁE��ータ構造を返す
        pass

    def add_game(self, game_data: Dict) -> int:
        # cover_art_pathフィールドを処琁E��なぁE        pass

    def update_game(self, game_id: int, game_data: Dict) -> None:
        # cover_art_pathフィールドを処琁E��なぁE        pass
```

**Implementation Notes**
- SQLクエリから`cover_art_path`カラムを削除する、E- `game_data`辞書を�E琁E��る際に`cover_art_path`キーを無視するロジチE��を追加する、E
### UI Layer

#### `game_detail_dialog.py`

| Field | Detail |
|-------|--------|
| Intent | 個、E�Eゲームの詳細表示と編雁E|
| Requirements | 2.1, 2.2, 3.1 |
| Owner / Reviewers | - |

**Responsibilities & Constraints**
- `cover_art_path`に関連するUI要素�E�EQLineEdit`など�E�を削除する、E- ゲームチE�EタとUI要素間�EバインチE��ングから`cover_art_path`への参�Eを削除する、E- `image_path`フィールドを使用してカバ�Eアートを表示および編雁E��る既存�E機�Eを維持する、E
**Dependencies**
- Inbound: `game_service.py` (間接皁E  EゲームチE�Eタの取得と更新 (P0)

**Contracts**: Service [ ] / API [ ] / Event [ ] / Batch [ ] / State [ ]

##### Service Interface
(直接皁E��サービスインターフェースの変更なし、UI要素の削除)

**Implementation Notes**
- `cover_art_path_line_edit`とぁE��名前の`QLineEdit`オブジェクトと、それに関連するレイアウト、シグナル/スロチE��接続、データバインチE��ングロジチE��を削除する、E
#### `game_card_widget.py`

| Field | Detail |
|-------|--------|
| Intent | 個、E�Eゲームカード�E視覚的表現 |
| Requirements | 3.1 |
| Owner / Reviewers | - |

**Responsibilities & Constraints**
- 既に`image_path`を使用してぁE��ため、`cover_art_path`に関するコメントや参�EをクリーンアチE�Eする、E
**Dependencies**
- Inbound: `image_loader.py`  E画像�E非同期ローチE(P0)

**Contracts**: Service [ ] / API [ ] / Event [ ] / Batch [ ] / State [ ]

##### Service Interface
(直接皁E��サービスインターフェースの変更なぁE

**Implementation Notes**
- 古い`cover_art_path`に関するコメントを削除する。コード�E体�E既に`image_path`を使用してぁE��ため、大きな変更は不要、E
## Data Models

### Logical Data Model
`Game`チE�Eブルから`cover_art_path`カラムが削除されます。既存�E`image_path`カラムがカバ�Eアート�Eパスを管琁E��る唯一のフィールドとなります、E
### Physical Data Model
**For Relational Databases**:
- `Game`チE�Eブルのスキーマから`cover_art_path`カラムを削除するSQL斁E��実行します、E
## Error Handling

### Error Strategy
- 既存�Eコードが`cover_art_path`フィールドにアクセスしよぁE��した場合、Pythonの`KeyError`めE��ータベ�Eスアクセスエラーが発生する可能性があります、E- これら�Eエラーは、該当するコードから`cover_art_path`への参�Eを削除することで解決します、E- 予期せぬエラーが発生した場合�E、既存�Eロギングメカニズム(`game_launcher_logger.py`)を通じてログに記録し、アプリケーションがクラチE��ュしなぁE��ぁE��適刁E��処琁E��ます、E
### Error Categories and Responses
- **開発時エラー**: `cover_art_path`への参�Eが残ってぁE��ことによる`KeyError`や`AttributeError`。これらは開発中に修正されるべきです、E- **チE�Eタベ�Eスエラー**: スキーマ変更後�EチE�Eタベ�Eスアクセスに関するエラー。これも開発中にチE��トを通じて検�E・修正します、E
## Testing Strategy

### Default sections
- **Unit Tests**:
    - `test_database.py`: `cover_art_path`カラムが`Game`チE�Eブルから削除されてぁE��ことを検証するチE��ト、E    - `test_game_repository.py`: `game_repository.py`が`cover_art_path`フィールドを処琁E��ようとしなぁE��と、およ�E`image_path`フィールドで正しく動作することを検証するチE��ト、E    - `test_game_detail_dialog.py`: `cover_art_path`に関連するUI要素が存在しなぁE��と、およ�E`image_path`フィールドでUIが正しく動作することを検証するチE��ト、E- **Integration Tests**:
    - `test_integration_image_registration.py`: `image_path`フィールドがカバ�Eアート�E登録と表示に正しく使用されることを検証するチE��ト、E    - アプリケーション全体でゲームの追加、編雁E��削除、起動が正しく動作し、`cover_art_path`関連のエラーが発生しなぁE��とを検証するチE��ト�
