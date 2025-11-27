#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Update manager
"""

import requests
import json
from typing import Optional, Callable
from PyQt5.QtWidgets import QMessageBox, QPushButton
from PyQt5.QtCore import QThread, pyqtSignal
import webbrowser


class UpdateCheckThread(QThread):
    """Thread for checking updates"""
    
    result = pyqtSignal(bool, object)  # available, info
    
    def __init__(self, manifest_url, current_version="1.0.0"):
        super().__init__()
        self.manifest_url = manifest_url
        self.current_version = current_version
    
    def run(self):
        """Check for updates"""
        try:
            response = requests.get(self.manifest_url, timeout=10)
            response.raise_for_status()
            manifest = response.json()
            
            latest_version = manifest.get('version', '0.0.0')
            
            # Simple version comparison
            if self.compare_versions(latest_version, self.current_version) > 0:
                self.result.emit(True, manifest)
            else:
                self.result.emit(False, None)
        
        except Exception as e:
            print(f"Update check failed: {e}")
            self.result.emit(False, None)
    
    def compare_versions(self, v1, v2):
        """Compare version strings"""
        v1_parts = [int(x) for x in v1.split('.')]
        v2_parts = [int(x) for x in v2.split('.')]
        
        for i in range(max(len(v1_parts), len(v2_parts))):
            p1 = v1_parts[i] if i < len(v1_parts) else 0
            p2 = v2_parts[i] if i < len(v2_parts) else 0
            
            if p1 > p2:
                return 1
            elif p1 < p2:
                return -1
        
        return 0


class UpdateManager:
    """Manages application updates"""
    
    def __init__(self, config):
        self.config = config
        self.current_version = "1.0.0"
    
    def check_updates(self, callback: Optional[Callable] = None):
        """Check for updates asynchronously"""
        manifest_url = self.config.get(
            'update_manifest_url',
            'https://raw.githubusercontent.com/yunfie-twitter/ytdlp-gui/main/manifest.json'
        )
        
        thread = UpdateCheckThread(manifest_url, self.current_version)
        
        if callback:
            thread.result.connect(lambda available, info: callback(available, info))
        
        thread.start()
    
    def show_update_dialog(self, info, parent=None):
        """Show update available dialog"""
        version = info.get('version', 'unknown')
        changelog = info.get('changelog', 'No changelog available')
        download_url = info.get('download_url', '')
        
        msg = QMessageBox(parent)
        msg.setWindowTitle("Update Available")
        msg.setIcon(QMessageBox.Information)
        msg.setText(f"A new version ({version}) is available!")
        msg.setDetailedText(changelog)
        
        if download_url:
            download_btn = msg.addButton("Download", QMessageBox.AcceptRole)
            msg.addButton("Later", QMessageBox.RejectRole)
            
            msg.exec_()
            
            if msg.clickedButton() == download_btn:
                webbrowser.open(download_url)
        else:
            msg.addButton(QMessageBox.Ok)
            msg.exec_()
