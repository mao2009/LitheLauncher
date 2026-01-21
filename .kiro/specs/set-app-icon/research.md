# Research & Design Decisions: Set App Icon

## Summary
- **Feature**: set-app-icon
- **Discovery Scope**: Extension / Simple Addition
- **Key Findings**:
  - `MainWindow.setWindowIcon` を用ぁE��ウィンドウアイコンを設定可能、E  - Windows環墁E��おいてタスクバ�EアイコンめEPython のチE��ォルトアイコンから変更するには、`ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID` の呼び出しが忁E��、E  - アイコンファイルは `res/icon.png` を使用する、E
## Research Log

### Windows タスクバ�Eアイコンの表示制御
- **Context**: Windows で Python スクリプトを実行すると、タスクバ�Eに Python のロゴが表示されてしまぁE��題への対処、E- **Sources Consulted**: PySide6 documentation, StackOverflow (AppUserModelID)
- **Findings**: Windows 7 以降では `AppUserModelID` を設定することで、�Eロセスをアプリケーションとして正しく識別させ、個別のアイコンを表示させることができる、E- **Implications**: `main.py` の早ぁE��階！EUI 表示前）で `ctypes` を使用して ID を設定する忁E��がある、E
### アイコンの読み込みと設宁E- **Context**: `MainWindow` にアイコンを適用する方法、E- **Sources Consulted**: PySide6 QIcon API
- **Findings**: `QIcon` は PNG ファイルから直接構築可能。`QMainWindow.setWindowIcon` でウィンドウ全体に適用される、E- **Implications**: `src/main_window.py` の `__init__` また�E `_create_ui` で設定�E琁E��追加する、E
## Architecture Pattern Evaluation
今回は既存�E `MainWindow` クラスを拡張するため、新たなアーキチE��チャパターンの導�Eは不要、E
## Design Decisions

### Decision: AppUserModelID の設定場所
- **Context**: ID は `QApplication` インスタンス化�E前後どちらかで設定する忁E��がある、E- **Selected Approach**: `main.py` の `QApplication` インスタンス化直前に設定する、E- **Rationale**: アプリケーションのグローバルな設定であるため、エントリポイントで行うのが適刁E��E
### Decision: アイコン設定�E場所
- **Context**: アイコン設定を `main.py` で行うぁE`main_window.py` で行うか、E- **Selected Approach**: `MainWindow` クラス冁E��設定する、E- **Rationale**: ウィンドウの外観に関する設定であり、`MainWindow` が�E身のプロパティとして管琁E��る�Eが�E然、E
## Risks & Mitigations
- アイコンファイルが見つからなぁE��合にクラチE��ュするリスク  E`Path.exists()` でチェチE��し、見つからなぁE��合�Eログを�E力してチE��ォルトアイコン�E�なし）で続行する、E- Windows 以外�E環墁E��の影響  E`sys.platform == 'win32'` のチェチE��を行い、仁EOS では ID 設定をスキチE�Eする、E
## References
- [PySide6 QIcon](https://doc.qt.io/qtforpython-6/PySide6/QtGui/QIcon.html)
- [Microsoft AppUserModelID Docs](https://learn.microsoft.com/en-us/windows/win32/shell/appids)
