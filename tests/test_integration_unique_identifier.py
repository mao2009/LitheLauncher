# tests/test_integration_unique_identifier.py

import unittest
import os
import uuid
import tempfile # 追加
import stat # 追加
import platform # 追加
from datetime import datetime # 追加
from typing import Dict, Any
from unittest.mock import patch, MagicMock

from database import initialize_database
from game_repository import GameRepository
from game_service import GameService
from exceptions import GameNotFoundError

class TestIntegrationUniqueIdentifiers(unittest.TestCase):
    """
    Unique identifier featureに関するGameServiceとGameRepositoryの統合テスト。
    """

    def setUp(self):
        """
        テスト環境をセットアップ: テスト用DBの初期化、サービスとリポジトリのインスタンス化。
        """
        self.db_path = "test_unique_identifier.db"
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        initialize_database(self.db_path)  # DBスキーマを初期化
        
        self.repo = GameRepository(self.db_path)
        self.game_service = GameService(self.repo, MagicMock())
        
        # ロガーをモックしてテスト中のファイルI/Oを避ける
        self.logger_patcher = patch('game_service.get_logger')
        self.mock_logger_game_service = self.logger_patcher.start()
        
        self.logger_repo_patcher = patch('game_repository.get_logger')
        self.mock_logger_game_repo = self.logger_repo_patcher.start()

        self._create_test_executables() # 追加

    def tearDown(self):
        """
        テスト環境をクリーンアップ: テスト用DBファイルの削除。
        """
        self._cleanup_test_files() # 追加
        self.logger_patcher.stop()
        self.logger_repo_patcher.stop()
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def _create_test_executables(self): # 追加
        """テスト用の実行可能ファイルを作成する。"""
        # 有効な実行可能ファイル
        with tempfile.NamedTemporaryFile(mode='w', suffix='.exe', delete=False) as temp_file:
            temp_file.write('echo "test executable"')
            self.valid_executable = temp_file.name
        
        # Unix系システムでは実行可能にする
        if os.name != 'nt':
            os.chmod(self.valid_executable, stat.S_IRWXU)
    
    def _cleanup_test_files(self): # 追加
        """一時テストファイルをクリーンアップする。"""
        if os.path.exists(self.valid_executable):
            os.unlink(self.valid_executable)

    def _create_test_game_data(self, title_suffix: str = "") -> Dict[str, Any]:
        """テスト用のゲームデータを作成するヘルパー。"""
        return {
            "title": f"Test Game {title_suffix}",
            "description": "A test game for unique identifiers",
            "pre_command": "",
            "post_command": "",
            "save_folder": "",
            "sync_enabled": 0,
            "remote_sync_path": "",
            "executable_path": self.valid_executable # 修正
        }

    def test_new_game_registration_assigns_unique_identifier_and_persistence(self):
        """
        新規ゲーム登録時にユニーク識別子が割り当てられ、永続化されることを検証する。
        Req 1.1, 1.3, 2.1
        """
        game_data = self._create_test_game_data("New")
        registered_game = self.game_service.register_game(game_data)
        
        self.assertIsNotNone(registered_game)
        self.assertIn("unique_identifier", registered_game)
        self.assertIsNotNone(registered_game["unique_identifier"])
        
        # DBから直接取得して永続化を確認
        retrieved_game = self.repo.get_game(registered_game["id"])
        self.assertIsNotNone(retrieved_game)
        self.assertEqual(retrieved_game["unique_identifier"], registered_game["unique_identifier"])

    def test_existing_game_gets_unique_identifier_on_load_if_missing(self):
        """
        既存ゲームがロードされた際にユニーク識別子が割り当てられ、永続化されることを検証する。
        Req 1.2, 2.1
        """
        # unique_identifierなしでゲームを直接DBに挿入 (GameService.register_gameは既にunique_identifierを生成するはずなので)
        conn = self.repo._connect() # 修正
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO Game (title, description, pre_command, post_command, 
                               save_folder, sync_enabled, remote_sync_path, executable_path, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, ("Old Game No UID", "Description", "", "", "", 0, "", self.valid_executable, datetime.now().isoformat(), datetime.now().isoformat())) # 修正: created_at, updated_at, executable_pathを追加
        game_id_no_uid = cursor.lastrowid
        conn.commit()
        conn.close()

        # GameService経由でゲームをロードし、unique_identifierが割り当てられることを確認
        loaded_game = self.game_service.get_game_details(game_id_no_uid)
        
        self.assertIsNotNone(loaded_game)
        self.assertIn("unique_identifier", loaded_game)
        self.assertIsNotNone(loaded_game["unique_identifier"])
        
        # DBから直接取得して永続化を確認
        retrieved_game = self.repo.get_game(game_id_no_uid)
        self.assertIsNotNone(retrieved_game)
        self.assertEqual(retrieved_game["unique_identifier"], loaded_game["unique_identifier"])

    def test_game_operations_by_unique_identifier(self):
        """
        ユニーク識別子によるゲームの取得、更新、削除を検証する。
        Req 3.1, 3.2, 3.3
        """
        game_data = self._create_test_game_data("Ops")
        registered_game = self.game_service.register_game(game_data)
        unique_id = registered_game["unique_identifier"]

        # 3.1 取得 by unique_identifier
        retrieved_game = self.game_service.get_game_by_unique_identifier(unique_id)
        self.assertIsNotNone(retrieved_game)
        self.assertEqual(retrieved_game["unique_identifier"], unique_id)
        self.assertEqual(retrieved_game["title"], game_data["title"])

        # GameNotFoundErrorの確認
        with self.assertRaises(GameNotFoundError):
            self.game_service.get_game_by_unique_identifier(str(uuid.uuid4())) # 存在しないID

        # 3.2 更新 by unique_identifier
        new_title = "Updated Game Title"
        updated_game_data = self.game_service.update_game_by_unique_identifier(unique_id, {"title": new_title})
        self.assertIsNotNone(updated_game_data)
        self.assertEqual(updated_game_data["title"], new_title)
        
        # DBから直接取得して更新を確認
        db_game_after_update = self.repo.get_game_by_unique_identifier(unique_id)
        self.assertIsNotNone(db_game_after_update)
        self.assertEqual(db_game_after_update["title"], new_title)

        # GameNotFoundErrorの確認
        with self.assertRaises(GameNotFoundError):
            self.game_service.update_game_by_unique_identifier(str(uuid.uuid4()), title="Non Existent")

        # 3.3 削除 by unique_identifier
        self.game_service.delete_game_by_unique_identifier(unique_id)
        
        # 削除されたことを確認
        with self.assertRaises(GameNotFoundError):
            self.game_service.get_game_by_unique_identifier(unique_id)
        
        # GameNotFoundErrorの確認
        with self.assertRaises(GameNotFoundError):
            self.game_service.delete_game_by_unique_identifier(str(uuid.uuid4())) # 存在しないID


    def test_get_game_list_assigns_unique_identifier_if_missing(self):
        """
        get_game_listがunique_identifierがないゲームに割り当て、永続化することを検証する。
        Req 1.2, 2.1
        """
        # unique_identifierなしでゲームを直接DBに挿入
        conn = self.repo._connect() # 修正
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO Game (title, description, pre_command, post_command, 
                               save_folder, sync_enabled, remote_sync_path, executable_path, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, ("Game List No UID", "Description", "", "", "", 0, "", self.valid_executable, datetime.now().isoformat(), datetime.now().isoformat())) # 修正: created_at, updated_at, executable_pathを追加
        game_id_no_uid = cursor.lastrowid
        conn.commit()
        conn.close()

        # GameService経由でゲームリストをロード
        game_list = self.game_service.get_game_list()
        
        found_game = next((g for g in game_list if g["id"] == game_id_no_uid), None)
        
        self.assertIsNotNone(found_game)
        self.assertIn("unique_identifier", found_game)
        self.assertIsNotNone(found_game["unique_identifier"])
        
        # DBから直接取得して永続化を確認
        retrieved_game = self.repo.get_game(game_id_no_uid)
        self.assertIsNotNone(retrieved_game)
        self.assertEqual(retrieved_game["unique_identifier"], found_game["unique_identifier"])

if __name__ == '__main__':
    unittest.main()