# src/game_repository.py
import sqlite3
from datetime import datetime
import logging
from src.game_launcher_logger import get_logger
from src.exceptions import GameNotFoundError # 追加

class GameRepository:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.logger = get_logger('GameRepository', log_file='game_launcher.log', level=logging.INFO)

    def _connect(self):
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            self.logger.info("Database connection successful.")
            return conn
        except sqlite3.Error as e:
            self.logger.exception("Failed to connect to the database.")
            raise e

    def add_game(self, game_data: dict) -> int:
        conn = self._connect()
        cursor = conn.cursor()

        now = datetime.now().isoformat()

        try:
            cursor.execute(
                """
                INSERT INTO Game (
                    title, description, pre_command, post_command,
                    save_folder, sync_enabled, remote_sync_path, executable_path, image_path, unique_identifier, command_line_settings, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    game_data["title"],
                    game_data.get("description"),
                    game_data.get("pre_command"),
                    game_data.get("post_command"),
                    game_data.get("save_folder"),
                    game_data.get("sync_enabled", 0),
                    game_data.get("remote_sync_path"),
                    game_data.get("executable_path"),
                    game_data.get("image_path", ""),
                    game_data.get("unique_identifier"),
                    game_data.get("command_line_settings", ""),
                    now,
                    now
                )
            )
            game_id = cursor.lastrowid
            conn.commit()
            self.logger.info(f"Game added successfully with ID: {game_id}")
            return game_id
        except sqlite3.Error as e:
            self.logger.exception(f"Failed to add game: {game_data.get('title', 'Unknown')}")
            raise e
        finally:
            conn.close()

    def get_game(self, game_id: int) -> dict | None:
        conn = self._connect()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT
                    id, title, description, pre_command, post_command,
                    save_folder, sync_enabled, remote_sync_path, executable_path,
                    image_path, unique_identifier, command_line_settings, created_at, updated_at
                FROM Game WHERE id = ?
                """, (game_id,))
            game = cursor.fetchone()
            if game:
                game_dict = dict(game)
                # image_path と command_line_settings は DEFAULT '' なので None にはならないが、
                # 念のため get() でアクセスする際はデフォルト値を指定する
                game_dict["image_path"] = game_dict.get("image_path", "")
                game_dict["command_line_settings"] = game_dict.get("command_line_settings", "")
                self.logger.info(f"Successfully retrieved game with ID: {game_id}")
                return game_dict
            else:
                self.logger.warning(f"Game with ID: {game_id} not found.")
                return None
        except sqlite3.Error as e:
            self.logger.exception(f"Failed to retrieve game with ID: {game_id}.")
            raise e
        finally:
            conn.close()

    def get_all_games(self) -> list[dict]:
        conn = self._connect()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT
                    id, title, description, pre_command, post_command,
                    save_folder, sync_enabled, remote_sync_path, executable_path,
                    image_path, unique_identifier, command_line_settings, created_at, updated_at
                FROM Game
                """)
            games = cursor.fetchall()
            self.logger.info(f"Successfully retrieved {len(games)} games.")
            return [dict(game) for game in games]
        except sqlite3.Error as e:
            self.logger.exception("Failed to retrieve all games.")
            raise e
        finally:
            conn.close()

    def get_total_game_count(self) -> int:
        conn = self._connect()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT COUNT(*) FROM Game")
            count = cursor.fetchone()[0]
            self.logger.info(f"Total game count: {count}")
            return count
        except sqlite3.Error as e:
            self.logger.exception("Failed to retrieve total game count.")
            raise e
        finally:
            conn.close()

    def get_games_paginated(self, offset: int, limit: int) -> list[dict]:
        conn = self._connect()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT
                    id, title, description, pre_command, post_command,
                    save_folder, sync_enabled, remote_sync_path, executable_path,
                    image_path, unique_identifier, command_line_settings, created_at, updated_at
                FROM Game
                LIMIT ? OFFSET ?
                """, (limit, offset))
            games = cursor.fetchall()
            self.logger.info(f"Retrieved {len(games)} games (offset: {offset}, limit: {limit}).")
            return [dict(game) for game in games]
        except sqlite3.Error as e:
            self.logger.exception(f"Failed to retrieve paginated games (offset: {offset}, limit: {limit}).")
            raise e
        finally:
            conn.close()

    def update_game(self, game_id: int, game_data: dict) -> None:
        conn = self._connect()
        cursor = conn.cursor()

        now = datetime.now().isoformat()

        set_clauses = []
        args = []

        for key, value in game_data.items():
            if key == "id":
                continue
            set_clauses.append(f"{key} = ?")
            args.append(value)

        set_clauses.append("updated_at = ?")
        args.append(now)

        if not set_clauses:
            self.logger.warning(f"No update data provided for game ID: {game_id}.")
            conn.close()
            return

        sql = f"UPDATE Game SET {', '.join(set_clauses)} WHERE id = ?"
        args.append(game_id)

        try:
            cursor.execute(sql, tuple(args))
            conn.commit()
            if cursor.rowcount == 0:
                self.logger.warning(f"Attempted to update non-existent game with ID: {game_id}.")
            else:
                self.logger.info(f"Game with ID: {game_id} updated successfully.")
        except sqlite3.Error as e:
            self.logger.exception(f"Failed to update game with ID: {game_id}.")
            raise e
        finally:
            conn.close()

    def delete_game(self, game_id: int) -> None:
        conn = self._connect()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM Game WHERE id = ?", (game_id,))
            conn.commit()
            if cursor.rowcount == 0:
                self.logger.warning(f"Attempted to delete non-existent game with ID: {game_id}.")
            else:
                self.logger.info(f"Game with ID: {game_id} deleted successfully.")
        except sqlite3.Error as e:
            self.logger.exception(f"Failed to delete game with ID: {game_id}.")
            raise e
        finally:
            conn.close()

    def update_game_by_unique_identifier(self, unique_id: str, game_data: dict) -> None:
        conn = self._connect()
        cursor = conn.cursor()

        now = datetime.now().isoformat()

        set_clauses = []
        args = []

        for key, value in game_data.items():
            if key == "unique_identifier": # unique_identifier自体は更新対象としない
                continue
            set_clauses.append(f"{key} = ?")
            args.append(value)

        set_clauses.append("updated_at = ?")
        args.append(now)

        if not set_clauses:
            self.logger.warning(f"No update data provided for game with unique_identifier: {unique_id}.")
            conn.close()
            return

        sql = f"UPDATE Game SET {', '.join(set_clauses)} WHERE unique_identifier = ?"
        args.append(unique_id)

        try:
            cursor.execute(sql, tuple(args))
            conn.commit()
            if cursor.rowcount == 0:
                self.logger.warning(f"Attempted to update non-existent game with unique_identifier: {unique_id}.")
                raise GameNotFoundError(unique_id) # GameNotFoundError を発生させる
            else:
                self.logger.info(f"Game with unique_identifier: {unique_id} updated successfully.")
        except sqlite3.Error as e:
            self.logger.exception(f"Failed to update game with unique_identifier: {unique_id}.")
            raise e
        finally:
            conn.close()

    def get_game_by_unique_identifier(self, unique_id: str) -> dict | None:
        conn = self._connect()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT
                    id, title, description, pre_command, post_command,
                    save_folder, sync_enabled, remote_sync_path, executable_path,
                    image_path, unique_identifier, command_line_settings, created_at, updated_at
                FROM Game WHERE unique_identifier = ?
                """, (unique_id,))
            game = cursor.fetchone()
            if game:
                self.logger.info(f"Successfully retrieved game with unique_identifier: {unique_id}")
                return dict(game)
            else:
                self.logger.warning(f"Game with unique_identifier: {unique_id} not found.")
                raise GameNotFoundError(unique_id)
        except sqlite3.Error as e:
            self.logger.exception(f"Failed to retrieve game with unique_identifier: {unique_id}.")
            raise e
        finally:
            conn.close()

    def delete_game_by_unique_identifier(self, unique_id: str) -> None:
        conn = self._connect()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM Game WHERE unique_identifier = ?", (unique_id,))
            conn.commit()
            if cursor.rowcount == 0:
                self.logger.warning(f"Attempted to delete non-existent game with unique_identifier: {unique_id}.")
                raise GameNotFoundError(unique_id)
            else:
                self.logger.info(f"Game with unique_identifier: {unique_id} deleted successfully.")
        except sqlite3.Error as e:
            self.logger.exception(f"Failed to delete game with unique_identifier: {unique_id}.")
            raise e
        finally:
            conn.close()

    def add_play_session(self, game_id: int, start_time: float, end_time: float, duration: float) -> int:
        conn = self._connect()
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                INSERT INTO PlaySession (game_id, start_time, end_time, duration)
                VALUES (?, ?, ?, ?)
                """,
                (game_id, start_time, end_time, duration)
            )
            session_id = cursor.lastrowid
            conn.commit()
            self.logger.info(f"Play session added successfully for game ID: {game_id} with session ID: {session_id}")
            return session_id
        except sqlite3.Error as e:
            self.logger.exception(f"Failed to add play session for game ID: {game_id}.")
            raise e
        finally:
            conn.close()

    def get_total_play_time_for_game(self, game_id: int) -> float:
        conn = self._connect()
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                SELECT SUM(duration) FROM PlaySession WHERE game_id = ?
                """,
                (game_id,)
            )
            total_duration = cursor.fetchone()[0]
            if total_duration is None:
                total_duration = 0.0
            self.logger.info(f"Retrieved total play time for game ID: {game_id}: {total_duration} seconds.")
            return total_duration
        except sqlite3.Error as e:
            self.logger.exception(f"Failed to retrieve total play time for game ID: {game_id}.")
            raise e
        finally:
            conn.close()

    def get_play_session_history_for_game(self, game_id: int) -> list[dict]:
        conn = self._connect()
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                SELECT id, game_id, start_time, end_time, duration
                FROM PlaySession WHERE game_id = ?
                ORDER BY start_time ASC
                """,
                (game_id,)
            )
            sessions = cursor.fetchall()
            self.logger.info(f"Retrieved {len(sessions)} play sessions for game ID: {game_id}.")
            return [dict(session) for session in sessions]
        except sqlite3.Error as e:
            self.logger.exception(f"Failed to retrieve play session history for game ID: {game_id}.")
            raise e
        finally:
            conn.close()

    def delete_play_time_data_for_game(self, game_id: int):
        conn = self._connect()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM PlaySession WHERE game_id = ?", (game_id,))
            conn.commit()
            if cursor.rowcount > 0:
                self.logger.info(f"Deleted {cursor.rowcount} play sessions for game ID: {game_id}.")
            else:
                self.logger.warning(f"No play sessions found to delete for game ID: {game_id}.")
        except sqlite3.Error as e:
            self.logger.exception(f"Failed to delete play time data for game ID: {game_id}.")
            raise e
        finally:
            conn.close()