#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Updater
"""

import os
import json
import requests
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Optional


class Updater:
    """Manages application updates"""
    
    VERSION = '1.0.0'
    
    def __init__(self, config):
        self.config = config
        self.manifest_url = config.get('update_manifest_url')
    
    def check_update(self) -> Dict:
        """Check for updates"""
        try:
            response = requests.get(self.manifest_url, timeout=10)
            
            if response.status_code == 200:
                manifest = response.json()
                
                latest_version = manifest.get('version', '0.0.0')
                
                # Compare versions
                update_available = self._compare_versions(
                    self.VERSION,
                    latest_version
                ) < 0
                
                return {
                    'update_available': update_available,
                    'current_version': self.VERSION,
                    'latest_version': latest_version,
                    'download_url': manifest.get('download_url', ''),
                    'changelog': manifest.get('changelog', '')
                }
            else:
                raise Exception(f'HTTP {response.status_code}')
        
        except Exception as e:
            raise Exception(f'マニフェストの取得に失敗: {e}')
    
    def download_update(self) -> bool:
        """Download and install update"""
        try:
            update_info = self.check_update()
            
            if not update_info['update_available']:
                return False
            
            download_url = update_info['download_url']
            
            if not download_url:
                return False
            
            # Download to temp directory
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir) / 'update.zip'
                
                # Download file
                response = requests.get(download_url, stream=True, timeout=30)
                
                if response.status_code == 200:
                    with open(temp_path, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)
                    
                    # Extract and replace files
                    # This is a simplified version - in production,
                    # you'd want more robust update mechanism
                    import zipfile
                    
                    with zipfile.ZipFile(temp_path, 'r') as zip_ref:
                        zip_ref.extractall(Path.cwd())
                    
                    return True
                else:
                    return False
        
        except Exception as e:
            print(f'Update download failed: {e}')
            return False
    
    @staticmethod
    def _compare_versions(v1: str, v2: str) -> int:
        """
        Compare version strings
        
        Returns:
            -1 if v1 < v2
             0 if v1 == v2
             1 if v1 > v2
        """
        def parse_version(v):
            return [int(x) for x in v.split('.')]
        
        try:
            parts1 = parse_version(v1)
            parts2 = parse_version(v2)
            
            # Pad shorter version
            max_len = max(len(parts1), len(parts2))
            parts1.extend([0] * (max_len - len(parts1)))
            parts2.extend([0] * (max_len - len(parts2)))
            
            for p1, p2 in zip(parts1, parts2):
                if p1 < p2:
                    return -1
                elif p1 > p2:
                    return 1
            
            return 0
        
        except:
            return 0
