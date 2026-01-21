# Requirements Document

## Introduction
縺薙・繝峨く繝･繝｡繝ｳ繝医・縲√訓yzree Game Launcher縲阪・蝗ｽ髫帛喧・・18n・画ｨ呎ｺ門喧縺ｫ髢｢縺吶ｋ隕∽ｻｶ繧貞ｮ夂ｾｩ縺励∪縺吶よ悽讖溯・縺ｮ逶ｮ逧・・縲√い繝励Μ繧ｱ繝ｼ繧ｷ繝ｧ繝ｳ蜈ｨ菴薙・UI譁・ｭ怜・繧・Qt 縺ｮ讓呎ｺ也噪縺ｪ鄙ｻ險ｳ繝｡繧ｫ繝九ぜ繝・・.tr()` 繝｡繧ｽ繝・ラ・峨〒繝ｩ繝・・縺励～QTranslator` 繧剃ｽｿ逕ｨ縺励◆蜍慕噪縺ｪ險隱槫・繧頑崛縺医ｒ螳悟・縺ｫ螳溯｣・☆繧九％縺ｨ縺ｧ縲√さ繝ｼ繝峨・繝ｼ繧ｹ縺ｮ菫晏ｮ域ｧ縺ｨ繝ｦ繝ｼ繧ｶ繝ｼ菴馴ｨ薙ｒ蜷台ｸ翫＆縺帙ｋ縺薙→縺ｧ縺吶・
## Requirements

### Requirement 1: UI譁・ｭ怜・縺ｮ讓呎ｺ門喧
**Objective:** 髢狗匱閠・→縺励※縲√☆縺ｹ縺ｦ縺ｮUI譁・ｭ怜・繧・`.tr()` 繝｡繧ｽ繝・ラ縺ｧ繝ｩ繝・・縺励◆縺・ゅ◎縺・☆繧九％縺ｨ縺ｧ縲∝､夊ｨ隱槭∈縺ｮ鄙ｻ險ｳ縺ｨ謚ｽ蜃ｺ繧貞庄閭ｽ縺ｫ縺吶ｋ縺溘ａ縲・
#### Acceptance Criteria
1. The LitheLauncher Game Launcher shall wrap all user-visible strings in the source code with the `.tr()` method.
2. When a UI component is initialized, the LitheLauncher Game Launcher shall assign all labels, button texts, and tooltips using the `.tr()` method.
3. The LitheLauncher Game Launcher shall ensure that complex strings with variables use standard Qt string formatting placeholders (e.g., `%1`) within `.tr()`.

### Requirement 2: 蜍慕噪縺ｪ險隱槫・繧頑崛縺・**Objective:** 繝ｦ繝ｼ繧ｶ繝ｼ縺ｨ縺励※縲√い繝励Μ繧ｱ繝ｼ繧ｷ繝ｧ繝ｳ繧貞・襍ｷ蜍輔☆繧九％縺ｨ縺ｪ縺上√Γ繝九Η繝ｼ縺九ｉ陦ｨ遉ｺ險隱槭ｒ蛻・ｊ譖ｿ縺医◆縺・・
#### Acceptance Criteria
1. When a user selects a language from the language menu, the LitheLauncher Game Launcher shall load the corresponding translation (`.qm`) file using `QTranslator`.
2. When a new `QTranslator` is installed in the application, the LitheLauncher Game Launcher shall call `retranslateUi()` (or equivalent refresh logic) for all active windows and dialogs.
3. If the required translation file is missing or corrupted, then the LitheLauncher Game Launcher shall fall back to the default language (English).

### Requirement 3: 險隱櫁ｨｭ螳壹・豌ｸ邯壼喧
**Objective:** 繝ｦ繝ｼ繧ｶ繝ｼ縺ｨ縺励※縲・∈謚槭＠縺溯ｨ隱櫁ｨｭ螳壹′谺｡蝗櫁ｵｷ蜍墓凾縺ｫ繧らｶｭ謖√＆繧後ｋ繧医≧縺ｫ縺励◆縺・・
#### Acceptance Criteria
1. When the application starts, the LitheLauncher Game Launcher shall retrieve the last used language setting from `QSettings`.
2. When a user changes the language preference, the LitheLauncher Game Launcher shall immediately save the new setting to `QSettings`.

### Requirement 4: 繧ｷ繧ｹ繝・Β險ｭ螳壹・閾ｪ蜍墓､懷・
**Objective:** 譁ｰ隕上Θ繝ｼ繧ｶ繝ｼ縺ｨ縺励※縲√い繝励Μ繧ｱ繝ｼ繧ｷ繝ｧ繝ｳ縺後す繧ｹ繝・Β縺ｮ險隱櫁ｨｭ螳壹↓蜷医ｏ縺帙※閾ｪ蜍慕噪縺ｫ蛻晄悄險隱槭ｒ驕ｸ謚槭＠縺ｦ縺ｻ縺励＞縲・
#### Acceptance Criteria
1. If no language preference is found in `QSettings` during startup, then the LitheLauncher Game Launcher shall detect the system's preferred language using `QLocale`.
2. The LitheLauncher Game Launcher shall provide a "System Default" option in the language menu that follows the OS locale settings.
