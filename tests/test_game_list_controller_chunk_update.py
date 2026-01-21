import pytest
from src.game_list_controller import GameListController
from unittest.mock import MagicMock

class MockWidget:
    def __init__(self):
        self._hidden = False
        self._moved = (0, 0)
        self._data = None
        self._shown = False

    def hide(self):
        self._hidden = True
        self._shown = False

    def show(self):
        self._shown = True
        self._hidden = False

    def move(self, x, y):
        self._moved = (x, y)

    def update_data(self, data, deferred=False):
        self._data = data

@pytest.fixture
def controller():
    ctrl = GameListController()
    ctrl.set_dimensions(800, 600, 100, 150, 10, (10, 10, 10, 10))
    ctrl.set_widget_factory(lambda: MockWidget())
    return ctrl

def test_set_total_items_initializes_with_none(controller):
    """set_total_itemsがデータをNoneで初期化することを確認"""
    controller.set_total_items(100)
    assert controller.total_items == 100
    assert len(controller.data) == 100
    assert all(item is None for item in controller.data)

def test_update_data_chunk_fills_data_correctly(controller):
    """update_data_chunkが指定位置のデータを更新することを確認"""
    controller.set_total_items(10)
    chunk = [{"id": 1, "title": "Game 1"}, {"id": 2, "title": "Game 2"}]
    controller.update_data_chunk(chunk, 5)
    
    assert controller.data[5] == {"id": 1, "title": "Game 1"}
    assert controller.data[6] == {"id": 2, "title": "Game 2"}
    assert controller.data[4] is None
    assert controller.data[7] is None

def test_update_view_skips_none_data(controller):
    """データがNoneの場合、ウィジェットを表示しない（スキップする）ことを確認"""
    controller.set_total_items(10)
    # 0-5番目はデータなし(None)、6-7番目にデータあり
    controller.update_data_chunk([{"id": 6, "title": "G6"}, {"id": 7, "title": "G7"}], 6)
    
    # 0~10番目が表示範囲内になるように設定（scroll_y=0, viewport=600なら十分入る）
    controller.update_view(0)
    
    # 6, 7番目だけがウィジェット化されているはず
    assert 6 in controller.visible_widgets
    assert 7 in controller.visible_widgets
    assert 0 not in controller.visible_widgets
    assert 5 not in controller.visible_widgets
    
    assert controller.visible_widgets[6]._shown is True
    assert controller.visible_widgets[6]._data == {"id": 6, "title": "G6"}

def test_set_data_still_works_as_before(controller):
    """既存のset_dataが引き続き正しく動作することを確認"""
    data = [{"id": i, "title": f"G{i}"} for i in range(5)]
    controller.set_data(data)
    
    assert controller.total_items == 5
    assert len(controller.data) == 5
    assert controller.data[0] == {"id": 0, "title": "G0"}
