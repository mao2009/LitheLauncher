# Implementation Plan

- [x] 1. 繝・・繧ｿ繝吶・繧ｹ繧ｹ繧ｭ繝ｼ繝槭°繧峨・`cover_art_path`繧ｫ繝ｩ繝縺ｮ蜑企勁 (P)
  - `src/database.py`蜀・・`Game`繝・・繝悶Ν螳夂ｾｩ縺九ｉ`cover_art_path TEXT,`陦後ｒ蜑企勁縺吶ｋ縲・  - 繝・・繧ｿ繝吶・繧ｹ繝槭う繧ｰ繝ｬ繝ｼ繧ｷ繝ｧ繝ｳ繧ｹ繧ｯ繝ｪ繝励ヨ・域焔蜍包ｼ峨ｒ逕滓・縺励～cover_art_path`繧ｫ繝ｩ繝縺悟炎髯､縺輔ｌ繧九％縺ｨ繧堤｢ｺ隱阪☆繧九・  - _Requirements: 1.1_

- [x] 2. `game_repository.py`縺九ｉ縺ｮ`cover_art_path`蜿ら・縺ｮ蜑企勁 (P)
  - `get_all_games`縺翫ｈ縺ｳ`get_game`繝｡繧ｽ繝・ラ縺ｮSQL繧ｯ繧ｨ繝ｪ縺九ｉ`cover_art_path`繧ｫ繝ｩ繝縺ｮ驕ｸ謚槭ｒ蜑企勁縺吶ｋ縲・  - `add_game`縺翫ｈ縺ｳ`update_game`繝｡繧ｽ繝・ラ蜀・〒縲～game_data`霎樊嶌縺九ｉ`cover_art_path`繧ｭ繝ｼ繧貞・逅・＠縺ｪ縺・ｈ縺・↓繝ｭ繧ｸ繝・け繧剃ｿｮ豁｣縺吶ｋ縲・  - `game`繝・・繧ｿ縺ｮ蛻晄悄蛹悶ｄ繝・ヵ繧ｩ繝ｫ繝亥､險ｭ螳壹↓縺翫＞縺ｦ`cover_art_path`縺ｮ險蜿翫ｒ蜑企勁縺吶ｋ縲・  - _Requirements: 1.1, 1.2, 2.1, 2.2_

- [x] 3. `game_detail_dialog.py`縺九ｉ縺ｮ`cover_art_path`髢｢騾｣UI隕∫ｴ縺ｨ繝ｭ繧ｸ繝・け縺ｮ蜑企勁 (P)
  - `cover_art_path`縺ｫ髢｢騾｣縺吶ｋ`QLineEdit`繧ｪ繝悶ず繧ｧ繧ｯ繝・(`self.cover_art_path_line_edit`) 縺ｨ縺昴・繧､繝ｳ繧ｹ繧ｿ繝ｳ繧ｹ蛹悶√Ξ繧､繧｢繧ｦ繝医∈縺ｮ霑ｽ蜉縲√す繧ｰ繝翫Ν/繧ｹ繝ｭ繝・ヨ謗･邯壹ｒ蜑企勁縺吶ｋ縲・  - `_game_data`縺ｸ縺ｮ`cover_art_path`縺ｮ繝舌う繝ｳ繝・ぅ繝ｳ繧ｰ・・setText`, `text`縺ｮ蜿門ｾ暦ｼ峨ｒ蜑企勁縺吶ｋ縲・  - _Requirements: 2.1, 2.2, 3.1_

- [x] 4. `game_card_widget.py`縺ｮ繧ｯ繝ｪ繝ｼ繝ｳ繧｢繝・・ (P)
  - `cover_art_path`縺ｸ縺ｮ險蜿翫ｒ蜷ｫ繧繧ｳ繝｡繝ｳ繝医ｒ蜑企勁縺吶ｋ縲・  - 繧ｳ繝ｼ繝峨′`image_path`繧呈ｭ｣縺励￥菴ｿ逕ｨ縺励※縺・ｋ縺薙→繧貞・遒ｺ隱阪☆繧九・  - _Requirements: 3.1_

- [x] 5. 繝・せ繝医こ繝ｼ繧ｹ縺ｮ霑ｽ蜉縺ｨ譖ｴ譁ｰ
  - [x] 5.1 (P) `test_database.py`縺ｮ譖ｴ譁ｰ
    - `Game`繝・・繝悶Ν縺ｫ`cover_art_path`繧ｫ繝ｩ繝縺悟ｭ伜惠縺励↑縺・％縺ｨ繧呈､懆ｨｼ縺吶ｋ繝・せ繝医ｒ霑ｽ蜉縺吶ｋ縲・    - _Requirements: 1.1_
  - [x] 5.2 (P) `test_game_repository.py`縺ｮ譖ｴ譁ｰ
    - `game_repository`縺形cover_art_path`繧貞・逅・＠縺ｪ縺・％縺ｨ繧呈､懆ｨｼ縺吶ｋ繝・せ繝医ｒ霑ｽ蜉縺吶ｋ縲・    - `image_path`繝輔ぅ繝ｼ繝ｫ繝峨〒繧ｲ繝ｼ繝繝・・繧ｿ縺ｮCRUD謫堺ｽ懊′豁｣縺励￥蜍穂ｽ懊☆繧九％縺ｨ繧呈､懆ｨｼ縺吶ｋ繝・せ繝医ｒ霑ｽ蜉縺吶ｋ縲・    - _Requirements: 1.1, 1.2, 2.1, 2.2_
  - [x] 5.3 (P) `test_game_detail_dialog.py`縺ｮ譖ｴ譁ｰ
    - `GameDetailDialog`縺ｫ`cover_art_path`髢｢騾｣縺ｮUI隕∫ｴ縺悟ｭ伜惠縺励↑縺・％縺ｨ繧呈､懆ｨｼ縺吶ｋ繝・せ繝医ｒ霑ｽ蜉縺吶ｋ縲・    - `image_path`繝輔ぅ繝ｼ繝ｫ繝峨〒UI縺梧ｭ｣縺励￥蜍穂ｽ懊☆繧九％縺ｨ繧呈､懆ｨｼ縺吶ｋ繝・せ繝医ｒ霑ｽ蜉縺吶ｋ縲・    - _Requirements: 2.1, 2.2, 3.1_
  - [x] 5.4 (P) 邨ｱ蜷医ユ繧ｹ繝医・譖ｴ譁ｰ
    - 譌｢蟄倥・邨ｱ蜷医ユ繧ｹ繝茨ｼ井ｾ・ `test_integration_image_registration.py`・峨′`image_path`繝輔ぅ繝ｼ繝ｫ繝峨ｒ菴ｿ逕ｨ縺励※繧ｫ繝舌・繧｢繝ｼ繝医・逋ｻ骭ｲ縺ｨ陦ｨ遉ｺ縺ｫ豁｣縺励￥蜍穂ｽ懊☆繧九％縺ｨ繧堤｢ｺ隱阪☆繧九・    - 繧｢繝励Μ繧ｱ繝ｼ繧ｷ繝ｧ繝ｳ蜈ｨ菴薙〒繧ｲ繝ｼ繝縺ｮ霑ｽ蜉縲∫ｷｨ髮・∝炎髯､縲∬ｵｷ蜍輔′`cover_art_path`髢｢騾｣縺ｮ繧ｨ繝ｩ繝ｼ縺ｪ縺励〒豁｣縺励￥蜍穂ｽ懊☆繧九％縺ｨ繧呈､懆ｨｼ縺吶ｋ縲・    - _Requirements: 3.1, 3.2_
