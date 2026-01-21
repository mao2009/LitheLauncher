# tests/test_database_manager_refactored.py
import unittest
import os
import sqlite3
import tempfile
from src.database import DatabaseManager

class TestDatabaseManagerRefactored(unittest.TestCase):
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

    def test_connection_context_manager_success(self):
        manager = DatabaseManager(self.db_path)
        with manager.get_connection() as conn:
            conn.execute("CREATE TABLE test (id INTEGER)")
            conn.execute("INSERT INTO test VALUES (1)")
        
        # Verify commit
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM test")
        self.assertEqual(cursor.fetchone()[0], 1)
        conn.close()

    def test_connection_context_manager_rollback(self):
        manager = DatabaseManager(self.db_path)
        # Create table first
        with manager.get_connection() as conn:
            conn.execute("CREATE TABLE test (id INTEGER)")
        
        try:
            with manager.get_connection() as conn:
                conn.execute("INSERT INTO test VALUES (2)")
                raise ValueError("Force rollback")
        except ValueError:
            pass
        
        # Verify rollback
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM test")
        self.assertEqual(cursor.fetchone()[0], 0)
        conn.close()
