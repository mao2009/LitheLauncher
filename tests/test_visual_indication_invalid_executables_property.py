"""
Property-based tests for visual indication of invalid executables.
**Feature: game-execution-bug-fixes, Property 7: Visual indication of invalid executables**
"""

import pytest
import tempfile
import os
import stat
from hypothesis import given, strategies as st, assume, settings, HealthCheck
from unittest.mock import Mock, patch
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from src.game_card_widget import GameCardWidget
from src.executable_validator import ExecutableValidator, ValidationResult


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
        'pre_command': draw(st.one_of(st.none(), st.text(max_size=200))),
        'post_command': draw(st.one_of(st.none(), st.text(max_size=200))),
        'save_folder': draw(st.one_of(st.none(), st.text(max_size=200))),
        'sync_enabled': draw(st.integers(min_value=0, max_value=1)),
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


@pytest.fixture
def qt_app():
    """Create QApplication instance for testing Qt widgets."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


@given(game_data=game_data_with_executable_strategy())
@settings(deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_visual_indication_of_invalid_executables(qt_app, temp_files, game_data):
    """
    **Feature: game-execution-bug-fixes, Property 7: Visual indication of invalid executables**
    **Validates: Requirements 3.3**
    
    For any game displayed in the library, if the executable path is missing or invalid, 
    the game card should provide a visual indicator of this state.
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
    
    # Create validator to determine expected validation state
    validator = ExecutableValidator()
    validation_result = validator.validate_executable(executable_path)
    
    # Create game card widget
    game_card = GameCardWidget(game_data)
    
    # Check if the game card has visual indication methods
    assert hasattr(game_card, 'update_validation_status'), \
        "GameCardWidget should have update_validation_status method for visual indicators"
    
    # Update validation status
    game_card.update_validation_status(validation_result)
    
    # Verify visual indicators based on validation result
    if validation_result.is_valid:
        # Valid executable should not have error indicators
        assert not game_card.has_error_indicator(), \
            f"Valid executable should not show error indicator for path: {executable_path}"
        
        # Check that the card doesn't have invalid styling
        assert "invalid" not in game_card.objectName().lower(), \
            "Valid executable should not have 'invalid' in object name"
            
    else:
        # Invalid executable should have visual indicators
        assert game_card.has_error_indicator(), \
            f"Invalid executable should show error indicator for path: {executable_path} (error: {validation_result.error_type})"
        
        # Check that appropriate styling is applied
        object_name = game_card.objectName()
        assert "invalid" in object_name.lower() or "error" in object_name.lower(), \
            f"Invalid executable should have appropriate object name for styling. Current: {object_name}"
        
        # Verify error tooltip or status text is available
        if hasattr(game_card, 'get_error_message'):
            error_message = game_card.get_error_message()
            assert error_message and len(error_message.strip()) > 0, \
                "Invalid executable should provide error message"
            assert validation_result.error_type in error_message.lower() or \
                   any(keyword in error_message.lower() for keyword in ['missing', 'not found', 'permission', 'executable', 'directory', 'file']), \
                f"Error message should contain relevant keywords. Message: {error_message}"


@given(st.lists(game_data_with_executable_strategy(), min_size=1, max_size=5))
@settings(deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_visual_indication_consistency_across_multiple_cards(qt_app, temp_files, game_data_list):
    """
    **Feature: game-execution-bug-fixes, Property 7: Visual indication of invalid executables**
    **Validates: Requirements 3.3**
    
    For any set of games with different validation states, visual indicators should be 
    consistently applied based on the validation result.
    """
    validator = ExecutableValidator()
    game_cards = []
    validation_results = []
    
    # Process each game and create cards
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
        
        # Validate and create card
        validation_result = validator.validate_executable(executable_path)
        validation_results.append(validation_result)
        
        game_card = GameCardWidget(game_data)
        game_card.update_validation_status(validation_result)
        game_cards.append(game_card)
    
    # Verify consistency across all cards
    for i, (card, validation_result) in enumerate(zip(game_cards, validation_results)):
        if validation_result.is_valid:
            assert not card.has_error_indicator(), \
                f"Card {i} with valid executable should not show error indicator"
        else:
            assert card.has_error_indicator(), \
                f"Card {i} with invalid executable should show error indicator (error: {validation_result.error_type})"
    
    # Verify that cards with the same validation state have consistent indicators
    valid_cards = [card for card, result in zip(game_cards, validation_results) if result.is_valid]
    invalid_cards = [card for card, result in zip(game_cards, validation_results) if not result.is_valid]
    
    # All valid cards should have consistent styling
    if len(valid_cards) > 1:
        first_valid_style = valid_cards[0].objectName()
        for card in valid_cards[1:]:
            assert card.objectName() == first_valid_style, \
                "All valid cards should have consistent object names for styling"
    
    # All invalid cards should have error indicators (though specific styling may vary by error type)
    for card in invalid_cards:
        assert card.has_error_indicator(), \
            "All invalid cards should have error indicators"


@given(game_data=game_data_with_executable_strategy())
@settings(deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_visual_indication_updates_dynamically(qt_app, temp_files, game_data):
    """
    **Feature: game-execution-bug-fixes, Property 7: Visual indication of invalid executables**
    **Validates: Requirements 3.3**
    
    For any game card, when the validation status changes, the visual indicators 
    should update accordingly.
    """
    # Start with an invalid path
    game_data['executable_path'] = '/nonexistent/path/game.exe'
    
    validator = ExecutableValidator()
    game_card = GameCardWidget(game_data)
    
    # Initial state - invalid executable
    invalid_result = validator.validate_executable(game_data['executable_path'])
    assert not invalid_result.is_valid
    
    game_card.update_validation_status(invalid_result)
    assert game_card.has_error_indicator(), \
        "Card should show error indicator for invalid executable"
    
    # Update to valid executable
    valid_path = temp_files['executable_file']
    game_data['executable_path'] = valid_path
    valid_result = validator.validate_executable(valid_path)
    assert valid_result.is_valid
    
    game_card.update_validation_status(valid_result)
    assert not game_card.has_error_indicator(), \
        "Card should not show error indicator after updating to valid executable"
    
    # Update back to invalid executable
    game_data['executable_path'] = temp_files['test_directory']  # Directory instead of file
    invalid_result2 = validator.validate_executable(game_data['executable_path'])
    assert not invalid_result2.is_valid
    
    game_card.update_validation_status(invalid_result2)
    assert game_card.has_error_indicator(), \
        "Card should show error indicator after updating back to invalid executable"


@given(game_data=game_data_with_executable_strategy())
@settings(deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_visual_indication_accessibility(qt_app, temp_files, game_data):
    """
    **Feature: game-execution-bug-fixes, Property 7: Visual indication of invalid executables**
    **Validates: Requirements 3.3**
    
    For any game card with validation status, visual indicators should be accessible
    and provide meaningful information to users.
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
    
    validator = ExecutableValidator()
    validation_result = validator.validate_executable(executable_path)
    
    game_card = GameCardWidget(game_data)
    game_card.update_validation_status(validation_result)
    
    # Check tooltip accessibility
    tooltip = game_card.toolTip()
    if not validation_result.is_valid:
        assert tooltip and len(tooltip.strip()) > 0, \
            "Invalid executable should have informative tooltip"
        assert any(keyword in tooltip.lower() for keyword in ['error', 'invalid', 'missing', 'not found', 'permission']), \
            f"Tooltip should contain relevant error information. Tooltip: {tooltip}"
    
    # Check that visual indicators don't interfere with basic functionality
    assert game_card.game_id == game_data['id'], \
        "Visual indicators should not affect game ID access"
    assert game_card.game_title == game_data['title'], \
        "Visual indicators should not affect game title access"
    
    # Verify that the card is still interactive
    assert game_card.isEnabled(), \
        "Game card should remain enabled even with validation errors"