# src/game_service.py
import os
import logging
from pathlib import Path
from typing import Optional, Any, Dict
import uuid
import subprocess # 追加
from src.game_launcher_logger import get_logger
from src.game_repository import GameRepository
from src.executable_validator import ExecutableValidator
from src.exceptions import ExecutableValidationError, GameNotFoundError, ImageValidationError
from src.image_manager import ImageManager

class GameService:
    def __init__(self, game_repository: GameRepository, image_manager: ImageManager): # image_manager を必須引数に
        self.game_repository = game_repository
        self.executable_validator = ExecutableValidator()
        self.logger = get_logger('GameService', log_file='game_launcher.log', level=logging.INFO)
        self.image_manager = image_manager # 外部から注入されたインスタンスを使用

    def register_game(self, game_data: Dict[str, Any], temp_image_path: Path | None = None) -> Dict[str, Any]:
        self.logger.info(f"Attempting to register new game: {game_data.get('title')}")
        
        # unique_identifier がない場合は生成
        if game_data.get("unique_identifier") is None:
            game_data["unique_identifier"] = str(uuid.uuid4().hex)
            self.logger.info(f"Generated new unique_identifier: {game_data['unique_identifier']} for game: {game_data.get('title')}")

        executable_path = game_data.get("executable_path")
        if executable_path:
            validation_result = self.executable_validator.validate_executable(executable_path)
            if not validation_result.is_valid:
                self.logger.error(f"Executable validation failed for game '{game_data.get('title')}': {validation_result.error_message}")
                raise ExecutableValidationError(
                    executable_path, 
                    validation_result.error_type, 
                    validation_result.error_message, 
                    validation_result.suggested_action
                )
        
        # game_data から image_path を削除し、後で改めて設定する
        initial_image_path = game_data.pop("image_path", None)

        try:
            game_id = self.game_repository.add_game(game_data) # まずゲームを登録し、IDを取得
            self.logger.info(f"Game '{game_data.get('title')}' registered successfully with ID: {game_id}, Unique ID: {game_data['unique_identifier']}")

            final_image_path = None
            if temp_image_path:
                # 一時画像を最終的な場所に移動
                final_image_path = self.image_manager.move_image_from_temp_to_game_data(temp_image_path, str(game_id))
                self.game_repository.update_game(game_id, {"image_path": str(final_image_path)})
                self.logger.info(f"Image for game ID: {game_id} moved to {final_image_path}")
            elif initial_image_path: # temp_image_path がないが、image_path があった場合（既存ゲームのimage_pathが渡された場合など）
                # ここでは新規登録なので、基本的にはtemp_image_pathが優先されるべき
                # もしinitial_image_pathがファイルシステム上に存在し、かつそれが一時ファイルでないなら、そのまま利用
                # ただし、新規登録フローではこれは通常発生しないはず
                self.logger.warning(f"No temp_image_path provided for new game {game_id}, but initial_image_path was present: {initial_image_path}. This path will be used as is.")
                self.game_repository.update_game(game_id, {"image_path": initial_image_path})
                final_image_path = Path(initial_image_path)


            registered_game = self.game_repository.get_game(game_id)
            if final_image_path:
                registered_game["image_path"] = str(final_image_path) # 返却するデータにも最新の画像パスを設定
            
            return registered_game
        except ExecutableValidationError as e: # 既存
            self.logger.exception(f"Executable validation error during registration for game: {game_data.get('title')}")
            raise e
        except ImageValidationError as e: # 追加
            self.logger.exception(f"Image validation error during registration for game: {game_data.get('title')}")
            # エラー発生時は、一時ファイルが存在すればクリーンアップを試みる
            if temp_image_path and temp_image_path.is_file():
                try:
                    self.image_manager.cleanup_temp_image(temp_image_path)
                    self.logger.info(f"Cleaned up temporary image {temp_image_path} after failed registration due to ImageValidationError.")
                except Exception as cleanup_e:
                    self.logger.error(f"Failed to clean up temporary image {temp_image_path} during ImageValidationError handling: {cleanup_e}")
            raise e
        except Exception as e:
            self.logger.exception(f"Failed to register game: {game_data.get('title')}")
            # エラー発生時は、一時ファイルが存在すればクリーンアップを試みる
            if temp_image_path and temp_image_path.is_file():
                try:
                    self.image_manager.cleanup_temp_image(temp_image_path)
                    self.logger.info(f"Cleaned up temporary image {temp_image_path} after failed registration.")
                except Exception as cleanup_e:
                    self.logger.error(f"Failed to clean up temporary image {temp_image_path} during error handling: {cleanup_e}")
            raise e

    def finalize_play_session(self, game_id: int, start_time: float, end_time: float, duration: float) -> int:
        self.logger.info(f"Finalizing play session for game ID: {game_id}, duration: {duration}s")
        try:
            session_id = self.game_repository.add_play_session(game_id, start_time, end_time, duration)
            self.logger.info(f"Play session (ID: {session_id}) finalized successfully for game ID: {game_id}.")
            return session_id
        except Exception as e:
            self.logger.exception(f"Failed to finalize play session for game ID: {game_id}.")
            raise e

    def get_play_session_history(self, game_id: int) -> list[dict]:
        """
        指定されたゲームのプレイセッション履歴を返す。
        各辞書は start_time, end_time, duration を含む。
        """
        self.logger.info(f"Retrieving play session history for game ID: {game_id}.")
        try:
            history = self.game_repository.get_play_session_history_for_game(game_id)
            self.logger.info(f"Retrieved {len(history)} play sessions for game ID: {game_id}.")
            return history
        except Exception as e:
            self.logger.exception(f"Failed to retrieve play session history for game ID: {game_id}.")
            return [] # エラー時は空リストを返すか、例外を再throwするかは要件次第。ここでは空リストとする。

    def get_total_play_time(self, game_id: int) -> float:
        """
        指定されたゲームの合計プレイ時間を秒単位で返す。
        """
        self.logger.info(f"Retrieving total play time for game ID: {game_id}.")
        try:
            total_seconds = self.game_repository.get_total_play_time_for_game(game_id)
            self.logger.info(f"Retrieved total play time for game ID: {game_id}: {total_seconds} seconds.")
            return total_seconds
        except Exception as e:
            self.logger.exception(f"Failed to retrieve total play time for game ID: {game_id}.")
            return 0.0 # エラー時は0を返す

    def _format_play_time(self, total_seconds: float) -> str:
        if total_seconds < 0:
            return "N/A" # または適切なエラー表示

        hours = int(total_seconds // 3600)
        minutes = int((total_seconds % 3600) // 60)
        seconds = int(total_seconds % 60)

        parts = []
        if hours > 0:
            parts.append(f"{hours}時間")
        if minutes > 0:
            parts.append(f"{minutes}分")
        if seconds > 0 or (hours == 0 and minutes == 0): # Total play time is 0 or less than a minute
            parts.append(f"{seconds}秒")
        
        return " ".join(parts) if parts else "0秒"

    def get_game_details(self, game_id: int) -> dict | None:
        self.logger.info(f"Attempting to retrieve details for game ID: {game_id}")
        try:
            game_details = self.game_repository.get_game(game_id)
            if game_details:
                if game_details.get("unique_identifier") is None:
                    new_unique_identifier = str(uuid.uuid4().hex)
                    self.logger.info(f"Generated missing unique_identifier: {new_unique_identifier} for game ID: {game_id}")
                    self.game_repository.update_game(game_id, {"unique_identifier": new_unique_identifier})
                    game_details["unique_identifier"] = new_unique_identifier
                
                # プレイ時間を取得してフォーマット
                total_play_time_seconds = self.get_total_play_time(game_id)
                game_details["play_time_seconds"] = total_play_time_seconds # 秒単位の合計プレイ時間も追加
                game_details["play_time_str"] = self._format_play_time(total_play_time_seconds)

                self.logger.info(f"Successfully retrieved details for game ID: {game_id}")
            else:
                self.logger.warning(f"Game with ID: {game_id} not found for details retrieval.")
            return game_details
        except Exception as e:
            self.logger.exception(f"Failed to retrieve details for game ID: {game_id}.")
            raise e

    def get_game_list(self) -> list[dict]:
        self.logger.info("Attempting to retrieve all games.")
        try:
            game_list = self.game_repository.get_all_games()
            
            for game in game_list:
                if game.get("unique_identifier") is None:
                    new_unique_identifier = str(uuid.uuid4().hex)
                    self.logger.info(f"Generated missing unique_identifier: {new_unique_identifier} for game ID: {game['id']}")
                    self.game_repository.update_game(game['id'], {"unique_identifier": new_unique_identifier})
                    game["unique_identifier"] = new_unique_identifier
            
            self.logger.info(f"Successfully retrieved {len(game_list)} games.")
            return game_list
        except Exception as e:
            self.logger.exception("Failed to retrieve game list.")
            raise e

    def get_total_game_count(self) -> int:
        self.logger.info("Retrieving total game count.")
        try:
            return self.game_repository.get_total_game_count()
        except Exception as e:
            self.logger.exception("Failed to retrieve total game count.")
            raise e

    def get_game_list_chunk(self, offset: int, limit: int) -> list[dict]:
        self.logger.info(f"Retrieving game list chunk (offset: {offset}, limit: {limit}).")
        try:
            game_list = self.game_repository.get_games_paginated(offset, limit)
            
            for game in game_list:
                if game.get("unique_identifier") is None:
                    new_unique_identifier = str(uuid.uuid4().hex)
                    self.logger.info(f"Generated missing unique_identifier: {new_unique_identifier} for game ID: {game['id']}")
                    self.game_repository.update_game(game['id'], {"unique_identifier": new_unique_identifier})
                    game["unique_identifier"] = new_unique_identifier
            
            return game_list
        except Exception as e:
            self.logger.exception(f"Failed to retrieve game list chunk (offset: {offset}, limit: {limit}).")
            raise e

    def get_game_list_stream(self, chunk_size: int = 50):
        """
        Yields (offset, chunk_list) pairs.
        """
        self.logger.info(f"Streaming game list with chunk size: {chunk_size}")
        total = self.get_total_game_count()
        for offset in range(0, total, chunk_size):
            yield offset, self.get_game_list_chunk(offset, chunk_size)

    def update_game_details(self, game_id: int, updates: Dict[str, Any], temp_image_path: Path | None = None) -> Dict[str, Any]:
        self.logger.info(f"Attempting to update details for game ID: {game_id} with {updates}")
        try:
            existing_game = self.game_repository.get_game(game_id)
            if not existing_game:
                self.logger.warning(f"Game with ID: {game_id} not found for update.")
                raise GameNotFoundError(f"Game with ID: {game_id} not found for update.")

            if 'executable_path' in updates and updates['executable_path']:
                validation_result = self.executable_validator.validate_executable(updates['executable_path'])
                if not validation_result.is_valid:
                    self.logger.error(f"Executable validation failed for game ID {game_id}: {validation_result.error_message}")
                    raise ExecutableValidationError(
                        updates['executable_path'], 
                        validation_result.error_type, 
                        validation_result.error_message, 
                        validation_result.suggested_action
                    )
            
            old_image_path_str = existing_game.get("image_path")
            old_image_path = Path(old_image_path_str) if old_image_path_str else None
            
            # updates から image_path を一時的に取り除く。これは_temp_image_pathの処理後に再設定される可能性があるため。
            current_image_path_in_updates = updates.pop("image_path", None)

            final_image_path = None
            if temp_image_path:
                # 新しい一時画像が選択された場合のみ、最終的な場所に移動
                final_image_path = self.image_manager.move_image_from_temp_to_game_data(temp_image_path, str(game_id))
                updates["image_path"] = str(final_image_path) # 更新データに新しい画像パスを設定
                self.logger.info(f"Image for game ID: {game_id} moved to {final_image_path}")
            elif current_image_path_in_updates is not None:
                # temp_image_path はないが、updates に image_path が含まれている場合（既存画像を維持またはクリア）
                updates["image_path"] = current_image_path_in_updates
                if current_image_path_in_updates: # 空でなければPathオブジェクトに変換
                    final_image_path = Path(current_image_path_in_updates)
                else: # 空の場合は画像がクリアされた
                    final_image_path = None
            else:
                # updates に image_path がなく、temp_image_pathもない場合、既存のパスを維持
                # このケースは、GameDetailDialog.get_game_data で image_path が updates に含まれない場合に発生
                updates["image_path"] = old_image_path_str
                if old_image_path_str:
                    final_image_path = Path(old_image_path_str)
                else:
                    final_image_path = None

            # 画像パスが変更された場合、古い画像を削除
            # final_image_path が None の場合は、画像がクリアされたケースも含む
            if old_image_path and (final_image_path is None or final_image_path != old_image_path):
                self.image_manager.delete_game_image(str(game_id), old_image_path)
                self.logger.info(f"Old image {old_image_path} for game ID: {game_id} deleted.")

            self.game_repository.update_game(game_id, updates)
            updated_game = self.game_repository.get_game(game_id)
            self.logger.info(f"Game with ID: {game_id} updated successfully.")
            return updated_game
        except ExecutableValidationError as e: # 追加
            self.logger.exception(f"Executable validation error during update for game ID: {game_id}")
            raise e
        except ImageValidationError as e: # 追加
            self.logger.exception(f"Image validation error during update for game ID: {game_id}")
            # エラー発生時は、一時ファイルが存在すればクリーンアップを試みる
            if temp_image_path and temp_image_path.is_file():
                try:
                    self.image_manager.cleanup_temp_image(temp_image_path)
                    self.logger.info(f"Cleaned up temporary image {temp_image_path} after failed update due to ImageValidationError.")
                except Exception as cleanup_e:
                    self.logger.error(f"Failed to clean up temporary image {temp_image_path} during ImageValidationError handling: {cleanup_e}")
            raise e
        except Exception as e:
            self.logger.exception(f"Failed to update game with ID: {game_id}.")
            raise e

    def remove_game(self, game_id: int) -> None:
        self.logger.info(f"Attempting to remove game with ID: {game_id}")
        try:
            existing_game = self.game_repository.get_game(game_id)
            if not existing_game:
                self.logger.warning(f"Game with ID: {game_id} not found for removal.")
                return
            self.game_repository.delete_game(game_id)
            self.game_repository.delete_play_time_data_for_game(game_id) # プレイ時間データも削除
            self.logger.info(f"Game with ID: {game_id} removed successfully.")
        except Exception as e:
            self.logger.exception(f"Failed to remove game with ID: {game_id}.")
            raise e



    def save_game_image(self, game_id: int, source_image_path: Path) -> Path:
        self.logger.info(f"Attempting to save image for game ID: {game_id} from {source_image_path}")
        try:
            game = self.game_repository.get_game(game_id)
            if not game:
                self.logger.warning(f"Game with ID: {game_id} not found for image save.")
                raise ValueError(f"Game with ID: {game_id} not found.")

            copied_image_path = self.image_manager.move_image_from_temp_to_game_data(source_image_path, str(game_id))

            self.game_repository.update_game(game_id, {"image_path": str(copied_image_path)})
            self.logger.info(f"Image for game ID: {game_id} saved successfully to {copied_image_path}")
            return copied_image_path
        except Exception as e:
            self.logger.exception(f"Failed to save image for game ID: {game_id}.")
            raise e

    def get_game_image_path(self, game_id: int) -> Optional[Path]:
        self.logger.info(f"Attempting to get image path for game ID: {game_id}")
        try:
            game = self.game_repository.get_game(game_id)
            if not game:
                self.logger.warning(f"Game with ID: {game_id} not found for image path retrieval.")
                return None
            
            image_path_str = game.get("image_path")
            if image_path_str:
                self.logger.info(f"Retrieved image path for game ID: {game_id}: {image_path_str}")
                return Path(image_path_str)
            else:
                self.logger.info(f"No image path found for game ID: {game_id}.")
                return None
        except Exception as e:
            self.logger.exception(f"Failed to get image path for game ID: {game_id}.")
            raise e

    def get_game_by_unique_identifier(self, unique_id: str) -> dict | None:
        self.logger.info(f"Attempting to retrieve details for game with unique_id: {unique_id}")
        try:
            game_details = self.game_repository.get_game_by_unique_identifier(unique_id)
            if game_details:
                self.logger.info(f"Successfully retrieved details for game with unique_id: {unique_id}")
            else:
                self.logger.warning(f"Game with unique_id: {unique_id} not found for details retrieval.")
                raise GameNotFoundError(unique_id)
            return game_details
        except Exception as e:
            self.logger.exception(f"Failed to retrieve details for game with unique_id: {unique_id}.")
            raise e

    def update_game_by_unique_identifier(self, unique_id: str, updates: Dict[str, Any]) -> dict | None:
        self.logger.info(f"Attempting to update details for game with unique_id: {unique_id} with {updates}")
        try:
            existing_game = self.game_repository.get_game_by_unique_identifier(unique_id)
            if not existing_game:
                self.logger.warning(f"Game with unique_id: {unique_id} not found for update.")
                raise GameNotFoundError(unique_id)

            if 'executable_path' in updates and updates['executable_path']:
                validation_result = self.executable_validator.validate_executable(updates['executable_path'])
                if not validation_result.is_valid:
                    self.logger.error(f"Executable validation failed for game with unique_id {unique_id}: {validation_result.error_message}")
                    raise ExecutableValidationError(
                        updates['executable_path'], 
                        validation_result.error_type, 
                        validation_result.error_message, 
                        validation_result.suggested_action
                    )

            self.game_repository.update_game_by_unique_identifier(unique_id, updates)
            updated_game = self.game_repository.get_game_by_unique_identifier(unique_id)
            self.logger.info(f"Game with unique_id: {unique_id} updated successfully.")
            return updated_game
        except GameNotFoundError as e:
            self.logger.warning(f"Game with unique_id: {unique_id} not found for update (handled by higher level).")
            raise e
        except Exception as e:
            self.logger.exception(f"Failed to update game with unique_id: {unique_id}.")
            raise e

    def delete_game_by_unique_identifier(self, unique_id: str) -> None:
        self.logger.info(f"Attempting to remove game with unique_id: {unique_id}")
        try:
            existing_game = self.game_repository.get_game_by_unique_identifier(unique_id)
            if not existing_game:
                self.logger.warning(f"Game with unique_id: {unique_id} not found for removal.")
                raise GameNotFoundError(unique_id)
            self.game_repository.delete_game_by_unique_identifier(unique_id)
            self.logger.info(f"Game with unique_id: {unique_id} removed successfully.")
        except Exception as e:
            self.logger.exception(f"Failed to remove game with unique_id: {unique_id}.")
            raise e