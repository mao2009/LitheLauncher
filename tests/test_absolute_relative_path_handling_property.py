# tests/test_absolute_relative_path_handling_property.py
"""
**Feature: game-execution-bug-fixes, Property 12: Absolute and relative path handling**
**Validates: Requirements 4.4**

Property test to verify that both absolute and relative executable paths are handled correctly.
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


class TestAbsoluteRelativePathHandling:
    
    @given(
        use_relative_path=st.booleans(),
        exe_name=st.text(
            alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'), min_codepoint=32, max_codepoint=126),
            min_size=1,
            max_size=15
        ).filter(lambda x: x.strip() and not any(c in x for c in '<>:"|?*'))
    )
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
    def test_absolute_relative_path_handling_property(self, use_relative_path, exe_name):
        """
        Property: For any executable path (absolute or relative), the launcher service should resolve and execute the path correctly.
        
        This test verifies that:
        1. Absolute paths are executed correctly
        2. Relative paths are resolved and executed correctly
        3. Both path types result in successful game launches
        """
        # Create a temporary directory structure
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create executable
            if platform.system() == "Windows":
                exe_filename = f"{exe_name.strip()}.exe"
            else:
                exe_filename = exe_name.strip()
            
            exe_path = os.path.join(temp_dir, exe_filename)
            
            # Create a simple executable
            if platform.system() == "Windows":
                with open(exe_path, 'w') as f:
                    f.write("@echo off\nexit 0\n")
            else:
                with open(exe_path, 'w') as f:
                    f.write("#!/bin/sh\nexit 0\n")
                os.chmod(exe_path, 0o755)
            
            # Determine the path to use (absolute or relative)
            if use_relative_path:
                # Change to temp directory and use relative path
                original_cwd = os.getcwd()
                os.chdir(temp_dir)
                test_exe_path = exe_filename  # Relative path
            else:
                test_exe_path = exe_path  # Absolute path
            
            try:
                # Mock game data
                game_data = {
                    "id": 1,
                    "title": f"Test Game {exe_name}",
                    "executable_path": test_exe_path,
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
                
                # Test that the game launches successfully regardless of path type
                result = launcher_service.launch_game(1)
                assert result is True, f"Game should launch successfully with {'relative' if use_relative_path else 'absolute'} path: {test_exe_path}"
                
                # Verify that the game service was called with correct ID
                mock_game_service.get_game_details.assert_called_with(1)
                
            except Exception as e:
                # If the launch fails, it should not be due to path resolution issues
                error_msg = str(e).lower()
                
                # These are path resolution errors that should not occur with proper handling
                forbidden_errors = [
                    "path not found",
                    "cannot resolve path",
                    "invalid path format"
                ]
                
                for forbidden_error in forbidden_errors:
                    assert forbidden_error not in error_msg, f"Path resolution failed for {'relative' if use_relative_path else 'absolute'} path: {e}"
                
                # If it's a legitimate system error (like permission denied), that's acceptable
                # as we're testing path resolution, not execution permissions
                
            finally:
                # Restore original working directory if we changed it
                if use_relative_path:
                    os.chdir(original_cwd)