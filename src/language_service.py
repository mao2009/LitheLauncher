# src/language_service.py
import os
import logging
from PySide6.QtCore import QObject, QSettings, QTranslator, QLocale, QCoreApplication
from PySide6.QtWidgets import QApplication
import sys # sys を追加

# PyInstallerでバンドルされた環境でのリソースパス解決
def resource_path(relative_path):
    """
    Get absolute path to resource, works for dev and PyInstaller
    """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class LanguageService(QObject):
    def __init__(self, org_name="LitheLauncher", app_name="GameLauncher"):
        super().__init__()
        self.org_name = org_name
        self.app_name = app_name
        self.settings = QSettings(self.org_name, self.app_name)
        self.translator = QTranslator()
        self.logger = logging.getLogger(__name__)
        
        # Load saved language or detect system default
        self._current_locale = self.settings.value("language", "system")
        self._apply_initial_language()

    def get_available_languages(self) -> list[dict[str, str]]:
        """利用可能な言語のリストを返す"""
        return [
            {"code": "system", "name": "System Default"},
            {"code": "en_US", "name": "English"},
            {"code": "ja_JP", "name": "日本語"}
        ]

    def _detect_system_locale(self) -> str:
        """システムロケールを検出する"""
        return QLocale.system().name()

    def get_current_locale(self) -> str:
        """現在設定されているロケールコードを返す"""
        if self._current_locale == "system":
            return self._detect_system_locale()
        return self._current_locale

    def change_language(self, locale_code: str) -> bool:
        """言語を変更し、設定を保存する"""
        success = self._load_translator(locale_code)
        if success:
            self._current_locale = locale_code
            self.settings.setValue("language", locale_code)
            return True
        elif locale_code == "en_US" or locale_code == "system":
            # English is default (no qm needed), so it's a "success" in terms of setting
            self._current_locale = locale_code
            self.settings.setValue("language", locale_code)
            return True
        
        return False

    def _apply_initial_language(self):
        """初期起動時の言語を適用する"""
        self._load_translator(self._current_locale)

    def _load_translator(self, locale_code: str) -> bool:
        """QTranslator に翻訳ファイルをロードして QApplication にインストールする"""
        # Remove old translator if any
        QCoreApplication.removeTranslator(self.translator)
        
        actual_locale = locale_code
        if locale_code == "system":
            actual_locale = self._detect_system_locale()

        if actual_locale == "en_US":
            return True # English is source, no translator needed

        # Assuming translations are in res/translations/lithelauncher_[locale].qm
        # For development, check both relative and project root
        translations_dir = resource_path(os.path.join("res", "translations")) # resource_path を適用
        filename = f"lithelauncher_{actual_locale}.qm"
        
        # resource_path を使用して翻訳ファイルのフルパスを構築
        full_translation_path = os.path.join(translations_dir, filename)

        if self.translator.load(full_translation_path): # フルパスでロードを試みる
            QCoreApplication.installTranslator(self.translator)
            return True
        
        self.logger.warning(f"Failed to load translation file: {full_translation_path}") # 読み込み失敗時にログ出力
        return False

