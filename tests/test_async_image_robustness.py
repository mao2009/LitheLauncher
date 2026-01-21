import pytest
from unittest.mock import MagicMock
from PySide6.QtCore import Qt, QSize, QTimer
from PySide6.QtGui import QImage
from pathlib import Path
import time
from src.game_card_widget import GameCardWidget
from src.image_loader import ImageLoader

class MockDelayedImageLoader(ImageLoader):
    """シグナル送信を意図的に遅延させるモック"""
    def __init__(self, image_path, target_size, request_id, delay_ms=100):
        super().__init__(image_path, target_size, request_id)
        self.delay_ms = delay_ms

    def run(self):
        # 実際のデコード処理は行うが、送信を遅延させる
        try:
            from PIL import Image
            with Image.open(self.image_path) as pil_image:
                pil_image = pil_image.convert("RGBA")
                width, height = pil_image.size
                qimage = QImage(pil_image.tobytes("raw", "RGBA"), width, height, width * 4, QImage.Format.Format_RGBA8888).copy()
            
            if self.target_size.isValid():
                qimage = qimage.scaled(self.target_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            
            # 遅延
            time.sleep(self.delay_ms / 1000.0)
            self.signals.image_loaded.emit(qimage, self.request_id)
        except Exception:
            self.signals.image_load_failed.emit()

@pytest.fixture
def temp_images(tmp_path):
    img1 = tmp_path / "img1.png"
    img2 = tmp_path / "img2.png"
    from PIL import Image
    Image.new('RGB', (100, 100), color='red').save(img1)
    Image.new('RGB', (100, 100), color='blue').save(img2)
    return img1, img2

def test_race_condition_on_widget_reuse(qtbot, temp_images, mocker):
    """
    高速にデータが更新された際、古いリクエストの結果が無視されることを検証する
    """
    img1_path, img2_path = temp_images
    
    # ImagePool.start をモックして、MockDelayedImageLoader を使用するようにする
    mock_pool = mocker.patch('src.image_pool.ImagePool.get_instance').return_value
    
    # 1つ目のリクエストをキャプチャするためのリスト
    loaders = []
    def start_mock(loader):
        loaders.append(loader)
        # 実際にはスレッドで走らせず、手動でrun()を呼んで制御する
    
    mock_pool.start.side_effect = start_mock
    
    data1 = {"id": 1, "title": "Game 1", "image_path": str(img1_path)}
    data2 = {"id": 2, "title": "Game 2", "image_path": str(img2_path)}
    
    widget = GameCardWidget(data1)
    # リクエスト1が開始されているはず
    assert len(loaders) == 1
    loader1 = loaders[0]
    req_id1 = loader1.request_id
    
    # すかさずデータを更新（ウィジェットの再利用をシミュレート）
    widget.update_data(data2)
    assert len(loaders) == 2
    loader2 = loaders[1]
    req_id2 = loader2.request_id
    
    assert req_id2 > req_id1
    
    # 1. 古いリクエスト(loader1)が完了したと報告する
    # loader1.run() をシミュレートしてシグナルを飛ばす
    # QImageを作成（赤色）
    red_image = QImage(10, 10, QImage.Format_RGB32)
    red_image.fill(Qt.red)
    
    widget._on_image_loaded(red_image, req_id1)
    
    # 表示が更新されてはいけない（pixmapがNullか、あるいは古いままなはず）
    # update_data で Pixmap は一旦クリアされている
    assert widget.cover_art_label.pixmap().isNull()
    assert widget.property("image_loading") is True # まだ最新を待っているはず
    
    # 2. 最新のリクエスト(loader2)が完了
    blue_image = QImage(10, 10, QImage.Format_RGB32)
    blue_image.fill(Qt.blue)
    
    widget._on_image_loaded(blue_image, req_id2)
    
    # 表示が更新される
    assert not widget.cover_art_label.pixmap().isNull()
    assert widget.property("image_loading") is False
    # 色のチェック（簡易的に）
    # QPixmap -> QImage に戻してピクセル確認は重いので、状態遷移が正しいことを主眼にする

def test_corrupted_image_handling(qtbot, tmp_path):
    """破損した画像ファイルに対する挙動を検証する"""
    corrupted_path = tmp_path / "corrupted.png"
    with open(corrupted_path, "w") as f:
        f.write("not an image")
        
    loader = ImageLoader(corrupted_path, QSize(100, 100), 1)
    
    with qtbot.waitSignal(loader.signals.image_load_failed, timeout=1000):
        loader.run()

def test_invalid_path_handling(qtbot):
    """存在しないパスに対する挙動を検証する"""
    invalid_path = Path("non_existent_file.png")
    loader = ImageLoader(invalid_path, QSize(100, 100), 1)
    
    with qtbot.waitSignal(loader.signals.image_load_failed, timeout=1000):
        loader.run()

def test_image_loader_preserves_aspect_ratio(qtbot, tmp_path):
    """ImageLoaderがアスペクト比を維持してスケーリングすることを検証する"""
    # 200x100 (2:1) の画像を作成
    rect_path = tmp_path / "rect.png"
    from PIL import Image
    Image.new('RGB', (200, 100), color='green').save(rect_path)
    
    # 100x100 の枠に収める -> 結果は 100x50 になるはず
    target_size = QSize(100, 100)
    loader = ImageLoader(rect_path, target_size, 1)
    
    mock_slot = MagicMock()
    loader.signals.image_loaded.connect(mock_slot)
    loader.run()
    
    args, _ = mock_slot.call_args
    loaded_image = args[0]
    assert loaded_image.width() == 100
    assert loaded_image.height() == 50

def test_ui_thread_not_blocked_by_update_data(qtbot, temp_images, mocker):
    """update_data がUIスレッドをブロックしない（短時間で復帰する）ことを検証する"""
    img1_path, _ = temp_images
    data = {"id": 1, "title": "Game 1", "image_path": str(img1_path)}
    
    # 重い処理をシミュレートするために ImagePool.start をモック
    mocker.patch('src.image_pool.ImagePool.get_instance')
    
    widget = GameCardWidget(data)
    
    import time
    start_time = time.perf_counter()
    
    # 100回連続で更新しても、UIスレッドの占有時間は極わずかであるはず
    for i in range(100):
        widget.update_data(data)
        
    end_time = time.perf_counter()
    total_time = end_time - start_time
    
    # 100回で0.5秒以下なら十分高速（環境によるが、同期処理ならデコードだけで数秒かかる）
    assert total_time < 0.5
