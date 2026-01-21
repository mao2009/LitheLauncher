"""
Property-based tests for launch request ID validation.
**Feature: game-execution-bug-fixes, Property 14: Launch request ID validation**
"""

import pytest
from hypothesis import given, strategies as st, assume, settings, HealthCheck
from unittest.mock import Mock, MagicMock, patch
from src.launcher_service import LauncherService
from src.game_service import GameService
from src.game_repository import GameRepository
from src.exceptions import GameNotFoundError


# Strategy for generating game IDs
@st.composite
def game_id_strategy(draw):
    """Generate game IDs for testing."""
    return draw(st.integers(min_value=1, max_value=1000000))


# Strategy for generating valid game data
@st.composite
def valid_game_data_strategy(draw):
    """Generate valid game data that exists in the database."""
    game_id = draw(st.integers(min_value=1, max_value=1000000))
    title = draw(st.text(min_size=1, max_size=100).filter(lambda x: x.strip()))
    
    return {
        'id': game_id,
        'title': title,
        'description': draw(st.text(max_size=200)),
        'executable_path': draw(st.one_of(st.none(), st.text(min_size=1, max_size=200))),
        'pre_command': draw(st.one_of(st.none(), st.text(max_size=100))),
        'post_command': draw(st.one_of(st.none(), st.text(max_size=100))),
        'save_folder': draw(st.one_of(st.none(), st.text(max_size=200))),
        'sync_enabled': draw(st.integers(min_value=0, max_value=1)),
        'remote_sync_path': draw(st.one_of(st.none(), st.text(max_size=200)))
    }


@given(invalid_game_id=game_id_strategy())
@settings(suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
def test_launch_request_validates_game_id_existence(invalid_game_id):
    """
    **Feature: game-execution-bug-fixes, Property 14: Launch request ID validation**
    **Validates: Requirements 5.3**
    
    For any launch request received by the launcher service, the system should validate 
    that the game ID exists in the database before proceeding.
    """
    # Create mock game service that returns None for any game ID (simulating non-existent games)
    mock_game_service = Mock(spec=GameService)
    mock_game_service.get_game_details.return_value = None
    
    # Create mock remote storage service
    mock_remote_storage_service = Mock()
    
    # Create launcher service with mocked dependencies
    with patch('src.launcher_service.get_logger'):
        launcher_service = LauncherService(mock_game_service, mock_remote_storage_service)
    
    # Attempt to launch a game with an invalid ID should raise GameNotFoundError
    with pytest.raises(GameNotFoundError) as exc_info:
        launcher_service.launch_game(invalid_game_id)
    
    # Verify that the exception contains the correct game ID
    assert exc_info.value.identifier == invalid_game_id, \
        f"GameNotFoundError should contain the invalid game ID: expected {invalid_game_id}, got {exc_info.value.identifier}"
    
    # Verify that get_game_details was called with the correct ID
    mock_game_service.get_game_details.assert_called_once_with(invalid_game_id)


@given(valid_game_data=valid_game_data_strategy())
@settings(suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
def test_launch_request_proceeds_with_valid_game_id(valid_game_data):
    """
    **Feature: game-execution-bug-fixes, Property 14: Launch request ID validation**
    **Validates: Requirements 5.3**
    
    For any launch request with a valid game ID, the system should proceed with 
    the launch process after validating the ID exists.
    """
    # Create mock game service that returns the valid game data
    mock_game_service = Mock(spec=GameService)
    mock_game_service.get_game_details.return_value = valid_game_data
    
    # Create mock remote storage service
    mock_remote_storage_service = Mock()
    
    # Create launcher service with mocked dependencies
    with patch('src.launcher_service.get_logger'):
        launcher_service = LauncherService(mock_game_service, mock_remote_storage_service)
    
    # Mock the executable validator to avoid file system dependencies
    with patch.object(launcher_service, 'executable_validator') as mock_validator:
        # Set up validation to fail to avoid actual subprocess execution
        mock_validation_result = Mock()
        mock_validation_result.is_valid = False
        mock_validation_result.error_type = "not_found"
        mock_validation_result.error_message = "File not found"
        mock_validation_result.suggested_action = "Check path"
        mock_validator.validate_executable.return_value = mock_validation_result
        
        # Attempt to launch should not raise GameNotFoundError (it may raise other validation errors)
        from src.exceptions import ExecutableValidationError
        
        try:
            launcher_service.launch_game(valid_game_data['id'])
        except ExecutableValidationError:
            # This is expected due to our mock validation failure
            pass
        except GameNotFoundError:
            # This should not happen with a valid game ID
            pytest.fail(f"GameNotFoundError should not be raised for valid game ID {valid_game_data['id']}")
        
        # Verify that get_game_details was called with the correct ID
        mock_game_service.get_game_details.assert_called_once_with(valid_game_data['id'])


@given(
    existing_game_ids=st.lists(game_id_strategy(), min_size=1, max_size=10, unique=True),
    requested_game_id=game_id_strategy()
)
@settings(suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
def test_launch_request_id_validation_boundary_conditions(existing_game_ids, requested_game_id):
    """
    **Feature: game-execution-bug-fixes, Property 14: Launch request ID validation**
    **Validates: Requirements 5.3**
    
    For any set of existing game IDs and any requested game ID, the system should 
    correctly validate whether the requested ID exists in the set of valid IDs.
    """
    # Assume the requested ID is not in the existing set to test the negative case
    assume(requested_game_id not in existing_game_ids)
    
    # Create mock game service
    mock_game_service = Mock(spec=GameService)
    
    # Configure mock to return None for the requested ID (not found)
    mock_game_service.get_game_details.return_value = None
    
    # Create mock remote storage service
    mock_remote_storage_service = Mock()
    
    # Create launcher service with mocked dependencies
    with patch('src.launcher_service.get_logger'):
        launcher_service = LauncherService(mock_game_service, mock_remote_storage_service)
    
    # Attempt to launch with non-existent ID should raise GameNotFoundError
    with pytest.raises(GameNotFoundError) as exc_info:
        launcher_service.launch_game(requested_game_id)
    
    # Verify the error contains the correct game ID
    assert exc_info.value.identifier == requested_game_id
    
    # Verify that the service attempted to look up the game
    mock_game_service.get_game_details.assert_called_once_with(requested_game_id)