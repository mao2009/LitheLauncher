from typing import Callable, List, Any

class WidgetPool:
    def __init__(self, factory: Callable[[], Any]):
        self.factory = factory
        self.idle_widgets: List[Any] = []
        self.active_widgets: List[Any] = []

    def acquire(self) -> Any:
        if self.idle_widgets:
            widget = self.idle_widgets.pop()
        else:
            widget = self.factory()
        self.active_widgets.append(widget)
        return widget

    def release(self, widget: Any):
        if widget in self.active_widgets:
            self.active_widgets.remove(widget)
            self.idle_widgets.append(widget)

    def release_all(self):
        self.idle_widgets.extend(self.active_widgets)
        self.active_widgets.clear()
