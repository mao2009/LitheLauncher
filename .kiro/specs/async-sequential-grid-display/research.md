# Research & Design Decisions

## Summary
- **Feature**: async-sequential-grid-display
- **Discovery Scope**: Extension
- **Key Findings**:
  - `GameListWorker` は現在 `get_all_games()` を使用して一括取得しているが、SQLiteの `fetchone()` またはチャンク単位の取得に切り替えることで逐次通知が可能。
  - `GameListController` は内部で `list` 形式の `data` を保持しており、これに追記するメソッドを追加することで既存の仮想化ロジックを流用可能。
  - 初期表示速度を最大化するため、最初のチャンク（ビューポート分）は小さく設定し、以降はスループットを優先して大きくする可変チャンク方式が有効。

## Research Log

### Python/PySide6 での非同期逐次データ通知
- **Context**: 重いデータロードをUIスレッドを止めずに、かつ段階的に表示したい。
- **Findings**: 
  - `QRunnable` 内から `Signal(list)` を複数回発行することで、UIスレッドにチャンクを届けることができる。
  - 1件ずつの通知は1000件超えの場合、シグナル発行のオーバーヘッドが無視できなくなるため、50-100件程度のチャンクが推奨される。
- **Implications**: `GameListWorkerSignals` に新しいチャンク通知用シグナルを追加する。

## Architecture Pattern Evaluation

| Option | Description | Strengths | Risks / Limitations | Notes |
|--------|-------------|-----------|---------------------|-------|
| Chunked Signal | データを一定数ごとに通知 | スクロールバーが確定しやすく、実装が単純 | 読み込み完了まで正確な全体位置が分からない（COUNTを使わない場合） | 既存のWorkerパターンに最も近い |
| Generator Wrapper | Serviceがジェネレータを返し、Workerがそれを回す | Serviceの責任が明確 | 特になし | 推奨アプローチ |

## Design Decisions

### Decision: チャンク単位の非同期通知
- **Context**: ユーザーが起動時に「何も表示されない時間」を最小化する。
- **Selected Approach**: `GameListWorker` が `count` を最初に通知し、その後 `data_chunk_loaded` を発行する。
- **Rationale**: 最初に `count` を送ることで、`GameListController` が即座に正しいスクロール領域を確保でき、空白のスクロールを防げる。
- **Trade-offs**: データベースへのアクセスが「カウント」と「データ取得」の2回（またはそれ以上）になる。

## Risks & Mitigations
- 読み込み中にユーザーがスクロールした場合の競合 — 仮想化ロジックが `data` リストのインデックスを参照するため、未ロード箇所は `None` で埋めておき、ウィジェット作成時に `None` ならプレースホルダーを表示するようガードする。

## References
- [Qt Signals & Slots](https://doc.qt.io/qtforpython-6/overviews/signalsandslots.html)
