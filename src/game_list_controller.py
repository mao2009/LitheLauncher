from typing import Tuple, List, Dict, Callable, Any
from src.widget_pool import WidgetPool

class GameListController:
    def __init__(self):
        self.viewport_width = 0
        self.viewport_height = 0
        self.item_width = 100
        self.item_height = 100
        self.spacing = 10
        self.total_items = 0
        self.margin_left = 0
        self.margin_top = 0
        self.margin_right = 0
        self.margin_bottom = 0
        
        self.data: List[Dict[str, Any]] = []
        self.pool: WidgetPool = None
        self.visible_widgets: Dict[int, Any] = {} # index -> widget

    def set_dimensions(self, viewport_width: int, viewport_height: int, item_width: int, item_height: int, spacing: int, margins: Tuple[int, int, int, int] = (0, 0, 0, 0)):
        self.viewport_width = viewport_width
        self.viewport_height = viewport_height
        self.item_width = item_width
        self.item_height = item_height
        self.spacing = spacing
        self.margin_left, self.margin_top, self.margin_right, self.margin_bottom = margins

    def set_total_items(self, total: int):
        if self.total_items != total:
            self.total_items = total
            self.data = [None] * total

    def set_widget_factory(self, factory: Callable[[], Any]):
        self.pool = WidgetPool(factory)

    def set_data(self, data: List[Dict[str, Any]]):
        self.total_items = len(data)
        self.data = data
        # Clear current visible widgets
        for w in self.visible_widgets.values():
            w.hide()
            self.pool.release(w)
        self.visible_widgets.clear()

    def update_data_chunk(self, chunk: List[Dict[str, Any]], offset: int):
        """特定のオフセットからチャンクデータを更新する"""
        if not self.data or len(self.data) < offset + len(chunk):
            # 必要に応じて拡張（基本的にはset_total_itemsで確保済みのはず）
            new_len = max(len(self.data) if self.data else 0, offset + len(chunk))
            if not self.data:
                self.data = [None] * new_len
            else:
                self.data.extend([None] * (new_len - len(self.data)))
            self.total_items = new_len
        
        for i, item in enumerate(chunk):
            self.data[offset + i] = item

    def get_items_per_row(self) -> int:
        available_width = self.viewport_width - self.margin_left - self.margin_right
        if available_width <= self.item_width:
            return 1
        return (available_width + self.spacing) // (self.item_width + self.spacing)

    def get_total_height(self) -> int:
        items_per_row = self.get_items_per_row()
        if items_per_row == 0 or self.total_items == 0:
            return 0
        total_rows = (self.total_items + items_per_row - 1) // items_per_row
        return total_rows * (self.item_height + self.spacing) - self.spacing + self.margin_top + self.margin_bottom

    def get_visible_range(self, scroll_y: int) -> Tuple[int, int]:
        items_per_row = self.get_items_per_row()
        if items_per_row == 0 or self.total_items == 0:
            return 0, 0
            
        row_height = self.item_height + self.spacing
        start_row = (scroll_y - self.margin_top) // row_height
        if start_row < 0:
            start_row = 0
            
        # End row: items that are partially visible at the bottom
        end_row = (scroll_y - self.margin_top + self.viewport_height + row_height - 1) // row_height
        
        start_index = start_row * items_per_row
        end_index = min(self.total_items, end_row * items_per_row)
        
        return start_index, end_index

    def update_view(self, scroll_y: int, deferred: bool = False):
        if not self.pool:
            return

        start_idx, end_idx = self.get_visible_range(scroll_y)
        new_visible_indices = set(range(start_idx, end_idx))
        current_visible_indices = set(self.visible_widgets.keys())

        # Remove widgets that are no longer visible
        to_remove = current_visible_indices - new_visible_indices
        for idx in to_remove:
            widget = self.visible_widgets.pop(idx)
            widget.hide()
            self.pool.release(widget)

        # Add or update widgets that are now visible
        for idx in new_visible_indices:
            data = self.data[idx]
            if data is None:
                continue

            if idx not in self.visible_widgets:
                widget = self.pool.acquire()
                widget.update_data(data, deferred=deferred)
                x, y = self.get_item_position(idx)
                widget.move(x, y)
                widget.show()
                self.visible_widgets[idx] = widget
            else:
                # Still visible, maybe just ensure position (for resize)
                x, y = self.get_item_position(idx)
                self.visible_widgets[idx].move(x, y)

    def load_visible_images(self):
        """表示されているすべてのウィジェットの画像読み込みを開始する"""
        for widget in self.visible_widgets.values():
            if hasattr(widget, 'load_image'):
                widget.load_image()

    def get_item_position(self, index: int) -> Tuple[int, int]:
        items_per_row = self.get_items_per_row()
        if items_per_row == 0:
            return 0, 0
        row = index // items_per_row
        col = index % items_per_row
        x = self.margin_left + col * (self.item_width + self.spacing)
        y = self.margin_top + row * (self.item_height + self.spacing)
        return x, y