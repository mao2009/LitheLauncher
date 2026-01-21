import unittest
import os
import logging
import re
import time
from unittest.mock import MagicMock, patch

from src.game_launcher_logger import get_logger

class TestGameLauncherLogger(unittest.TestCase):
    def setUp(self):
        # 各テストのロガー名をユニークにする
        self.logger_name = f"test_logger_{time.time()}" 
        self.log_file = f"{self.logger_name}.log"

        # 念のため、前回のテストで残ったファイルがあれば削除
        if os.path.exists(self.log_file):
            os.remove(self.log_file)
        
        # テスト間でロガーの状態が混じらないように、loggingモジュール全体をリセット
        logging.shutdown()
        # rootロガーのハンドラをクリア (影響を受けないようにするため)
        logging.root.handlers = []

    def tearDown(self):
        # 各テスト後にログファイルを削除
        if os.path.exists(self.log_file):
            os.remove(self.log_file)
        
        # 'other_logger_*.log' ファイルを削除
        for file in os.listdir('.'):
            if file.startswith("other_logger_") and file.endswith(".log"):
                os.remove(file)
        
        # loggingモジュール全体をシャットダウンし、すべてのハンドラをクローズ
        logging.shutdown()
        # rootロガーのハンドラをクリア (念のため)
        logging.root.handlers = []

    # 各テストメソッド内でロガーを取得した後、そのロガーのハンドラをクローズするヘルパー関数
    def _close_logger_handlers(self, logger):
        for handler in logger.handlers[:]:
            handler.close()
            logger.removeHandler(handler)
        logger.handlers = []

    def test_logger_creation_and_info_logging(self):
        logger = get_logger(self.logger_name, self.log_file)
        self.assertIsInstance(logger, logging.Logger)
        self.assertEqual(logger.name, self.logger_name)
        self.assertTrue(logger.hasHandlers())

        test_message = "This is an info message."
        logger.info(test_message)

        with open(self.log_file, 'r') as f:
            log_content = f.read()
        self.assertIn(test_message, log_content)
        self.assertIn("INFO", log_content)
        self._close_logger_handlers(logger) # ハンドラをクローズ

    def test_logger_error_logging(self):
        logger = get_logger(self.logger_name, self.log_file)
        self.assertTrue(logger.hasHandlers())

        test_error_message = "This is an error message."
        logger.error(test_error_message)

        with open(self.log_file, 'r') as f:
            log_content = f.read()
        self.assertIn(test_error_message, log_content)
        self.assertIn("ERROR", log_content)
        self._close_logger_handlers(logger) # ハンドラをクローズ

    @patch('logging.StreamHandler')
    @patch('logging.FileHandler')
    def test_logger_with_console_output(self, MockFileHandler, MockStreamHandler):
        logger = get_logger(self.logger_name, self.log_file, console_output=True)
        self.assertIsInstance(logger, logging.Logger)
        self.assertEqual(logger.name, self.logger_name)
        
        MockFileHandler.assert_called_once()
        MockStreamHandler.assert_called_once()
        
        self.assertEqual(len(logger.handlers), 2)
        self._close_logger_handlers(logger) # ハンドラをクローズ

    @patch('logging.StreamHandler')
    @patch('logging.FileHandler')
    def test_logger_without_console_output(self, MockFileHandler, MockStreamHandler):
        logger = get_logger(self.logger_name, self.log_file, console_output=False)
        self.assertIsInstance(logger, logging.Logger)
        self.assertEqual(logger.name, self.logger_name)

        MockFileHandler.assert_called_once()
        MockStreamHandler.assert_not_called()

        self.assertEqual(len(logger.handlers), 1)
        self._close_logger_handlers(logger) # ハンドラをクローズ

    def test_logger_formatter_includes_timestamp_level_name_message(self):
        logger = get_logger(self.logger_name, self.log_file)
        
        file_handler = next(h for h in logger.handlers if isinstance(h, logging.FileHandler))
        formatter = file_handler.formatter
        
        test_message = "Formatted log test."
        logger.info(test_message)
        
        with open(self.log_file, 'r') as f:
            log_content = f.read()
        
        pattern = r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3} - " + re.escape(self.logger_name) + r" - INFO - " + re.escape(test_message)
        self.assertRegex(log_content, pattern)
        self._close_logger_handlers(logger) # ハンドラをクローズ

    def test_logger_level_filtering(self):
        logger = get_logger(self.logger_name, self.log_file, level=logging.WARNING)
        
        logger.info("This info message should not be logged.")
        logger.warning("This warning message should be logged.")
        
        with open(self.log_file, 'r') as f:
            log_content = f.read()
        
        self.assertNotIn("This info message should not be logged.", log_content)
        self.assertIn("This warning message should be logged.", log_content)
        self._close_logger_handlers(logger) # ハンドラをクローズ

    @patch('logging.FileHandler')
    def test_file_handler_error_reporting(self, MockFileHandler):
        # FileHandler の constructor が例外を発生させるようにモック
        MockFileHandler.side_effect = IOError("Permission denied")

        # get_logger が呼ばれたときに、エラーが適切にハンドリングされるか
        # get_logger内で例外が捕捉されない場合、get_logger呼び出し自体が失敗する
        with self.assertRaises(IOError):
            get_logger(self.logger_name, self.log_file)
        
        # モックされたFileHandlerが呼ばれたことを確認
        MockFileHandler.assert_called_once()


    def test_get_logger_does_not_add_duplicate_handlers(self):
        logger1 = get_logger(self.logger_name, self.log_file)
        self.assertEqual(len(logger1.handlers), 2)

        logger2 = get_logger(self.logger_name, self.log_file)
        self.assertEqual(len(logger2.handlers), 2)
        self.assertEqual(logger1, logger2)

        other_logger_name = f"other_logger_{time.time()}"
        other_log_file = f"{other_logger_name}.log"
        other_logger = get_logger(other_logger_name, other_log_file)
        self.assertEqual(len(other_logger.handlers), 2)
        self.assertNotEqual(logger1, other_logger)
        
        self._close_logger_handlers(logger1) # logger1のハンドラをクローズ
        self._close_logger_handlers(other_logger) # other_loggerのハンドラをクローズ
        
        # other_log_fileはtearDownで削除されるため、ここでは削除しない