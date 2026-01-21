# Design Document: Move Add Game Button to Toolbar

## Feature Name
move-add-game-button-to-toolbar

## Project Description (Input)
ゲームを追加ボタンをツールバ�Eの`ライブラリ`->`ゲームの追加`に移勁E
## Design Decisions

This design outlines the relocation of the "Add Game" button functionality to a menu item within the application's menu bar, specifically under a "Library" menu, named "Add Game". This change aims to improve the application's user interface organization and accessibility for adding new games, aligning with standard GUI application practices.

### 1. Removal of Existing Button (`src/main_window.py`)

*   **Component**: The `QPushButton` currently labeled "ゲームを追加" (Add Game).
*   **Location**: `MainWindow._create_ui` method.
*   **Action**: The lines responsible for creating this `QPushButton` and adding it to `main_layout` will be removed. This includes the `add_game_button = QPushButton("ゲームを追加")` line and the subsequent `add_game_button.clicked.connect(...)` and `main_layout.addWidget(add_game_button)` calls.
*   **Impact**: This will free up vertical space at the bottom of the main window and clean up the primary view.

### 2. Menu Bar Implementation (`src/main_window.py`)

*   **Accessing `QMenuBar`**: The `QMainWindow` inherently provides a `QMenuBar` instance, accessible via `self.menuBar()`. If `self.menuBar()` returns `None`, it implies it hasn't been explicitly created; however, `QMainWindow` typically creates one on demand.
*   **Method**: The menu bar and its contents will be set up within the `_create_ui` method, or a new private method like `_create_menus()` can be introduced and called from `_create_ui` for better organization. For simplicity in this initial implementation, it will be added directly in `_create_ui`.
*   **Imports**: Ensure `QMenuBar` and `QAction` are correctly imported. (`QAction` is in `PySide6.QtGui`, `QMenu` in `PySide6.QtWidgets`).

### 3. "Library" Menu Creation (`src/main_window.py`)

*   **Menu Name**: A new `QMenu` will be created with the title "ライブラリ" (Library).
*   **Addition to Menu Bar**: This `QMenu` instance will be added to the `QMenuBar` using `self.menuBar().addMenu(library_menu)`.

### 4. "Add Game" Action Creation (`src/main_window.py`)

*   **Action Text**: A new `QAction` will be created with the text "ゲームの追加" (Add Game).
*   **Addition to Menu**: This `QAction` will be added to the "Library" `QMenu` using `library_menu.addAction(add_game_action)`.

### 5. Action Connection (`src/main_window.py`)

*   **Signal**: The `triggered` signal of the new "ゲームの追加" `QAction` will be connected.
*   **Slot**: It will be connected to the existing `self._open_add_game_dialog` method. This method already contains the necessary logic for opening the dialog and handling game registration.
    ```python
    add_game_action.triggered.connect(self._open_add_game_dialog)
    ```

### 6. UI Adjustments and Consistency

*   **No Major Layout Shift**: The removal of the button will primarily affect vertical spacing. The existing `QScrollArea` containing the `FlowLayout` for game cards will naturally expand to fill the available space.
*   **Event Handling**: The existing `_open_add_game_dialog` method will be reused, ensuring consistent behavior for adding games.
*   **PySide6 Best Practices**: The use of `QMenuBar`, `QMenu`, and `QAction` aligns with standard PySide6/Qt practices for menu-driven applications.

## Component Interactions

*   **`MainWindow`**: Orchestrates the creation and display of the menu bar, "Library" menu, and "Add Game" action.
*   **`QMenuBar`**: Top-level container for menus.
*   **`QMenu` (`"ライブラリ"`)**: Contains the "ゲームの追加" `QAction`.
*   **`QAction` (`"ゲームの追加"`)**: Triggers `MainWindow._open_add_game_dialog` when selected.
*   **`MainWindow._open_add_game_dialog`**: Existing method handling the game addition logic.

## Future Considerations

*   **Other Menu Items**: As the application grows, more actions can be organized under "Library" or other top-level menus (e.g., "File", "Edit", "Help").
*   **Keyboard Shortcuts**: Add keyboard shortcuts to menu actions for improved accessibility.
*   **Iconography**: Add icons to menu actions for better visual cues.
