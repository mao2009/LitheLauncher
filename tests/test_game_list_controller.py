import pytest
from src.game_list_controller import GameListController

def test_calculate_visible_range_basic():
    # Setup
    # item: 100x100, spacing: 10, margins: 0
    # viewport: 320x400
    # items_per_row = (320 + 10) // (100 + 10) = 330 // 110 = 3
    # scroll_y: 0
    # start_row = 0 // 110 = 0
    # end_row = (0 + 400 + 110 - 1) // 110 = 509 // 110 = 4
    # visible items should be rows 0, 1, 2, 3 (indices 0 to 11)
    
    controller = GameListController()
    controller.set_dimensions(viewport_width=320, viewport_height=400, item_width=100, item_height=100, spacing=10)
    controller.set_total_items(100)
    
    start, end = controller.get_visible_range(scroll_y=0)
    assert start == 0
    assert end == 12 # 4 rows * 3 items = 12

def test_calculate_visible_range_scrolled():
    controller = GameListController()
    controller.set_dimensions(viewport_width=320, viewport_height=400, item_width=100, item_height=100, spacing=10)
    controller.set_total_items(100)
    
    # scroll_y: 120 (past first row and spacing)
    # start_row = 120 // 110 = 1
    # end_row = (120 + 400 + 110 - 1) // 110 = 629 // 110 = 5
    # visible items: rows 1, 2, 3, 4 (indices 3 to 14)
    start, end = controller.get_visible_range(scroll_y=120)
    assert start == 3
    assert end == 15 # 5 rows * 3 items = 15

def test_calculate_total_height():
    controller = GameListController()
    controller.set_dimensions(viewport_width=320, viewport_height=400, item_width=100, item_height=100, spacing=10)
    controller.set_total_items(10)
    # items_per_row = 3
    # total_rows = (10 + 2) // 3 = 4
    # height = 4 * 110 - 10 = 430
    assert controller.get_total_height() == 430

def test_items_per_row_minimum_one():
    controller = GameListController()
    # viewport too narrow for item + spacing
    controller.set_dimensions(viewport_width=50, viewport_height=400, item_width=100, item_height=100, spacing=10)
    assert controller.get_items_per_row() == 1
