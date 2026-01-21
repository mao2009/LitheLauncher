import unittest
from PySide6.QtCore import QThreadPool
from src.image_pool import ImagePool

class TestImagePool(unittest.TestCase):
    def test_singleton_instance(self):
        pool1 = ImagePool.get_instance()
        pool2 = ImagePool.get_instance()
        self.assertIs(pool1, pool2)
        self.assertIsInstance(pool1, QThreadPool)

    def test_separate_from_global(self):
        pool = ImagePool.get_instance()
        global_pool = QThreadPool.globalInstance()
        self.assertIsNot(pool, global_pool)

    def test_thread_limit(self):
        pool = ImagePool.get_instance()
        # 同時実行数がシステムリソースに基づいて制限されていることを確認
        # デフォルトのmaxThreadCountは大抵CPU数だが、画像用はそれより抑えるか、あるいは明示的に設定する
        self.assertGreater(pool.maxThreadCount(), 0)
        self.assertLessEqual(pool.maxThreadCount(), 4) # 例として最大4スレッドに制限することを期待

if __name__ == "__main__":
    unittest.main()
