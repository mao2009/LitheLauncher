import pytest
import os
from src.game_repository import GameRepository
from src.game_service import GameService
from src.image_manager import ImageManager
from src.database import initialize_database

@pytest.fixture
def db_path(tmp_path):
    db = tmp_path / "test_games.db"
    initialize_database(str(db))
    return str(db)

@pytest.fixture
def repository(db_path):
    return GameRepository(db_path)

@pytest.fixture
def service(repository, tmp_path):
    image_manager = ImageManager(tmp_path)
    return GameService(repository, image_manager)

def test_repository_get_total_game_count(repository):
    # Setup: Add some games
    for i in range(5):
        repository.add_game({"title": f"Game {i}", "unique_identifier": f"id_{i}"})
    
    # Verify
    assert repository.get_total_game_count() == 5

def test_repository_get_games_paginated(repository):
    # Setup: Add 10 games
    for i in range(10):
        repository.add_game({"title": f"Game {i}", "unique_identifier": f"id_{i}"})
    
    # Verify first chunk
    chunk1 = repository.get_games_paginated(offset=0, limit=3)
    assert len(chunk1) == 3
    assert chunk1[0]["title"] == "Game 0"
    
    # Verify second chunk
    chunk2 = repository.get_games_paginated(offset=3, limit=3)
    assert len(chunk2) == 3
    assert chunk2[0]["title"] == "Game 3"
    
    # Verify last partial chunk
    chunk3 = repository.get_games_paginated(offset=9, limit=3)
    assert len(chunk3) == 1
    assert chunk3[0]["title"] == "Game 9"

def test_service_get_game_list_chunk(service, repository):
    # Setup: Add 5 games, some without unique_identifier
    for i in range(5):
        repository.add_game({"title": f"Game {i}"}) # unique_identifier is missing
    
    # Verify service populates unique_identifier when fetching chunk
    chunk = service.get_game_list_chunk(offset=0, limit=5)
    assert len(chunk) == 5
    for game in chunk:
        assert game["unique_identifier"] is not None
        assert len(game["unique_identifier"]) > 0

def test_service_get_game_list_stream(service, repository):
    # Setup: Add 12 games
    for i in range(12):
        repository.add_game({"title": f"Game {i}"})
    
    # Verify stream yielding chunks of 5
    stream = service.get_game_list_stream(chunk_size=5)
    
    # First chunk
    offset, chunk = next(stream)
    assert offset == 0
    assert len(chunk) == 5
    
    # Second chunk
    offset, chunk = next(stream)
    assert offset == 5
    assert len(chunk) == 5
    
    # Third chunk (last)
    offset, chunk = next(stream)
    assert offset == 10
    assert len(chunk) == 2
    
    # End of stream
    with pytest.raises(StopIteration):
        next(stream)
