from PySide6.QtCore import QThreadPool
import multiprocessing

class ImagePool:
    _instance = None

    @classmethod
    def get_instance(cls) -> QThreadPool:
        if cls._instance is None:
            cls._instance = QThreadPool()
            # 画像デコード用なので、CPUコア数に応じつつ、UIスレッドを邪魔しない程度に制限
            # 最小1、最大4スレッド程度に制限（要件2.2: 同時実行数を制限）
            num_cores = multiprocessing.cpu_count()
            max_threads = max(1, min(num_cores - 1, 4))
            cls._instance.setMaxThreadCount(max_threads)
        return cls._instance
