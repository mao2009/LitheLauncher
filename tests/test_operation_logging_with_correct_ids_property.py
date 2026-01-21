"""
Property-based tests for operation logging with correct IDs.
**Feature: game-execution-bug-fixes, Property 15: Operation logging with correct IDs**
"""

import pytest
from hypothesis import given, strategies as st, assume, settings, HealthCheck
from unittest.mock import Mock, MagicMock, patch, call
from src.launcher_service import LauncherService
from src.game_service import GameService
from src.game_repository import GameRepository
from src.exceptions import GameNotFoundError, ExecutableValidationError, CommandExecutionError, SaveDataSyncError


# Strategy for generating game IDs
@st.composite
def game_id_strategy(draw):
    """Generate game IDs for testing."""
    return draw(st.integers(min_value=1, max_value=1000000))


# Strategy for generating valid game data with executable path
@st.composite
def valid_game_with_executable_strategy(draw):
    """Generate valid game data with executable path for testing."""
    game_id = draw(st.integers(min_value=1, max_value=1000000))
    title = draw(st.text(min_size=1, max_size=100).filter(lambda x: x.strip()))
    executable_path = draw(st.text(min_size=1, max_size=200).filter(lambda x: x.strip()))
    
    return {
        'id': game_id,
        'title': title,
        'description': draw(st.text(max_size=200)),
        'executable_path': executable_path,
        'pre_command': draw(st.one_of(st.none(), st.text(max_size=100))),
        'post_command': draw(st.one_of(st.none(), st.text(max_size=100))),
        'save_folder': draw(st.one_of(st.none(), st.text(max_size=200))),
        'sync_enabled': draw(st.integers(min_value=0, max_value=1)),
        'remote_sync_path': draw(st.one_of(st.none(), st.text(max_size=200)))
    }


# Strategy for generating game data without executable path
@st.composite
def game_without_executable_strategy(draw):
    """Generate game data without executable path for testing."""
    game_id = draw(st.integers(min_value=1, max_value=1000000))
    title = draw(st.text(min_size=1, max_size=100).filter(lambda x: x.strip()))
    
    return {
        'id': game_id,
        'title': title,
        'description': draw(st.text(max_size=200)),
        'executable_path': None,  # No executable path
        'pre_command': draw(st.one_of(st.none(), st.text(max_size=100))),
        'post_command': draw(st.one_of(st.none(), st.text(max_size=100))),
        'save_folder': draw(st.one_of(st.none(), st.text(max_size=200))),
        'sync_enabled': draw(st.integers(min_value=0, max_value=1)),
        'remote_sync_path': draw(st.one_of(st.none(), st.text(max_size=200)))
    }


@given(invalid_game_id=game_id_strategy())
@settings(suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
def test_game_not_found_logging_includes_correct_id(invalid_game_id):
    """
    **Feature: game-execution-bug-fixes, Property 15: Operation logging with correct IDs**
    **Validates: Requirements 5.5**
    
    For any game operation that is logged, the log entry should include the correct game ID for traceability.
    This test verifies that when a game is not found, the error log includes the correct game ID.
    """
    # Create mock game service that returns None (game not found)
    mock_game_service = Mock(spec=GameService)
    mock_game_service.get_game_details.return_value = None
    
    # Create mock remote storage service
    mock_remote_storage_service = Mock()
    
    # Create mock logger to capture log calls
    mock_logger = Mock()
    
    # Create launcher service with mocked dependencies
    with patch('src.launcher_service.get_logger', return_value=mock_logger):
        launcher_service = LauncherService(mock_game_service, mock_remote_storage_service)
    
    # Attempt to launch game with invalid ID
    with pytest.raises(GameNotFoundError):
        launcher_service.launch_game(invalid_game_id)
    
    # Verify that the error log includes the correct game ID
    mock_logger.error.assert_called_once_with(f"Game with ID {invalid_game_id} not found.")


@given(game_data=game_without_executable_strategy())
@settings(suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
def test_missing_executable_logging_includes_correct_id(game_data):
    """
    **Feature: game-execution-bug-fixes, Property 15: Operation logging with correct IDs**
    **Validates: Requirements 5.5**
    
    For any game operation that is logged, the log entry should include the correct game ID for traceability.
    This test verifies that when an executable path is missing, the error log includes the correct game ID.
    """
    # Create mock game service that returns game data without executable path
    mock_game_service = Mock(spec=GameService)
    mock_game_service.get_game_details.return_value = game_data
    
    # Create mock remote storage service
    mock_remote_storage_service = Mock()
    
    # Create mock logger to capture log calls
    mock_logger = Mock()
    
    # Create launcher service with mocked dependencies
    with patch('src.launcher_service.get_logger', return_value=mock_logger):
        launcher_service = LauncherService(mock_game_service, mock_remote_storage_service)
    
    # Attempt to launch game without executable path
    with pytest.raises(ExecutableValidationError):
        launcher_service.launch_game(game_data['id'])
    
    # Verify that the error log includes the correct game ID
    mock_logger.error.assert_called_once_with(f"Executable path not set for game ID {game_data['id']}.")


@given(game_data=valid_game_with_executable_strategy())
@settings(suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
def test_executable_validation_failure_logging_includes_correct_id(game_data):
    """
    **Feature: game-execution-bug-fixes, Property 15: Operation logging with correct IDs**
    **Validates: Requirements 5.5**
    
    For any game operation that is logged, the log entry should include the correct game ID for traceability.
    This test verifies that when executable validation fails, the error log includes the correct game ID.
    """
    # Create mock game service that returns valid game data
    mock_game_service = Mock(spec=GameService)
    mock_game_service.get_game_details.return_value = game_data
    
    # Create mock remote storage service
    mock_remote_storage_service = Mock()
    
    # Create mock logger to capture log calls
    mock_logger = Mock()
    
    # Create launcher service with mocked dependencies
    with patch('src.launcher_service.get_logger', return_value=mock_logger):
        launcher_service = LauncherService(mock_game_service, mock_remote_storage_service)
    
    # Mock the executable validator to return validation failure
    with patch.object(launcher_service, 'executable_validator') as mock_validator:
        mock_validation_result = Mock()
        mock_validation_result.is_valid = False
        mock_validation_result.error_type = "not_found"
        mock_validation_result.error_message = "File not found"
        mock_validation_result.suggested_action = "Check path"
        mock_validator.validate_executable.return_value = mock_validation_result
        
        # Attempt to launch game with invalid executable
        with pytest.raises(ExecutableValidationError):
            launcher_service.launch_game(game_data['id'])
        
        # Verify that the error log includes the correct game ID
        expected_log_message = f"Executable validation failed for game ID {game_data['id']}: File not found"
        mock_logger.error.assert_called_once_with(expected_log_message)


@given(game_data=valid_game_with_executable_strategy())
@settings(suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
def test_sync_operation_logging_includes_correct_id(game_data):
    """
    **Feature: game-execution-bug-fixes, Property 15: Operation logging with correct IDs**
    **Validates: Requirements 5.5**
    
    For any game operation that is logged, the log entry should include the correct game ID for traceability.
    This test verifies that sync operations include the correct game ID in their log messages.
    """
    # Ensure sync is enabled for this test
    game_data['sync_enabled'] = 1
    game_data['save_folder'] = '/local/save/path'
    game_data['remote_sync_path'] = '/remote/save/path'
    
    # Create mock game service
    mock_game_service = Mock(spec=GameService)
    mock_game_service.get_game_details.return_value = game_data
    
    # Create mock remote storage service
    mock_remote_storage_service = Mock()
    
    # Create mock logger to capture log calls
    mock_logger = Mock()
    
    # Create launcher service with mocked dependencies
    with patch('src.launcher_service.get_logger', return_value=mock_logger):
        launcher_service = LauncherService(mock_game_service, mock_remote_storage_service)
    
    # Test sync_save_data method directly
    launcher_service.sync_save_data(game_data['id'], "download")
    
    # Verify that the info log includes the correct game ID and operation
    from pathlib import Path # Path をインポート
    expected_log_message_download = f"Downloading save data for {game_data['title']} from {game_data['remote_sync_path']} to {Path(game_data['save_folder'])}"
    mock_logger.info.assert_called_with(expected_log_message_download)
    
    # Test upload direction as well
    launcher_service.sync_save_data(game_data['id'], "upload")
    
    expected_upload_log = f"Uploading save data for {game_data['title']} from {Path(game_data['save_folder'])} to {game_data['remote_sync_path']}"
    mock_logger.info.assert_any_call(expected_upload_log)


@given(game_data=valid_game_with_executable_strategy())
@settings(suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
def test_sync_error_logging_includes_correct_id(game_data):
    """
    **Feature: game-execution-bug-fixes, Property 15: Operation logging with correct IDs**
    **Validates: Requirements 5.5**
    
    For any game operation that is logged, the log entry should include the correct game ID for traceability.
    This test verifies that sync error logs include the correct game ID.
    """
    # Ensure sync is enabled for this test
    game_data['sync_enabled'] = 1
    game_data['save_folder'] = '/local/save/path'
    game_data['remote_sync_path'] = '/remote/save/path'
    
    # Create mock game service
    mock_game_service = Mock(spec=GameService)
    mock_game_service.get_game_details.return_value = game_data
    
    # Create mock remote storage service that raises an exception
    mock_remote_storage_service = Mock()
    mock_remote_storage_service.download_save_data.side_effect = Exception("Network error")
    
    # Create mock logger to capture log calls
    mock_logger = Mock()
    
    # Create launcher service with mocked dependencies
    with patch('src.launcher_service.get_logger', return_value=mock_logger):
        launcher_service = LauncherService(mock_game_service, mock_remote_storage_service)
    
    # Test sync_save_data method with error
    with pytest.raises(SaveDataSyncError):
        launcher_service.sync_save_data(game_data['id'], "download")
    
    # Verify that the exception log includes the correct game ID
    mock_logger.exception.assert_called_once_with(f"Error during save data sync (download) for game {game_data['id']}.")


@given(game_data=valid_game_with_executable_strategy())
@settings(suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
def test_command_execution_logging_includes_correct_id(game_data):
    """
    **Feature: game-execution-bug-fixes, Property 15: Operation logging with correct IDs**
    **Validates: Requirements 5.5**
    
    For any game operation that is logged, the log entry should include the correct game ID for traceability.
    This test verifies that command execution logs include the correct game ID.
    """
    # Set up game with pre and post commands
    game_data['pre_command'] = 'echo "pre command"'
    game_data['post_command'] = 'echo "post command"'
    
    # Create mock game service
    mock_game_service = Mock(spec=GameService)
    mock_game_service.get_game_details.return_value = game_data
    
    # Create mock remote storage service
    mock_remote_storage_service = Mock()
    
    # Create mock logger to capture log calls
    mock_logger = Mock()
    
    # Create launcher service with mocked dependencies
    with patch('src.launcher_service.get_logger', return_value=mock_logger):
        launcher_service = LauncherService(mock_game_service, mock_remote_storage_service)
    
    # Mock executable validation to pass
    with patch.object(launcher_service, 'executable_validator') as mock_validator:
        mock_validation_result = Mock()
        mock_validation_result.is_valid = True
        mock_validator.validate_executable.return_value = mock_validation_result
        
        # Mock subprocess execution to avoid actual process launch
        with patch.object(launcher_service, '_launch_executable') as mock_launch:
            mock_process = Mock()
            mock_process.wait.return_value = 0
            mock_launch.return_value = mock_process
            
            # Mock command execution to return success
            with patch.object(launcher_service, 'execute_command', return_value=(0, "success", "")):
                # Launch the game
                try:
                    launcher_service.launch_game(game_data['id'])
                except Exception:
                    # We don't care about the final result, just the logging
                    pass
                
                # Verify that command execution logs include the game ID context
                # Check for pre-command logging (now includes game ID)
                expected_pre_log = f"Executing pre-command for game ID {game_data['id']}: {game_data['pre_command']}"
                mock_logger.info.assert_any_call(expected_pre_log)
                
                # Check for post-command logging (now includes game ID)
                expected_post_log = f"Executing post-command for game ID {game_data['id']}: {game_data['post_command']}"
                mock_logger.info.assert_any_call(expected_post_log)

                # Check for game launch logging (with settings and final command list)
                expected_launch_settings_log = f"Launching game ID {game_data['id']} with settings: ''"
                mock_logger.info.assert_any_call(expected_launch_settings_log)

                expected_final_command_list_log = f"Final command list for game ID {game_data['id']}: {[game_data['executable_path']]}"
                mock_logger.info.assert_any_call(expected_final_command_list_log)