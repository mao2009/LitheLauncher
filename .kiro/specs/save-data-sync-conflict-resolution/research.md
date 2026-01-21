# Research & Design Decisions: save-data-sync-conflict-resolution

## Summary
- **Feature**: save-data-sync-conflict-resolution
- **Discovery Scope**: Extension
- **Key Findings**:
  - `LauncherService.sync_save_data` 縺ｮ `smart` 繝｢繝ｼ繝峨↓譌｢縺ｫ繧ｿ繧､繝繧ｹ繧ｿ繝ｳ繝玲ｯ碑ｼ・→繝繧､繧｢繝ｭ繧ｰ陦ｨ遉ｺ (`_show_sync_conflict_dialog`) 縺ｮ莉慕ｵ・∩縺後≠繧九・  - 迴ｾ蝨ｨ縺ｯ縲梧悴譚･縺ｮ繧ｿ繧､繝繧ｹ繧ｿ繝ｳ繝励肴凾縺ｮ縺ｿ繝繧､繧｢繝ｭ繧ｰ繧定｡ｨ遉ｺ縺励※縺翫ｊ縲・壼ｸｸ縺ｮ縲後Ο繝ｼ繧ｫ繝ｫ縺梧眠縺励＞縲阪こ繝ｼ繧ｹ縺ｯ閾ｪ蜍輔い繝・・繝ｭ繝ｼ繝峨↓縺ｪ縺｣縺ｦ縺・ｋ縲・  - `_show_sync_conflict_dialog` 縺ｯ `QMessageBox` 繧堤峩謗･逕滓・縺励※陦ｨ遉ｺ縺励※縺翫ｊ縲√ユ繧ｹ繝医〒縺ｯ `mocker.patch.object` 縺ｧ繝｢繝・け縺輔ｌ縺ｦ縺・ｋ縲・
## Research Log

### 譌｢蟄倥・蜷梧悄繝ｭ繧ｸ繝・け縺ｮ蜍穂ｽ・- **Context**: 譌｢蟄倥・ `LauncherService` 縺後←縺ｮ繧医≧縺ｫ遶ｶ蜷医ｒ謇ｱ縺｣縺ｦ縺・ｋ縺九・- **Sources Consulted**: `src/launcher_service.py`
- **Findings**: 
  - `abs(remote_mtime - local_mtime) < 1.0` 縺ｪ繧峨せ繧ｭ繝・・縲・  - `remote_mtime > local_mtime` 縺ｪ繧峨ム繧ｦ繝ｳ繝ｭ繝ｼ繝峨・  - 縺昴ｌ莉･螟厄ｼ・local_mtime > remote_mtime`・峨↑繧峨い繝・・繝ｭ繝ｼ繝峨・  - 譛ｪ譚･譌･莉俶凾縺ｮ縺ｿ繝繧､繧｢繝ｭ繧ｰ陦ｨ遉ｺ縲・- **Implications**: `local_mtime > remote_mtime` 縺ｮ蝣ｴ蜷医ｂ繝繧､繧｢繝ｭ繧ｰ繧定｡ｨ遉ｺ縺吶ｋ繧医≧縺ｫ譚｡莉ｶ繧堤ｷｩ蜥後・螟画峩縺吶ｋ蠢・ｦ√′縺ゅｋ縲・
### 繝繧､繧｢繝ｭ繧ｰ縺ｮ謌ｻ繧雁､縺ｨ繧｢繧ｯ繧ｷ繝ｧ繝ｳ
- **Context**: 繝繧､繧｢繝ｭ繧ｰ縺瑚ｿ斐☆蛟､縺ｨ縺昴・蠕後・蜃ｦ逅・・- **Findings**: 
  - 繝繧､繧｢繝ｭ繧ｰ縺ｯ `"local"`, `"remote"`, `"cancel"` 繧定ｿ斐☆縲・  - `"local"` 縺ｯ `target_direction = "upload"` 縺ｫ螟画鋤縺輔ｌ繧九・  - `"remote"` 縺ｯ `target_direction = "download"` 縺ｫ螟画鋤縺輔ｌ繧九・- **Implications**: 譌｢蟄倥・謌ｻ繧雁､菴鍋ｳｻ繧偵◎縺ｮ縺ｾ縺ｾ蛻ｩ逕ｨ蜿ｯ閭ｽ縲・
## Architecture Pattern Evaluation

| Option | Description | Strengths | Risks / Limitations | Notes |
|--------|-------------|-----------|---------------------|-------|
| 譌｢蟄俶僑蠑ｵ | `sync_save_data` 縺ｮ譚｡莉ｶ蛻・ｲ舌ｒ菫ｮ豁｣ | 譛蟆城剞縺ｮ螟画峩縲∵里蟄倥ユ繧ｹ繝域ｵ∫畑蜿ｯ | 繝｡繧ｽ繝・ラ縺ｮ閧･螟ｧ蛹・| 莉雁屓縺ｮ隕∽ｻｶ縺ｫ譛驕ｩ |

## Design Decisions

### Decision: 譌｢蟄倥ム繧､繧｢繝ｭ繧ｰ縺ｮ豢ｻ逕ｨ縺ｨ譚｡莉ｶ諡｡蠑ｵ
- **Context**: 繝ｦ繝ｼ繧ｶ繝ｼ縺ｫ遒ｺ隱阪ｒ豎ゅａ繧九ヨ繝ｪ繧ｬ繝ｼ縺ｮ螟画峩縲・- **Alternatives Considered**:
  1. 譁ｰ縺励＞繝繧､繧｢繝ｭ繧ｰ繧ｯ繝ｩ繧ｹ繧剃ｽ懈・縺吶ｋ
  2. 譌｢蟄倥・ `_show_sync_conflict_dialog` 繧呈僑蠑ｵ縺吶ｋ
- **Selected Approach**: 2. 譌｢蟄倥・ `_show_sync_conflict_dialog` 繧呈僑蠑ｵ縺吶ｋ縲・- **Rationale**: 譌｢縺ｫ蠢・ｦ√↑諠・ｱ・医Ο繝ｼ繧ｫ繝ｫ/繝ｪ繝｢繝ｼ繝医・譎る俣縲√ご繝ｼ繝繧ｿ繧､繝医Ν・峨ｒ蜿励￠蜿悶▲縺ｦ驕ｸ謚櫁い繧呈署遉ｺ縺吶ｋ讖溯・縺悟ｙ繧上▲縺ｦ縺・ｋ縺溘ａ縲・- **Trade-offs**: 譛ｪ譚･譌･莉倥・蝣ｴ蜷医→縲悟腰縺ｫ繝ｭ繝ｼ繧ｫ繝ｫ縺梧眠縺励＞縲榊ｴ蜷医〒繝｡繝・そ繝ｼ繧ｸ繧貞・縺怜・縺代ｋ蠢・ｦ√′縺ゅｋ縲・- **Follow-up**: `local_mtime > remote_mtime` 縺ｮ繝・せ繝医こ繝ｼ繧ｹ繧定ｿｽ蜉縺吶ｋ縲・
## Risks & Mitigations
- 繝ｦ繝ｼ繧ｶ繝ｼ繝薙Μ繝・ぅ縺ｮ菴惹ｸ・窶・鬆ｻ郢√↓繝繧､繧｢繝ｭ繧ｰ縺悟・繧九→繝ｦ繝ｼ繧ｶ繝ｼ縺檎・繧上＠縺乗─縺倥ｋ蜿ｯ閭ｽ諤ｧ縺後≠繧九・itigation: 繧ｿ繧､繝繧ｹ繧ｿ繝ｳ繝励′螳悟・縺ｫ荳閾ｴ縺吶ｋ蝣ｴ蜷医ｄ繝ｪ繝｢繝ｼ繝医′譁ｰ縺励＞蝣ｴ蜷医・閾ｪ蜍募・逅・ｒ邯ｭ謖√☆繧九・- UI繝輔Μ繝ｼ繧ｺ 窶・`sync_save_data` 縺ｯ蛻･繧ｹ繝ｬ繝・ラ縺ｧ螳溯｡後＆繧後ｋ蜿ｯ閭ｽ諤ｧ縺後≠繧具ｼ・auncherService縺ｮ騾夂衍繝代ち繝ｼ繝ｳ・峨・itigation: Qt縺ｮGUI謫堺ｽ懊・繝｡繧､繝ｳ繧ｹ繝ｬ繝・ラ縺ｧ陦後≧蠢・ｦ√′縺ゅｋ縺後∫樟迥ｶ `_show_sync_conflict_dialog` 縺ｯ逶ｴ謗･ `QMessageBox` 繧貞他繧薙〒縺・ｋ縲ゅ％繧後′蛻･繧ｹ繝ｬ繝・ラ縺九ｉ蜻ｼ縺ｰ繧後※縺・↑縺・°隕∫｢ｺ隱搾ｼ育樟迥ｶ縺ｯ蜻ｼ縺ｳ蜃ｺ縺怜・縺後Γ繧､繝ｳ繧ｹ繝ｬ繝・ラ縺ｧ縺ゅｋ縺薙→繧貞燕謠舌→縺励※縺・ｋ讓｡讒假ｼ峨・
## References
- `src/launcher_service.py` 窶・蜷梧悄繝ｭ繧ｸ繝・け譛ｬ菴・- `tests/test_launcher_service.py` 窶・繝・せ繝医さ繝ｼ繝・
