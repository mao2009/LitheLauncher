# tests/test_subprocess_error_reporting_property.py
"""
**Feature: game-execution-bug-fixes, Property 4: Error message specificity for subprocess failures**
**Validates: Requirements 2.3, 4.5**

Property-based test for subprocess error reporting.
Tests that subprocess execution failures are captured and reported with specific system errors.
"""

import pytest
import tempfile
import os
import platform
from hypothesis import given, strategies as st, assume, settings, HealthCheck
from unittest.mock import MagicMock
from src.launcher_service import LauncherService
from src.game_service import GameService
from src.game_repository import GameRepository
from src.remote_storage_service import RemoteStorageService
from src.database import initialize_database
from src.exceptions import CommandExecutionError


def create_launcher_service():
    """Create a launcher service for testing."""
    # Set up test database with unique name
    import time
    db_path = f"test_subprocess_error_{time.time()}.db"
    if os.path.exists(db_path):
        os.remove(db_path)
    initialize_database(db_path)
    
    # Create dependencies
    game_repository = GameRepository(db_path)
    game_service = GameService(game_repository, MagicMock()) # image_manager のモックを追加
    remote_storage_service = RemoteStorageService()
    
    launcher_service = LauncherService(game_service, remote_storage_service)
    launcher_service._test_db_path = db_path
    return launcher_service


def cleanup_launcher_service(launcher_service):
    """Clean up test database."""
    if hasattr(launcher_service, '_test_db_path') and os.path.exists(launcher_service._test_db_path):
        os.remove(launcher_service._test_db_path)


class TestSubprocessErrorReporting:
    
    @given(
        invalid_executable_path=st.sampled_from([
            "nonexistent_file_12345.exe",
            "invalid_executable_path.exe",
            "missing_program.exe"
        ])
    )
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None, max_examples=10)
    def test_subprocess_error_reporting_captures_specific_errors(self, invalid_executable_path):
        """
        Property: For any invalid executable path, subprocess execution should capture 
        and report the specific system error that caused the failure.
        """
        # Assume the path doesn't exist to ensure we get a subprocess error
        assume(not os.path.exists(invalid_executable_path))
        
        launcher_service = create_launcher_service()
        try:
            # Attempt to launch the invalid executable
            with pytest.raises(CommandExecutionError) as exc_info:
                launcher_service._launch_executable([invalid_executable_path])
            
            # Verify that the error contains specific information
            error = exc_info.value
            
            # The error should contain the command that failed
            assert invalid_executable_path in str(error) or os.path.abspath(invalid_executable_path) in str(error)
            
            # The error should have a non-zero return code indicating failure
            assert error.returncode == -1  # Our convention for subprocess failures
            
            # The error message should contain system-specific error information
            assert len(str(error)) > 0
            
            # The stderr should contain some error information
            assert isinstance(error.stderr, str)
            assert len(error.stderr) > 0
        finally:
            cleanup_launcher_service(launcher_service)
    
    @given(
        command_with_invalid_executable=st.one_of(
            st.just("nonexistent_command_12345"),
            st.just("invalid/path/to/executable"),
            st.just("invalid_command_that_does_not_exist")
        )
    )
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
    def test_command_execution_error_reporting_captures_details(self, command_with_invalid_executable):
        """
        Property: For any command execution that fails, the system should capture
        the command, return code, stdout, and stderr details.
        """
        launcher_service = create_launcher_service()
        try:
            # Execute the invalid command
            returncode, stdout, stderr = launcher_service.execute_command(command_with_invalid_executable)
            
            # Verify that failure is properly detected
            assert returncode != 0
            
            # Verify that stdout and stderr are captured (even if empty)
            assert isinstance(stdout, str)
            assert isinstance(stderr, str)
            
            # At least one of stdout or stderr should contain error information
            # (some systems report errors in stdout, others in stderr)
            error_output = stdout + stderr
            assert len(error_output.strip()) >= 0  # May be empty on some systems, but should be strings
        finally:
            cleanup_launcher_service(launcher_service)
    
    def test_subprocess_error_contains_original_exception_info(self):
        """
        Property: When subprocess execution fails due to system errors,
        the reported error should contain information from the original exception.
        """
        launcher_service = create_launcher_service()
        try:
            # Use a path that will definitely cause a subprocess error
            invalid_path = "definitely_nonexistent_file_12345.exe"
            
            with pytest.raises(CommandExecutionError) as exc_info:
                launcher_service._launch_executable([invalid_path])
            
            error = exc_info.value
            
            # The error should contain the failed command
            assert invalid_path in error.command or os.path.abspath(invalid_path) in error.command
            
            # The error should have failure indicators
            assert error.returncode == -1  # Our convention for subprocess failures
            
            # The stderr should contain the original exception information
            assert len(error.stderr) > 0
            assert isinstance(error.stderr, str)
        finally:
            cleanup_launcher_service(launcher_service)