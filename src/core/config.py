# -*- coding: utf-8 -*-
"""
設定管理モジュール
"""

import json
import os
from pathlib import Path
from typing import Any, Dict

class ConfigManager:
    """設定マネージャークラス"""
    
    DEFAULT_CONFIG = {
        "download_path": "./downloads",
        "ffmpeg_path": "",
        "aria2c_enabled": True,
        "aria2c_mode": "rpc",  # "rpc" or "cli"
        "aria2c_rpc_url": "http://localhost:6800/jsonrpc",
        "aria2c_rpc_token": "",
        "aria2c_max_connection_per_server": 16,
        "aria2c_split": 16,
        "max_concurrent_downloads": 3,
        "auto_update": True,
        "update_check_url": "https://api.github.com/repos/yunfie-twitter/ytdlp-gui/releases/latest",
        "theme": "light",
        "language": "ja"
    }
    
    def __init__(self, config_path: str = "config.json"):
        self.config_path = Path(config_path)
        self.config: Dict[str, Any] = self.DEFAULT_CONFIG.copy()
    
    def load(self) -> Dict[str, Any]:
        """設定ファイルを読み込む"""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    # デフォルト設定をマージ
                    self.config.update(loaded_config)
            except Exception as e:
                print(f"設定ファイルの読み込みに失敗: {e}")
                self.save()  # デフォルト設定で保存
        else:
            # 初回起動時はデフォルト設定で保存
            self.save()
        
        # ダウンロードフォルダを作成
        download_path = Path(self.config["download_path"])
        download_path.mkdir(parents=True, exist_ok=True)
        
        return self.config
    
    def save(self) -> None:
        """設定ファイルを保存"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"設定ファイルの保存に失敗: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """設定値を取得"""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any, save: bool = True) -> None:
        """設定値を設定"""
        self.config[key] = value
        if save:
            self.save()
    
    def get_all(self) -> Dict[str, Any]:
        """すべての設定を取得"""
        return self.config.copy()
