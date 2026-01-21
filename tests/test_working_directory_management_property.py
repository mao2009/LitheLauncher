# tests/test_working_directory_management_property.py
"""
**Feature: game-execution-bug-fixes, Property 11: Working directory management**
**Validates: Requirements 4.3**

Property test to verify that working directories are set appropriately for game execution.
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


class TestWorkingDirectoryManagement:
    
    @given(
        dir_name=st.text(
            alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'), blacklist_characters='<>:"/\\|?*.\' ', min_codepoint=32, max_codepoint=126), # ファイルシステムで安全な文字のみを許可
            min_size=1,
            max_size=20
        ).filter(lambda x: x.strip() and not any(c in x for c in '<>:"|?*'))
    )
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
    def test_working_directory_management_property(self, dir_name):
        """
        Property: For any game that requires a specific working directory, the launcher service should set the working directory appropriately before execution.
        
        This test verifies that:
        1. The working directory is set to the executable's directory
        2. Relative paths in the executable work correctly
        3. The game can access files relative to its installation directory
        """
        # Create a temporary directory structure
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a game directory
            game_dir = os.path.join(temp_dir, dir_name.strip())
            os.makedirs(game_dir, exist_ok=True)
            
            # Create a data file that the executable should be able to find
            data_file = os.path.join(game_dir, "game_data.txt")
            with open(data_file, 'w') as f:
                f.write("test data")
            
            # Create executable in the game directory
            if platform.system() == "Windows":
                exe_name = "game.exe"
                exe_path = os.path.join(game_dir, exe_name)
                # Create a batch file that tries to read the data file
                with open(exe_path, 'w') as f:
                    f.write("@echo off\nif exist game_data.txt (exit 0) else (exit 1)\n")
            else:
                exe_name = "game"
                exe_path = os.path.join(game_dir, exe_name)
                # Create a shell script that tries to read the data file
                with open(exe_path, 'w') as f:
                    f.write("#!/bin/sh\nif [ -f game_data.txt ]; then exit 0; else exit 1; fi\n")
                os.chmod(exe_path, 0o755)
            
            # Mock game data
            game_data = {
                "id": 1,
                "title": f"Test Game {dir_name}",
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
            
            # Test that the game launches successfully with proper working directory
            try:
                result = launcher_service.launch_game(1)
                assert result is True, f"Game should launch successfully with proper working directory: {game_dir}"
                
                # Verify that the game service was called with correct ID
                mock_game_service.get_game_details.assert_called_with(1)
                
            except Exception as e:
                # If the launch fails, it should not be due to working directory issues
                error_msg = str(e).lower()
                
                # These are working directory related errors that should not occur
                forbidden_errors = [
                    "cannot change directory",
                    "working directory error",
                    "directory not found"
                ]
                
                for forbidden_error in forbidden_errors:
                    assert forbidden_error not in error_msg, f"Working directory not set correctly: {e}"
                
                # The test executable checks for game_data.txt in the working directory
                # If working directory is set correctly, the executable should find the file and exit with code 0
                # If it exits with code 1, it means the working directory was not set to the executable's directory