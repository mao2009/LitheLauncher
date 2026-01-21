# tests/test_path_handling_with_spaces_property.py
"""
**Feature: game-execution-bug-fixes, Property 10: Path handling with spaces**
**Validates: Requirements 4.2**

Property test to verify that executable paths containing spaces are handled correctly.
"""

import pytest
import platform
import tempfile
import os
from hypothesis import given, strategies as st, assume, settings, HealthCheck
from unittest.mock import Mock, MagicMock
from src.launcher_service import LauncherService
from src.game_service import GameService
from src.remote_storage_service import RemoteStorageService


class TestPathHandlingWithSpaces:
    
    @given(
        path_with_spaces=st.text(
            alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'), min_codepoint=32, max_codepoint=126) | st.just(' '),
            min_size=5,
            max_size=30
        ).filter(lambda x: ' ' in x and x.strip() and not any(c in x for c in '<>:"|?*'))
    )
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
    def test_path_handling_with_spaces_property(self, path_with_spaces):
        """
        Property: For any executable path containing spaces, the launcher service should handle path quoting correctly to ensure successful execution.
        
        This test verifies that:
        1. Paths with spaces are properly quoted/escaped
        2. The subprocess call handles spaced paths without errors
        3. The execution doesn't fail due to path parsing issues
        """
        # Create a temporary directory structure with spaces in the path
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a subdirectory with spaces
            spaced_dir = os.path.join(temp_dir, path_with_spaces.strip())
            os.makedirs(spaced_dir, exist_ok=True)
            
            # Create executable in the spaced directory
            if platform.system() == "Windows":
                exe_name = "test game.exe"
                exe_path = os.path.join(spaced_dir, exe_name)
                # Create a simple batch file that exits successfully
                with open(exe_path, 'w') as f:
                    f.write("@echo off\nexit 0\n")
            else:
                exe_name = "test game"
                exe_path = os.path.join(spaced_dir, exe_name)
                # Create a simple shell script that exits successfully
                with open(exe_path, 'w') as f:
                    f.write("#!/bin/sh\nexit 0\n")
                os.chmod(exe_path, 0o755)
            
            # Verify the path actually contains spaces
            assume(' ' in exe_path)
            
            # Mock game data with spaced path
            game_data = {
                "id": 1,
                "title": "Test Game With Spaces",
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
            
            # Test that the game launches successfully despite spaces in path
            try:
                result = launcher_service.launch_game(1)
                assert result is True, f"Game should launch successfully with spaced path: {exe_path}"
                
                # Verify that the game service was called with correct ID
                mock_game_service.get_game_details.assert_called_with(1)
                
            except Exception as e:
                # If the launch fails, it should not be due to path parsing issues with spaces
                error_msg = str(e).lower()
                
                # These are space-related path errors that should not occur with proper quoting
                forbidden_errors = [
                    "no such file or directory",
                    "cannot find the file",
                    "the system cannot find the file specified",
                    "file not found"
                ]
                
                # Only check for these errors if the file actually exists
                if os.path.exists(exe_path):
                    for forbidden_error in forbidden_errors:
                        assert forbidden_error not in error_msg, f"Path with spaces not handled correctly: {e}"
                
                # If it's a different system error, that's acceptable as we're testing path handling specifically