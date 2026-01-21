# tests/test_migration_engine.py
import unittest
import sqlite3
import tempfile
import os
from src.database import MigrationEngine, DatabaseManager

class TestMigrationEngine(unittest.TestCase):
    def setUp(self):
        self.test_file = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.db_path = self.test_file.name
        self.test_file.close()
        self.manager = DatabaseManager(self.db_path)

    def tearDown(self):
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_get_current_version_empty_db(self):
        engine = MigrationEngine(self.manager)
        self.assertEqual(engine.get_current_version(), 0)

    def test_initialize_migration_tables(self):
        engine = MigrationEngine(self.manager)
        engine.initialize_migration_tables()
        
        with self.manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='schema_version'")
            self.assertIsNotNone(cursor.fetchone())
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='migration_history'")
            self.assertIsNotNone(cursor.fetchone())

    def test_apply_migrations(self):
        engine = MigrationEngine(self.manager)
        engine.initialize_migration_tables()
        
        # Define some dummy migrations
        engine.migrations = {
            1: ["CREATE TABLE test1 (id INTEGER)"],
            2: ["ALTER TABLE test1 ADD COLUMN name TEXT"]
        }
        
        engine.apply_migrations(target_version=2)
        
        self.assertEqual(engine.get_current_version(), 2)
        
        with self.manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("PRAGMA table_info(test1)")
            cols = [col[1] for col in cursor.fetchall()]
            self.assertIn("id", cols)
            self.assertIn("name", cols)
            
            # Check history
            cursor.execute("SELECT COUNT(*) FROM migration_history WHERE status='SUCCESS'")
            self.assertEqual(cursor.fetchone()[0], 2)
