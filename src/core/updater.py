# -*- coding: utf-8 -*-
"""
アップデート管理モジュール
"""

import requests
from typing import Optional, Dict, Any
from packaging import version

class UpdateManager:
    """アップデートマネージャークラス"""
    
    def __init__(self, current_version: str, update_url: str):
        self.current_version = current_version
        self.update_url = update_url
    
    def check_update(self) -> Optional[Dict[str, Any]]:
        """アップデートを確認"""
        try:
            response = requests.get(self.update_url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                latest_version = data.get('tag_name', '').lstrip('v')
                
                if self._is_newer_version(latest_version):
                    return {
                        'available': True,
                        'version': latest_version,
                        'url': data.get('html_url', ''),
                        'body': data.get('body', ''),
                        'assets': data.get('assets', [])
                    }
            return {'available': False}
        except Exception as e:
            print(f"アップデート確認エラー: {e}")
            return None
    
    def _is_newer_version(self, latest: str) -> bool:
        """バージョン比較"""
        try:
            return version.parse(latest) > version.parse(self.current_version)
        except:
            return False
