# Implementation Plan

- [x] 1. 繝・・繧ｿ繝吶・繧ｹ繧ｹ繧ｭ繝ｼ繝槭・譖ｴ譁ｰ (P)
  - `games` 繝・・繝悶Ν縺ｫ `command_line_settings` 繧ｫ繝ｩ繝 (TEXT, NOT NULL, DEFAULT '') 繧定ｿｽ蜉縺吶ｋ縲・  - _Requirements: 1.3_

- [x] 2. `GameRepository` 縺ｮ諡｡蠑ｵ (P)
  - `add_game` 繝｡繧ｽ繝・ラ縺・`command_line_settings` 繧貞女縺大叙繧翫√ョ繝ｼ繧ｿ繝吶・繧ｹ縺ｫ菫晏ｭ倥☆繧九ｈ縺・↓螟画峩縺吶ｋ縲・  - `update_game` 繝｡繧ｽ繝・ラ縺・`command_line_settings` 繧呈峩譁ｰ縺ｧ縺阪ｋ繧医≧縺ｫ螟画峩縺吶ｋ縲・  - `get_game` 繝｡繧ｽ繝・ラ縺・`command_line_settings` 繧貞叙蠕励〒縺阪ｋ繧医≧縺ｫ螟画峩縺吶ｋ縲・  - _Requirements: 1.2, 1.3, 1.4_

- [ ] 3. `LauncherService` 縺ｮ讖溯・諡｡蠑ｵ
  - [x] 3.1 `LauncherService.validate_command_line_settings` 繝｡繧ｽ繝・ラ縺ｮ螳溯｣・(P)
    - 繧ｳ繝槭Φ繝峨Λ繧､繝ｳ險ｭ螳壽枚蟄怜・縺ｮ蝓ｺ譛ｬ逧・↑繝舌Μ繝・・繧ｷ繝ｧ繝ｳ・・shlex.split` 縺ｮ萓句､匁黒謐峨↑縺ｩ・峨ｒ陦後≧縲・    - 蝠城｡後′縺ゅｌ縺ｰ隴ｦ蜻翫Γ繝・そ繝ｼ繧ｸ繧定ｿ斐☆縲・    - _Requirements: 4.1, 4.2_
  - [x] 3.2 `LauncherService.launch_game` 繝｡繧ｽ繝・ラ縺ｮ謾ｹ菫ｮ
    - `command_line_settings: str` 蠑墓焚繧貞女縺大叙繧九ｈ縺・↓螟画峩縺吶ｋ縲・    - `command_line_settings` 繧偵ヱ繝ｼ繧ｹ縺励～%command%` 繝励Ξ繝ｼ繧ｹ繝帙Ν繝繝ｼ繧偵ご繝ｼ繝縺ｮ螳溯｡後ヵ繧｡繧､繝ｫ繝代せ縺ｧ鄂ｮ謠帙☆繧九Ο繧ｸ繝・け繧貞ｮ溯｣・☆繧九・    - `%command%` 縺悟性縺ｾ繧後↑縺・ｴ蜷医・縲∝ｮ溯｡後ヵ繧｡繧､繝ｫ繝代せ繧偵ヱ繝ｼ繧ｹ縺輔ｌ縺溷ｼ墓焚繝ｪ繧ｹ繝医・蜈磯ｭ縺ｫ霑ｽ蜉縺吶ｋ縲・    - 蜃ｦ逅・ｸ医∩縺ｮ蠑墓焚繝ｪ繧ｹ繝医ｒ菴ｿ縺｣縺ｦ `subprocess.Popen` 繧貞他縺ｳ蜃ｺ縺吶・    - _Requirements: 2.1, 2.2, 2.3, 3.1, 3.2_

- [ ] 4. `GameService` 縺ｮ諡｡蠑ｵ (P)
  - `register_game` 繝｡繧ｽ繝・ラ縺・`command_line_settings` 繧貞女縺大叙繧翫～GameRepository` 繧剃ｻ九＠縺ｦ菫晏ｭ倥☆繧九ｈ縺・↓螟画峩縺吶ｋ縲・  - `update_game_details` 繝｡繧ｽ繝・ラ縺・`command_line_settings` 繧貞女縺大叙繧翫～GameRepository` 繧剃ｻ九＠縺ｦ譖ｴ譁ｰ縺吶ｋ繧医≧縺ｫ螟画峩縺吶ｋ縲・  - _Requirements: 1.2, 1.3, 1.4_

- [ ] 5. `GameDetailDialog` 縺ｮ UI 縺ｨ繝ｭ繧ｸ繝・け縺ｮ謾ｹ菫ｮ
  - [ ] 5.1 繧ｳ繝槭Φ繝峨Λ繧､繝ｳ險ｭ螳壼・蜉婉I縺ｮ霑ｽ蜉
    - `GameDetailDialog` 縺ｫ `QLineEdit` (繧ｳ繝槭Φ繝峨Λ繧､繝ｳ險ｭ螳夂畑) 縺ｨ蟇ｾ蠢懊☆繧九Λ繝吶Ν繧定ｿｽ蜉縺吶ｋ縲・    - _Requirements: 1.1_
  - [ ] 5.2 `GameDetailDialog` 縺ｮ繝・・繧ｿ繝舌う繝ｳ繝・ぅ繝ｳ繧ｰ縺ｨ菫晏ｭ倥Ο繧ｸ繝・け縺ｮ譖ｴ譁ｰ
    - `_update_ui_from_game_data` 繝｡繧ｽ繝・ラ縺後√ご繝ｼ繝縺ｮ譌｢蟄倥・ `command_line_settings` 繧・`QLineEdit` 縺ｫ陦ｨ遉ｺ縺吶ｋ繧医≧縺ｫ螟画峩縺吶ｋ縲・    - `_get_game_data_from_ui` 繝｡繧ｽ繝・ラ縺後～QLineEdit` 縺ｮ蛟､繧貞叙蠕励＠縺ｦ `GameService` 縺ｫ貂｡縺吶ｈ縺・↓螟画峩縺吶ｋ縲・    - _Requirements: 1.2, 1.3, 1.4_
  - [ ] 5.3 繧ｳ繝槭Φ繝峨Λ繧､繝ｳ險ｭ螳壹ヰ繝ｪ繝・・繧ｷ繝ｧ繝ｳ縺ｮ邨ｱ蜷・    - `QLineEdit` 縺ｮ `textChanged` 繧ｷ繧ｰ繝翫Ν繧・`LauncherService.validate_command_line_settings` 縺ｫ謗･邯壹☆繧九・    - 繝舌Μ繝・・繧ｷ繝ｧ繝ｳ邨先棡・郁ｭｦ蜻翫Γ繝・そ繝ｼ繧ｸ・峨ｒUI縺ｫ陦ｨ遉ｺ縺吶ｋ繝ｭ繧ｸ繝・け繧定ｿｽ蜉縺吶ｋ縲・    - _Requirements: 4.1, 4.2_

- [ ] 6. 繝・せ繝医・霑ｽ蜉
  - [ ] 6.1 `GameRepository` 縺ｮ繝ｦ繝九ャ繝医ユ繧ｹ繝医・霑ｽ蜉 (P)
    - `command_line_settings` 縺ｮCRUD謫堺ｽ懊↓髢｢縺吶ｋ繝・せ繝医こ繝ｼ繧ｹ繧剃ｽ懈・縺吶ｋ縲・    - _Requirements: 1.3_
  - [ ] 6.2 `LauncherService` 縺ｮ繝ｦ繝九ャ繝医ユ繧ｹ繝医・霑ｽ蜉 (P)
    - `launch_game` 繝｡繧ｽ繝・ラ縺ｫ縺翫￠繧・`%command%` 繝励Ξ繝ｼ繧ｹ繝帙Ν繝繝ｼ縺ｮ蜃ｦ逅・→蠑墓焚繝代・繧ｹ縺ｫ髢｢縺吶ｋ繝・せ繝医こ繝ｼ繧ｹ繧剃ｽ懈・縺吶ｋ縲・    - `validate_command_line_settings` 繝｡繧ｽ繝・ラ縺ｮ繝舌Μ繝・・繧ｷ繝ｧ繝ｳ繝ｭ繧ｸ繝・け縺ｫ髢｢縺吶ｋ繝・せ繝医こ繝ｼ繧ｹ繧剃ｽ懈・縺吶ｋ縲・    - _Requirements: 2.1, 2.2, 2.3, 3.1, 3.2, 4.1, 4.2_
  - [ ] 6.3 `GameService` 縺ｮ繝ｦ繝九ャ繝医ユ繧ｹ繝医・霑ｽ蜉 (P)
    - `command_line_settings` 繧貞性繧繧ｲ繝ｼ繝縺ｮ逋ｻ骭ｲ縺ｨ譖ｴ譁ｰ縺ｫ髢｢縺吶ｋ繝・せ繝医こ繝ｼ繧ｹ繧剃ｽ懈・縺吶ｋ縲・    - _Requirements: 1.2, 1.3, 1.4_
  - [ ] 6.4 `GameDetailDialog` 縺ｮ繝ｦ繝九ャ繝医ユ繧ｹ繝医・霑ｽ蜉 (P)
    - 繧ｳ繝槭Φ繝峨Λ繧､繝ｳ險ｭ螳壼・蜉帙ヵ繧｣繝ｼ繝ｫ繝峨・陦ｨ遉ｺ縲√ョ繝ｼ繧ｿ繝舌う繝ｳ繝・ぅ繝ｳ繧ｰ縲√ヰ繝ｪ繝・・繧ｷ繝ｧ繝ｳ隴ｦ蜻翫・陦ｨ遉ｺ縺ｫ髢｢縺吶ｋ繝・せ繝医こ繝ｼ繧ｹ繧剃ｽ懈・縺吶ｋ縲・    - _Requirements: 1.1, 1.2, 1.3, 1.4, 4.1, 4.2_
  - [ ] 6.5 邨ｱ蜷医ユ繧ｹ繝医・霑ｽ蜉
    - `GameDetailDialog` 縺九ｉ `GameService` 繧堤ｵ檎罰縺励◆繧ｳ繝槭Φ繝峨Λ繧､繝ｳ險ｭ螳壹・菫晏ｭ倥→隱ｭ縺ｿ霎ｼ縺ｿ繝輔Ο繝ｼ縺ｮ繝・せ繝医・    - `GameDetailDialog` 縺九ｉ `LauncherService` 繧堤ｵ檎罰縺励◆繧ｳ繝槭Φ繝峨Λ繧､繝ｳ險ｭ螳壻ｻ倥″繧ｲ繝ｼ繝縺ｮ襍ｷ蜍輔ヵ繝ｭ繝ｼ縺ｮ繝・せ繝医・    - 荳肴ｭ｣縺ｪ繧ｳ繝槭Φ繝峨Λ繧､繝ｳ險ｭ螳壹ｒ蜈･蜉帙＠縺溷ｴ蜷医・隴ｦ蜻願｡ｨ遉ｺ縺ｨ縲√◎縺ｮ迥ｶ諷九〒縺ｮ繧ｲ繝ｼ繝襍ｷ蜍戊ｩｦ陦後・繝・せ繝医・    - _Requirements: 1.1, 1.2, 1.3, 1.4, 2.1, 2.2, 2.3, 3.1, 3.2, 4.1, 4.2_
