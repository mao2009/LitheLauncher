import pytest
from unittest.mock import MagicMock, patch
from PySide6.QtWidgets import QApplication
from src.main_window import MainWindow
from src.game_service import GameService
from src.launcher_service import LauncherService
from src.language_service import LanguageService
from src.game_list_worker import GameListWorker

@pytest.fixture
def mock_services():
    mock_game = MagicMock(spec=GameService)
    mock_launcher = MagicMock(spec=LauncherService)
    mock_language = MagicMock(spec=LanguageService)
    
    # Setup GameService mock
    mock_game.get_total_game_count.return_value = 0
    
    # Setup LanguageService mock
    mock_language.get_available_languages.return_value = []
    mock_language.settings = MagicMock()
    mock_language.settings.value.return_value = "en_US"
    
    return {
        "game": mock_game,
        "launcher": mock_launcher,
        "language": mock_language
    }

def test_main_window_sequential_loading_integration(qtbot, mock_services):
    # Setup
    window = MainWindow(
        mock_services["game"],
        mock_services["launcher"],
        mock_services["language"]
    )
    qtbot.addWidget(window)
    
    # Verify connections by triggering signals (simulating worker)
    # 1. Total determined
    with patch.object(window.controller, 'set_total_items') as mock_set_total:
        with patch.object(window, '_update_controller_dimensions') as mock_update_dim:
            # We need to find the slot connected to total_determined
            # For now, we assume we will name it _on_total_determined
            if hasattr(window, '_on_total_determined'):
                window._on_total_determined(100)
                mock_set_total.assert_called_once_with(100)
                mock_update_dim.assert_called_once()
            else:
                pytest.fail("MainWindow does not have _on_total_determined slot")

    # 2. Chunk loaded
    dummy_chunk = [{"id": i, "title": f"Game {i}"} for i in range(10)]
    with patch.object(window.controller, 'update_data_chunk') as mock_update_chunk:
        with patch.object(window, '_on_scroll') as mock_on_scroll:
            if hasattr(window, '_on_chunk_loaded'):
                window._on_chunk_loaded(dummy_chunk, 0)
                mock_update_chunk.assert_called_once_with(dummy_chunk, 0)
                mock_on_scroll.assert_called_once()
            else:
                pytest.fail("MainWindow does not have _on_chunk_loaded slot")

    # 3. Finished
    if hasattr(window, '_on_loading_finished'):
        window._on_loading_finished()
        assert window.statusBar().currentMessage() == "Ready"
    else:
        pytest.fail("MainWindow does not have _on_loading_finished slot")
