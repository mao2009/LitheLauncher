import pytest
import time
from PySide6.QtWidgets import QApplication
from src.main_window import MainWindow
from unittest.mock import MagicMock
from pathlib import Path

@pytest.fixture
def mock_services():
    game_service = MagicMock()
    launcher_service = MagicMock()
    language_service = MagicMock()
    
    # 1000 games
    games = []
    for i in range(1000):
        games.append({
            "id": i,
            "title": f"Game {i}",
            "image_path": "res/icon.png",
            "executable_path": "C:/Windows/notepad.exe"
        })
    
    game_service.get_all_games.return_value = games
    # For async loader, we might need to mock the worker or the signal
    return game_service, launcher_service, language_service, games

def test_startup_performance(qtbot, mock_services):
    game_service, launcher_service, language_service, games = mock_services
    
    start_time = time.perf_counter()
    
    window = MainWindow(game_service, launcher_service, language_service)
    qtbot.addWidget(window)
    window.show()
    
    end_time = time.perf_counter()
    duration = end_time - start_time
    
    print(f"\nStartup duration: {duration:.4f} seconds")
    # Requirement: Less than 0.7 seconds
    assert duration < 0.7

def test_scroll_performance(qtbot, mock_services):
    game_service, launcher_service, language_service, games = mock_services
    window = MainWindow(game_service, launcher_service, language_service)
    qtbot.addWidget(window)
    window.show()
    
    # Manually trigger data load completion if needed (depending on how signals are handled in tests)
    window._on_games_loaded(games)
    
    scroll_bar = window.scroll_area.verticalScrollBar()
    max_scroll = scroll_bar.maximum()
    
    # Measure time for a large scroll jump
    start_time = time.perf_counter()
    scroll_bar.setValue(max_scroll // 2)
    # qtbot.wait(50) is too long for performance measurement. Use processEvents instead.
    QApplication.processEvents() 
    end_time = time.perf_counter()
    
    scroll_duration = end_time - start_time
    print(f"Scroll update duration: {scroll_duration:.4f} seconds")
    # For 60fps, each frame should be < 16.6ms. 
    # Here we allow more for the test environment but focus on the logic overhead.
    assert scroll_duration < 0.1 
