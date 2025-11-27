# -*- coding: utf-8 -*-
"""
aria2c統合モジュール
"""

import json
import requests
import subprocess
import shutil
from typing import Dict, Any, Optional, List
from pathlib import Path

class Aria2cManager:
    """
aria2c管理クラス
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.mode = config.get("aria2c_mode", "rpc")
        self.rpc_url = config.get("aria2c_rpc_url", "http://localhost:6800/jsonrpc")
        self.token = config.get("aria2c_rpc_token", "")
        self.max_connection = config.get("aria2c_max_connection_per_server", 16)
        self.split = config.get("aria2c_split", 16)
    
    def is_available(self) -> bool:
        """
aria2cが利用可能か確認
        """
        # CLIモードの場合は実行ファイルが存在するか確認
        if self.mode == "cli":
            return shutil.which("aria2c") is not None
        
        # RPCモードの場合は接続テスト
        try:
            response = self._rpc_call("aria2.getVersion")
            return response is not None
        except:
            return False
    
    def _rpc_call(self, method: str, params: Optional[List] = None) -> Optional[Dict]:
        """
RPCコールを実行
        """
        if params is None:
            params = []
        
        # トークンを追加
        if self.token:
            params.insert(0, f"token:{self.token}")
        
        payload = {
            "jsonrpc": "2.0",
            "id": "ytdlp_gui",
            "method": method,
            "params": params
        }
        
        try:
            response = requests.post(self.rpc_url, json=payload, timeout=5)
            result = response.json()
            return result.get("result")
        except Exception as e:
            print(f"RPCコールエラー: {e}")
            return None
    
    def add_download(self, url: str, output_dir: str, filename: str, 
                     options: Optional[Dict] = None) -> Optional[str]:
        """
ダウンロードを追加
        """
        if self.mode == "rpc":
            return self._add_download_rpc(url, output_dir, filename, options)
        else:
            return self._add_download_cli(url, output_dir, filename, options)
    
    def _add_download_rpc(self, url: str, output_dir: str, filename: str,
                          options: Optional[Dict] = None) -> Optional[str]:
        """
RPCモードでダウンロードを追加
        """
        aria2_options = {
            "dir": output_dir,
            "out": filename,
            "max-connection-per-server": str(self.max_connection),
            "split": str(self.split),
            "continue": "true",
            "max-tries": "5",
            "retry-wait": "3"
        }
        
        if options:
            aria2_options.update(options)
        
        gid = self._rpc_call("aria2.addUri", [[url], aria2_options])
        return gid
    
    def _add_download_cli(self, url: str, output_dir: str, filename: str,
                          options: Optional[Dict] = None) -> Optional[str]:
        """
CLIモードでダウンロードを追加
        """
        cmd = [
            "aria2c",
            "-x", str(self.max_connection),
            "-s", str(self.split),
            "-d", output_dir,
            "-o", filename,
            "--continue=true",
            "--max-tries=5",
            "--retry-wait=3",
            url
        ]
        
        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            return str(process.pid)
        except Exception as e:
            print(f"CLIダウンロードエラー: {e}")
            return None
    
    def get_status(self, gid: str) -> Optional[Dict]:
        """
ダウンロードステータスを取得
        """
        if self.mode == "rpc":
            return self._rpc_call("aria2.tellStatus", [gid])
        else:
            # CLIモードではステータス取得が困難
            return None
    
    def pause(self, gid: str) -> bool:
        """
ダウンロードを一時停止
        """
        if self.mode == "rpc":
            result = self._rpc_call("aria2.pause", [gid])
            return result == gid
        return False
    
    def unpause(self, gid: str) -> bool:
        """
ダウンロードを再開
        """
        if self.mode == "rpc":
            result = self._rpc_call("aria2.unpause", [gid])
            return result == gid
        return False
    
    def remove(self, gid: str) -> bool:
        """
ダウンロードを中止
        """
        if self.mode == "rpc":
            result = self._rpc_call("aria2.remove", [gid])
            return result == gid
        return False
