# tests/test_game_detail_dialog.py
import pytest
from unittest.mock import MagicMock, patch
from PySide6 import QtCore, QtGui
from PySide6.QtWidgets import QDialog, QLineEdit, QTextEdit, QCheckBox, QPushButton, QFileDialog, QLabel
from pathlib import Path
from src.game_service import GameService
from src.game_detail_dialog import GameDetailDialog
from src.launcher_service import LauncherService
from src.executable_validator import ExecutableValidator
from src.exceptions import CommandExecutionError, GameNotFoundError, ExecutableValidationError, ImageValidationError, SaveDataSyncError

@pytest.fixture
def game_service_mock():
    return MagicMock(spec=GameService)

@pytest.fixture
def launcher_service_mock():
    mock_launcher_service = MagicMock(spec=LauncherService)
    mock_launcher_service.validate_command_line_settings.return_value = (True, None)
    return mock_launcher_service

@pytest.fixture
def image_manager_mock():
    mock = MagicMock()
    mock.save_game_image.side_effect = lambda game_id, image_path: Path(f"/mocked/path/{game_id}/{image_path.name}")
    return mock

@pytest.fixture
def game_data_template_fixture():
    return {
        "id": 1,
        "title": "Test Game",
        "description": "A test game description.",
        "pre_command": "echo pre",
        "post_command": "echo post",
        "save_folder": "/path/to/save",
        "sync_enabled": 1,
        "remote_sync_path": "/remote/path",
        "executable_path": "/path/to/game.exe",
        "command_line_settings": "", # Ensure this is a string
        "image_path": "", # Ensure this is a string
        "play_time_str": "1時間 1分 1秒" # New field for play time display
    }

def _assert_common_fields_exist(dialog):
    assert dialog.findChild(QLineEdit, "titleLineEdit") is not None
    assert dialog.findChild(QTextEdit, "descriptionTextEdit") is not None
    assert dialog.findChild(QLineEdit, "preCommandLineEdit") is not None
    assert dialog.findChild(QLineEdit, "postCommandLineEdit") is not None
    assert dialog.findChild(QLineEdit, "saveFolderLineEdit") is not None
    assert dialog.findChild(QCheckBox, "syncEnabledCheckBox") is not None
    assert dialog.findChild(QLineEdit, "remoteSyncPathLineEdit") is not None
    assert dialog.findChild(QLineEdit, "executablePathLineEdit") is not None
    assert dialog.findChild(QLineEdit, "commandLineSettingsLineEdit") is not None
    assert dialog.findChild(QLabel, "commandLineSettingsWarningLabel") is not None
    assert dialog.findChild(QPushButton, "browseExecutablePathButton") is not None
    assert dialog.findChild(QPushButton, "launchGameButton") is not None
    assert dialog.findChild(QPushButton, "saveButton") is not None
    assert dialog.findChild(QPushButton, "cancelButton") is not None

def test_dialog_creation_for_new_game(qtbot, game_service_mock, launcher_service_mock):
    game_service_mock.get_game_details.return_value = None # No existing game data for new game
    dialog = GameDetailDialog(game_service_mock, MagicMock(), launcher_service_mock)
    assert isinstance(dialog, QDialog)
    assert dialog.windowTitle() == "New Game Registration"
    _assert_common_fields_exist(dialog)

def test_executable_path_ui_elements_exist(qtbot, game_service_mock, image_manager_mock, launcher_service_mock):
    game_service_mock.get_game_details.return_value = None # No existing game data
    dialog = GameDetailDialog(game_service_mock, image_manager_mock, launcher_service_mock)
    executable_path_line_edit = dialog.findChild(QLineEdit, "executablePathLineEdit")
    assert executable_path_line_edit is not None
    browse_executable_path_button = dialog.findChild(QPushButton, "browseExecutablePathButton")
    assert browse_executable_path_button is not None

def test_dialog_creation_for_editing_existing_game(qtbot, game_service_mock, game_data_template_fixture, launcher_service_mock):
    game_service_mock.get_game_details.return_value = game_data_template_fixture
    dialog = GameDetailDialog(game_service_mock, MagicMock(), launcher_service_mock, game_id=game_data_template_fixture["id"])
    assert dialog.windowTitle() == "Edit Game"
    _assert_common_fields_exist(dialog)
    assert dialog.findChild(QLineEdit, "titleLineEdit").text() == game_data_template_fixture["title"]
    assert dialog.findChild(QTextEdit, "descriptionTextEdit").toPlainText() == game_data_template_fixture["description"]
    assert dialog.findChild(QLineEdit, "preCommandLineEdit").text() == game_data_template_fixture["pre_command"]
    assert dialog.findChild(QLineEdit, "postCommandLineEdit").text() == game_data_template_fixture["post_command"]
    assert dialog.findChild(QLineEdit, "saveFolderLineEdit").text() == game_data_template_fixture["save_folder"]
    assert dialog.findChild(QCheckBox, "syncEnabledCheckBox").isChecked() == bool(game_data_template_fixture["sync_enabled"])
    assert dialog.findChild(QLineEdit, "remoteSyncPathLineEdit").text() == game_data_template_fixture["remote_sync_path"]
    assert dialog.findChild(QLineEdit, "executablePathLineEdit").text() == game_data_template_fixture["executable_path"]
    assert dialog.findChild(QLineEdit, "commandLineSettingsLineEdit").text() == game_data_template_fixture["command_line_settings"]
    game_service_mock.get_game_details.assert_called_once_with(game_data_template_fixture["id"])

def test_load_game_data_initializes_executable_path(qtbot, game_service_mock, game_data_template_fixture, launcher_service_mock):
    game_data_template_fixture["executable_path"] = "/initial/path/to/game.exe"
    game_service_mock.get_game_details.return_value = game_data_template_fixture
    dialog = GameDetailDialog(game_service_mock, MagicMock(), launcher_service_mock, game_id=game_data_template_fixture["id"])
    executable_path_line_edit = dialog.findChild(QLineEdit, "executablePathLineEdit")
    assert executable_path_line_edit.text() == "/initial/path/to/game.exe"

def test_get_game_data_includes_executable_path(qtbot, game_service_mock, launcher_service_mock):
    game_service_mock.get_game_details.return_value = None # No existing game data
    dialog = GameDetailDialog(game_service_mock, MagicMock(), launcher_service_mock)
    executable_path_line_edit = dialog.findChild(QLineEdit, "executablePathLineEdit")
    test_path = "/test/get/path.exe"
    executable_path_line_edit.setText(test_path)
    game_data, _ = dialog.get_game_data()
    assert "executable_path" in game_data
    assert game_data["executable_path"] == test_path
    # assert "cover_art_path" not in game_data # Removed as per new design

@patch('PySide6.QtWidgets.QFileDialog.getOpenFileName')
def test_browse_executable_path_functionality(mock_get_open_file_name, qtbot, game_service_mock, launcher_service_mock):
    game_service_mock.get_game_details.return_value = None # No existing game data
    mock_get_open_file_name.return_value = ("/selected/path/to/game.exe", "All Files (*)")
    dialog = GameDetailDialog(game_service_mock, MagicMock(), launcher_service_mock)
    browse_button = dialog.findChild(QPushButton, "browseExecutablePathButton")
    executable_path_line_edit = dialog.findChild(QLineEdit, "executablePathLineEdit")
    browse_button.click()
    mock_get_open_file_name.assert_called_once()
    assert executable_path_line_edit.text() == "/selected/path/to/game.exe"

@patch('PySide6.QtWidgets.QFileDialog.getOpenFileName')
def test_browse_executable_path_cross_platform_filtering(mock_get_open_file_name, qtbot, game_service_mock, launcher_service_mock):
    game_service_mock.get_game_details.return_value = None # No existing game data
    mock_get_open_file_name.return_value = ("/path/to/game.exe", "")
    dialog = GameDetailDialog(game_service_mock, MagicMock(), launcher_service_mock)
    browse_button = dialog.findChild(QPushButton, "browseExecutablePathButton")
    browse_button.click()
    args, _ = mock_get_open_file_name.call_args
    import platform
    system = platform.system().lower()
    if system == "windows":
        assert "Executable Files" in args[3]
    elif system == "darwin":
        assert "Applications" in args[3]
    else:
        assert "Shell Scripts" in args[3]

@patch('PySide6.QtWidgets.QMessageBox.information')
def test_game_launch_button_and_event(mock_qmessagebox_info, qtbot, game_service_mock, game_data_template_fixture, launcher_service_mock):
    game_service_mock.get_game_details.return_value = game_data_template_fixture
    launcher_service_mock.launch_game.return_value = True
    dialog = GameDetailDialog(game_service_mock, MagicMock(), launcher_service_mock, game_id=game_data_template_fixture["id"])
    launch_button = dialog.findChild(QPushButton, "launchGameButton")
    launch_button.click()
    launcher_service_mock.launch_game.assert_called_once_with(game_data_template_fixture["id"])
    mock_qmessagebox_info.assert_called_once()

@patch('PySide6.QtWidgets.QMessageBox.warning')
def test_save_game_with_invalid_executable_path(mock_qmessagebox_warning, qtbot, game_service_mock, launcher_service_mock):
    game_service_mock.get_game_details.return_value = None # No existing game data
    dialog = GameDetailDialog(game_service_mock, MagicMock(), launcher_service_mock)
    dialog.findChild(QLineEdit, "titleLineEdit").setText("Valid Title")
    exe_edit = dialog.findChild(QLineEdit, "executablePathLineEdit")
    exe_edit.setText("some_path.exe")
    
    with patch.object(ExecutableValidator, 'validate_executable') as mock_validate:
        mock_validate.return_value = MagicMock(is_valid=False, error_message="Invalid", suggested_action="Fix it")
        save_button = dialog.findChild(QPushButton, "saveButton")
        qtbot.mouseClick(save_button, QtCore.Qt.LeftButton)
        mock_qmessagebox_warning.assert_called_once()

@patch('PySide6.QtWidgets.QMessageBox.critical')
def test_game_launch_failure_notification(mock_qmessagebox_critical, qtbot, game_service_mock, game_data_template_fixture, launcher_service_mock):
    game_service_mock.get_game_details.return_value = game_data_template_fixture
    launcher_service_mock.launch_game.side_effect = CommandExecutionError("mock_exe", 1, "", "Mock error")
    dialog = GameDetailDialog(game_service_mock, MagicMock(), launcher_service_mock, game_id=game_data_template_fixture["id"])
    launch_button = dialog.findChild(QPushButton, "launchGameButton")
    launch_button.click()
    launcher_service_mock.launch_game.assert_called_once_with(game_data_template_fixture["id"])
    mock_qmessagebox_critical.assert_called_once()

def test_save_button_enabled_on_executable_path_change(qtbot, game_service_mock, game_data_template_fixture, launcher_service_mock):
    game_service_mock.get_game_details.return_value = game_data_template_fixture # Load existing game data
    dialog = GameDetailDialog(game_service_mock, MagicMock(), launcher_service_mock, game_id=game_data_template_fixture["id"])
    save_button = dialog.findChild(QPushButton, "saveButton")
    assert not save_button.isEnabled()
    executable_path_line_edit = dialog.findChild(QLineEdit, "executablePathLineEdit")
    executable_path_line_edit.setText("/new/path.exe")
    assert save_button.isEnabled()

def test_command_line_settings_ui_elements_exist(qtbot, game_service_mock, launcher_service_mock):
    game_service_mock.get_game_details.return_value = None # No existing game data
    dialog = GameDetailDialog(game_service_mock, MagicMock(), launcher_service_mock)
    assert dialog.findChild(QLineEdit, "commandLineSettingsLineEdit") is not None
    assert dialog.findChild(QLabel, "commandLineSettingsWarningLabel") is not None

def test_load_game_data_initializes_command_line_settings(qtbot, game_service_mock, game_data_template_fixture, launcher_service_mock):
    test_settings = "--debug -windowed"
    game_data_template_fixture["command_line_settings"] = test_settings
    game_service_mock.get_game_details.return_value = game_data_template_fixture
    dialog = GameDetailDialog(game_service_mock, MagicMock(), launcher_service_mock, game_id=game_data_template_fixture["id"])
    command_line_edit = dialog.findChild(QLineEdit, "commandLineSettingsLineEdit") # Corrected objectName
    assert command_line_edit.text() == test_settings

def test_get_game_data_includes_command_line_settings(qtbot, game_service_mock, launcher_service_mock):
    game_service_mock.get_game_details.return_value = None # No existing game data
    dialog = GameDetailDialog(game_service_mock, MagicMock(), launcher_service_mock)
    command_line_edit = dialog.findChild(QLineEdit, "commandLineSettingsLineEdit")
    test_settings = "game.exe --option value"
    command_line_edit.setText(test_settings)
    game_data, _ = dialog.get_game_data()
    assert "command_line_settings" in game_data
    assert game_data["command_line_settings"] == test_settings

def test_command_line_settings_validation_displays_warning(qtbot, game_service_mock, launcher_service_mock):
    game_service_mock.get_game_details.return_value = None # No existing game data
    launcher_service_mock.validate_command_line_settings.return_value = (False, "Warning")
    dialog = GameDetailDialog(game_service_mock, MagicMock(), launcher_service_mock)
    command_line_edit = dialog.findChild(QLineEdit, "commandLineSettingsLineEdit")
    warning_label = dialog.findChild(QLabel, "commandLineSettingsWarningLabel")
    command_line_edit.setText('--invalid "path')
    assert warning_label.text() == "Warning"

def test_command_line_settings_validation_clears_warning_on_valid_input(qtbot, game_service_mock, launcher_service_mock):
    game_service_mock.get_game_details.return_value = None # No existing game data
    launcher_service_mock.validate_command_line_settings.side_effect = [(False, "Warning"), (True, None)]
    dialog = GameDetailDialog(game_service_mock, MagicMock(), launcher_service_mock)
    command_line_edit = dialog.findChild(QLineEdit, "commandLineSettingsLineEdit")
    warning_label = dialog.findChild(QLabel, "commandLineSettingsWarningLabel")
    command_line_edit.setText('--invalid "path')
    assert warning_label.text() == "Warning"
    command_line_edit.setText('--valid-command')
    assert warning_label.text() == ""

def test_save_button_enabled_on_command_line_settings_change(qtbot, game_service_mock, game_data_template_fixture, launcher_service_mock):
    game_service_mock.get_game_details.return_value = game_data_template_fixture
    dialog = GameDetailDialog(game_service_mock, MagicMock(), launcher_service_mock, game_id=game_data_template_fixture["id"])
    save_button = dialog.findChild(QPushButton, "saveButton")
    assert not save_button.isEnabled()
    command_line_edit = dialog.findChild(QLineEdit, "commandLineSettingsLineEdit")
    command_line_edit.setText("--new")
    assert save_button.isEnabled()

@pytest.fixture
def image_path_fixture():
    return Path("/path/to/test_image.png")

@pytest.fixture
def qpixmap_mock():
    mock = MagicMock(spec=QtGui.QPixmap)
    mock.isNull.return_value = False
    return mock

def test_image_selection_ui_elements_exist(qtbot, game_service_mock, launcher_service_mock):
    game_service_mock.get_game_details.return_value = None # No existing game data
    dialog = GameDetailDialog(game_service_mock, MagicMock(), launcher_service_mock)
    assert dialog.findChild(QPushButton, "browseImageButton") is not None
    assert dialog.findChild(QLabel, "imagePreviewLabel") is not None

@patch('PySide6.QtWidgets.QFileDialog.getOpenFileName')
def test_browse_image_button_opens_file_dialog(mock_get_open_file_name, qtbot, game_service_mock, launcher_service_mock):
    game_service_mock.get_game_details.return_value = None # No existing game data
    mock_get_open_file_name.return_value = ("", "")
    dialog = GameDetailDialog(game_service_mock, MagicMock(), launcher_service_mock)
    browse_image_button = dialog.findChild(QPushButton, "browseImageButton")
    browse_image_button.click()
    mock_get_open_file_name.assert_called_once()

@patch('src.game_detail_dialog.QFileDialog.getOpenFileName')
@patch('src.game_detail_dialog.QPixmap')
@patch('PySide6.QtWidgets.QLabel.setPixmap')
def test_image_selection_updates_preview_and_saves_path(mock_set_pixmap, mock_qpixmap_constructor, mock_get_open_file_name, qtbot, game_service_mock, game_data_template_fixture, image_path_fixture, qpixmap_mock, launcher_service_mock, image_manager_mock):
    mock_get_open_file_name.return_value = (str(image_path_fixture), "Image Files (*.png)")
    copied_image_path = Path(f"/appdata/temp/{image_path_fixture.name}")
    image_manager_mock.save_temp_image.return_value = copied_image_path
    image_manager_mock.validate_image.return_value = True
    game_service_mock.get_game_details.return_value = {**game_data_template_fixture, "image_path": str(copied_image_path)}
    dialog = GameDetailDialog(game_service_mock, image_manager_mock, launcher_service_mock, game_id=game_data_template_fixture["id"])
    browse_image_button = dialog.findChild(QPushButton, "browseImageButton")
    mock_qpixmap_constructor.return_value = qpixmap_mock # Apply mock_qpixmap_constructor to QPixmap
    browse_image_button.click()
    image_manager_mock.save_temp_image.assert_called_once_with(image_path_fixture)
    mock_set_pixmap.assert_called_once()

@patch('PySide6.QtWidgets.QMessageBox.warning')
@patch('PySide6.QtWidgets.QFileDialog.getOpenFileName')
def test_image_selection_handles_save_error(mock_get_open_file_name, mock_qmessagebox_warning, qtbot, game_service_mock, game_data_template_fixture, image_path_fixture, launcher_service_mock, image_manager_mock):
    game_service_mock.get_game_details.return_value = {**game_data_template_fixture, "image_path": ""} # Ensure game data is loaded
    mock_get_open_file_name.return_value = (str(image_path_fixture), "Image Files (*.png)")
    image_manager_mock.validate_image.return_value = True
    image_manager_mock.save_temp_image.side_effect = Exception("File save error")
    dialog = GameDetailDialog(game_service_mock, image_manager_mock, launcher_service_mock, game_id=game_data_template_fixture["id"])
    browse_image_button = dialog.findChild(QPushButton, "browseImageButton")
    browse_image_button.click()
    mock_qmessagebox_warning.assert_called_once()
    assert dialog.findChild(QLabel, "imagePreviewLabel").text() == "No Image"

@patch('src.game_detail_dialog.QPixmap')
@patch('PySide6.QtWidgets.QLabel.setPixmap')
def test_dialog_loads_existing_image_on_edit(mock_set_pixmap, mock_qpixmap_constructor, qtbot, game_service_mock, game_data_template_fixture, qpixmap_mock, launcher_service_mock):
    existing_image_path = Path("/appdata/existing/image.png")
    game_service_mock.get_game_details.return_value = {**game_data_template_fixture, "image_path": str(existing_image_path)}
    game_service_mock.get_game_image_path.return_value = existing_image_path
    mock_qpixmap_constructor.return_value = qpixmap_mock
    dialog = GameDetailDialog(game_service_mock, MagicMock(), launcher_service_mock, game_id=game_data_template_fixture["id"])
    mock_set_pixmap.assert_called_once()

@patch('PySide6.QtGui.QPixmap')
def test_dialog_no_image_on_edit_if_path_missing(mock_qpixmap_class, qtbot, game_service_mock, game_data_template_fixture, launcher_service_mock):
    game_data_template_fixture["image_path"] = None
    game_service_mock.get_game_details.return_value = game_data_template_fixture
    game_service_mock.get_game_image_path.return_value = None
    dialog = GameDetailDialog(game_service_mock, MagicMock(), launcher_service_mock, game_id=game_data_template_fixture["id"])
    assert dialog.findChild(QLabel, "imagePreviewLabel").text() == "No Image"

def test_play_time_labels_exist_initially(qtbot, game_service_mock, game_data_template_fixture, launcher_service_mock):
    # This test will pass when the UI elements are added to _create_ui
    game_service_mock.get_game_details.return_value = game_data_template_fixture # Ensure game data is loaded
    dialog = GameDetailDialog(game_service_mock, MagicMock(), launcher_service_mock, game_id=game_data_template_fixture["id"])
    play_time_label = dialog.findChild(QLabel, "totalPlayTimeLabel")
    play_time_value_label = dialog.findChild(QLabel, "totalPlayTimeValueLabel")
    assert play_time_label is not None
    assert play_time_value_label is not None

def test_sync_enabled_checkbox_toggles_remote_path_fields(qtbot, game_service_mock, launcher_service_mock):
    game_service_mock.get_game_details.return_value = None # No existing game data
    launcher_service_mock.validate_command_line_settings.return_value = (True, None)
    dialog = GameDetailDialog(game_service_mock, MagicMock(), launcher_service_mock)
    sync_check = dialog.findChild(QCheckBox, "syncEnabledCheckBox")
    remote_path_edit = dialog.findChild(QLineEdit, "remoteSyncPathLineEdit")
    sync_check.setChecked(False)
    assert not remote_path_edit.isEnabled()
    sync_check.setChecked(True)
    assert remote_path_edit.isEnabled()

@patch('PySide6.QtWidgets.QMessageBox.warning')
def test_save_game_with_sync_enabled_and_empty_remote_path_shows_warning(mock_qmessagebox_warning, qtbot, game_service_mock, launcher_service_mock):
    game_service_mock.get_game_details.return_value = None # No existing game data
    launcher_service_mock.validate_command_line_settings.return_value = (True, None)
    dialog = GameDetailDialog(game_service_mock, MagicMock(), launcher_service_mock)
    dialog.findChild(QCheckBox, "syncEnabledCheckBox").setChecked(True)
    dialog.findChild(QLineEdit, "remoteSyncPathLineEdit").setText("")
    dialog.findChild(QLineEdit, "titleLineEdit").setText("Test")
    save_button = dialog.findChild(QPushButton, "saveButton")
    qtbot.mouseClick(save_button, QtCore.Qt.LeftButton)
    mock_qmessagebox_warning.assert_called_once_with(
        dialog,
        "Validation Error",
        "Remote sync path is required when save data sync is enabled."
    )

def test_dialog_does_not_contain_cover_art_path_widget(qtbot, game_service_mock, launcher_service_mock):
    game_service_mock.get_game_details.return_value = None # No existing game data
    dialog = GameDetailDialog(game_service_mock, MagicMock(), launcher_service_mock)
    assert dialog.findChild(QLineEdit, "coverArtPathLineEdit") is None

def test_play_time_labels_display_correctly(qtbot, game_service_mock, game_data_template_fixture, launcher_service_mock):
    game_id = game_data_template_fixture["id"]
    # Mock get_game_details to return our fixture which now includes "play_time_str"
    game_service_mock.get_game_details.return_value = game_data_template_fixture

    dialog = GameDetailDialog(game_service_mock, MagicMock(), launcher_service_mock, game_id=game_id)
    
    # Assert that the play time labels exist
    play_time_label_header = dialog.findChild(QLabel, "totalPlayTimeLabel")
    play_time_value_label = dialog.findChild(QLabel, "totalPlayTimeValueLabel")
    assert play_time_label_header is not None
    assert play_time_value_label is not None

    # Assert that get_game_details was called (implicitly through _load_game_data)
    game_service_mock.get_game_details.assert_called_once_with(game_id)

    # Assert that the play time is displayed correctly from the fixture
    assert play_time_value_label.text() == game_data_template_fixture["play_time_str"]