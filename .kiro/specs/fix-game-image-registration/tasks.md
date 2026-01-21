# Implementation Plan

- [x] 1. `ImageManager` 縺ｮ讖溯・諡｡蠑ｵ縺ｨ荳譎ゅヵ繧｡繧､繝ｫ縺ｮ邂｡逅・- [x] 1.1 (P) `ImageManager` 繧ｯ繝ｩ繧ｹ縺ｮ繝輔ぃ繧､繝ｫ謫堺ｽ憺未騾｣繧､繝ｳ繝昴・繝医・霑ｽ蜉縺ｨ荳譎ゅョ繧｣繝ｬ繧ｯ繝医Μ縺ｮ蛻晄悄蛹・  - `pathlib`, `tempfile`, `shutil` 縺ｪ縺ｩ縺ｮ蠢・ｦ√↑繝｢繧ｸ繝･繝ｼ繝ｫ繧偵う繝ｳ繝昴・繝医☆繧九・  - 荳譎ら判蜒上ｒ菫晏ｭ倥☆繧九◆繧√・繧｢繝励Μ繧ｱ繝ｼ繧ｷ繝ｧ繝ｳ蝗ｺ譛峨・荳譎ゅョ繧｣繝ｬ繧ｯ繝医Μ繧貞・譛溷喧縺吶ｋ繝ｭ繧ｸ繝・け繧定ｿｽ蜉縲・  - _Requirements: 1.3, 1.4, 2.1, 2.3_
- [x] 1.2 (P) `ImageManager.save_temp_image` 繝｡繧ｽ繝・ラ縺ｮ螳溯｣・  - 繧ｽ繝ｼ繧ｹ逕ｻ蜒上ヱ繧ｹ繧貞女縺大叙繧翫√い繝励Μ繧ｱ繝ｼ繧ｷ繝ｧ繝ｳ縺ｮ荳譎ゅョ繧｣繝ｬ繧ｯ繝医Μ縺ｫ繧ｳ繝斐・縺励※縲√◎縺ｮ荳譎ゅヱ繧ｹ繧定ｿ斐☆縲・  - _Requirements: 1.3_
- [x] 1.3 (P) `ImageManager.move_image_from_temp_to_game_data` 繝｡繧ｽ繝・ラ縺ｮ螳溯｣・  - 荳譎ゅヱ繧ｹ縺ｮ逕ｻ蜒上ｒ譛邨ら噪縺ｪ `data/[game_id]/images/` 縺ｫ遘ｻ蜍輔＆縺帙∵怙邨ゅヱ繧ｹ繧定ｿ斐☆縲らｧｻ蜍募・縺ｮ荳譎ら判蜒上・蜑企勁縲・  - _Requirements: 2.1_
- [x] 1.4 (P) `ImageManager.delete_game_image` 繝｡繧ｽ繝・ラ縺ｮ螳溯｣・  - 迚ｹ螳壹・繧ｲ繝ｼ繝縺ｫ髢｢騾｣縺吶ｋ逕ｻ蜒上ヵ繧｡繧､繝ｫ繧呈欠螳壹＆繧後◆繝代せ縺九ｉ蜑企勁縺吶ｋ縲・  - _Requirements: 3.2_
- [x] 1.5 (P) `ImageManager.cleanup_temp_image` 繝｡繧ｽ繝・ラ縺ｮ螳溯｣・  - 謖・ｮ壹＆繧後◆荳譎ら判蜒上ｒ蜑企勁縺吶ｋ縲・  - _Requirements: 1.4_
- [x] 1.6 (P) `ImageManager.validate_image` 繝｡繧ｽ繝・ラ縺ｮ螳溯｣・  - Pillow 繝ｩ繧､繝悶Λ繝ｪ繧剃ｽｿ逕ｨ縺励※縲∫判蜒上ヵ繧｡繧､繝ｫ縺梧怏蜉ｹ縺ｧ縺ゅｋ縺具ｼ育ｴ謳阪＠縺ｦ縺・↑縺・°縲∵里遏･縺ｮ蠖｢蠑上°縺ｪ縺ｩ・峨ｒ繝√ぉ繝・け縺吶ｋ縲・  - _Requirements: 2.4_

- [ ] 2. `GameDetailDialog` 縺ｮ UI 縺ｨ繝・・繧ｿ菫晄戟繝ｭ繧ｸ繝・け縺ｮ謾ｹ菫ｮ
- [x] 2.1 (P) `GameDetailDialog` 縺ｮ繧ｳ繝ｳ繧ｹ繝医Λ繧ｯ繧ｿ螟画峩縺ｨ繧､繝ｳ繧ｹ繧ｿ繝ｳ繧ｹ螟画焚縺ｮ霑ｽ蜉
  - `GameService` 縺ｨ `ImageManager` 縺ｮ繧､繝ｳ繧ｹ繧ｿ繝ｳ繧ｹ繧貞女縺大叙繧九ｈ縺・↓繧ｳ繝ｳ繧ｹ繝医Λ繧ｯ繧ｿ繧呈峩譁ｰ縲・  - `_temp_image_path: Path | None`, `_game_data: Dict[str, Any]` (縺ｾ縺溘・鬘樔ｼｼ縺ｮ讒矩) 繧偵う繝ｳ繧ｹ繧ｿ繝ｳ繧ｹ螟画焚縺ｨ縺励※霑ｽ蜉縲・  - _Requirements: 1.1, 1.2, 1.3, 3.1_
- [x] 2.2 (P) 蜈ｨ蜈･蜉帙ヵ繧｣繝ｼ繝ｫ繝峨・繝・・繧ｿ菫晄戟繝ｭ繧ｸ繝・け縺ｮ謾ｹ菫ｮ縺ｨ蛻晄悄蛹・  - 繝繧､繧｢繝ｭ繧ｰ蜀・・蜷・・蜉帙え繧｣繧ｸ繧ｧ繝・ヨ・・LineEdit縺ｪ縺ｩ・峨・蛟､繧・`_game_data` 繧､繝ｳ繧ｹ繧ｿ繝ｳ繧ｹ螟画焚縺ｫ繝舌う繝ｳ繝峨＠縲ゞI譖ｴ譁ｰ髢｢謨ｰ繧貞ｮ溯｣・・  - 譌｢蟄倥ご繝ｼ繝邱ｨ髮・凾縺ｯ譌｢蟄倥ョ繝ｼ繧ｿ繧偵Ο繝ｼ繝峨＠縲∵眠隕冗匳骭ｲ譎ゅ・遨ｺ縺ｮ繝・・繧ｿ繧貞・譛溷喧縲・  - _Requirements: 1.1_
- [x] 2.3 (P) 逕ｻ蜒城∈謚槭・繧ｿ繝ｳ縺ｮ繧｢繧ｯ繧ｷ繝ｧ繝ｳ縺ｨUI陦ｨ遉ｺ繝ｭ繧ｸ繝・け縺ｮ謾ｹ菫ｮ
  - 逕ｻ蜒城∈謚槭・繧ｿ繝ｳ繧ｯ繝ｪ繝・け譎ゅ↓繝輔ぃ繧､繝ｫ繝繧､繧｢繝ｭ繧ｰ繧帝幕縺上・  - 驕ｸ謚槭＆繧後◆逕ｻ蜒上ヱ繧ｹ繧・`ImageManager.save_temp_image` 縺ｫ貂｡縺励∬ｿ斐＆繧後◆荳譎ゅヱ繧ｹ繧・`_temp_image_path` 縺ｫ菫晏ｭ倥＠縲ゞI縺ｮ逕ｻ蜒剰｡ｨ遉ｺ繧ｨ繝ｪ繧｢縺ｫ繝ｭ繝ｼ繝峨＠縺ｦ陦ｨ遉ｺ縲・  - _Requirements: 1.2, 1.3, 3.1_
- [x] 2.4 (P) 逋ｻ骭ｲ/譖ｴ譁ｰ繝懊ち繝ｳ繧ｯ繝ｪ繝・け譎ゅ・繝・・繧ｿ蜿朱寔縺ｨ `GameService` 蜻ｼ縺ｳ蜃ｺ縺・  - 繝繧､繧｢繝ｭ繧ｰ縺ｮ `accepted` 繧ｷ繧ｰ繝翫Ν逋ｺ逕滓凾縺ｫ縲～_game_data` 縺ｨ `_temp_image_path` 繧・`GameService.register_game` 縺ｾ縺溘・ `GameService.update_game_details` 縺ｫ貂｡縺吶・  - _Requirements: 2.1, 2.2, 3.1, 3.2_
- [x] 2.5 (P) 繧ｭ繝｣繝ｳ繧ｻ繝ｫ譎ゅ・繝・・繧ｿ遐ｴ譽・→UI繝ｪ繧ｻ繝・ヨ繝ｭ繧ｸ繝・け縺ｮ謾ｹ菫ｮ
  - 繝繧､繧｢繝ｭ繧ｰ縺ｮ `rejected` 繧ｷ繧ｰ繝翫Ν逋ｺ逕滓凾縺ｫ縲～ImageManager.cleanup_temp_image` 繧貞他縺ｳ蜃ｺ縺励～_temp_image_path` 縺後≠繧後・蜑企勁縲・  - 繝繧､繧｢繝ｭ繧ｰ縺ｮ蜈ｨ縺ｦ縺ｮ蜈･蜉帙ヵ繧｣繝ｼ繝ｫ繝峨ｒ繝ｪ繧ｻ繝・ヨ縺励～_game_data` 縺ｨ `_temp_image_path` 繧偵け繝ｪ繧｢縺吶ｋ縲・  - _Requirements: 1.4_

- [ ] 3. `GameService` 縺ｮ逕ｻ蜒丞・逅・が繝ｼ繧ｱ繧ｹ繝医Ξ繝ｼ繧ｷ繝ｧ繝ｳ繝ｭ繧ｸ繝・け縺ｮ霑ｽ蜉
- [x] 3.1 (P) `GameService` 繧ｳ繝ｳ繧ｹ繝医Λ繧ｯ繧ｿ縺ｮ螟画峩
  - `ImageManager` 縺ｮ繧､繝ｳ繧ｹ繧ｿ繝ｳ繧ｹ繧貞女縺大叙繧九ｈ縺・↓繧ｳ繝ｳ繧ｹ繝医Λ繧ｯ繧ｿ繧呈峩譁ｰ縲・  - _Requirements: 2.1, 3.1_
- [x] 3.2 (P) `GameService.register_game` 繝｡繧ｽ繝・ラ縺ｮ謾ｹ菫ｮ
  - `temp_image_path: Path | None` 蠑墓焚繧貞女縺大叙繧九ｈ縺・↓螟画峩縲・  - 繧ｲ繝ｼ繝逋ｻ骭ｲ蠕後～ImageManager.move_image_from_temp_to_game_data` 繧貞他縺ｳ蜃ｺ縺励※逕ｻ蜒上ｒ譛邨ゅヱ繧ｹ縺ｸ遘ｻ蜍輔＠縲～GameRepository` 繧剃ｻ九＠縺ｦ `image_path` 繧呈峩譁ｰ縲・  - _Requirements: 2.1, 2.2_
- [x] 3.3 (P) `GameService.update_game_details` 繝｡繧ｽ繝・ラ縺ｮ謾ｹ菫ｮ
  - `temp_image_path: Path | None` 蠑墓焚繧貞女縺大叙繧九ｈ縺・↓螟画峩縲・  - 譁ｰ縺励＞逕ｻ蜒上ヱ繧ｹ縺後≠繧後・ `ImageManager.move_image_from_temp_to_game_data` 縺ｧ逕ｻ蜒上ｒ遘ｻ蜍輔・  - 蜿､縺・判蜒上ヱ繧ｹ縺ｨ譁ｰ縺励＞逕ｻ蜒上ヱ繧ｹ縺檎焚縺ｪ繧句ｴ蜷医～ImageManager.delete_game_image` 縺ｧ蜿､縺・判蜒上ｒ蜑企勁縲・  - `GameRepository` 繧剃ｻ九＠縺ｦ `image_path` 繧呈峩譁ｰ縲・  - _Requirements: 3.1, 3.2_
- [x] 3.4 (P) `GameService` 縺ｮ逕ｻ蜒乗､懆ｨｼ繝ｭ繧ｸ繝・け縺ｮ霑ｽ蜉
  - `register_game` 縺翫ｈ縺ｳ `update_game_details` 縺ｮ荳ｭ縺ｧ縲～ImageManager.validate_image` 繧貞他縺ｳ蜃ｺ縺励∽ｸ肴ｭ｣縺ｪ逕ｻ蜒上・蝣ｴ蜷医・繧ｨ繝ｩ繝ｼ繧堤匱逕溘＆縺帙ｋ縲・  - _Requirements: 2.4_

- [x] 4. 繧ｨ繝ｩ繝ｼ繝上Φ繝峨Μ繝ｳ繧ｰ縺ｮ霑ｽ蜉
- [x] 4.1 (P) `ImageValidationError` 繧ｫ繧ｹ繧ｿ繝萓句､悶・螳夂ｾｩ
  - `src/exceptions.py` 縺ｫ `ImageValidationError` (GameLauncherError 繧堤ｶ呎価) 繧貞ｮ夂ｾｩ縺吶ｋ縲・  - _Requirements: 2.4_
- [x] 4.2 (P) 髢｢騾｣縺吶ｋ繝｡繧ｽ繝・ラ縺ｧ縺ｮ萓句､門・逅・・霑ｽ蜉
  - `ImageManager.validate_image` 縺悟､ｱ謨励＠縺溷ｴ蜷医～ImageValidationError` 繧堤匱逕溘＆縺帙ｋ縲・  - `GameService` 縺ｧ `ImageValidationError` 繧呈黒謐峨＠縲・←蛻・↓蜀咲匱逕溘＆縺帙ｋ縲・  - `GameDetailDialog` 縺ｧ `ImageValidationError` 繧呈黒謐峨＠縲√Θ繝ｼ繧ｶ繝ｼ縺ｫ蛻・°繧翫ｄ縺吶＞繝｡繝・そ繝ｼ繧ｸ繧定｡ｨ遉ｺ縺吶ｋ縲・  - _Requirements: 2.4_

- [x] 5. 繝・せ繝医・霑ｽ蜉
- [x] 5.1 (P) `ImageManager` 縺ｮ繝ｦ繝九ャ繝医ユ繧ｹ繝医・霑ｽ蜉
  - `save_temp_image`, `move_image_from_temp_to_game_data`, `delete_game_image`, `cleanup_temp_image`, `validate_image` 縺ｮ蜷・Γ繧ｽ繝・ラ縺ｫ蟇ｾ縺吶ｋ繝・せ繝医こ繝ｼ繧ｹ繧剃ｽ懈・縲・  - _Requirements: 1.3, 1.4, 2.1, 2.3, 2.4, 3.1, 3.2_
- [x] 5.2 (P) `GameDetailDialog` 縺ｮ繝ｦ繝九ャ繝医ユ繧ｹ繝医・霑ｽ蜉
  - 蜈･蜉帑ｿ晄戟縲∫判蜒城∈謚槭√く繝｣繝ｳ繧ｻ繝ｫ譎ゅ・謖吝虚縺ｫ髢｢縺吶ｋ繝・せ繝医こ繝ｼ繧ｹ繧剃ｽ懈・縲ゅΔ繝・け繧剃ｽｿ逕ｨ縺励※ `GameService` 縺ｨ `ImageManager` 縺ｮ逶ｸ莠剃ｽ懃畑繧呈､懆ｨｼ縲・  - _Requirements: 1.1, 1.2, 1.3, 1.4, 3.1_
- [x] 5.3 (P) `GameService` 縺ｮ繝ｦ繝九ャ繝医ユ繧ｹ繝医・霑ｽ蜉
  - `register_game`, `update_game_details` 縺ｮ逕ｻ蜒丞・逅・∵､懆ｨｼ縲∝商縺・判蜒丞炎髯､縺ｫ髢｢縺吶ｋ繝・せ繝医こ繝ｼ繧ｹ繧剃ｽ懈・縲ゅΔ繝・け繧剃ｽｿ逕ｨ縺励※ `GameRepository` 縺ｨ `ImageManager` 縺ｮ逶ｸ莠剃ｽ懃畑繧呈､懆ｨｼ縲・  - _Requirements: 2.1, 2.2, 2.4, 3.1, 3.2_
- [x] 5.4 (P) 逕ｻ蜒冗匳骭ｲ/譖ｴ譁ｰ繝輔Ο繝ｼ縺ｮ邨ｱ蜷医ユ繧ｹ繝医・霑ｽ蜉
  - `GameDetailDialog` 縺九ｉ `GameService` 繧堤ｵ檎罰縺励※ `ImageManager` 縺ｾ縺ｧ縺ｮ繧ｨ繝ｳ繝峨ヤ繝ｼ繧ｨ繝ｳ繝峨・繝輔Ο繝ｼ繧呈､懆ｨｼ縺吶ｋ繝・せ繝医・  - 逋ｻ骭ｲ繧ｭ繝｣繝ｳ繧ｻ繝ｫ譎ゅ↓荳譎ら判蜒上′豁｣縺励￥蜑企勁縺輔ｌ繧九％縺ｨ縺ｮ繝・せ繝医・  - _Requirements: 1.1, 1.2, 1.3, 1.4, 2.1, 2.2, 2.3, 2.4, 3.1, 3.2_
- [x] 5.5 (P) 繧ｨ繝ｩ繝ｼ繝上Φ繝峨Μ繝ｳ繧ｰ縺ｫ髢｢縺吶ｋ繝・せ繝医・霑ｽ蜉
  - `ImageValidationError` 縺碁←蛻・↓逋ｺ逕溘＠縲∝・逅・＆繧後ｋ縺薙→繧呈､懆ｨｼ縺吶ｋ繝・せ繝医・  - _Requirements: 2.4_

- [x] 6. 萓晏ｭ倬未菫ゅ・霑ｽ蜉
- [x] 6.1 (P) `requirements.txt` 縺ｫ Pillow (PIL) 繧定ｿｽ蜉
  - `Pillow` 繝代ャ繧ｱ繝ｼ繧ｸ縺ｮ萓晏ｭ倬未菫ゅｒ霑ｽ蜉縲・  - _Requirements: 2.4_
