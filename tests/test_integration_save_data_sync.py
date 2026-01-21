import pytest
import logging
import shutil
import os
from unittest.mock import MagicMock, patch
from pathlib import Path
from PySide6.QtWidgets import QDialog, QLineEdit, QPushButton, QCheckBox

from src.database import initialize_database
from src.game_repository import GameRepository
from src.game_service import GameService
from src.launcher_service import LauncherService
from src.image_manager import ImageManager
from src.remote_storage_service import RemoteStorageService
from src.exceptions import SaveDataSyncError

@pytest.fixture(scope="function")
def test_db_path(tmp_path):
    db_path = tmp_path / "test_game_launcher.db"
    initialize_database(str(db_path))
    return db_path

@pytest.fixture(scope="function")
def game_repository(test_db_path):
    return GameRepository(str(test_db_path))

@pytest.fixture(scope="function")
def image_manager(tmp_path):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    temp_images_dir = data_dir / "temp_images"
    temp_images_dir.mkdir()
    return ImageManager(str(data_dir))

@pytest.fixture(scope="function")
def remote_storage_service_mock():
    mock = MagicMock(spec=RemoteStorageService)
    mock.get_latest_mtime.return_value = 0.0
    return mock

@pytest.fixture(scope="function")
def game_service(game_repository, image_manager):
    with patch('src.game_service.ExecutableValidator') as MockExecutableValidator:
        mock_validator_instance = MockExecutableValidator.return_value
        mock_validator_instance.validate_executable.return_value = MagicMock(is_valid=True, error_message="", suggested_action="")
        service = GameService(game_repository, image_manager)
        service.executable_validator = mock_validator_instance
        return service

@pytest.fixture(scope="function")
def launcher_service(game_service, remote_storage_service_mock):
    with patch('src.launcher_service.subprocess.Popen') as mock_popen:
        mock_process = MagicMock()
        mock_process.poll.side_effect = [None, 0]
        mock_process.wait.return_value = 0
        mock_popen.return_value = mock_process
        
        with patch('src.launcher_service.ExecutableValidator') as MockExecutableValidator:
            mock_validator_instance = MockExecutableValidator.return_value
            mock_validator_instance.validate_executable.return_value = MagicMock(is_valid=True, error_message="", suggested_action="")
            
            service = LauncherService(game_service, remote_storage_service_mock)
            service.logger.propagate = True
            service.validate_command_line_settings = MagicMock(return_value=(True, None))
            yield service

@pytest.fixture(scope="function")
def game_detail_dialog_factory(game_service, image_manager, launcher_service):
    def _factory():
        from src.game_detail_dialog import GameDetailDialog
        dialog = GameDetailDialog(game_service, image_manager, launcher_service)
        dialog.executable_validator = MagicMock()
        dialog.executable_validator.validate_executable.return_value = MagicMock(is_valid=True)
        return dialog
    return _factory

def test_launch_game_with_sync_success_integration(qtbot, game_detail_dialog_factory, game_service, launcher_service, remote_storage_service_mock, tmp_path):
    dialog = game_detail_dialog_factory()
    qtbot.addWidget(dialog)

    local_save_path = tmp_path / "local_saves" / "game_1"
    local_save_path.mkdir(parents=True, exist_ok=True)
    remote_sync_path = "remote:/path/to/sync"

    dialog.findChild(QLineEdit, "titleLineEdit").setText("Sync Game Success")
    dialog.findChild(QLineEdit, "executablePathLineEdit").setText("C:/path/to/game.exe")
    dialog.findChild(QCheckBox, "syncEnabledCheckBox").setChecked(True)
    dialog.findChild(QLineEdit, "saveFolderLineEdit").setText(str(local_save_path))
    dialog.findChild(QLineEdit, "remoteSyncPathLineEdit").setText(remote_sync_path)
    dialog.findChild(QPushButton, "saveButton").click()
    assert dialog.result() == QDialog.Accepted

    game_list = game_service.get_game_list()
    game_id = game_list[0]["id"]

    # リモートの方が新しいと設定
    remote_storage_service_mock.get_latest_mtime.side_effect = [100.0, 200.0]
    remote_storage_service_mock.download_save_data.return_value = True

    launcher_service.launch_game(game_id)

    remote_storage_service_mock.download_save_data.assert_called_once_with(
        game_id, remote_sync_path, local_save_path
    )
    # ゲーム終了後のアップロード
    remote_storage_service_mock.upload_save_data.assert_called_once_with(
        game_id, local_save_path, remote_sync_path
    )

def test_launch_game_with_download_failure_integration(qtbot, game_detail_dialog_factory, game_service, launcher_service, remote_storage_service_mock, tmp_path, caplog):
    caplog.set_level(logging.WARNING, logger='LauncherService')

    dialog = game_detail_dialog_factory()
    qtbot.addWidget(dialog)

    local_save_path = tmp_path / "local_saves" / "game_2"
    local_save_path.mkdir(parents=True, exist_ok=True)
    remote_sync_path = "remote:/path/to/sync_fail_download"

    dialog.findChild(QLineEdit, "titleLineEdit").setText("Sync Game Download Fail")
    dialog.findChild(QLineEdit, "executablePathLineEdit").setText("C:/path/to/game.exe")
    dialog.findChild(QCheckBox, "syncEnabledCheckBox").setChecked(True)
    dialog.findChild(QLineEdit, "saveFolderLineEdit").setText(str(local_save_path))
    dialog.findChild(QLineEdit, "remoteSyncPathLineEdit").setText(remote_sync_path)
    dialog.findChild(QPushButton, "saveButton").click()
    assert dialog.result() == QDialog.Accepted

    game_list = game_service.get_game_list()
    game_id = game_list[0]["id"]

    remote_storage_service_mock.get_latest_mtime.side_effect = [100.0, 200.0]
    remote_storage_service_mock.download_save_data.side_effect = SaveDataSyncError(game_id, "download", Exception("Mock download error"))

    with pytest.raises(SaveDataSyncError):
        launcher_service.launch_game(game_id)

    assert "Save data download failed" in caplog.text

def test_launch_game_with_upload_failure_integration(qtbot, game_detail_dialog_factory, game_service, launcher_service, remote_storage_service_mock, tmp_path, caplog, mocker):
    dialog = game_detail_dialog_factory()
    qtbot.addWidget(dialog)

    local_save_path = tmp_path / "local_saves" / "game_3"
    local_save_path.mkdir(parents=True, exist_ok=True)
    remote_sync_path = "remote:/path/to/sync_fail_upload"

    dialog.findChild(QLineEdit, "titleLineEdit").setText("Sync Game Upload Fail")
    dialog.findChild(QLineEdit, "executablePathLineEdit").setText("C:/path/to/game.exe")
    dialog.findChild(QCheckBox, "syncEnabledCheckBox").setChecked(True)
    dialog.findChild(QLineEdit, "saveFolderLineEdit").setText(str(local_save_path))
    dialog.findChild(QLineEdit, "remoteSyncPathLineEdit").setText(remote_sync_path)
    dialog.findChild(QPushButton, "saveButton").click()
    assert dialog.result() == QDialog.Accepted

    game_list = game_service.get_game_list()
    game_id = game_list[0]["id"]

    # Local Newer
    remote_storage_service_mock.get_latest_mtime.side_effect = [200.0, 100.0]
    # Mock choice to "local" (upload)
    mocker.patch.object(launcher_service, '_show_sync_conflict_dialog', return_value="local")
    
    remote_storage_service_mock.upload_save_data.side_effect = SaveDataSyncError(game_id, "upload", Exception("Mock upload error"))

    with pytest.raises(SaveDataSyncError):
        launcher_service.launch_game(game_id)

    assert "Save data upload failed" in caplog.text

def test_launch_game_with_sync_no_remote_data_integration(qtbot, game_detail_dialog_factory, game_service, launcher_service, remote_storage_service_mock, tmp_path):
    dialog = game_detail_dialog_factory()
    qtbot.addWidget(dialog)

    local_save_path = tmp_path / "local_saves" / "game_no_remote"
    local_save_path.mkdir(parents=True, exist_ok=True)
    (local_save_path / "savegame.dat").write_text("local_save_data_content")

    remote_sync_path = "remote:/path/to/no_remote_sync"

    dialog.findChild(QLineEdit, "titleLineEdit").setText("Sync Game No Remote Data")
    dialog.findChild(QLineEdit, "executablePathLineEdit").setText("C:/path/to/game.exe")
    dialog.findChild(QCheckBox, "syncEnabledCheckBox").setChecked(True)
    dialog.findChild(QLineEdit, "saveFolderLineEdit").setText(str(local_save_path))
    dialog.findChild(QLineEdit, "remoteSyncPathLineEdit").setText(remote_sync_path)
    dialog.findChild(QPushButton, "saveButton").click()
    assert dialog.result() == QDialog.Accepted

    game_list = game_service.get_game_list()
    game_id = game_list[0]["id"]

    remote_storage_service_mock.get_latest_mtime.side_effect = [100.0, 0.0]
    remote_storage_service_mock.download_save_data.return_value = False

    launcher_service.launch_game(game_id)

    remote_storage_service_mock.upload_save_data.assert_called()

def test_launch_game_with_sync_conflict_cancel_integration(qtbot, game_detail_dialog_factory, game_service, launcher_service, remote_storage_service_mock, tmp_path, mocker):
    dialog = game_detail_dialog_factory()
    qtbot.addWidget(dialog)

    local_save_path = tmp_path / "local_saves" / "game_conflict"
    local_save_path.mkdir(parents=True, exist_ok=True)
    remote_sync_path = "remote:/path/to/sync_conflict"

    dialog.findChild(QLineEdit, "titleLineEdit").setText("Sync Conflict Cancel")
    dialog.findChild(QLineEdit, "executablePathLineEdit").setText("C:/path/to/game.exe")
    dialog.findChild(QCheckBox, "syncEnabledCheckBox").setChecked(True)
    dialog.findChild(QLineEdit, "saveFolderLineEdit").setText(str(local_save_path))
    dialog.findChild(QLineEdit, "remoteSyncPathLineEdit").setText(remote_sync_path)
    dialog.findChild(QPushButton, "saveButton").click()
    assert dialog.result() == QDialog.Accepted

    game_list = game_service.get_game_list()
    game_id = game_list[0]["id"]

    # Local (200.0) > Remote (100.0) -> Conflict
    remote_storage_service_mock.get_latest_mtime.side_effect = [200.0, 100.0]
    
    # Mock the dialog to return "cancel"
    mocker.patch.object(launcher_service, '_show_sync_conflict_dialog', return_value="cancel")

    # launch_game raises SaveDataSyncError when sync is cancelled/failed
    with pytest.raises(SaveDataSyncError):
        launcher_service.launch_game(game_id)
    
    remote_storage_service_mock.upload_save_data.assert_not_called()
    remote_storage_service_mock.download_save_data.assert_not_called()