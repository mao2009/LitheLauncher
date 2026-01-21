import shutil
from pathlib import Path
from typing import Optional
import tempfile
import logging
import os
import uuid # 追加

from PIL import Image
from src.exceptions import ImageValidationError

class ImageManager:
    _TEMP_PREFIX = "img_tmp_" # 一時ディレクトリ名のプレフィックス

    def __init__(self, base_data_dir: Path | None = None):
        self.logger = logging.getLogger('ImageManager')
        self.logger.setLevel(logging.INFO)

        if base_data_dir is None:
            # 外部から指定がない場合は、カレントディレクトリの 'data' を基準とする
            appdata_base_dir = Path("data")
        else:
            # 指定されたパスを基準とする
            appdata_base_dir = Path(base_data_dir) # 文字列をPathオブジェクトに変換
        
        # 'data' サブディレクトリを適切に処理
        if appdata_base_dir.name != "data":
            appdata_base_dir = appdata_base_dir / "data"

        appdata_base_dir.mkdir(parents=True, exist_ok=True)
        
        self._temp_dir = appdata_base_dir / "temp_images"
        self._temp_dir.mkdir(exist_ok=True)
        self.logger.info(f"ImageManager initialized. Temporary image directory: {self._temp_dir}")

    def save_temp_image(self, source_path: Path) -> Path:
        """
        ソース画像を一時ディレクトリにコピーし、一時パスを返す。
        """
        if not source_path.is_file():
            self.logger.error(f"Source image file not found: {source_path}")
            raise FileNotFoundError(f"Source image file not found: {source_path}")

        temp_file_name = f"{uuid.uuid4().hex}_{source_path.name}"
        dest_path = self._temp_dir / temp_file_name
        
        try:
            shutil.copy2(source_path, dest_path)
            self.logger.info(f"Copied {source_path} to temporary location: {dest_path}")
            return dest_path
        except Exception as e:
            self.logger.error(f"Failed to copy image {source_path} to temporary location: {e}")
            raise

    def delete_game_image(self, game_id: str, image_path: Path | None) -> None:
        """
        特定のゲームに関連する画像ファイルを削除する。
        """
        if image_path is None:
            self.logger.info(f"No image_path provided for game_id: {game_id}. Skipping deletion.")
            return

        if not image_path.is_file():
            self.logger.warning(f"Image file not found at {image_path} for game_id: {game_id}. Skipping deletion.")
            return

        try:
            os.remove(image_path)
            self.logger.info(f"Deleted image file: {image_path} for game_id: {game_id}")
        except OSError as e:
            self.logger.error(f"Error deleting image file {image_path} for game_id {game_id}: {e}")
            raise

    def cleanup_temp_image(self, temp_path: Path | None) -> None:
        """
        指定された一時画像を削除する。
        """
        if temp_path is None:
            self.logger.info("No temporary image path provided for cleanup. Skipping.")
            return

        if not temp_path.is_file():
            self.logger.warning(f"Temporary image file not found at {temp_path}. Skipping cleanup.")
            return
        
        try:
            os.remove(temp_path)
            self.logger.info(f"Cleaned up temporary image file: {temp_path}")
        except OSError as e:
            self.logger.error(f"Error cleaning up temporary image file {temp_path}: {e}")
            raise

    def validate_image(self, image_path: Path) -> bool:
        """画像ファイルの有効性をチェックする。"""
        if not image_path.is_file():
            self.logger.warning(f"Image validation failed for {image_path}: File not found")
            raise ImageValidationError(str(image_path), "Image file not found.")
        try:
            with Image.open(image_path) as img:
                img.verify() # 画像の読み込みを試みて破損をチェック
            self.logger.info(f"Image validated successfully: {image_path}")
            return True
        except Exception as e:
            self.logger.warning(f"Image validation failed for {image_path}: {e}")
            raise ImageValidationError(str(image_path), f"Invalid image file: {e}")

    def move_image_from_temp_to_game_data(self, temp_path: Path, game_id: str) -> Path:
        """
        一時画像を最終的な game_id ディレクトリに移動させ、最終パスを返す。
        移動元の一時画像は削除。
        """
        if not temp_path.is_file():
            self.logger.error(f"Failed to move temporary image from {temp_path}: File not found")
            raise FileNotFoundError(f"Temporary image file not found: {temp_path}")

        appdata_base_dir = Path("data")
        dest_dir = appdata_base_dir / game_id / "images"
        dest_dir.mkdir(parents=True, exist_ok=True) # 最終ディレクトリが存在しない場合は作成
        
        final_path = dest_dir / temp_path.name
        
        try:
            shutil.move(temp_path, final_path) # ファイルを移動
            self.logger.info(f"Moved temporary image from {temp_path} to {final_path}")
            return final_path
        except Exception as e:
            self.logger.error(f"Failed to move temporary image from {temp_path} to final destination: {e}")
            raise
