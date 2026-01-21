import pytest
import shutil
import time
import os
from pathlib import Path
from unittest.mock import MagicMock, patch

from src.launcher_service import LauncherService
from src.game_service import GameService
from src.remote_storage_service import RemoteStorageService
from src.exceptions import GameNotFoundError, CommandExecutionError, SaveDataSyncError, ExecutableValidationError

@pytest.fixture
def mock_game_service():
    return MagicMock(spec=GameService)

@pytest.fixture
def mock_remote_storage_service():
    return MagicMock(spec=RemoteStorageService)

@pytest.fixture
def launcher_service(mock_game_service, mock_remote_storage_service):
    return LauncherService(mock_game_service, mock_remote_storage_service)

@pytest.fixture
def setup_sync_test_dirs(tmp_path):
    local_save_folder = tmp_path / "local_save"
    local_save_folder.mkdir()
    (local_save_folder / "existing_file.txt").write_text("existing_local_data")
    return local_save_folder

class TestLauncherService:
    def test_launch_game_tracks_play_time(self, launcher_service, mock_game_service, mocker):
        game_id = 1
        executable_path = "/path/to/game.exe"
        game_title = "Test Game"

        mock_game_service.get_game_details.return_value = {
            "id": game_id,
            "executable_path": executable_path,
            "title": game_title,
            "command_line_settings": "",
            "sync_enabled": False,
            "remote_sync_path": "",
            "save_folder": ""
        }
        mock_game_service.finalize_play_session.return_value = None

        # Mock subprocess.Popen
        mock_process = MagicMock()
        mock_process.wait.return_value = 0 # Simulate game exiting normally
        mock_process.returncode = 0 # Explicitly set returncode
        mock_process.communicate.return_value = ("", "") # Mock communicate to return empty stdout/stderr
        mocker.patch('subprocess.Popen', return_value=mock_process)
        mocker.patch('time.time', side_effect=[100.0, 110.0]) # Simulate start and end time

        mock_validation_result = MagicMock()
        mock_validation_result.is_valid = True
        mocker.patch.object(launcher_service.executable_validator, 'validate_executable', return_value=mock_validation_result)

        launcher_service.launch_game(game_id)

        mock_game_service.finalize_play_session.assert_called_once()
        args, kwargs = mock_game_service.finalize_play_session.call_args
        assert args[0] == game_id
        assert args[1] == 100.0 # start_time
        assert args[2] == 110.0 # end_time
        assert args[3] == 10.0  # duration

    def test_on_launcher_shutdown_finalizes_active_sessions(self, launcher_service, mock_game_service, mocker):
        game_id = 1
        executable_path = "/path/to/game.exe"
        game_title = "Test Game"

        # Mock subprocess.Popen so the process appears to be running initially
        mock_process = MagicMock()
        mock_process.poll.side_effect = [None, 0] # Simulate process running, then terminating
        mock_process.terminate.return_value = None
        mock_process.wait.return_value = 0 # Simulate it eventually terminates
        mock_process.returncode = 0
        mock_process.communicate.return_value = ("", "")
        mocker.patch('subprocess.Popen', return_value=mock_process)
        
        # Simulate time progression for start and end
        mocker.patch('time.time', return_value=110.0) # Only need the end_time for the shutdown

        # Directly add a mock active session, simulating a game that was launched
        launcher_service._active_play_sessions[game_id] = {
            "process": mock_process,
            "start_time": 100.0 # Use the first time.time() value as start_time
        }
        
        mock_game_service.finalize_play_session.reset_mock() # Ensure this is clean

        launcher_service._on_launcher_shutdown()

        # Assertions
        mock_process.terminate.assert_called_once() # Should try to terminate the running process
        mock_process.wait.assert_called_once_with(timeout=5) # Should wait for graceful termination

        mock_game_service.finalize_play_session.assert_called_once()
        args, kwargs = mock_game_service.finalize_play_session.call_args
        assert args[0] == game_id
        assert args[1] == 100.0 # start_time
        assert args[2] == 110.0 # end_time (from time.time() side_effect)
        assert args[3] == 10.0  # duration (110 - 100)
        assert not launcher_service._active_play_sessions # Should be empty after shutdown

    def test_sync_save_data_download_fail_restores_backup(
        self, launcher_service, mock_game_service, mock_remote_storage_service, mocker, setup_sync_test_dirs
    ):
        game_id = 1
        local_save_folder = setup_sync_test_dirs
        remote_sync_path = "mock_remote_path"

        mock_game_service.get_game_details.return_value = {
            "game_id": game_id,
            "sync_enabled": True,
            "remote_sync_path": remote_sync_path,
            "save_folder": str(local_save_folder),
            "title": "Test Game"
        }

        mock_remote_storage_service.download_save_data.side_effect = SaveDataSyncError(game_id, "download", Exception("Mocked download error"))

        mocker.patch('shutil.copytree')
        mocker.patch('shutil.rmtree')
        mocker.patch('pathlib.Path.mkdir')
        mocker.patch('pathlib.Path.exists', return_value=True)

        with pytest.raises(SaveDataSyncError):
            launcher_service.sync_save_data(game_id, "download")

        assert shutil.copytree.call_count == 2
        assert shutil.rmtree.call_count == 2
    
    def test_sync_save_data_download_success_deletes_backup(
        self, launcher_service, mock_game_service, mock_remote_storage_service, mocker, setup_sync_test_dirs
    ):
        game_id = 1
        local_save_folder = setup_sync_test_dirs
        remote_sync_path = "mock_remote_path"

        mock_game_service.get_game_details.return_value = {
            "game_id": game_id,
            "sync_enabled": True,
            "remote_sync_path": remote_sync_path,
            "save_folder": str(local_save_folder),
            "title": "Test Game"
        }

        mock_remote_storage_service.download_save_data.return_value = True

        mocker.patch('shutil.copytree')
        mocker.patch('shutil.rmtree')
        mocker.patch('pathlib.Path.mkdir')
        mocker.patch('pathlib.Path.exists', return_value=True)

        result = launcher_service.sync_save_data(game_id, "download")

        assert result is True
        shutil.copytree.assert_called_once()
        shutil.rmtree.assert_called_once()
    
    def test_sync_save_data_smart_remote_newer(self, launcher_service, mock_game_service, mock_remote_storage_service, mocker):
        game_id = 1
        mock_game_service.get_game_details.return_value = {
            "game_id": game_id,
            "sync_enabled": True,
            "remote_sync_path": "remote",
            "save_folder": "local",
            "title": "Test"
        }
        
        mock_remote_storage_service.get_latest_mtime.side_effect = [1000.0, 2000.0]
        mock_remote_storage_service.download_save_data.return_value = True
        
        mocker.patch('pathlib.Path.exists', return_value=True)
        mocker.patch('shutil.copytree')
        mocker.patch('shutil.rmtree')

        result = launcher_service.sync_save_data(game_id, "smart")
        
        assert result is True
        mock_remote_storage_service.download_save_data.assert_called_once()
        mock_remote_storage_service.upload_save_data.assert_not_called()

    def test_sync_save_data_smart_local_newer(self, launcher_service, mock_game_service, mock_remote_storage_service, mocker):
        game_id = 1
        mock_game_service.get_game_details.return_value = {
            "game_id": game_id,
            "sync_enabled": True,
            "remote_sync_path": "remote",
            "save_folder": "local",
            "title": "Test"
        }
        
        mock_remote_storage_service.get_latest_mtime.side_effect = [2000.0, 1000.0]
        
        mocker.patch('pathlib.Path.exists', return_value=True)
        mocker.patch('shutil.copytree')
        mocker.patch('shutil.rmtree')
        mocker.patch.object(launcher_service, '_show_sync_conflict_dialog', return_value="local")

        result = launcher_service.sync_save_data(game_id, "smart")
        
        launcher_service._show_sync_conflict_dialog.assert_called_once()
        mock_remote_storage_service.upload_save_data.assert_called_once()
        assert result is True

    def test_sync_save_data_smart_local_newer_user_chooses_remote(self, launcher_service, mock_game_service, mock_remote_storage_service, mocker):
        game_id = 1
        mock_game_service.get_game_details.return_value = {
            "game_id": game_id,
            "sync_enabled": True,
            "remote_sync_path": "remote",
            "save_folder": "local",
            "title": "Test Remote Choice"
        }
        
        # Local (2000.0) > Remote (1000.0)
        mock_remote_storage_service.get_latest_mtime.side_effect = [2000.0, 1000.0]
        mock_remote_storage_service.download_save_data.return_value = True
        
        mocker.patch('pathlib.Path.exists', return_value=True)
        mocker.patch('shutil.copytree')
        mocker.patch('shutil.rmtree')
        mocker.patch.object(launcher_service, '_show_sync_conflict_dialog', return_value="remote")

        result = launcher_service.sync_save_data(game_id, "smart")
        
        # Should call dialog and then proceed to download
        launcher_service._show_sync_conflict_dialog.assert_called_once()
        mock_remote_storage_service.download_save_data.assert_called_once()
        mock_remote_storage_service.upload_save_data.assert_not_called()
        assert result is True

    def test_sync_save_data_smart_local_newer_user_cancels(self, launcher_service, mock_game_service, mock_remote_storage_service, mocker):
        game_id = 1
        mock_game_service.get_game_details.return_value = {
            "game_id": game_id,
            "sync_enabled": True,
            "remote_sync_path": "remote",
            "save_folder": "local",
            "title": "Test Cancel Choice"
        }
        
        # Local (2000.0) > Remote (1000.0)
        mock_remote_storage_service.get_latest_mtime.side_effect = [2000.0, 1000.0]
        
        mocker.patch('pathlib.Path.exists', return_value=True)
        mocker.patch.object(launcher_service, '_show_sync_conflict_dialog', return_value="cancel")

        result = launcher_service.sync_save_data(game_id, "smart")
        
        # Should call dialog and then return False (cancel)
        launcher_service._show_sync_conflict_dialog.assert_called_once()
        mock_remote_storage_service.download_save_data.assert_not_called()
        mock_remote_storage_service.upload_save_data.assert_not_called()
        assert result is False


    def test_sync_save_data_smart_same_time(self, launcher_service, mock_game_service, mock_remote_storage_service, mocker):
        game_id = 1
        mock_game_service.get_game_details.return_value = {
            "game_id": game_id,
            "sync_enabled": True,
            "remote_sync_path": "remote",
            "save_folder": "local",
            "title": "Test"
        }
        
        mock_remote_storage_service.get_latest_mtime.return_value = 1000.0
        mocker.patch('pathlib.Path.exists', return_value=True)

        result = launcher_service.sync_save_data(game_id, "smart")
        
        assert result is True
        mock_remote_storage_service.download_save_data.assert_not_called()
        mock_remote_storage_service.upload_save_data.assert_not_called()

    def test_sync_save_data_smart_conflict_future_date(self, launcher_service, mock_game_service, mock_remote_storage_service, mocker):
        game_id = 1
        mock_game_service.get_game_details.return_value = {
            "game_id": game_id,
            "sync_enabled": True,
            "remote_sync_path": "remote",
            "save_folder": "local",
            "title": "Test"
        }
        
        future_time = time.time() + 86400
        mock_remote_storage_service.get_latest_mtime.side_effect = [1000.0, future_time]
        
        mocker.patch('pathlib.Path.exists', return_value=True)
        mocker.patch.object(launcher_service, '_show_sync_conflict_dialog', return_value="cancel")

        result = launcher_service.sync_save_data(game_id, "smart")
        
        launcher_service._show_sync_conflict_dialog.assert_called_once()

    def test_show_sync_conflict_dialog_local_newer_message(self, launcher_service, mocker):
        # We need to test the actual UI component or its configuration
        # Since QMessageBox.exec() blocks, we mock it
        mock_msg_box = mocker.patch('src.launcher_service.QMessageBox')
        instance = mock_msg_box.return_value
        
        # Mock buttons
        local_btn = MagicMock()
        remote_btn = MagicMock()
        cancel_btn = MagicMock()
        instance.addButton.side_effect = [local_btn, remote_btn, cancel_btn]
        
        # Simulate clicking local button
        instance.clickedButton.return_value = local_btn
        
        local_time = 1735113600.0  # 2024-12-25 08:00:00
        remote_time = 1735027200.0 # 2024-12-24 08:00:00
        
        result = launcher_service._show_sync_conflict_dialog("Test Game", local_time, remote_time)
        
        assert result == "local"
        # Verify message contains specific info
        args, _ = instance.setText.call_args
        assert "ローカルのセーブデータがリモートより新しい" in args[0]

    def test_sync_save_data_smart_timestamp_near_equal(self, launcher_service, mock_game_service, mock_remote_storage_service, mocker):
        game_id = 1
        mock_game_service.get_game_details.return_value = {
            "game_id": game_id,
            "sync_enabled": True,
            "remote_sync_path": "remote",
            "save_folder": "local",
            "title": "Test"
        }
        
        # Difference < 1.0s (e.g., 0.5s)
        mock_remote_storage_service.get_latest_mtime.side_effect = [1000.0, 1000.5]
        mocker.patch('pathlib.Path.exists', return_value=True)

        result = launcher_service.sync_save_data(game_id, "smart")
        
        assert result is True
        mock_remote_storage_service.download_save_data.assert_not_called()
        mock_remote_storage_service.upload_save_data.assert_not_called()

    def test_sync_save_data_smart_no_remote_data_uses_upload(self, launcher_service, mock_game_service, mock_remote_storage_service, mocker):
        game_id = 1
        mock_game_service.get_game_details.return_value = {
            "game_id": game_id,
            "sync_enabled": True,
            "remote_sync_path": "remote",
            "save_folder": "local",
            "title": "Test"
        }
        
        # Local exists (1000.0), Remote is 0.0 -> Local is newer -> Show Dialog
        mock_remote_storage_service.get_latest_mtime.side_effect = [1000.0, 0.0]
        mocker.patch('pathlib.Path.exists', return_value=True)
        mocker.patch.object(launcher_service, '_show_sync_conflict_dialog', return_value="local")

        result = launcher_service.sync_save_data(game_id, "smart")
        
        launcher_service._show_sync_conflict_dialog.assert_called_once()
        mock_remote_storage_service.upload_save_data.assert_called_once()
        assert result is True

    def test_show_sync_conflict_dialog_future_date_message(self, launcher_service, mocker):
        mock_msg_box = mocker.patch('src.launcher_service.QMessageBox')
        instance = mock_msg_box.return_value
        
        local_btn = MagicMock()
        remote_btn = MagicMock()
        cancel_btn = MagicMock()
        instance.addButton.side_effect = [local_btn, remote_btn, cancel_btn]
        instance.clickedButton.return_value = cancel_btn
        
        # Current time is around 1700000000
        future_time = time.time() + 100000
        
        launcher_service._show_sync_conflict_dialog("Test Game", future_time, 1000.0)
        
        args, _ = instance.setText.call_args
        assert "未来のタイムスタンプが検出されました" in args[0]
        