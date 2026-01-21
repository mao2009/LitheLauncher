# src/game_launcher_logger.py
import logging
import os

def get_logger(name: str, log_file: str, level=logging.INFO, console_output=True): # console_output を追加
    # print(f"DEBUG: get_logger called with name={name}") # Debug print removed
    logger = logging.getLogger(name)
    logger.setLevel(level) # ログレベルを設定

    logger.propagate = False # 親ロガーへの伝播を停止
    # 既にハンドラが設定されている場合は追加しない (重複を避けるため)
    if not logger.handlers:
        # フォーマッタを設定
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        # ファイルハンドラ
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        # コンソールハンドラ
        if console_output: # console_output がTrueの場合のみ追加
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)

    return logger