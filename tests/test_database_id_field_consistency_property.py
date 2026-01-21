"""
Property-based tests for database ID field consistency.
**Feature: game-execution-bug-fixes, Property 13: Database ID field consistency**
"""

import pytest
import tempfile
import os
from hypothesis import given, strategies as st, settings, HealthCheck
from src.game_repository import GameRepository
from src.database import initialize_database


# Strategy for generating valid game data for database operations
@st.composite
def game_data_for_db_strategy(draw):
    """Generate game data suitable for database operations."""
    title = draw(st.text(min_size=1, max_size=100).filter(lambda x: x.strip()))
    
    return {
        'title': title,
        'description': draw(st.one_of(st.none(), st.text(max_size=200))),
        'executable_path': draw(st.one_of(st.none(), st.text(max_size=200))),
        'pre_command': draw(st.one_of(st.none(), st.text(max_size=100))),
        'post_command': draw(st.one_of(st.none(), st.text(max_size=100))),
        'save_folder': draw(st.one_of(st.none(), st.text(max_size=200))),
        'sync_enabled': draw(st.integers(min_value=0, max_value=1)),
        'remote_sync_path': draw(st.one_of(st.none(), st.text(max_size=200)))
    }


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    temp_file.close()
    db_path = temp_file.name
    
    # Initialize the database
    initialize_database(db_path)
    
    yield db_path
    
    # Cleanup
    if os.path.exists(db_path):
        os.unlink(db_path)


@given(game_data=game_data_for_db_strategy())
@settings(deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_database_id_field_consistency(temp_db, game_data):
    """
    **Feature: game-execution-bug-fixes, Property 13: Database ID field consistency**
    **Validates: Requirements 5.4**
    
    For any database query that returns game data, the system should use consistent 
    field names for game identification across all components.
    """
    repository = GameRepository(temp_db)
    
    # Add a game to the database
    game_id = repository.add_game(game_data)
    assert isinstance(game_id, int), "Game ID should be an integer"
    assert game_id > 0, "Game ID should be positive"
    
    # Retrieve the game and verify the ID field is consistently named 'id'
    retrieved_game = repository.get_game(game_id)
    assert retrieved_game is not None, "Game should be retrievable after adding"
    
    # Verify that the database returns the game with 'id' field (not 'game_id')
    assert 'id' in retrieved_game, "Database should return games with 'id' field"
    assert retrieved_game['id'] == game_id, f"Retrieved game ID should match: expected {game_id}, got {retrieved_game['id']}"
    
    # Verify that 'game_id' field is NOT present (this was the old inconsistent field name)
    assert 'game_id' not in retrieved_game, "Database should not return 'game_id' field - should use 'id' consistently"
    
    # Verify that all games returned by get_all_games also use 'id' field consistently
    all_games = repository.get_all_games()
    assert len(all_games) >= 1, "Should have at least the game we just added"
    
    for game in all_games:
        assert 'id' in game, "All games from get_all_games should have 'id' field"
        assert isinstance(game['id'], int), "All game IDs should be integers"
        assert game['id'] > 0, "All game IDs should be positive"
        assert 'game_id' not in game, "No games should have 'game_id' field - should use 'id' consistently"


@given(game_data_list=st.lists(game_data_for_db_strategy(), min_size=1, max_size=10))
@settings(deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_multiple_games_id_field_consistency(temp_db, game_data_list):
    """
    **Feature: game-execution-bug-fixes, Property 13: Database ID field consistency**
    **Validates: Requirements 5.4**
    
    For any set of games in the database, all should consistently use the 'id' field
    for identification across all database operations.
    """
    repository = GameRepository(temp_db)
    
    # Clear any existing games from previous test runs (since fixture is reused)
    existing_games = repository.get_all_games()
    for game in existing_games:
        repository.delete_game(game['id'])
    
    # Add multiple games and collect their IDs
    added_game_ids = []
    for game_data in game_data_list:
        game_id = repository.add_game(game_data)
        added_game_ids.append(game_id)
    
    # Retrieve all games and verify consistent ID field usage
    all_games = repository.get_all_games()
    assert len(all_games) == len(game_data_list), "Should retrieve all added games"
    
    # Verify that all games use 'id' field consistently
    retrieved_ids = []
    for game in all_games:
        assert 'id' in game, "Every game should have 'id' field"
        assert 'game_id' not in game, "No game should have 'game_id' field"
        assert isinstance(game['id'], int), "All IDs should be integers"
        assert game['id'] > 0, "All IDs should be positive"
        retrieved_ids.append(game['id'])
    
    # Verify that the IDs match what was returned during addition
    assert set(retrieved_ids) == set(added_game_ids), \
        f"Retrieved IDs should match added IDs: added={sorted(added_game_ids)}, retrieved={sorted(retrieved_ids)}"
    
    # Test individual game retrieval for consistency
    for game_id in added_game_ids:
        individual_game = repository.get_game(game_id)
        assert individual_game is not None, f"Should be able to retrieve game with ID {game_id}"
        assert 'id' in individual_game, f"Individual game {game_id} should have 'id' field"
        assert 'game_id' not in individual_game, f"Individual game {game_id} should not have 'game_id' field"
        assert individual_game['id'] == game_id, f"Individual game ID should match: expected {game_id}, got {individual_game['id']}"


@given(game_data=game_data_for_db_strategy())
@settings(deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_update_operations_id_field_consistency(temp_db, game_data):
    """
    **Feature: game-execution-bug-fixes, Property 13: Database ID field consistency**
    **Validates: Requirements 5.4**
    
    For any game update operation, the ID field should remain consistently named 'id'
    before and after the update.
    """
    repository = GameRepository(temp_db)
    
    # Add a game
    game_id = repository.add_game(game_data)
    
    # Get the game before update
    game_before_update = repository.get_game(game_id)
    assert 'id' in game_before_update, "Game should have 'id' field before update"
    assert 'game_id' not in game_before_update, "Game should not have 'game_id' field before update"
    
    # Update the game with new data
    update_data = {'title': 'Updated Title', 'description': 'Updated Description'}
    repository.update_game(game_id, update_data)
    
    # Get the game after update
    game_after_update = repository.get_game(game_id)
    assert game_after_update is not None, "Game should exist after update"
    assert 'id' in game_after_update, "Game should have 'id' field after update"
    assert 'game_id' not in game_after_update, "Game should not have 'game_id' field after update"
    assert game_after_update['id'] == game_id, f"Game ID should remain consistent after update: expected {game_id}, got {game_after_update['id']}"
    
    # Verify the update actually worked
    assert game_after_update['title'] == 'Updated Title', "Title should be updated"
    assert game_after_update['description'] == 'Updated Description', "Description should be updated"