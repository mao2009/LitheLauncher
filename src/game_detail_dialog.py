# src/game_detail_dialog.py
import os
from PySide6.QtWidgets import QDialog, QLineEdit, QTextEdit, QCheckBox, QPushButton, QFileDialog, QVBoxLayout, QHBoxLayout, QLabel, QWidget, QMessageBox, QGroupBox
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtCore import Qt, QEvent
from src.executable_validator import ExecutableValidator
from src.exceptions import ExecutableValidationError, ImageValidationError, GameNotFoundError, CommandExecutionError, SaveDataSyncError
from pathlib import Path
from src.launcher_service import LauncherService

class GameDetailDialog(QDialog):
    def __init__(self, game_service, image_manager, launcher_service, game_id=None, parent=None):
        super().__init__(parent)
        self.game_service = game_service
        self.image_manager = image_manager
        self.launcher_service = launcher_service
        self.game_id = game_id
        self.executable_validator = ExecutableValidator()
        self.setGeometry(200, 200, 600, 600)

        self._temp_image_path: Path | None = None
        self._game_data: dict = {}

        self._create_ui()
        self.retranslateUi() # 初期翻訳の適用
        
        if self.game_id is not None:
            self._load_game_data()
        else:
            self._game_data = {
                "title": "", "description": "",
                "pre_command": "", "post_command": "", "save_folder": "",
                "sync_enabled": 0, "remote_sync_path": "", "executable_path": "",
                "image_path": ""
            }

        # シグナルとスロットの接続
        self.save_button.clicked.connect(self._save_game)
        self.cancel_button.clicked.connect(self._cancel_game)
        
        self.browse_executable_path_button.clicked.connect(self._browse_executable_path)
        self.launch_game_button.clicked.connect(self._launch_game)
        self.browse_image_button.clicked.connect(self._browse_image)
        self.browse_save_folder_button.clicked.connect(self._browse_save_folder)
        self.browse_remote_sync_path_button.clicked.connect(self._browse_remote_sync_path)

        self.sync_enabled_check_box.stateChanged.connect(self._update_sync_path_fields_state)

        self.title_line_edit.textChanged.connect(self._on_form_changed)
        self.description_text_edit.textChanged.connect(self._on_form_changed)
        self.pre_command_line_edit.textChanged.connect(self._on_form_changed)
        self.post_command_line_edit.textChanged.connect(self._on_form_changed)
        self.save_folder_line_edit.textChanged.connect(self._on_form_changed)
        self.sync_enabled_check_box.stateChanged.connect(self._on_form_changed)
        self.remote_sync_path_line_edit.textChanged.connect(self._on_form_changed)
        self.executable_path_line_edit.textChanged.connect(self._on_form_changed)
        self.command_line_settings_line_edit.textChanged.connect(self._on_form_changed)
        self.command_line_settings_line_edit.textChanged.connect(self._validate_command_line_settings)

        self.save_button.setEnabled(False)
        self._update_sync_path_fields_state()

    def _create_ui(self):
        main_layout = QVBoxLayout(self)

        # 画像プレビューと参照ボタン
        image_layout = QHBoxLayout()
        self.image_preview_label = QLabel()
        self.image_preview_label.setObjectName("imagePreviewLabel")
        self.image_preview_label.setFixedSize(200, 200)
        self.image_preview_label.setAlignment(Qt.AlignCenter)
        self.image_preview_label.setStyleSheet("border: 1px solid gray;")
        image_layout.addWidget(self.image_preview_label)

        image_button_layout = QVBoxLayout()
        self.browse_image_button = QPushButton()
        self.browse_image_button.setObjectName("browseImageButton")
        image_button_layout.addWidget(self.browse_image_button)
        image_button_layout.addStretch()
        image_layout.addLayout(image_button_layout)
        main_layout.addLayout(image_layout)
        
        # タイトル
        title_layout = QHBoxLayout()
        self.title_label_header = QLabel()
        title_layout.addWidget(self.title_label_header)
        self.title_line_edit = QLineEdit()
        self.title_line_edit.setObjectName("titleLineEdit")
        title_layout.addWidget(self.title_line_edit)
        main_layout.addLayout(title_layout)

        # 説明
        description_layout = QHBoxLayout()
        self.description_label_header = QLabel()
        description_layout.addWidget(self.description_label_header)
        self.description_text_edit = QTextEdit()
        self.description_text_edit.setObjectName("descriptionTextEdit")
        description_layout.addWidget(self.description_text_edit)
        main_layout.addLayout(description_layout)

        # 実行ファイルパス
        executable_path_layout = QHBoxLayout()
        self.executable_path_label_header = QLabel()
        executable_path_layout.addWidget(self.executable_path_label_header)
        self.executable_path_line_edit = QLineEdit()
        self.executable_path_line_edit.setObjectName("executablePathLineEdit")
        executable_path_layout.addWidget(self.executable_path_line_edit)
        self.browse_executable_path_button = QPushButton()
        self.browse_executable_path_button.setObjectName("browseExecutablePathButton")
        executable_path_layout.addWidget(self.browse_executable_path_button)
        main_layout.addLayout(executable_path_layout)

        # コマンドライン設定
        command_line_settings_layout = QHBoxLayout()
        self.command_line_settings_label_header = QLabel()
        command_line_settings_layout.addWidget(self.command_line_settings_label_header)
        self.command_line_settings_line_edit = QLineEdit()
        self.command_line_settings_line_edit.setObjectName("commandLineSettingsLineEdit")
        command_line_settings_layout.addWidget(self.command_line_settings_line_edit)
        main_layout.addLayout(command_line_settings_layout)

        self.command_line_settings_warning_label = QLabel("")
        self.command_line_settings_warning_label.setObjectName("commandLineSettingsWarningLabel")
        self.command_line_settings_warning_label.setStyleSheet("color: red;")
        main_layout.addWidget(self.command_line_settings_warning_label)

        # 実行前コマンド
        pre_command_layout = QHBoxLayout()
        self.pre_command_label_header = QLabel()
        pre_command_layout.addWidget(self.pre_command_label_header)
        self.pre_command_line_edit = QLineEdit()
        self.pre_command_line_edit.setObjectName("preCommandLineEdit")
        pre_command_layout.addWidget(self.pre_command_line_edit)
        main_layout.addLayout(pre_command_layout)

        # 実行後コマンド
        post_command_layout = QHBoxLayout()
        self.post_command_label_header = QLabel()
        post_command_layout.addWidget(self.post_command_label_header)
        self.post_command_line_edit = QLineEdit()
        self.post_command_line_edit.setObjectName("postCommandLineEdit")
        post_command_layout.addWidget(self.post_command_line_edit)
        main_layout.addLayout(post_command_layout)

        # ゲーム起動ボタン
        launch_button_layout = QHBoxLayout()
        self.launch_game_button = QPushButton()
        self.launch_game_button.setObjectName("launchGameButton")
        launch_button_layout.addStretch()
        launch_button_layout.addWidget(self.launch_game_button)
        main_layout.addLayout(launch_button_layout)
        
        # プレイ時間表示
        play_time_layout = QHBoxLayout()
        self.total_play_time_label = QLabel()
        self.total_play_time_label.setObjectName("totalPlayTimeLabel")
        play_time_layout.addWidget(self.total_play_time_label)
        self.total_play_time_value_label = QLabel()
        self.total_play_time_value_label.setObjectName("totalPlayTimeValueLabel")
        play_time_layout.addWidget(self.total_play_time_value_label)
        play_time_layout.addStretch()
        main_layout.addLayout(play_time_layout)

        # セーブデータ同期設定
        self.sync_settings_group_box = QGroupBox()
        sync_settings_layout = QVBoxLayout(self.sync_settings_group_box)

        self.sync_enabled_check_box = QCheckBox()
        self.sync_enabled_check_box.setObjectName("syncEnabledCheckBox")
        sync_settings_layout.addWidget(self.sync_enabled_check_box)

        local_save_folder_layout = QHBoxLayout()
        self.save_folder_label_header = QLabel()
        local_save_folder_layout.addWidget(self.save_folder_label_header)
        self.save_folder_line_edit = QLineEdit()
        self.save_folder_line_edit.setObjectName("saveFolderLineEdit")
        local_save_folder_layout.addWidget(self.save_folder_line_edit)
        self.browse_save_folder_button = QPushButton()
        self.browse_save_folder_button.setObjectName("browseSaveFolderButton")
        local_save_folder_layout.addWidget(self.browse_save_folder_button)
        sync_settings_layout.addLayout(local_save_folder_layout)

        remote_sync_path_layout = QHBoxLayout()
        self.remote_sync_path_label_header = QLabel()
        remote_sync_path_layout.addWidget(self.remote_sync_path_label_header)
        self.remote_sync_path_line_edit = QLineEdit()
        self.remote_sync_path_line_edit.setObjectName("remoteSyncPathLineEdit")
        remote_sync_path_layout.addWidget(self.remote_sync_path_line_edit)
        self.browse_remote_sync_path_button = QPushButton()
        self.browse_remote_sync_path_button.setObjectName("browseRemoteSyncPathButton")
        remote_sync_path_layout.addWidget(self.browse_remote_sync_path_button)
        sync_settings_layout.addLayout(remote_sync_path_layout)
        
        main_layout.addWidget(self.sync_settings_group_box)

        # ボタン
        button_layout = QHBoxLayout()
        self.save_button = QPushButton()
        self.save_button.setObjectName("saveButton")
        self.cancel_button = QPushButton()
        self.cancel_button.setObjectName("cancelButton")
        button_layout.addStretch()
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)
        main_layout.addLayout(button_layout)

    def retranslateUi(self):
        if self.game_id is None:
            self.setWindowTitle(self.tr("New Game Registration"))
        else:
            self.setWindowTitle(self.tr("Edit Game"))

        if not self._temp_image_path and (not self._game_data or not self._game_data.get("image_path")):
            self.image_preview_label.setText(self.tr("No Image"))
        
        self.browse_image_button.setText(self.tr("Select Image..."))
        self.title_label_header.setText(self.tr("Title:"))
        self.description_label_header.setText(self.tr("Description:"))
        self.executable_path_label_header.setText(self.tr("Executable Path:"))
        self.browse_executable_path_button.setText(self.tr("Browse..."))
        self.command_line_settings_label_header.setText(self.tr("Command Line Settings:"))
        self.pre_command_label_header.setText(self.tr("Pre-launch Command:"))
        self.post_command_label_header.setText(self.tr("Post-launch Command:"))
        self.launch_game_button.setText(self.tr("Launch Game"))
        self.total_play_time_label.setText(self.tr("Total Play Time:"))
        self.total_play_time_value_label.setText(self.tr("N/A")) # 初期値
        self.sync_settings_group_box.setTitle(self.tr("Save Data Sync Settings"))
        self.sync_enabled_check_box.setText(self.tr("Enable Save Data Sync"))
        self.save_folder_label_header.setText(self.tr("Local Save Folder:"))
        self.browse_save_folder_button.setText(self.tr("Browse..."))
        self.remote_sync_path_label_header.setText(self.tr("Remote Sync Path:"))
        self.remote_sync_path_line_edit.setPlaceholderText(self.tr("Remote path (local folder, S3 bucket URL, etc.)"))
        self.browse_remote_sync_path_button.setText(self.tr("Browse..."))
        self.save_button.setText(self.tr("Save"))
        self.cancel_button.setText(self.tr("Cancel"))

    def changeEvent(self, event):
        if event.type() == QEvent.LanguageChange:
            self.retranslateUi()
        super().changeEvent(event)

    def _load_game_data(self):
        self._block_signals(True)
        game = self.game_service.get_game_details(self.game_id)
        if game:
            self._game_data = game
            self.title_line_edit.setText(self._game_data.get("title", ""))
            self.description_text_edit.setText(self._game_data.get("description", ""))
            self.pre_command_line_edit.setText(self._game_data.get("pre_command", ""))
            self.post_command_line_edit.setText(self._game_data.get("post_command", ""))
            self.save_folder_line_edit.setText(self._game_data.get("save_folder", ""))
            self.sync_enabled_check_box.setChecked(bool(self._game_data.get("sync_enabled", 0)))
            self.remote_sync_path_line_edit.setText(self._game_data.get("remote_sync_path", ""))
            self.executable_path_line_edit.setText(self._game_data.get("executable_path", ""))
            self.command_line_settings_line_edit.setText(self._game_data.get("command_line_settings", ""))
            
            image_path_str = self._game_data.get("image_path")
            if image_path_str:
                actual_image_path = self.game_service.get_game_image_path(self.game_id)
                if actual_image_path:
                    self._update_image_preview(actual_image_path)
                else:
                    self._temp_image_path = None
                    self.image_preview_label.setText(self.tr("No Image"))
            else:
                self._temp_image_path = None
                self.image_preview_label.setText(self.tr("No Image"))
            
            # プレイ時間表示の更新
            # game_service.get_game_details ですでに play_time_str が追加されていることを想定
            self.total_play_time_value_label.setText(self._game_data.get("play_time_str", self.tr("N/A")))

        self._block_signals(False)
        self.save_button.setEnabled(False)

    def get_game_data(self):
        self._game_data["title"] = self.title_line_edit.text()
        self._game_data["description"] = self.description_text_edit.toPlainText()
        self._game_data["pre_command"] = self.pre_command_line_edit.text()
        self._game_data["post_command"] = self.post_command_line_edit.text()
        self._game_data["save_folder"] = self.save_folder_line_edit.text()
        self._game_data["sync_enabled"] = int(self.sync_enabled_check_box.isChecked())
        self._game_data["remote_sync_path"] = self.remote_sync_path_line_edit.text()
        self._game_data["executable_path"] = self.executable_path_line_edit.text()
        self._game_data["command_line_settings"] = self.command_line_settings_line_edit.text()
        if self._temp_image_path:
            self._game_data["image_path"] = str(self._temp_image_path)
        elif "image_path" in self._game_data:
            pass
        else:
            self._game_data["image_path"] = ""
        return self._game_data, self._temp_image_path

    def _on_form_changed(self):
        self.save_button.setEnabled(True)

    def _validate_command_line_settings(self):
        settings_string = self.command_line_settings_line_edit.text()
        is_valid, warning_message = self.launcher_service.validate_command_line_settings(settings_string)
        if not is_valid:
            self.command_line_settings_warning_label.setText(warning_message)
        else:
            self.command_line_settings_warning_label.setText("")

    def _block_signals(self, block: bool):
        self.title_line_edit.blockSignals(block)
        self.description_text_edit.blockSignals(block)
        self.pre_command_line_edit.blockSignals(block)
        self.post_command_line_edit.blockSignals(block)
        self.save_folder_line_edit.blockSignals(block)
        self.sync_enabled_check_box.blockSignals(block)
        self.remote_sync_path_line_edit.blockSignals(block)
        self.executable_path_line_edit.blockSignals(block)
        self.command_line_settings_line_edit.blockSignals(block)

    def _update_sync_path_fields_state(self):
        is_enabled = self.sync_enabled_check_box.isChecked()
        self.remote_sync_path_line_edit.setEnabled(is_enabled)
        self.browse_remote_sync_path_button.setEnabled(is_enabled)

    def _browse_save_folder(self):
        folder_path = QFileDialog.getExistingDirectory(
            self, self.tr("Select Save Folder"), self.save_folder_line_edit.text()
        )
        if folder_path:
            self.save_folder_line_edit.setText(folder_path)

    def _browse_remote_sync_path(self):
        folder_path = QFileDialog.getExistingDirectory(
            self, self.tr("Select Remote Sync Folder"), self.remote_sync_path_line_edit.text()
        )
        if folder_path:
            self.remote_sync_path_line_edit.setText(folder_path)

    def _browse_executable_path(self):
        import platform
        system = platform.system().lower()
        if system == "windows":
            file_filter = self.tr("Executable Files (*.exe *.bat *.cmd *.com *.pif *.scr *.msi);;Batch Files (*.bat *.cmd);;Executable Files (*.exe);;All Files (*.*)")
        elif system == "darwin":
            file_filter = self.tr("Executable Files (*.app *.command *.tool);;Applications (*.app);;Command Files (*.command *.tool);;All Files (*.*)")
        else:
            file_filter = self.tr("Executable Files (*.sh *.run *.bin *.AppImage);;Shell Scripts (*.sh);;Binary Files (*.bin *.run);;AppImage (*.AppImage);;All Files (*.*)")
        
        file_path, _ = QFileDialog.getOpenFileName(
            self, self.tr("Select Executable File"), "", file_filter
        )
        if file_path:
            self.executable_path_line_edit.setText(file_path)

    def _browse_image(self):
        file_filter = self.tr("Image Files (*.png *.jpg *.jpeg *.webp *.gif);;All Files (*.*)")
        selected_file_path_str, _ = QFileDialog.getOpenFileName(
            self, self.tr("Select Image File"), "", file_filter
        )
        if selected_file_path_str:
            selected_file_path = Path(selected_file_path_str)
            try:
                if not self.image_manager.validate_image(selected_file_path):
                    QMessageBox.warning(self, self.tr("Error"), self.tr("Selected image file is invalid."))
                    self._temp_image_path = None
                    self.image_preview_label.setText(self.tr("No Image"))
                    self._on_form_changed()
                    return
                self._temp_image_path = self.image_manager.save_temp_image(selected_file_path)
                self._update_image_preview(self._temp_image_path)
                self._on_form_changed()
            except Exception as e:
                QMessageBox.warning(self, self.tr("Error"), self.tr("Failed to save or validate temporary image: %1").replace("%1", str(e)))
                self._temp_image_path = None
                self.image_preview_label.setText(self.tr("No Image"))
                self._on_form_changed()

    def _update_image_preview(self, image_path: Path):
        pixmap = QPixmap(str(image_path))
        if not pixmap.isNull():
            scaled_pixmap = pixmap.scaled(
                self.image_preview_label.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.image_preview_label.setPixmap(scaled_pixmap)
            self.image_preview_label.setText("")
        else:
            self.image_preview_label.setText(self.tr("No Image"))

    def _launch_game(self):
        if self.game_id is None:
            QMessageBox.warning(self, self.tr("Warning"), self.tr("Please save the game first before launching."))
            return
        try:
            self.launcher_service.launch_game(self.game_id)
            QMessageBox.information(self, self.tr("Success"), self.tr("Game launched successfully."))
        except GameNotFoundError as e:
            QMessageBox.critical(self, self.tr("Error"), self.tr("Game launch error: %1").replace("%1", str(e)))
        except ExecutableValidationError as e:
            QMessageBox.critical(self, self.tr("Error"), self.tr("Executable validation error: %1").replace("%1", str(e)))
        except CommandExecutionError as e:
            error_message = self.tr("Command execution error: %1").replace("%1", str(e))
            if "WinError 740" in str(e):
                error_message = self.tr("Administrator privileges are required to launch this game. Please restart Game Launcher as an administrator.")
            QMessageBox.critical(self, self.tr("Error"), error_message)
        except SaveDataSyncError as e:
            QMessageBox.critical(self, self.tr("Error"), self.tr("Save data sync error: %1").replace("%1", str(e)))
        except Exception as e:
            QMessageBox.critical(self, self.tr("Error"), self.tr("An unexpected error occurred: %1").replace("%1", str(e)))

    def _save_game(self):
        executable_path = self.executable_path_line_edit.text()
        if executable_path:
            validation_result = self.executable_validator.validate_executable(executable_path)
            if not validation_result.is_valid:
                QMessageBox.warning(
                    self, 
                    self.tr("Executable Validation Error"), 
                    self.tr("%1\n\nSuggested Action: %2").replace("%1", validation_result.error_message).replace("%2", validation_result.suggested_action)
                )
                return
        game_data, temp_image_path = self.get_game_data()
        if game_data.get("sync_enabled") and not game_data.get("remote_sync_path"):
            QMessageBox.warning(
                self, 
                self.tr("Validation Error"), 
                self.tr("Remote sync path is required when save data sync is enabled.")
            )
            return
        try:
            if self.game_id is None:
                self.game_service.register_game(game_data, temp_image_path)
            else:
                self.game_service.update_game_details(self.game_id, game_data, temp_image_path)
            self.accept()
        except (ExecutableValidationError, ImageValidationError) as e:
            QMessageBox.warning(self, self.tr("Validation Error"), self.tr("Input has issues: %1").replace("%1", str(e)))
        except GameNotFoundError as e:
            QMessageBox.critical(self, self.tr("Error"), self.tr("Game not found: %1").replace("%1", str(e)))
        except Exception as e:
            QMessageBox.critical(self, self.tr("Save Error"), self.tr("An unexpected error occurred during game save: %1").replace("%1", str(e)))

    def _cancel_game(self):
        if self._temp_image_path:
            try:
                self.image_manager.cleanup_temp_image(self._temp_image_path)
            except Exception as e:
                print(f"Warning: Failed to clean up temporary image {self._temp_image_path}: {e}")
            finally:
                self._temp_image_path = None
        self.reject()
