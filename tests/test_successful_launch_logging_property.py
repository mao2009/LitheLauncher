"""
Property-based tests for successful launch logging consistency.
**Feature: game-execution-bug-fixes, Property 3: Successful launch logging consistency**
"""

import pytest
from hypothesis import given, strategies as st, assume, settings, HealthCheck
from unittest.mock import Mock, MagicMock, patch, call
from src.launcher_service import LauncherService
from src.game_service import GameService
from src.game_repository import GameRepository


# Strategy for generating valid game data with executable path
@st.composite
def valid_game_with_executable_strategy(draw):
    """Generate valid game data with executable path for testing."""
    game_id = draw(st.integers(min_value=1, max_value=1000000))
    title = draw(st.text(min_size=1, max_size=100, alphabet=st.characters(min_codepoint=32, max_codepoint=126)).filter(lambda x: x.strip()))
    # Generate more realistic executable paths
    executable_path = draw(st.text(min_size=5, max_size=200, alphabet=st.characters(min_codepoint=32, max_codepoint=126)).filter(lambda x: x.strip() and len(x) > 3))
    
    return {
        'id': game_id,
        'title': title,
        'description': draw(st.text(max_size=200, alphabet=st.characters(min_codepoint=32, max_codepoint=126))),
        'executable_path': executable_path,
        'pre_command': draw(st.one_of(st.none(), st.text(min_size=3, max_size=100, alphabet=st.characters(min_codepoint=32, max_codepoint=126)))),
        'post_command': draw(st.one_of(st.none(), st.text(min_size=3, max_size=100, alphabet=st.characters(min_codepoint=32, max_codepoint=126)))),
        'save_folder': draw(st.one_of(st.none(), st.text(max_size=200, alphabet=st.characters(min_codepoint=32, max_codepoint=126)))),
        'sync_enabled': draw(st.integers(min_value=0, max_value=1)),
        'remote_sync_path': draw(st.one_of(st.none(), st.text(max_size=200, alphabet=st.characters(min_codepoint=32, max_codepoint=126))))
    }


@given(game_data=valid_game_with_executable_strategy())
@settings(suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
def test_successful_launch_logging_consistency(game_data):
    """
    **Feature: game-execution-bug-fixes, Property 3: Successful launch logging consistency**
    **Validates: Requirements 1.4, 1.5**
    
    For any game with a valid executable path, when launched successfully, the system should log both 
    the launch initiation and process completion.
    """
    # Create mock game service that returns valid game data
    mock_game_service = Mock(spec=GameService, image_manager=MagicMock())
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
        
        # Mock subprocess execution to simulate successful launch
        with patch.object(launcher_service, '_launch_executable') as mock_launch:
            mock_process = Mock()
            mock_process.wait.return_value = 0  # Successful exit
            mock_launch.return_value = mock_process
            
            # Mock command execution to return success for pre/post commands
            with patch.object(launcher_service, 'execute_command', return_value=(0, "success", "")):
                # Mock sync operations if enabled
                if game_data.get('sync_enabled') and game_data.get('save_folder') and game_data.get('remote_sync_path'):
                    with patch.object(launcher_service, 'sync_save_data', return_value=True):
                        # Launch the game
                        result = launcher_service.launch_game(game_data['id'])
                else:
                    # Launch the game without sync
                    result = launcher_service.launch_game(game_data['id'])
                
                # Verify successful launch
                assert result is True
                
                # Verify launch initiation logging (settings)
                expected_launch_settings_log = f"Launching game ID {game_data['id']} with settings: ''"
                
                # Verify final command list logging
                from pathlib import Path
                final_command_list_expected = [str(Path(game_data['executable_path']))] if game_data.get('executable_path') else []
                expected_final_command_list_log = f"Final command list for game ID {game_data['id']}: {final_command_list_expected}"

                # Verify process completion logging (now includes game ID and exit code)
                expected_exit_log = f"Game process for game ID {game_data['id']} ({game_data['executable_path']}) exited with code 0"
                
                # Check actual log calls (get the actual arguments passed to logger.info)
                actual_log_messages = [call.args[0] for call in mock_logger.info.call_args_list]
                
                # Find launch settings log
                launch_settings_found = any(expected_launch_settings_log == msg for msg in actual_log_messages)
                assert launch_settings_found, f"Launch settings log not found. Expected: '{expected_launch_settings_log}'. Actual messages: {actual_log_messages}"

                # Find final command list log
                final_command_list_found = any(expected_final_command_list_log == msg for msg in actual_log_messages)
                assert final_command_list_found, f"Final command list log not found. Expected: '{expected_final_command_list_log}'. Actual messages: {actual_log_messages}"
                
                # Find process completion log
                exit_found = any(expected_exit_log == msg for msg in actual_log_messages)
                assert exit_found, f"Process completion log not found. Expected: '{expected_exit_log}'. Actual messages: {actual_log_messages}"


@given(game_data=valid_game_with_executable_strategy())
@settings(suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
def test_successful_launch_with_commands_logging_consistency(game_data):
    """
    **Feature: game-execution-bug-fixes, Property 3: Successful launch logging consistency**
    **Validates: Requirements 1.4, 1.5**
    
    For any game with valid executable path and pre/post commands, when launched successfully, 
    the system should log launch initiation, process completion, and command execution.
    """
    # Ensure game has pre and post commands
    game_data['pre_command'] = 'echo "pre command"'
    game_data['post_command'] = 'echo "post command"'
    
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
    
    # Mock executable validation to pass
    with patch.object(launcher_service, 'executable_validator') as mock_validator:
        mock_validation_result = Mock()
        mock_validation_result.is_valid = True
        mock_validator.validate_executable.return_value = mock_validation_result
        
        # Mock subprocess execution to simulate successful launch
        with patch.object(launcher_service, '_launch_executable') as mock_launch:
            mock_process = Mock()
            mock_process.wait.return_value = 0  # Successful exit
            mock_launch.return_value = mock_process
            
            # Mock command execution to return success
            with patch.object(launcher_service, 'execute_command', return_value=(0, "success", "")):
                # Launch the game
                result = launcher_service.launch_game(game_data['id'])
                
                # Verify successful launch
                assert result is True
                
                # Verify all expected logs are present (now with game IDs)
                from pathlib import Path
                final_command_list_expected = [f"echo \"pre command\""] # _build_command_and_args の結果をシミュレート
                game_exe_path_str = str(Path(game_data['executable_path'])) # Pathオブジェクトに変換
                final_command_list_game = [game_exe_path_str] # _build_command_and_args の結果をシミュレート
                
                expected_logs = [
                    f"Executing pre-command for game ID {game_data['id']}: {game_data['pre_command']}",
                    f"Pre-command completed successfully for game ID {game_data['id']}. Output: success",
                    f"Launching game ID {game_data['id']} with settings: '{game_data.get('command_line_settings', '')}'",
                    f"Final command list for game ID {game_data['id']}: {final_command_list_game}",
                    f"Game process for game ID {game_data['id']} ({game_data['executable_path']}) exited with code 0",
                    f"Executing post-command for game ID {game_data['id']}: {game_data['post_command']}",
                    f"Post-command completed successfully for game ID {game_data['id']}. Output: success"
                ]
                
                # Check actual log calls (get the actual arguments passed to logger.info)
                actual_log_messages = [call.args[0] for call in mock_logger.info.call_args_list]
                
                for expected_log in expected_logs:
                    log_found = any(expected_log == msg for msg in actual_log_messages)
                    assert log_found, f"Expected log not found: '{expected_log}'. Actual messages: {actual_log_messages}"


@given(game_data=valid_game_with_executable_strategy())
@settings(suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
def test_successful_launch_with_sync_logging_consistency(game_data):
    """
    **Feature: game-execution-bug-fixes, Property 3: Successful launch logging consistency**
    **Validates: Requirements 1.4, 1.5**
    
    For any game with valid executable path and sync enabled, when launched successfully, 
    the system should log launch initiation, process completion, and sync operations.
    """
    # Ensure sync is enabled and clear any commands to avoid execution issues
    game_data['sync_enabled'] = 1
    game_data['save_folder'] = '/local/save/path'
    game_data['remote_sync_path'] = '/remote/save/path'
    game_data['pre_command'] = None  # Clear to avoid command execution
    game_data['post_command'] = None  # Clear to avoid command execution
    
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
    
    # Mock executable validation to pass
    with patch.object(launcher_service, 'executable_validator') as mock_validator:
        mock_validation_result = Mock()
        mock_validation_result.is_valid = True
        mock_validator.validate_executable.return_value = mock_validation_result
        
        # Mock subprocess execution to simulate successful launch
        with patch.object(launcher_service, '_launch_executable') as mock_launch:
            mock_process = Mock()
            mock_process.wait.return_value = 0  # Successful exit
            mock_launch.return_value = mock_process
            
            # Mock sync operations to return success
            with patch.object(launcher_service, 'sync_save_data', return_value=True):
                # Launch the game
                result = launcher_service.launch_game(game_data['id'])
                
                # Verify successful launch
                assert result is True
                
                # Verify core launch logs are present (now with game IDs)
                from pathlib import Path
                final_command_list_expected_sync = [str(Path(game_data['executable_path']))] if game_data.get('executable_path') else []
                expected_launch_settings_log = f"Launching game ID {game_data['id']} with settings: '{game_data.get('command_line_settings', '')}'"
                expected_final_command_list_log = f"Final command list for game ID {game_data['id']}: {final_command_list_expected_sync}"
                expected_exit_log = f"Game process for game ID {game_data['id']} ({game_data['executable_path']}) exited with code 0"
                
                # Check actual log calls (get the actual arguments passed to logger.info)
                actual_log_messages = [call.args[0] for call in mock_logger.info.call_args_list]
                
                # Find launch initiation log
                launch_settings_found = any(expected_launch_settings_log == msg for msg in actual_log_messages)
                assert launch_settings_found, f"Launch settings log not found. Expected: '{expected_launch_settings_log}'. Actual messages: {actual_log_messages}"

                # Find final command list log
                final_command_list_found = any(expected_final_command_list_log == msg for msg in actual_log_messages)
                assert final_command_list_found, f"Final command list log not found. Expected: '{expected_final_command_list_log}'. Actual messages: {actual_log_messages}"
                
                # Find process completion log
                exit_found = any(expected_exit_log == msg for msg in actual_log_messages)
                assert exit_found, f"Process completion log not found. Expected: '{expected_exit_log}'. Actual messages: {actual_log_messages}"
                
                # Verify sync operation logs are present
                expected_sync_logs = [
                    f"Sync enabled for game ID {game_data['id']}. Checking for download...",
                    f"Sync enabled for game ID {game_data['id']}. Checking for upload after game exit..."
                ]
                
                for expected_sync_log in expected_sync_logs:
                    sync_found = any(expected_sync_log == msg for msg in actual_log_messages)
                    assert sync_found, f"Sync log not found. Expected: '{expected_sync_log}'. Actual messages: {actual_log_messages}"