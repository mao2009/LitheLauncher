# src/exceptions.py
from typing import Any # 追加

class GameLauncherError(Exception):
    """Base exception for Game Launcher application."""
    pass

class GameNotFoundError(GameLauncherError):
    """Raised when a game is not found."""
    def __init__(self, identifier: Any): # Any型で汎用的に
        self.identifier = identifier
        super().__init__(f"Game with identifier '{identifier}' not found.")

class CommandExecutionError(GameLauncherError):
    """Raised when a pre/post command execution fails."""
    def __init__(self, command: str, returncode: int, stdout: str, stderr: str):
        self.command = command
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr
        message = f"Command '{command}' failed with exit code {returncode}.\nStdout: {stdout}\nStderr: {stderr}"
        super().__init__(message)

class SaveDataSyncError(GameLauncherError):
    """Raised when save data synchronization fails."""
    def __init__(self, game_id: int, direction: str, original_exception: Exception = None):
        self.game_id = game_id
        self.direction = direction
        self.original_exception = original_exception
        message = f"Save data sync ({direction}) failed for game ID {game_id}."
        if original_exception:
            message += f" Original error: {original_exception}"
        super().__init__(message)


class ExecutableValidationError(GameLauncherError):
    """Raised when executable path validation fails."""
    def __init__(self, path: str, error_type: str, error_message: str, suggested_action: str = ""):
        self.path = path
        self.error_type = error_type
        self.suggested_action = suggested_action
        message = f"Executable validation failed for '{path}': {error_message}"
        if suggested_action:
            message += f" Suggestion: {suggested_action}"
        super().__init__(message)

class ImageValidationError(GameLauncherError):
    """Raised when an image validation fails."""
    def __init__(self, image_path: str, message: str = "Image validation failed."):
        self.image_path = image_path
        super().__init__(f"{message} Path: '{image_path}'")
