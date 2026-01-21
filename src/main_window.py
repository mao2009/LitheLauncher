# src/main_window.py
import logging
import sys # sys を追加
import os # os を追加
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QDialog, QScrollArea, QHBoxLayout, QMessageBox, QMenu
from PySide6.QtCore import Qt, Signal, Slot, QEvent, QThreadPool, QTimer
from PySide6.QtGui import QAction, QIcon, QPixmap
import time
from pathlib import Path
from src.game_detail_dialog import GameDetailDialog
from src.exceptions import GameNotFoundError, CommandExecutionError, SaveDataSyncError
from src.game_launcher_logger import get_logger
from src.flow_layout import FlowLayout
from src.game_card_widget import GameCardWidget
from src.game_list_worker import GameListWorker
from src.game_list_controller import GameListController


# PyInstallerでバンドルされた環境でのリソースパス解決
def resource_path(relative_path):
    """
    Get absolute path to resource, works for dev and PyInstaller
    """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


class MainWindow(QMainWindow):
    def __init__(self, game_service, launcher_service, language_service):
        super().__init__()
        self.game_service = game_service
        self.launcher_service = launcher_service
        self.language_service = language_service
        self.setGeometry(100, 100, 800, 600)
        self.logger = get_logger(__name__, "game_launcher.log")
        self._set_app_icon() # アイコン設定メソッドを呼び出し
        
        # LauncherService のステータス通知をセットアップ
        self.launcher_service.set_status_callback(self._update_status_message)
        
        self.controller = GameListController()
        self.controller.set_widget_factory(self._create_game_card)
        
        # スクロール停止検知用タイマー
        self.scroll_stop_timer = QTimer()
        self.scroll_stop_timer.setSingleShot(True)
        self.scroll_stop_timer.setInterval(150) # 150ms 停止でロード開始
        self.scroll_stop_timer.timeout.connect(self._on_scroll_settled)
        
        self._last_scroll_time = 0
        self._last_scroll_value = 0
        
        self._create_ui()
        self.retranslateUi()
        self._load_games_async()

    def _create_game_card(self):
        # プレースホルダーで作成し、Controllerが後でupdate_dataする
        card = GameCardWidget({"id": 0, "title": ""}, parent=self.container_widget)
        card.launched.connect(self._launch_game_action)
        card.edited.connect(self._open_edit_game_dialog)
        card.deleted.connect(self._delete_game)
        return card


    def _update_status_message(self, message: str):
        if hasattr(self, 'status_bar'):
            self.status_bar.showMessage(message)
        self.logger.info(f"UI Status Update: {message}")

    def _set_app_icon(self):
        icon_file_path = resource_path(os.path.join("res", "icon.png"))
        if Path(icon_file_path).exists():
            try:
                pixmap = QPixmap(icon_file_path)
                app_icon = QIcon(pixmap)
                self.setWindowIcon(app_icon)
                self.logger.info(f"Application icon set from {icon_file_path}")
            except Exception as e:
                self.logger.warning(f"Failed to load application icon from {icon_file_path}: {e}")
        else:
            self.logger.warning(f"Application icon file not found at {icon_file_path}. Using default icon.")

    def _create_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.container_widget = QWidget()
        self.scroll_area.setWidget(self.container_widget)

        main_layout.addWidget(self.scroll_area)

        # スクロール位置の変化を監視
        self.scroll_area.verticalScrollBar().valueChanged.connect(self._on_scroll)
        
        # リサイズ時に表示範囲を更新
        self.scroll_area.viewport().installEventFilter(self)

        self.status_bar = self.statusBar()


        self.status_bar.showMessage(self.tr("Ready"))

        self.menu_bar = self.menuBar()
        
        self.library_menu = QMenu(self)
        self.library_menu.setObjectName("libraryMenu")
        self.menu_bar.addMenu(self.library_menu)

        self.add_game_action = QAction(self)
        self.library_menu.addAction(self.add_game_action)
        self.add_game_action.triggered.connect(self._open_add_game_dialog)

        self.settings_menu = QMenu(self)
        self.settings_menu.setObjectName("settingsMenu")
        self.menu_bar.addMenu(self.settings_menu)

        self.language_menu = QMenu(self)
        self.language_menu.setObjectName("languageMenu")
        self.settings_menu.addMenu(self.language_menu)
        self._populate_language_menu()

    def _populate_language_menu(self):
        self.language_menu.clear()
        languages = self.language_service.get_available_languages()
        current_locale = self.language_service.settings.value("language", "system")

        for lang in languages:
            action = QAction(lang["name"], self)
            action.setCheckable(True)
            if lang["code"] == current_locale:
                action.setChecked(True)
            
            action.triggered.connect(lambda checked, code=lang["code"]: self._change_language(code))
            self.language_menu.addAction(action)

    def _change_language(self, locale_code: str):
        if self.language_service.change_language(locale_code):
            self._populate_language_menu()

    def retranslateUi(self):
        self.setWindowTitle(self.tr("LitheLauncher"))
        self.add_game_action.setText(self.tr("Add Game"))

    def changeEvent(self, event):
        if event.type() == QEvent.LanguageChange:
            self.retranslateUi()
        super().changeEvent(event)

    def eventFilter(self, source, event):
        if source is self.scroll_area.viewport() and event.type() == QEvent.Resize:
            self._update_controller_dimensions()
            self._on_scroll()
        return super().eventFilter(source, event)


    def _update_controller_dimensions(self):
        # GameCardWidget is fixed at 130x220
        self.controller.set_dimensions(
            viewport_width=self.scroll_area.viewport().width(),
            viewport_height=self.scroll_area.viewport().height(),
            item_width=130,
            item_height=220,
            spacing=10,
            margins=(10, 10, 10, 10)
        )

        total_height = self.controller.get_total_height()
        self.container_widget.setMinimumHeight(total_height)
        self.container_widget.setMaximumHeight(total_height)

    def _on_scroll_settled(self):
        """スクロールが停止した際に画像を読み込む"""
        self.controller.load_visible_images()

    def _on_scroll(self):
        current_time = time.time()
        current_value = self.scroll_area.verticalScrollBar().value()
        
        dt = current_time - self._last_scroll_time
        dv = abs(current_value - self._last_scroll_value)
        
        # 速度計算 (pixels/sec)
        speed = dv / dt if dt > 0 else 0
        
        # 高速スクロール中（1500px/s以上）は画像のロードを遅延させる
        is_fast_scrolling = speed > 1500
        
        self.controller.update_view(current_value, deferred=is_fast_scrolling)
        
        if is_fast_scrolling:
            self.scroll_stop_timer.start()
        else:
            # 低速スクロール時はタイマーを止めて即時ロードを優先しても良いが、
            # 念のためタイマーが走っているなら再始動させる（完全に止まった時の保険）
            if self.scroll_stop_timer.isActive():
                self.scroll_stop_timer.start()
            else:
                self.controller.load_visible_images()

        self._last_scroll_time = current_time
        self._last_scroll_value = current_value

    def _load_games_async(self):
        self.status_bar.showMessage(self.tr("Loading games..."))
        worker = GameListWorker(self.game_service)
        worker.signals.total_determined.connect(self._on_total_determined)
        worker.signals.data_chunk_loaded.connect(self._on_chunk_loaded)
        worker.signals.finished.connect(self._on_loading_finished)
        worker.signals.load_failed.connect(self._on_games_load_failed)
        QThreadPool.globalInstance().start(worker)

    @Slot(int)
    def _on_total_determined(self, total):
        self.controller.set_total_items(total)
        self._update_controller_dimensions()
        # 初期の空の状態でもスクロールバーなどを確定させるために一度呼ぶ
        self._on_scroll()

    @Slot(list, int)
    def _on_chunk_loaded(self, chunk, offset):
        self.controller.update_data_chunk(chunk, offset)
        # 現在の表示範囲に含まれる可能性があるため、ビューを更新
        self._on_scroll()

    @Slot()
    def _on_loading_finished(self):
        self.status_bar.showMessage(self.tr("Ready"))

    @Slot(list)
    def _on_games_loaded(self, games):
        # 互換性のために残すが、基本的には使われない
        self.controller.set_data(games)
        self._update_controller_dimensions()
        self._on_scroll()
        self.status_bar.showMessage(self.tr("Ready"))

    @Slot(str)
    def _on_games_load_failed(self, error_message):
        self.logger.error(f"Failed to load games: {error_message}")
        self.status_bar.showMessage(self.tr("Failed to load games."))
        QMessageBox.critical(self, self.tr("Error"), self.tr("Failed to load games: %1").replace("%1", error_message))

    def _load_games(self):
        # 互換性のために残すが、基本は非同期を使う
        self._load_games_async()


    @Slot()
    def _open_add_game_dialog(self):
        dialog = GameDetailDialog(self.game_service, self.game_service.image_manager, self.launcher_service)
        if dialog.exec() == QDialog.Accepted:
            self.logger.info(f"Game registration dialog accepted.")
            self._load_games()

    @Slot(int)
    def _open_edit_game_dialog(self, game_id: int):
        dialog = GameDetailDialog(self.game_service, self.game_service.image_manager, self.launcher_service, game_id=game_id)
        if dialog.exec() == QDialog.Accepted:
            self.logger.info(f"Game edit dialog for ID {game_id} accepted.")
            self._load_games()

    @Slot(int)
    def _delete_game(self, game_id: int):
        reply = QMessageBox.question(self, self.tr("Delete Game"), self.tr("Are you sure you want to delete game ID %1?").replace("%1", str(game_id)),
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            try:
                self.game_service.remove_game(game_id)
                self.logger.info(f"Game ID {game_id} deleted.")
                self._load_games()
            except Exception as e:
                self.logger.exception(f"Error deleting game ID {game_id}.")
                QMessageBox.critical(self, self.tr("Error"), self.tr("Failed to delete game: %1").replace("%1", str(e)))

    @Slot(int)
    def _launch_game_action(self, game_id: int):
        try:
            self.launcher_service.launch_game(game_id)
            self.logger.info(f"Game ID {game_id} launched.")
        except GameNotFoundError as e:
            self.logger.error(f"Game launch error: {e}")
            QMessageBox.critical(self, self.tr("Error"), self.tr("Game launch error: %1").replace("%1", str(e)))
        except CommandExecutionError as e:
            self.logger.error(f"Command execution error: {e}")
            error_message = self.tr("Command execution error: %1").replace("%1", str(e))
            if "WinError 740" in str(e):
                error_message = self.tr("Administrator privileges are required to launch this game. Please restart Game Launcher as an administrator.")
            QMessageBox.critical(self, self.tr("Error"), error_message)
        except SaveDataSyncError as e:
            self.logger.error(f"Save data sync error: {e}")
            QMessageBox.critical(self, self.tr("Error"), self.tr("Save data sync error: %1").replace("%1", str(e)))
        except Exception as e:
            self.logger.exception(f"Unexpected error launching game ID {game_id}.")
            QMessageBox.critical(self, self.tr("Error"), self.tr("An unexpected error occurred: %1").replace("%1", str(e)))
