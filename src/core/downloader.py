# -*- coding: utf-8 -*-
"""
ダウンローダーモジュール
"""

import os
import time
from pathlib import Path
from typing import Dict, Any, Optional, Callable
from PyQt5.QtCore import QObject, QRunnable, pyqtSignal, pyqtSlot
import yt_dlp
from .aria2c import Aria2cManager

class DownloadSignals(QObject):
    """ダウンロードシグナル"""
    progress = pyqtSignal(dict)  # 進捗情報
    completed = pyqtSignal(dict)  # 完了情報
    error = pyqtSignal(str)  # エラーメッセージ
    started = pyqtSignal(dict)  # 開始情報

class DownloadTask(QRunnable):
    """ダウンロードタスク"""
    
    def __init__(self, url: str, config: Dict[str, Any], 
                 aria2c_manager: Optional[Aria2cManager] = None,
                 hooks: Optional[Dict[str, list]] = None):
        super().__init__()
        self.url = url
        self.config = config
        self.aria2c_manager = aria2c_manager
        self.signals = DownloadSignals()
        self.hooks = hooks or {}
        self.is_cancelled = False
    
    def _call_hook(self, hook_name: str, info: Dict[str, Any]):
        """フックを呼び出す"""
        if hook_name in self.hooks:
            for callback in self.hooks[hook_name]:
                try:
                    callback(info)
                except Exception as e:
                    print(f"フックエラー ({hook_name}): {e}")
    
    @pyqtSlot()
    def run(self):
        """ダウンロード実行"""
        try:
            # ダウンロードパス
            download_path = Path(self.config.get("download_path", "./downloads"))
            download_path.mkdir(parents=True, exist_ok=True)
            
            # yt-dlpオプション
            ydl_opts = {
                'outtmpl': str(download_path / '%(title)s.%(ext)s'),
                'progress_hooks': [self._progress_hook],
                'quiet': True,
                'no_warnings': True,
            }
            
            # ffmpegパスを設定
            ffmpeg_path = self.config.get("ffmpeg_path", "")
            if ffmpeg_path and os.path.exists(ffmpeg_path):
                ydl_opts['ffmpeg_location'] = ffmpeg_path
            
            # aria2cを使用する場合
            if self.config.get("aria2c_enabled", False) and self.aria2c_manager:
                if self.aria2c_manager.is_available():
                    ydl_opts['external_downloader'] = 'aria2c'
                    ydl_opts['external_downloader_args'] = [
                        f'-x {self.aria2c_manager.max_connection}',
                        f'-s {self.aria2c_manager.split}',
                        '--continue=true'
                    ]
            
            # ダウンロード開始
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # 情報取得
                info = ydl.extract_info(self.url, download=False)
                
                start_info = {
                    'url': self.url,
                    'title': info.get('title', 'Unknown'),
                    'duration': info.get('duration', 0),
                    'uploader': info.get('uploader', 'Unknown')
                }
                self.signals.started.emit(start_info)
                self._call_hook('on_download_start', start_info)
                
                # ダウンロード実行
                if not self.is_cancelled:
                    ydl.download([self.url])
                    
                    # 完了情報
                    complete_info = {
                        'url': self.url,
                        'title': info.get('title', 'Unknown'),
                        'filename': ydl.prepare_filename(info),
                        'filesize': info.get('filesize', 0)
                    }
                    self.signals.completed.emit(complete_info)
                    self._call_hook('on_complete', complete_info)
                    
        except Exception as e:
            error_msg = f"ダウンロードエラー: {str(e)}"
            self.signals.error.emit(error_msg)
            self._call_hook('on_error', {'url': self.url, 'error': str(e)})
    
    def _progress_hook(self, d: Dict[str, Any]):
        """進捗フック"""
        if self.is_cancelled:
            raise Exception("ダウンロードがキャンセルされました")
        
        if d['status'] == 'downloading':
            progress_info = {
                'status': 'downloading',
                'downloaded_bytes': d.get('downloaded_bytes', 0),
                'total_bytes': d.get('total_bytes', 0) or d.get('total_bytes_estimate', 0),
                'speed': d.get('speed', 0),
                'eta': d.get('eta', 0),
                'percent': d.get('_percent_str', '0%').strip()
            }
            self.signals.progress.emit(progress_info)
            self._call_hook('on_progress', progress_info)
    
    def cancel(self):
        """ダウンロードをキャンセル"""
        self.is_cancelled = True
