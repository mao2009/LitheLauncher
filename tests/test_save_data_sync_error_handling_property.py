# tests/test_save_data_sync_error_handling_property.py
"""
**Feature: game-execution-bug-fixes, Property 6: Save data sync error handling**
**Validates: Requirements 2.5**

Property-based test for save data sync error handling.
Tests that save data synchronization failures are captured and reported with sync-specific error information.
"""

import pytest
import tempfile
import os
import platform
from hypothesis import given, strategies as st, assume, settings, HealthCheck
from unittest.mock import MagicMock, patch
from src.launcher_service import LauncherService
from src.game_service import GameService
from src.game_repository import GameRepository
from src.remote_storage_service import RemoteStorageService
from src.database import initialize_database
from src.exceptions import SaveDataSyncError


def create_launcher_service():
    """Create a launcher service for testing."""
    # Set up test database with unique name
    import time
    db_path = f"test_sync_error_{time.time()}.db"
    if os.path.exists(db_path):
        os.remove(db_path)
    initialize_database(db_path)
    
    # Create dependencies
    game_repository = GameRepository(db_path)
    game_service = GameService(game_repository, MagicMock())
    remote_storage_service = RemoteStorageService()
    
    launcher_service = LauncherService(game_service, remote_storage_service)
    launcher_service._test_db_path = db_path
    return launcher_service


def cleanup_launcher_service(launcher_service):
    """Clean up test database."""
    if hasattr(launcher_service, '_test_db_path') and os.path.exists(launcher_service._test_db_path):
        os.remove(launcher_service._test_db_path)


class TestSaveDataSyncErrorHandling:
    
    @given(
        sync_direction=st.sampled_from(["download", "upload"])
    )
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None, max_examples=10)
    def test_sync_error_contains_direction_and_game_info(self, sync_direction):
        """
        Property: For any save data synchronization failure, the system should display 
        sync-specific error information that identifies the sync direction and cause.
        """
        launcher_service = create_launcher_service()
        try:
            # Create a test game with sync enabled
            game_data = {
                "title": "Sync Test Game",
                "description": "Test game for sync error testing",

                "pre_command": "",
                "post_command": "",
                "save_folder": "/test/save/folder",
                "sync_enabled": 1,
                "remote_sync_path": "/remote/test/path",
                "executable_path": None
            }
            
            # Create a temporary executable file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.exe', delete=False) as temp_file:
                temp_file.write('echo "test"')
                temp_executable = temp_file.name
            
            try:
                # Make it executable on Unix-like systems
                if os.name != 'nt':
                    import stat
                    os.chmod(temp_executable, stat.S_IRWXU)
                
                game_data["executable_path"] = temp_executable
                game = launcher_service.game_service.register_game(game_data)
                game_id = game["id"]
                
                # Mock the remote storage service to raise an exception
                test_exception = Exception(f"Test {sync_direction} failure")
                
                if sync_direction == "download":
                    launcher_service.remote_storage_service.download_save_data = MagicMock(side_effect=test_exception)
                else:
                    launcher_service.remote_storage_service.upload_save_data = MagicMock(side_effect=test_exception)
                
                # Attempt to sync, which should fail
                with pytest.raises(SaveDataSyncError) as exc_info:
                    launcher_service.sync_save_data(game_id, sync_direction)
                
                error = exc_info.value
                
                # Verify that the error contains sync-specific information
                assert error.game_id == game_id
                assert error.direction == sync_direction
                
                # Verify that the error message contains sync direction information
                error_str = str(error)
                assert sync_direction in error_str
                assert str(game_id) in error_str
                
                # Verify that the original exception is preserved
                assert error.original_exception is not None
                assert str(test_exception) in str(error.original_exception)
                
            finally:
                # Clean up temporary executable
                if os.path.exists(temp_executable):
                    os.unlink(temp_executable)
                    
        finally:
            cleanup_launcher_service(launcher_service)
    
    def test_sync_error_during_game_launch_download(self):
        """
        Property: When save data download fails during game launch, 
        the error should be specific about the download failure.
        """
        launcher_service = create_launcher_service()
        try:
            # Create a test game with sync enabled
            game_data = {
                "title": "Download Sync Test Game",
                "description": "Test game for download sync error testing",

                "pre_command": "",
                "post_command": "",
                "save_folder": "/test/save/folder",
                "sync_enabled": 1,
                "remote_sync_path": "/remote/test/path",
                "executable_path": None
            }
            
            # Create a temporary executable file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.exe', delete=False) as temp_file:
                temp_file.write('echo "test"')
                temp_executable = temp_file.name
            
            try:
                # Make it executable on Unix-like systems
                if os.name != 'nt':
                    import stat
                    os.chmod(temp_executable, stat.S_IRWXU)
                
                game_data["executable_path"] = temp_executable
                game = launcher_service.game_service.register_game(game_data)
                game_id = game["id"]
                
                # Mock the remote storage service download to fail
                download_exception = Exception("Network error during download")
                launcher_service.remote_storage_service.download_save_data = MagicMock(side_effect=download_exception)
                
                # Attempt to launch the game, which should fail on download
                with pytest.raises(SaveDataSyncError) as exc_info:
                    launcher_service.launch_game(game_id)
                
                error = exc_info.value
                
                # Verify that this is specifically a download error
                assert error.direction == "download"
                assert error.game_id == game_id
                
                # Verify that the error message indicates download failure
                error_str = str(error)
                assert "download" in error_str
                assert str(game_id) in error_str
                
            finally:
                # Clean up temporary executable
                if os.path.exists(temp_executable):
                    os.unlink(temp_executable)
                    
        finally:
            cleanup_launcher_service(launcher_service)
    
    def test_sync_error_during_game_launch_upload(self):
        """
        Property: When save data upload fails after game completion,
        the error should be specific about the upload failure.
        """
        launcher_service = create_launcher_service()
        try:
            # Create a test game with sync enabled
            game_data = {
                "title": "Upload Sync Test Game",
                "description": "Test game for upload sync error testing",

                "pre_command": "",
                "post_command": "",
                "save_folder": "/test/save/folder",
                "sync_enabled": 1,
                "remote_sync_path": "/remote/test/path",
                "executable_path": None
            }
            
            # Create a temporary executable file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.exe', delete=False) as temp_file:
                temp_file.write('echo "test"')
                temp_executable = temp_file.name
            
            try:
                # Make it executable on Unix-like systems
                if os.name != 'nt':
                    import stat
                    os.chmod(temp_executable, stat.S_IRWXU)
                
                game_data["executable_path"] = temp_executable
                game = launcher_service.game_service.register_game(game_data)
                game_id = game["id"]
                
                # Mock the remote storage service upload to fail, but download to succeed
                upload_exception = Exception("Storage quota exceeded during upload")
                launcher_service.remote_storage_service.download_save_data = MagicMock()  # Succeeds
                launcher_service.remote_storage_service.upload_save_data = MagicMock(side_effect=upload_exception)
                
                # Mock the _launch_executable to succeed quickly
                with patch.object(launcher_service, '_launch_executable') as mock_launch:
                    mock_process = MagicMock()
                    mock_process.wait.return_value = None
                    mock_launch.return_value = mock_process
                    
                    # Attempt to launch the game, which should fail on upload
                    with pytest.raises(SaveDataSyncError) as exc_info:
                        launcher_service.launch_game(game_id)
                    
                    error = exc_info.value
                    
                    # Verify that this is specifically an upload error
                    assert error.direction == "upload"
                    assert error.game_id == game_id
                    
                    # Verify that the error message indicates upload failure
                    error_str = str(error)
                    assert "upload" in error_str
                    assert str(game_id) in error_str
                    
            finally:
                # Clean up temporary executable
                if os.path.exists(temp_executable):
                    os.unlink(temp_executable)
                    
        finally:
            cleanup_launcher_service(launcher_service)
    
    def test_invalid_sync_direction_error(self):
        """
        Property: When an invalid sync direction is provided,
        the error should indicate the invalid direction.
        """
        launcher_service = create_launcher_service()
        try:
            # Create a test game with sync enabled
            game_data = {
                "title": "Invalid Direction Test Game",
                "description": "Test game for invalid direction testing",

                "pre_command": "",
                "post_command": "",
                "save_folder": "/test/save/folder",
                "sync_enabled": 1,
                "remote_sync_path": "/remote/test/path",
                "executable_path": None
            }
            
            game = launcher_service.game_service.register_game(game_data)
            game_id = game["id"]
            
            # Attempt to sync with invalid direction
            invalid_direction = "invalid_direction"
            
            with pytest.raises(SaveDataSyncError) as exc_info:
                launcher_service.sync_save_data(game_id, invalid_direction)
            
            error = exc_info.value
            
            # Verify that the error contains information about the invalid direction
            assert error.direction == invalid_direction
            assert error.game_id == game_id
            
            # Verify that the error message indicates the invalid direction
            error_str = str(error)
            assert invalid_direction in error_str
            assert "Invalid direction" in str(error.original_exception)
                    
        finally:
            cleanup_launcher_service(launcher_service)