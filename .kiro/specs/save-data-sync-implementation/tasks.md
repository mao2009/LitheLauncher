# Implementation Plan

- [x] 1. 繝・・繧ｿ繝吶・繧ｹ繧ｹ繧ｭ繝ｼ繝槭・譖ｴ譁ｰ (P)
  - `Game` 繝・・繝悶Ν縺ｫ `sync_enabled` (INTEGER, NOT NULL, DEFAULT 0), `save_folder` (TEXT, NULLABLE, DEFAULT ''), `remote_sync_path` (TEXT, NULLABLE, DEFAULT '') 繧ｫ繝ｩ繝繧定ｿｽ蜉縺吶ｋ縲・  - _Requirements: 1.3_

- [x] 2. `GameRepository` 縺ｮ諡｡蠑ｵ (P)
  - `add_game` 繝｡繧ｽ繝・ラ縺・`sync_enabled`, `save_folder`, `remote_sync_path` 繧貞女縺大叙繧翫√ョ繝ｼ繧ｿ繝吶・繧ｹ縺ｫ菫晏ｭ倥☆繧九ｈ縺・↓螟画峩縺吶ｋ縲・  - `update_game` 繝｡繧ｽ繝・ラ縺・`sync_enabled`, `save_folder`, `remote_sync_path` 繧呈峩譁ｰ縺ｧ縺阪ｋ繧医≧縺ｫ螟画峩縺吶ｋ縲・  - `get_game` 繝｡繧ｽ繝・ラ縺・`sync_enabled`, `save_folder`, `remote_sync_path` 繧貞叙蠕励〒縺阪ｋ繧医≧縺ｫ螟画峩縺吶ｋ縲・  - _Requirements: 1.3, 1.4_

- [x] 3. `RemoteStorageService` 縺ｮ螳溯｣・(P)
  - `download_save_data(self, game_id: int, remote_path: str, local_path: Path)` 繝｡繧ｽ繝・ラ繧貞ｮ溯｣・☆繧九・    - 繝ｪ繝｢繝ｼ繝医せ繝医Ξ繝ｼ繧ｸ縺九ｉ繝ｭ繝ｼ繧ｫ繝ｫ縺ｸ繝輔ぃ繧､繝ｫ繧偵さ繝斐・縺吶ｋ繝ｭ繧ｸ繝・け縲・    - `shutil` 縺ｨ `pathlib` 繧剃ｽｿ逕ｨ縺励※繝輔ぃ繧､繝ｫ繧ｷ繧ｹ繝・Β謫堺ｽ懊ｒ陦後≧縲・    - 繝繧ｦ繝ｳ繝ｭ繝ｼ繝我ｸｭ縺ｮ繧ｨ繝ｩ繝ｼ繧呈黒謐峨＠ `SaveDataSyncError` 繧堤匱逕溘＆縺帙ｋ縲・  - `upload_save_data(self, game_id: int, local_path: Path, remote_path: str)` 繝｡繧ｽ繝・ラ繧貞ｮ溯｣・☆繧九・    - 繝ｭ繝ｼ繧ｫ繝ｫ縺九ｉ繝ｪ繝｢繝ｼ繝医せ繝医Ξ繝ｼ繧ｸ縺ｸ繝輔ぃ繧､繝ｫ繧偵さ繝斐・縺吶ｋ繝ｭ繧ｸ繝・け縲・    - `shutil` 縺ｨ `pathlib` 繧剃ｽｿ逕ｨ縺励※繝輔ぃ繧､繝ｫ繧ｷ繧ｹ繝・Β謫堺ｽ懊ｒ陦後≧縲・    - 繧｢繝・・繝ｭ繝ｼ繝我ｸｭ縺ｮ繧ｨ繝ｩ繝ｼ繧呈黒謐峨＠ `SaveDataSyncError` 繧堤匱逕溘＆縺帙ｋ縲・  - _Requirements: 2.1, 2.2, 3.1, 3.2, 4.1_

- [x] 4. `GameService` 縺ｮ諡｡蠑ｵ (P)
  - `register_game` 繝｡繧ｽ繝・ラ縺・`sync_enabled`, `save_folder`, `remote_sync_path` 繧貞女縺大叙繧翫～GameRepository` 繧剃ｻ九＠縺ｦ菫晏ｭ倥☆繧九ｈ縺・↓螟画峩縺吶ｋ縲・  - `update_game_details` 繝｡繧ｽ繝・ラ縺・`sync_enabled`, `save_folder`, `remote_sync_path` 繧貞女縺大叙繧翫～GameRepository` 繧剃ｻ九＠縺ｦ譖ｴ譁ｰ縺吶ｋ繧医≧縺ｫ螟画峩縺吶ｋ縲・  - _Requirements: 1.3_

- [x] 5. `LauncherService` 縺ｮ讖溯・諡｡蠑ｵ (P)
  - `__init__` 繝｡繧ｽ繝・ラ縺ｧ `RemoteStorageService` 縺ｮ繧､繝ｳ繧ｹ繧ｿ繝ｳ繧ｹ繧貞女縺大叙繧九ｈ縺・↓螟画峩縺吶ｋ縲・  - `launch_game(self, game_id: int)` 繝｡繧ｽ繝・ラ繧呈隼菫ｮ縺吶ｋ縲・    - 繧ｲ繝ｼ繝繝・・繧ｿ縺九ｉ `sync_enabled`, `save_folder`, `remote_sync_path` 繧貞叙蠕励☆繧九・    - `sync_enabled` 縺梧怏蜉ｹ縺九▽繝代せ縺瑚ｨｭ螳壹＆繧後※縺・ｋ蝣ｴ蜷・(`save_folder` 縺ｨ `remote_sync_path` 縺檎ｩｺ縺ｧ縺ｪ縺・ｴ蜷・ 縺ｫ縺ｮ縺ｿ蜷梧悄蜃ｦ逅・ｒ螳溯｡後☆繧九・    - 繧ｲ繝ｼ繝襍ｷ蜍募燕縺ｫ `RemoteStorageService.download_save_data` 繧貞他縺ｳ蜃ｺ縺吶・    - 繧ｲ繝ｼ繝繝励Ο繧ｻ繧ｹ邨ゆｺ・ｾ後↓ `RemoteStorageService.upload_save_data` 繧貞他縺ｳ蜃ｺ縺吶・    - 蜷梧悄蜃ｦ逅・ｸｭ縺ｮ `SaveDataSyncError` 繧呈黒謐峨＠縲√Ο繧ｰ險倬鹸縺ｨ `MainWindow` 縺ｸ縺ｮ騾夂衍・・QMessageBox`・峨・貅門ｙ繧定｡後≧縲・    - _Requirements: 2.1, 2.2, 2.3, 2.4, 3.1, 3.2, 3.3, 4.1, 4.2, 4.3_

- [x] 6. `GameDetailDialog` 縺ｮ UI 縺ｨ繝ｭ繧ｸ繝・け縺ｮ謾ｹ菫ｮ
  - [x] 6.1. 蜷梧悄險ｭ螳壼・蜉婉I縺ｮ霑ｽ蜉
  - [x] 6.2. UI縺ｮ繝・・繧ｿ繝舌う繝ｳ繝・ぅ繝ｳ繧ｰ縺ｨ菫晏ｭ倥Ο繧ｸ繝・け縺ｮ譖ｴ譁ｰ
  - [x] 6.3. 蜷梧悄險ｭ螳壹ヰ繝ｪ繝・・繧ｷ繝ｧ繝ｳ縺ｮ邨ｱ蜷・
- [ ] 7. 繝・せ繝医・霑ｽ蜉
  - [x] 7.1. `RemoteStorageService` 縺ｮ繝ｦ繝九ャ繝医ユ繧ｹ繝医・霑ｽ蜉
    - `download_save_data` 縺翫ｈ縺ｳ `upload_save_data` 繝｡繧ｽ繝・ラ縺ｮ謌仙粥/螟ｱ謨励す繝翫Μ繧ｪ縲√ヵ繧｡繧､繝ｫ謫堺ｽ懊・遒ｺ隱阪√お繝ｩ繝ｼ謐墓拷縺ｫ髢｢縺吶ｋ繝・せ繝医こ繝ｼ繧ｹ繧剃ｽ懈・縺吶ｋ縲・  - [x] 7.2. `GameService` 縺ｮ繝ｦ繝九ャ繝医ユ繧ｹ繝医・霑ｽ蜉
    - `sync_enabled`, `save_folder`, `remote_sync_path` 繧貞性繧繧ｲ繝ｼ繝縺ｮ逋ｻ骭ｲ縺ｨ譖ｴ譁ｰ縺ｫ髢｢縺吶ｋ繝・せ繝医こ繝ｼ繧ｹ繧剃ｽ懈・縺吶ｋ縲・  - [x] 7.3. `LauncherService` 縺ｮ繝ｦ繝九ャ繝医ユ繧ｹ繝医・霑ｽ蜉
    - `launch_game` 繝｡繧ｽ繝・ラ縺ｫ縺翫￠繧句酔譛溷・逅・・繝医Μ繧ｬ繝ｼ縲～RemoteStorageService` 縺ｨ縺ｮ騾｣謳ｺ縲√お繝ｩ繝ｼ莨晄眺縲√ご繝ｼ繝襍ｷ蜍慕ｶ咏ｶ壹Ο繧ｸ繝・け縺ｫ髢｢縺吶ｋ繝・せ繝医こ繝ｼ繧ｹ繧剃ｽ懈・縺吶ｋ縲・  - [x] 7.4. `GameDetailDialog` 縺ｮ繝ｦ繝九ャ繝医ユ繧ｹ繝医・霑ｽ蜉
    - 蜷梧悄險ｭ螳啅I縺ｮ陦ｨ遉ｺ縲√ョ繝ｼ繧ｿ繝舌う繝ｳ繝・ぅ繝ｳ繧ｰ縲√Μ繝｢繝ｼ繝医ヱ繧ｹ縺ｮ譛牙柑蛹・辟｡蜉ｹ蛹悶∽ｿ晏ｭ俶凾縺ｮ繝舌Μ繝・・繧ｷ繝ｧ繝ｳ繝｡繝・そ繝ｼ繧ｸ陦ｨ遉ｺ縺ｫ髢｢縺吶ｋ繝・せ繝医こ繝ｼ繧ｹ繧剃ｽ懈・縺吶ｋ縲・  - [x] 7.5. 邨ｱ蜷医ユ繧ｹ繝医・霑ｽ蜉 (P)
    - `GameDetailDialog` 縺九ｉ `GameService` 繧堤ｵ檎罰縺励◆蜷梧悄險ｭ螳壹・菫晏ｭ倥→隱ｭ縺ｿ霎ｼ縺ｿ繝輔Ο繝ｼ縺ｮ繝・せ繝医・    - `GameDetailDialog` 縺九ｉ `LauncherService` 繧堤ｵ檎罰縺励◆蜷梧悄險ｭ螳壻ｻ倥″繧ｲ繝ｼ繝縺ｮ襍ｷ蜍輔→邨ゆｺ・ｾ後・蜷梧悄繝輔Ο繝ｼ縺ｮ繝・せ繝医・    - 蜷梧悄荳ｭ縺ｮ繧ｨ繝ｩ繝ｼ・医ム繧ｦ繝ｳ繝ｭ繝ｼ繝・繧｢繝・・繝ｭ繝ｼ繝牙､ｱ謨暦ｼ臥匱逕滓凾縺ｮUI騾夂衍縺ｨ縲√ご繝ｼ繝襍ｷ蜍・邨ゆｺ・・邯咏ｶ壽ｧ縺ｫ髢｢縺吶ｋ繝・せ繝医・    - _Requirements: All_
