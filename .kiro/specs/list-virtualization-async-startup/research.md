# Research & Design Decisions: List Virtualization and Async Startup

---
**Purpose**: 1000件規模のゲームリストにおける起動速度向上とメモリ使用量最適化のための技術調査と意思決定を記録します。
---

## Summary
- **Feature**: list-virtualization-async-startup
- **Discovery Scope**: Extension (既存の MainWindow と GameService の最適化)
- **Key Findings**:
  - 現在のボトルネックは 1000 個の `GameCardWidget` の同期的なインスタンス化である（約 0.75s）。
  - `QListView` への移行は標準的な仮想化を提供するが、既存の `GameCardWidget` (QWidget) の再利用が難しく、デリゲートでの再実装コストが高い。
  - ハイブリッドアプローチ（`QScrollArea` + ウィジェットプール）により、既存の UI 資産を活かしつつ仮想化が可能。

## Research Log

### Qt における大規模リストの表示手法
- **Context**: 1000件以上のアイテムをスムーズに表示するための最適なコンポーネントの選定。
- **Sources Consulted**: Qt Documentation (QListView, QAbstractItemView, QScrollArea), StackOverflow patterns for PySide6.
- **Findings**:
  - `QListView` + `QAbstractListModel`: メモリ効率は最高だが、各アイテムは「描画」されるものであり、複雑なインタラクション（個別のアニメーションや QSS 状態）を持つウィジェットをそのまま置くには向かない。
  - `setIndexWidget`: `QListView` でウィジェットを使えるが、大量に使用するとパフォーマンスが著しく低下するため、仮想化のメリットが相殺される。
  - `QScrollArea` + `FlowLayout`: 現行方式。全件追加すると起動が重い。
- **Implications**: 既存の `GameCardWidget` のリッチな表現を維持するため、標準の `QListView` ではなく、自前での「ウィジェットプーリング」を伴う仮想化を採用する。

### 非同期データ取得とスレッドセーフ
- **Context**: DB からの取得を非同期化する際のスレッド安全性。
- **Sources Consulted**: Python `sqlite3` documentation, PySide6 `QThread`/`QRunnable` guides.
- **Findings**:
  - `sqlite3` は接続を作成したスレッドでのみ使用可能（デフォルト）。`GameRepository` はメソッドごとに接続を作成するため、バックグラウンドスレッドからの呼び出しは安全。
  - UI の更新はメインスレッドで行う必要があるため、`QSignnal` を介したデータ受け渡しが必須。
- **Implications**: `QRunnable` を使用した `GameListWorker` を実装し、結果をシグナルで `MainWindow` に送る。

## Architecture Pattern Evaluation

| Option | Description | Strengths | Risks / Limitations | Notes |
|--------|-------------|-----------|---------------------|-------|
| **Lazy Loading** | スクロールに応じて少しずつウィジェットを追加 | 実装が非常に容易 | 最終的にメモリを消費し続ける。戻るスクロールは速いが、下へ行くほど重くなる | 0.7s 起動には有効 |
| **Full Virtualization** | 表示領域分のみウィジェットを作成し、使い回す | メモリ使用量が一定（20〜30枚分）。1万件でも高速 | スクロール位置からのインデックス計算が複雑。FlowLayout との相性が悪い | 要件 2.1 に合致 |
| **QListView 移行** | 標準のリストビューを使用 | 安定したパフォーマンス、標準機能 | スタイルとインタラクションの再実装が必要 | 既存のデザインを壊すリスク |

## Design Decisions

### Decision: ハイブリッド・ウィジェット・バーチャライザーの実装
- **Context**: 要件 2.1「表示されているウィジェットのみをレンダリングする」の達成。
- **Alternatives Considered**:
  1. 既存の `FlowLayout` を改造して非表示アイテムを無視する
  2. `QListView` に移行する
- **Selected Approach**: `QScrollArea` 内に「仮想Viewport」を構築し、固定サイズのグリッドとして扱う。スクロール位置に応じて、プーリングされた `GameCardWidget` の中身（データ）を差し替え、座標を再配置する。
- **Rationale**: `GameCardWidget` の QSS スタイルやコンテキストメニューなどの既存ロジックを 100% 再利用できる。
- **Trade-offs**: `FlowLayout` の「可変幅に応じた流動的な配置」を維持しつつ仮想化するため、ウィンドウリサイズ時の再計算ロジックが複雑になる。
- **Follow-up**: リサイズイベント時のグリッド再計算のパフォーマンスを検証する。

## Risks & Mitigations
- **スクロールのガタつき**: ウィジェットの中身を差し替える際（特に画像）に一瞬の遅延が発生する可能性がある。 → **Mitigation**: 画像のキャッシュを強化し、表示領域より少し広い範囲（バッファ）を事前に準備する。
- **実装の複雑化**: `FlowLayout` 自体は仮想化をサポートしていないため、管理クラスを分離する。 → **Mitigation**: `GameListController` という新しいレイヤーを導入し、`MainWindow` から表示管理を委譲する。

## References
- [Qt Virtual Scrolling](https://doc.qt.io/qt-6/model-view-programming.html)
- [PySide6 Threading Guide](https://doc.qt.io/qtforpython-6/tutorials/basictutorial/threading.html)
