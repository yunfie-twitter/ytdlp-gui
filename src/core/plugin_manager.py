# -*- coding: utf-8 -*-
"""
プラグイン管理モジュール
"""

import importlib
import importlib.util
import sys
from pathlib import Path
from typing import Dict, List, Any, Callable, Optional

class PluginAPI:
    """プラグインAPIクラス"""
    
    def __init__(self, app):
        self.app = app
        self.hooks: Dict[str, List[Callable]] = {
            'on_download_start': [],
            'on_progress': [],
            'on_complete': [],
            'on_error': []
        }
    
    def register_hook(self, name: str, callback: Callable):
        """フックを登録"""
        if name in self.hooks:
            self.hooks[name].append(callback)
            self.log(f"フック登録: {name}")
        else:
            self.log(f"未対応のフック: {name}")
    
    def log(self, message: str):
        """ログ出力"""
        if hasattr(self.app, 'log'):
            self.app.log(message)
        else:
            print(f"[Plugin] {message}")
    
    def open_file(self, path: str):
        """ファイルを開く"""
        import platform
        import subprocess
        
        if platform.system() == 'Windows':
            os.startfile(path)
        elif platform.system() == 'Darwin':  # macOS
            subprocess.run(['open', path])
        else:  # Linux
            subprocess.run(['xdg-open', path])
    
    def get_config(self) -> Dict[str, Any]:
        """設定を取得"""
        if hasattr(self.app, 'config_manager'):
            return self.app.config_manager.get_all()
        return {}
    
    def set_config(self, key: str, value: Any):
        """設定を変更"""
        if hasattr(self.app, 'config_manager'):
            self.app.config_manager.set(key, value)

class PluginManager:
    """プラグインマネージャークラス"""
    
    def __init__(self, app, plugin_dir: str = "plugins"):
        self.app = app
        self.plugin_dir = Path(plugin_dir)
        self.plugins: Dict[str, Any] = {}
        self.api = PluginAPI(app)
        
        # プラグインディレクトリを作成
        self.plugin_dir.mkdir(exist_ok=True)
        
        # __init__.pyを作成
        init_file = self.plugin_dir / "__init__.py"
        if not init_file.exists():
            init_file.write_text("# -*- coding: utf-8 -*-\n# Plugins directory\n")
    
    def load_plugins(self):
        """プラグインを読み込む"""
        if not self.plugin_dir.exists():
            return
        
        # .pyファイルを検索
        for plugin_file in self.plugin_dir.glob("*.py"):
            if plugin_file.name.startswith("__"):
                continue
            
            plugin_name = plugin_file.stem
            try:
                # プラグインをインポート
                spec = importlib.util.spec_from_file_location(plugin_name, plugin_file)
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    sys.modules[plugin_name] = module
                    spec.loader.exec_module(module)
                    
                    # register関数を呼び出す
                    if hasattr(module, 'register'):
                        module.register(self.api)
                        self.plugins[plugin_name] = module
                        self.api.log(f"プラグイン読み込み: {plugin_name}")
                    else:
                        self.api.log(f"プラグインにregister関数がありません: {plugin_name}")
                        
            except Exception as e:
                self.api.log(f"プラグイン読み込みエラー ({plugin_name}): {e}")
    
    def get_plugin_menu_actions(self) -> List[Dict[str, Any]]:
        """プラグインのメニューアクションを取得"""
        actions = []
        for plugin_name, plugin_module in self.plugins.items():
            if hasattr(plugin_module, 'get_menu_actions'):
                try:
                    plugin_actions = plugin_module.get_menu_actions()
                    if isinstance(plugin_actions, list):
                        actions.extend(plugin_actions)
                except Exception as e:
                    self.api.log(f"プラグインメニューエラー ({plugin_name}): {e}")
        return actions
    
    def get_hooks(self) -> Dict[str, List[Callable]]:
        """登録されたフックを取得"""
        return self.api.hooks
