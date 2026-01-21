import pytest
from PySide6.QtWidgets import QWidget, QLabel, QMenu
from PySide6.QtGui import QPixmap, QMouseEvent, QImage
from PySide6.QtCore import Qt, QPoint, QSize
from unittest.mock import MagicMock
from pathlib import Path
from src.game_card_widget import GameCardWidget
from src.image_loader import ImageLoader, ImageLoaderSignals
from src.image_pool import ImagePool
import os
from PIL import Image

# Dummy game data for testing
@pytest.fixture
def dummy_game_data():
    return {
        "id": 1,
        "title": "Test Game",
        "image_path": "tests/test_data/test_cover.png"
    }

# Dummy game data without cover art
@pytest.fixture
def dummy_game_data_no_cover():
    return {
        "id": 2,
        "title": "Another Game",
        "image_path": None
    }

# Create a dummy image file for testing cover art
@pytest.fixture(scope="session", autouse=True)
def create_dummy_image():
    test_data_dir = "tests/test_data"
    os.makedirs(test_data_dir, exist_ok=True)
    dummy_image_path = os.path.join(test_data_dir, "test_cover.png")
    img = Image.new('RGB', (600, 900), color = 'black')
    img.save(dummy_image_path)
    yield
    os.remove(dummy_image_path)
    os.rmdir(test_data_dir)


def test_game_card_widget_instantiation(qtbot, dummy_game_data):
    """Test if GameCardWidget can be instantiated."""
    widget = GameCardWidget(dummy_game_data)
    assert widget is not None
    assert widget.game_id == dummy_game_data["id"]
    assert widget.game_title == dummy_game_data["title"]

def test_game_card_widget_title_display(qtbot, dummy_game_data):
    """Test if the game title is displayed correctly."""
    widget = GameCardWidget(dummy_game_data)
    assert widget.title_label.text() == dummy_game_data["title"]

def test_game_card_widget_cover_art_display(qtbot, dummy_game_data, mocker):
    """Test if cover art is loaded and displayed correctly from QImage."""
    mocker.patch('src.image_loader.ImageLoader')
    
    widget = GameCardWidget(dummy_game_data)

    # Create a real QImage
    image = QImage(120, 180, QImage.Format_RGB32)
    image.fill(Qt.black)

    # Call the method that is called when an image is loaded
    widget._on_image_loaded(image, widget._current_request_id)

    # Check if the pixmap was set
    label_pixmap = widget.cover_art_label.pixmap()
    assert label_pixmap is not None
    assert not label_pixmap.isNull()
    assert label_pixmap.width() == 120
    assert label_pixmap.height() == 180

def test_game_card_widget_no_cover_art_display(qtbot, dummy_game_data_no_cover):
    """Test display when no cover art is provided."""
    widget = GameCardWidget(dummy_game_data_no_cover)
    assert widget.cover_art_label.text() == "No Cover Art"
    assert widget.cover_art_label.size().width() == 120
    assert widget.cover_art_label.size().height() == 180

def test_game_card_widget_double_click_signal(qtbot, dummy_game_data, mocker):
    """Test if the launched signal is emitted on double-click."""
    widget = GameCardWidget(dummy_game_data)
    mock_slot = mocker.Mock()
    widget.launched.connect(mock_slot)

    event = QMouseEvent(QMouseEvent.Type.MouseButtonDblClick, QPoint(10, 10), Qt.LeftButton, Qt.LeftButton, Qt.NoModifier)
    widget.mouseDoubleClickEvent(event)

    mock_slot.assert_called_once_with(dummy_game_data["id"])

# Mocking ImageLoader and ImagePool
@pytest.fixture
def mock_image_loader_instance(mocker):
    mock_loader = mocker.MagicMock(spec=ImageLoader)
    mock_loader.signals = mocker.MagicMock(spec=ImageLoaderSignals)
    return mock_loader

@pytest.fixture
def mock_image_pool(mocker):
    mock_instance = mocker.patch('src.image_pool.ImagePool.get_instance', autospec=True)
    mock_pool = mocker.MagicMock()
    mock_instance.return_value = mock_pool
    return mock_pool

def test_game_card_widget_uses_image_loader_for_cover_art(qtbot, dummy_game_data, mocker, mock_image_pool, mock_image_loader_instance):
    mock_image_loader_class = mocker.patch('src.image_loader.ImageLoader', return_value=mock_image_loader_instance)
    dummy_game_data["image_path"] = "/path/to/game_image.png"

    widget = GameCardWidget(dummy_game_data)

    # ImageLoaderが適切な引数でインスタンス化されたことを確認
    mock_image_loader_class.assert_called_once_with(
        Path(dummy_game_data["image_path"]),
        QSize(120, 180),
        1 # 最初のリクエストID
    )
    # ImagePoolにサブミットされたことを確認
    mock_image_pool.start.assert_called_once_with(mock_image_loader_instance)

    # signals.image_loadedとsignals.image_load_failedがconnectされたことを確認
    mock_image_loader_instance.signals.image_loaded.connect.assert_called_once()
    mock_image_loader_instance.signals.image_load_failed.connect.assert_called_once()

    assert widget.cover_art_label.text() == "Loading..."

def test_game_card_widget_displays_placeholder_when_no_image_path(qtbot, dummy_game_data_no_cover, mocker, mock_image_pool):
    widget = GameCardWidget(dummy_game_data_no_cover)

    mock_image_loader_class = mocker.patch('src.game_card_widget.ImageLoader')
    mock_image_loader_class.assert_not_called()
    mock_image_pool.start.assert_not_called()

    assert widget.cover_art_label.text() == "No Cover Art"

def test_game_card_widget_updates_on_image_loaded_signal(qtbot, dummy_game_data, mocker):
    dummy_game_data["image_path"] = "/path/to/game_image.png"
    
    mocker.patch('src.image_loader.ImageLoader')
    widget = GameCardWidget(dummy_game_data)

    widget.cover_art_label.setPixmap = mocker.MagicMock()
    image = QImage(10, 10, QImage.Format_RGB32)

    # Call the slot with correct arguments
    widget._on_image_loaded(image, widget._current_request_id)

    widget.cover_art_label.setPixmap.assert_called_once()
    assert widget.cover_art_label.text() == ""

def test_game_card_widget_ignores_outdated_image_loaded_signal(qtbot, dummy_game_data, mocker):
    dummy_game_data["image_path"] = "/path/to/game_image.png"
    
    mocker.patch('src.image_loader.ImageLoader')
    widget = GameCardWidget(dummy_game_data)
    
    # リクエストIDを強制的に進める
    widget._current_request_id = 2
    
    widget.cover_art_label.setPixmap = mocker.MagicMock()
    image = QImage(10, 10, QImage.Format_RGB32)

    # 古いリクエストID (1) でスロットを呼ぶ
    widget._on_image_loaded(image, 1)

    # setPixmapが呼ばれていないことを確認
    widget.cover_art_label.setPixmap.assert_not_called()

def test_game_card_widget_handles_image_load_failed_signal(qtbot, dummy_game_data, mocker):
    dummy_game_data["image_path"] = "/path/to/game_image.png"
    
    mocker.patch('src.image_loader.ImageLoader')
    widget = GameCardWidget(dummy_game_data)

    widget._on_image_load_failed()

    assert widget.cover_art_label.pixmap() is None or widget.cover_art_label.pixmap().isNull()
    assert widget.cover_art_label.text() == "No Cover Art"