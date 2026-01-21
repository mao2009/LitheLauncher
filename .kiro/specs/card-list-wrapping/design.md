# Design Document: Card List Wrapping

## Feature Name
card-list-wrapping

## Project Description (Input)
一覧をカードスタイルにして左から右に並んで折り返す

## Design Decisions

This design outlines the implementation of a card-based, horizontally wrapping game list in the LitheLauncher Game Launcher, leveraging PySide6. The core architectural changes involve introducing a custom `FlowLayout` for dynamic arrangement and a dedicated `GameCardWidget` for each game entry, along with a robust QSS styling strategy.

### 1. FlowLayout Implementation (`src/flow_layout.py`)

*   **Purpose**: To dynamically arrange `GameCardWidget` instances from left to right, wrapping to the next line when horizontal space is exhausted, and adjusting automatically upon window resizing.
*   **Location**: A new file `src/flow_layout.py` will be created.
*   **Class Definition**: `FlowLayout` will inherit from `QLayout`.
*   **Core Logic**:
    *   **Item Management**: Override `addItem(item)`, `count()`, `itemAt(index)`, `takeAt(index)` to manage the internal list of `QLayoutItem`s.
    *   **Layout Calculation (`setGeometry`)**: This is the primary method for positioning widgets. It will iterate through the layout's items, calculating their positions. When an item's calculated position extends beyond the available width, it will start a new row. The `x` and `y` coordinates for each item will be set using `item.setGeometry()`.
    *   **Size Hints (`sizeHint`, `minimumSize`)**: Implement these methods to provide appropriate size suggestions to the parent widget, ensuring the layout behaves correctly within its container.
    *   **Responsiveness**: The `setGeometry()` method is inherently responsive. Qt's layout system will automatically call `setGeometry()` on the `FlowLayout` whenever its parent widget (the `QScrollArea`'s viewport) is resized, triggering a recalculation and re-arrangement of the game cards.

### 2. GameCardWidget Design (`src/game_card_widget.py`)

*   **Purpose**: To encapsulate the visual representation and interaction logic for a single game entry.
*   **Location**: A new file `src/game_card_widget.py` will be created.
*   **Class Definition**: `GameCardWidget` will inherit from `QWidget`.
*   **Constructor**: `__init__(self, game_data: dict, parent=None)` will accept a dictionary containing game information (e.g., `game_id`, `title`, `cover_art_path`).
*   **UI Elements**:
    *   **Layout**: A `QVBoxLayout` will be used internally within the `GameCardWidget` to arrange its elements vertically.
    *   **Cover Art**: A `QLabel` (`cover_art_label` with `setObjectName("cover_art_label")`) will display the game's cover art. The cover art will be loaded as a `QPixmap` from `game_data['cover_art_path']` and scaled to **600 x 900 pixels**. This `QLabel` should have a fixed size or size policy to accommodate these dimensions.
    *   **Title**: A `QLabel` (`title_label` with `setObjectName("title_label")`) will display `game_data['title']`.
*   **Interactions & Signals**:
    *   **Double-Click for Launch**: Override `mouseDoubleClickEvent(event: QMouseEvent)`. Upon detection of a double-click, it will emit a custom PySide6 signal, e.g., `launched = Signal(int)`, passing `self.game_id`.
    *   **Right-Click Context Menu**: Override `contextMenuEvent(event: QContextMenuEvent)`. This method will:
        *   Create a `QMenu` instance.
        *   Add `QAction`s for "Launch Game" and "Edit Game Details".
        *   Connect these actions to internal slots that will emit custom signals, e.g., `edited = Signal(int)` and `deleted = Signal(int)`, passing `self.game_id`.
        *   Display the menu at the event's position (`menu.exec(self.mapToGlobal(event.pos()))`).
*   **Properties**: The `game_id` will be stored as an instance variable (`self.game_id`) for easy access in signals.

### 3. QSS Styling Strategy (`res/style.qss`)

*   **Purpose**: To apply a modern, visually appealing, and consistent style to the `GameCardWidget` and other UI elements.
*   **Location**: A new directory `res/` will be created at the project root, and a file `res/style.qss` will reside within it.
*   **Styling Rules**:
    *   **`GameCardWidget` Base Style**: Define `background-color`, `border`, `border-radius`, and `margin`.
    *   **Hover Effect**: Implement a `:hover` pseudo-state to provide visual feedback when the mouse hovers over a card.
    *   **Internal Labels**: Style `QLabel#title_label` for font properties (e.g., `font-weight`, `color`).
    *   **Potential for further styling**: Expand to include styles for scroll areas, main window, etc., as needed.
*   **Loading Mechanism**:
    *   In `main.py`, before `app.exec_()`, the `style.qss` file will be read.
    *   `QApplication.setStyleSheet()` will be called with the content of the QSS file.
    *   Error handling for `FileNotFoundError` will be included to ensure graceful degradation if the stylesheet is missing.

### 4. Integration into MainWindow (`src/main_window.py`)

*   **Imports**: Add `from src.flow_layout import FlowLayout` and `from src.game_card_widget import GameCardWidget`.
*   **`_create_ui()` Method Modifications**:
    *   **Container for Cards**: The `game_card_list_layout` (currently a `QVBoxLayout`) will be replaced. A `QScrollArea` will become the primary container for the game cards to enable scrolling when content overflows.
    *   **FlowLayout Initialization**: Inside the `QScrollArea`, a `QWidget` will serve as the content widget, and the `FlowLayout` will be applied to this content widget.
    ```python
    # In MainWindow._create_ui
    scroll_area = QScrollArea()
    scroll_area.setWidgetResizable(True)
    scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff) # Ensure only vertical scrolling
    container_widget = QWidget()
    self.game_card_list_layout = FlowLayout() # Initialize FlowLayout
    container_widget.setLayout(self.game_card_list_layout) # Apply FlowLayout to container
    scroll_area.setWidget(container_widget)
    main_layout.addWidget(scroll_area) # Add scroll area to main window's layout
    ```
*   **`_load_games()` Method Modifications**:
    *   **Clearing Existing Cards**: Before loading new games, ensure all existing `GameCardWidget` instances are removed from the `FlowLayout`. This involves iterating through `self.game_card_list_layout.takeAt(0)` until the layout is empty.
    *   **Populating with `GameCardWidget`**: Iterate through the game data obtained from `game_service.get_game_list()`. For each `game_data` item:
        *   Create an instance of `GameCardWidget(game_data)`.
        *   Connect the `GameCardWidget`'s signals (`launched`, `edited`, `deleted`) to appropriate slots in `MainWindow` (e.g., `_launch_game_action`, `_open_edit_game_dialog`, `_delete_game`).
        *   Add the `GameCardWidget` to `self.game_card_list_layout` using `self.game_card_list_layout.addWidget(game_card)`.
*   **Removal of `_add_game_card()`**: The `_add_game_card` method will be removed as its functionality is superseded by the direct creation and addition of `GameCardWidget` instances within `_load_games()`.
*   **New Slots**: Implement the slots `_launch_game_action(game_id)`, `_open_edit_game_dialog(game_id)`, and `_delete_game(game_id)` in `MainWindow` to handle signals from `GameCardWidget`. These slots will then interact with `LauncherService` and `GameService` accordingly.

### 5. Data Flow

*   **Game Data Population**:
    *   `MainWindow` (specifically `_load_games()`) retrieves a list of game data dictionaries from `GameService.get_game_list()`.
    *   Each game data dictionary is passed to the constructor of a new `GameCardWidget` instance.
*   **User Actions from `GameCardWidget`**:
    *   **Launch Game (Double-click)**: `GameCardWidget` emits `launched(game_id)`. This signal is connected to `MainWindow._launch_game_action(game_id)`, which then calls `LauncherService.launch_game(game_id)`.
    *   **Edit Game (Context Menu)**: `GameCardWidget` emits `edited(game_id)`. This signal is connected to `MainWindow._open_edit_game_dialog(game_id)`. The `MainWindow` will then open the `game_detail_dialog` populated with the game's details.
    *   **Delete Game (Context Menu)**: `GameCardWidget` emits `deleted(game_id)`. This signal is connected to `MainWindow._delete_game(game_id)`, which will then call `GameService.delete_game(game_id)` and refresh the list.

### 6. Responsiveness

*   **Inherent FlowLayout Behavior**: The custom `FlowLayout`'s `setGeometry()` method will automatically be invoked by the Qt layout engine whenever the available space for the layout changes (e.g., due to window resizing or maximization/restoration).
*   **Dynamic Card Arrangement**: Within `setGeometry()`, the `FlowLayout` recalculates the position of each `GameCardWidget`. It intelligently determines when to wrap cards to the next line based on the current width, thus dynamically adjusting the number of cards displayed per row. This ensures the UI remains aesthetically pleasing and functional across various window sizes.

## Future Considerations

*   **Placeholder for missing cover art**: Implement a default image for games without specified cover art.
*   **Card sizing**: Allow for configurable card sizes, potentially through QSS variables or application settings.
*   **Filtering/Sorting**: Integrate filtering and sorting options for the game card list.
