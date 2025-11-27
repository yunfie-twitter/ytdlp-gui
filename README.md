# yt-dlp GUI

PyQt5ベースのyt-dlp GUIアプリケーション。aria2c統合、プラグインシステム、自動更新機能を備えています。

## 特徴

- 🎨 **モダンなGUI**: PyQt5による直感的なインターフェース
- ⚡ **高速ダウンロード**: aria2c統合による並列ダウンロード
- 🔌 **プラグインシステム**: 機能拡張可能なプラグインAPI
- 🔄 **自動更新**: リモートマニフェストからの自動更新チェック
- 📊 **詳細な進捗表示**: タスクごとの進捗バーと全体進捗
- ⚙️ **柔軟な設定**: ダウンロード先、ffmpegパスなどの設定

## 必要要件

- Python 3.8以上
- PyQt5
- yt-dlp
- aria2c (オプション、高速ダウンロード用)
- ffmpeg (オプション、動画変換用)

## インストール

```bash
# リポジトリをクローン
git clone https://github.com/yunfie-twitter/ytdlp-gui.git
cd ytdlp-gui

# 依存関係をインストール
pip install -r requirements.txt

# アプリケーションを起動
python main.py
```

## aria2cのインストール（推奨）

### Windows
```bash
winget install aria2.aria2
```

### macOS
```bash
brew install aria2
```

### Linux (Ubuntu/Debian)
```bash
sudo apt install aria2
```

## 使い方

1. アプリケーションを起動
2. URLフィールドに動画URLを入力
3. 出力フォーマットと品質を選択
4. 「ダウンロード開始」をクリック

### メニューバー

- **File**: 設定、終了
- **Downloads**: ダウンロード管理、履歴
- **Tools**: プラグイン管理、ログビューア
- **Help**: バージョン情報、アップデート確認

## プラグイン開発

プラグインは `plugins/` フォルダに配置します。

### 基本的なプラグイン構造

```python
# plugins/my_plugin.py

def register(app):
    """プラグイン登録関数（必須）"""
    app.log("マイプラグインを読み込みました")
    
    # フックを登録
    app.register_hook('on_download_start', on_start)
    app.register_hook('on_complete', on_complete)

def on_start(info):
    print(f"ダウンロード開始: {info['url']}")

def on_complete(info):
    print(f"ダウンロード完了: {info['filename']}")

def get_menu_actions():
    """メニューバーに追加するアクション"""
    return [
        {
            'text': 'マイプラグイン',
            'callback': lambda: print('実行!')
        }
    ]
```

### プラグインAPI

- `app.register_hook(name, callback)`: イベントフックを登録
- `app.log(message)`: ログに出力
- `app.open_file(path)`: ファイルを開く
- `app.get_config()`: 設定を取得
- `app.set_config(key, value)`: 設定を変更

### 利用可能なフック

- `on_download_start`: ダウンロード開始時
- `on_progress`: 進捗更新時
- `on_complete`: ダウンロード完了時
- `on_error`: エラー発生時

## 設定ファイル

`config.json` は初回起動時に自動生成されます。

```json
{
  "download_path": "./downloads",
  "ffmpeg_path": "",
  "aria2c_enabled": true,
  "aria2c_mode": "rpc",
  "aria2c_rpc_url": "http://localhost:6800/jsonrpc",
  "aria2c_rpc_token": "",
  "max_concurrent_downloads": 3,
  "auto_update": true,
  "update_check_url": "https://api.github.com/repos/yunfie-twitter/ytdlp-gui/releases/latest"
}
```

## ライセンス

MIT License

## 作者

ゆんふぃ ([@yunfie_misskey](https://twitter.com/yunfie_misskey))
