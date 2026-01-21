# src/launcher_service.py
import subprocess
import os
import time
import logging
from typing import Optional # 追加
from PySide6.QtWidgets import QMessageBox # 追加
import shlex # 追加
import shutil # 追加
from src.game_service import GameService
from src.executable_validator import ExecutableValidator
from src.exceptions import GameNotFoundError, CommandExecutionError, SaveDataSyncError, ExecutableValidationError
from src.game_launcher_logger import get_logger
from pathlib import Path # 追加

class LauncherService:
    def __init__(self, game_service: GameService, remote_storage_service):
        self.game_service = game_service
        self.remote_storage_service = remote_storage_service
        self.executable_validator = ExecutableValidator()
        self.logger = get_logger('LauncherService', log_file='game_launcher.log', level=logging.INFO) # ロガーを取得
        self.status_callback = None # UI更新用のコールバック
        self._active_play_sessions = {} # アクティブなプレイセッションを追跡するための辞書

    def set_status_callback(self, callback):
        """Set a callback function(message: str) to update UI status."""
        self.status_callback = callback

    def _notify_status(self, message: str):
        if self.status_callback:
            self.status_callback(message)

    def _build_command_and_args(self, game_executable_path: Path, command_line_settings: str) -> list[str]:
        """
        ゲームの実行ファイルパスとコマンドライン設定から、subprocess.Popen に渡すコマンドリストを構築する。
        %command% プレースホルダーの置換と、shlex を使用した安全なパースを行う。
        """
        parsed_args = shlex.split(command_line_settings, posix=True) # posix=True はクロスプラットフォームで安定した挙動に役立つ

        if "%command%" in parsed_args:
            # "%command%" プレースホルダーを置換
            final_command_list = [
                str(game_executable_path) if arg == "%command%" else arg
                for arg in parsed_args
            ]
        else:
            # "%command%" が含まれない場合、実行ファイルを先頭に追加
            final_command_list = [str(game_executable_path)] + parsed_args
            
        return final_command_list

    def _launch_executable(self, command_list: list[str]) -> subprocess.Popen:
        """
        Launch an executable with proper cross-platform subprocess handling using a command list.
        
        Args:
            command_list: List of command and arguments to launch
            
        Returns:
            subprocess.Popen: The launched process
            
        Raises:
            CommandExecutionError: If the process fails to start
        """
        import platform
        
        # Resolve absolute path for the main executable in the command_list
        # command_list の最初の要素が実行ファイルパスであると仮定
        executable_path = command_list[0]
        abs_exe_path = os.path.abspath(executable_path)
        
        # Set working directory to the executable's directory
        working_dir = os.path.dirname(abs_exe_path)
        
        # Ensure the executable path in the command list is absolute
        # This prevents issues with relative paths when cwd is set
        final_command_list = command_list.copy()
        final_command_list[0] = abs_exe_path
        
        try:
            # Cross-platform subprocess execution
            # shell=False で引数リストを直接渡すのがより安全で推奨される
            # ただし、Windowsでは.exeファイルはそのまま実行可能
            process = subprocess.Popen(
                final_command_list, # 絶対パスに置換したリストを渡す
                cwd=working_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                shell=False # shlex.split でパース済みなので shell=False が安全
            )
            
            # For Windows with shell=True, we need to check if the process starts successfully
            # by waiting a short time and checking if it's still running or exited with error
            # shell=False に変更したので、このWindows固有のチェックは不要になるが、
            # 起動失敗時の検出を考慮すると、短い待機は有効かもしれない
            import time
            time.sleep(0.1)  # Give the process a moment to start
            
            if process.poll() is not None and process.returncode != 0:
                 # Process has already exited with an error
                stdout, stderr = process.communicate()
                self.logger.error(f"Process exited immediately with code {process.returncode} for command: {command_list[0]}, Stderr: {stderr}")
                raise CommandExecutionError(command_list[0], process.returncode, stdout, stderr)
            
            return process
        except FileNotFoundError as e:
            # Specific error for missing executable files
            error_msg = f"Executable file not found: {abs_exe_path}"
            self.logger.error(f"FileNotFoundError launching {abs_exe_path}: {str(e)}")
            raise CommandExecutionError(abs_exe_path, -1, "", f"FileNotFoundError: {str(e)}")
        except PermissionError as e:
            # Specific error for permission issues
            error_msg = f"Permission denied accessing executable: {abs_exe_path}"
            self.logger.error(f"PermissionError launching {abs_exe_path}: {str(e)}")
            raise CommandExecutionError(abs_exe_path, -1, "", f"PermissionError: {str(e)}")
        except OSError as e:
            # General OS-level errors (includes subprocess creation failures)
            error_msg = f"OS error launching executable: {abs_exe_path}"
            self.logger.error(f"OSError launching {abs_exe_path}: {str(e)}")
            raise CommandExecutionError(abs_exe_path, -1, "", f"OSError: {str(e)}")
        except Exception as e:
            # Catch-all for any other subprocess-related errors
            error_msg = f"Unexpected error launching executable: {abs_exe_path}"
            self.logger.error(f"Unexpected error launching {abs_exe_path}: {str(e)}")
            raise CommandExecutionError(abs_exe_path, -1, "", f"Unexpected error: {str(e)}")

    def execute_command(self, command: str) -> tuple[int, str, str]:
        """
        Execute a command with proper cross-platform handling.
        
        Args:
            command: Command string to execute
            
        Returns:
            tuple: (return_code, stdout, stderr)
        """
        try:
            import platform
            
            # Cross-platform command execution
            if platform.system() == "Windows":
                # On Windows, use shell=True with string for proper command parsing
                result = subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    check=False
                )
            else:
                # On Unix-like systems, use shell=True with string for command parsing
                # This is appropriate for command strings that may contain pipes, redirects, etc.
                result = subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    check=False
                )
            
            # 実行結果をログに出力
            if result.returncode != 0:
                self.logger.error(f"Command failed: {command}, Return Code: {result.returncode}, Stdout: {result.stdout.strip()}, Stderr: {result.stderr.strip()}")
            else:
                self.logger.debug(f"Command executed: {command}, Stdout: {result.stdout.strip()}")

            return result.returncode, result.stdout.strip(), result.stderr.strip()
        except Exception as e:
            self.logger.exception(f"Error executing command: {command}") # logger.exception を使用
            return -1, "", str(e)

    def launch_game(self, game_id: int) -> bool:
        game = self.game_service.get_game_details(game_id)
        if not game:
            self.logger.error(f"Game with ID {game_id} not found.")
            raise GameNotFoundError(game_id)

        game_exe_path_str = game.get("executable_path")
        if not game_exe_path_str:
            self.logger.error(f"Executable path not set for game ID {game_id}.")
            raise ExecutableValidationError("", "missing", "Executable path not set", "Please set the executable path in game settings")
        
        game_exe_path = Path(game_exe_path_str)
        
        validation_result = self.executable_validator.validate_executable(game_exe_path_str)
        if not validation_result.is_valid:
            self.logger.error(f"Executable validation failed for game ID {game_id}: {validation_result.error_message}")
            raise ExecutableValidationError(
                game_exe_path_str, 
                validation_result.error_type, 
                validation_result.error_message, 
                validation_result.suggested_action
            )

        pre_command = game.get("pre_command")
        if pre_command:
            self.logger.info(f"Executing pre-command for game ID {game_id}: {pre_command}")
            returncode, stdout, stderr = self.execute_command(pre_command)
            if returncode != 0:
                self.logger.error(f"Pre-command failed for game ID {game_id}: {pre_command}")
                raise CommandExecutionError(pre_command, returncode, stdout, stderr)
            else:
                self.logger.info(f"Pre-command completed successfully for game ID {game_id}. Output: {stdout}")

        if game.get("sync_enabled") and game.get("remote_sync_path") and game.get("save_folder"):
             self.logger.info(f"Sync enabled for game ID {game_id}. Checking for smart sync...")
             self._notify_status(f"セーブデータを同期中...")
             if not self.sync_save_data(game_id, "smart"):
                 self.logger.error(f"Save data smart sync failed for game ID {game_id}.")
                 self._notify_status(f"同期失敗")
                 raise SaveDataSyncError(game_id, "smart")

        command_line_settings = game.get("command_line_settings", "")
        self.logger.info(f"Launching game ID {game_id} with settings: '{command_line_settings}'")
        self._notify_status(f"ゲームを起動中...")

        try:
            final_command_list = self._build_command_and_args(game_exe_path, command_line_settings)
            
            self.logger.info(f"Final command list for game ID {game_id}: {final_command_list}")
            
            start_time = time.time() # プレイ時間計測開始
            game_process = self._launch_executable(final_command_list)
            self.logger.info(f"Game process started successfully for game ID {game_id}: {game_exe_path_str}")
            self._notify_status(f"実行中: {game.get('title')}")
            
            # アクティブなセッションとして追跡に追加
            self._active_play_sessions[game_id] = {"process": game_process, "start_time": start_time}
            
            exit_code = game_process.wait()
            end_time = time.time() # プレイ時間計測終了
            duration = end_time - start_time
            self.logger.info(f"Game process for game ID {game_id} ({game_exe_path_str}) exited with code {exit_code}")
            
            # セッションが正常に終了したのでアクティブリストから削除
            if game_id in self._active_play_sessions:
                del self._active_play_sessions[game_id]
            
            # プレイセッションを確定し、GameServiceに永続化を依頼
            try:
                self.game_service.finalize_play_session(game_id, start_time, end_time, duration)
            except Exception as play_time_error:
                # プレイ時間の永続化エラーはログに記録するが、ゲーム起動の成功は妨げない
                self.logger.exception(f"Failed to finalize play session for game ID {game_id}: {play_time_error}")
            
            if exit_code != 0:
                self.logger.warning(f"Game process for game ID {game_id} exited with non-zero code: {exit_code}")
            else:
                self.logger.info(f"Game launch completed successfully for game ID {game_id}")
        except Exception as e:
            self.logger.exception(f"Error launching game: {game_exe_path_str}")
            self._notify_status(f"起動エラー")
            raise CommandExecutionError(game_exe_path_str, -1, "", str(e))

        if game.get("sync_enabled") and game.get("remote_sync_path") and game.get("save_folder"):
            self.logger.info(f"Sync enabled for game ID {game_id}. Checking for upload after game exit...")
            self._notify_status(f"セーブデータをアップロード中...")
            if not self.sync_save_data(game_id, "upload"):
                self.logger.error(f"Save data upload failed for game ID {game_id}.")
                self._notify_status(f"アップロード失敗")
                raise SaveDataSyncError(game_id, "upload")

        post_command = game.get("post_command")
        if post_command:
            self.logger.info(f"Executing post-command for game ID {game_id}: {post_command}")
            self._notify_status(f"事後コマンドを実行中...")
            returncode, stdout, stderr = self.execute_command(post_command)
            if returncode != 0:
                self.logger.error(f"Post-command failed for game ID {game_id}: {post_command}")
                self._notify_status(f"事後コマンド失敗")
                raise CommandExecutionError(post_command, returncode, stdout, stderr)
            else:
                self.logger.info(f"Post-command completed successfully for game ID {game_id}. Output: {stdout}")
        
        self.logger.info(f"Game launch workflow completed successfully for game ID {game_id}")
        self._notify_status(f"完了")
        return True

    def _on_launcher_shutdown(self):
        """
        ランチャー終了時に呼び出され、全てのアクティブなプレイセッションを確定する。
        """
        self.logger.info("Launcher shutdown detected. Finalizing active play sessions.")
        sessions_to_finalize = list(self._active_play_sessions.items()) # 変更中に辞書が変更されないようにコピー

        for game_id, session_data in sessions_to_finalize:
            try:
                process = session_data["process"]
                start_time = session_data["start_time"]
                
                # プロセスがまだ実行中であれば終了を待つか、killする（ここでは終了を待つ）
                if process.poll() is None: # プロセスがまだ生きている場合
                    self.logger.warning(f"Game process for ID {game_id} still running during shutdown. Terminating...")
                    process.terminate()
                    process.wait(timeout=5) # 5秒間終了を待つ
                    if process.poll() is None:
                        self.logger.error(f"Game process for ID {game_id} did not terminate gracefully. Killing...")
                        process.kill()
                        process.wait()
                
                end_time = time.time()
                duration = end_time - start_time
                self.game_service.finalize_play_session(game_id, start_time, end_time, duration)
                self.logger.info(f"Finalized play session for game ID {game_id} during shutdown.")
            except Exception as e:
                self.logger.exception(f"Error finalizing play session for game ID {game_id} during shutdown: {e}")
            finally:
                if game_id in self._active_play_sessions:
                    del self._active_play_sessions[game_id]
        self.logger.info("All active play sessions finalized.")

    def sync_save_data(self, game_id: int, direction: str) -> bool:
        game = self.game_service.get_game_details(game_id)
        if not game or not game.get("sync_enabled"):
            self.logger.warning(f"Save data sync not enabled or game not found for game ID {game_id}.")
            return False

        remote_path = game["remote_sync_path"]
        local_path_str = game["save_folder"]
        local_path = Path(local_path_str)

        if not remote_path or not local_path_str:
            self.logger.warning(f"Remote or local path not set for save data sync for game ID {game_id}.")
            return False

        if not self.remote_storage_service:
            self.logger.error(f"Remote storage service not available for game ID {game_id}.")
            return False

        backup_path = None
        download_occurred = False 
        start_time = time.time()

        try:
            target_direction = direction
            
            if direction == "smart":
                self.logger.info(f"Performing smart sync for {game['title']} between {local_path} and {remote_path}")
                local_mtime = self.remote_storage_service.get_latest_mtime(local_path)
                remote_mtime = self.remote_storage_service.get_latest_mtime(Path(remote_path))
                self.logger.info(f"Timestamps for {game['title']} - Local: {local_mtime}, Remote: {remote_mtime}")
                
                # 新旧判定ロジック
                current_time = time.time()
                should_show_dialog = False
                
                if local_mtime > current_time + 3600 or remote_mtime > current_time + 3600:
                    self.logger.warning(f"Detected suspicious future timestamp for {game['title']}. Triggering conflict dialog.")
                    should_show_dialog = True
                elif abs(remote_mtime - local_mtime) < 1.0:
                    self.logger.info(f"Save data is already in sync for {game['title']}. Skipping.")
                    return True
                elif remote_mtime > local_mtime:
                    self.logger.info(f"Remote save data is newer for {game['title']}.")
                    target_direction = "download"
                else:
                    self.logger.info(f"Local save data is newer for {game['title']}. Triggering conflict dialog.")
                    should_show_dialog = True
                
                if should_show_dialog:
                    choice = self._show_sync_conflict_dialog(game['title'], local_mtime, remote_mtime)
                    if choice == "local":
                        target_direction = "upload"
                    elif choice == "remote":
                        target_direction = "download"
                    else:
                        self.logger.info(f"Sync cancelled by user for {game['title']}.")
                        return False

            if target_direction == "download":
                if local_path.exists():
                    backup_path = Path(f"{local_path}_backup_{os.urandom(8).hex()}")
                    self.logger.info(f"Creating local save data backup for game ID {game_id} at {backup_path}")
                    try:
                        shutil.copytree(local_path, backup_path, dirs_exist_ok=True)
                        self.logger.info(f"Successfully created backup at {backup_path}")
                    except Exception as e:
                        self.logger.error(f"Failed to create backup for game ID {game_id} at {backup_path}: {e}")
                        backup_path = None
                
                self.logger.info(f"Downloading save data for {game['title']} from {remote_path} to {local_path}")
                download_occurred = self.remote_storage_service.download_save_data(game_id, remote_path, local_path)
            
            elif target_direction == "upload":
                self.logger.info(f"Uploading save data for {game['title']} from {local_path} to {remote_path}")
                self.remote_storage_service.upload_save_data(game_id, local_path, remote_path)
            
            else:
                error_msg = f"Invalid sync direction: {direction} for game ID {game_id}."
                self.logger.error(error_msg)
                raise SaveDataSyncError(game_id, direction, ValueError(f"Invalid direction: {direction}"))
            
            end_time = time.time()
            duration = end_time - start_time
            self.logger.info(f"Save data sync ({direction}) for {game['title']} completed in {duration:.2f} seconds.")
            return True

        except SaveDataSyncError as e:
            if target_direction == "download" and backup_path and backup_path.exists():
                self.logger.warning(f"Save data download failed for game ID {game_id}: {e}. Attempting to restore from backup at {backup_path}.")
                try:
                    if local_path.exists():
                        shutil.rmtree(local_path)
                    shutil.copytree(backup_path, local_path, dirs_exist_ok=True)
                    self.logger.info(f"Successfully restored local save data for game ID {game_id} from backup.")
                except Exception as restore_e:
                    self.logger.error(f"Failed to restore local save data for game ID {game_id} from backup: {restore_e}")
            elif target_direction == "upload":
                self.logger.warning(f"Save data upload failed for game ID {game_id}: {e}.")
            raise 
        
        except Exception as e:
            self.logger.exception(f"Error during save data sync ({direction}) for game {game_id}.")
            raise SaveDataSyncError(game_id, direction, e)
        
        finally:
            if backup_path and backup_path.exists():
                self.logger.info(f"Attempting to delete backup at {backup_path} in finally block.")
                try:
                    shutil.rmtree(backup_path)
                    self.logger.info(f"Successfully deleted backup at {backup_path}.")
                except Exception as e:
                    self.logger.error(f"Failed to delete backup at {backup_path} in finally block: {e}")

    def validate_command_line_settings(self, settings_string: str) -> tuple[bool, Optional[str]]:
        """
        コマンドライン設定文字列の基本的なバリデーションを行う。
        shlex.split を使用して、構文エラー（特に引用符の不整合）を検出する。
        """
        if not settings_string:
            return True, None

        try:
            # shlex.split を試行し、構文エラーを検出
            # posix=True で一般的なシェル構文をエミュレートし、Windowsでも同様の解析挙動を期待する
            _ = shlex.split(settings_string, posix=True)
            return True, None
        except ValueError as e:
            # shlex が構文エラーを検出した場合
            if "unmatched quotes" in str(e) or "No closing quotation" in str(e):
                return False, "引用符が正しく閉じられていません。"
            else:
                return False, f"コマンドラインの解析エラー: {e}"
        except Exception as e:
            return False, f"予期せぬバリデーションエラー: {e}"

    def _show_sync_conflict_dialog(self, game_title: str, local_mtime: float, remote_mtime: float) -> str:
        """
        QMessageBox を使用してユーザーに同期の競合を通知し、解決策を選択させる。
        
        Returns:
            str: "local", "remote", または "cancel"
        """
        import datetime
        local_time_str = datetime.datetime.fromtimestamp(local_mtime).strftime('%Y-%m-%d %H:%M:%S') if local_mtime > 0 else "なし"
        remote_time_str = datetime.datetime.fromtimestamp(remote_mtime).strftime('%Y-%m-%d %H:%M:%S') if remote_mtime > 0 else "なし"
        
        import time
        current_time = time.time()
        is_future = local_mtime > current_time + 3600 or remote_mtime > current_time + 3600
        
        msg_box = QMessageBox()
        msg_box.setWindowTitle("セーブデータの同期競合")
        
        if is_future:
            msg_box.setText(f"ゲーム「{game_title}」のセーブデータに未来のタイムスタンプが検出されました。")
        elif local_mtime > remote_mtime:
            msg_box.setText(f"ゲーム「{game_title}」のローカルのセーブデータがリモートより新しいようです。")
        else:
            msg_box.setText(f"ゲーム「{game_title}」のセーブデータに不整合が検出されました。")
        
        msg_box.setInformativeText(
            f"ローカル: {local_time_str}\n"
            f"リモート: {remote_time_str}\n\n"
            "どちらのデータを使用しますか？"
        )
        
        local_button = msg_box.addButton("ローカルを優先 (アップロード)", QMessageBox.ActionRole)
        remote_button = msg_box.addButton("リモートを優先 (ダウンロード)", QMessageBox.ActionRole)
        cancel_button = msg_box.addButton("キャンセル (起動中断)", QMessageBox.RejectRole)
        
        msg_box.exec()
        
        if msg_box.clickedButton() == local_button:
            return "local"
        elif msg_box.clickedButton() == remote_button:
            return "remote"
        else:
            return "cancel"
