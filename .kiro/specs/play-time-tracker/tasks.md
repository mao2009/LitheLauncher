# Implementation Plan: play-time-tracker

- [x] 1. 繝励Ξ繧､譎る俣繝・・繧ｿ繝｢繝・Ν縺ｮ螳夂ｾｩ縺ｨ繝槭う繧ｰ繝ｬ繝ｼ繧ｷ繝ｧ繝ｳ (P)
  - `src/database.py` 縺ｫ `PlaySession` 繝・・繝悶Ν縺ｮ繧ｹ繧ｭ繝ｼ繝槭ｒ螳夂ｾｩ縺吶ｋ縲・  - `Game` 繝・・繝悶Ν縺ｨ縺ｮ `game_id` 繧堤畑縺・◆螟夜Κ繧ｭ繝ｼ蛻ｶ邏・→ `ON DELETE CASCADE` 繧定ｨｭ螳壹☆繧九・  - 譌｢蟄倥・繝槭う繧ｰ繝ｬ繝ｼ繧ｷ繝ｧ繝ｳ繧ｷ繧ｹ繝・Β・・MigrationEngine`・峨↓ `PlaySession` 繝・・繝悶Ν霑ｽ蜉縺ｮ繝槭う繧ｰ繝ｬ繝ｼ繧ｷ繝ｧ繝ｳ繧ｹ繧ｯ繝ｪ繝励ヨ繧堤函謌舌・霑ｽ蜉縺吶ｋ縲・  - _Requirements: 2.1, 2.4_

- [x] 2. `GameRepository` 縺ｮ繝励Ξ繧､譎る俣繝・・繧ｿ繧｢繧ｯ繧ｻ繧ｹ螳溯｣・(P)
  - `GameRepository` 縺ｫ `add_play_session` 繝｡繧ｽ繝・ラ繧貞ｮ溯｣・＠縲√・繝ｬ繧､繧ｻ繝・す繝ｧ繝ｳ繝・・繧ｿ繧奪B縺ｫ菫晏ｭ倥☆繧九・  - `GameRepository` 縺ｫ `get_total_play_time_for_game` 繝｡繧ｽ繝・ラ繧貞ｮ溯｣・＠縲∵欠螳壹ご繝ｼ繝縺ｮ蜷郁ｨ医・繝ｬ繧､譎る俣繧貞叙蠕励☆繧九・  - `GameRepository` 縺ｫ `get_play_session_history_for_game` 繝｡繧ｽ繝・ラ繧貞ｮ溯｣・＠縲∵欠螳壹ご繝ｼ繝縺ｮ繝励Ξ繧､繧ｻ繝・す繝ｧ繝ｳ螻･豁ｴ繧貞叙蠕励☆繧九・  - `GameRepository` 縺ｫ `delete_play_time_data_for_game` 繝｡繧ｽ繝・ラ繧貞ｮ溯｣・＠縲∵欠螳壹ご繝ｼ繝縺ｮ繝励Ξ繧､譎る俣繝・・繧ｿ繧貞炎髯､縺吶ｋ縲・  - _Requirements: 2.1, 2.2, 2.3, 2.4_

- [x] 3. `GameService` 縺ｮ繝励Ξ繧､譎る俣邂｡逅・Ο繧ｸ繝・け螳溯｣・(P)
  - `GameService` 縺ｫ `finalize_play_session` 繝｡繧ｽ繝・ラ繧貞ｮ溯｣・＠縲～GameRepository` 繧剃ｻ九＠縺ｦ繝励Ξ繧､繧ｻ繝・す繝ｧ繝ｳ繝・・繧ｿ繧呈ｰｸ邯壼喧縺吶ｋ縲・  - `GameService` 縺ｮ `delete_game_data` 繝｡繧ｽ繝・ラ縺ｫ `GameRepository.delete_play_time_data_for_game` 縺ｮ蜻ｼ縺ｳ蜃ｺ縺励ｒ霑ｽ蜉縺吶ｋ縲・  - `GameService` 縺ｫ `get_total_play_time` 繝｡繧ｽ繝・ラ繧貞ｮ溯｣・＠縲～GameRepository` 縺九ｉ蜷郁ｨ医・繝ｬ繧､譎る俣繧貞叙蠕励＠縲∝ｿ・ｦ√↓蠢懊§縺ｦ繝輔か繝ｼ繝槭ャ繝医☆繧九・  - `GameService` 縺ｫ `get_play_session_history` 繝｡繧ｽ繝・ラ繧貞ｮ溯｣・＠縲～GameRepository` 縺九ｉ繝励Ξ繧､繧ｻ繝・す繝ｧ繝ｳ螻･豁ｴ繧貞叙蠕励☆繧九・  - _Requirements: 2.1, 2.2, 2.3, 2.4, 4.2_

- [x] 4. `LauncherService` 縺ｮ繝励Ξ繧､譎る俣險域ｸｬ繝ｭ繧ｸ繝・け螳溯｣・  - `LauncherService.launch_game` 繝｡繧ｽ繝・ラ蜀・〒縲√ご繝ｼ繝繝励Ο繧ｻ繧ｹ襍ｷ蜍墓凾縺ｫ繝励Ξ繧､譎る俣險域ｸｬ繧ｿ繧､繝槭・・医う繝ｳ繝｡繝｢繝ｪ・峨ｒ髢句ｧ九☆繧九Ο繧ｸ繝・け繧定ｿｽ蜉縺吶ｋ縲・  - `subprocess.Popen` 縺ｧ襍ｷ蜍輔＠縺溘ご繝ｼ繝繝励Ο繧ｻ繧ｹ縺ｮ迥ｶ諷九ｒ逶｣隕悶＠縲√・繝ｭ繧ｻ繧ｹ縺檎ｵゆｺ・＠縺滄圀縺ｫ繧ｿ繧､繝槭・繧貞●豁｢繝ｻ遒ｺ螳壹＠縲～GameService.finalize_play_session` 繧貞他縺ｳ蜃ｺ縺吶Ο繧ｸ繝・け繧定ｿｽ蜉縺吶ｋ縲・  - 繝ｩ繝ｳ繝√Ε繝ｼ邨ゆｺ・う繝吶Φ繝茨ｼ井ｾ・ `QApplication.instance().aboutToQuit` 繧ｷ繧ｰ繝翫Ν・峨ｒ繝輔ャ繧ｯ縺励√い繧ｯ繝・ぅ繝悶↑繝励Ξ繧､繧ｻ繝・す繝ｧ繝ｳ縺後≠繧後・蠑ｷ蛻ｶ逧・↓邨ゆｺ・・遒ｺ螳壹☆繧九Ο繧ｸ繝・け繧・`_on_launcher_shutdown` 繝｡繧ｽ繝・ラ縺ｨ縺励※螳溯｣・☆繧九・  - _Requirements: 1.1, 1.2, 1.3, 1.4, 4.1_

- [x] 5. UI (GameDetailDialog) 縺ｸ縺ｮ繝励Ξ繧､譎る俣陦ｨ遉ｺ螳溯｣・  - `src/game_detail_dialog.py` 繧剃ｿｮ豁｣縺励√ご繝ｼ繝隧ｳ邏ｰ逕ｻ髱｢縺ｫ蜷郁ｨ医・繝ｬ繧､譎る俣繧定｡ｨ遉ｺ縺吶ｋ縺溘ａ縺ｮ QLabel 縺ｪ縺ｩ縺ｮ UI 隕∫ｴ繧定ｿｽ蜉縺吶ｋ縲・  - `_load_game_data` 繝｡繧ｽ繝・ラ蜀・〒 `GameService.get_total_play_time` 繧貞他縺ｳ蜃ｺ縺励∝叙蠕励＠縺滓凾髢薙ｒ莠ｺ髢薙′隱ｭ縺ｿ繧・☆縺・ｽ｢蠑擾ｼ井ｾ・ "XX譎る俣 YY蛻・・峨↓螟画鋤縺励※ UI 縺ｫ陦ｨ遉ｺ縺吶ｋ縲・  - _Requirements: 3.1, 3.2, 4.3_

- [x] 6. 繝励Ξ繧､譎る俣險域ｸｬ繝ｻ邂｡逅・・蜊倅ｽ薙ユ繧ｹ繝亥ｼｷ蛹・  - [x] `tests/test_launcher_service.py` 縺ｫ `launch_game` 繝｡繧ｽ繝・ラ縺ｮ繝励Ξ繧､譎る俣險域ｸｬ繝ｭ繧ｸ繝・け縺ｮ蜊倅ｽ薙ユ繧ｹ繝医ｒ霑ｽ蜉縺吶ｋ縲・  - [x] `tests/test_game_service.py` 縺ｫ `finalize_play_session`, `get_total_play_time`, `get_play_session_history` 繝｡繧ｽ繝・ラ縺ｮ蜊倅ｽ薙ユ繧ｹ繝医ｒ霑ｽ蜉縺吶ｋ縲・  - [x] `tests/test_game_repository.py` 縺ｫ `add_play_session`, `get_total_play_time_for_game`, `get_play_session_history_for_game`, `delete_play_time_data_for_game` 繝｡繧ｽ繝・ラ縺ｮ蜊倅ｽ薙ユ繧ｹ繝医ｒ霑ｽ蜉縺吶ｋ縲・  - _Requirements: 1.1, 1.2, 1.3, 1.4, 2.1, 2.2, 2.3, 2.4, 4.1, 4.2, 4.3_

- [x] 7. 邨ｱ蜷医ユ繧ｹ繝医→豁｣蟶ｸ邉ｻ繝ｻ逡ｰ蟶ｸ邉ｻ縺ｮ讀懆ｨｼ
  - 螳滄圀縺ｮ繧ｲ繝ｼ繝襍ｷ蜍輔ヵ繝ｭ繝ｼ蜈ｨ菴薙ｒ騾壹＠縺ｦ縲√・繝ｬ繧､譎る俣縺梧ｭ｣縺励￥險域ｸｬ繝ｻ菫晏ｭ倥・陦ｨ遉ｺ縺輔ｌ繧九％縺ｨ繧堤｢ｺ隱阪☆繧狗ｵｱ蜷医ユ繧ｹ繝医ｒ `tests/test_integration_launch_workflow.py` 縺ｾ縺溘・譁ｰ隕上・邨ｱ蜷医ユ繧ｹ繝医ヵ繧｡繧､繝ｫ縺ｫ霑ｽ蜉縺吶ｋ縲・  - 繝ｩ繝ｳ繝√Ε繝ｼ蠑ｷ蛻ｶ邨ゆｺ・凾・医Δ繝・け・峨・繝励Ξ繧､譎る俣菫晏ｭ伜・逅・・邨ｱ蜷医ユ繧ｹ繝医ｒ霑ｽ蜉縺吶ｋ縲・  - 繝励Ξ繧､譎る俣險域ｸｬ縺ｾ縺溘・菫晏ｭ倅ｸｭ縺ｮ繧ｨ繝ｩ繝ｼ縺檎匱逕溘＠縺溷ｴ蜷医↓縲√Ο繧ｰ縺瑚ｨ倬鹸縺輔ｌ UI 縺碁←蛻・↓謖ｯ繧玖・縺・％縺ｨ繧堤｢ｺ隱阪☆繧狗ｵｱ蜷医ユ繧ｹ繝医ｒ霑ｽ蜉縺吶ｋ縲・  - _Requirements: 1.1, 1.2, 1.3, 1.4, 2.1, 2.2, 2.3, 2.4, 3.1, 3.2, 4.1, 4.2, 4.3_
