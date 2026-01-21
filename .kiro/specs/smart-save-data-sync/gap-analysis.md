# Gap Analysis: Smart Save Data Sync

## Analysis Summary
- **Scope**: 繧ｲ繝ｼ繝襍ｷ蜍墓凾縺ｮ繧ｻ繝ｼ繝悶ョ繝ｼ繧ｿ蜷梧悄繧偵御ｸ譁ｹ蜷代・荳頑嶌縺阪阪°繧峨梧怙譁ｰ繝・・繧ｿ縺ｮ蜆ｪ蜈域治逕ｨ縲阪↓繧｢繝・・繧ｰ繝ｬ繝ｼ繝峨☆繧九・- **Challenges**: 繝ｭ繝ｼ繧ｫ繝ｫ/繝ｪ繝｢繝ｼ繝亥曙譁ｹ縺ｮ繝・ぅ繝ｬ繧ｯ繝医Μ蜀・↓縺ゅｋ繝輔ぃ繧､繝ｫ縺ｮ譛譁ｰ譖ｴ譁ｰ譌･譎ゅｒ豁｣遒ｺ縺ｫ豈碑ｼ・☆繧九Ο繧ｸ繝・け縺ｮ螳溯｣・ゅ∪縺溘∽ｸ肴紛蜷域凾縺ｮUI騾夂衍・・MessageBox遲会ｼ峨・邨ｱ蜷医・- **Recommendation**: 譌｢蟄倥・ `RemoteStorageService` 縺ｫ豈碑ｼ・Ο繧ｸ繝・け繧定ｿｽ蜉縺励～LauncherService` 縺ｮ蜷梧悄繝輔Ο繝ｼ繧呈僑蠑ｵ縺吶ｋ縲後が繝励す繝ｧ繝ｳ A縲阪ｒ謗ｨ螂ｨ縲・
## Current State vs. Requirements

| Requirement ID | Technical Needs | Existing Assets | Gap Status | Details |
| :--- | :--- | :--- | :--- | :--- |
| 1 | 譛邨よ峩譁ｰ譌･譎ゅ・豈碑ｼ・| `RemoteStorageService` | **Missing** | 繝輔ぃ繧､繝ｫ/繝・ぅ繝ｬ繧ｯ繝医Μ縺ｮ繧ｿ繧､繝繧ｹ繧ｿ繝ｳ繝励ｒ蜿門ｾ励・豈碑ｼ・☆繧区ｩ溯・縺後↑縺・・|
| 1.2 | 譚｡莉ｶ莉倥″蜷梧悄 (DL/UL/Skip) | `LauncherService.sync_save_data` | **Missing** | 迴ｾ迥ｶ縺ｯ "download" 縺・"upload" 縺ｮ蝗ｺ螳壽欠遉ｺ縺ｮ縺ｿ縲・|
| 2.2 | 遶ｶ蜷域凾縺ｮ謇句虚驕ｸ謚槭ム繧､繧｢繝ｭ繧ｰ | `LauncherService`, `PySide6` | **Missing** | 繝ｦ繝ｼ繧ｶ繝ｼ縺ｫ蝠上＞蜷医ｏ縺帙ｋ UI 繝ｭ繧ｸ繝・け縺梧悴螳溯｣・・|
| 3.1 | UI縺ｸ縺ｮ繧ｹ繝・・繧ｿ繧ｹ陦ｨ遉ｺ | `MainWindow` / `LauncherService` | **Missing** | 蜷梧悄荳ｭ縺ｮ迥ｶ諷九ｒ繝ｦ繝ｼ繧ｶ繝ｼ縺ｫ繝輔ぅ繝ｼ繝峨ヰ繝・け縺吶ｋ莉慕ｵ・∩縺悟ｿ・ｦ√・|

## Implementation Options

### Option A: Extend RemoteStorageService & LauncherService (Recommended)
- **Rationale**: 迴ｾ陦後・繧ｵ繝ｼ繝薙せ讒矩縺ｫ閾ｪ辟ｶ縺ｫ繝輔ぅ繝・ヨ縺励・幕逋ｺ繧ｳ繧ｹ繝医′菴弱＞縲・- **Changes**: 
  - `RemoteStorageService`: `get_latest_timestamp(path)` 繝｡繧ｽ繝・ラ遲峨・霑ｽ蜉縲・  - `LauncherService`: `sync_save_data` 蜀・〒豈碑ｼ・Ο繧ｸ繝・け繧貞他縺ｳ蜃ｺ縺励∵擅莉ｶ蛻・ｲ舌ｒ霑ｽ蜉縲・- **Trade-offs**: 
  - 笨・譌｢蟄倩ｳ・肇繧呈怙螟ｧ髯先ｴｻ逕ｨ縲・  - 笶・`LauncherService` 縺ｮ繝｡繧ｽ繝・ラ縺碁聞縺上↑繧句庄閭ｽ諤ｧ縺後≠繧九・
### Option B: Create SaveDataSyncService
- **Rationale**: 蜷梧悄繝ｭ繧ｸ繝・け縺御ｻ雁ｾ後＆繧峨↓隍・尅蛹悶☆繧句ｴ蜷医↓蛯吶∴縲∬ｲｬ蜍吶ｒ螳悟・縺ｫ迢ｬ遶九＆縺帙ｋ縲・- **Changes**: 蜷梧悄縺ｫ髢｢縺吶ｋ蜈ｨ縺ｦ縺ｮ繝薙ず繝阪せ繝ｭ繧ｸ繝・け繧呈眠繧ｵ繝ｼ繝薙せ縺ｫ遘ｻ蜍輔・- **Trade-offs**:
  - 笨・鬮倥＞菫晏ｮ域ｧ縺ｨ繝・せ繝亥ｮｹ譏捺ｧ縲・  - 笶・螳溯｣・が繝ｼ繝舌・繝倥ャ繝峨′繧・ｄ螟ｧ縺阪＞縲・
## Complexity & Risk
- **Effort**: **S (1窶・ days)**
  - 譌｢蟄倥・繝代ち繝ｼ繝ｳ縺ｫ蠕薙▲縺溘Γ繧ｽ繝・ラ霑ｽ蜉縺ｨ譚｡莉ｶ蛻・ｲ舌・螳溯｣・〒螳檎ｵ舌☆繧九◆繧√・- **Risk**: **Low**
  - 菴ｿ逕ｨ縺吶ｋ謚陦難ｼ・ython讓呎ｺ悶Λ繧､繝悶Λ繝ｪ `os`, `pathlib`, `shutil`・峨′遒ｺ遶九＆繧後※縺翫ｊ縲∵里蟄倥・ `LauncherService` 繝・せ繝育ｾ､繧呈ｵ∫畑縺ｧ縺阪ｋ縺溘ａ縲・
## Next Steps for Design
- 繝・ぅ繝ｬ繧ｯ繝医Μ蜀・・譛譁ｰ繝輔ぃ繧､繝ｫ繧堤音螳壹☆繧九◆繧√・蜀榊ｸｰ逧・↑繧ｿ繧､繝繧ｹ繧ｿ繝ｳ繝怜叙蠕励い繝ｫ繧ｴ繝ｪ繧ｺ繝縺ｮ險ｭ險医・- 繝ｦ繝ｼ繧ｶ繝ｼ騾夂衍逕ｨ繝繧､繧｢繝ｭ繧ｰ縺ｮ繝｡繝・そ繝ｼ繧ｸ譁・ｨ縺ｨ陦ｨ遉ｺ繧ｿ繧､繝溘Φ繧ｰ縺ｮ螳夂ｾｩ縲・- `LauncherService` 縺ｫ縺翫￠繧句酔譛溘ヵ繧ｧ繝ｼ繧ｺ縺ｮ繧ｹ繝・・繧ｿ繧ｹ騾夂衍譁ｹ豕包ｼ医す繧ｰ繝翫Ν/繧ｹ繝ｭ繝・ヨ遲会ｼ峨・讀懆ｨ弱・
