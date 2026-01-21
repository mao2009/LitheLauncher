import pytest
from unittest.mock import MagicMock
from src.widget_pool import WidgetPool

def test_widget_pool_acquire_new():
    factory = MagicMock(return_value="widget")
    pool = WidgetPool(factory)
    
    w = pool.acquire()
    assert w == "widget"
    assert factory.call_count == 1

def test_widget_pool_acquire_recycled():
    factory = MagicMock()
    factory.side_effect = ["widget1", "widget2"]
    pool = WidgetPool(factory)
    
    w1 = pool.acquire()
    pool.release(w1)
    
    w2 = pool.acquire()
    assert w2 == "widget1"
    assert factory.call_count == 1 # Recycled
