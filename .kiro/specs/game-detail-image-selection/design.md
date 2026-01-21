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
**Purpose**: こ�E機�Eは、ゲーム詳細画面で画像を選択してゲームに紐付け、一覧画面で非同期に表示する機�Eを提供します。これにより、ユーザーはゲームの視覚的なカスタマイズが可能になり、アプリケーションの応答性が向上します、E**Users**: LitheLauncher Game Launcherのユーザーは、ゲームのカバ�E画像などを設定�E閲覧できます、E**Impact**: ゲーム詳細ダイアログに画像選択UIが追加され、ゲームチE�Eタに画像パスが保存されるようになります。ゲーム一覧画面では、画像を非同期にロードして表示する仕絁E��が導�Eされます、E
### Goals
- ゲーム詳細画面で、ユーザーが画像ファイル (PNG, JPG, WEBP, GIF) を選択し、アプリケーションチE�EタチE��レクトリにコピ�Eできること、E- 選択された画像�EパスがゲームのメタチE�Eタとして永続化されること、E- ゲーム詳細画面に選択された画像が表示されること、E- ゲーム一覧画面で、ゲーム画像を非同期にロードし、表示すること、E- 画像�E琁E��よ�Eファイル操作におけるエラーを適刁E��ハンドリングし、ユーザーに通知すること、E- UIの応答性を維持すること、E
### Non-Goals
- 画像編雁E���E (トリミング、フィルタリングなど)、E- 褁E��画像�E管琁E���E、E- 画像�Eクラウド同期機�E (リモートストレージサービスとの連携は封E��皁E��検討事頁E、E
## Architecture

### Architecture Pattern & Boundary Map

```mermaid
graph TD
    User --> GameDetailDialog
    GameDetailDialog --> GameService
    GameService --> ImageManager
    ImageManager --> DatabaseService
    ImageManager --> FileSystem
    GameService --> GameRepository
    GameRepository --> Database

    User --> MainWindow
    MainWindow --> GameCardWidget
    GameCardWidget --> ImageLoader
    ImageLoader --> ImageManager
    ImageLoader --> FileSystem
    ImageLoader --> PlaceholderImage

    subgraph "Application Boundary"
        GameDetailDialog
        GameService
        ImageManager
        GameRepository
        Database
        FileSystem
        MainWindow
        GameCardWidget
        ImageLoader
    end
```

**Architecture Integration**:
- Selected pattern: **Modularity & Service-Oriented (Extension)**. 既存�ELitheLauncherのサービス層とUI層を拡張し、画像管琁E��非同期ロード�Eための新しいモジュール (`ImageManager`, `ImageLoader`) を導�Eします。これにより、既存�EアーキチE��チャパターンとの整合性を保ちつつ、新しい機�Eを追加します、E- Domain/feature boundaries: `GameService`はゲームチE�Eタに関するビジネスロジチE��を担当し、`ImageManager`は画像ファイルの操作と管琁E��拁E��します。`ImageLoader`はUI層で画像�E非同期ロードを拁E��します、E- Existing patterns preserved: Service Layer, Repository Pattern, UI Layerの明確な刁E��、E- New components rationale:
    - `ImageManager`: 画像ファイルのコピ�E、削除、パス生�EとぁE��た低レベルのファイルシスチE��操作と、Pillowを使用した画像�E琁E��忁E��に応じて�E�をカプセル化します。これにより、`GameService`からファイル操作�E詳細を�E離し、E��忁E�E刁E��を俁E��します、E    - `ImageLoader`: PySide6の`QRunnable`と`QThreadPool`を利用して、バチE��グラウンドでの画像ロード�E琁E��UI更新のためのシグナル発行を拁E��します。これにより、UIの応答性を確保し、E��同期処琁E�EロジチE��を集中管琁E��ます、E- Steering compliance: モジュラーチE��インと関忁E�E刁E��とぁE��原則を維持します、E
### Technology Stack

| Layer | Choice / Version | Role in Feature | Notes |
|-------|------------------|-----------------|-------|
| Frontend / CLI | PySide6 | UIコンポ�EネンチE(GameDetailDialog, MainWindow, GameCardWidget) の拡張と画像表示、E| Qtのシグナル/スロチE��とQPixmapを活用、E|
| Backend / Services | Python 3.x, Pillow | 画像ファイルのコピ�E、パスの管琁E��Pillowを用ぁE��画像�E琁E��読み込み、形式変換�E�を拁E��、E| Pillowは新規追加依存、E|
| Data / Storage | SQLite (via `database.py`) | ゲームメタチE�Eタ�E�画像パス�E��E永続化、E| 既存�EチE�Eタベ�Eススキーマに画像パスを追加、E|
| Messaging / Events | PySide6 Signals/Slots | UIスレチE��とバックグラウンドスレチE��間�E非同期通信、E| ImageLoaderからUIコンポ�Eネントへの画像ロード完亁E��知、E|
| Infrastructure / Runtime | Python Virtual Environment | 依存関俁E(Pillow) の管琁E��E| `requirements.txt`にPillowを追加、E|

## System Flows

### 1. ゲーム詳細画面での画像選択�E保存フロー

```mermaid
sequenceDiagram
    actor User
    participant GDD as GameDetailDialog
    participant GS as GameService
    participant IM as ImageManager
    participant FS as FileSystem
    participant DB as Database

    User->>GDD: "Browse"ボタンをクリチE��
    activate GDD
    GDD->>GDD: ファイルダイアログを開ぁE(PNG, JPG, WEBP, GIFフィルタ)
    User->>GDD: 画像ファイルを選抁E    GDD->>GS: save_game_image(game_id, selected_image_path)
    activate GS
    GS->>IM: copy_image_to_appdata(game_id, source_path)
    activate IM
    IM->>FS: 画像ファイルをdata/{game_id}/images/にコピ�E
    activate FS
    FS-->>IM: コピ�E完亁Eエラー
    deactivate FS
    IM-->>GS: コピ�Eされたファイルパス/エラー
    deactivate IM
    alt 画像コピ�E成功
        GS->>DB: ゲームの画像パスを更新
        activate DB
        DB-->>GS: 更新完亁E        deactivate DB
        GS-->>GDD: 成功
    else 画像コピ�E失敁E        GS-->>GDD: エラー
    end
    deactivate GS
    GDD->>GDD: 画像をUIに表示/エラーメチE��ージ表示
    deactivate GDD
```

### 2. ゲーム一覧画面での画像非同期ロードフロー

```mermaid
sequenceDiagram
    actor User
    participant MW as MainWindow
    participant GCW as GameCardWidget
    participant IL as ImageLoader
    participant IM as ImageManager
    participant FS as FileSystem

    User->>MW: 一覧画面を表示
    activate MW
    loop 各GameCard
        MW->>GCW: ゲーム惁E�� (画像パス含む) を渡ぁE        activate GCW
        GCW->>GCW: プレースホルダー画像を表示
        GCW->>IL: load_image_async(image_path)
        activate IL
        IL->>IL: QThreadPoolで画像ロードタスクを開姁E        alt 画像ロード�E劁E            IL->>IL: ロードした画像をQPixmapに変換
            IL-->>GCW: image_loaded(QPixmap) シグナル
            GCW->>GCW: プレースホルダーを実画像に置き換ぁE        else 画像ロード失敁E            IL-->>GCW: image_load_failed() シグナル
            GCW->>GCW: エラー画像表示 (オプション)
        end
        deactivate IL
        deactivate GCW
    end
    deactivate MW
```

## Requirements Traceability

| Requirement | Summary | Components | Interfaces | Flows |
|-------------|---------|------------|------------|-------|
| 1.1 | "Browse"ボタン表示 | `GameDetailDialog` | UI (`QPushButton`) | ゲーム詳細画面での画像選択�E保存フロー |
| 1.2 | ファイルダイアログ表示 | `GameDetailDialog` | UI (`QFileDialog`) | ゲーム詳細画面での画像選択�E保存フロー |
| 1.3 | ファイルフィルタリング | `GameDetailDialog` | UI (`QFileDialog`フィルタ) | ゲーム詳細画面での画像選択�E保存フロー |
| 2.1 | 画像コピ�E | `GameService`, `ImageManager`, `FileSystem` | `ImageManager.copy_image_to_appdata` | ゲーム詳細画面での画像選択�E保存フロー |
| 2.2 | 画像パス保孁E| `GameService`, `GameRepository`, `Database` | `GameService.save_game_image` | ゲーム詳細画面での画像選択�E保存フロー |
| 2.3 | コピ�E失敗エラー | `GameService`, `ImageManager`, `GameDetailDialog` | エラー通知メカニズム | ゲーム詳細画面での画像選択�E保存フロー |
| 3.1 | 詳細画面画像表示 | `GameDetailDialog` | UI (`QLabel`また�E`QGraphicsView`) | ゲーム詳細画面での画像選択�E保存フロー |
| 3.2 | 詳細画面画像更新 | `GameDetailDialog` | UI更新ロジチE�� | ゲーム詳細画面での画像選択�E保存フロー |
| 4.1 | 一覧画面非同期表示 | `MainWindow`, `GameCardWidget`, `ImageLoader` | `ImageLoader.load_image_async` | ゲーム一覧画面での画像非同期ロードフロー |
| 4.2 | プレースホルダー表示 | `GameCardWidget`, `ImageLoader` | UI更新ロジチE�� | ゲーム一覧画面での画像非同期ロードフロー |
| 4.3 | 実画像置き換ぁE| `GameCardWidget`, `ImageLoader` | `ImageLoader.image_loaded`シグナル | ゲーム一覧画面での画像非同期ロードフロー |

## Components and Interfaces

### UI Layer

#### GameDetailDialog
| Field | Detail |
|-------|--------|
| Intent | ゲームの詳細惁E��を表示・編雁E��、画像選択�E保存機�Eを提供すめE|
| Requirements | 1.1, 1.2, 1.3, 2.3, 3.1, 3.2 |
| Owner / Reviewers | UI Team |

**Responsibilities & Constraints**
- ゲーム詳細惁E��の表示と編雁E��E- 画像選択用の"Browse"ボタンの提供とファイルダイアログの起動、E- 選択された画像パスを`GameService`に渡し、結果を受け取る、E- 選択された画像をUI上に表示し、更新する、E- エラーメチE��ージの表示、E
**Dependencies**
- Inbound: `MainWindow`  E詳細ダイアログの起勁E(P0)
- Outbound: `GameService`  Eゲーム惁E��の保存、画像ファイルの保孁E(P0)
- Outbound: `QFileDialog`  Eファイル選択ダイアログ (P0)

**Contracts**: Service [X] / API [ ] / Event [ ] / Batch [ ] / State [ ]

##### Service Interface
```python
# GameDetailDialogはGameServiceと連携しまぁE# GameServiceの既存�Eインターフェースに以下�E機�Eが追加/利用されまぁEclass GameService:
    def save_game_image(self, game_id: str, source_image_path: Path) -> Path:
        """
        持E��された画像をappdataにコピ�Eし、ゲームの画像パスを更新します、E        成功した場合�Eコピ�Eされた画像�EPathを返します、E        """
        pass
    
    def get_game_image_path(self, game_id: str) -> Optional[Path]:
        """
        持E��されたゲームの画像パスを取得します、E        """
        pass
```

**Implementation Notes**
- `QFileDialog`を使用してファイル選択を行い、E��択されたファイルのパスを`GameService.save_game_image`に渡す、E- `GameService`から返された画像パスを使用して`QPixmap`をロードし、UI (`QLabel`など) に表示する、E- `GameService`からのエラーを適刁E��ハンドルし、ユーザーに通知する、E
#### MainWindow
| Field | Detail |
|-------|--------|
| Intent | メインアプリケーションウィンドウとしてゲーム一覧を表示し、各ゲームカードを管琁E��めE|
| Requirements | 4.1 |
| Owner / Reviewers | UI Team |

**Responsibilities & Constraints**
- ゲームカードウィジェチE�� (`GameCardWidget`) の生�Eと配置、E- `GameCardWidget`への画像パスの提供、E
**Dependencies**
- Outbound: `GameCardWidget`  Eゲーム惁E��の表示 (P0)

**Contracts**: Service [ ] / API [ ] / Event [ ] / Batch [ ] / State [ ]

**Implementation Notes**
- 既存�Eゲーム一覧表示ロジチE��を拡張し、各ゲームカードに画像パスを渡す、E- `GameCardWidget`が`ImageLoader`を利用して非同期に画像をロードするため、`MainWindow`側での直接皁E��画像ロード�E琁E�E不要、E
#### GameCardWidget
| Field | Detail |
|-------|--------|
| Intent | 一覧画面の吁E��ームエントリを表示し、画像を非同期にロードして表示する |
| Requirements | 4.1, 4.2, 4.3 |
| Owner / Reviewers | UI Team |

**Responsibilities & Constraints**
- ゲームのタイトル、情報、およ�E関連画像�E表示、E- `ImageLoader`からのシグナルを受け取り、ロードされた画像をUIに表示、E- 画像ロード中はプレースホルダー画像を表示、E
**Dependencies**
- Inbound: `MainWindow`  Eゲーム惁E��の提侁E(P0)
- Outbound: `ImageLoader`  E画像�E非同期ローチE(P0)

**Contracts**: Service [ ] / API [ ] / Event [X] / Batch [ ] / State [ ]

##### Event Contract
- Subscribed events:
    - `ImageLoader.image_loaded(QPixmap)`: 画像ロードが成功した際に受け取る、E    - `ImageLoader.image_load_failed()`: 画像ロードが失敗した際に受け取る、E
**Implementation Notes**
- `ImageLoader`のインスタンスを生成し、`image_loaded`シグナルと`image_load_failed`シグナルを�E身のスロチE��に接続する、E- `ImageLoader.load_image_async`を呼び出して画像�Eロードを開始し、ロード中はプレースホルダーを表示する、E
### Service Layer

#### GameService
| Field | Detail |
|-------|--------|
| Intent | ゲームチE�Eタに関するビジネスロジチE��と画像ファイルの管琁E��連携する |
| Requirements | 2.1, 2.2, 2.3 |
| Owner / Reviewers | Core Logic Team |

**Responsibilities & Constraints**
- ゲームの画像パスの保存、更新、取得、E- `ImageManager`を介した画像ファイルのコピ�E操作�Eトリガー、E- ファイル操作エラーのハンドリングと`GameDetailDialog`への通知、E
**Dependencies**
- Outbound: `ImageManager`  E画像ファイルの操佁E(P0)
- Outbound: `GameRepository`  EゲームチE�Eタ�E�画像パス含む�E��E永続化 (P0)

**Contracts**: Service [X] / API [ ] / Event [ ] / Batch [ ] / State [ ]

##### Service Interface
```python
# 既存�EGameServiceインターフェースを拡張
class GameService:
    # ... 既存�EメソチE�� ...

    def save_game_image(self, game_id: str, source_image_path: Path) -> Path:
        """
        持E��された画像をappdataにコピ�Eし、ゲームの画像パスを更新します、E        成功した場合�Eコピ�Eされた画像�EPathを返します、E        """
        pass

    def get_game_image_path(game_id: str) -> Optional[Path]:
        """
        持E��されたゲームの画像パスを取得します、E        """
        pass
```

#### ImageManager (新規コンポ�EネンチE
| Field | Detail |
|-------|--------|
| Intent | 画像ファイルのコピ�E、削除、パス生�EとぁE��た低レベルのファイルシスチE��操作を管琁E��めE|
| Requirements | 2.1, 2.3 |
| Owner / Reviewers | Core Logic Team |

**Responsibilities & Constraints**
- 選択された画像ファイルをアプリケーションの`data/`チE��レクトリ (`data/{game_id}/images/`形弁E にコピ�Eする、E- コピ�E先�Eファイルパスを生成する、E- ファイル操作エラー (権限、ディスク容量など) を適刁E��ハンドリングし、`GameService`に通知する、E- Pillowライブラリを使用して、忁E��に応じて画像形式�E変換などを行う�E�今回は直接皁E��変換は不要だが、封E��皁E��拡張を見越して�E�、E
**Dependencies**
- Outbound: `FileSystem`  Eファイルコピ�E操佁E(P0)
- Outbound: `Pillow`  E画像�E琁E(P0)

**Contracts**: Service [X] / API [ ] / Event [ ] / Batch [ ] / State [ ]

##### Service Interface
```python
from pathlib import Path
from typing import Optional

class ImageManager:
    def copy_image_to_appdata(self, game_id: str, source_path: Path) -> Path:
        """
        持E��された画像をappdata冁E�Eゲーム固有ディレクトリにコピ�Eします、E        コピ�EされたファイルのPathを返します、E        """
        pass

    def get_appdata_image_path(self, game_id: str, filename: str) -> Path:
        """
        持E��されたゲームIDとファイル名に基づぁE��、appdata冁E�E画像パスを生成します、E        """
        pass

    def delete_game_image(self, game_id: str, filename: str) -> None:
        """
        持E��されたゲームの画像をappdataから削除します、E        """
        pass
```

#### ImageLoader (新規コンポ�EネンチE
| Field | Detail |
|-------|--------|
| Intent | バックグラウンドスレチE��で画像を非同期にロードし、UIスレチE��に結果を通知する |
| Requirements | 4.1, 4.2, 4.3 |
| Owner / Reviewers | UI Team |

**Responsibilities & Constraints**
- `QRunnable`を継承し、`QThreadPool`で実行可能な画像ロードタスクを定義、E- バックグラウンドスレチE��で持E��された画像ファイルをロードし、`QPixmap`に変換する、E- ロード完亁E��た�E失敗時にUIスレチE��へのシグナルを発行、E- UIスレチE��をブロチE��しなぁE��と、E
**Dependencies**
- Inbound: `GameCardWidget`  Eロード要汁E(P0)
- Outbound: `Pillow`  E画像ファイルの読み込み (P0)
- Outbound: `PySide6.QtGui.QPixmap`  Eロードした画像�E変換 (P0)

**Contracts**: Service [ ] / API [ ] / Event [X] / Batch [ ] / State [ ]

##### Event Contract
- Published events:
    - `image_loaded(QPixmap)`: 画像が正常にロードされ、`QPixmap`オブジェクトをUIスレチE��に送信するシグナル、E    - `image_load_failed()`: 画像ロード中にエラーが発生した場合にUIスレチE��に通知するシグナル、E
**Implementation Notes**
- `QRunnable`を継承したクラスとして実裁E��、`run`メソチE��冁E��Pillowを使用して画像をロードし、`QPixmap`に変換する、E- `QObject`を継承した冁E��クラスにシグナルを定義し、スレチE��セーフな形でUIスレチE��に結果を通知する、E
### Data Layer

#### GameRepository
- 既存�Eコンポ�Eネント。ゲームオブジェクトに画像パスを格納するフィールドを追加し、データベ�Eスとの永続化ロジチE��を更新、E
#### Database
- 既存�Eコンポ�Eネント。ゲームチE�Eブルのスキーマに画像パスを格納するカラムを追加、E
## Data Models

### Domain Model
- `Game` エンチE��チE��: 既存�E`Game`エンチE��チE��に画像パスを表すフィールドを追加、E
### Logical Data Model
- `Game`チE�Eブル: `image_path` (TEXT) カラムを追加、E
## Error Handling

### Error Strategy
- **ファイル操作エラー**: `ImageManager`冁E��`try-except`ブロチE��を用ぁE��`FileNotFoundError`, `PermissionError`, `IOError`などを捕捉。`GameService`を通じて`GameDetailDialog`にエラーメチE��ージを返す、E- **画像ロードエラー**: `ImageLoader`冁E��Pillowによる画像読み込みエラーや`QPixmap`変換エラーを捕捉。`image_load_failed`シグナルを通じて`GameCardWidget`に通知、E- **UIエラー**: `GameDetailDialog`および`GameCardWidget`は受け取ったエラー惁E��に基づき、ユーザーフレンドリーなメチE��ージを表示、E
## Testing Strategy

- **Unit Tests**:
    - `ImageManager`: `copy_image_to_appdata`, `get_appdata_image_path`などのファイル操作ロジチE��、E    - `ImageLoader`: `run`メソチE��冁E�E画像ロードとシグナル発行ロジチE���E�モチE��化したQPixmap変換とシグナル接続）、E    - `GameService`: `save_game_image`が`ImageManager`と`GameRepository`を正しく呼び出すか、E- **Integration Tests**:
    - `GameDetailDialog`と`GameService`の連携: "Browse"ボタンクリチE��から画像保存までのフロー、E    - `MainWindow`と`GameCardWidget`と`ImageLoader`の連携: 一覧画面での非同期画像表示フロー、E- **E2E/UI Tests (pytest-qt)**:
    - ゲーム詳細画面で画像を正しく選択�E保存し、UIに表示されること、E    - ゲーム一覧画面で褁E��のゲームカード�E画像が非同期に表示されること、E    - 無効なファイルを選択した場合やファイルコピ�E失敗時のエラーメチE��ージ表示、E
