#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Download Manager
"""

import os
import subprocess
import threading
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QProgressBar
)
from PyQt5.QtCore import QObject, pyqtSignal, QThread, QTimer
from .aria2_manager import Aria2Manager


class DownloadTask(QObject):
    """Single download task"""
    
    progress_updated = pyqtSignal(int, str)  # progress, status
    completed = pyqtSignal(bool, str)  # success, message
    
    def __init__(self, url, output_dir, config, aria2_manager, api):
        super().__init__()
        self.url = url
        self.output_dir = output_dir
        self.config = config
        self.aria2_manager = aria2_manager
        self.api = api
        self.is_running = False
        self.gid = None
    
    def start(self):
        """Start download"""
        self.is_running = True
        
        # Emit hook
        self.api.call_hook('on_download_start', {
            'url': self.url,
            'output_dir': self.output_dir
        })
        
        # Start in thread
        thread = threading.Thread(target=self._download)
        thread.daemon = True
        thread.start()
    
    def _download(self):
        """Download process"""
        try:
            # Get video info
            self.progress_updated.emit(0, '情報取得中...')
            info = self._get_video_info()
            
            if not info:
                self.completed.emit(False, '動画情報の取得に失敗しました')
                return
            
            # Download with aria2
            self.progress_updated.emit(10, 'ダウンロード中...')
            
            # Get direct URL from yt-dlp
            direct_url = self._get_direct_url()
            
            if not direct_url:
                self.completed.emit(False, 'ダウンロードURLの取得に失敗しました')
                return
            
            # Download with aria2
            filename = info.get('title', 'video') + '.%(ext)s'
            result = self.aria2_manager.download(
                direct_url,
                self.output_dir,
                filename,
                self._progress_callback
            )
            
            if result['success']:
                self.progress_updated.emit(100, '完了')
                self.completed.emit(True, 'ダウンロード完了')
                
                # Emit hook
                self.api.call_hook('on_complete', {
                    'url': self.url,
                    'output_dir': self.output_dir,
                    'filename': filename
                })
            else:
                error_msg = result.get('error', '不明なエラー')
                self.completed.emit(False, f'ダウンロード失敗: {error_msg}')
                
                # Emit hook
                self.api.call_hook('on_error', {
                    'url': self.url,
                    'error': error_msg
                })
        
        except Exception as e:
            self.completed.emit(False, f'エラー: {str(e)}')
            self.api.call_hook('on_error', {
                'url': self.url,
                'error': str(e)
            })
        
        finally:
            self.is_running = False
    
    def _get_video_info(self):
        """Get video information"""
        try:
            cmd = [
                'yt-dlp',
                '--dump-json',
                '--no-playlist',
                self.url
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                import json
                return json.loads(result.stdout)
            
            return None
        
        except Exception as e:
            self.api.log(f'情報取得エラー: {e}')
            return None
    
    def _get_direct_url(self):
        """Get direct download URL"""
        try:
            cmd = [
                'yt-dlp',
                '-g',
                '--no-playlist',
                self.url
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                return result.stdout.strip().split('\n')[0]
            
            return None
        
        except Exception as e:
            self.api.log(f'URL取得エラー: {e}')
            return None
    
    def _progress_callback(self, progress):
        """Progress callback"""
        self.progress_updated.emit(progress, 'ダウンロード中...')
        
        # Emit hook (throttled)
        self.api.call_hook('on_progress', {
            'url': self.url,
            'progress': progress
        })


class DownloadWidget(QWidget):
    """Widget for single download task"""
    
    remove_requested = pyqtSignal()
    
    def __init__(self, task):
        super().__init__()
        self.task = task
        self.init_ui()
        
        # Connect signals
        self.task.progress_updated.connect(self.update_progress)
        self.task.completed.connect(self.on_completed)
    
    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Title and remove button
        title_layout = QHBoxLayout()
        
        self.title_label = QLabel(self.task.url[:80] + '...' if len(self.task.url) > 80 else self.task.url)
        title_layout.addWidget(self.title_label)
        
        title_layout.addStretch()
        
        self.remove_btn = QPushButton('削除')
        self.remove_btn.setMaximumWidth(60)
        self.remove_btn.clicked.connect(self.remove_requested.emit)
        title_layout.addWidget(self.remove_btn)
        
        layout.addLayout(title_layout)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)
        
        # Status label
        self.status_label = QLabel('準備中...')
        layout.addWidget(self.status_label)
        
        # Styling
        self.setStyleSheet("""
            DownloadWidget {
                background-color: #f0f0f0;
                border-radius: 5px;
                margin-bottom: 5px;
            }
        """)
    
    def update_progress(self, progress, status):
        """Update progress"""
        self.progress_bar.setValue(progress)
        self.status_label.setText(status)
    
    def on_completed(self, success, message):
        """Handle completion"""
        self.status_label.setText(message)
        
        if success:
            self.progress_bar.setStyleSheet("""
                QProgressBar::chunk {
                    background-color: #4CAF50;
                }
            """)


class DownloadManager:
    """Manages download tasks"""
    
    def __init__(self, config, api):
        self.config = config
        self.api = api
        self.aria2_manager = Aria2Manager(config)
        self.tasks = []
    
    def add_download(self, url, output_dir, downloads_layout):
        """Add download task"""
        # Create task
        task = DownloadTask(url, output_dir, self.config, self.aria2_manager, self.api)
        
        # Create widget
        widget = DownloadWidget(task)
        widget.remove_requested.connect(lambda: self.remove_download(task, widget, downloads_layout))
        
        # Add to layout
        downloads_layout.addWidget(widget)
        
        # Store task
        self.tasks.append({'task': task, 'widget': widget})
        
        # Start download
        task.start()
    
    def remove_download(self, task, widget, downloads_layout):
        """Remove download task"""
        # Remove widget
        downloads_layout.removeWidget(widget)
        widget.deleteLater()
        
        # Remove from tasks
        self.tasks = [t for t in self.tasks if t['task'] != task]
    
    def clear_completed(self):
        """Clear completed tasks"""
        self.tasks = [t for t in self.tasks if t['task'].is_running]
        
        # Remove widgets
        for t in self.tasks:
            if not t['task'].is_running:
                t['widget'].deleteLater()
    
    def clear_all(self):
        """Clear all tasks"""
        for t in self.tasks:
            t['widget'].deleteLater()
        
        self.tasks.clear()
