import unittest
import os
from unittest.mock import patch, MagicMock
import logging

from src.database import initialize_database
from src.game_repository import GameRepository
from src.game_service import GameService
from src.image_manager import ImageManager


class TestGameServiceImageFeature(unittest.TestCase):
    def setUp(self):
        self.db_path = "test_game_launcher_image.db"
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        initialize_database(self.db_path)
        self.repo = GameRepository(self.db_path)
        self.image_manager = MagicMock(spec=ImageManager)
        self.service = GameService(self.repo, self.image_manager)

        # Register a game for testing purposes
        self.game_data = {
            "title": "Test Game with Image",
            "description": "Description",
            "pre_command": "",
            "post_command": "",
            "save_folder": "",
            "sync_enabled": 0,
            "remote_sync_path": "",
            "executable_path": None
        }
        self.registered_game_id = self.service.register_game(self.game_data)["id"]

    def tearDown(self):
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_save_game_image_successfully_updates_game_image_path(self):
        source_image_path = Path("/source/image.png")
        expected_copied_path = Path(f"data/{self.registered_game_id}/images/image.png")
        self.image_manager.copy_image_to_appdata.return_value = expected_copied_path

        returned_path = self.service.save_game_image(self.registered_game_id, source_image_path)

        self.image_manager.copy_image_to_appdata.assert_called_once_with(
            str(self.registered_game_id), source_image_path
        )
        self.repo.update_game.assert_called_once_with(
            self.registered_game_id, {"image_path": str(expected_copied_path)}
        )
        self.assertEqual(returned_path, expected_copied_path)

        # Verify the image path is updated in the database
        updated_game = self.service.get_game_details(self.registered_game_id)
        self.assertEqual(updated_game["image_path"], str(expected_copied_path))

    def test_save_game_image_handles_image_manager_failure(self):
        source_image_path = Path("/source/image.png")
        self.image_manager.copy_image_to_appdata.side_effect = IOError("Disk full")

        with self.assertRaises(IOError):
            self.service.save_game_image(self.registered_game_id, source_image_path)

        self.image_manager.copy_image_to_appdata.assert_called_once()
        self.repo.update_game.assert_not_called() # Should not try to update if copy failed

    def test_save_game_image_handles_game_not_found(self):
        source_image_path = Path("/source/image.png")
        non_existent_game_id = 999
        with self.assertRaisesRegex(ValueError, f"Game with ID: {non_existent_game_id} not found."):
            self.service.save_game_image(non_existent_game_id, source_image_path)
        self.image_manager.copy_image_to_appdata.assert_not_called()
        self.repo.update_game.assert_not_called()

    def test_get_game_image_path_returns_correct_path(self):
        # First save an image path
        source_image_path = Path("/source/image.jpg")
        expected_copied_path = Path(f"data/{self.registered_game_id}/images/image.jpg")
        self.image_manager.copy_image_to_appdata.return_value = expected_copied_path
        self.service.save_game_image(self.registered_game_id, source_image_path)

        # Now retrieve it
        retrieved_path = self.service.get_game_image_path(self.registered_game_id)
        self.assertEqual(retrieved_path, expected_copied_path)

    def test_get_game_image_path_returns_none_if_no_image(self):
        # Game was registered without an image path initially
        retrieved_path = self.service.get_game_image_path(self.registered_game_id)
        self.assertIsNone(retrieved_path)

    def test_get_game_image_path_returns_none_for_non_existent_game(self):
        non_existent_game_id = 999
        retrieved_path = self.service.get_game_image_path(non_existent_game_id)
        self.assertIsNone(retrieved_path)

    @patch('src.game_service.get_logger')
    def test_logging_in_save_game_image(self, mock_get_logger):
        mock_logger = mock_get_logger.return_value
        source_image_path = Path("/source/log_image.png")
        expected_copied_path = Path(f"data/{self.registered_game_id}/images/log_image.png")
        self.image_manager.copy_image_to_appdata.return_value = expected_copied_path

        self.service.save_game_image(self.registered_game_id, source_image_path)
        mock_logger.info.assert_any_call(f"Attempting to save image for game ID: {self.registered_game_id} from {source_image_path}")
        mock_logger.info.assert_any_call(f"Image for game ID: {self.registered_game_id} saved successfully to {expected_copied_path}")

    @patch('src.game_service.get_logger')
    def test_logging_error_in_save_game_image(self, mock_get_logger):
        mock_logger = mock_get_logger.return_value
        source_image_path = Path("/source/log_image.png")
        self.image_manager.copy_image_to_appdata.side_effect = IOError("Permission denied")

        with self.assertRaises(IOError):
            self.service.save_game_image(self.registered_game_id, source_image_path)
        mock_logger.exception.assert_called_once_with(f"Failed to save image for game ID: {self.registered_game_id}.")

    @patch('src.game_service.get_logger')
    def test_logging_in_get_game_image_path(self, mock_get_logger):
        mock_logger = mock_get_logger.return_value
        
        # Scenario 1: Image path exists
        source_image_path = Path("/source/log_get_image.png")
        expected_copied_path = Path(f"data/{self.registered_game_id}/images/log_get_image.png")
        self.image_manager.copy_image_to_appdata.return_value = expected_copied_path
        self.service.save_game_image(self.registered_game_id, source_image_path)
        mock_logger.reset_mock() # Clear calls from save_game_image

        self.service.get_game_image_path(self.registered_game_id)
        mock_logger.info.assert_any_call(f"Attempting to get image path for game ID: {self.registered_game_id}")
        mock_logger.info.assert_any_call(f"Retrieved image path for game ID: {self.registered_game_id}: {expected_copied_path}")

        # Scenario 2: No image path
        # Assuming another game without image
        game_no_image_data = self.game_data.copy()
        game_no_image_data["title"] = "Game No Image"
        registered_game_no_image_id = self.repo.add_game(game_no_image_data)
        mock_logger.reset_mock()

        self.service.get_game_image_path(registered_game_no_image_id)
        mock_logger.info.assert_any_call(f"Attempting to get image path for game ID: {registered_game_no_image_id}")
        mock_logger.info.assert_any_call(f"No image path found for game ID: {registered_game_no_image_id}.")

    @patch('src.game_service.get_logger')
    def test_logging_error_in_get_game_image_path(self, mock_get_logger):
        mock_logger = mock_get_logger.return_value
        # Simulate an error in game_repository.get_game
        self.repo.get_game = MagicMock(side_effect=Exception("DB Error"))
        
        with self.assertRaises(Exception):
            self.service.get_game_image_path(self.registered_game_id)
        mock_logger.exception.assert_called_once_with(f"Failed to get image path for game ID: {self.registered_game_id}.")
