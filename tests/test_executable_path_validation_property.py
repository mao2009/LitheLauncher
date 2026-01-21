"""
Property-based tests for executable path validation before launch.
**Feature: game-execution-bug-fixes, Property 2: Executable path validation before launch**
"""

import pytest
import tempfile
import os
import stat
from hypothesis import given, strategies as st, assume, settings, HealthCheck
from unittest.mock import Mock, patch
from src.executable_validator import ExecutableValidator, ValidationResult
from src.launcher_service import LauncherService
from src.game_service import GameService
from src.exceptions import ExecutableValidationError


# Strategy for generating various types of paths (valid and invalid)
@st.composite
def path_strategy(draw):
    """Generate various types of file paths for testing validation."""
    path_type = draw(st.sampled_from(['empty', 'nonexistent', 'directory', 'valid_file', 'no_permission']))
    
    if path_type == 'empty':
        return draw(st.sampled_from(['', '   ', None]))
    elif path_type == 'nonexistent':
        # Generate a path that definitely doesn't exist
        return f"/nonexistent/path/{draw(st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'))))}.exe"
    elif path_type == 'directory':
        # We'll create a temporary directory for this
        return 'TEMP_DIR'  # Placeholder, will be replaced in test
    elif path_type == 'valid_file':
        # We'll create a temporary executable file for this
        return 'TEMP_EXECUTABLE'  # Placeholder, will be replaced in test
    elif path_type == 'no_permission':
        # We'll create a file without execute permissions
        return 'TEMP_NO_PERMISSION'  # Placeholder, will be replaced in test


@st.composite
def game_data_with_executable_strategy(draw):
    """Generate game data with various executable path scenarios."""
    game_id = draw(st.integers(min_value=1, max_value=1000000))
    title = draw(st.text(min_size=1, max_size=100).filter(lambda x: x.strip()))
    executable_path = draw(path_strategy())
    
    return {
        'id': game_id,
        'title': title,
        'description': draw(st.text(max_size=200)),
        'executable_path': executable_path,
        'pre_command': None,  # Avoid random pre-commands that cause test failures
        'post_command': None,  # Avoid random post-commands that cause test failures
        'save_folder': draw(st.one_of(st.none(), st.text(max_size=200))),
        'sync_enabled': 0,  # Disable sync to avoid sync-related test complications
        'remote_sync_path': draw(st.one_of(st.none(), st.text(max_size=200)))
    }


@pytest.fixture
def temp_files():
    """Create temporary files and directories for testing."""
    temp_dir = tempfile.mkdtemp()
    
    # Create a valid executable file
    executable_file = os.path.join(temp_dir, 'test_game.exe')
    with open(executable_file, 'w') as f:
        f.write('#!/bin/bash\necho "test game"')
    os.chmod(executable_file, stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)
    
    # Create a file without execute permissions
    no_permission_file = os.path.join(temp_dir, 'no_permission.txt')  # Use .txt extension to make it non-executable on Windows
    with open(no_permission_file, 'w') as f:
        f.write('#!/bin/bash\necho "no permission"')
    if os.name != 'nt':  # Only set permissions on Unix-like systems
        os.chmod(no_permission_file, stat.S_IRUSR | stat.S_IWUSR)  # Read/write only, no execute
    
    # Create a directory
    test_directory = os.path.join(temp_dir, 'test_directory')
    os.makedirs(test_directory)
    
    yield {
        'temp_dir': temp_dir,
        'executable_file': executable_file,
        'no_permission_file': no_permission_file,
        'test_directory': test_directory
    }
    
    # Cleanup
    import shutil
    shutil.rmtree(temp_dir, ignore_errors=True)


@given(game_data=game_data_with_executable_strategy())
@settings(deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_executable_path_validation_before_launch(temp_files, game_data):
    """
    **Feature: game-execution-bug-fixes, Property 2: Executable path validation before launch**
    **Validates: Requirements 1.2, 3.1**
    
    For any game launch attempt, if the game has an executable path set, 
    the system should validate the file exists before attempting subprocess execution.
    """
    # Replace placeholder paths with actual temporary files
    executable_path = game_data['executable_path']
    if executable_path == 'TEMP_EXECUTABLE':
        executable_path = temp_files['executable_file']
    elif executable_path == 'TEMP_DIR':
        executable_path = temp_files['test_directory']
    elif executable_path == 'TEMP_NO_PERMISSION':
        executable_path = temp_files['no_permission_file']
    
    game_data['executable_path'] = executable_path
    
    # Create validator and test validation
    validator = ExecutableValidator()
    
    # Mock game service and launcher service
    mock_game_service = Mock()
    mock_game_service.get_game_details.return_value = game_data
    mock_remote_storage = Mock()
    
    launcher_service = LauncherService(mock_game_service, mock_remote_storage)
    
    # Test the validation logic
    if not executable_path or (isinstance(executable_path, str) and not executable_path.strip()):
        # Empty path case
        validation_result = validator.validate_executable(executable_path)
        assert not validation_result.is_valid
        assert validation_result.error_type == "missing"
        
        # LauncherService should raise ExecutableValidationError for empty paths
        with pytest.raises(ExecutableValidationError) as exc_info:
            launcher_service.launch_game(game_data['id'])
        assert exc_info.value.error_type == "missing"
        
    elif executable_path == temp_files['executable_file']:
        # Valid executable case
        validation_result = validator.validate_executable(executable_path)
        assert validation_result.is_valid
        assert validation_result.error_type == ""
        assert validation_result.error_message == ""
        
        # LauncherService should not raise validation error for valid executables
        # (it might raise other errors due to mocking, but not ExecutableValidationError)
        try:
            launcher_service.launch_game(game_data['id'])
        except ExecutableValidationError:
            pytest.fail("Should not raise ExecutableValidationError for valid executable")
        except Exception:
            # Other exceptions are expected due to mocking
            pass
            
    elif executable_path == temp_files['test_directory']:
        # Directory instead of file case
        validation_result = validator.validate_executable(executable_path)
        assert not validation_result.is_valid
        assert validation_result.error_type == "not_executable"
        
        # LauncherService should raise ExecutableValidationError for directories
        with pytest.raises(ExecutableValidationError) as exc_info:
            launcher_service.launch_game(game_data['id'])
        assert exc_info.value.error_type == "not_executable"
        
    elif executable_path == temp_files['no_permission_file']:
        # No execute permission case
        validation_result = validator.validate_executable(executable_path)
        assert not validation_result.is_valid
        assert validation_result.error_type == "permission_denied"
        
        # LauncherService should raise ExecutableValidationError for files without execute permission
        with pytest.raises(ExecutableValidationError) as exc_info:
            launcher_service.launch_game(game_data['id'])
        assert exc_info.value.error_type == "permission_denied"
        
    else:
        # Nonexistent file case
        validation_result = validator.validate_executable(executable_path)
        assert not validation_result.is_valid
        assert validation_result.error_type == "not_found"
        
        # LauncherService should raise ExecutableValidationError for nonexistent files
        with pytest.raises(ExecutableValidationError) as exc_info:
            launcher_service.launch_game(game_data['id'])
        assert exc_info.value.error_type == "not_found"


@given(executable_path=path_strategy())
@settings(deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_executable_validator_comprehensive_validation(temp_files, executable_path):
    """
    **Feature: game-execution-bug-fixes, Property 2: Executable path validation before launch**
    **Validates: Requirements 1.2, 3.1**
    
    For any executable path, the ExecutableValidator should provide comprehensive
    validation covering existence, file type, and permissions.
    """
    # Replace placeholder paths with actual temporary files
    if executable_path == 'TEMP_EXECUTABLE':
        executable_path = temp_files['executable_file']
    elif executable_path == 'TEMP_DIR':
        executable_path = temp_files['test_directory']
    elif executable_path == 'TEMP_NO_PERMISSION':
        executable_path = temp_files['no_permission_file']
    
    validator = ExecutableValidator()
    result = validator.validate_executable(executable_path)
    
    # Verify that the result is always a ValidationResult with proper structure
    assert isinstance(result, ValidationResult)
    assert isinstance(result.is_valid, bool)
    assert isinstance(result.error_type, str)
    assert isinstance(result.error_message, str)
    assert isinstance(result.suggested_action, str)
    
    # Verify validation logic consistency
    if not executable_path or (isinstance(executable_path, str) and not executable_path.strip()):
        # Empty paths should be invalid
        assert not result.is_valid
        assert result.error_type == "missing"
        assert "empty" in result.error_message.lower() or "not set" in result.error_message.lower()
        assert result.suggested_action != ""
        
    elif executable_path == temp_files['executable_file']:
        # Valid executable should pass all validations
        assert result.is_valid
        assert result.error_type == ""
        assert result.error_message == ""
        assert result.suggested_action == ""
        
    elif executable_path == temp_files['test_directory']:
        # Directory should fail with appropriate error
        assert not result.is_valid
        assert result.error_type == "not_executable"
        assert "directory" in result.error_message.lower()
        assert result.suggested_action != ""
        
    elif executable_path == temp_files['no_permission_file']:
        # File without execute permission should fail
        assert not result.is_valid
        assert result.error_type == "permission_denied"
        assert ("permission" in result.error_message.lower() or "executable" in result.error_message.lower())
        assert result.suggested_action != ""
        
    else:
        # Nonexistent file should fail
        assert not result.is_valid
        assert result.error_type == "not_found"
        assert "not found" in result.error_message.lower()
        assert result.suggested_action != ""


@given(st.lists(game_data_with_executable_strategy(), min_size=1, max_size=5))
@settings(deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_batch_executable_validation_consistency(temp_files, game_data_list):
    """
    **Feature: game-execution-bug-fixes, Property 2: Executable path validation before launch**
    **Validates: Requirements 1.2, 3.1**
    
    For any set of games, executable path validation should be consistent
    and deterministic across multiple validation calls.
    """
    validator = ExecutableValidator()
    
    # Process each game's executable path
    for game_data in game_data_list:
        executable_path = game_data['executable_path']
        
        # Replace placeholder paths
        if executable_path == 'TEMP_EXECUTABLE':
            executable_path = temp_files['executable_file']
        elif executable_path == 'TEMP_DIR':
            executable_path = temp_files['test_directory']
        elif executable_path == 'TEMP_NO_PERMISSION':
            executable_path = temp_files['no_permission_file']
        
        game_data['executable_path'] = executable_path
        
        # Validate the same path multiple times to ensure consistency
        result1 = validator.validate_executable(executable_path)
        result2 = validator.validate_executable(executable_path)
        result3 = validator.validate_game_executable(game_data)
        
        # All validation results should be identical
        assert result1.is_valid == result2.is_valid == result3.is_valid, \
            f"Validation results should be consistent for path: {executable_path}"
        assert result1.error_type == result2.error_type == result3.error_type, \
            f"Error types should be consistent for path: {executable_path}"
        
        # Verify that validation is deterministic (same input -> same output)
        if result1.is_valid:
            assert result1.error_message == result2.error_message == result3.error_message == ""
            assert result1.suggested_action == result2.suggested_action == result3.suggested_action == ""
        else:
            assert result1.error_message == result2.error_message == result3.error_message
            assert result1.suggested_action == result2.suggested_action == result3.suggested_action