from PySide6.QtCore import QRunnable, QObject, Signal, QSize, Qt
from PySide6.QtGui import QImage
from pathlib import Path
from PIL import Image

class ImageLoaderSignals(QObject):
    image_loaded = Signal(QImage, int)
    image_load_failed = Signal()

class ImageLoader(QRunnable):
    def __init__(self, image_path: Path, target_size: QSize, request_id: int):
        super().__init__()
        self.image_path = image_path
        self.target_size = target_size
        self.request_id = request_id
        self.signals = ImageLoaderSignals()

    def run(self):
        try:
            # Using PIL for initial decoding as per design document
            with Image.open(self.image_path) as pil_image:
                pil_image = pil_image.convert("RGBA")
                width, height = pil_image.size
                
                # Create QImage from raw bytes
                # We use .copy() to ensure QImage owns the data, 
                # as the PIL buffer will be freed after the 'with' block.
                qimage = QImage(
                    pil_image.tobytes("raw", "RGBA"),
                    width,
                    height,
                    width * 4,
                    QImage.Format.Format_RGBA8888
                ).copy()
            
            # Perform high-quality scaling in the background thread
            if self.target_size.isValid() and not self.target_size.isEmpty():
                qimage = qimage.scaled(
                    self.target_size,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
            
            self.signals.image_loaded.emit(qimage, self.request_id)
        except Exception:
            self.signals.image_load_failed.emit()