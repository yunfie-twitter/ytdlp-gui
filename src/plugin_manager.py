#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Plugin Manager
"""

import os
import sys
import importlib
import importlib.util
from pathlib import Path


class PluginManager:
    """Manages plugins"""
    
    def __init__(self, api):
        self.api = api
        self.plugins_dir = Path('plugins')
        self.plugins = []
        
        # Create plugins directory if not exists
        self.plugins_dir.mkdir(exist_ok=True)
        
        # Create example plugin
        self._create_example_plugin()
    
    def _create_example_plugin(self):
        """Create example plugin"""
        example_file = self.plugins_dir / 'example_plugin.py.disabled'
        
        if not example_file.exists():
            example_code = '''
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Example Plugin
このファイルの拡張子を .py に変更すると有効化されます
"""

def register(app):
    """
    プラグイン登録関数
    
    Args:
        app: AppAPI instance
    """
    app.log('例示プラグインが読み込まれました')
    
    # フックの登録
    app.register_hook('on_download_start', on_download_start)
    app.register_hook('on_complete', on_complete)
    app.register_hook('on_error', on_error)
    
    # メニューアクションの追加
    app.add_menu_action('Tools', '例示アクション', example_action)

def on_download_start(info):
    """ダウンロード開始時"""
    print(f'プラグイン: ダウンロード開始 - {info["url"]}')

def on_complete(info):
    """ダウンロード完了時"""
    print(f'プラグイン: ダウンロード完了 - {info.get("filename", "Unknown")}')

def on_error(info):
    """エラー発生時"""
    print(f'プラグイン: エラー - {info.get("error", "Unknown")}')

def example_action():
    """例示アクション"""
    print('例示アクションが実行されました')
'''
            try:
                with open(example_file, 'w', encoding='utf-8') as f:
                    f.write(example_code)
            except Exception as e:
                print(f'Failed to create example plugin: {e}')
    
    def load_plugins(self):
        """Load all plugins"""
        self.plugins.clear()
        
        if not self.plugins_dir.exists():
            return
        
        # Get all .py files in plugins directory
        plugin_files = list(self.plugins_dir.glob('*.py'))
        
        for plugin_file in plugin_files:
            self._load_plugin(plugin_file)
    
    def _load_plugin(self, plugin_file: Path):
        """Load single plugin"""
        try:
            # Load module
            spec = importlib.util.spec_from_file_location(
                plugin_file.stem,
                plugin_file
            )
            
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # Check if register function exists
                if hasattr(module, 'register'):
                    # Call register function
                    module.register(self.api)
                    
                    self.plugins.append({
                        'name': plugin_file.stem,
                        'module': module,
                        'path': plugin_file
                    })
                    
                    self.api.log(f'プラグイン読み込み: {plugin_file.stem}')
                else:
                    self.api.log(f'プラグインエラー: register関数が見つかりません - {plugin_file.stem}')
        
        except Exception as e:
            self.api.log(f'プラグイン読み込みエラー: {plugin_file.stem} - {e}')
    
    def reload_plugins(self):
        """Reload all plugins"""
        self.load_plugins()
    
    def get_plugin_info(self) -> list:
        """Get loaded plugin information"""
        return [
            {
                'name': p['name'],
                'path': str(p['path'])
            }
            for p in self.plugins
        ]
