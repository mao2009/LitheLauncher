# Requirements Document

## Introduction
大量データ時のスクロール性能を維持するため、GameCardWidget内の画像デコード処理を非同期化し、メインUIスレッド（GUIスレッド）をブロックせずに画像を読み込み・表示する仕組みを構築します。

## Requirements

### Requirement 1: 非同期画像デコード
**Objective:** ユーザーとして、大量のゲームを高速にスクロールしてもUIが固まらないようにしたい。そのため、画像のデコード処理をバックグラウンドスレッドで実行し、メインスレッドの負荷を軽減してほしい。

#### Acceptance Criteria
1. While 画像をデコード中, the ImageLoader shall メインUIスレッドをブロックせずに処理を継続する
2. When 画像のデコードが完了した, the ImageLoader shall デコード済みの画像データをGUIスレッドに通知する
3. When デコード済み画像データの通知を受け取った, the GameCardWidget shall 速やかに画像を画面に反映する

### Requirement 2: 画像デコード用のワーカープール管理
**Objective:** システムとして、大量の画像読み込みリクエストが発生した際にリソースを効率的に管理し、システム全体の安定性を維持したい。

#### Acceptance Criteria
1. The ImageLoader shall デコード処理を管理するための専用のワーカープール（QThreadPool等）を使用する
2. When スクロール等により大量のリクエストが発生した, the ImageLoader shall 同時実行されるデコードスレッド数を制限する
3. When 未処理のリクエストが存在する状態で新しいリクエストが追加された, the ImageLoader shall リクエストをキューに蓄積し、順次処理する

### Requirement 3: スクロール性能とユーザー体験
**Objective:** ユーザーとして、スクロール中に画像が順次表示されることで、アプリが動作していることを実感し、快適に操作したい。

#### Acceptance Criteria
1. While 画像のロード・デコードが完了していない, the GameCardWidget shall プレースホルダー画像（または「読み込み中」を示す表示）を表示する
2. When スクロールが高速で行われ、ウィジェットが再利用された, the ImageLoader shall 以前の（現在は不要になった）デコードリクエストをキャンセルまたは無視する
3. The system shall 大量（1000件以上）のゲームカードが存在する場合でも、スクロール時のFPS低下を最小限に抑える