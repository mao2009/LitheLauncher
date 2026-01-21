# src/executable_validator.py
import os
import stat
from typing import Dict, Any
from dataclasses import dataclass


@dataclass
class ValidationResult:
    """Result of executable path validation."""
    is_valid: bool
    error_type: str = ""  # "missing", "not_found", "not_executable", "permission_denied"
    error_message: str = ""
    suggested_action: str = ""


class ExecutableValidator:
    """Centralized validation component for executable paths and permissions."""
    
    def validate_executable(self, path: str) -> ValidationResult:
        """
        Validate an executable path for existence and permissions.
        
        Args:
            path: The file system path to validate
            
        Returns:
            ValidationResult with validation status and error details
        """
        if not path or not path.strip():
            return ValidationResult(
                is_valid=False,
                error_type="missing",
                error_message="Executable path is empty or not set",
                suggested_action="Please set the executable path in game settings"
            )
        
        # Check if file exists
        if not os.path.exists(path):
            return ValidationResult(
                is_valid=False,
                error_type="not_found",
                error_message=f"Executable file not found at path: {path}",
                suggested_action="Please verify the file path and ensure the file exists"
            )
        
        # Check if it's a file (not a directory)
        if not os.path.isfile(path):
            return ValidationResult(
                is_valid=False,
                error_type="not_executable",
                error_message=f"Path points to a directory, not a file: {path}",
                suggested_action="Please select an executable file, not a directory"
            )
        
        # Check file permissions
        try:
            file_stat = os.stat(path)
            # On Windows, check if file has execute permissions
            # On Unix-like systems, check the execute bit
            if os.name == 'nt':  # Windows
                # On Windows, check if the file extension suggests it's executable
                # or if it has execute permissions for the owner
                if not (file_stat.st_mode & stat.S_IEXEC):
                    # Additional check for Windows executable extensions
                    executable_extensions = ['.exe', '.bat', '.cmd', '.com', '.scr', '.msi']
                    if not any(path.lower().endswith(ext) for ext in executable_extensions):
                        return ValidationResult(
                            is_valid=False,
                            error_type="permission_denied",
                            error_message=f"File does not appear to be executable: {path}",
                            suggested_action="Please select an executable file (.exe, .bat, .cmd, etc.)"
                        )
            else:  # Unix-like systems
                if not (file_stat.st_mode & stat.S_IEXEC):
                    return ValidationResult(
                        is_valid=False,
                        error_type="permission_denied",
                        error_message=f"File does not have execute permissions: {path}",
                        suggested_action="Please ensure the file has execute permissions or select a different executable"
                    )
        except OSError as e:
            return ValidationResult(
                is_valid=False,
                error_type="permission_denied",
                error_message=f"Cannot access file permissions: {path}. Error: {str(e)}",
                suggested_action="Please check file permissions and try again"
            )
        
        # All validations passed
        return ValidationResult(
            is_valid=True,
            error_type="",
            error_message="",
            suggested_action=""
        )
    
    def validate_game_executable(self, game_data: Dict[str, Any]) -> ValidationResult:
        """
        Validate the executable path from game data.
        
        Args:
            game_data: Dictionary containing game information
            
        Returns:
            ValidationResult with validation status
        """
        executable_path = game_data.get("executable_path", "")
        return self.validate_executable(executable_path)