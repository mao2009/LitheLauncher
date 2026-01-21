# Research & Design Decisions: i18n Standardization

---
**Purpose**: Capture discovery findings, architectural investigations, and rationale that inform the technical design for i18n standardization.

---

## Summary
- **Feature**: `i18n-standardization`
- **Discovery Scope**: Extension (Existing System)
- **Key Findings**:
  - The codebase currently has 0% i18n coverage; all strings are hardcoded literals.
  - PySide6 provides a standard `QTranslator` and `.tr()` mechanism that fits the modular service-based architecture of LitheLauncher.
  - Dynamic language switching requires overriding `changeEvent` in UI components to catch `LanguageChange` events.

## Research Log

### PySide6 Dynamic i18n Support
- **Context**: Need to support language switching without application restart.
- **Sources Consulted**: Qt Documentation (Internationalization with Qt), PySide6 API Reference.
- **Findings**:
  - Strings wrapped in `self.tr()` are automatically re-evaluated when a new `QTranslator` is installed.
  - The `QEvent.LanguageChange` event is dispatched to all top-level widgets when a translator is changed.
  - Static strings (e.g., in `__init__`) must be moved to a `retranslateUi()` method called from both `__init__` and `changeEvent`.
- **Implications**: Every UI class (`MainWindow`, `GameDetailDialog`, `GameCardWidget`) needs a structural update to support `retranslateUi()`.

### available Translation Tools
- **Context**: Automating string extraction and compilation.
- **Sources Consulted**: PySide6 documentation.
- **Findings**:
  - `pyside6-lupdate`: Extracts `.tr()` strings into `.ts` (XML) files.
  - `pyside6-lrelease`: Compiles `.ts` into binary `.qm` files for runtime loading.
- **Implications**: The build process or a maintenance script should include these commands.

### User Preference Persistence
- **Context**: Saving and restoring language settings.
- **Sources Consulted**: PySide6 `QSettings`.
- **Findings**: `QSettings` is the idiomatic way to handle application settings in Qt, mapping to the registry on Windows and config files on Unix.
- **Implications**: A new `LanguageService` should encapsulate `QSettings` interaction.

## Architecture Pattern Evaluation

| Option | Description | Strengths | Risks / Limitations | Notes |
|--------|-------------|-----------|---------------------|-------|
| Centralized Manager | `LanguageService` handles all i18n logic | Decoupled UI and logic, easy to test | Slightly more complex initial setup | Recommended approach |
| Main Window Only | Logic resides in `MainWindow` | Simple for small apps | `main.py` and `MainWindow` become bloated | Not scalable |

## Design Decisions

### Decision: Dedicated `LanguageService`
- **Context**: Need to centralize translator management and settings.
- **Alternatives Considered**: 
  1. Static utility functions.
  2. Singleton pattern.
- **Selected Approach**: Service-based injection (consistent with `GameService`).
- **Rationale**: LitheLauncher already uses a service-based architecture. `LanguageService` can be instantiated in `main.py` and passed to UI components or used to manage global state.
- **Trade-offs**: Requires updating `main.py` and potentially passing the service around, but ensures high testability.

### Decision: `retranslateUi` Pattern
- **Context**: How to update UI strings dynamically.
- **Selected Approach**: Use the standard Qt `retranslateUi()` method and override `changeEvent`.
- **Rationale**: This is the "Qt way" and is supported by both manual code and Qt Designer generated code.
- **Trade-offs**: Adds boilerplate to every UI class.

## Risks & Mitigations
- **Missed Strings**  EMitigation: Use `pyside6-lupdate` to identify untranslated strings and conduct a thorough code review.
- **UI Layout Breaking**  EMitigation: Use layouts (`QVBoxLayout`, `FlowLayout`) that adjust to varying string lengths; use `Qt.KeepAspectRatio` for images.
- **Missing QM Files**  EMitigation: Implementation must include a robust fallback to default strings (English) if a `.qm` file is not found.

## References
- [Qt Internationalization](https://doc.qt.io/qt-6/internationalization.html)  EOfficial guide.
- [PySide6 i18n Example](https://doc.qt.io/qtforpython-6/tutorials/i18n/i18n.html)  EPractical implementation.
