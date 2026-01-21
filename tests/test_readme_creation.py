import unittest
import pytest
import os
import shutil

class TestReadmeCreation(unittest.TestCase):
    """
    README.mdファイルの作成に関するテストクラス。
    """

    def setUp(self):
        self.readme_path = "README.md"
        self.readme_en_path = "README.en.md"
        self.readme_ja_path = "README.ja.md"
        # 各テストの前にREADMEファイルをクリーンアップ (TDDサイクルで手動で作成したファイルが消えないようにコメントアウト)
        # self._backup_and_remove(self.readme_path)
        # self._backup_and_remove(self.readme_en_path)
        # self._backup_and_remove(self.readme_ja_path)

    def tearDown(self):
        # 各テストの後にREADMEファイルを復元 (TDDサイクルで手動で作成したファイルが消えないようにコメントアウト)
        # self._restore_from_backup(self.readme_path)
        # self._restore_from_backup(self.readme_en_path)
        # self._restore_from_backup(self.readme_ja_path)
        pass # TDDサイクルでファイルが残るようにするため、tearDownでは何もしない

    @classmethod
    def _backup_and_remove(cls, path_to_file):
        backup_path = path_to_file + ".bak"
        if os.path.exists(path_to_file):
            shutil.move(path_to_file, backup_path)
        if os.path.exists(path_to_file):
            os.remove(path_to_file)

    @classmethod
    def _restore_from_backup(cls, path_to_file):
        backup_path = path_to_file + ".bak"
        if os.path.exists(path_to_file):
            os.remove(path_to_file)
        if os.path.exists(backup_path):
            shutil.move(backup_path, path_to_file)

    def test_readme_md_exists(self):
        """
        README.mdファイルがプロジェクトのルートに存在することを確認する。
        """
        assert os.path.exists(self.readme_path), f"{self.readme_path} が存在しません。"

    def test_readme_md_initial_content(self):
        """
        README.mdの初期コンテンツが期待通りであること。
        """
        with open(self.readme_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        assert "LitheLauncher" in content
        assert "[English Version (README.en.md)](README.en.md)" in content
        assert "[日本語版 (README.ja.md)](README.ja.md)" in content

    def test_readme_en_md_exists(self):
        """
        README.en.mdファイルがプロジェクトのルートに存在することを確認する。
        """
        assert os.path.exists(self.readme_en_path), f"{self.readme_en_path} が存在しません。"

    def test_readme_en_md_initial_content(self):
        """
        README.en.mdの初期コンテンツが期待通りであること。
        """
        with open(self.readme_en_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        assert "# LitheLauncher" in content
        assert "LitheLauncher is a game launcher application developed in Python. Users can customize their gaming experience through features such as centralized game library management, execution of custom commands before and after game launches, and save data synchronization." in content
        assert "Key Features" in content
        assert "Installation" in content
        assert "Usage" in content
        assert "Contributing" in content
        assert "License" in content

    def test_readme_ja_md_exists(self):
        """
        README.ja.mdファイルがプロジェクトのルートに存在することを確認する。
        """
        assert os.path.exists(self.readme_ja_path), f"{self.readme_ja_path} が存在しません。"

    def test_readme_ja_md_initial_content(self):
        """
        README.ja.mdの初期コンテンツが期待通りであること。
        """
        with open(self.readme_ja_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        assert "# LitheLauncher" in content
        assert "Pythonで開発されたゲームランチャーアプリケーション" in content
        assert "主要機能" in content
        assert "インストール" in content
        assert "利用方法" in content
        assert "貢献" in content
        assert "ライセンス" in content