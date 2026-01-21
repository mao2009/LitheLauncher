import unittest
from unittest.mock import MagicMock, patch
from PySide6.QtCore import QSettings, QTranslator, QCoreApplication
from src.language_service import LanguageService
import os

class TestLanguageService(unittest.TestCase):
    def setUp(self):
        # Use a temporary organization/application name for QSettings to avoid affecting the real ones
        self.org_name = "LitheLauncherTest"
        self.app_name = "LanguageServiceTest"
        self.settings = QSettings(self.org_name, self.app_name)
        self.settings.clear()
        
        # Mock QApplication instance if it doesn't exist
        if not QCoreApplication.instance():
            self.app = QCoreApplication([])
        else:
            self.app = QCoreApplication.instance()

    def tearDown(self):
        self.settings.clear()

    def test_get_available_languages(self):
        service = LanguageService(self.org_name, self.app_name)
        languages = service.get_available_languages()
        
        # Expect at least Japanese, English, and System Default
        codes = [lang['code'] for lang in languages]
        self.assertIn("ja_JP", codes)
        self.assertIn("en_US", codes)
        self.assertIn("system", codes)

    def test_detect_system_locale(self):
        service = LanguageService(self.org_name, self.app_name)
        locale = service._detect_system_locale()
        self.assertTrue(isinstance(locale, str))
        self.assertGreater(len(locale), 0)

    def test_settings_persistence(self):
        service = LanguageService(self.org_name, self.app_name)
        
        # Set to Japanese
        service.change_language("ja_JP")
        self.assertEqual(service.get_current_locale(), "ja_JP")
        
        # New service instance should load the saved setting
        new_service = LanguageService(self.org_name, self.app_name)
        self.assertEqual(new_service.get_current_locale(), "ja_JP")

    @patch('PySide6.QtCore.QTranslator.load')
    @patch('PySide6.QtCore.QCoreApplication.installTranslator')
    def test_change_language_installs_translator(self, mock_install, mock_load):
        mock_load.return_value = True
        service = LanguageService(self.org_name, self.app_name)
        
        result = service.change_language("ja_JP")
        
        self.assertTrue(result)
        mock_load.assert_called()
        mock_install.assert_called()

    @patch('PySide6.QtCore.QTranslator.load')
    def test_change_language_fallback_logic(self, mock_load):
        # Simulate translation file not found
        mock_load.return_value = False
        service = LanguageService(self.org_name, self.app_name)
        service._current_locale = "en_US" # Set a known state
        
        result = service.change_language("non_existent")
        
        self.assertFalse(result)
        # Should remain en_US because change failed
        self.assertEqual(service.get_current_locale(), "en_US")

if __name__ == '__main__':
    unittest.main()
