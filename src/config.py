#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuration manager
"""

import json
import os
from typing import Any, Optional


class ConfigManager:
    """Manages application configuration"""
    
    DEFAULT_CONFIG = {
        "output_dir": os.path.expanduser("~/Downloads"),
        "ffmpeg_path": "ffmpeg",
        "aria2c_path": "aria2c",
        "aria2c_rpc_url": "http://localhost:6800/jsonrpc",
        "aria2c_rpc_secret": "",
        "aria2c_use_rpc": True,
        "aria2c_max_connections": 16,
        "aria2c_split": 16,
        "auto_check_updates": True,
        "auto_update": False,
        "update_manifest_url": "https://raw.githubusercontent.com/yunfie-twitter/ytdlp-gui/main/manifest.json",
        "theme": "system",
        "download_format": "best",
        "extract_audio": False,
        "audio_format": "mp3",
        "embed_thumbnail": True,
        "embed_metadata": True,
    }
    
    def __init__(self, config_path="config.json"):
        self.config_path = config_path
        self.data = {}
        self.load()
    
    def load(self):
        """Load configuration from file"""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self.data = json.load(f)
                # Merge with defaults for new keys
                for key, value in self.DEFAULT_CONFIG.items():
                    if key not in self.data:
                        self.data[key] = value
                self.save()  # Save merged config
            except Exception as e:
                print(f"Failed to load config: {e}")
                self.data = self.DEFAULT_CONFIG.copy()
                self.save()
        else:
            self.data = self.DEFAULT_CONFIG.copy()
            self.save()
    
    def save(self):
        """Save configuration to file"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Failed to save config: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        return self.data.get(key, default)
    
    def set(self, key: str, value: Any):
        """Set configuration value"""
        self.data[key] = value
        self.save()
    
    def get_all(self) -> dict:
        """Get all configuration"""
        return self.data.copy()
