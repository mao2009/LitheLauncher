import pytest
from unittest.mock import MagicMock, patch, call
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QWidget, QScrollArea, QPushButton, QVBoxLayout, QDialog, QMessageBox, QMenu
from PySide6.QtGui import QAction
from PySide6.QtCore import Qt, QPoint
from src.exceptions import GameNotFoundError, CommandExecutionError, SaveDataSyncError
from src.main_window import MainWindow
from src.flow_layout import FlowLayout
from src.game_card_widget import GameCardWidget
from unittest.mock import ANY

@pytest.fixture
def game_service_mock():
    return MagicMock()

@pytest.fixture
def launcher_service_mock():
    return MagicMock()

@pytest.fixture
def language_service_mock():
    mock = MagicMock()
    mock.get_available_languages.return_value = [
        {"code": "system", "name": "System Default"},
        {"code": "en_US", "name": "English"},
        {"code": "ja_JP", "name": "日本語"}
    ]
    mock.settings = MagicMock()
    mock.settings.value.return_value = "system"
    return mock

@pytest.fixture
def mock_game_detail_dialog(mocker):
    return mocker.patch('src.main_window.GameDetailDialog', autospec=True)

@pytest.fixture
def mock_get_logger(mocker):
    return mocker.patch('src.main_window.get_logger', autospec=True)

@pytest.fixture
def mock_qmessagebox(mocker):
    mock = mocker.patch('src.main_window.QMessageBox', autospec=True)
    mock.Yes = QMessageBox.Yes
    mock.No = QMessageBox.No
    return mock

def test_main_window_creation_and_ui_structure(qtbot, game_service_mock, launcher_service_mock, language_service_mock, mock_get_logger, mock_qmessagebox):
    main_window = MainWindow(game_service_mock, launcher_service_mock, language_service_mock)
    QApplication.instance().processEvents()
    assert isinstance(main_window, QMainWindow)
    mock_get_logger.assert_called_once_with('src.main_window', 'game_launcher.log')
    main_window.close()

def test_main_window_loads_and_displays_game_cards(qtbot, game_service_mock, launcher_service_mock, language_service_mock, mock_get_logger, mock_qmessagebox):
    game_data_list = [
        {"id": 1, "title": "Game A", "description": "", "pre_command": "", "post_command": "", "save_folder": "", "sync_enabled": 0, "remote_sync_path": "", "executable_path": ""},
        {"id": 2, "title": "Game B", "description": "", "pre_command": "", "post_command": "", "save_folder": "", "sync_enabled": 0, "remote_sync_path": "", "executable_path": ""}
    ]
    game_service_mock.get_game_list.return_value = game_data_list
    
    with patch('src.main_window.QThreadPool.globalInstance') as mock_pool:
        main_window = MainWindow(game_service_mock, launcher_service_mock, language_service_mock)
        # Simulate worker finishing
        main_window._on_games_loaded(game_data_list)
        
    QApplication.instance().processEvents()
    assert main_window.controller.total_items == 2
    main_window.close()

def test_game_card_double_click_launches_game(qtbot, game_service_mock, launcher_service_mock, language_service_mock, mock_get_logger, mock_qmessagebox):
    game_to_launch_id = 1
    game_data = {"id": game_to_launch_id, "title": "Launchable Game"}
    game_service_mock.get_game_list.return_value = [game_data]
    
    with patch('src.main_window.QThreadPool.globalInstance') as mock_pool:
        main_window = MainWindow(game_service_mock, launcher_service_mock, language_service_mock)
        main_window._on_games_loaded([game_data])
        
    QApplication.instance().processEvents()
    # Find the widget from the controller
    game_card = main_window.controller.visible_widgets[0]
    game_card.launched.emit(game_to_launch_id)
    QApplication.instance().processEvents()
    launcher_service_mock.launch_game.assert_called_once_with(game_to_launch_id)
    main_window.close()

def test_game_card_context_menu_edit_opens_dialog_and_updates_game(qtbot, game_service_mock, launcher_service_mock, language_service_mock, mock_game_detail_dialog, mock_get_logger, mock_qmessagebox):
    game_to_edit_id = 1
    original_game_data = {"id": game_to_edit_id, "title": "Game to Edit"}
    updated_game_data_from_dialog = {"title": "Edited Game"}
    game_service_mock.get_game_list.side_effect = [[original_game_data], [{**original_game_data, **updated_game_data_from_dialog}]]
    game_service_mock.get_game_details.return_value = original_game_data
    
    with patch('src.main_window.QThreadPool.globalInstance') as mock_pool:
        main_window = MainWindow(game_service_mock, launcher_service_mock, language_service_mock)     
        main_window._on_games_loaded([original_game_data])
        mock_pool.return_value.start.reset_mock()

        QApplication.instance().processEvents()
        game_card = main_window.controller.visible_widgets[0]
        mock_dialog_instance = mock_game_detail_dialog.return_value
        mock_dialog_instance.exec.return_value = QDialog.Accepted
        mock_dialog_instance.get_game_data.return_value = (updated_game_data_from_dialog, None)
        game_card.edited.emit(game_to_edit_id)
        QApplication.instance().processEvents()
        mock_dialog_instance.exec.assert_called_once()
        # MainWindow should start a new worker to reload
        mock_pool.return_value.start.assert_called_once()
    main_window.close()

    

def test_game_card_context_menu_delete_deletes_game(qtbot, game_service_mock, launcher_service_mock, language_service_mock, mock_qmessagebox, mock_get_logger):
    game_to_delete_id = 1
    game_data = {"id": game_to_delete_id, "title": "Game to Delete"}
    game_service_mock.get_game_list.side_effect = [[game_data], []]
    
    with patch('src.main_window.QThreadPool.globalInstance') as mock_pool:
        main_window = MainWindow(game_service_mock, launcher_service_mock, language_service_mock)
        main_window._on_games_loaded([game_data])
        
    QApplication.instance().processEvents()
    game_card = main_window.controller.visible_widgets[0]
    mock_qmessagebox.question.return_value = QMessageBox.Yes
    game_card.deleted.emit(game_to_delete_id)
    QApplication.instance().processEvents()
    game_service_mock.remove_game.assert_called_once_with(game_to_delete_id)
    main_window.close()


def test_add_game_button_opens_dialog(qtbot, game_service_mock, launcher_service_mock, language_service_mock, mock_game_detail_dialog, mock_get_logger):
    main_window = MainWindow(game_service_mock, launcher_service_mock, language_service_mock)
    QApplication.instance().processEvents()
    mock_dialog_instance = mock_game_detail_dialog.return_value
    mock_dialog_instance.exec.return_value = QDialog.Rejected
    main_window.add_game_action.trigger()
    QApplication.instance().processEvents()
    mock_dialog_instance.exec.assert_called_once()
    main_window.close()