# tests/test_command_execution_error_reporting_property.py
"""
**Feature: game-execution-bug-fixes, Property 5: Command execution error reporting**
**Validates: Requirements 2.4**

Property-based test for command execution error reporting.
Tests that pre/post command execution failures are captured and reported with specific error details.
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
from src.exceptions import CommandExecutionError


def create_launcher_service():
    """Create a launcher service for testing."""
    # Set up test database with unique name
    import time
    db_path = f"test_command_error_{time.time()}.db"
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


class TestCommandExecutionErrorReporting:
    
    @given(
        failing_command=st.sampled_from([
            "nonexistent_command_12345",
            "invalid_command_xyz",
            "missing_executable_abc"
        ])
    )
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None, max_examples=10)
    def test_command_execution_error_contains_command_and_details(self, failing_command):
        """
        Property: For any pre/post command that fails, the system should display 
        both the command that failed and the specific error details.
        """
        launcher_service = create_launcher_service()
        try:
            # Create a test game with the failing command as pre_command
            game_data = {
                "title": "Test Game",
                "description": "Test game for command error testing",
                "pre_command": failing_command,
                "post_command": "",
                "save_folder": "",
                "sync_enabled": 0,
                "remote_sync_path": "",
                "executable_path": None  # Will be set to a valid path
            }
            
            # Create a temporary executable file for the game
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
                
                # Attempt to launch the game, which should fail on the pre_command
                with pytest.raises(CommandExecutionError) as exc_info:
                    launcher_service.launch_game(game_id)
                
                error = exc_info.value
                
                # Verify that the error contains the command that failed
                assert failing_command in error.command
                
                # Verify that the error has a non-zero return code
                assert error.returncode != 0
                
                # Verify that error details are captured
                assert isinstance(error.stdout, str)
                assert isinstance(error.stderr, str)
                
                # The error message should contain information about the command failure
                error_str = str(error)
                assert failing_command in error_str
                assert "failed" in error_str.lower()
                
            finally:
                # Clean up temporary executable
                if os.path.exists(temp_executable):
                    os.unlink(temp_executable)
                    
        finally:
            cleanup_launcher_service(launcher_service)
    
    def test_command_execution_error_includes_return_code_and_output(self):
        """
        Property: When a command execution fails, the error should include
        the return code, stdout, and stderr from the failed command.
        """
        launcher_service = create_launcher_service()
        try:
            # Test with a command that will definitely fail
            failing_command = "nonexistent_command_test_12345"
            
            # Execute the command directly to test error reporting
            returncode, stdout, stderr = launcher_service.execute_command(failing_command)
            
            # Verify failure is detected
            assert returncode != 0
            
            # Verify output is captured
            assert isinstance(stdout, str)
            assert isinstance(stderr, str)
            
            # On Windows, stderr should contain error information about the command not being found
            if platform.system() == "Windows":
                assert len(stderr) > 0
                # Should contain some indication that the command was not found
                assert ("認識されていません" in stderr or 
                       "not recognized" in stderr or 
                       "not found" in stderr.lower())
                
        finally:
            cleanup_launcher_service(launcher_service)
    
    def test_post_command_error_reporting(self):
        """
        Property: When a post-launch command fails, the error should be reported
        with the same level of detail as pre-launch command failures.
        """
        launcher_service = create_launcher_service()
        try:
            failing_post_command = "invalid_post_command_xyz"
            
            # Create a test game with a failing post_command
            game_data = {
                "title": "Test Game Post Command",
                "description": "Test game for post command error testing",
                "pre_command": "",
                "post_command": failing_post_command,
                "save_folder": "",
                "sync_enabled": 0,
                "remote_sync_path": "",
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
                
                # Mock the _launch_executable to succeed quickly so we get to post_command
                with patch.object(launcher_service, '_launch_executable') as mock_launch:
                    mock_process = MagicMock()
                    mock_process.wait.return_value = None
                    mock_launch.return_value = mock_process
                    
                    # Attempt to launch the game, which should fail on the post_command
                    with pytest.raises(CommandExecutionError) as exc_info:
                        launcher_service.launch_game(game_id)
                    
                    error = exc_info.value
                    
                    # Verify that the error contains the post command that failed
                    assert failing_post_command in error.command
                    
                    # Verify error details are captured
                    assert error.returncode != 0
                    assert isinstance(error.stdout, str)
                    assert isinstance(error.stderr, str)
                    
            finally:
                # Clean up temporary executable
                if os.path.exists(temp_executable):
                    os.unlink(temp_executable)
                    
        finally:
            cleanup_launcher_service(launcher_service)