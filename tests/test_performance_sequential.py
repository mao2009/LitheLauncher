import pytest
import time
from PySide6.QtCore import QThreadPool
from PySide6.QtWidgets import QApplication
from src.main_window import MainWindow
from src.game_service import GameService
from src.launcher_service import LauncherService
from src.language_service import LanguageService
from src.game_list_worker import GameListWorker
from unittest.mock import MagicMock, patch

@pytest.fixture
def mock_services():
    mock_game = MagicMock(spec=GameService)
    mock_launcher = MagicMock(spec=LauncherService)
    mock_language = MagicMock(spec=LanguageService)
    
    # Setup LanguageService mock
    mock_language.get_available_languages.return_value = []
    mock_language.settings = MagicMock()
    mock_language.settings.value.return_value = "en_US"
    
    # Mock data for 1000 games
    def slow_total_count():
        time.sleep(0.1) # Give test time to setup waitSignal
        return 1000
        
    mock_game.get_total_game_count.side_effect = slow_total_count

    def get_chunk(offset, limit):
        return [{"id": i, "title": f"Game {i}"} for i in range(offset, min(offset + limit, 1000))]
    mock_game.get_game_list_chunk.side_effect = get_chunk
    
    return {
        "game": mock_game,
        "launcher": mock_launcher,
        "language": mock_language
    }

def test_first_chunk_display_performance(qtbot, mock_services):
    # Capture the worker instance when it's created
    captured_worker = None
    original_init = GameListWorker.__init__
    
    def mocked_init(self, *args, **kwargs):
        nonlocal captured_worker
        original_init(self, *args, **kwargs)
        captured_worker = self
        
    with patch.object(GameListWorker, "__init__", mocked_init):
        start_time = time.perf_counter()
        
        window = MainWindow(
            mock_services["game"],
            mock_services["launcher"],
            mock_services["language"]
        )
        qtbot.addWidget(window)
        window.show()
        
        # Wait for the worker to be created
        timeout = time.time() + 2
        while captured_worker is None and time.time() < timeout:
            QApplication.processEvents()
            
        if captured_worker is None:
            pytest.fail("GameListWorker was not created")

        # Wait for the first chunk signal
        with qtbot.waitSignal(captured_worker.signals.data_chunk_loaded, timeout=2000):
            pass
        
        end_time = time.perf_counter()
        duration = end_time - start_time
        
        print(f"\nTime to first chunk: {duration:.4f} seconds")
        assert duration < 0.7
        
        # Verify scrollbar size
        max_scroll = window.scroll_area.verticalScrollBar().maximum()
        print(f"Max scroll: {max_scroll}")
        assert max_scroll > 0
        # 1000 items should produce a large scroll range
        assert max_scroll > 10000 
    
    # Clean up thread pool
    QThreadPool.globalInstance().waitForDone()

def test_responsiveness_during_loading(qtbot, mock_services):
    # Simulate a slow DB to check responsiveness
    def slow_get_chunk(offset, limit):
        time.sleep(0.1) # 100ms delay per chunk
        return [{"id": i, "title": f"Game {i}"} for i in range(offset, min(offset + limit, 1000))]
    
    mock_services["game"].get_game_list_chunk.side_effect = slow_get_chunk
    
    window = MainWindow(
        mock_services["game"],
        mock_services["launcher"],
        mock_services["language"]
    )
    qtbot.addWidget(window)
    window.show()
    
    # While loading is in progress, check if we can resize
    start_resize = time.perf_counter()
    window.resize(800, 600)
    QApplication.processEvents()
    end_resize = time.perf_counter()
    
    resize_duration = end_resize - start_resize
    print(f"Resize duration during load: {resize_duration:.4f} seconds")
    assert resize_duration < 0.05 
    
    # Clean up
    QThreadPool.globalInstance().clear()
    QThreadPool.globalInstance().waitForDone()