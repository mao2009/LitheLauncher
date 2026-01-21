# tests/test_image_manager.py
import unittest
import os
from pathlib import Path
from unittest.mock import patch, MagicMock
from src.image_manager import ImageManager
import shutil # 追加
import tempfile # 追加

class TestImageManager(unittest.TestCase):
    def setUp(self):
        self.game_id = "test_game_123"
        self.appdata_dir = Path("data") # プロジェクトルートにdataディレクトリがあると仮定
        self.test_image_dir = self.appdata_dir / self.game_id / "images"
        
        # クリーンアップ
        if self.appdata_dir.exists():
            shutil.rmtree(self.appdata_dir)
        self.appdata_dir.mkdir(parents=True, exist_ok=True)
        
        # ImageManager が使用する _temp_dir も作成しておく
        self.temp_images_dir = self.appdata_dir / "temp_images"
        self.temp_images_dir.mkdir(exist_ok=True)

        # テスト用のダミー画像ファイルを作成
        # NamedTemporaryFile を使用して、ユニークな一時ファイル名を生成
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False, dir=self.temp_images_dir) as f:
            f.write(b"dummy_image_content")
            self.dummy_source_path = Path(f.name)

    def tearDown(self):
        if self.appdata_dir.exists():
            shutil.rmtree(self.appdata_dir)
        # NamedTemporaryFile で作成したファイルは、delete=False のため手動で削除
        if self.dummy_source_path.exists():
            os.remove(self.dummy_source_path)

    def test_image_manager_creation(self):
        manager = ImageManager(self.appdata_dir.parent) # 親ディレクトリを渡す
        self.assertIsInstance(manager, ImageManager)
        self.assertEqual(manager._temp_dir, self.appdata_dir / "temp_images")

    def test_move_image_from_temp_to_game_data_skeleton_exists(self):
        manager = ImageManager(self.appdata_dir.parent)
        self.assertTrue(hasattr(manager, 'move_image_from_temp_to_game_data'))
        self.assertTrue(callable(manager.move_image_from_temp_to_game_data))

    def test_delete_game_image_skeleton_exists(self):
        manager = ImageManager(self.appdata_dir.parent)
        self.assertTrue(hasattr(manager, 'delete_game_image'))
        self.assertTrue(callable(manager.delete_game_image))

    def test_move_image_from_temp_to_game_data_should_move_file_and_return_path(self):
        manager = ImageManager(self.appdata_dir.parent)
        
        # 一時ファイルを直接作成
        temp_path = self.dummy_source_path
        
        moved_path = manager.move_image_from_temp_to_game_data(temp_path, self.game_id)
        
        expected_dest_dir = self.appdata_dir / self.game_id / "images"
        expected_dest_path = expected_dest_dir / temp_path.name

        self.assertTrue(expected_dest_dir.is_dir())
        self.assertTrue(expected_dest_path.is_file())
        self.assertFalse(temp_path.is_file()) # 元の一時ファイルが削除されたことを確認
        self.assertEqual(moved_path, expected_dest_path)
        with open(moved_path, "rb") as f:
            self.assertEqual(f.read(), b"dummy_image_content")

    @patch('src.image_manager.shutil.move')
    def test_move_image_from_temp_to_game_data_handles_file_not_found(self, mock_move):
        manager = ImageManager(self.appdata_dir.parent)
        
        # 存在しない一時ファイルパス
        non_existent_temp_path = Path("non_existent_temp.png")

        with self.assertRaisesRegex(FileNotFoundError, "Temporary image file not found"):
            manager.move_image_from_temp_to_game_data(non_existent_temp_path, self.game_id)
        mock_move.assert_not_called() # shutil.move は呼ばれないはず

    @patch('src.image_manager.shutil.move')
    def test_move_image_from_temp_to_game_data_handles_permission_error(self, mock_move):
        manager = ImageManager(self.appdata_dir.parent)
        mock_move.side_effect = PermissionError("Permission denied for move")
        
        # 一時ファイルを直接作成
        temp_path = self.dummy_source_path

        with self.assertRaises(PermissionError):
            manager.move_image_from_temp_to_game_data(temp_path, self.game_id)
        mock_move.assert_called_once()
