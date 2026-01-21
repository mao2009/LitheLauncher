# Requirements Document

## Introduction
This document outlines the requirements for relocating the "Add Game" button functionality to a menu item within the application's toolbar, specifically under a "Library" menu, named "Add Game". This change aims to improve the application's user interface organization and accessibility for adding new games.

## Requirements

### Requirement 1: Relocation of "Add Game" Functionality
**Objective:** As a user, I want to add new games via a menu item instead of a dedicated button in the main window, so that the UI is cleaner and more organized.

#### Acceptance Criteria
1. WHEN the application starts THEN the dedicated "Add Game" `QPushButton` SHALL NOT be visible in the main window's layout.
2. WHEN the application starts THEN a menu bar SHALL be present at the top of the main window.
3. WHEN the menu bar is present THEN it SHALL contain a top-level menu named "ライブラリ" (Library).
4. WHEN the "ライブラリ" menu is clicked THEN it SHALL display a menu item named "ゲームの追加" (Add Game).
5. WHEN the "ゲームの追加" menu item is triggered THEN the LitheLauncher Game Launcher SHALL open the "Add Game" dialog.
   * _(Derived from Project Description)_

### Requirement 2: User Interaction
**Objective:** As a user, I want the process of adding a game through the new menu item to be intuitive and consistent with the previous button functionality, so that my workflow is not disrupted.

#### Acceptance Criteria
1. WHEN the "ゲームの追加" menu item is clicked THEN the LitheLauncher Game Launcher SHALL invoke the same underlying logic as the previous "Add Game" button.
2. IF the "Add Game" dialog is successfully completed THEN the LitheLauncher Game Launcher SHALL add the new game to the list.
   * _(Derived from Project Description, consistency with existing functionality)_

### Requirement 3: UI Consistency and Maintainability
**Objective:** As a developer, I want the new menu structure to align with PySide6 best practices and be easily maintainable, so that future UI enhancements are straightforward.

#### Acceptance Criteria
1. WHERE a menu bar is implemented THEN it SHALL utilize PySide6's `QMenuBar` component.
2. WHERE menu items are implemented THEN they SHALL utilize PySide6's `QMenu` and `QAction` components.
3. WHEN connecting the "ゲームの追加" `QAction` THEN it SHALL connect to the existing `MainWindow._open_add_game_dialog` slot.
   * _(Derived from technical context, maintainability)_
