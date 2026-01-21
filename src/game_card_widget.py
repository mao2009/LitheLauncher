from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QMenu
from PySide6.QtGui import QPixmap, QAction
from PySide6.QtCore import Signal, Qt, QThreadPool, QEvent
from src.executable_validator import ExecutableValidator, ValidationResult
from src.image_loader import ImageLoader
from pathlib import Path

class GameCardWidget(QWidget):
    # Signals for interactions
    launched = Signal(int)
    edited = Signal(int)
    deleted = Signal(int)

    def __init__(self, game_data: dict, parent=None):
        super().__init__(parent)
        self._init_ui()
        self.update_data(game_data)

    def update_data(self, game_data: dict, deferred: bool = False):
        """ウィジェットのデータを更新し、UIを再構築せずに再利用する"""
        self.game_id = game_data.get('id')
        self.game_title = game_data.get('title', 'Unknown Title')
        self.image_path = Path(game_data["image_path"]) if game_data.get("image_path") else None
        self.game_data = game_data
        self._validation_result = None
        self._error_indicator = False

        self.title_label.setText(self.game_title)
        
        # Reset state and set placeholder
        self.cover_art_label.setPixmap(QPixmap())
        
        if self.image_path:
            self.setProperty("image_loading", True)
            self.setProperty("no_image", False)
            if deferred:
                self.cover_art_label.setText(self.tr("..."))
            else:
                self._load_image_async()
        else:
            self.setProperty("image_loading", False)
            self.setProperty("no_image", True)
            self.cover_art_label.setText(self.tr("No Cover Art"))
        
        self.retranslateUi()
        self._update_initial_validation_status()
        self._apply_style()

    def _apply_style(self):
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()

    def load_image(self):
        """明示的に画像の読み込みを開始する"""
        if self.image_path and self.cover_art_label.pixmap().isNull():
            self._load_image_async()


    def _init_ui(self):
        self.setFixedSize(130, 220) # 全体のサイズを固定
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(5, 5, 5, 5)

        self.layout.setSpacing(5)

        # Cover Art
        self.cover_art_label = QLabel()
        self.cover_art_label.setObjectName("cover_art_label")
        self.cover_art_label.setAlignment(Qt.AlignCenter)
        self.cover_art_label.setFixedSize(120, 180)
        self.cover_art_label.setStyleSheet("border: 1px solid gray; background-color: #333;")
        self.layout.addWidget(self.cover_art_label)

        # Title
        self.title_label = QLabel()
        self.title_label.setObjectName("title_label")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.title_label)

        self.setLayout(self.layout)


    def retranslateUi(self):
        """UI文字列の翻訳を更新する"""
        if not self.image_path:
            self.cover_art_label.setText(self.tr("No Cover Art"))
        elif self.property("image_loading"):
            # Preserve loading text if still loading
            if self.cover_art_label.text() == "...":
                self.cover_art_label.setText(self.tr("..."))
            else:
                self.cover_art_label.setText(self.tr("Loading..."))
        
        # Update tooltip if error exists
        if self._validation_result and not self._validation_result.is_valid:
            self._update_error_tooltip()

    def changeEvent(self, event):
        if event.type() == QEvent.LanguageChange:
            self.retranslateUi()
        super().changeEvent(event)

    def _load_image_async(self):
        if not self.image_path:
            return

        self.setProperty("image_loading", True)
        self.cover_art_label.setText(self.tr("Loading..."))
        self._apply_style()
        
        # Request ID handling for consistency (Task 3)
        self._current_request_id = getattr(self, '_current_request_id', 0) + 1
        
        from src.image_loader import ImageLoader
        from src.image_pool import ImagePool
        
        self.image_loader = ImageLoader(
            self.image_path, 
            self.cover_art_label.size(), 
            self._current_request_id
        )
        self.image_loader.signals.image_loaded.connect(self._on_image_loaded)
        self.image_loader.signals.image_load_failed.connect(self._on_image_load_failed)
        ImagePool.get_instance().start(self.image_loader)

    def _on_image_loaded(self, image, request_id: int):
        # Validate request ID to prevent overwriting with old requests (Task 3)
        if hasattr(self, '_current_request_id') and request_id != self._current_request_id:
            return

        self.setProperty("image_loading", False)
        if not image.isNull():
            # QImage to QPixmap conversion must happen on the main thread
            pixmap = QPixmap.fromImage(image)
            self.cover_art_label.setPixmap(pixmap)
            self.cover_art_label.setText("")
            self.setProperty("no_image", False)
        else:
            self._on_image_load_failed()
        self._apply_style()

    def _on_image_load_failed(self):
        self.setProperty("image_loading", False)
        self.setProperty("no_image", True)
        self.cover_art_label.setPixmap(QPixmap())
        self.cover_art_label.setText(self.tr("No Cover Art"))
        self._apply_style()

    def mouseDoubleClickEvent(self, event):
        self.launched.emit(self.game_id)
        super().mouseDoubleClickEvent(event)

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        launch_action = menu.addAction(self.tr("Launch Game"))
        edit_action = menu.addAction(self.tr("Edit Game Details"))
        delete_action = menu.addAction(self.tr("Delete Game"))
        
        launch_action.triggered.connect(lambda: self.launched.emit(self.game_id))
        edit_action.triggered.connect(lambda: self.edited.emit(self.game_id))
        delete_action.triggered.connect(lambda: self.deleted.emit(self.game_id))

        menu.exec(event.globalPos())

    def _update_initial_validation_status(self):
        validator = ExecutableValidator()
        executable_path = self.game_data.get('executable_path', '')
        validation_result = validator.validate_executable(executable_path)
        self.update_validation_status(validation_result)

    def update_validation_status(self, validation_result: ValidationResult):
        self._validation_result = validation_result
        self._error_indicator = not validation_result.is_valid
        
        if validation_result.is_valid:
            self.setObjectName("GameCardWidget")
            self.setToolTip("")
        else:
            self.setObjectName("GameCardWidget_invalid")
            self._update_error_tooltip()
        
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()

    def _update_error_tooltip(self):
        """エラーツールチップを現在の言語で更新する"""
        if not self._validation_result:
            return
            
        tooltip = self.tr("Error: %1").replace("%1", self._validation_result.error_message)
        if self._validation_result.suggested_action:
            tooltip += "\n\n" + self.tr("Suggestion: %1").replace("%1", self._validation_result.suggested_action)
        self.setToolTip(tooltip)

    def has_error_indicator(self) -> bool:
        return self._error_indicator

    def get_error_message(self) -> str:
        if self._validation_result and not self._validation_result.is_valid:
            return self._validation_result.error_message
        return ""

    def get_validation_result(self) -> ValidationResult:
        return self._validation_result