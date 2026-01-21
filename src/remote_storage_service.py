# src/remote_storage_service.py
import logging
import shutil # 追加
import os # 追加
from pathlib import Path # 追加
from src.game_launcher_logger import get_logger
from src.exceptions import SaveDataSyncError # 追加

class RemoteStorageService:
    def __init__(self):
        self.logger = get_logger('RemoteStorageService', log_file='game_launcher.log', level=logging.INFO)

    def download_save_data(self, game_id: int, remote_path: str, local_path: Path) -> bool:
        self.logger.info(f"Attempting to download save data for game {game_id} from {remote_path} to {local_path}")
        try:
            remote_path_obj = Path(remote_path)
            
            if not remote_path_obj.exists():
                self.logger.warning(f"Remote path {remote_path} does not exist for game {game_id}. Skipping download and keeping local save data intact.")
                return False # No download occurred

            else:
                # local_path が存在する場合、その内容を削除してクリーンな状態にする
                if local_path.exists():
                    self.logger.debug(f"Removing existing local save data at {local_path} for game {game_id}.")
                    shutil.rmtree(local_path)
                
                # local_path の親ディレクトリが存在しない場合は作成
                local_path.mkdir(parents=True, exist_ok=True)
                
                # リモートパスからローカルパスへファイルをコピー
                self.logger.debug(f"Copying data from {remote_path_obj} to {local_path} for game {game_id}.")
                shutil.copytree(remote_path_obj, local_path, dirs_exist_ok=True)
                self.logger.info(f"Successfully downloaded save data for game {game_id} to {local_path}.")
                return True # Download occurred
        except Exception as e:
            error_msg = f"Failed to download save data for game {game_id} from {remote_path} to {local_path}: {str(e)}"
            self.logger.error(error_msg)
            raise SaveDataSyncError(game_id, "download", e)

    def upload_save_data(self, game_id: int, local_path: Path, remote_path: str):
        """
        Upload save data from local path to remote storage.
        
        Args:
            game_id: ID of the game
            local_path: Local source path (Pathオブジェクト)
            remote_path: Remote destination path
            
        Raises:
            SaveDataSyncError: If upload fails
        """
        self.logger.info(f"Uploading save data for game {game_id} from {local_path} to {remote_path}")
        try:
            # remote_path が存在する場合、その内容を削除してクリーンな状態にする
            # remote_path は文字列なのでPathオブジェクトに変換
            remote_path_obj = Path(remote_path)
            if remote_path_obj.exists():
                shutil.rmtree(remote_path_obj)
                self.logger.debug(f"Removed existing remote save data at {remote_path} for game {game_id}.")
            
            # remote_path の親ディレクトリが存在しない場合は作成
            remote_path_obj.mkdir(parents=True, exist_ok=True)
            
            # ローカルパスからリモートパスへファイルをコピー
            shutil.copytree(local_path, remote_path_obj, dirs_exist_ok=True)
            self.logger.info(f"Successfully uploaded save data for game {game_id} from {local_path} to {remote_path}.")
        except Exception as e:
            error_msg = f"Failed to upload save data for game {game_id} from {local_path} to {remote_path}: {str(e)}"
            self.logger.error(error_msg)
            raise SaveDataSyncError(game_id, "upload", e)

    def get_latest_mtime(self, path: Path) -> float:
        """
        Get the latest modification time of any file within the given directory recursively.
        
        Args:
            path: Path to the directory or file
            
        Returns:
            float: Latest modification time as a UNIX timestamp, or 0 if path doesn't exist or is empty
        """
        if not path.exists():
            self.logger.debug(f"Path {path} does not exist. Returning 0 for latest mtime.")
            return 0.0

        if path.is_file():
            return path.stat().st_mtime

        latest_mtime = 0.0
        try:
            for root, _, files in os.walk(path):
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        mtime = os.path.getmtime(file_path)
                        if mtime > latest_mtime:
                            latest_mtime = mtime
                    except OSError:
                        continue
        except Exception as e:
            self.logger.warning(f"Error while walking directory {path}: {e}")
            
        return latest_mtime
