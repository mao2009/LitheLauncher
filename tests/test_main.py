import unittest
import os
import sys
import logging
import subprocess
from unittest.mock import patch, MagicMock, call # Import call

# sys.path にプロジェクトルートを追加
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class TestMainFunction(unittest.TestCase):
    def setUp(self):
        # 各テストでロガーがクリーンな状態であることを保証するため、ハンドラをクリアする
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)
        logging.basicConfig(level=logging.INFO) # デフォルトレベルを設定
        self.mock_logger_instance = MagicMock(spec=logging.Logger)

    # tearDown は QApplication をクリーンアップしないため不要。pytest-qt の qapp フィクスチャ等を使う場合は必要。

    @patch('main.get_logger')
    @patch('main.QApplication')
    @patch('main.MainWindow')
    @patch('main.GameService')
    @patch('main.GameRepository')
    @patch('main.LauncherService')
    @patch('main.RemoteStorageService')
    @patch('main.initialize_database')
    @patch('main.os.makedirs')
    @patch('sys.exit')
    def test_main_initializes_logger_with_correct_args(self, mock_sys_exit, mock_os_makedirs, mock_initialize_database, mock_RemoteStorageService, mock_LauncherService, mock_GameRepository, mock_GameService, mock_MainWindow, mock_QApplication, mock_get_logger):
        mock_get_logger.return_value = self.mock_logger_instance
        mock_QApplication.return_value.exec.return_value = 0

        from main import main # Move import inside test
        main()

        mock_get_logger.assert_called_once_with("game_launcher_app", os.path.join("data", "game_launcher.log"), console_output=True)
        # ログメッセージが2つあるため、has_calls を使用
        self.mock_logger_instance.info.assert_has_calls([
            call("Game Launcher application started."),
            call(f"QSSスタイルシート '{os.path.join('res', 'style.qss')}' を適用しました。")
        ], any_order=True)
        mock_sys_exit.assert_called_once_with(0)

    @patch('main.get_logger')
    @patch('main.QApplication')
    @patch('main.MainWindow')
    @patch('main.GameService')
    @patch('main.GameRepository')
    @patch('main.LauncherService')
    @patch('main.RemoteStorageService')
    @patch('main.ImageManager')
    @patch('main.initialize_database')
    @patch('main.os.makedirs')
    @patch('sys.exit')
    def test_main_initializes_database_and_services(self, mock_sys_exit, mock_os_makedirs, mock_initialize_database, mock_ImageManager, mock_RemoteStorageService, mock_LauncherService, mock_GameRepository, mock_GameService, mock_MainWindow, mock_QApplication, mock_get_logger):
        mock_get_logger.return_value = self.mock_logger_instance
        mock_QApplication.return_value.exec.return_value = 0

        from main import main # Move import inside test
        main()
        # os.makedirs が "data" と "res" の両方で呼ばれることを確認
        mock_os_makedirs.assert_has_calls([call(os.path.join("data"), exist_ok=True), call(os.path.join("res"), exist_ok=True)], any_order=True)
        mock_initialize_database.assert_called_once_with(os.path.join("data", "game_launcher.db"))
        mock_GameRepository.assert_called_once_with(os.path.join("data", "game_launcher.db"))
        mock_GameService.assert_called_once_with(mock_GameRepository.return_value, mock_ImageManager.return_value) # image_manager のモックを渡す
        mock_RemoteStorageService.assert_called_once()
        mock_LauncherService.assert_called_once_with(mock_GameService.return_value, mock_RemoteStorageService.return_value)
        mock_QApplication.assert_called_once_with(sys.argv)
        mock_MainWindow.assert_called_once_with(mock_GameService.return_value, mock_LauncherService.return_value)
        mock_MainWindow.return_value.show.assert_called_once()
        mock_QApplication.return_value.exec.assert_called_once()
        mock_sys_exit.assert_called_once_with(0)

    @patch('main.get_logger')
    @patch('main.QApplication')
    @patch('main.MainWindow')
    @patch('main.GameService')
    @patch('main.GameRepository')
    @patch('main.LauncherService')
    @patch('main.RemoteStorageService')
    @patch('main.initialize_database')
    @patch('main.os.makedirs')
    @patch('sys.exit')
    @patch('builtins.open', new_callable=MagicMock) # Mock builtins.open
    @patch('os.path.exists', return_value=True) # Mock os.path.exists for style.qss
    def test_main_loads_qss_stylesheet(self, mock_os_path_exists, mock_open, mock_sys_exit, mock_os_makedirs, mock_initialize_database, mock_RemoteStorageService, mock_LauncherService, mock_GameRepository, mock_GameService, mock_MainWindow, mock_QApplication, mock_get_logger):
        mock_get_logger.return_value = self.mock_logger_instance
        mock_QApplication.return_value.exec.return_value = 0

        # Configure mock_open to return QSS content
        mock_file = MagicMock()
        mock_file.read.return_value = "GameCardWidget { background-color: #333; }"
        mock_open.return_value.__enter__.return_value = mock_file

        from main import main # Move import inside test
        main()

        # Assert that style.qss was opened and its content was set as stylesheet
        # os.path.exists は明示的に呼ばれないので、open の呼び出しをチェック
        mock_open.assert_called_with(os.path.join("res", "style.qss"), "r", encoding="utf-8") # Correct path and encoding
        mock_QApplication.return_value.setStyleSheet.assert_called_once_with("GameCardWidget { background-color: #333; }")

        main_window = mock_MainWindow.return_value
        main_window.show.assert_called_once()
        mock_QApplication.return_value.exec.assert_called_once()
        mock_sys_exit.assert_called_once_with(0)

    # test_application_startup_logging はコメントアウトされたまま
