import pytest
from PySide6.QtWidgets import QApplication, QMessageBox, QFileDialog, QPushButton
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from pathlib import Path
import shutil
import os
from PIL import Image
from unittest.mock import MagicMock # MagicMock をインポート

from src.database import initialize_database
from src.game_repository import GameRepository
from src.image_manager import ImageManager
from src.game_service import GameService
from src.game_detail_dialog import GameDetailDialog
from src.exceptions import ImageValidationError, ExecutableValidationError
from src.executable_validator import ExecutableValidator # ExecutableValidator をインポート
from src.launcher_service import LauncherService # LauncherService をインポート

# テスト用のベースディレクトリとDBパス
TEST_BASE_DIR = Path("./test_data")
TEST_DB_PATH = TEST_BASE_DIR / "test_games.db"

@pytest.fixture(scope="module", autouse=True)
def app():
    # PySide6アプリケーションインスタンスを生成（既に存在する場合は再利用）
    # headless モードでの実行を許可するために QPA_PLATFORM 環境変数を設定
    if os.environ.get('QT_QPA_PLATFORM') is None:
        os.environ['QT_QPA_PLATFORM'] = 'offscreen'
    
    _app = QApplication.instance()
    if not _app:
        _app = QApplication([])
    yield _app
    # アプリケーションをきれいに終了
    del _app

@pytest.fixture(autouse=True)
def setup_teardown_test_environment():
    # 各テストの前に、テスト環境をセットアップ
    if TEST_BASE_DIR.exists():
        shutil.rmtree(TEST_BASE_DIR)
    TEST_BASE_DIR.mkdir(parents=True, exist_ok=True)
    initialize_database(str(TEST_DB_PATH))
    yield
    # 各テストの後に、テスト環境をクリーンアップ
    if TEST_BASE_DIR.exists():
        shutil.rmtree(TEST_BASE_DIR)

@pytest.fixture
def game_repository():
    return GameRepository(str(TEST_DB_PATH))

@pytest.fixture
def image_manager():
    return ImageManager(TEST_BASE_DIR)

@pytest.fixture
def executable_validator():
    return ExecutableValidator()

@pytest.fixture
def game_service(game_repository, image_manager):
    return GameService(game_repository, image_manager)

@pytest.fixture # launcher_service の fixture を追加
def launcher_service(game_service):
    # MagicMock(spec=LauncherService) は RemoteStorageService も要求するため、それをモックして渡す
    return MagicMock(spec=LauncherService, game_service=game_service, remote_storage_service=MagicMock())


# ヘルパー関数: ダミー実行可能ファイルの作成
def create_dummy_executable(file_path: Path):
    file_path.touch()
    return file_path

# ヘルパー関数: ダミー画像ファイルの作成
def create_dummy_image(file_path: Path, size=(100, 100), color=(255, 0, 0)):
    image = Image.new("RGB", size, color)
    image.save(file_path)
    return file_path

# ヘルパー関数: ダイアログの入力値を設定
def fill_game_details(dialog: GameDetailDialog, data: dict):
    if "title" in data:
        dialog.title_line_edit.setText(data["title"])
    if "description" in data:
        dialog.description_text_edit.setText(data["description"])
    if "executable_path" in data:
        dialog.executable_path_line_edit.setText(data["executable_path"])
    # 他のフィールドも必要に応じて追加

# ヘルパー関数: QFileDialogのモック
@pytest.fixture
def mock_qfiledialog(monkeypatch):
    """QFileDialog.getOpenFileNameをモックするフィクスチャ"""
    def mock_get_open_file_name(*args, **kwargs):
        # 常にダミーの画像パスを返す
        return (str(create_dummy_image(TEST_BASE_DIR / "dummy_selected_image.png")), "画像ファイル (*.png)")
    monkeypatch.setattr(QFileDialog, 'getOpenFileName', mock_get_open_file_name)

@pytest.fixture
def mock_qfiledialog_with_specific_path(monkeypatch):
    """QFileDialog.getOpenFileNameを特定のパスでモックするフィクスチャ"""
    def _mock_factory(file_path: Path):
        def mock_get_open_file_name(*args, **kwargs):
            return (str(file_path), "画像ファイル (*.png)")
        return mock_get_open_file_name
    return _mock_factory

class TestImageRegistrationIntegration:

    def test_new_game_registration_with_image(self, qtbot, game_service, image_manager, launcher_service, game_repository, mock_qfiledialog_with_specific_path): # launcher_service を追加
        """画像を伴う新規ゲーム登録の統合テスト"""
        # GIVEN
        dialog = GameDetailDialog(game_service, image_manager, launcher_service, parent=None) # launcher_service を追加
        dummy_image_path = create_dummy_image(TEST_BASE_DIR / "test_image_1.png", color=(0, 255, 0))
        mock_get_open_file_name = mock_qfiledialog_with_specific_path(dummy_image_path)
        QFileDialog.getOpenFileName = mock_get_open_file_name # QFileDialogをモック
    
        game_data_input = {
            "title": "Test Game with Image",
            "description": "A game with a beautiful image.",
            "executable_path": str(TEST_BASE_DIR / "test_game.exe")
        }
        create_dummy_executable(Path(game_data_input["executable_path"])) # ダミー実行ファイル

        fill_game_details(dialog, game_data_input)

        # WHEN
        # 画像選択ボタンをクリック
        qtbot.mouseClick(dialog.browse_image_button, Qt.LeftButton)
        assert dialog._temp_image_path is not None
        assert dialog._temp_image_path.exists()

        # 保存ボタンをクリック
        qtbot.mouseClick(dialog.save_button, Qt.LeftButton)
        qtbot.wait_signal(dialog.finished) # ダイアログが閉じるのを待つ
        
        # THEN
        # データベースにゲームが保存されていることを確認
        games = game_repository.get_all_games()
        assert len(games) == 1
        registered_game = games[0]
        assert registered_game["title"] == game_data_input["title"]
        assert registered_game["description"] == game_data_input["description"]
        assert registered_game["executable_path"] == game_data_input["executable_path"]
        assert registered_game["image_path"] != ""

        # 永続化された画像ファイルが存在することを確認
        final_image_path = Path(registered_game["image_path"])
        assert final_image_path.is_file()
        assert Path("data") in final_image_path.parents # 'data' ディレクトリの下にあることを確認
        assert str(registered_game["id"]) in final_image_path.parts # game_id ディレクトリの下にあることを確認
        
        # 一時画像ファイルがクリーンアップされていることを確認
        assert not dialog._temp_image_path.exists()

    def test_new_game_registration_without_image(self, qtbot, game_service, image_manager, launcher_service, game_repository): # launcher_service を追加
        """画像を伴わない新規ゲーム登録の統合テスト"""
        # GIVEN
        dialog = GameDetailDialog(game_service, image_manager, launcher_service, parent=None) # launcher_service を追加
        
        game_data_input = {
            "title": "Test Game without Image",
            "description": "A game without an image.",
            "executable_path": str(TEST_BASE_DIR / "test_game_no_img.exe")
        }
        create_dummy_executable(Path(game_data_input["executable_path"])) # ダミー実行ファイル

        fill_game_details(dialog, game_data_input)
        
        # WHEN
        qtbot.mouseClick(dialog.save_button, Qt.LeftButton)
        qtbot.wait_signal(dialog.finished)
        
        # THEN
        games = game_repository.get_all_games()
        assert len(games) == 1
        registered_game = games[0]
        assert registered_game["title"] == game_data_input["title"]
        assert registered_game["image_path"] == "" # 画像パスが空であることを確認
        assert dialog._temp_image_path is None # 一時画像パスが設定されていないことを確認

    def test_cancel_new_game_registration_with_image(self, qtbot, game_service, image_manager, launcher_service, game_repository, mock_qfiledialog_with_specific_path): # launcher_service を追加
        """画像を伴う新規ゲーム登録キャンセル時の統合テスト"""
        # GIVEN
        dialog = GameDetailDialog(game_service, image_manager, launcher_service, parent=None) # launcher_service を追加
        dummy_image_path = create_dummy_image(TEST_BASE_DIR / "test_image_cancel.png", color=(0, 0, 255))
        mock_get_open_file_name = mock_qfiledialog_with_specific_path(dummy_image_path)
        QFileDialog.getOpenFileName = mock_get_open_file_name

        game_data_input = {
            "title": "Test Game Cancel",
            "executable_path": str(TEST_BASE_DIR / "test_game_cancel.exe")
        }
        create_dummy_executable(Path(game_data_input["executable_path"]))

        fill_game_details(dialog, game_data_input)
        
        # WHEN
        qtbot.mouseClick(dialog.browse_image_button, Qt.LeftButton)
        assert dialog._temp_image_path is not None
        # 一時画像ファイルが作成されていることを確認 (キャンセル前)
        assert dialog._temp_image_path.exists()
        
        
        temp_image_path_before_cleanup = dialog._temp_image_path # cleanup前にパスを保存
        qtbot.mouseClick(dialog.cancel_button, Qt.LeftButton)
        qtbot.wait_signal(dialog.finished)
        
        # THEN
        # データベースにゲームが保存されていないことを確認
        games = game_repository.get_all_games()
        assert len(games) == 0
        
        # 一時画像ファイルがクリーンアップされていることを確認
        assert not temp_image_path_before_cleanup.exists()
        assert dialog._temp_image_path is None # _temp_image_path が None にリセットされていることを確認
        assert not image_manager._temp_dir.exists() or not any(image_manager._temp_dir.iterdir()) # temp_dir が空か、存在しないことを確認

    def test_update_existing_game_image(self, qtbot, game_service, image_manager, launcher_service, game_repository, mock_qfiledialog_with_specific_path): # launcher_service を追加
        """既存ゲームの画像更新の統合テスト"""
        # GIVEN: 既存ゲームを画像付きで登録
        initial_image_path = create_dummy_image(TEST_BASE_DIR / "initial_image.png", color=(255, 255, 0))
        
        # QFileDialogをモックして初期画像を選択させる
        mock_initial_qfiledialog = mock_qfiledialog_with_specific_path(initial_image_path)
        QFileDialog.getOpenFileName = mock_initial_qfiledialog
        
        initial_game_dialog = GameDetailDialog(game_service, image_manager, launcher_service) # launcher_service を追加
        initial_game_data = {
            "title": "Game to Update Image",
            "executable_path": str(TEST_BASE_DIR / "game_update_img.exe")
        }
        create_dummy_executable(Path(initial_game_data["executable_path"]))
        fill_game_details(initial_game_dialog, initial_game_data)
        qtbot.mouseClick(initial_game_dialog.browse_image_button, Qt.LeftButton)
        qtbot.mouseClick(initial_game_dialog.save_button, Qt.LeftButton)
        qtbot.wait_signal(initial_game_dialog.finished)

        games = game_repository.get_all_games()
        assert len(games) == 1
        game_id = games[0]["id"]
        old_final_image_path = Path(games[0]["image_path"])
        assert old_final_image_path.exists()
        assert not initial_game_dialog._temp_image_path.exists() # temp cleaned up

        # WHEN: 既存ゲームの画像を別のものに更新
        new_image_path = create_dummy_image(TEST_BASE_DIR / "new_image.png", color=(0, 255, 255))
        mock_new_qfiledialog = mock_qfiledialog_with_specific_path(new_image_path)
        QFileDialog.getOpenFileName = mock_new_qfiledialog # QFileDialogを新しい画像でモック

        update_dialog = GameDetailDialog(game_service, image_manager, launcher_service, game_id=game_id) # launcher_service を追加
        qtbot.mouseClick(update_dialog.browse_image_button, Qt.LeftButton) # 新しい画像を選択
        assert update_dialog._temp_image_path is not None
        assert update_dialog._temp_image_path.exists()

        qtbot.mouseClick(update_dialog.save_button, Qt.LeftButton)
        qtbot.wait_signal(update_dialog.finished)

        # THEN
        updated_game = game_repository.get_game(game_id)
        assert updated_game["image_path"] != ""
        new_final_image_path = Path(updated_game["image_path"])

        # 新しい画像ファイルが存在することを確認
        assert new_final_image_path.is_file()
        assert Path("data") in new_final_image_path.parents
        assert str(game_id) in new_final_image_path.parts
        assert new_final_image_path != old_final_image_path # パスが変更されたことを確認

        # 古い画像ファイルが削除されていることを確認
        assert not old_final_image_path.exists()
        
        # 一時画像ファイルがクリーンアップされていることを確認
        assert not update_dialog._temp_image_path.exists()
        
    def test_update_existing_game_without_changing_image(self, qtbot, game_service, image_manager, launcher_service, game_repository, mock_qfiledialog_with_specific_path): # launcher_service を追加
        """既存ゲームの画像を変更せずに他の情報を更新する統合テスト"""
        # GIVEN: 既存ゲームを画像付きで登録
        initial_image_path = create_dummy_image(TEST_BASE_DIR / "initial_image_no_change.png", color=(100, 100, 100))
        mock_initial_qfiledialog = mock_qfiledialog_with_specific_path(initial_image_path)
        QFileDialog.getOpenFileName = mock_initial_qfiledialog

        initial_game_dialog = GameDetailDialog(game_service, image_manager, launcher_service) # launcher_service を追加
        initial_game_data = {
            "title": "Game to Update Text",
            "description": "Initial description.",
            "executable_path": str(TEST_BASE_DIR / "game_update_text.exe")
        }
        create_dummy_executable(Path(initial_game_data["executable_path"]))
        fill_game_details(initial_game_dialog, initial_game_data)
        qtbot.mouseClick(initial_game_dialog.browse_image_button, Qt.LeftButton)
        qtbot.mouseClick(initial_game_dialog.save_button, Qt.LeftButton)
        qtbot.wait_signal(initial_game_dialog.finished)

        games = game_repository.get_all_games()
        assert len(games) == 1
        game_id = games[0]["id"]
        old_final_image_path = Path(games[0]["image_path"])
        assert old_final_image_path.exists()
        assert not initial_game_dialog._temp_image_path.exists()

        # WHEN: 既存ゲームのテキスト情報を更新 (画像は変更しない)
        update_dialog = GameDetailDialog(game_service, image_manager, launcher_service, game_id=game_id) # launcher_service を追加
        # 画像選択ボタンはクリックしない

        new_description = "Updated description for the game."
        fill_game_details(update_dialog, {"description": new_description})

        qtbot.mouseClick(update_dialog.save_button, Qt.LeftButton)
        qtbot.wait_signal(update_dialog.finished)

        # THEN
        updated_game = game_repository.get_game(game_id)
        assert updated_game["description"] == new_description # 説明が更新されたことを確認
        assert Path(updated_game["image_path"]) == old_final_image_path # 画像パスが変更されていないことを確認
        assert old_final_image_path.exists() # 画像ファイルが削除されていないことを確認

    def test_update_existing_game_by_removing_image(self, qtbot, game_service, image_manager, launcher_service, game_repository, mock_qfiledialog_with_specific_path): # launcher_service を追加
        """既存ゲームから画像を削除して更新する統合テスト"""
        # GIVEN: 既存ゲームを画像付きで登録
        initial_image_path = create_dummy_image(TEST_BASE_DIR / "initial_image_remove.png", color=(0, 0, 100))
        mock_initial_qfiledialog = mock_qfiledialog_with_specific_path(initial_image_path)
        QFileDialog.getOpenFileName = mock_initial_qfiledialog

        initial_game_dialog = GameDetailDialog(game_service, image_manager, launcher_service) # launcher_service を追加
        initial_game_data = {
            "title": "Game to Remove Image",
            "executable_path": str(TEST_BASE_DIR / "game_remove_img.exe")
        }
        create_dummy_executable(Path(initial_game_data["executable_path"]))
        fill_game_details(initial_game_dialog, initial_game_data)
        qtbot.mouseClick(initial_game_dialog.browse_image_button, Qt.LeftButton)
        qtbot.mouseClick(initial_game_dialog.save_button, Qt.LeftButton)
        qtbot.wait_signal(initial_game_dialog.finished)

        games = game_repository.get_all_games()
        assert len(games) == 1
        game_id = games[0]["id"]
        old_final_image_path = Path(games[0]["image_path"])
        assert old_final_image_path.exists()
        assert not initial_game_dialog._temp_image_path.exists()

        # WHEN: 既存ゲームから画像を削除
        update_dialog = GameDetailDialog(game_service, image_manager, launcher_service, game_id=game_id) # launcher_service を追加
        
        # 画像をクリアする操作をシミュレート
        # _game_data の image_path を空文字列にする
        update_dialog._game_data["image_path"] = ""
        update_dialog._temp_image_path = None
        # _on_form_changedを呼び出して保存ボタンを有効にする
        update_dialog._on_form_changed() 

        qtbot.mouseClick(update_dialog.save_button, Qt.LeftButton)
        qtbot.wait_signal(update_dialog.finished)

        # THEN
        updated_game = game_repository.get_game(game_id)
        assert updated_game["image_path"] == "" # image_pathが空であることを確認
        assert not old_final_image_path.exists() # 古い画像ファイルが削除されていることを確認
        
    # --- エラーハンドリングの統合テスト ---

    @pytest.fixture
    def mock_qmessagebox(self, monkeypatch):
        """QMessageBoxの各種メソッドをモックするフィクスチャ"""
        mock_warning = MagicMock(return_value=QMessageBox.Ok)
        mock_critical = MagicMock(return_value=QMessageBox.Ok)
        monkeypatch.setattr(QMessageBox, 'warning', mock_warning)
        monkeypatch.setattr(QMessageBox, 'critical', mock_critical)
        return mock_warning, mock_critical

    def test_image_validation_error_new_game(self, qtbot, game_service, image_manager, launcher_service, game_repository, mock_qfiledialog_with_specific_path, mock_qmessagebox, monkeypatch): # launcher_service を追加
        """新規ゲーム登録時、画像バリデーションエラーのテスト"""
        # GIVEN
        mock_warning, _ = mock_qmessagebox
        # ImageManager.validate_image が ImageValidationError を発生させるようにモック
        monkeypatch.setattr(image_manager, 'validate_image', MagicMock(side_effect=ImageValidationError("dummy_path.png", "Test invalid image.")))

        dialog = GameDetailDialog(game_service, image_manager, launcher_service, parent=None) # launcher_service を追加
        dummy_image_path = create_dummy_image(TEST_BASE_DIR / "invalid_image.png") # ダミー画像を作成
        mock_get_open_file_name = mock_qfiledialog_with_specific_path(dummy_image_path)
        QFileDialog.getOpenFileName = mock_get_open_file_name

        game_data_input = {
            "title": "Game with Invalid Image",
            "executable_path": str(TEST_BASE_DIR / "game_invalid_image.exe")
        }
        create_dummy_executable(Path(game_data_input["executable_path"]))
        fill_game_details(dialog, game_data_input)

        # WHEN
        qtbot.mouseClick(dialog.browse_image_button, Qt.LeftButton)
        
        # THEN
        # QMessageBox.warning が呼び出されたことを確認
        mock_warning.assert_called_once()
        assert "画像の一時保存または検証に失敗しました" in mock_warning.call_args[0][2]
        
        # _temp_image_path が None にリセットされていることを確認
        assert dialog._temp_image_path is None
        # UIの画像表示エリアがクリアされていることを確認
        assert "画像なし" in dialog.image_preview_label.text()

        # ゲームは登録されていないことを確認 (save_button がクリックされてないため)
        assert len(game_repository.get_all_games()) == 0

    def test_executable_validation_error_new_game(self, qtbot, game_service, image_manager, launcher_service, game_repository, mock_qmessagebox, monkeypatch): # launcher_service を追加
        """新規ゲーム登録時、実行ファイルバリデーションエラーのテスト"""
        # GIVEN
        mock_warning, _ = mock_qmessagebox
        # ExecutableValidator.validate_executable をモックして無効な結果を返す
        mock_validator_result = MagicMock()
        mock_validator_result.is_valid = False
        mock_validator_result.error_message = "Test invalid executable."
        mock_validator_result.error_type = "invalid_path"
        mock_validator_result.suggested_action = "Check path."
        monkeypatch.setattr(game_service.executable_validator, 'validate_executable', MagicMock(return_value=mock_validator_result))
        # GameDetailDialog 内の ExecutableValidator もモックする
        monkeypatch.setattr('src.game_detail_dialog.ExecutableValidator.validate_executable', MagicMock(return_value=mock_validator_result))

        dialog = GameDetailDialog(game_service, image_manager, launcher_service, parent=None) # launcher_service を追加
        game_data_input = {
            "title": "Game with Invalid Executable",
            "executable_path": str(TEST_BASE_DIR / "non_existent_game.exe") # 存在しないパス
        }
        fill_game_details(dialog, game_data_input)
        
        # WHEN
        qtbot.mouseClick(dialog.save_button, Qt.LeftButton) # 保存ボタンをクリック
        qtbot.wait_signal(dialog.finished) # ダイアログが閉じられるのを待つ (エラーで閉じない場合はタイムアウト)

        # THEN
        # QMessageBox.warning が呼び出されたことを確認
        mock_warning.assert_called_once()
        # エラーメッセージが適切に含まれていることを確認
        assert "実行ファイル検証エラー" in mock_warning.call_args[0][1]
        assert "Test invalid executable." in mock_warning.call_args[0][2]
        
        # ゲームは登録されていないことを確認
        assert len(game_repository.get_all_games()) == 0

    def test_image_validation_error_existing_game_update(self, qtbot, game_service, image_manager, launcher_service, game_repository, mock_qfiledialog_with_specific_path, mock_qmessagebox, monkeypatch): # launcher_service を追加
        """既存ゲーム更新時、画像バリデーションエラーのテスト"""
        # GIVEN: 既存ゲームを画像付きで登録
        initial_image_path = create_dummy_image(TEST_BASE_DIR / "valid_initial_image.png")
        mock_get_open_file_name_initial = mock_qfiledialog_with_specific_path(initial_image_path)
        QFileDialog.getOpenFileName = mock_get_open_file_name_initial

        initial_game_dialog = GameDetailDialog(game_service, image_manager, launcher_service) # launcher_service を追加
        initial_game_data = { "title": "Game for Update Error Test", "executable_path": str(TEST_BASE_DIR / "game_update_error.exe") }
        create_dummy_executable(Path(initial_game_data["executable_path"]))
        fill_game_details(initial_game_dialog, initial_game_data)
        qtbot.mouseClick(initial_game_dialog.browse_image_button, Qt.LeftButton)
        qtbot.mouseClick(initial_game_dialog.save_button, Qt.LeftButton)
        qtbot.wait_signal(initial_game_dialog.finished)

        game_id = game_repository.get_all_games()[0]["id"]
        old_image_path = Path(game_repository.get_game(game_id)["image_path"])
        assert old_image_path.exists()

        mock_warning, _ = mock_qmessagebox
        # ImageManager.validate_image が ImageValidationError を発生させるようにモック
        monkeypatch.setattr(image_manager, 'validate_image', MagicMock(side_effect=ImageValidationError("new_invalid_path.png", "Test invalid image on update.")))

        # WHEN: 既存ゲームの画像を不正なものに更新
        update_dialog = GameDetailDialog(game_service, image_manager, launcher_service, game_id=game_id) # launcher_service を追加
        new_dummy_image_path = create_dummy_image(TEST_BASE_DIR / "new_invalid_image.png")
        mock_get_open_file_name_new = mock_qfiledialog_with_specific_path(new_dummy_image_path)
        QFileDialog.getOpenFileName = mock_get_open_file_name_new

        qtbot.mouseClick(update_dialog.browse_image_button, Qt.LeftButton) # 不正な画像を選択
        
        # THEN (QMessageBox がエラーを表示し、ダイアログは閉じない)
        mock_warning.assert_called_once()
        assert "画像の一時保存または検証に失敗しました" in mock_warning.call_args[0][2]
        
        # _temp_image_path は None にリセットされていることを確認
        assert update_dialog._temp_image_path is None
        # UIの画像表示エリアがクリアされていることを確認 (または元の画像が表示されていることを確認)
        # ここでは元の画像が表示されたままになっているはずなので、直接は確認しない。

        # ゲームの画像パスが変更されていないことを確認
        updated_game = game_repository.get_game(game_id)
        assert Path(updated_game["image_path"]) == old_image_path
        assert old_image_path.exists()
        
        # ImageManager が一時ファイルをクリーンアップしたことを確認
        assert not image_manager._temp_dir.exists() or not any(image_manager._temp_dir.iterdir())


    def test_executable_validation_error_existing_game_update(self, qtbot, game_service, image_manager, launcher_service, game_repository, mock_qmessagebox, monkeypatch): # launcher_service を追加
        """既存ゲーム更新時、実行ファイルバリデーションエラーのテスト"""
        # GIVEN: 既存ゲームを登録
        initial_game_data = { "title": "Game for Exec Update Error Test", "executable_path": str(TEST_BASE_DIR / "game_exec_update_valid.exe") }
        create_dummy_executable(Path(initial_game_data["executable_path"]))
        registered_game = game_service.register_game(initial_game_data)
        game_id = registered_game["id"]
        old_executable_path = Path(registered_game["executable_path"])
        assert old_executable_path.exists()

        mock_warning, _ = mock_qmessagebox
        # ExecutableValidator.validate_executable をモックして無効な結果を返す
        mock_validator_result = MagicMock()
        mock_validator_result.is_valid = False
        mock_validator_result.error_message = "Test invalid executable on update."
        mock_validator_result.error_type = "invalid_path_update"
        mock_validator_result.suggested_action = "Check path update."
        monkeypatch.setattr(game_service.executable_validator, 'validate_executable', MagicMock(return_value=mock_validator_result))
        # GameDetailDialog 内の ExecutableValidator もモックする
        monkeypatch.setattr('src.game_detail_dialog.ExecutableValidator.validate_executable', MagicMock(return_value=mock_validator_result))

        # WHEN: 既存ゲームの実行ファイルパスを不正なものに更新
        update_dialog = GameDetailDialog(game_service, image_manager, launcher_service, game_id=game_id) # launcher_service を追加
        invalid_executable_path = str(TEST_BASE_DIR / "non_existent_update.exe")
        fill_game_details(update_dialog, {"executable_path": invalid_executable_path})
        
        qtbot.mouseClick(update_dialog.save_button, Qt.LeftButton) # 保存ボタンをクリック
        qtbot.wait_signal(update_dialog.finished) # ダイアログが閉じられるのを待つ (エラーで閉じない場合はタイムアウト)

        # THEN
        # QMessageBox.warning が呼び出されたことを確認
        mock_warning.assert_called_once()
        assert "実行ファイル検証エラー" in mock_warning.call_args[0][1]
        assert "Test invalid executable on update." in mock_warning.call_args[0][2]
        
        # ゲームの実行ファイルパスが変更されていないことを確認
        updated_game = game_repository.get_game(game_id)
        assert Path(updated_game["executable_path"]) == old_executable_path
        assert old_executable_path.exists()