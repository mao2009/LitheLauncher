# Research & Design Decisions Template

## Summary
- **Feature**: `remove-obsolete-cover-art-path-field`
- **Discovery Scope**: Extension
- **Key Findings**:
  - `cover_art_path`フィールド�E`database.py`のスキーマに存在し、`game_repository.py`と`game_detail_dialog.py`で参�EされてぁE��、E  - `game_card_widget.py`では`image_path`への移行が既に示唁E��れており、`cover_art_path`は古ぁE��ィールドであることが確認された、E  - 主な変更箁E��はチE�Eタベ�Eススキーマ�E変更と、E��連するコードから�E`cover_art_path`の参�E削除となる、E
## Research Log

### `cover_art_path`フィールド�E現状調査
- **Context**: 「カバ�Eアートパス(旧)フィールド�E削除」機�Eの要件に基づき、既存コード�Eースにおける`cover_art_path`フィールド�E使用状況を調査した、E- **Sources Consulted**:
    - `grep -r "cover_art_path" src/` コマンド�E結果
    - `src/database.py`
    - `src/game_repository.py`
    - `src/game_detail_dialog.py`
    - `src/game_card_widget.py`
- **Findings**:
    - `src/database.py`にチE�Eブル定義の一部として`cover_art_path TEXT,`が存在する、E    - `src/game_repository.py`では、ゲームチE�Eタの`get`めE��ィールドリストで`cover_art_path`が参照されてぁE��、E    - `src/game_detail_dialog.py`では、`QLineEdit`とゲームチE�EタのバインチE��ングに`cover_art_path`が使用されてぁE��、E    - `src/game_card_widget.py`のコメントでは、`cover_art_path`から`image_path`への変更が既に示唁E��れてぁE��。これ�E、`cover_art_path`が「旧」フィールドであることを裏付ける、E- **Implications**:
    - チE�Eタベ�Eススキーマから`cover_art_path`カラムを削除する忁E��がある、E    - `game_repository.py`と`game_detail_dialog.py`における`cover_art_path`への参�Eを`image_path`に置き換えるか、完�Eに削除する忁E��がある、E    - `game_card_widget.py`は既に`image_path`を使用してぁE��ため、大きな変更は不要だが、コメント�EクリーンアチE�Eが忁E��かもしれなぁE�
