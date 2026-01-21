import pytest
from unittest.mock import MagicMock
from src.game_list_controller import GameListController
from src.game_list_worker import GameListWorker

def test_controller_update_data_chunk_auto_expansion():
    controller = GameListController()
    # Initially data is empty
    assert len(controller.data) == 0
    
    chunk = [{"id": 1}, {"id": 2}]
    controller.update_data_chunk(chunk, 5)
    
    # Should expand to length 7 (offset 5 + chunk size 2)
    assert len(controller.data) == 7
    assert controller.total_items == 7
    assert controller.data[0:5] == [None] * 5
    assert controller.data[5] == {"id": 1}
    assert controller.data[6] == {"id": 2}

def test_controller_update_view_skips_none():
    controller = GameListController()
    controller.set_dimensions(viewport_width=320, viewport_height=400, item_width=100, item_height=100, spacing=10)
    
    # Set total items but data is all None
    controller.set_total_items(10)
    
    # Mock widget factory/pool
    mock_factory = MagicMock()
    controller.set_widget_factory(mock_factory)
    
    # Update view - should not call factory because all data in visible range is None
    controller.update_view(scroll_y=0)
    mock_factory.assert_not_called()
    assert len(controller.visible_widgets) == 0

def test_game_list_worker_stops_on_empty_chunk():
    mock_service = MagicMock()
    mock_service.get_total_game_count.return_value = 100
    # Returns chunk for offset 0, then empty for offset 20
    def get_chunk(offset, limit):
        if offset == 0:
            return [{"id": i} for i in range(20)]
        return []
    mock_service.get_game_list_chunk.side_effect = get_chunk
    
    worker = GameListWorker(mock_service)
    
    captured_chunks = []
    worker.signals.data_chunk_loaded.connect(lambda data, offset: captured_chunks.append(offset))
    
    worker.run()
    
    # Should only have one chunk (offset 0)
    assert captured_chunks == [0]
    # Should not loop forever
