# Design Document: Set App Icon

## Overview
LitheLauncher Game Launcher のブランドアイチE��チE��チE��を強化し、ユーザーがデスクトップやタスクバ�Eでアプリケーションを容易に識別できるようにするため、カスタムアイコン�E�Eres/icon.png`�E�を設定します、E
### Goals
- アプリケーションのメインウィンドウにアイコンを表示する、E- Windows のタスクバ�Eにおいて、Python のチE��ォルトアイコンではなぁELitheLauncher のアイコンが表示されるよぁE��する、E- アイコンファイルが存在しなぁE��合でも、アプリケーションが正常に起動するよぁE��する、E
### Non-Goals
- アイコン画像�E動的な生�E�E�手動で用意された画像を使用することを前提とする�E�、E- 褁E��のアイコンチE�Eマ�E刁E��替え、E
## Architecture

### Existing Architecture Analysis
PySide6 を�EースとしたチE��クトップアプリケーションであり、`main.py` をエントリポイントとして `MainWindow` が起動されます。アイコン設定�E Qt の標準的なメカニズム�E�EsetWindowIcon`�E�およ�E Windows 固有�E API 呼び出し！ESetCurrentProcessExplicitAppUserModelID`�E�を利用して統合します、E
### Architecture Pattern & Boundary Map
既存�E UI アーキチE��チャに以下�E処琁E��統合します、E
- **エントリポインチE(`main.py`)**: Windows 環墁E��おいてプロセスの `AppUserModelID` を設定し、タスクバ�Eでのアイコン表示を正常化する、E- **メインウィンドウ (`src/main_window.py`)**: `QIcon` を使用してウィンドウアイコンを設定する、E
## Technology Stack

| Layer | Choice / Version | Role in Feature | Notes |
|-------|------------------|-----------------|-------|
| Frontend / UI | PySide6 | GUI フレームワーク | `QIcon`, `setWindowIcon` を使用 |
| OS Integration | ctypes (Standard Lib) | Windows API 呼び出ぁE| `AppUserModelID` 設定に使用 |

## Requirements Traceability

| Requirement | Summary | Components | Interfaces |
|-------------|---------|------------|------------|
| 1.1 | 256x256 PNG の存在確誁E| MainWindow | `os.path.exists` |
| 1.2 | アイコンに "UiU" を含む | (Manual/Resource) | N/A |
| 2.1 | `setWindowIcon` による設宁E| MainWindow | `setWindowIcon()` |
| 2.2 | タスクバ�Eへの表示 | main.py | `ctypes` API |
| 2.3 | フォールバック処琁E| MainWindow | Error handling |

## Components and Interfaces

### UI Layer

#### MainWindow (`src/main_window.py`)

| Field | Detail |
|-------|--------|
| Intent | ウィンドウのプロパティとしてアイコンを設定すめE|
| Requirements | 1.1, 2.1, 2.3 |

**Responsibilities & Constraints**
- `res/icon.png` を読み込み、`QIcon` オブジェクトを作�Eする、E- `setWindowIcon()` を呼び出して自身に適用する、E- ファイルが存在しなぁE��合�Eエラーをログ出力し、�E琁E��スキチE�Eする�E�フォールバック�E�、E
**Dependencies**
- Outbound: `PySide6.QtGui.QIcon`  Eアイコンオブジェクト作�E (P0)

**Contracts**: Service [x] / API [ ] / Event [ ] / Batch [ ] / State [ ]

##### Service Interface
```python
# MainWindow クラス冁E��の冁E��メソチE��また�E初期化�E琁Edef _set_app_icon(self) -> None:
    ...
```

### Application Entry

#### main.py

| Field | Detail |
|-------|--------|
| Intent | プロセスレベルの初期設定を行う |
| Requirements | 2.2 |

**Responsibilities & Constraints**
- Windows 環墁E��おいて `AppUserModelID` を設定する、E- `QApplication` インスタンス化�E直前に実行する、E
**Dependencies**
- External: `ctypes`  EWindows Shell32 API 呼び出ぁE(P1)

## Data Models
本機�Eでは永続的なチE�EタモチE��の変更は行いません、E
## Error Handling

### Error Strategy
- ファイル入出力エラー�E�EileNotFoundError 等）に対しては、例外をキャチE��してログを記録し、ユーザーにはチE��ォルト�E状態（アイコンなし）でアプリを継続提供する、E
### Error Categories and Responses
- **System Errors**:
    - アイコンファイル欠落: `logging.warning` を�E力し、デフォルトアイコンを使用、E    - Windows API 呼び出し失敁E 例外をキャチE��し、無視して続行（タスクバ�E表示のみが影響を受けるため�E�、E
## Testing Strategy
- **Unit Tests**:
    - `res/icon.png` のパス解決ロジチE��のチE��ト、E- **Integration Tests**:
    - `MainWindow` 初期化時に `windowIcon()` が設定されてぁE��か�E確認、E- **UI Tests**:
    - �E�手動）Windows タスクバ�Eで正しいアイコンが表示されてぁE��か、E    - �E�手動）アイコンファイルがなぁE��態でアプリが正常に起動するか、E
