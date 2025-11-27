#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Plugin manager
"""

import os
import sys
import importlib.util
from pathlib import Path


class PluginManager:
    """Manages plugins"""
    
    def __init__(self, app):
        self.app = app
        self.plugins = []
        self.hooks = {
            'on_download_start': [],
            'on_progress': [],
            'on_complete': [],
            'on_error': [],
        }
        self.plugins_dir = Path('plugins')
        self.plugins_dir.mkdir(exist_ok=True)
    
    def load_plugins(self):
        """Load all plugins from plugins directory"""
        if not self.plugins_dir.exists():
            return
        
        for file_path in self.plugins_dir.glob('*.py'):
            if file_path.name.startswith('_'):
                continue
            
            try:
                self.load_plugin(file_path)
            except Exception as e:
                self.app.log(f"Failed to load plugin {file_path.name}: {e}")
    
    def load_plugin(self, file_path):
        """Load a single plugin"""
        module_name = f"plugin_{file_path.stem}"
        
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        
        # Call register function
        if hasattr(module, 'register'):
            module.register(self.app)
            self.plugins.append(module)
            self.app.log(f"Loaded plugin: {file_path.name}")
            
            # Add menu actions if provided
            if hasattr(module, 'get_menu_actions'):
                actions = module.get_menu_actions()
                for action in actions:
                    self.app.add_plugin_menu_action(action)
        else:
            raise Exception("Plugin must have a register() function")
    
    def register_hook(self, name, callback):
        """Register a hook callback"""
        if name in self.hooks:
            self.hooks[name].append(callback)
    
    def trigger_hook(self, name, *args, **kwargs):
        """Trigger all callbacks for a hook"""
        if name in self.hooks:
            for callback in self.hooks[name]:
                try:
                    callback(*args, **kwargs)
                except Exception as e:
                    self.app.log(f"Plugin hook error ({name}): {e}")
