# Implementation Plan

- [x] 1. 繝・・繧ｿ繝吶・繧ｹ繧ｹ繧ｭ繝ｼ繝槭・譖ｴ譁ｰ縺ｨGameRepository縺ｮ蟇ｾ蠢・(P)
  - [x] 1.1 (P) Game繝・・繝悶Ν縺ｸ縺ｮpre_command, post_command繧ｫ繝ｩ繝霑ｽ蜉
    - `src/database.py` 蜀・・`Game`繝・・繝悶Ν縺ｫ`pre_command` (TEXT, DEFAULT '') 縺ｨ `post_command` (TEXT, DEFAULT '') 繧ｫ繝ｩ繝繧定ｿｽ蜉縺吶ｋ繝槭う繧ｰ繝ｬ繝ｼ繧ｷ繝ｧ繝ｳ繧ｹ繧ｯ繝ｪ繝励ヨ繧剃ｽ懈・縺ｾ縺溘・譌｢蟄倥・繧ｹ繧ｭ繝ｼ繝槫ｮ夂ｾｩ繧呈峩譁ｰ縲・    - _Requirements: 1.2_
  - [x] 1.2 (P) GameRepository縺ｮCRUD謫堺ｽ懊↓縺翫￠繧九さ繝槭Φ繝峨ヵ繧｣繝ｼ繝ｫ繝峨・蟇ｾ蠢・    - `src/game_repository.py` 縺ｮ `add_game`, `update_game`, `get_game` 繝｡繧ｽ繝・ラ縺ｧ `pre_command` 縺翫ｈ縺ｳ `post_command` 繝輔ぅ繝ｼ繝ｫ繝峨ｒ驕ｩ蛻・↓蜃ｦ逅・☆繧九ｈ縺・↓菫ｮ豁｣縲・    - _Requirements: 1.2_

- [x] 2. GameDetailDialog縺ｮUI譖ｴ譁ｰ (P)
  - [x] 2.1 (P) GameDetailDialog縺ｸ縺ｮ繧ｳ繝槭Φ繝牙・蜉帙ヵ繧｣繝ｼ繝ｫ繝峨・霑ｽ蜉
    - `src/game_detail_dialog.py` 縺ｫ螳溯｡悟燕繧ｳ繝槭Φ繝・(`pre_command_line_edit`) 縺翫ｈ縺ｳ螳溯｡悟ｾ後さ繝槭Φ繝・(`post_command_line_edit`) 逕ｨ縺ｮ `QLineEdit` 繧ｦ繧｣繧ｸ繧ｧ繝・ヨ繧定ｿｽ蜉縲・    - 縺薙ｌ繧峨・繧ｦ繧｣繧ｸ繧ｧ繝・ヨ繧帝←蛻・↑繝ｬ繧､繧｢繧ｦ繝医↓霑ｽ蜉縺励ゞI縺ｫ陦ｨ遉ｺ縺輔ｌ繧九ｈ縺・↓縺吶ｋ縲・    - _Requirements: 1.1_
  - [x] 2.2 (P) UI縺ｸ縺ｮ繧ｳ繝槭Φ繝芽ｨｭ螳壹・隱ｭ縺ｿ霎ｼ縺ｿ縺ｨ菫晏ｭ・    - `src/game_detail_dialog.py` 縺ｮ `_update_ui_from_game_data` 繝｡繧ｽ繝・ラ繧剃ｿｮ豁｣縺励∝叙蠕励＠縺溘ご繝ｼ繝繝・・繧ｿ縺九ｉ `pre_command` 縺ｨ `post_command` 繧貞ｯｾ蠢懊☆繧・`QLineEdit` 縺ｫ險ｭ螳壹☆繧九・    - `src/game_detail_dialog.py` 縺ｮ `get_game_data` 繝｡繧ｽ繝・ラ繧剃ｿｮ豁｣縺励～QLineEdit` 縺九ｉ `pre_command` 縺ｨ `post_command` 縺ｮ蛟､繧貞叙蠕励＠縺ｦ繧ｲ繝ｼ繝繝・・繧ｿ縺ｫ蜷ｫ繧√ｋ縲・    - _Requirements: 1.3, 1.2_

- [x] 3. GameService縺ｫ縺翫￠繧九さ繝槭Φ繝芽ｨｭ螳壹・蜃ｦ逅・(P)
  - [x] 3.1 (P) GameService縺ｮ繧ｲ繝ｼ繝逋ｻ骭ｲ繝ｻ譖ｴ譁ｰ蜃ｦ逅・・諡｡蠑ｵ
    - `src/game_service.py` 縺ｮ `register_game` 縺翫ｈ縺ｳ `update_game_details` 繝｡繧ｽ繝・ラ繧剃ｿｮ豁｣縺励～game_data` 縺ｫ蜷ｫ縺ｾ繧後ｋ `pre_command` 縺ｨ `post_command` 繧・`GameRepository` 邨檎罰縺ｧ菫晏ｭ倥〒縺阪ｋ繧医≧縺ｫ縺吶ｋ縲・    - _Requirements: 1.2_

- [ ] 4. LauncherService縺ｮ繧ｳ繝槭Φ繝牙ｮ溯｡後Ο繧ｸ繝・け螳溯｣・→邨ｱ蜷・  - [x] 4.1 (P) execute_command繝倥Ν繝代・繝｡繧ｽ繝・ラ縺ｮ螳溯｣・    - `src/launcher_service.py` 縺ｫ `execute_command(self, command: str) -> tuple[int, str, str]` 繝｡繧ｽ繝・ラ繧貞ｮ溯｣・・    - 縺薙・繝｡繧ｽ繝・ラ縺ｯ `subprocess` 繝｢繧ｸ繝･繝ｼ繝ｫ繧剃ｽｿ逕ｨ縺励※謖・ｮ壹＆繧後◆繧ｳ繝槭Φ繝峨ｒ螳溯｡後＠縲∫ｵゆｺ・さ繝ｼ繝峨∵ｨ呎ｺ門・蜉帙∵ｨ呎ｺ悶お繝ｩ繝ｼ繧偵ち繝励Ν縺ｧ霑斐☆縲・    - 繧ｳ繝槭Φ繝峨・ `shlex.split` 繧剃ｽｿ逕ｨ縺励※螳牙・縺ｫ繝代・繧ｹ縺吶ｋ縲・    - _Requirements: 2.1, 3.1, 4.1_
  - [x] 4.2 launch_game繝｡繧ｽ繝・ラ縺ｸ縺ｮ螳溯｡悟燕繧ｳ繝槭Φ繝牙ｮ溯｡後Ο繧ｸ繝・け縺ｮ邨ｱ蜷・    - `src/launcher_service.py` 縺ｮ `launch_game` 繝｡繧ｽ繝・ラ蜀・〒縲√ご繝ｼ繝螳溯｡悟燕縺ｫ `pre_command` 縺悟ｭ伜惠縺吶ｋ蝣ｴ蜷医・ `execute_command` 繧貞他縺ｳ蜃ｺ縺吶・    - `execute_command` 縺ｮ邨先棡縺後お繝ｩ繝ｼ (髱槭ぞ繝ｭ縺ｮ邨ゆｺ・さ繝ｼ繝・ 縺ｮ蝣ｴ蜷医√お繝ｩ繝ｼ繧偵Ο繧ｰ縺ｫ險倬鹸縺励√Θ繝ｼ繧ｶ繝ｼ縺ｫ騾夂衍 (`MainWindow` 邨檎罰) 縺励√ご繝ｼ繝縺ｮ襍ｷ蜍輔ｒ荳ｭ豁｢縺吶ｋ縲・    - _Requirements: 2.1, 2.2, 2.3, 4.2_
  - [x] 4.3 launch_game繝｡繧ｽ繝・ラ縺ｸ縺ｮ螳溯｡悟ｾ後さ繝槭Φ繝牙ｮ溯｡後Ο繧ｸ繝・け縺ｮ邨ｱ蜷・    - `src/launcher_service.py` 縺ｮ `launch_game` 繝｡繧ｽ繝・ラ蜀・〒縲√ご繝ｼ繝繝励Ο繧ｻ繧ｹ邨ゆｺ・ｾ後↓ `post_command` 縺悟ｭ伜惠縺吶ｋ蝣ｴ蜷医・ `execute_command` 繧貞他縺ｳ蜃ｺ縺吶・    - `execute_command` 縺ｮ邨先棡縺後お繝ｩ繝ｼ縺ｮ蝣ｴ蜷医√お繝ｩ繝ｼ繧偵Ο繧ｰ縺ｫ險倬鹸縺励√Θ繝ｼ繧ｶ繝ｼ縺ｫ騾夂衍縺吶ｋ縺後√ご繝ｼ繝縺ｮ襍ｷ蜍輔↓縺ｯ蠖ｱ髻ｿ繧剃ｸ弱∴縺ｪ縺・・    - _Requirements: 3.1, 3.2, 3.3, 4.3_

- [ ] 5. 繝・せ繝医・螳溯｣・(P)
  - [ ] 5.1 (P) GameRepository縺ｮ繝・せ繝医こ繝ｼ繧ｹ霑ｽ蜉
    - `tests/test_game_repository.py` 縺ｫ `pre_command` 縺翫ｈ縺ｳ `post_command` 繧貞性繧繧ｲ繝ｼ繝繝・・繧ｿ縺ｮ菫晏ｭ倥∝叙蠕励∵峩譁ｰ縺ｫ髢｢縺吶ｋ繝・せ繝医こ繝ｼ繧ｹ繧定ｿｽ蜉縲・    - _Requirements: 1.2_
  - [ ] 5.2 (P) GameDetailDialog縺ｮ繝・せ繝医こ繝ｼ繧ｹ霑ｽ蜉
    - `tests/test_game_detail_dialog.py` 縺ｫ `pre_command_line_edit` 縺翫ｈ縺ｳ `post_command_line_edit` 縺ｮ陦ｨ遉ｺ縲√ョ繝ｼ繧ｿ繝舌う繝ｳ繝・ぅ繝ｳ繧ｰ縺ｫ髢｢縺吶ｋ繝・せ繝医こ繝ｼ繧ｹ繧定ｿｽ蜉縲・    - _Requirements: 1.1, 1.3_
  - [ ] 5.3 (P) GameService縺ｮ繝・せ繝医こ繝ｼ繧ｹ霑ｽ蜉
    - `tests/test_game_service.py` 縺ｫ `register_game` 縺翫ｈ縺ｳ `update_game_details` 繝｡繧ｽ繝・ラ縺・`pre_command` 縺ｨ `post_command` 繧帝←蛻・↓蜃ｦ逅・☆繧九％縺ｨ繧呈､懆ｨｼ縺吶ｋ繝・せ繝医こ繝ｼ繧ｹ繧定ｿｽ蜉縲・    - _Requirements: 1.2_
  - [ ] 5.4 (P) LauncherService縺ｮ繝ｦ繝九ャ繝医ユ繧ｹ繝医こ繝ｼ繧ｹ霑ｽ蜉
    - `tests/test_launcher_service.py` 縺ｫ `execute_command` 繝｡繧ｽ繝・ラ縺ｮ豁｣蟶ｸ邉ｻ縺ｨ逡ｰ蟶ｸ邉ｻ (謌仙粥縲∝､ｱ謨励∝ｭ伜惠縺励↑縺・さ繝槭Φ繝・ 縺ｮ繝・せ繝医こ繝ｼ繧ｹ繧定ｿｽ蜉縲・    - `launch_game` 繝｡繧ｽ繝・ラ縺ｫ縺翫￠繧句ｮ溯｡悟燕繧ｳ繝槭Φ繝峨・繝医Μ繧ｬ繝ｼ縲√ご繝ｼ繝襍ｷ蜍穂ｸｭ豁｢縲∝ｮ溯｡悟ｾ後さ繝槭Φ繝峨・繝医Μ繧ｬ繝ｼ縲√お繝ｩ繝ｼ騾夂衍縺ｫ髢｢縺吶ｋ繝・せ繝医こ繝ｼ繧ｹ繧定ｿｽ蜉縲・    - _Requirements: 2.1, 2.2, 2.3, 3.1, 3.2, 3.3, 4.1, 4.2, 4.3_
  - [ ] 5.5 (P) 邨仙粋繝・せ繝医こ繝ｼ繧ｹ霑ｽ蜉
    - `tests/test_integration_pre_post_commands.py` (譁ｰ隕丈ｽ懈・) 縺ｫ縲～GameDetailDialog` 縺九ｉ `GameService` 繧堤ｵ檎罰縺励◆繧ｳ繝槭Φ繝芽ｨｭ螳壹・菫晏ｭ倥→隱ｭ縺ｿ霎ｼ縺ｿ繝輔Ο繝ｼ縺ｮ繝・せ繝医ｒ霑ｽ蜉縲・    - `GameDetailDialog` 縺九ｉ `LauncherService` 繧堤ｵ檎罰縺励◆繧ｳ繝槭Φ繝芽ｨｭ螳壻ｻ倥″繧ｲ繝ｼ繝縺ｮ襍ｷ蜍輔→邨ゆｺ・ｾ後・繧ｳ繝槭Φ繝牙ｮ溯｡後ヵ繝ｭ繝ｼ縺ｮ繝・せ繝医ｒ霑ｽ蜉縲・    - 繧ｳ繝槭Φ繝牙ｮ溯｡御ｸｭ縺ｮ繧ｨ繝ｩ繝ｼ逋ｺ逕滓凾縺ｮUI騾夂衍縺ｨ縲√ご繝ｼ繝襍ｷ蜍・邨ゆｺ・・邯咏ｶ壽ｧ・亥ｮ溯｡悟燕/蠕後さ繝槭Φ繝峨〒謖吝虚縺檎焚縺ｪ繧九％縺ｨ繧呈､懆ｨｼ・峨・繝・せ繝医ｒ霑ｽ蜉縲・    - _Requirements: 1.1, 1.2, 1.3, 2.1, 2.2, 2.3, 3.1, 3.2, 3.3, 4.1, 4.2, 4.3_
