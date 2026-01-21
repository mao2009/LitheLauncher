import pytest
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QPixmap
from src.game_card_widget import GameCardWidget
from pathlib import Path

@pytest.fixture
def game_data():
    return {
        "id": 1,
        "title": "Test Game",
        "image_path": "res/icon.png",
        "executable_path": "C:/Windows/notepad.exe"
    }

def test_game_card_widget_deferred_loading(qtbot, game_data):
    # widget.update_data(data, deferred=True) should not start loading
    widget = GameCardWidget(game_data)
    qtbot.addWidget(widget)
    
    # Reset cover art label
    widget.cover_art_label.setText("")
    widget.cover_art_label.setPixmap(QPixmap())
    
    # Update with deferred=True
    # This will fail initially because deferred is not an argument
    try:
        widget.update_data(game_data, deferred=True)
    except TypeError:
        pytest.fail("update_data should accept deferred argument")
    
    # Should show placeholder text or title, but not "Loading..."
    assert widget.cover_art_label.text() != "Loading..."
    
    # Call load_image()
    if not hasattr(widget, 'load_image'):
        pytest.fail("GameCardWidget should have load_image method")
    
    widget.load_image()
    assert widget.cover_art_label.text() == "Loading..."

from src.game_list_controller import GameListController
from unittest.mock import MagicMock

def test_controller_deferred_update(game_data):
    controller = GameListController()
    controller.set_dimensions(500, 500, 100, 100, 10)
    controller.set_data([game_data] * 10)
    
    mock_pool = MagicMock()
    mock_widget = MagicMock()
    mock_pool.acquire.return_value = mock_widget
    controller.pool = mock_pool
    
    # Update view with deferred=True
    controller.update_view(0, deferred=True)
    
    # Check that update_data was called with deferred=True
    mock_widget.update_data.assert_called_with(game_data, deferred=True)

def test_controller_load_visible_images(game_data):
    controller = GameListController()
    controller.set_dimensions(500, 500, 100, 100, 10)
    controller.set_data([game_data] * 10)
    
    mock_widget = MagicMock()
    controller.visible_widgets = {0: mock_widget, 1: mock_widget}
    
    # Call load_visible_images
    if not hasattr(controller, 'load_visible_images'):
        pytest.fail("GameListController should have load_visible_images method")
        
    controller.load_visible_images()
    
    # Check that load_image was called
    assert mock_widget.load_image.call_count == 2
