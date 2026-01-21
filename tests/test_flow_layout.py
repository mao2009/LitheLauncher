import pytest
from PySide6.QtWidgets import QApplication, QWidget, QLabel
from src.flow_layout import FlowLayout

@pytest.fixture(scope="session")
def qapp():
    """Fixture for QApplication."""
    app = QApplication([])
    yield app
    app.quit()

def test_flow_layout_instantiation(qapp):
    """Test if FlowLayout can be instantiated."""
    layout = FlowLayout()
    assert layout is not None

def test_flow_layout_add_item(qapp):
    """Test if items can be added to FlowLayout."""
    layout = FlowLayout()
    widget = QLabel("Test Widget")
    layout.addWidget(widget)
    assert layout.count() == 1
    assert layout.itemAt(0).widget() == widget

def test_flow_layout_geometry_single_line(qapp):
    """Test geometry for a single line of widgets."""
    parent = QWidget()
    layout = FlowLayout(parent)
    widgets = []
    for i in range(3):
        widget = QLabel(f"Widget {i}")
        widget.setFixedSize(50, 20)
        widgets.append(widget)
        layout.addWidget(widget)

    parent.resize(200, 50)
    layout.setGeometry(parent.rect())

    assert widgets[0].geometry().x() == 0 # Should be at the start
    assert widgets[0].geometry().y() == 0
    assert widgets[1].geometry().x() > widgets[0].geometry().x() # Should be to the right of the first
    assert widgets[1].geometry().y() == 0
    assert widgets[2].geometry().x() > widgets[1].geometry().x() # Should be to the right of the second
    assert widgets[2].geometry().y() == 0

def test_flow_layout_geometry_wrapping(qapp):
    """Test geometry for wrapping widgets."""
    parent = QWidget()
    layout = FlowLayout(parent)
    widgets = []
    for i in range(5):
        widget = QLabel(f"Widget {i}")
        widget.setFixedSize(50, 20)
        widgets.append(widget)
        layout.addWidget(widget)

    # Make parent narrow enough to force wrapping
    parent.resize(120, 100) # Should fit 2 widgets per row approximately
    layout.setGeometry(parent.rect())

    # Check if widgets wrap
    assert widgets[0].geometry().y() == 0
    assert widgets[1].geometry().y() == 0
    assert widgets[2].geometry().y() > widgets[0].geometry().y() # Widget 2 should be on the second line
    assert widgets[3].geometry().y() > widgets[0].geometry().y() # Widget 3 should be on the second line
    assert widgets[4].geometry().y() > widgets[2].geometry().y() # Widget 4 should be on the third line


