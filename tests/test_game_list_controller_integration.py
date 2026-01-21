import pytest
from PySide6.QtWidgets import QScrollArea, QWidget, QVBoxLayout
from src.game_list_controller import GameListController
from src.game_card_widget import GameCardWidget

@pytest.fixture
def dummy_game_data():
    return [{"id": i, "title": f"Game {i}", "image_path": ""} for i in range(100)]

def test_controller_initial_render(qtbot, dummy_game_data):
    # Setup UI
    scroll_area = QScrollArea()
    content_widget = QWidget()
    scroll_area.setWidget(content_widget)
    scroll_area.setWidgetResizable(True)
    qtbot.addWidget(scroll_area)
    
    # Setup Controller
    controller = GameListController()
    controller.set_dimensions(
        viewport_width=400, 
        viewport_height=600, 
        item_width=120, 
        item_height=200, 
        spacing=10
    )
    controller.set_total_items(len(dummy_game_data))
    
    # We need a way to tell the controller how to create/update widgets
    def factory():
        return GameCardWidget({"id": 0, "title": "", "image_path": ""}, parent=content_widget)
    
    controller.set_widget_factory(factory)
    controller.set_data(dummy_game_data)
    
    # Trigger first render
    controller.update_view(scroll_y=0)
    
    # Verify widgets
    # 400 width, 120 item -> items_per_row = (400+10)//130 = 3
    # 600 height, 200 item -> start_row=0, end_row=(600+210-1)//210 = 3
    # visible: rows 0, 1, 2 -> 9 items
    assert len(controller.pool.active_widgets) == 9

    
    # Check if widgets are correctly positioned
    w0 = controller.visible_widgets[0]
    assert w0.pos().x() == 0
    assert w0.pos().y() == 0
    assert w0.title_label.text() == "Game 0"

def test_controller_scrolling(qtbot, dummy_game_data):
    # Similar setup
    scroll_area = QScrollArea()
    content_widget = QWidget()
    scroll_area.setWidget(content_widget)
    qtbot.addWidget(scroll_area)
    
    controller = GameListController()
    controller.set_dimensions(400, 600, 120, 200, 10)
    controller.set_total_items(len(dummy_game_data))
    controller.set_widget_factory(lambda: GameCardWidget({"id": 0, "title": "", "image_path": ""}, parent=content_widget))
    controller.set_data(dummy_game_data)
    
    # Initial render
    controller.update_view(scroll_y=0)
    initial_widgets = list(controller.visible_widgets.values())
    
    # Scroll down past first row (row_height=210)
    controller.update_view(scroll_y=220)
    
    # Row 0 (index 0,1,2) should be recycled
    # Row 1,2,3,4 (index 3-14) should be visible
    assert 0 not in controller.visible_widgets
    assert 3 in controller.visible_widgets
    
    # Check if one of the initial widgets was reused
    new_widgets = list(controller.visible_widgets.values())
    assert any(w in initial_widgets for w in new_widgets)
