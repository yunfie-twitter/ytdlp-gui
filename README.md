# yt-dlp GUI

PyQt5ベースのyt-dlpグラフィカルインターフェース

## 機能

- ✅ **メニューバーインターフェース**
  - ファイルメニュー: 設定、終了
  - ダウンロードメニュー: タスク管理、フォルダを開く
  - ツールメニュー: aria2c/ffmpeg確認、プラグイン再読み込み
  - ヘルプメニュー: 更新確認、アプリ情報

- ✅ **aria2c統合**
  - RPCモード（推奨）: JSON-RPC経由でaria2を制御
  - CLIモード（フォールバック）: subprocess経由で直接実行
  - マルチスレッドダウンロード
  - 分割ダウンロードサポート

- ✅ **進捗バー**
  - 個別タスクごとの進捗表示
  - リアルタイム更新
  - ステータス表示（情報取得中、ダウンロード中、完了）

- ✅ **プラグインシステム**
  - `plugins/` フォルダにPythonモジュールを配置
  - フックAPI: `on_download_start`, `on_progress`, `on_complete`, `on_error`
  - メニューアクション追加機能
  - 動的ロード・リロード

- ✅ **自動更新機能**
  - リモートマニフェスト確認
  - バージョン比較
  - 自動または手動更新

- ✅ **設定管理**
  - `config.json` による永続化
  - 起動時自動生成
  - UIから変更可能

## インストール

### 前提条件

1. **Python 3.8+**
2. **yt-dlp**
   ```bash
   pip install yt-dlp
   ```

3. **aria2c** (推奨)
   - Windows: [aria2 releases](https://github.com/aria2/aria2/releases)
   - macOS: `brew install aria2`
   - Linux: `sudo apt install aria2` / `sudo yum install aria2`

4. **ffmpeg** (任意)
   - Windows: [ffmpeg downloads](https://ffmpeg.org/download.html)
   - macOS: `brew install ffmpeg`
   - Linux: `sudo apt install ffmpeg`

### アプリインストール

```bash
# リポジトリをクローン
git clone https://github.com/yunfie-twitter/ytdlp-gui.git
cd ytdlp-gui

# 依存関係をインストール
pip install -r requirements.txt

# アプリを起動
python main.py
```

## 使い方

### 基本的なダウンロード

1. アプリを起動
2. URL欄に動画URLを入力
3. 保存先を確認（必要に応じて変更）
4. 「ダウンロード」ボタンをクリック
5. 進捗バーで進捗を確認

### aria2cのRPCモード設定

#### aria2cをRPCサーバーとして起動

```bash
aria2c --enable-rpc --rpc-listen-all=false --rpc-listen-port=6800
```

シークレットトークンを使う場合:

```bash
aria2c --enable-rpc --rpc-secret=YOUR_SECRET_TOKEN
```

#### アプリ設定

1. メニューバー → ファイル → 設定
2. aria2cタブを選択
3. RPCモード使用にチェック
4. RPC URLを設定（デフォルト: `http://localhost:6800/jsonrpc`）
5. 必要に応じてRPCシークレットを設定
6. 保存

### プラグインの作成

1. `plugins/` フォルダに `.py` ファイルを作成
2. 必須関数 `register(app)` を実装

例:

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
My Custom Plugin
"""

def register(app):
    """プラグイン登録"""
    app.log('My Plugin loaded!')
    
    # フックを登録
    app.register_hook('on_download_start', on_start)
    app.register_hook('on_complete', on_complete)
    
    # メニューアクションを追加
    app.add_menu_action('Tools', 'My Action', my_action)

def on_start(info):
    print(f'Starting: {info["url"]}')

def on_complete(info):
    print(f'Completed: {info.get("filename")}')

def my_action():
    print('My action executed!')
```

### 利用可能なAppAPI

- `app.register_hook(name, callback)` - フックを登録
- `app.log(message)` - ログにメッセージを追加
- `app.open_file(path)` - ファイルをシステムデフォルトで開く
- `app.get_config()` - 設定を取得
- `app.set_config(key, value)` - 設定を変更
- `app.add_menu_action(menu_name, action_name, callback)` - メニューアクションを追加

### 利用可能なフック

- `on_download_start(info)` - ダウンロード開始時
  - `info`: `{"url": str, "output_dir": str}`

- `on_progress(info)` - 進捗更新時
  - `info`: `{"url": str, "progress": int}`

- `on_complete(info)` - ダウンロード完了時
  - `info`: `{"url": str, "output_dir": str, "filename": str}`

- `on_error(info)` - エラー発生時
  - `info`: `{"url": str, "error": str}`

## 設定ファイル (config.json)

初回起動時に自動生成されます。以下の項目を含みます:

- `output_dir`: デフォルトの保存先
- `ffmpeg_path`: ffmpeg実行ファイルパス
- `aria2c_path`: aria2c実行ファイルパス
- `aria2c_rpc_url`: aria2c RPC URL
- `aria2c_rpc_secret`: aria2c RPCシークレットトークン
- `aria2c_use_rpc`: RPCモードを使用するか
- `aria2c_max_connections`: 最大接続数
- `aria2c_split`: 分割数
- `auto_check_updates`: 起動時の更新確認
- `auto_update`: 自動更新
- `update_manifest_url`: 更新マニフェストURL

## トラブルシューティング

### aria2cに接続できない

1. aria2cがインストールされているか確認
2. RPCモードでaria2cが起動しているか確認
3. メニューバー → ツール → aria2c接続確認でステータスを確認
4. RPC接続失敗時はCLIモードに自動フォールバック

### ダウンロードが失敗する

1. URLが有効か確認
2. yt-dlpが最新バージョンか確認: `pip install -U yt-dlp`
3. ログでエラーメッセージを確認

### ffmpegが見つからない

1. ffmpegがインストールされているか確認
2. 設定でffmpegパスを正しく設定
3. メニューバー → ツール → ffmpeg確認でステータスを確認

## ライセンス

MIT License

## 開発者

yunfie

## 貼献

Pull Requestを歓迎します！

1. フォーク
2. フィーチャーブランチを作成 (`git checkout -b feature/amazing-feature`)
3. 変更をコミット (`git commit -m 'Add amazing feature'`)
4. ブランチにプッシュ (`git push origin feature/amazing-feature`)
5. Pull Requestを作成
