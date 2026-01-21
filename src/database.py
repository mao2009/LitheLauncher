# src/database.py
import sqlite3
import os
import shutil
import logging
from datetime import datetime
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from contextlib import contextmanager
from src.game_launcher_logger import get_logger

@dataclass
class Column:
    name: str
    type: str
    primary_key: bool = False
    autoincrement: bool = False
    not_null: bool = False
    default: Optional[str] = None
    foreign_key_ref: Optional[str] = None

    def to_sql(self) -> str:
        parts = [f"{self.name} {self.type}"]
        if self.primary_key:
            parts.append("PRIMARY KEY")
        if self.autoincrement:
            parts.append("AUTOINCREMENT")
        if self.not_null:
            parts.append("NOT NULL")
        if self.default is not None:
            parts.append(f"DEFAULT {self.default}")
        return " ".join(parts)

@dataclass
class Table:
    name: str
    columns: Dict[str, Column] = field(default_factory=dict)

    def add_column(self, name: str, type: str, **kwargs):
        self.columns[name] = Column(name=name, type=type, **kwargs)

    def to_sql(self) -> str:
        col_defs = []
        foreign_keys = []
        for col in self.columns.values():
            col_defs.append(col.to_sql())
            if col.foreign_key_ref:
                foreign_keys.append(f"FOREIGN KEY ({col.name}) REFERENCES {col.foreign_key_ref} ON DELETE CASCADE")
        
        all_defs = col_defs + foreign_keys
        return f"CREATE TABLE {self.name} (\n    " + ",\n    ".join(all_defs) + "\n);"

class Schema:
    def __init__(self):
        self.tables: Dict[str, Table] = {}
        self._define_schema()

    def _define_schema(self):
        game = Table("Game")
        game.add_column("id", "INTEGER", primary_key=True, autoincrement=True)
        game.add_column("title", "TEXT", not_null=True)
        game.add_column("description", "TEXT")
        game.add_column("pre_command", "TEXT")
        game.add_column("post_command", "TEXT")
        game.add_column("save_folder", "TEXT")
        game.add_column("sync_enabled", "INTEGER", default="0")
        game.add_column("remote_sync_path", "TEXT")
        game.add_column("executable_path", "TEXT")
        game.add_column("image_path", "TEXT")
        game.add_column("unique_identifier", "TEXT")
        game.add_column("command_line_settings", "TEXT", default="''")
        game.add_column("created_at", "TEXT", not_null=True)
        game.add_column("updated_at", "TEXT", not_null=True)
        self.tables["Game"] = game

        play_session = Table("PlaySession")
        play_session.add_column("id", "INTEGER", primary_key=True, autoincrement=True)
        play_session.add_column("game_id", "INTEGER", not_null=True, foreign_key_ref="Game(id)")
        play_session.add_column("start_time", "REAL", not_null=True)
        play_session.add_column("end_time", "REAL", not_null=True)
        play_session.add_column("duration", "REAL", not_null=True)
        self.tables["PlaySession"] = play_session

    def generate_create_sql(self, table_name: str) -> str:
        return self.tables[table_name].to_sql()

class BackupService:
    def __init__(self, db_path: str, logger: logging.Logger):
        self.db_path = db_path
        self.logger = logger

    def create_backup(self) -> str:
        backup_path = self.db_path + ".bak"
        self.logger.info(f"Creating backup at {backup_path}...")
        shutil.copy2(self.db_path, backup_path)
        return backup_path

    def restore_backup(self):
        backup_path = self.db_path + ".bak"
        if os.path.exists(backup_path):
            self.logger.info(f"Restoring backup from {backup_path}...")
            shutil.copy2(backup_path, self.db_path)
            self.logger.info("Backup restored.")
        else:
            self.logger.error("No backup found to restore.")

class MigrationEngine:
    MIGRATIONS = {
        1: [
            """
            CREATE TABLE IF NOT EXISTS Game (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                pre_command TEXT,
                post_command TEXT,
                save_folder TEXT,
                sync_enabled INTEGER DEFAULT 0,
                remote_sync_path TEXT,
                executable_path TEXT,
                image_path TEXT,
                unique_identifier TEXT,
                command_line_settings TEXT DEFAULT '',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );
            """
        ],
        2: [
            "ALTER TABLE Game ADD COLUMN pre_command TEXT;",
            "ALTER TABLE Game ADD COLUMN post_command TEXT;",
            "ALTER TABLE Game ADD COLUMN save_folder TEXT;",
            "ALTER TABLE Game ADD COLUMN sync_enabled INTEGER DEFAULT 0;",
            "ALTER TABLE Game ADD COLUMN remote_sync_path TEXT;"
        ],
        3: [
            "ALTER TABLE Game ADD COLUMN executable_path TEXT;",
            "ALTER TABLE Game ADD COLUMN image_path TEXT;"
        ],
        4: [
            "ALTER TABLE Game ADD COLUMN unique_identifier TEXT;"
        ],
        5: [
            "ALTER TABLE Game ADD COLUMN command_line_settings TEXT DEFAULT '';"
        ],
        6: [
            """
            CREATE TABLE IF NOT EXISTS PlaySession (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                game_id INTEGER NOT NULL,
                start_time REAL NOT NULL,
                end_time REAL NOT NULL,
                duration REAL NOT NULL,
                FOREIGN KEY (game_id) REFERENCES Game (id) ON DELETE CASCADE
            );
            """
        ]
    }

    def __init__(self, manager: 'DatabaseManager'):
        self.manager = manager
        self.logger = manager.logger
        self.migrations = self.MIGRATIONS.copy()

    def get_current_version(self) -> int:
        try:
            with self.manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='schema_version'")
                if not cursor.fetchone():
                    return self._detect_version_legacy(cursor)
                
                cursor.execute("SELECT MAX(version) FROM schema_version")
                row = cursor.fetchone()
                return row[0] if row and row[0] is not None else 0
        except Exception:
            return 0

    def _detect_version_legacy(self, cursor) -> int:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Game'")
        if not cursor.fetchone():
            return 0
            
        cursor.execute("PRAGMA table_info(Game)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if "command_line_settings" in columns:
            return 5
        if "unique_identifier" in columns:
            return 4
        if "executable_path" in columns:
            return 3
        if "pre_command" in columns:
            return 2
        return 1

    def initialize_migration_tables(self):
        with self.manager.get_connection() as conn:
            conn.execute("CREATE TABLE IF NOT EXISTS schema_version (version INTEGER PRIMARY KEY, applied_at TEXT NOT NULL)")
            conn.execute("""
                CREATE TABLE IF NOT EXISTS migration_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    from_version INTEGER,
                    to_version INTEGER,
                    applied_at TEXT,
                    status TEXT
                )
            """)

    def apply_migrations(self, target_version: int):
        current_version = self.get_current_version()
        if current_version >= target_version:
            self.logger.info(f"Database is up to date (Version {current_version}).")
            return

        self.logger.info(f"Migrating database from version {current_version} to {target_version}...")
        
        for v in range(current_version + 1, target_version + 1):
            self.logger.info(f"Applying migration to version {v}...")
            
            try:
                with self.manager.get_connection() as conn:
                    if v in self.migrations:
                        for sql in self.migrations[v]:
                            try:
                                conn.execute(sql)
                            except sqlite3.OperationalError as e:
                                if "duplicate column name" in str(e):
                                    self.logger.warning(f"Column already exists, skipping: {sql}")
                                else:
                                    raise e
                    
                    conn.execute("INSERT OR REPLACE INTO schema_version (version, applied_at) VALUES (?, ?)", 
                                 (v, datetime.now().isoformat()))
                    conn.execute("INSERT INTO migration_history (from_version, to_version, applied_at, status) VALUES (?, ?, ?, ?)",
                                 (v-1, v, datetime.now().isoformat(), "SUCCESS"))
                self.logger.info(f"Successfully migrated to version {v}.")
            except Exception as e:
                self.logger.error(f"Migration to version {v} failed: {e}")
                with self.manager.get_connection() as conn:
                    conn.execute("INSERT INTO migration_history (from_version, to_version, applied_at, status) VALUES (?, ?, ?, ?)",
                                 (v-1, v, datetime.now().isoformat(), f"FAILED: {e}"))
                raise e

class DatabaseManager:
    LATEST_VERSION = 6
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.logger = get_logger('Database', log_file='game_launcher.log', level=logging.INFO)
        self.schema = Schema()
        self.migration_engine = MigrationEngine(self)
        self.backup_service = BackupService(db_path, self.logger)

    @contextmanager
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def initialize(self):
        self.logger.info(f"Initializing database at {self.db_path}...")
        
        if not os.path.exists(self.db_path):
            self._create_new_database()
        else:
            self._migrate_database()
            
        self.logger.info(f"Database initialization complete.")

    def _create_new_database(self):
        self.logger.info("Creating a new database...")
        try:
            self.migration_engine.initialize_migration_tables()
            
            with self.get_connection() as conn:
                # Execute full schema from Schema class
                for table_name in self.schema.tables:
                    conn.execute(self.schema.generate_create_sql(table_name))
                
                # Record current version
                conn.execute("INSERT INTO schema_version (version, applied_at) VALUES (?, ?)", 
                             (self.LATEST_VERSION, datetime.now().isoformat()))
                conn.execute("INSERT INTO migration_history (from_version, to_version, applied_at, status) VALUES (?, ?, ?, ?)",
                             (0, self.LATEST_VERSION, datetime.now().isoformat(), "SUCCESS"))
            self.logger.info(f"New database created at version {self.LATEST_VERSION}.")
        except Exception as e:
            self.logger.error(f"Migration failed: {e}")
            raise e

    def _migrate_database(self):
        current_version = self.migration_engine.get_current_version()
        if current_version >= self.LATEST_VERSION:
            self.logger.info(f"Database is up to date (Version {current_version}).")
            return

        self.backup_service.create_backup()
        
        try:
            self.migration_engine.initialize_migration_tables()
            self.migration_engine.apply_migrations(self.LATEST_VERSION)
        except Exception as e:
            self.logger.error(f"Migration failed: {e}")
            self.backup_service.restore_backup()
            raise e

def initialize_database(db_path: str):
    manager = DatabaseManager(db_path)
    manager.initialize()
