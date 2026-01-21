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
    
    # Setup LanguageService mock
    mock_language.get_available_languages.return_value = []
    mock_language.settings = MagicMock()
    mock_language.settings.value.return_value = "en_US"
    
    return {
        "game": mock_game,
        "launcher": mock_launcher,
        "language": mock_language
    }

def test_main_window_starts_async_loading(qtbot, mock_services):
    with patch('PySide6.QtCore.QThreadPool.globalInstance') as mock_pool:
        window = MainWindow(
            mock_services["game"],
            mock_services["launcher"],
            mock_services["language"]
        )
        qtbot.addWidget(window)
        
        # Verify that a worker was started
        mock_pool.return_value.start.assert_called()
        args = mock_pool.return_value.start.call_args[0]
        assert isinstance(args[0], GameListWorker)


def test_main_window_handles_async_data(qtbot, mock_services):
    dummy_games = [{"id": 1, "title": "Game 1", "image_path": ""}]
    mock_services["language"].get_available_languages.return_value = []
    
    window = MainWindow(
        mock_services["game"],
        mock_services["launcher"],
        mock_services["language"]
    )
    qtbot.addWidget(window)
    
    # Manually trigger the signal that worker would emit
    with patch.object(window.controller, 'set_data') as mock_set_data:
        with patch.object(window.controller, 'update_view') as mock_update:
            window._on_games_loaded(dummy_games)
            
            mock_set_data.assert_called_once_with(dummy_games)
            mock_update.assert_called_once()
