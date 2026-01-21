# Implementation Plan

- [ ] 1. Implement menu bar and "Add Game" action
  - [x] 1.1 Remove the existing "Add Game" button from the main window
    - In `src/main_window.py`, remove the lines creating the `QPushButton("ゲームを追加")`.
    - Remove the `add_game_button.setObjectName(...)`, `add_game_button.clicked.connect(...)`, and `main_layout.addWidget(add_game_button)` lines.
    - _Requirements: Requirement 1_
  - [x] 1.2 Create and integrate the menu bar and "Library" menu
    - In `src/main_window.py`, get the `QMenuBar` instance using `self.menuBar()`.
    - Create a new `QMenu` titled "ライブラリ" (Library).
    - Add this `QMenu` to the `QMenuBar` using `self.menuBar().addMenu(...)`.
    - _Requirements: Requirement 1, Requirement 3_
  - [x] 1.3 Create and connect the "Add Game" menu action
    - Create a new `QAction` with the text "ゲームの追加" (Add Game).
    - Add this `QAction` to the "ライブラリ" menu.
    - Connect the `triggered` signal of this `QAction` to the existing `self._open_add_game_dialog` method.
    - Ensure `QAction` is imported from `PySide6.QtGui`.
    - _Requirements: Requirement 1, Requirement 2, Requirement 3_

- [ ] 2. Develop comprehensive unit and integration tests
  - [x] 2.1 Develop unit tests for the menu bar and actions
    - Test that the "Add Game" button `QPushButton` is no longer present.
    - Test that a `QMenuBar` exists.
    - Test that a "ライブラリ" `QMenu` exists in the menu bar.
    - Test that a "ゲームの追加" `QAction` exists within the "ライブラリ" menu.
    - _Requirements: Requirement 1, Requirement 3_
  - [x] 2.2 Develop integration tests for "Add Game" menu action functionality
    - Simulate triggering the "ゲームの追加" `QAction`.
    - Assert that `_open_add_game_dialog` is called.
    - Assert that the correct game addition logic (mocked `game_service.register_game`) is invoked.
    - _Requirements: Requirement 2_
```
