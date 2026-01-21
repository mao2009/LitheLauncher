# Implementation Plan: Set App Icon

- [x] 1. Windows AppUserModelID の設宁E(P)
  - 1.1 `main.py` に `ctypes` をインポ�Eトし、`myappid` を定義する、E  - 1.2 `QApplication` インスタンス化�E前に `ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)` を呼び出すコードを `main.py` に追加する、E  - 1.3 Windows プラチE��フォームでのみ AppUserModelID を設定するよぁE��`sys.platform == 'win32'` で条件刁E��させる、E  - _Requirements: 2.2_

- [x] 2. メインウィンドウアイコンの設宁E(P)
  - 2.1 `src/main_window.py` に `Path`, `QIcon`, `QPixmap` をインポ�Eトする、E  - 2.2 `MainWindow.__init__` 冁E��アイコンパス (`res/icon.png`) を定義する、E  - 2.3 アイコンファイルが存在するかチェチE��し、存在すれば `QPixmap` と `QIcon` を使用して `self.setWindowIcon()` を呼び出す、E  - 2.4 アイコンファイルが見つからなぁE��合に `logging.warning` を�E力し、クラチE��ュしなぁE��ぁE��する、E  - _Requirements: 1.1, 2.1, 2.3_

- [x] 3. アイコン設定�EチE��チE  - 3.1 `main.py` と `src/main_window.py` の変更をテスト環墁E��実行し、アプリケーション起動時にアイコンが正しく表示されることを手動で確認する、E  - 3.2 アイコンファイル (`res/icon.png`) が存在しなぁE��合に、アプリケーションがデフォルトアイコンで正常に起動し、警告がログに出力されることを確認する、E  - _Requirements: 2.1, 2.2, 2.3_
