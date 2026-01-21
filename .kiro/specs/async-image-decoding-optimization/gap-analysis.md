# Gap Analysis: Async Image Decoding Optimization

## 1. Analysis Summary
- **現状の課題**: `ImageLoader` が非同期で動作しているものの、画像の「スケーリング」処理がメインUIスレッド（`GameCardWidget._on_image_loaded`）で行われており、大量データ時にFPS低下の原因となる可能性がある。
- **スレッドセーフティ**: `QPixmap.fromImage` がバックグラウンドスレッドで呼ばれているが、`QPixmap` はGUIスレッドでの作成が推奨される。`QImage` をバックグラウンドで処理し、GUIスレッドで `QPixmap` に変換するのが安全かつ効率的。
- **リソース管理**: 現在はグローバルな `QThreadPool` を使用しており、他の非同期処理（DBアクセス等）とリソースを共有している。画像専用のプール管理が欠如している。
- **リクエスト制御**: スクロール中に不要になった読み込みリクエストをキャンセル、または結果を無視する仕組み（Request ID/Sequence tracking）がない。

## 2. Requirement-to-Asset Map

| Requirement | Asset(s) | Status | Gap/Constraint |
|-------------|----------|--------|----------------|
| Req 1: 非同期画像デコード | `src/image_loader.py` | Partial | スケーリング処理がUIスレッドに残っている。QImageベースの処理への移行が必要。 |
| Req 2: ワーカープール管理 | `src/game_card_widget.py` | Missing | グローバルプールを使用中。専用プールの導入が必要。 |
| Req 3: キャンセル/リクエスト制御 | `src/game_card_widget.py` | Missing | 古いリクエストの結果を無視する仕組みがない。 |
| Req 3: プレースホルダー | `src/game_card_widget.py` | Exist | "Loading..." テキストを表示中。より洗練された表示への改善余地あり。 |

## 3. Implementation Approach Options

### Option A: Extend Existing Components (Recommended)
`ImageLoader` と `GameCardWidget` を拡張して課題を解決する。

- **内容**:
  - `ImageLoader` に `target_size` 引数を追加し、バックグラウンドで `QImage.scaled` を実行する。
  - `ImageLoader` は `QPixmap` ではなく `QImage` を `emit` する。
  - `GameCardWidget` に `current_request_id` を持たせ、古いリクエストの結果を破棄する。
- **Trade-offs**:
  - ✅ 既存の構造を活かせるため、実装コストが低い。
  - ✅ 依存関係がシンプル。
  - ❌ `GameCardWidget` ごとにプール管理のロジックが分散する可能性がある。

### Option B: Centralized Image Service
画像デコード専用のサービス（例: `AsyncImageService`）を導入する。

- **内容**:
  - 専用の `QThreadPool` を管理し、リクエストのスケジューリング、重複排除、キャッシュを行う。
- **Trade-offs**:
  - ✅ リソース管理が一元化され、効率的。
  - ✅ 複雑なキャッシュ戦略などを導入しやすい。
  - ❌ 新規設計・実装のコストが高い。

## 4. Complexity & Risk
- **Effort: S (1-3 days)**
  - 既存の `ImageLoader` と `GameCardWidget` の修正で要件の大部分を満たせるため。
- **Risk: Low**
  - PySide6/Qt の標準的なパターン（QImage in background, QPixmap in UI）に従うため。

## 5. Recommendations for Design Phase
- **画像デコードの完全非同期化**: `QImage` を使用してバックグラウンドでデコードとスケーリングを完遂させ、UIスレッドでは `QPixmap.fromImage` の最小限の処理のみを行う。
- **リクエスト追跡**: Widgetが再利用（仮想化による更新）された際に、古いロード処理を無視するための ID 管理を導入する。
- **Research Needed**: `QImage` から `QPixmap` への変換自体のコストが極小であることを確認する（通常は問題ない）。
