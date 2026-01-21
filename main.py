# main.py
import sys
import os
from pathlib import Path
import ctypes # AppUserModelIDを設定するために必要

# PyInstallerでバンドルされた環境でのリソースパス解決
def resource_path(relative_path):
    """
    Get absolute path to resource, works for dev and PyInstaller
    """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# AppUserModelIDを定義 (アプリケーションに合わせて変更してください)
myappid = 'LitheLauncher.GameLauncher.1.0' 

# GUIが表示される前にAppUserModelIDを設定
# Windowsでのみ実行
if sys.platform == 'win32':
    try:
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    except AttributeError:
        # Windows XPなど、この関数が存在しない古いOSの場合
        pass

from PySide6.QtWidgets import QApplication
from src.main_window import MainWindow
from src.game_service import GameService
from src.game_repository import GameRepository
from src.launcher_service import LauncherService
from src.game_launcher_logger import get_logger
from src.remote_storage_service import RemoteStorageService
from src.database import initialize_database
from src.image_manager import ImageManager
from src.language_service import LanguageService

import time

def main():
    start_time = time.perf_counter()
    # データのディレクトリとログファイルの初期化
    data_dir = "data"
    os.makedirs(resource_path(data_dir), exist_ok=True)
    log_file_path = os.path.join(resource_path(data_dir), "game_launcher.log")
    
    logger = get_logger("game_launcher_app", log_file_path, console_output=True)
    logger.info("Game Launcher application starting...")

    # QApplication インスタンスの作成
    app = QApplication(sys.argv)
    qapp_time = time.perf_counter()
    logger.info(f"QApplication created in {qapp_time - start_time:.4f}s")

    # 言語管理サービスの初期化
    language_service = LanguageService()
    
    # データベースの初期化とGameRepositoryの作成
    db_path = os.path.join(resource_path(data_dir), "game_launcher.db")
    initialize_database(db_path)
    game_repository = GameRepository(db_path)
    
    # ImageManagerの作成
    image_manager = ImageManager()
    
    # GameService の作成
    game_service = GameService(game_repository, image_manager)
    service_time = time.perf_counter()
    logger.info(f"Services initialized in {service_time - qapp_time:.4f}s")

    # RemoteStorageService の初期化
    remote_storage_service = RemoteStorageService()

    # LauncherService の作成
    launcher_service = LauncherService(game_service, remote_storage_service)

    # QSSスタイルシートの読み込み
    qss_file_path = resource_path(os.path.join("res", "style.qss"))
    try:
        with open(qss_file_path, "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())
    except Exception as e:
        logger.warning(f"QSS load failed: {e}")

    # メインウィンドウの作成と表示
    main_window = MainWindow(game_service, launcher_service, language_service)
    window_create_time = time.perf_counter()
    logger.info(f"MainWindow created in {window_create_time - service_time:.4f}s")
    
    main_window.show()
    total_time = time.perf_counter()
    logger.info(f"Total startup time: {total_time - start_time:.4f}s")

    # ログを強制的に書き出す
    for handler in logger.handlers:
        handler.flush()

    # アプリケーションの実行
    sys.exit(app.exec())

if __name__ == "__main__":
    main()