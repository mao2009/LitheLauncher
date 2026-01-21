# Research & Design Decisions: Async Image Decoding Optimization

## Summary
- **Feature**: async-image-decoding-optimization
- **Discovery Scope**: Extension (Existing ImageLoader & GameCardWidget)
- **Key Findings**:
  - `QImage` はスレッドセーフであり、バックグラウンドスレッドでのデコードおよびスケーリングに適している。
  - `QPixmap` はGUIスレッド専用であり、スレッド間での受け渡しには適さない（`QImage` を渡すべき）。
  - スケーリング処理をバックグラウンドで行うことで、メインスレッドの負荷を大幅に軽減できる。

## Research Log

### PySide6/Qt における非同期画像処理のベストプラクティス
- **Context**: 現状の `ImageLoader` が `QPixmap` をバックグラウンドで作成しており、スケーリングがUIスレッドで行われている課題の調査。
- **Sources Consulted**: Qt Official Documentation (`QImage`, `QPixmap`), Stack Overflow, Community forums.
- **Findings**:
  - `QImage` はピクセルベースの操作（読み込み、スケーリング、変換）をバックグラウンドスレッドで安全に実行可能。
  - `QPixmap.fromImage()` はメインGUIスレッドで呼び出す必要がある。
  - `Qt.SmoothTransformation` を使用することで高品質なスケーリングが可能だが、計算コストがかかるため非同期化のメリットが大きい。
- **Implications**: `ImageLoader` の信号を `QPixmap` から `QImage` に変更し、スケーリングロジックを `ImageLoader` 内部に移動する必要がある。

### リクエストのキャンセルと再利用の制御
- **Context**: スクロール中にウィジェットが再利用された際、古い画像ロードリクエストが完了して新しい画像を上書きしてしまう問題の調査。
- **Findings**:
  - `GameCardWidget` 内にシーケンスIDまたはリクエストオブジェクトへの参照を保持し、シグナル受信時にIDが一致するかチェックするパターンが一般的。
  - `QThreadPool` のタスク自体をキャンセルするのは複雑（`QRunnable` ではフラグチェックが必要）なため、UI側での無視（Ignore）を優先する。

## Architecture Pattern Evaluation

| Option | Description | Strengths | Risks / Limitations | Notes |
|--------|-------------|-----------|---------------------|-------|
| Task Ignored Pattern | UIスレッドでリクエストIDを管理し、古いタスクの結果を無視する | 実装がシンプルで低リスク | バックグラウンドで不要な計算が継続される | 現状の `QThreadPool` 構成に最適 |
| Task Cancellation Pattern | `QRunnable` 内で中断フラグをチェックし、処理を早期終了させる | CPUリソースを節約できる | ロジックがやや複雑になる | 非常に重い処理の場合に検討 |

## Design Decisions

### Decision: QImage-based Background Processing
- **Context**: メインスレッドのブロック回避とスレッドセーフティの確保。
- **Selected Approach**: `ImageLoader` で `QImage` を作成・スケーリングし、完了後に `QImage` をシグナルで飛ばす。
- **Rationale**: `QImage` はスレッドセーフであり、UIスレッドの負荷を最小限（`QPixmap.fromImage` のみ）にできる。
- **Trade-offs**: `QImage` から `QPixmap` への変換コストがメインスレッドに残るが、スケーリングに比べれば無視できるレベル。

### Decision: Request ID Tracking in Widget
- **Context**: 仮想化によるウィジェット再利用時の競合防止。
- **Selected Approach**: `GameCardWidget` に `_current_image_request_id` を持たせ、各ロードリクエストにユニークIDを付与する。
- **Rationale**: 既存の `GameCardWidget` 構造を最小限の変更で安定させることができる。

## Risks & Mitigations
- 大量スレッドによるメモリ圧迫 — 専用の `QThreadPool` インスタンスを作成し、同時実行数を制限する（例: コア数程度）。
- デコードエラー時のプレースホルダー表示 — 失敗シグナルを確実にハンドリングし、エラー用のQSSプロパティをセットする。

## References
- [Qt Documentation: QImage Class](https://doc.qt.io/qtforpython-6/PySide6/QtGui/QImage.html)
- [Qt Documentation: QPixmap Class](https://doc.qt.io/qtforpython-6/PySide6/QtGui/QPixmap.html)
