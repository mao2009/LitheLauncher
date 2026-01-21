# tests/test_game_repository.py
import unittest
import os
import sqlite3
from unittest.mock import patch, MagicMock, call
import logging
from src.database import initialize_database # データベース初期化関数
from src.game_repository import GameRepository
from src.exceptions import GameNotFoundError # 追加

class TestGameRepository(unittest.TestCase):
    def setUp(self):
        self.db_path = "test_game_launcher.db"
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        initialize_database(self.db_path) # 各テスト前にデータベースを初期化

    def tearDown(self):
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_add_game(self):
        repo = GameRepository(self.db_path)

        game_data = {
            "title": "Test Game",
            "description": "A test game description.",
            "image_path": "/path/to/cover.jpg",
            "pre_command": "echo pre",
            "post_command": "echo post",
            "save_folder": "/path/to/save",
            "sync_enabled": 1,
            "remote_sync_path": "/remote/path"
        }
        game_id = repo.add_game(game_data)
        self.assertIsInstance(game_id, int)
        self.assertGreater(game_id, 0)

        # データベースから直接読み込み、データが正しく保存されたことを確認
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Game WHERE id = ?", (game_id,))
        saved_game = cursor.fetchone()
        conn.close()

        self.assertIsNotNone(saved_game)
        self.assertEqual(saved_game[1], game_data["title"]) # title
        self.assertEqual(saved_game[9], game_data["image_path"]) # image_path

    def test_get_game_by_id_should_return_game_data(self):
        repo = GameRepository(self.db_path)

        game_data = {
            "title": "Test Game for Get",
            "description": "Description for get test.",
            "image_path": "/path/to/get_cover.jpg",
            "pre_command": "pre_get",
            "post_command": "post_get",
            "save_folder": "/path/to/get_save",
            "sync_enabled": 1,
            "remote_sync_path": "/remote/get"
        }
        added_id = repo.add_game(game_data)

        found_game = repo.get_game(added_id)

        self.assertIsNotNone(found_game)
        self.assertEqual(found_game["id"], added_id)
        self.assertEqual(found_game["title"], game_data["title"])
        self.assertEqual(found_game["description"], game_data["description"])
        self.assertEqual(found_game["image_path"], game_data["image_path"])
        self.assertEqual(found_game["pre_command"], game_data["pre_command"])
        self.assertEqual(found_game["post_command"], game_data["post_command"])
        self.assertEqual(found_game["save_folder"], game_data["save_folder"])
        self.assertEqual(found_game["sync_enabled"], game_data["sync_enabled"])
        self.assertEqual(found_game["remote_sync_path"], game_data["remote_sync_path"])

    def test_get_non_existent_game_should_return_none(self):
        repo = GameRepository(self.db_path)
        self.assertIsNone(repo.get_game(9999))

    def test_get_all_games_should_return_all_games(self):
        repo = GameRepository(self.db_path)

        # 複数のゲームを追加
        game1_data = {"title": "Game 1"}
        game2_data = {"title": "Game 2"}
        game3_data = {"title": "Game 3"}

        repo.add_game(game1_data)
        repo.add_game(game2_data)
        repo.add_game(game3_data)

        all_games = repo.get_all_games()

        self.assertIsInstance(all_games, list)
        self.assertEqual(len(all_games), 3)
        self.assertEqual(all_games[0]["title"], "Game 1")
        self.assertEqual(all_games[1]["title"], "Game 2")
        self.assertEqual(all_games[2]["title"], "Game 3")

    def test_get_all_games_should_return_empty_list_if_no_games(self):
        repo = GameRepository(self.db_path)
        all_games = repo.get_all_games()
        self.assertIsInstance(all_games, list)
        self.assertEqual(len(all_games), 0)

    def test_update_game_should_update_existing_game(self):
        repo = GameRepository(self.db_path)

        game_data = {
            "title": "Game to Update",
            "description": "Old description.",
            "image_path": "old_path.jpg",
            "pre_command": "old_pre",
            "post_command": "old_post",
            "save_folder": "old_save",
            "sync_enabled": 0,
            "remote_sync_path": "old_remote"
        }
        added_id = repo.add_game(game_data)

        updated_data = {
            "title": "Updated Game Title",
            "description": "New description.",
            "image_path": "new_path.png",
            "pre_command": "new_pre",
            "post_command": "new_post",
            "save_folder": "new_save",
            "sync_enabled": 1,
            "remote_sync_path": "new_remote"
        }

        repo.update_game(added_id, updated_data)

        found_game = repo.get_game(added_id)

        self.assertIsNotNone(found_game)
        self.assertEqual(found_game["id"], added_id)
        self.assertEqual(found_game["title"], updated_data["title"])
        self.assertEqual(found_game["description"], updated_data["description"])
        self.assertEqual(found_game["image_path"], updated_data["image_path"])
        self.assertEqual(found_game["pre_command"], updated_data["pre_command"])
        self.assertEqual(found_game["post_command"], updated_data["post_command"])
        self.assertEqual(found_game["save_folder"], updated_data["save_folder"])
        self.assertEqual(found_game["sync_enabled"], updated_data["sync_enabled"])
        self.assertEqual(found_game["remote_sync_path"], updated_data["remote_sync_path"])
        # updated_at の比較はISOフォーマットで文字列として行われるため、datetimeオブジェクトではなく文字列として比較
        # 厳密にはupdated_atが更新された時刻に近いことを確認するが、ここでは単純に異なることを確認        
        original_game = repo.get_game(added_id) # 更新前のゲームデータを再度取得してupdated_atを確認      
        self.assertNotEqual(found_game["updated_at"], original_game["created_at"])


    def test_update_game_should_not_update_non_existent_game(self):
        repo = GameRepository(self.db_path)

        updated_data = {
            "title": "Non Existent Game Update",
            "description": "This should not be updated."
        }

        repo.update_game(9999, updated_data)

        # データベースに存在しないことを確認 (既存のテストで確認済みの get_game を使用)
        self.assertIsNone(repo.get_game(9999))

    def test_add_game_with_executable_path(self):
        repo = GameRepository(self.db_path)

        game_data = {
            "title": "Game with Executable Path",
            "executable_path": "/path/to/game.exe"
        }
        game_id = repo.add_game(game_data)

        found_game = repo.get_game(game_id)

        self.assertIsNotNone(found_game)
        self.assertEqual(found_game["title"], game_data["title"])
        self.assertEqual(found_game["executable_path"], game_data["executable_path"])

    def test_update_game_with_executable_path(self):
        repo = GameRepository(self.db_path)

        game_data = {
            "title": "Game to Update Executable Path",
            "executable_path": "/old/path/to/game.exe"
        }
        game_id = repo.add_game(game_data)

        updated_executable_path = "/new/path/to/game.exe"
        repo.update_game(game_id, {"executable_path": updated_executable_path})

        found_game = repo.get_game(game_id)

        self.assertIsNotNone(found_game)
        self.assertEqual(found_game["executable_path"], updated_executable_path)

    def test_delete_game_should_remove_existing_game(self):
        repo = GameRepository(self.db_path)

        game_data = {"title": "Game to Delete"}
        added_id = repo.add_game(game_data)

        self.assertIsNotNone(repo.get_game(added_id)) # 削除前に存在することを確認

        # RED: delete_game メソッドがまだ実装されていないため AttributeError を期待する
        repo.delete_game(added_id)

        self.assertIsNone(repo.get_game(added_id)) # 削除後に存在しないことを確認

    def test_delete_game_should_do_nothing_for_non_existent_game(self):
        repo = GameRepository(self.db_path)

        # RED: delete_game メソッドがまだ実装されていないため AttributeError を期待する
        repo.delete_game(9999) # 存在しないIDを削除

        self.assertIsNone(repo.get_game(9999)) # 存在しないことを確認

    @patch('src.game_repository.get_logger')
    def test_init_logging(self, mock_get_logger):
        # GameRepositoryのインスタンスを作成
        repo = GameRepository(self.db_path)
        # get_loggerが呼び出されたことを検証
        mock_get_logger.assert_called_once_with(
            'GameRepository',
            log_file='game_launcher.log',
            level=logging.INFO
        )

    @patch('src.game_repository.get_logger')
    def test_connect_logging_success(self, mock_get_logger):
        # ロガーインスタンスのモックを取得
        mock_logger = mock_get_logger.return_value
        repo = GameRepository(self.db_path)
        
        # _connectを呼び出し
        conn = repo._connect()
        conn.close()

        # logger.infoが呼び出されたことを検証
        mock_logger.info.assert_called_once_with("Database connection successful.")
        # logger.exceptionは呼び出されないことを検証
        mock_logger.exception.assert_not_called()

    @patch('src.game_repository.get_logger')
    @patch('src.game_repository.sqlite3.connect')
    def test_connect_logging_failure(self, mock_sqlite_connect, mock_get_logger):
        # ロガーインスタンスのモックを取得
        mock_logger = mock_get_logger.return_value
        # sqlite3.connectが例外を発生させるようにモックを設定
        mock_sqlite_connect.side_effect = sqlite3.Error("Test connection error")

        repo = GameRepository(self.db_path)
        
        # _connectを呼び出し
        with self.assertRaises(sqlite3.Error):
            repo._connect()

        # logger.exceptionが呼び出されたことを検証
        mock_logger.exception.assert_called_once_with("Failed to connect to the database.")
        # logger.infoは呼び出されないことを検証
        mock_logger.info.assert_not_called()
        # logger.warningは呼び出されないことを検証
        mock_logger.warning.assert_not_called()

    @patch('src.game_repository.get_logger')
    def test_add_game_logging_success(self, mock_get_logger):
        mock_logger = mock_get_logger.return_value
        repo = GameRepository(self.db_path)

        game_data = {
            "title": "Test Game",
            "description": "A test game description.",
            "image_path": "/path/to/cover.jpg",
            "pre_command": "echo pre",
            "post_command": "echo post",
            "save_folder": "/path/to/save",
            "sync_enabled": 1,
            "remote_sync_path": "/remote/path"
        }
        game_id = repo.add_game(game_data)

        mock_logger.info.assert_any_call(f"Game added successfully with ID: {game_id}")
        mock_logger.exception.assert_not_called()

    @patch('src.game_repository.get_logger')
    @patch('src.game_repository.sqlite3.connect')
    def test_add_game_logging_failure(self, mock_sqlite_connect, mock_get_logger):
        mock_logger = mock_get_logger.return_value
        
        # モックされた接続とカーソルを設定
        mock_conn = mock_sqlite_connect.return_value
        mock_cursor = mock_conn.cursor.return_value
        # execute_sqlが例外を発生させるように設定
        mock_cursor.execute.side_effect = sqlite3.Error("Test add game error")

        repo = GameRepository(self.db_path)

        game_data = {
            "title": "Failing Game",
            "description": "This game should fail to add."
        }
        
        with self.assertRaises(sqlite3.Error):
            repo.add_game(game_data)

        # logger.exceptionが呼び出されたことを検証
        mock_logger.exception.assert_called_once_with(f"Failed to add game: {game_data['title']}")
        # データベース接続成功のログは出力されることを検証
        mock_logger.info.assert_any_call("Database connection successful.")

    @patch('src.game_repository.get_logger')
    def test_get_game_logging_success(self, mock_get_logger):
        mock_logger = mock_get_logger.return_value
        repo = GameRepository(self.db_path)

        # テスト用のゲームを追加
        game_data = {"title": "Game for Get Logging"}
        added_id = repo.add_game(game_data)
        mock_logger.reset_mock() # add_gameでのログ呼び出しをリセット

        # get_gameを呼び出し
        found_game = repo.get_game(added_id)

        # logger.infoが呼び出されたことを検証
        mock_logger.info.assert_any_call("Database connection successful.") # _connectのログ
        mock_logger.exception.assert_not_called()

    @patch('src.game_repository.get_logger')
    def test_get_game_logging_not_found(self, mock_get_logger):
        mock_logger = mock_get_logger.return_value
        repo = GameRepository(self.db_path)
        mock_logger.reset_mock() # _connectのログ呼び出しをリセット

        # 存在しないゲームIDでget_gameを呼び出し
        found_game = repo.get_game(9999)

        # logger.warningが呼び出されたことを検証
        mock_logger.warning.assert_called_once_with("Game with ID: 9999 not found.")
        mock_logger.exception.assert_not_called()
        mock_logger.info.assert_any_call("Database connection successful.") # _connectのログ

    @patch('src.game_repository.get_logger')
    @patch('src.game_repository.GameRepository._connect') # _connectをモックする
    def test_get_game_logging_failure(self, mock_connect, mock_get_logger):
        mock_logger = mock_get_logger.return_value
        
        # _connectが正常な接続を返すように設定
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        # execute_sqlが例外を発生させるように設定
        mock_cursor.execute.side_effect = sqlite3.Error("Test get_game error")

        repo = GameRepository(self.db_path)
        
        # get_gameを呼び出し
        with self.assertRaises(sqlite3.Error):
            repo.get_game(1) # 任意のID

        # logger.exceptionが呼び出されたことを検証
        mock_logger.exception.assert_called_once_with("Failed to retrieve game with ID: 1.")
        # logger.infoは呼び出されないことを検証 (_connectのログ以外)
        self.assertNotIn(call("Successfully retrieved 0 games."), mock_logger.info.call_args_list)
        # logger.warningは呼び出されないことを検証
        mock_logger.warning.assert_not_called()

    @patch('src.game_repository.get_logger')
    def test_get_all_games_logging_success(self, mock_get_logger):
        mock_logger = mock_get_logger.return_value
        repo = GameRepository(self.db_path)

        # テスト用のゲームを追加
        repo.add_game({"title": "Game 1"})
        repo.add_game({"title": "Game 2"})
        mock_logger.reset_mock() # add_gameでのログ呼び出しをリセット

        # get_all_gamesを呼び出し
        all_games = repo.get_all_games()

        # logger.infoが呼び出されたことを検証
        mock_logger.info.assert_any_call("Database connection successful.") # _connectのログ
        mock_logger.info.assert_any_call(f"Successfully retrieved {len(all_games)} games.")
        mock_logger.exception.assert_not_called()
        mock_logger.warning.assert_not_called()

    @patch('src.game_repository.get_logger')
    @patch('src.game_repository.GameRepository._connect') # _connectをモックする
    def test_get_all_games_logging_failure(self, mock_connect, mock_get_logger):
        mock_logger = mock_get_logger.return_value
        
        # _connectが正常な接続を返すように設定
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        # execute_sqlが例外を発生させるように設定
        mock_cursor.execute.side_effect = sqlite3.Error("Test get_all_games error")

        repo = GameRepository(self.db_path)
        
        # get_all_gamesを呼び出し
        with self.assertRaises(sqlite3.Error):
            repo.get_all_games()

        # logger.exceptionが呼び出されたことを検証
        mock_logger.exception.assert_called_once_with("Failed to retrieve all games.")
        # logger.infoは呼び出されないことを検証 (_connectのログ以外)
        self.assertNotIn(call("Successfully retrieved 0 games."), mock_logger.info.call_args_list)
        self.assertNotIn(call("Successfully retrieved 2 games."), mock_logger.info.call_args_list)
        # logger.warningは呼び出されないことを検証
        mock_logger.warning.assert_not_called()

    @patch('src.game_repository.get_logger')
    def test_update_game_logging_success(self, mock_get_logger):
        mock_logger = mock_get_logger.return_value
        repo = GameRepository(self.db_path)

        # テスト用のゲームを追加
        game_data = {"title": "Game to Update"}
        added_id = repo.add_game(game_data)
        mock_logger.reset_mock() # add_gameでのログ呼び出しをリセット

        updated_data = {"title": "Updated Game"}
        repo.update_game(added_id, updated_data)

        mock_logger.info.assert_any_call("Database connection successful.") # _connectのログ
        mock_logger.info.assert_any_call(f"Game with ID: {added_id} updated successfully.")
        mock_logger.exception.assert_not_called()
        mock_logger.warning.assert_not_called()

    @patch('src.game_repository.get_logger')
    def test_update_game_logging_not_found(self, mock_get_logger):
        mock_logger = mock_get_logger.return_value
        repo = GameRepository(self.db_path)

        # 存在しないゲームIDでupdate_gameを呼び出し
        repo.update_game(9999, {"title": "Non Existent Update"})

        # logger.warningが呼び出されたことを検証
        mock_logger.warning.assert_any_call("Attempted to update non-existent game with ID: 9999.")
        mock_logger.exception.assert_not_called()
        mock_logger.info.assert_any_call("Database connection successful.") # _connectのログ

    @patch('src.game_repository.get_logger')
    @patch('src.game_repository.GameRepository._connect') # _connectをモックする
    def test_update_game_logging_failure(self, mock_connect, mock_get_logger):
        mock_logger = mock_get_logger.return_value
        
        # _connectが正常な接続を返すように設定
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        # execute_sqlが例外を発生させるように設定
        mock_cursor.execute.side_effect = sqlite3.Error("Test update_game error")

        repo = GameRepository(self.db_path)

        game_data = {"title": "Game to Update"}
        
        with self.assertRaises(sqlite3.Error):
            repo.update_game(1, game_data) # 任意のID

        # logger.exceptionが呼び出されたことを検証
        mock_logger.exception.assert_called_once_with("Failed to update game with ID: 1.")
        # logger.infoは呼び出されないことを検証 (_connectのログ以外)
        self.assertNotIn(call("Game with ID: 1 updated successfully."), mock_logger.info.call_args_list)
        # logger.warningは呼び出されないことを検証
        self.assertNotIn(call("Attempted to update non-existent game with ID: 1."), mock_logger.warning.call_args_list)

    @patch('src.game_repository.get_logger')
    def test_delete_game_logging_success(self, mock_get_logger):
        mock_logger = mock_get_logger.return_value
        repo = GameRepository(self.db_path)

        # テスト用のゲームを追加
        game_data = {"title": "Game to Delete"}
        added_id = repo.add_game(game_data)
        mock_logger.reset_mock() # add_gameでのログ呼び出しをリセット

        repo.delete_game(added_id)

        mock_logger.info.assert_any_call("Database connection successful.") # _connectのログ
        mock_logger.info.assert_any_call(f"Game with ID: {added_id} deleted successfully.")
        mock_logger.exception.assert_not_called()
        mock_logger.warning.assert_not_called()

    @patch('src.game_repository.get_logger')
    def test_delete_game_logging_not_found(self, mock_get_logger):
        mock_logger = mock_get_logger.return_value
        repo = GameRepository(self.db_path)

        # 存在しないゲームIDでdelete_gameを呼び出し
        repo.delete_game(9999)

        # logger.warningが呼び出されたことを検証
        mock_logger.warning.assert_any_call("Attempted to delete non-existent game with ID: 9999.")
        mock_logger.exception.assert_not_called()
        mock_logger.info.assert_any_call("Database connection successful.") # _connectのログ

    @patch('src.game_repository.get_logger')
    @patch('src.game_repository.GameRepository._connect') # _connectをモックする
    def test_delete_game_logging_failure(self, mock_connect, mock_get_logger):
        mock_logger = mock_get_logger.return_value
        
        # _connectが正常な接続を返すように設定
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        # execute_sqlが例外を発生させるように設定
        mock_cursor.execute.side_effect = sqlite3.Error("Test delete_game error")

        repo = GameRepository(self.db_path)
        
        # delete_gameを呼び出し
        with self.assertRaises(sqlite3.Error):
            repo.delete_game(1) # 任意のID

        # logger.exceptionが呼び出されたことを検証
        mock_logger.exception.assert_called_once_with("Failed to delete game with ID: 1.")
        # logger.infoは呼び出されないことを検証 (_connectのログ以外)
        self.assertNotIn(call("Game with ID: 1 deleted successfully."), mock_logger.info.call_args_list)
        # logger.warningは呼び出されないことを検証
        self.assertNotIn(call("Attempted to delete non-existent game with ID: 1."), mock_logger.warning.call_args_list)

    def test_game_has_image_path_attribute(self):
        repo = GameRepository(self.db_path)
        game_data = {
            "title": "Game with image path",
            "description": "Description.",
            "pre_command": "pre",
            "post_command": "post",
            "save_folder": "/path/to/save",
            "sync_enabled": 1,
            "remote_sync_path": "/remote/path",
            "image_path": "/new/image/path.png" # Test image path
        }
        game_id = repo.add_game(game_data)
        found_game = repo.get_game(game_id)
        
        self.assertIn("image_path", found_game)
        self.assertEqual(found_game["image_path"], game_data["image_path"])

    def test_add_game_without_image_path_sets_none(self):
        repo = GameRepository(self.db_path)
        game_data = {
            "title": "Game without image path"
        }
        game_id = repo.add_game(game_data)
        found_game = repo.get_game(game_id)
        
        self.assertIn("image_path", found_game)
        self.assertEqual(found_game["image_path"], "")

    def test_add_game_with_unique_identifier_field(self):
        repo = GameRepository(self.db_path)

        game_data = {
            "title": "Test Game with Unique ID",
            "unique_identifier": "test-guid-123" # 新しいフィールド
        }
        game_id = repo.add_game(game_data)
        self.assertIsInstance(game_id, int)
        self.assertGreater(game_id, 0)

        found_game = repo.get_game(game_id)
        self.assertIsNotNone(found_game)
        self.assertEqual(found_game["title"], game_data["title"])
        self.assertEqual(found_game["unique_identifier"], game_data["unique_identifier"])

    def test_get_game_by_unique_identifier_should_return_game_data(self):
        repo = GameRepository(self.db_path)

        game_data = {
            "title": "Test Game by Unique ID",
            "unique_identifier": "find-me-guid-456"
        }
        added_id = repo.add_game(game_data)

        found_game = repo.get_game_by_unique_identifier("find-me-guid-456")

        self.assertIsNotNone(found_game)
        self.assertEqual(found_game["id"], added_id)
        self.assertEqual(found_game["title"], game_data["title"])
        self.assertEqual(found_game["unique_identifier"], game_data["unique_identifier"])



    @patch('src.game_repository.get_logger')
    def test_get_game_by_unique_identifier_raises_error_if_not_found(self, mock_get_logger):
        # Arrange
        mock_logger = mock_get_logger.return_value
        repo = GameRepository(self.db_path)
        unique_id = "non-existent-guid-raises-error"

        # Act & Assert
        with self.assertRaises(GameNotFoundError):
            repo.get_game_by_unique_identifier(unique_id)
        
        mock_logger.exception.assert_not_called()
        mock_logger.warning.assert_called_once_with(f"Game with unique_identifier: {unique_id} not found.")

    def test_update_game_by_unique_identifier_should_update_existing_game(self):
        repo = GameRepository(self.db_path)

        game_data = {
            "title": "Game to Update by Unique ID",
            "unique_identifier": "update-me-guid-123"
        }
        added_id = repo.add_game(game_data)

        updated_data = {
            "title": "Updated Title by Unique ID",
            "description": "New description."
        }

        repo.update_game_by_unique_identifier("update-me-guid-123", updated_data)

        found_game = repo.get_game(added_id)

        self.assertIsNotNone(found_game)
        self.assertEqual(found_game["title"], updated_data["title"])
        self.assertEqual(found_game["description"], updated_data["description"])



    @patch('src.game_repository.get_logger')
    def test_update_game_by_unique_identifier_raises_error_if_not_found(self, mock_get_logger):
        # Arrange
        mock_logger = mock_get_logger.return_value
        repo = GameRepository(self.db_path)
        unique_id = "non-existent-guid-raises-error-update"
        update_data = {"title": "Should not update"}

        # Act & Assert
        with self.assertRaises(GameNotFoundError):
            repo.update_game_by_unique_identifier(unique_id, update_data)
        
        mock_logger.exception.assert_not_called()
        mock_logger.warning.assert_called_once_with(f"Attempted to update non-existent game with unique_identifier: {unique_id}.")

    @patch('src.game_repository.get_logger')
    def test_delete_game_by_unique_identifier_raises_error_if_not_found(self, mock_get_logger):
        # Arrange
        mock_logger = mock_get_logger.return_value
        repo = GameRepository(self.db_path)
        unique_id = "non-existent-guid-raises-error-delete"

        # Act & Assert
        with self.assertRaises(GameNotFoundError):
            repo.delete_game_by_unique_identifier(unique_id)
        
        mock_logger.exception.assert_not_called()
        mock_logger.warning.assert_called_once_with(f"Attempted to delete non-existent game with unique_identifier: {unique_id}.")

    def test_delete_game_by_unique_identifier_should_remove_existing_game(self):
        repo = GameRepository(self.db_path)

        game_data = {
            "title": "Game to Delete by Unique ID",
            "unique_identifier": "delete-me-guid-123"
        }
        added_id = repo.add_game(game_data)

        self.assertIsNotNone(repo.get_game(added_id)) # 削除前に存在することを確認
        
        repo.delete_game_by_unique_identifier("delete-me-guid-123")

        self.assertIsNone(repo.get_game(added_id)) # 削除後に存在しないことを確認

    def test_add_game_with_command_line_settings(self):
        repo = GameRepository(self.db_path)
        game_data = {
            "title": "Game with Command Line",
            "command_line_settings": "--fullscreen -resolution 1920x1080"
        }
        game_id = repo.add_game(game_data)
        found_game = repo.get_game(game_id)

        self.assertIsNotNone(found_game)
        self.assertEqual(found_game["title"], game_data["title"])
        self.assertEqual(found_game["command_line_settings"], game_data["command_line_settings"])

    def test_add_game_without_command_line_settings_defaults_to_empty(self):
        repo = GameRepository(self.db_path)
        game_data = {
            "title": "Game without Command Line"
        }
        game_id = repo.add_game(game_data)
        found_game = repo.get_game(game_id)

        self.assertIsNotNone(found_game)
        self.assertEqual(found_game["title"], game_data["title"])
        self.assertEqual(found_game["command_line_settings"], "") # デフォルトで空文字列になることを期待

    def test_update_game_updates_command_line_settings(self):
        repo = GameRepository(self.db_path)
        game_data = {
            "title": "Game to Update Cmd Line",
            "command_line_settings": "--old-settings"
        }
        game_id = repo.add_game(game_data)

        updated_settings = "--new-settings -test"
        repo.update_game(game_id, {"command_line_settings": updated_settings})

        found_game = repo.get_game(game_id)
        self.assertIsNotNone(found_game)
        self.assertEqual(found_game["command_line_settings"], updated_settings)

    def test_update_game_removes_command_line_settings_if_empty_string(self):
        repo = GameRepository(self.db_path)
        game_data = {
            "title": "Game to Remove Cmd Line",
            "command_line_settings": "--settings-to-remove"
        }
        game_id = repo.add_game(game_data)

        repo.update_game(game_id, {"command_line_settings": ""}) # 空文字列で更新

        found_game = repo.get_game(game_id)
        self.assertIsNotNone(found_game)
        self.assertEqual(found_game["command_line_settings"], "")

    def test_get_game_by_id_returns_command_line_settings(self):
        repo = GameRepository(self.db_path)
        game_data = {
            "title": "Game for Get Cmd Line",
            "command_line_settings": "-debuglog"
        }
        game_id = repo.add_game(game_data)
        found_game = repo.get_game(game_id)

        self.assertIsNotNone(found_game)
        self.assertEqual(found_game["id"], game_id)
        self.assertEqual(found_game["command_line_settings"], game_data["command_line_settings"])

    def test_get_methods_do_not_return_cover_art_path(self):
        repo = GameRepository(self.db_path)
        game_data = {
            "title": "Test Game No Cover Art Path",
            "image_path": "/path/to/image.jpg"
        }
        game_id = repo.add_game(game_data)

        # Test get_game
        found_game = repo.get_game(game_id)
        self.assertIsNotNone(found_game)
        self.assertNotIn("cover_art_path", found_game)

        # Test get_all_games
        all_games = repo.get_all_games()
        self.assertGreater(len(all_games), 0)
        self.assertNotIn("cover_art_path", all_games[0])

    def test_add_play_session(self):
        repo = GameRepository(self.db_path)
        
        # まずゲームを追加
        game_data = {"title": "Test Game for Play Session"}
        game_id = repo.add_game(game_data)

        start_time = 1678886400.0 # 2023-03-15 00:00:00 UTC
        end_time = 1678890000.0   # 2023-03-15 01:00:00 UTC
        duration = 3600.0         # 1 hour

        session_id = repo.add_play_session(game_id, start_time, end_time, duration)
        
        self.assertIsInstance(session_id, int)
        self.assertGreater(session_id, 0)

        # データベースから直接読み込み、データが正しく保存されたことを確認
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM PlaySession WHERE id = ?", (session_id,))
        saved_session = cursor.fetchone()
        conn.close()

        self.assertIsNotNone(saved_session)
        self.assertEqual(saved_session[1], game_id)       # game_id
        self.assertEqual(saved_session[2], start_time)    # start_time
        self.assertEqual(saved_session[3], end_time)      # end_time
        self.assertEqual(saved_session[4], duration)      # duration

    def test_get_total_play_time_for_game(self):
        repo = GameRepository(self.db_path)
        
        game_data = {"title": "Test Game for Total Play Time"}
        game_id = repo.add_game(game_data)

        # プレイセッションを追加
        repo.add_play_session(game_id, 1, 3601, 3600)   # 1時間
        repo.add_play_session(game_id, 2, 1802, 1800)   # 30分
        repo.add_play_session(game_id, 3, 3603, 3600) # 1時間

        total_time = repo.get_total_play_time_for_game(game_id)
        self.assertEqual(total_time, 3600 + 1800 + 3600)

    def test_get_total_play_time_for_game_no_sessions(self):
        repo = GameRepository(self.db_path)
        
        game_data = {"title": "Test Game No Sessions"}
        game_id = repo.add_game(game_data)

        total_time = repo.get_total_play_time_for_game(game_id)
        self.assertEqual(total_time, 0.0)

    def test_get_total_play_time_for_non_existent_game(self):
        repo = GameRepository(self.db_path)
        
        # 存在しないゲームID
        total_time = repo.get_total_play_time_for_game(9999)
        self.assertEqual(total_time, 0.0)

    def test_get_play_session_history_for_game(self):
        repo = GameRepository(self.db_path)
        
        game_data = {"title": "Test Game for Session History"}
        game_id = repo.add_game(game_data)

        # 複数のプレイセッションを追加 (異なる開始時刻で)
        repo.add_play_session(game_id, 1678890000.0, 1678893600.0, 3600.0) # 1時間 (後)
        repo.add_play_session(game_id, 1678886400.0, 1678890000.0, 3600.0) # 1時間 (先)
        repo.add_play_session(game_id, 1678893600.0, 1678895400.0, 1800.0) # 30分 (一番後)

        history = repo.get_play_session_history_for_game(game_id)
        
        self.assertIsInstance(history, list)
        self.assertEqual(len(history), 3)

        # start_timeでソートされていることを確認
        self.assertEqual(history[0]["start_time"], 1678886400.0)
        self.assertEqual(history[1]["start_time"], 1678890000.0)
        self.assertEqual(history[2]["start_time"], 1678893600.0)

        # 各セッションのデータが正しいことを確認
        self.assertEqual(history[0]["game_id"], game_id)
        self.assertEqual(history[0]["duration"], 3600.0)

    def test_get_play_session_history_for_game_no_sessions(self):
        repo = GameRepository(self.db_path)
        
        game_data = {"title": "Test Game No History"}
        game_id = repo.add_game(game_data)

        history = repo.get_play_session_history_for_game(game_id)
        
        self.assertIsInstance(history, list)
        self.assertEqual(len(history), 0)

    def test_get_play_session_history_for_non_existent_game(self):
        repo = GameRepository(self.db_path)
        
        history = repo.get_play_session_history_for_game(9999)
        
        self.assertIsInstance(history, list)
        self.assertEqual(len(history), 0)


    def test_delete_play_time_data_for_game(self):
        repo = GameRepository(self.db_path)
        
        game1_data = {"title": "Game 1 for Deletion"}
        game1_id = repo.add_game(game1_data)
        game2_data = {"title": "Game 2 (Should not be deleted)"}
        game2_id = repo.add_game(game2_data)

        # Game 1 に複数のプレイセッションを追加
        repo.add_play_session(game1_id, 1, 3601, 3600)
        repo.add_play_session(game1_id, 2, 1802, 1800)
        
        # Game 2 にプレイセッションを追加
        repo.add_play_session(game2_id, 3, 3603, 3600)

        # 削除前にデータが存在することを確認
        self.assertGreater(repo.get_total_play_time_for_game(game1_id), 0)
        self.assertGreater(repo.get_total_play_time_for_game(game2_id), 0)

        repo.delete_play_time_data_for_game(game1_id)

        # Game 1 のプレイ時間が0になったことを確認
        self.assertEqual(repo.get_total_play_time_for_game(game1_id), 0.0)
        self.assertEqual(len(repo.get_play_session_history_for_game(game1_id)), 0)

        # Game 2 のプレイ時間は変更されていないことを確認
        self.assertGreater(repo.get_total_play_time_for_game(game2_id), 0)
        self.assertEqual(len(repo.get_play_session_history_for_game(game2_id)), 1)


    def test_delete_play_time_data_for_non_existent_game(self):
        repo = GameRepository(self.db_path)
        
        # 存在しないゲームIDで削除を試みる
        repo.delete_play_time_data_for_game(9999)

        # エラーが発生しないことを確認（何も変更されないため、Assertionは不要だが、呼び出しが成功することを確認）
        # もし例外を出すなら、ここでassertRaisesを使う
        # 現状では何も起こらないことが期待される
        pass




