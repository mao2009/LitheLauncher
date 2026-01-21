# Implementation Plan

- [x] 1. 繝・・繧ｿ繝吶・繧ｹ繧ｹ繧ｭ繝ｼ繝槭・譖ｴ譁ｰ
- [x] 1.1 Game繝・・繝悶Ν縺ｫ螳溯｡後ヵ繧｡繧､繝ｫ繝代せ逕ｨ縺ｮ繧ｫ繝ｩ繝繧定ｿｽ蜉
  - `database.py`縺ｮ`DATABASE_SCHEMA`縺ｫ`executable_path TEXT`繧定ｿｽ蜉縺吶ｋ縲・  - 繝・・繧ｿ繝吶・繧ｹ蛻晄悄蛹匁凾縺ｫ譌｢蟄魯B縺ｫ繧ｫ繝ｩ繝縺悟ｭ伜惠縺励↑縺・ｴ蜷医・霑ｽ蜉縺吶ｋ繝槭う繧ｰ繝ｬ繝ｼ繧ｷ繝ｧ繝ｳ繝ｭ繧ｸ繝・け繧呈､懆ｨ弱・螳溯｣・☆繧九・  - _Requirements: 1.2_

- [x] 2. 繝・・繧ｿ繧｢繧ｯ繧ｻ繧ｹ螻､ (GameRepository) 縺ｮ讖溯・諡｡蠑ｵ
- [x] 2.1 GameRepository縺ｮ繧ｲ繝ｼ繝霑ｽ蜉繝ｭ繧ｸ繝・け縺ｮ譖ｴ譁ｰ
  - `add_game`繝｡繧ｽ繝・ラ縺ｧ`game_data`霎樊嶌縺ｫ`executable_path`縺悟性縺ｾ繧後ｋ蝣ｴ蜷医√％繧後ｒ蜃ｦ逅・〒縺阪ｋ繧医≧縺ｫ縺吶ｋ縲・  - _Requirements: 1.2_

- [x] 2.2 GameRepository縺ｮ繧ｲ繝ｼ繝譖ｴ譁ｰ繝ｭ繧ｸ繝・け縺ｮ譖ｴ譁ｰ
  - `update_game`繝｡繧ｽ繝・ラ縺ｧ`game_data`霎樊嶌縺ｫ`executable_path`縺悟性縺ｾ繧後ｋ蝣ｴ蜷医√％繧後ｒ譖ｴ譁ｰ縺ｧ縺阪ｋ繧医≧縺ｫ縺吶ｋ縲・  - _Requirements: 1.2_

- [x] 2.3 GameRepository縺ｮ繧ｲ繝ｼ繝蜿門ｾ励Ο繧ｸ繝・け縺ｮ譖ｴ譁ｰ
  - `get_game`繝｡繧ｽ繝・ラ縺ｧ`executable_path`繧ｫ繝ｩ繝縺ｮ蛟､繧ょ叙蠕励＠縺ｦ霑斐☆繧医≧縺ｫ縺吶ｋ縲・  - _Requirements: 1.4, 2.2_

- [x] 3. 繧ｵ繝ｼ繝薙せ螻､ (GameService) 縺ｮ讖溯・諡｡蠑ｵ
- [x] 3.1 GameService縺ｮ繧ｲ繝ｼ繝逋ｻ骭ｲ繝ｭ繧ｸ繝・け縺ｮ譖ｴ譁ｰ
  - `register_game`繝｡繧ｽ繝・ラ縺ｮ蠑墓焚縺ｫ`executable_path`繧定ｿｽ蜉縺励～game_repository.add_game`縺ｫ貂｡縺吶・  - _Requirements: 1.2_

- [x] 3.2 GameService縺ｮ繧ｲ繝ｼ繝隧ｳ邏ｰ譖ｴ譁ｰ繝ｭ繧ｸ繝・け縺ｮ譖ｴ譁ｰ
  - `update_game_details`繝｡繧ｽ繝・ラ縺ｮ蠑墓焚縺ｫ`executable_path`繧定ｿｽ蜉縺励～game_repository.update_game`縺ｫ貂｡縺吶・  - _Requirements: 1.2_

- [x] 3.3 繧ｲ繝ｼ繝襍ｷ蜍輔Ο繧ｸ繝・け縺ｮ螳溯｣・  - `GameService`縺ｫ`launch_game(game_id: int)`繝｡繧ｽ繝・ラ繧呈眠隕丞ｮ溯｣・☆繧九・  - `game_id`縺九ｉ`executable_path`繧貞叙蠕励＠縲～subprocess`繝｢繧ｸ繝･繝ｼ繝ｫ繧剃ｽｿ逕ｨ縺励※繧ｲ繝ｼ繝繧貞ｮ溯｡後☆繧九・  - 繧ｲ繝ｼ繝繝励Ο繧ｻ繧ｹ縺檎ｵゆｺ・☆繧九∪縺ｧ蠕・ｩ溘☆繧九Ο繧ｸ繝・け繧貞ｮ溯｣・☆繧九・  - _Requirements: 2.2, 2.4_

- [x] 3.4 繧ｲ繝ｼ繝襍ｷ蜍墓凾縺ｮ繧ｨ繝ｩ繝ｼ繝上Φ繝峨Μ繝ｳ繧ｰ
  - `launch_game`繝｡繧ｽ繝・ラ蜀・〒繝励Ο繧ｻ繧ｹ襍ｷ蜍募､ｱ謨玲凾縺ｮ萓句､悶ｒ謐墓拷縺励・←蛻・↓蜃ｦ逅・☆繧九・  - _Requirements: 2.3_

- [x] 4. UI螻､ (GameDetailDialog) 縺ｮ讖溯・霑ｽ蜉縺ｨ譖ｴ譁ｰ
- [x] 4.1 螳溯｡後ヵ繧｡繧､繝ｫ繝代せ蜈･蜉婉I縺ｮ霑ｽ蜉
  - `GameDetailDialog._create_ui()`繝｡繧ｽ繝・ラ縺ｫ縲∝ｮ溯｡後ヵ繧｡繧､繝ｫ繝代せ蜈･蜉帷畑縺ｮ`QLineEdit`縺ｨ蜿ら・繝懊ち繝ｳ (`QPushButton`) 繧定ｿｽ蜉縺吶ｋ縲・  - UI繝ｬ繧､繧｢繧ｦ繝医↓隱ｿ蜥後☆繧九ｈ縺・↓驟咲ｽｮ縺吶ｋ縲・  - _Requirements: 1.1, 3.1_

- [x] 4.2 螳溯｡後ヵ繧｡繧､繝ｫ繝代せ蜿ら・讖溯・縺ｮ螳溯｣・  - 蜿ら・繝懊ち繝ｳ縺ｮ繧ｯ繝ｪ繝・け繧､繝吶Φ繝医↓蟇ｾ蠢懊☆繧義_browse_executable_path()`繝｡繧ｽ繝・ラ繧呈眠隕丞ｮ溯｣・☆繧九・  - `QFileDialog`繧剃ｽｿ逕ｨ縺励※繝輔ぃ繧､繝ｫ驕ｸ謚槭ム繧､繧｢繝ｭ繧ｰ繧定｡ｨ遉ｺ縺励・∈謚槭＆繧後◆繝代せ繧蛋QLineEdit`縺ｫ險ｭ螳壹☆繧九・  - _Requirements: 1.1_

- [x] 4.3 繧ｲ繝ｼ繝繝・・繧ｿ繝ｭ繝ｼ繝画凾縺ｮ繝代せ蛻晄悄陦ｨ遉ｺ
  - `GameDetailDialog._load_game_data()`繝｡繧ｽ繝・ラ縺ｧ縲√Ο繝ｼ繝峨＠縺溘ご繝ｼ繝繝・・繧ｿ縺九ｉ`executable_path`繧貞叙蠕励＠縲∵眠縺励￥霑ｽ蜉縺励◆`QLineEdit`縺ｫ險ｭ螳壹☆繧九・  - _Requirements: 1.4_

- [x] 4.4 繝輔か繝ｼ繝繝・・繧ｿ蜿門ｾ励Ο繧ｸ繝・け縺ｮ譖ｴ譁ｰ
  - `GameDetailDialog.get_game_data()`繝｡繧ｽ繝・ラ縺ｧ縲∵眠縺励￥霑ｽ蜉縺励◆`QLineEdit`縺九ｉ`executable_path`縺ｮ蛟､繧貞叙蠕励＠縲∬ｿ斐☆霎樊嶌縺ｫ蜷ｫ繧√ｋ縲・  - _Requirements: 1.2_

- [x] 4.5 繧ｲ繝ｼ繝襍ｷ蜍輔・繧ｿ繝ｳ縺ｮ霑ｽ蜉縺ｨ繧､繝吶Φ繝医ワ繝ｳ繝峨Μ繝ｳ繧ｰ
  - `GameDetailDialog._create_ui()`縺ｫ繧ｲ繝ｼ繝襍ｷ蜍輔・繧ｿ繝ｳ繧定ｿｽ蜉縺吶ｋ縲・  - 襍ｷ蜍輔・繧ｿ繝ｳ縺ｮ繧ｯ繝ｪ繝・け繧､繝吶Φ繝医↓蟇ｾ蠢懊☆繧九せ繝ｭ繝・ヨ (`_launch_game()`) 繧呈眠隕丞ｮ溯｣・＠縲～GameService.launch_game()`繧貞他縺ｳ蜃ｺ縺吶・  - _Requirements: 2.1, 2.2_

- [x] 4.6 螳溯｡後ヵ繧｡繧､繝ｫ繝代せ蜈･蜉帙・繝舌Μ繝・・繧ｷ繝ｧ繝ｳ縺ｨ繧ｨ繝ｩ繝ｼ陦ｨ遉ｺ
  - 菫晏ｭ倥・繧ｿ繝ｳ繧ｯ繝ｪ繝・け譎ゅ～GameService`蜻ｼ縺ｳ蜃ｺ縺怜燕縺ｫ`QLineEdit`縺ｮ蜈･蜉帛､縺梧怏蜉ｹ縺ｪ螳溯｡後ヵ繧｡繧､繝ｫ繝代せ縺ｧ縺ゅｋ縺区､懆ｨｼ縺吶ｋ縲・  - 辟｡蜉ｹ縺ｪ蝣ｴ蜷医・縲√Θ繝ｼ繧ｶ繝ｼ縺ｫ繧ｨ繝ｩ繝ｼ繝｡繝・そ繝ｼ繧ｸ繧定｡ｨ遉ｺ縺吶ｋ縲・  - _Requirements: 1.3_

- [x] 4.7 繧ｲ繝ｼ繝襍ｷ蜍募､ｱ謨玲凾縺ｮ繧ｨ繝ｩ繝ｼ騾夂衍
  - `GameService.launch_game()`縺九ｉ縺ｮ襍ｷ蜍募､ｱ謨礼ｵ先棡繧貞女縺大叙繧翫√Θ繝ｼ繧ｶ繝ｼ縺ｫ繧ｨ繝ｩ繝ｼ繝｡繝・そ繝ｼ繧ｸ繧定｡ｨ遉ｺ縺吶ｋ縲・  - _Requirements: 2.3_

- [x] 4.8 螟画峩譎ゅ・菫晏ｭ倡憾諷九ヵ繧｣繝ｼ繝峨ヰ繝・け縺ｮ閠・・
  - `QLineEdit`縺ｮ`textChanged`繧ｷ繧ｰ繝翫Ν縺ｪ縺ｩ繧貞茜逕ｨ縺励～executable_path`蜈･蜉帙↓螟画峩縺後≠縺｣縺溷ｴ蜷医↓縲∽ｿ晏ｭ倥・繧ｿ繝ｳ縺ｮ豢ｻ諤ｧ蛹悶↑縺ｩ隕冶ｦ夂噪縺ｪ繝輔ぅ繝ｼ繝峨ヰ繝・け繧呈､懆ｨ弱☆繧九・  - _Requirements: 3.2_

- [x] 5. 繝・せ繝医・螳溯｣・→譖ｴ譁ｰ
- [x] 5.1 GameRepository縺ｮexecutable_path髢｢騾｣繝・せ繝・  - `test_game_repository.py`縺ｫ`executable_path`縺ｮ霑ｽ蜉縲∝叙蠕励∵峩譁ｰ繧呈､懆ｨｼ縺吶ｋ蜊倅ｽ薙ユ繧ｹ繝医ｒ霑ｽ蜉縺吶ｋ縲・  - _Requirements: 1.2, 1.4, 2.2_

- [x] 5.2 GameService縺ｮlaunch_game繝｡繧ｽ繝・ラ縺ｮ繝・せ繝・  - `test_game_service.py`縺ｫ`launch_game`繝｡繧ｽ繝・ラ縺ｮ蜊倅ｽ薙ユ繧ｹ繝医ｒ霑ｽ蜉縺吶ｋ縲・  - 譛牙柑縺ｪ繝代せ縺ｧ縺ｮ襍ｷ蜍墓・蜉溘∫┌蜉ｹ縺ｪ繝代せ縺ｧ縺ｮ襍ｷ蜍募､ｱ謨励√・繝ｭ繧ｻ繧ｹ邨ゆｺ・ｾ・ｩ溘ｒ繝｢繝・け・・subprocess`繝｢繝・け縺ｪ縺ｩ・峨ｒ菴ｿ逕ｨ縺励※讀懆ｨｼ縺吶ｋ縲・  - _Requirements: 2.2, 2.3, 2.4_

- [x] 5.3 邨仙粋繝・せ繝医・霑ｽ蜉
  - `test_game_detail_dialog.py`縺ｾ縺溘・譁ｰ隕上ユ繧ｹ繝医ヵ繧｡繧､繝ｫ縺ｫ縲～GameDetailDialog`縲～GameService`縲～GameRepository`繧堤ｵｱ蜷医＠縺溽ｵ仙粋繝・せ繝医ｒ霑ｽ蜉縺吶ｋ縲・  - UI謫堺ｽ懊°繧峨ョ繝ｼ繧ｿ豌ｸ邯壼喧縲√ご繝ｼ繝襍ｷ蜍輔∪縺ｧ縺ｮ荳騾｣縺ｮ繝輔Ο繝ｼ繧呈､懆ｨｼ縺吶ｋ縲・  - _Requirements: All_
