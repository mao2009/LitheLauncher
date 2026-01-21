import pytest
import shutil
import os
from pathlib import Path
from unittest.mock import MagicMock, patch

from src.remote_storage_service import RemoteStorageService
from src.exceptions import SaveDataSyncError

@pytest.fixture
def remote_storage_service():
    return RemoteStorageService()

@pytest.fixture
def setup_test_dirs(tmp_path):
    remote_dir = tmp_path / "remote_test_data"
    local_dir = tmp_path / "local_test_data"
    remote_dir.mkdir()
    local_dir.mkdir()
    (remote_dir / "file1.txt").write_text("remote_content1")
    (remote_dir / "file2.txt").write_text("remote_content2")
    return remote_dir, local_dir

class TestRemoteStorageService:
    def test_download_save_data_success_remote_exists(self, remote_storage_service, mocker, setup_test_dirs):
        remote_path, local_path = setup_test_dirs
        game_id = 1

        mocker.patch('shutil.copytree')
        mocker.patch('shutil.rmtree')

        # Create a dummy local file to be removed by rmtree
        (local_path / "dummy.txt").write_text("local_content")

        remote_storage_service.download_save_data(game_id, str(remote_path), local_path)

        # local_path が存在するため、rmtree が呼ばれることを期待
        shutil.rmtree.assert_called_once_with(local_path)
        shutil.copytree.assert_called_once_with(Path(remote_path), local_path, dirs_exist_ok=True)

    def test_download_save_data_remote_not_exists(self, remote_storage_service, mocker, setup_test_dirs):
        remote_path, local_path = setup_test_dirs
        game_id = 1

        mocker.patch('shutil.copytree')
        mocker.patch('shutil.rmtree')

        # Path.exists をパッチして、特定のリモートパスだけ存在しないことにする
        original_exists = Path.exists
        def mock_exists(self_path):
            if str(self_path) == str(remote_path):
                return False
            return original_exists(self_path)
        
        mocker.patch('pathlib.Path.exists', side_effect=mock_exists, autospec=True)

        # Create a dummy local file
        (local_path / "dummy.txt").write_text("local_content")

        remote_storage_service.download_save_data(game_id, str(remote_path), local_path)

        shutil.rmtree.assert_not_called()
        shutil.copytree.assert_not_called()

    def test_upload_save_data_copy_fails(self, remote_storage_service, mocker, setup_test_dirs):
        remote_path, local_path = setup_test_dirs
        game_id = 1

        # Mock shutil.copytree to raise an exception
        mocker.patch('shutil.copytree', side_effect=IOError("Mocked upload copytree error"))
        mocker.patch('shutil.rmtree') 

        # remote_path が存在することにする
        mocker.patch('pathlib.Path.exists', return_value=True)

        with pytest.raises(SaveDataSyncError) as excinfo:
            remote_storage_service.upload_save_data(game_id, local_path, str(remote_path))
        
        assert "upload" in str(excinfo.value)
        assert str(game_id) in str(excinfo.value)
        assert "Mocked upload copytree error" in str(excinfo.value)

    def test_get_latest_mtime_empty_dir(self, remote_storage_service, tmp_path):
        empty_dir = tmp_path / "empty_dir"
        empty_dir.mkdir()
        assert remote_storage_service.get_latest_mtime(empty_dir) == 0

    def test_get_latest_mtime_with_files(self, remote_storage_service, tmp_path):
        test_dir = tmp_path / "test_dir"
        test_dir.mkdir()
        file1 = test_dir / "file1.txt"
        file2 = test_dir / "file2.txt"
        file1.write_text("test1")
        file2.write_text("test2")
        
        os.utime(file1, (1000, 1000))
        os.utime(file2, (2000, 2000))
        
        assert remote_storage_service.get_latest_mtime(test_dir) == 2000

    def test_get_latest_mtime_recursive(self, remote_storage_service, tmp_path):
        test_dir = tmp_path / "test_dir_rec"
        test_dir.mkdir()
        sub_dir = test_dir / "sub"
        sub_dir.mkdir()
        file_sub = sub_dir / "file_sub.txt"
        file_sub.write_text("sub")
        
        os.utime(file_sub, (3000, 3000))
        
        assert remote_storage_service.get_latest_mtime(test_dir) == 3000

    def test_get_latest_mtime_not_exists(self, remote_storage_service, tmp_path):
        non_existent = tmp_path / "not_here"
        assert remote_storage_service.get_latest_mtime(non_existent) == 0
