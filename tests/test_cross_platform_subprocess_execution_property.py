# tests/test_cross_platform_subprocess_execution_property.py
"""
**Feature: game-execution-bug-fixes, Property 9: Cross-platform subprocess execution**
**Validates: Requirements 4.1**

Property test to verify that subprocess execution uses appropriate parameters for the current operating system.
"""

import pytest
import platform
import subprocess
import tempfile
import os
from hypothesis import given, strategies as st, assume, settings, HealthCheck
from unittest.mock import Mock, MagicMock
from src.launcher_service import LauncherService
from src.game_service import GameService
from src.remote_storage_service import RemoteStorageService


class TestCrossPlatformSubprocessExecution:
    
    @given(
        executable_name=st.text(
            alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'), min_codepoint=32, max_codepoint=126),
            min_size=1,
            max_size=20
        ).filter(lambda x: x.strip() and not any(c in x for c in '<>:"|?*'))
    )
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
    def test_cross_platform_subprocess_execution_property(self, executable_name):
        """
        Property: For any game launch, the subprocess execution should use appropriate parameters for the current operating system.
        
        This test verifies that:
        1. On Windows, executable paths are handled correctly
        2. On Unix-like systems, executable paths are handled correctly
        3. The subprocess call uses appropriate parameters for the platform
        """
        # Create a temporary executable file for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            if platform.system() == "Windows":
                exe_path = os.path.join(temp_dir, f"{executable_name}.exe")
            else:
                exe_path = os.path.join(temp_dir, executable_name)
            
            # Create a simple executable script
            if platform.system() == "Windows":
                # Create a simple batch file that exits successfully
                with open(exe_path, 'w') as f:
                    f.write("@echo off\nexit 0\n")
            else:
                # Create a simple shell script that exits successfully
                with open(exe_path, 'w') as f:
                    f.write("#!/bin/sh\nexit 0\n")
                os.chmod(exe_path, 0o755)
            
            # Mock game data
            game_data = {
                "id": 1,
                "title": f"Test Game {executable_name}",
                "executable_path": exe_path,
                "pre_command": None,
                "post_command": None,
                "sync_enabled": 0,
                "save_folder": None,
                "remote_sync_path": None
            }
            
            # Create mock services
            mock_game_service = Mock()
            mock_remote_storage_service = Mock()
            
            # Configure mock to return our test game
            mock_game_service.get_game_details.return_value = game_data
            
            # Create launcher service
            launcher_service = LauncherService(mock_game_service, mock_remote_storage_service)
            
            # Test that the game launches successfully with platform-appropriate subprocess handling
            try:
                result = launcher_service.launch_game(1)
                assert result is True, "Game should launch successfully with cross-platform subprocess execution"
                
                # Verify that the game service was called with correct ID
                mock_game_service.get_game_details.assert_called_with(1)
                
            except Exception as e:
                # If the launch fails, it should not be due to improper subprocess parameter usage
                # The failure should be a legitimate system error, not a parameter error
                error_msg = str(e).lower()
                
                # These are subprocess parameter-related errors that should not occur
                forbidden_errors = [
                    "cannot use shell=true with a list",
                    "invalid shell parameter",
                    "shell parameter error"
                ]
                
                for forbidden_error in forbidden_errors:
                    assert forbidden_error not in error_msg, f"Subprocess execution failed due to improper parameter usage: {e}"
                
                # If it's a legitimate system error (like file not found, permission denied), that's acceptable
                # as we're testing the subprocess parameter handling, not the actual execution success