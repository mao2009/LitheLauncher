# tests/test_database.py
import unittest
import os
import sqlite3
import logging
from unittest.mock import patch, MagicMock, call
import tempfile
from src.database import initialize_database

class TestDatabase(unittest.TestCase):
    def setUp(self):
        self.test_file = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.db_path = self.test_file.name
        self.test_file.close()
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def tearDown(self):
        if os.path.exists(self.db_path):
            try:
                os.remove(self.db_path)
            except PermissionError:
                pass
        backup_path = self.db_path + ".bak"
        if os.path.exists(backup_path):
            try:
                os.remove(backup_path)
            except PermissionError:
                pass

    def test_database_initialization_and_table_creation(self):
        self.assertFalse(os.path.exists(self.db_path))
        initialize_database(self.db_path)
        self.assertTrue(os.path.exists(self.db_path))

        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Game';")
            self.assertIsNotNone(cursor.fetchone())

            cursor.execute("PRAGMA table_info(Game);")
            columns = [col[1] for col in cursor.fetchall()]
            expected_columns = [
                "id", "title", "description", "pre_command", 
                "post_command", "save_folder", "sync_enabled", "remote_sync_path",
                "executable_path", "image_path", "unique_identifier", "command_line_settings",
                "created_at", "updated_at"
            ]
            self.assertEqual(sorted(columns), sorted(expected_columns))
        finally:
            conn.close()

    @patch('src.database.get_logger')
    def test_initialize_database_logging_success(self, mock_get_logger):
        mock_logger = mock_get_logger.return_value
        initialize_database(self.db_path)

        mock_get_logger.assert_called_once_with(
            'Database', 
            log_file='game_launcher.log', 
            level=logging.INFO
        )
        # Check for new logging sequence
        mock_logger.info.assert_any_call(f"Initializing database at {self.db_path}...")
        mock_logger.info.assert_any_call("Creating a new database...")
        mock_logger.info.assert_any_call("Database initialization complete.")

    @patch('src.database.get_logger')
    @patch('src.database.sqlite3.connect')
    def test_initialize_database_logging_failure(self, mock_sqlite_connect, mock_get_logger):
        mock_logger = mock_get_logger.return_value
        # Fail during initial connection check or creation
        mock_sqlite_connect.side_effect = sqlite3.Error("Test DB error")

        with self.assertRaises(sqlite3.Error):
            initialize_database(self.db_path)

        mock_logger.error.assert_any_call("Migration failed: Test DB error")

    def test_database_migration_adds_columns(self):
        # Create DB at V1
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE Game (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
        
        initialize_database(self.db_path)

        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            cursor.execute("PRAGMA table_info(Game);")
            column_names = [col[1] for col in cursor.fetchall()]
            self.assertIn("unique_identifier", column_names)
            self.assertIn("command_line_settings", column_names)
            self.assertIn("image_path", column_names)
        finally:
            conn.close()

    def test_play_session_table_creation_and_schema(self):
        initialize_database(self.db_path)
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='PlaySession';")
            self.assertIsNotNone(cursor.fetchone(), "PlaySession table should exist")

            cursor.execute("PRAGMA table_info(PlaySession);")
            columns = [col[1] for col in cursor.fetchall()]
            expected_columns = [
                "id", "game_id", "start_time", "end_time", "duration"
            ]
            self.assertEqual(sorted(columns), sorted(expected_columns), "PlaySession table columns do not match expected schema")

            # Check foreign key constraint
            cursor.execute("PRAGMA foreign_key_list(PlaySession);")
            fk_info = cursor.fetchall()
            self.assertTrue(any(
                fk[2] == 'Game' and fk[3] == 'game_id' and fk[5] == 'CASCADE'
                for fk in fk_info
            ), "Foreign key constraint on game_id with ON DELETE CASCADE should exist")

        finally:
            conn.close()