import pytest
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QImage
from pathlib import Path
from src.game_card_widget import GameCardWidget

@pytest.fixture
def dummy_game_data():
    return {
        "id": 1,
        "title": "Test Game",
        "image_path": "tests/test_data/test_cover.png"
    }

def test_placeholder_state_on_update_data(qtbot, dummy_game_data, mocker):
    # Mock ImagePool to avoid actual thread starting
    mocker.patch('src.image_pool.ImagePool.get_instance')
    
    widget = GameCardWidget(dummy_game_data)
    
    # 1. 正常なロード開始時の状態確認
    assert widget.property("image_loading") is True
    assert widget.cover_art_label.text() == "Loading..."
    assert widget.cover_art_label.pixmap().isNull()

    # 画像がロードされた状態にする
    image = QImage(10, 10, QImage.Format_RGB32)
    widget._on_image_loaded(image, widget._current_request_id)
    assert widget.property("image_loading") is False
    assert not widget.cover_art_label.pixmap().isNull()

    # 2. データの更新（再利用）時に即座にプレースホルダーに戻るか
    widget.update_data(dummy_game_data)
    assert widget.property("image_loading") is True
    assert widget.cover_art_label.text() == "Loading..."
    assert widget.cover_art_label.pixmap().isNull()

def test_placeholder_state_on_deferred_update(qtbot, dummy_game_data, mocker):
    mocker.patch('src.image_pool.ImagePool.get_instance')
    widget = GameCardWidget(dummy_game_data)
    
    # 3. 遅延ロード時の状態確認 (改善ポイント)
    # 現在の実装では deferred=True の時 image_loading が False になるが、
    # プレースホルダー表示（QSS適用）のためには True もしくは適切なプロパティが必要
    widget.update_data(dummy_game_data, deferred=True)
    
    assert widget.property("image_loading") is True # これを期待するように改善する
    assert widget.cover_art_label.text() == "..."
    assert widget.cover_art_label.pixmap().isNull()

def test_no_image_placeholder_state(qtbot, mocker):
    mocker.patch('src.image_pool.ImagePool.get_instance')
    data_no_image = {"id": 1, "title": "No Image", "image_path": None}
    
    widget = GameCardWidget(data_no_image)
    
    # 4. 画像なしの場合の状態確認
    assert widget.property("image_loading") is False
    assert widget.property("no_image") is True
    assert widget.cover_art_label.text() == "No Cover Art"
