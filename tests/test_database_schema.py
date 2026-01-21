# tests/test_database_schema.py
import unittest
from src.database import Schema

class TestSchema(unittest.TestCase):
    def test_schema_definition(self):
        # Test if Schema class can hold table definitions
        schema = Schema()
        self.assertIn("Game", schema.tables)
        game_table = schema.tables["Game"]
        self.assertIn("id", game_table.columns)
        self.assertEqual(game_table.columns["id"].type, "INTEGER")
        self.assertTrue(game_table.columns["id"].primary_key)

    def test_generate_create_table_sql(self):
        schema = Schema()
        sql = schema.generate_create_sql("Game")
        self.assertIn("CREATE TABLE Game", sql)
        self.assertIn("id INTEGER PRIMARY KEY AUTOINCREMENT", sql)
        self.assertIn("title TEXT NOT NULL", sql)
