import pytest
from unittest.mock import MagicMock
from src.game_list_worker import GameListWorker
from src.game_service import GameService

def test_game_list_worker_fetches_data_sequentially():
    # Setup
    mock_game_service = MagicMock(spec=GameService)
    mock_game_service.get_total_game_count.return_value = 1
    mock_game_service.get_game_list_chunk.return_value = [{"id": 1, "title": "Game 1"}]
    
    worker = GameListWorker(mock_game_service)
    
    # Spy on signals
    captured_chunks = []
    def on_chunk(data, offset):
        captured_chunks.append((data, offset))
    
    worker.signals.data_chunk_loaded.connect(on_chunk)
    
    # Execute
    worker.run()
    
    # Verify
    mock_game_service.get_total_game_count.assert_called_once()
    mock_game_service.get_game_list_chunk.assert_called_with(0, 20)
    assert len(captured_chunks) == 1
    assert captured_chunks[0] == ([{"id": 1, "title": "Game 1"}], 0)

def test_game_list_worker_emits_sequential_signals_multi_chunk():
    # Setup mock service
    mock_game_service = MagicMock(spec=GameService)
    
    total_count = 120
    mock_game_service.get_total_game_count.return_value = total_count
    
    # Mock get_game_list_chunk
    def mock_get_chunk(offset, limit):
        if offset == 0:
            return [{"id": i} for i in range(20)] # initial_chunk_size is 20
        elif offset == 20:
            return [{"id": i} for i in range(20, 120)] # remaining
        return []
        
    mock_game_service.get_game_list_chunk.side_effect = mock_get_chunk
    
    worker = GameListWorker(mock_game_service)
    
    # Signal spies
    captured_total = []
    captured_chunks = []
    finished_called = [False]
    
    worker.signals.total_determined.connect(lambda n: captured_total.append(n))
    worker.signals.data_chunk_loaded.connect(lambda data, offset: captured_chunks.append((data, offset)))
    worker.signals.finished.connect(lambda: finished_called.__setitem__(0, True))
    
    # Execute
    worker.run()
    
    # Verify
    assert captured_total == [total_count]
    assert len(captured_chunks) == 2
    assert captured_chunks[0] == ([{"id": i} for i in range(20)], 0)
    assert captured_chunks[1] == ([{"id": i} for i in range(20, 120)], 20)
    assert finished_called[0] is True

def test_game_list_worker_emits_error_signal_on_failure():
    # Setup
    mock_game_service = MagicMock(spec=GameService)
    # Fail on the first call
    mock_game_service.get_total_game_count.side_effect = Exception("DB Error")
    
    worker = GameListWorker(mock_game_service)
    
    # Spy on signals
    error_messages = []
    def on_failed(msg):
        error_messages.append(msg)
    
    worker.signals.load_failed.connect(on_failed)
    
    # Execute
    worker.run()
    
    # Verify
    assert error_messages == ["DB Error"]
