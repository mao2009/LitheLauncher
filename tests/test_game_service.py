# tests/test_game_service.py
import unittest
import os
from unittest.mock import patch, MagicMock, call
import logging
from database import initialize_database
from game_repository import GameRepository
from game_service import GameService
import subprocess
from exceptions import GameNotFoundError
from pathlib import Path
import uuid # 追加

class TestGameService(unittest.TestCase):
    def setUp(self):
        self.db_path = "test_game_launcher.db"
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        initialize_database(self.db_path)
        self.repo = GameRepository(self.db_path)

    def tearDown(self):
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_register_game(self):
        service = GameService(self.repo, MagicMock())

        game_data = {
            "title": "New Game",
            "description": "New game description.",
            "pre_command": "echo new_pre",
            "post_command": "echo new_post",
            "save_folder": "/path/to/new_save",
            "sync_enabled": 1,
            "remote_sync_path": "/remote/new",
            "executable_path": None  # Set to None to avoid validation
        }
        registered_game = service.register_game(game_data)
        
        self.assertIsNotNone(registered_game)
        self.assertIn("id", registered_game)
        self.assertEqual(registered_game["title"], game_data["title"])
        self.assertEqual(registered_game["executable_path"], game_data["executable_path"])

        found_game = self.repo.get_game(registered_game["id"])
        self.assertIsNotNone(found_game)
        self.assertEqual(found_game["title"], game_data["title"])
        self.assertEqual(found_game["executable_path"], game_data["executable_path"])

    def test_get_game_details(self):
        service = GameService(self.repo, MagicMock())

        game_data = {
            "title": "Game to Get Details",
            "description": "Details description.",
            "pre_command": "pre_details",
            "post_command": "post_details",
            "save_folder": "/path/to/details_save",
            "sync_enabled": 1,
            "remote_sync_path": "/remote/details"
        }
        registered_game = service.register_game(game_data)
        game_id = registered_game["id"]

        found_game = service.get_game_details(game_id)
        self.assertIsNotNone(found_game)
        self.assertEqual(found_game["id"], game_id)
        self.assertEqual(found_game["title"], game_data["title"])

    def test_get_game_details_non_existent(self):
        service = GameService(self.repo, MagicMock())
        found_game = service.get_game_details(9999)
        self.assertIsNone(found_game)

    @patch('uuid.uuid4')
    @patch('game_repository.GameRepository')
    def test_get_game_details_generates_and_persists_unique_identifier(self, MockGameRepository, mock_uuid4):
        # Arrange
        mock_uuid_instance = MagicMock()
        mock_uuid_instance.hex = "generated-guid-12345"
        mock_uuid4.return_value = mock_uuid_instance

        # Mock GameRepository methods
        mock_repo_instance = MockGameRepository.return_value
        
        # unique_identifier が None のゲームデータを返すようにモック
        game_id = 1
        game_data_without_uuid = {
            "id": game_id,
            "title": "Game without UUID",
            "unique_identifier": None, # ここが重要
            "created_at": "2023-01-01T00:00:00",
            "updated_at": "2023-01-01T00:00:00"
        }
        mock_repo_instance.get_game.return_value = game_data_without_uuid
        mock_repo_instance.get_total_play_time_for_game.return_value = 0.0 # 追加

        
        # update_game のモック
        mock_repo_instance.update_game.return_value = None

        service = GameService(mock_repo_instance, MagicMock())

        # Act
        found_game = service.get_game_details(game_id)

        # Assert
        mock_uuid4.assert_called_once() # uuid.uuid4 が呼ばれること
        mock_repo_instance.get_game.assert_called_once_with(game_id) # get_game が呼ばれること
        mock_repo_instance.update_game.assert_called_once_with(
            game_id, {"unique_identifier": "generated-guid-12345"}
        ) # update_game が呼ばれ、unique_identifier が更新されること

        self.assertIsNotNone(found_game)
        self.assertEqual(found_game["id"], game_id)
        self.assertEqual(found_game["unique_identifier"], "generated-guid-12345") # 割り当てられた unique_identifier が返されること


    def test_get_game_list(self):
        service = GameService(self.repo, MagicMock())

        game1_data = {"title": "Game A", "description": "", "pre_command": "", "post_command": "", "save_folder": "", "sync_enabled": 0, "remote_sync_path": "", "executable_path": ""}
        game2_data = {"title": "Game B", "description": "", "pre_command": "", "post_command": "", "save_folder": "", "sync_enabled": 0, "remote_sync_path": "", "executable_path": ""}
        
        service.register_game(game1_data)
        service.register_game(game2_data)

        game_list = service.get_game_list()
        self.assertIsInstance(game_list, list)
        self.assertEqual(len(game_list), 2)
        self.assertEqual(game_list[0]["title"], "Game A")
        self.assertEqual(game_list[1]["title"], "Game B")

    def test_get_game_list_empty(self):
        service = GameService(self.repo, MagicMock())
        game_list = service.get_game_list()
        self.assertIsInstance(game_list, list)
        self.assertEqual(len(game_list), 0)

    @patch('uuid.uuid4')
    @patch('game_repository.GameRepository')
    def test_get_game_list_generates_and_persists_unique_identifier(self, MockGameRepository, mock_uuid4):
        # Arrange
        mock_uuid_instance_1 = MagicMock()
        mock_uuid_instance_1.hex = "generated-guid-list-1"
        mock_uuid_instance_2 = MagicMock()
        mock_uuid_instance_2.hex = "generated-guid-list-2"
        mock_uuid4.side_effect = [mock_uuid_instance_1, mock_uuid_instance_2]

        mock_repo_instance = MockGameRepository.return_value

        # unique_identifier が None のゲームデータを2つ返すようにモック
        game_data_1 = {
            "id": 1,
            "title": "Game 1 without UUID",
            "unique_identifier": None,
            "created_at": "2023-01-01T00:00:00",
            "updated_at": "2023-01-01T00:00:00"
        }
        game_data_2 = {
            "id": 2,
            "title": "Game 2 without UUID",
            "unique_identifier": None,
            "created_at": "2023-01-01T00:00:00",
            "updated_at": "2023-01-01T00:00:00"
        }
        mock_repo_instance.get_all_games.return_value = [game_data_1, game_data_2]
        mock_repo_instance.update_game.return_value = None # update_game のモック

        service = GameService(mock_repo_instance, MagicMock())

        # Act
        game_list = service.get_game_list()

        # Assert
        self.assertEqual(mock_uuid4.call_count, 2) # uuid.uuid4 が2回呼ばれること
        mock_repo_instance.get_all_games.assert_called_once() # get_all_games が呼ばれること
        
        # update_game が正しい引数で2回呼ばれること
        expected_calls = [
            call(1, {"unique_identifier": "generated-guid-list-1"}),
            call(2, {"unique_identifier": "generated-guid-list-2"})
        ]
        mock_repo_instance.update_game.assert_has_calls(expected_calls, any_order=True)

        self.assertEqual(len(game_list), 2)
        self.assertEqual(game_list[0]["unique_identifier"], "generated-guid-list-1")
        self.assertEqual(game_list[1]["unique_identifier"], "generated-guid-list-2")

    def test_update_game_details(self):
        service = GameService(self.repo, MagicMock())

        game_data = {
            "title": "Original Title",
            "description": "Original description.",
            "pre_command": "original_pre",
            "post_command": "original_post",
            "save_folder": "original_save",
            "sync_enabled": 0,
            "remote_sync_path": "original_remote",
            "executable_path": None  # Set to None to avoid validation
        }
        registered_game = service.register_game(game_data)
        game_id = registered_game["id"]

        updated_fields = {
            "title": "Updated Title",
            "description": "Updated description.",
            "sync_enabled": 1,
            "executable_path": None  # Set to None to avoid validation
        }

        updated_game = service.update_game_details(game_id, updated_fields)
        self.assertIsNotNone(updated_game)
        self.assertEqual(updated_game["id"], game_id)
        self.assertEqual(updated_game["title"], updated_fields["title"])
        self.assertEqual(updated_game["description"], updated_fields["description"])
        self.assertEqual(updated_game["sync_enabled"], updated_fields["sync_enabled"])
        self.assertEqual(updated_game["executable_path"], updated_fields["executable_path"])
        # 他のフィールドは変更されていないことを確認

    def test_update_game_details_non_existent(self):
        service = GameService(self.repo, MagicMock())
        updated_fields = {"title": "Should not update"}
        with self.assertRaises(GameNotFoundError):
            service.update_game_details(9999, updated_fields)

    @patch('game_repository.GameRepository')
    def test_get_game_by_unique_identifier(self, MockGameRepository):
        # Arrange
        mock_repo_instance = MockGameRepository.return_value
        unique_id = "test-unique-id-123"
        expected_game_data = {
            "id": 1,
            "title": "Game by Unique ID",
            "unique_identifier": unique_id,
            "created_at": "2023-01-01T00:00:00",
            "updated_at": "2023-01-01T00:00:00"
        }
        mock_repo_instance.get_game_by_unique_identifier.return_value = expected_game_data

        service = GameService(mock_repo_instance, MagicMock())

        # Act
        found_game = service.get_game_by_unique_identifier(unique_id)

        # Assert
        mock_repo_instance.get_game_by_unique_identifier.assert_called_once_with(unique_id)
        self.assertIsNotNone(found_game)
        self.assertEqual(found_game, expected_game_data)

    @patch('game_repository.GameRepository')
    def test_get_game_by_unique_identifier_not_found(self, MockGameRepository):
        # Arrange
        mock_repo_instance = MockGameRepository.return_value
        unique_id = "non-existent-unique-id"
        mock_repo_instance.get_game_by_unique_identifier.return_value = None

        service = GameService(mock_repo_instance, MagicMock())

        # Act & Assert
        with self.assertRaises(GameNotFoundError):
            service.get_game_by_unique_identifier(unique_id)

        mock_repo_instance.get_game_by_unique_identifier.assert_called_once_with(unique_id)



    @patch('game_repository.GameRepository')
    def test_update_game_by_unique_identifier(self, MockGameRepository):
        # Arrange
        mock_repo_instance = MockGameRepository.return_value
        unique_id = "update-game-guid-123"
        update_data = {"title": "Updated Title by GUID", "description": "New Description"}
        
        # update_game_by_unique_identifier が成功した場合の get_game_by_unique_identifier の戻り値
        updated_game_from_repo = {
            "id": 1,
            "title": update_data["title"],
            "description": update_data["description"],
            "unique_identifier": unique_id,
            "created_at": "2023-01-01T00:00:00",
            "updated_at": "2023-01-01T00:00:00"
        }
        mock_repo_instance.update_game_by_unique_identifier.return_value = None # 返り値がないのでNone
        mock_repo_instance.get_game_by_unique_identifier.return_value = updated_game_from_repo

        service = GameService(mock_repo_instance, MagicMock())

        # Act
        updated_game = service.update_game_by_unique_identifier(unique_id, update_data)

        # Assert
        mock_repo_instance.update_game_by_unique_identifier.assert_called_once_with(unique_id, update_data)
        self.assertEqual(mock_repo_instance.get_game_by_unique_identifier.call_count, 2) # 更新前と更新後に計2回呼ばれることを検証
        mock_repo_instance.get_game_by_unique_identifier.assert_called_with(unique_id) # 更新後に再取得されることを検証
        self.assertIsNotNone(updated_game)
        self.assertEqual(updated_game["title"], update_data["title"])
        self.assertEqual(updated_game["description"], update_data["description"])
        self.assertEqual(updated_game["unique_identifier"], unique_id)

    @patch('game_repository.GameRepository')
    def test_update_game_by_unique_identifier_non_existent(self, MockGameRepository):
        # Arrange
        mock_repo_instance = MockGameRepository.return_value
        unique_id = "non-existent-guid"
        update_data = {"title": "Should not update"}
        
        # get_game_by_unique_identifier がゲームを見つけないようにモック
        mock_repo_instance.get_game_by_unique_identifier.return_value = None

        service = GameService(mock_repo_instance, MagicMock())

        # Act & Assert
        with self.assertRaises(GameNotFoundError):
            service.update_game_by_unique_identifier(unique_id, update_data)

        mock_repo_instance.get_game_by_unique_identifier.assert_called_once_with(unique_id)
        mock_repo_instance.update_game_by_unique_identifier.assert_not_called()
        mock_repo_instance.get_game_by_unique_identifier.assert_called_once_with(unique_id)

    @patch('game_repository.GameRepository')
    def test_update_game_by_unique_identifier_raises_error_if_non_existent(self, MockGameRepository):
        # Arrange
        mock_repo_instance = MockGameRepository.return_value
        unique_id = "non-existent-guid"
        update_data = {"title": "Should not update"}
        
        mock_repo_instance.get_game_by_unique_identifier.return_value = None # 存在しないことをシミュレート

        service = GameService(mock_repo_instance, MagicMock())

        # Act & Assert
        with self.assertRaises(GameNotFoundError):
            service.update_game_by_unique_identifier(unique_id, update_data)

        mock_repo_instance.get_game_by_unique_identifier.assert_called_once_with(unique_id)
        mock_repo_instance.update_game_by_unique_identifier.assert_not_called()


    @patch('game_repository.GameRepository')
    def test_delete_game_by_unique_identifier(self, MockGameRepository):
        # Arrange
        mock_repo_instance = MockGameRepository.return_value
        unique_id = "delete-game-guid-123"
        
        # get_game_by_unique_identifier がゲームを見つけるようにモック
        mock_repo_instance.get_game_by_unique_identifier.return_value = {
            "id": 1,
            "title": "Game to Delete",
            "unique_identifier": unique_id
        }
        mock_repo_instance.delete_game_by_unique_identifier.return_value = None

        service = GameService(mock_repo_instance, MagicMock())

        # Act
        service.delete_game_by_unique_identifier(unique_id)

        # Assert
        mock_repo_instance.get_game_by_unique_identifier.assert_called_once_with(unique_id) # 削除前にゲームが存在するか確認
        mock_repo_instance.delete_game_by_unique_identifier.assert_called_once_with(unique_id)


    @patch('game_repository.GameRepository')
    def test_delete_game_by_unique_identifier_non_existent(self, MockGameRepository):
        # Arrange
        mock_repo_instance = MockGameRepository.return_value
        unique_id = "non-existent-delete-guid"
        
        # get_game_by_unique_identifier がゲームを見つけないようにモック
        mock_repo_instance.get_game_by_unique_identifier.return_value = None
        mock_repo_instance.delete_game_by_unique_identifier.return_value = None

        service = GameService(mock_repo_instance, MagicMock())

        # Act & Assert
        with self.assertRaises(GameNotFoundError):
            service.delete_game_by_unique_identifier(unique_id)

        mock_repo_instance.get_game_by_unique_identifier.assert_called_once_with(unique_id) # 削除前にゲームが存在するか確認
        mock_repo_instance.delete_game_by_unique_identifier.assert_not_called() # 存在しない場合は削除が呼ばれない

    @patch('game_repository.GameRepository')
    def test_delete_game_by_unique_identifier_raises_error_if_non_existent(self, MockGameRepository):
        # Arrange
        mock_repo_instance = MockGameRepository.return_value
        unique_id = "non-existent-delete-guid"
        
        mock_repo_instance.get_game_by_unique_identifier.return_value = None # 存在しないことをシミュレート

        service = GameService(mock_repo_instance, MagicMock())

        # Act & Assert
        with self.assertRaises(GameNotFoundError):
            service.delete_game_by_unique_identifier(unique_id)

        mock_repo_instance.get_game_by_unique_identifier.assert_called_once_with(unique_id)
        mock_repo_instance.delete_game_by_unique_identifier.assert_not_called()

    @patch('game_service.get_logger')
    def test_logger_initialization(self, mock_get_logger):
        # GameServiceのインスタンスを作成
        service = GameService(self.repo, MagicMock())
        # get_loggerが呼び出されたことを検証
        mock_get_logger.assert_called_once_with(
            'GameService', 
            log_file='game_launcher.log', 
            level=logging.INFO
        )

    @patch('image_manager.ImageManager')  # ImageManagerを先にモック
    @patch('game_repository.GameRepository') # GameRepositoryを後にモック
    @patch('executable_validator.ExecutableValidator') # ExecutableValidatorを最後にモック
    def test_save_game_image(self, MockExecutableValidator, MockImageManager, MockGameRepository): # 引数の順序に合わせて修正
        
        # ExecutableValidatorのモックインスタンス
        mock_executable_validator_instance = MockExecutableValidator.return_value
        mock_executable_validator_instance.validate_executable.return_value = MagicMock(is_valid=True)

        # GameRepositoryのモックインスタンス
        mock_game_repository_instance = MockGameRepository.return_value
        # get_game メソッドの戻り値を設定 (update_gameの動作確認用)
        mock_game_repository_instance.get_game.return_value = {
            "id": 1,
            "title": "Test Game for Image",
            "executable_path": None, # ここをNoneに設定
            "image_path": "/appdata/test_game_1/images/new_image.png" # 更新後のパス
        }
        mock_game_repository_instance.add_game.return_value = 1 # register_gameで利用
        mock_game_repository_instance.get_total_play_time_for_game.return_value = 0.0 # 追加


        # ImageManagerのモックインスタンス
        mock_image_manager_instance = MockImageManager.return_value

        service = GameService(mock_game_repository_instance, image_manager=mock_image_manager_instance) # モックを注入

        
        mock_image_manager_instance.move_image_from_temp_to_game_data.return_value = Path("/appdata/test_game_1/images/new_image.png")

        # テスト用のゲームを登録
        game_data = {
            "title": "Test Game for Image",
            "description": "",
            "pre_command": "",
            "post_command": "",
            "save_folder": "",
            "sync_enabled": 0,
            "remote_sync_path": "",
            "executable_path": None # ここをNoneに設定
        }
        # register_game は GameService のメソッドであり、内部で mock_game_repository_instance.add_game を呼び出す
        registered_game_id = service.register_game(game_data)["id"]

        source_image_path = Path("/source/image.png")
        
        # save_game_image を呼び出す
        saved_image_path = service.save_game_image(registered_game_id, source_image_path)
        
        # ImageManager.move_image_from_temp_to_game_data が正しく呼び出されたことを確認
        mock_image_manager_instance.move_image_from_temp_to_game_data.assert_called_once_with(
            source_image_path, str(registered_game_id)
        )
        
        # GameRepository.update_game が正しく呼び出されたことを確認
        # updated_at は変化するため、image_pathのみを確認
        expected_update_data = {"image_path": str(mock_image_manager_instance.move_image_from_temp_to_game_data.return_value)}
        mock_game_repository_instance.update_game.assert_called_once_with(registered_game_id, expected_update_data)
        
        # 戻り値が正しいことを確認
        self.assertEqual(saved_image_path, mock_image_manager_instance.move_image_from_temp_to_game_data.return_value)
        
        # データベース上のゲームデータが更新されていることを確認 (モックのget_gameで確認)
        updated_game_in_db = service.get_game_details(registered_game_id) # service.get_game_detailsはget_gameを呼び出す
        self.assertEqual(Path(updated_game_in_db["image_path"]), saved_image_path)

    @patch('image_manager.ImageManager')
    def test_register_game_with_command_line_settings(self, MockImageManager):
        service = GameService(self.repo, MagicMock()) # MockImageManager を渡す

        game_data = {
            "title": "Game with Cmd Line",
            "command_line_settings": "--fullscreen -res 1920x1080",
            "executable_path": None # 検証をスキップ
        }
        registered_game = service.register_game(game_data) # **game_data を修正

        self.assertIsNotNone(registered_game)
        self.assertEqual(registered_game["title"], game_data["title"])
        self.assertEqual(registered_game["command_line_settings"], game_data["command_line_settings"])

        found_game = self.repo.get_game(registered_game["id"])
        self.assertEqual(found_game["command_line_settings"], game_data["command_line_settings"])

    @patch('image_manager.ImageManager')
    def test_register_game_without_command_line_settings_defaults_to_empty(self, MockImageManager):
        service = GameService(self.repo, MagicMock()) # MockImageManager を渡す

        game_data = {
            "title": "Game without Cmd Line",
            "executable_path": None # 検証をスキップ
        }
        registered_game = service.register_game(game_data) # **game_data を修正

        self.assertIsNotNone(registered_game)
        self.assertEqual(registered_game["command_line_settings"], "")

        found_game = self.repo.get_game(registered_game["id"])
        self.assertEqual(found_game["command_line_settings"], "")

    @patch('image_manager.ImageManager')
    def test_update_game_details_updates_command_line_settings(self, MockImageManager):
        service = GameService(self.repo, MagicMock()) # MockImageManager を渡す

        game_data = {
            "title": "Game to Update Cmd Line",
            "command_line_settings": "--old-settings",
            "executable_path": None # 検証をスキップ
        }
        registered_game = service.register_game(game_data) # **game_data を修正
        game_id = registered_game["id"]

        updated_settings = "--new-settings -test"
        updated_game = service.update_game_details(game_id, {"command_line_settings": updated_settings})

        self.assertIsNotNone(updated_game)
        self.assertEqual(updated_game["command_line_settings"], updated_settings)

        found_game = self.repo.get_game(game_id)
        self.assertEqual(found_game["command_line_settings"], updated_settings)

    @patch('image_manager.ImageManager')
    def test_update_game_details_removes_command_line_settings_if_empty_string(self, MockImageManager):
        service = GameService(self.repo, MagicMock()) # MockImageManager を渡す

        game_data = {
            "title": "Game to Remove Cmd Line",
            "command_line_settings": "--settings-to-remove",
            "executable_path": None # 検証をスキップ
        }
        registered_game = service.register_game(game_data) # **game_data を修正
        game_id = registered_game["id"]

        updated_game = service.update_game_details(game_id, {"command_line_settings": ""})

        self.assertIsNotNone(updated_game)
        self.assertEqual(updated_game["command_line_settings"], "")

        self.assertEqual(updated_game["command_line_settings"], "")

    @patch('game_repository.GameRepository')
    def test_finalize_play_session(self, MockGameRepository):
        # Arrange
        mock_repo_instance = MockGameRepository.return_value
        mock_repo_instance.add_play_session.return_value = 1 # 成功時の戻り値

        service = GameService(mock_repo_instance, MagicMock())
        game_id = 1
        start_time = 1672531200.0 # Jan 1, 2023 00:00:00 UTC
        end_time = 1672534800.0   # Jan 1, 2023 01:00:00 UTC
        duration = 3600.0

        # Act
        service.finalize_play_session(game_id, start_time, end_time, duration)

        # Assert
        mock_repo_instance.add_play_session.assert_called_once_with(game_id, start_time, end_time, duration)

    @patch('game_repository.GameRepository')
    def test_finalize_play_session_handles_repository_error(self, MockGameRepository):
        # Arrange
        mock_repo_instance = MockGameRepository.return_value
        mock_repo_instance.add_play_session.side_effect = Exception("DB error")

        service = GameService(mock_repo_instance, MagicMock())
        game_id = 1
        start_time = 1672531200.0
        end_time = 1672534800.0
        duration = 3600.0

        # Act & Assert
        with self.assertRaises(Exception): # GameService内で例外を再throwすることを確認
            service.finalize_play_session(game_id, start_time, end_time, duration)

        mock_repo_instance.add_play_session.assert_called_once_with(game_id, start_time, end_time, duration)

    @patch('game_repository.GameRepository')
    def test_get_total_play_time(self, MockGameRepository):
        # Arrange
        mock_repo_instance = MockGameRepository.return_value
        mock_repo_instance.get_total_play_time_for_game.return_value = 7200.0 # 2時間

        service = GameService(mock_repo_instance, MagicMock())
        game_id = 1

        # Act
        total_time = service.get_total_play_time(game_id)

        # Assert
        mock_repo_instance.get_total_play_time_for_game.assert_called_once_with(game_id)
        self.assertEqual(total_time, 7200.0)

    @patch('game_repository.GameRepository')
    def test_get_total_play_time_for_non_existent_game_returns_zero(self, MockGameRepository):
        # Arrange
        mock_repo_instance = MockGameRepository.return_value
        mock_repo_instance.get_total_play_time_for_game.return_value = 0.0

        service = GameService(mock_repo_instance, MagicMock())
        game_id = 999

        # Act
        total_time = service.get_total_play_time(game_id)

        # Assert
        mock_repo_instance.get_total_play_time_for_game.assert_called_once_with(game_id)
        self.assertEqual(total_time, 0.0)

    @patch('game_repository.GameRepository')
    def test_get_play_session_history(self, MockGameRepository):
        # Arrange
        mock_repo_instance = MockGameRepository.return_value
        expected_history = [
            {"start_time": 1672531200.0, "end_time": 1672534800.0, "duration": 3600.0},
            {"start_time": 1672534800.0, "end_time": 1672536600.0, "duration": 1800.0},
        ]
        mock_repo_instance.get_play_session_history_for_game.return_value = expected_history

        service = GameService(mock_repo_instance, MagicMock())
        game_id = 1

        # Act
        history = service.get_play_session_history(game_id)

        # Assert
        mock_repo_instance.get_play_session_history_for_game.assert_called_once_with(game_id)
        self.assertEqual(history, expected_history)

    @patch('game_repository.GameRepository')
    def test_get_play_session_history_for_game_with_no_sessions_returns_empty_list(self, MockGameRepository):
        # Arrange
        mock_repo_instance = MockGameRepository.return_value
        mock_repo_instance.get_play_session_history_for_game.return_value = []

        service = GameService(mock_repo_instance, MagicMock())
        game_id = 1

        # Act
        history = service.get_play_session_history(game_id)

        # Assert
        mock_repo_instance.get_play_session_history_for_game.assert_called_once_with(game_id)
        self.assertEqual(history, [])

    @patch('game_repository.GameRepository')
    def test_remove_game_also_deletes_play_time_data(self, MockGameRepository):
        # Arrange
        mock_repo_instance = MockGameRepository.return_value
        game_id = 1
        
        # remove_game内でget_gameが呼ばれるので、モックする
        mock_repo_instance.get_game.return_value = {"id": game_id, "title": "Game to remove"}

        service = GameService(mock_repo_instance, MagicMock())

        # Act
        service.remove_game(game_id)

        # Assert
        mock_repo_instance.delete_game.assert_called_once_with(game_id)
        mock_repo_instance.delete_play_time_data_for_game.assert_called_once_with(game_id)