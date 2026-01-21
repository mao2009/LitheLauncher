from PySide6.QtCore import QRunnable, QObject, Signal
from typing import List, Dict, Any

class GameListWorkerSignals(QObject):
    data_loaded = Signal(list)
    total_determined = Signal(int)
    data_chunk_loaded = Signal(list, int)
    load_failed = Signal(str)
    finished = Signal()

class GameListWorker(QRunnable):
    def __init__(self, game_service):
        super().__init__()
        self.game_service = game_service
        self.signals = GameListWorkerSignals()

    def run(self):
        try:
            total_count = self.game_service.get_total_game_count()
            self.signals.total_determined.emit(total_count)

            # Sequential loading with variable chunk sizes
            # First chunk is small to show results quickly
            initial_chunk_size = 20
            standard_chunk_size = 100

            offset = 0
            while offset < total_count:
                limit = initial_chunk_size if offset == 0 else standard_chunk_size
                chunk = self.game_service.get_game_list_chunk(offset, limit)
                if not chunk:
                    break
                
                self.signals.data_chunk_loaded.emit(chunk, offset)
                offset += len(chunk)

            self.signals.finished.emit()
        except Exception as e:
            self.signals.load_failed.emit(str(e))
