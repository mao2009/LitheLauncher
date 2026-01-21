import unittest
from unittest.mock import patch, MagicMock
from PySide6.QtCore import QRunnable, QObject, Signal, QSize, Qt
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtWidgets import QApplication
from pathlib import Path
from src.image_loader import ImageLoader

class TestImageLoader(unittest.TestCase):
    _app = None

    @classmethod
    def setUpClass(cls):
        if not QApplication.instance():
            cls._app = QApplication([])
        else:
            cls._app = QApplication.instance()

    @classmethod
    def tearDownClass(cls):
        if cls._app and cls._app is not QApplication.instance():
            cls._app.quit()
            cls._app = None

    def setUp(self):
        self.dummy_image_content = b"dummy_image_content"
        self.dummy_source_path = Path("dummy_image.png")
        with open(self.dummy_source_path, "wb") as f:
            f.write(self.dummy_image_content)
        self.target_size = QSize(200, 300)
        self.request_id = 42

    def tearDown(self):
        if self.dummy_source_path.exists():
            self.dummy_source_path.unlink()

    def test_image_loader_creation(self):
        loader = ImageLoader(Path("dummy_path.png"), self.target_size, self.request_id)
        self.assertIsInstance(loader, ImageLoader)
        self.assertIsInstance(loader, QRunnable)
        self.assertEqual(loader.target_size, self.target_size)
        self.assertEqual(loader.request_id, self.request_id)

    def test_image_loader_signals_exists(self):
        loader = ImageLoader(Path("dummy_path.png"), self.target_size, self.request_id)
        self.assertTrue(hasattr(loader, 'signals'))
        self.assertIsInstance(loader.signals, QObject)

        self.assertTrue(hasattr(loader.signals, 'image_loaded'))
        self.assertTrue(hasattr(loader.signals, 'image_load_failed'))

    def test_run_loads_scales_and_emits_qimage(self):
        # Create a real 100x100 white image to test scaling
        from PIL import Image
        real_image_path = Path("test_actual_image.png")
        img = Image.new('RGB', (100, 100), color = 'white')
        img.save(real_image_path)
        
        try:
            target_size = QSize(50, 50)
            request_id = 123
            loader = ImageLoader(real_image_path, target_size, request_id)
            
            mock_slot = MagicMock()
            loader.signals.image_loaded.connect(mock_slot)
            
            loader.run()
            
            mock_slot.assert_called_once()
            args, _ = mock_slot.call_args
            loaded_image = args[0]
            loaded_id = args[1]
            
            self.assertIsInstance(loaded_image, QImage)
            self.assertEqual(loaded_id, request_id)
            self.assertEqual(loaded_image.size(), target_size)
        finally:
            if real_image_path.exists():
                real_image_path.unlink()

    @patch('src.image_loader.Image')
    def test_run_emits_image_load_failed_on_error(self, MockImage):
        MockImage.open.side_effect = Exception("Load error")
        
        test_path = Path("error_image.png")
        loader = ImageLoader(test_path, self.target_size, self.request_id)
        
        mock_slot = MagicMock()
        loader.signals.image_load_failed.connect(mock_slot)
        
        loader.run()
        
        mock_slot.assert_called_once()