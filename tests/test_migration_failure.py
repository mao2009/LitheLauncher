# tests/test_migration_failure.py
import unittest
import os
import sqlite3
import shutil
import tempfile
from src.database import DatabaseManager, initialize_database

class TestMigrationFailure(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.test_dir, "test.db")

    def tearDown(self):
        # Ensure any logger handlers are closed if they hold the file
        import logging
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)
            handler.close()
        
        # Try to delete files individually with retry/error handling
        for ext in ["", ".bak"]:
            path = self.db_path + ext
            if os.path.exists(path):
                try:
                    os.remove(path)
                except PermissionError:
                    pass
        
        if os.path.exists(self.test_dir):
            try:
                shutil.rmtree(self.test_dir)
            except PermissionError:
                pass

    def test_migration_failure_and_restoration(self):
        # 1. Create a version 1 database with some data
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("CREATE TABLE Game (id INTEGER PRIMARY KEY, title TEXT, created_at TEXT, updated_at TEXT)")
            conn.execute("INSERT INTO Game (title, created_at, updated_at) VALUES ('Old Game', 'now', 'now')")
        
        # 2. Setup DatabaseManager but mock MigrationEngine to fail at version 2
        manager = DatabaseManager(self.db_path)
        
        # Inject a failing migration
        manager.migration_engine.migrations[2] = ["INVALID SQL STATEMENT;"]
        
        # 3. Attempt initialization - should fail
        with self.assertRaises(sqlite3.Error):
            manager.initialize()
            
        # 4. Verify that the database was restored to its original state (Version 1 data exists)
        self.assertTrue(os.path.exists(self.db_path))
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT title FROM Game")
            row = cursor.fetchone()
            self.assertEqual(row[0], 'Old Game')
            
            # Verify that columns from higher versions are NOT there
            cursor.execute("PRAGMA table_info(Game)")
            columns = [col[1] for col in cursor.fetchall()]
            self.assertNotIn("unique_identifier", columns)
            
        # 5. Check if backup file exists (it should be kept for safety, or at least it existed during the process)
        # Actually our BackupService keeps .bak
        self.assertTrue(os.path.exists(self.db_path + ".bak"))

    def test_backup_creation_failure_stops_migration(self):
        # Create a DB
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("CREATE TABLE Game (id INTEGER PRIMARY KEY, title TEXT, created_at TEXT, updated_at TEXT)")

        manager = DatabaseManager(self.db_path)
        
        # Mock create_backup to fail
        with unittest.mock.patch.object(manager.backup_service, 'create_backup', side_effect=OSError("Backup failed")):
            with self.assertRaises(OSError):
                manager.initialize()
                
        # Database should still be in original state
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='schema_version'")
            self.assertIsNone(cursor.fetchone())
