#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main Application Window
"""

import os
import sys
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLineEdit, QTextEdit, QLabel,
    QFileDialog, QMessageBox, QMenuBar, QMenu, QAction,
    QDialog, QFormLayout, QSpinBox, QCheckBox, QComboBox,
    QProgressBar, QScrollArea, QGroupBox, QListWidget,
    QSplitter
)
from PyQt5.QtCore import Qt, pyqtSignal, QObject
from PyQt5.QtGui import QIcon

from .config import ConfigManager
from .plugin_manager import PluginManager
from .updater import Updater
from .download_manager import DownloadManager
from .settings_dialog import SettingsDialog


class AppAPI(QObject):
    """Public API for plugins"""
    
    log_signal = pyqtSignal(str)
    
    def __init__(self, app):
        super().__init__()
        self._app = app
        self._hooks = {
            'on_download_start': [],
            'on_progress': [],
            'on_complete': [],
            'on_error': []
        }
    
    def register_hook(self, name: str, callback):
        """Register a hook callback"""
        if name in self._hooks:
            self._hooks[name].append(callback)
    
    def call_hook(self, name: str, info: dict):
        """Call all registered hooks"""
        if name in self._hooks:
            for callback in self._hooks[name]:
                try:
                    callback(info)
                except Exception as e:
                    self.log(f"Plugin hook error: {e}")
    
    def log(self, message: str):
        """Log message to UI"""
        self.log_signal.emit(message)
    
    def open_file(self, path: str):
        """Open file with system default application"""
        import subprocess
        import platform
        
        try:
            if platform.system() == 'Windows':
                os.startfile(path)
            elif platform.system() == 'Darwin':
                subprocess.run(['open', path])
            else:
                subprocess.run(['xdg-open', path])
        except Exception as e:
            self.log(f"Failed to open file: {e}")
    
    def get_config(self) -> dict:
        """Get all configuration"""
        return self._app.config.get_all()
    
    def set_config(self, key: str, value):
        """Set configuration value"""
        self._app.config.set(key, value)
    
    def add_menu_action(self, menu_name: str, action_name: str, callback):
        """Add action to menu"""
        self._app.add_plugin_menu_action(menu_name, action_name, callback)


class YtDlpGUI(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        
        # Initialize managers
        self.config = ConfigManager()
        self.api = AppAPI(self)
        self.plugin_manager = PluginManager(self.api)
        self.updater = Updater(self.config)
        self.download_manager = DownloadManager(self.config, self.api)
        
        # Setup UI
        self.init_ui()
        
        # Connect signals
        self.api.log_signal.connect(self.log_message)
        
        # Load plugins
        self.plugin_manager.load_plugins()
        
        # Check for updates
        if self.config.get('auto_check_updates'):
            self.check_updates(silent=True)
    
    def init_ui(self):
        """Initialize user interface"""
        self.setWindowTitle('yt-dlp GUI')
        self.setMinimumSize(900, 600)
        
        # Create menu bar
        self.create_menu_bar()
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        
        # URL input section
        url_layout = QHBoxLayout()
        url_layout.addWidget(QLabel('URL:'))
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText('動画URLを入力してください...')
        url_layout.addWidget(self.url_input)
        
        self.download_btn = QPushButton('ダウンロード')
        self.download_btn.clicked.connect(self.start_download)
        url_layout.addWidget(self.download_btn)
        
        main_layout.addLayout(url_layout)
        
        # Output directory
        dir_layout = QHBoxLayout()
        dir_layout.addWidget(QLabel('保存先:'))
        self.output_dir = QLineEdit(self.config.get('output_dir'))
        self.output_dir.setReadOnly(True)
        dir_layout.addWidget(self.output_dir)
        
        browse_btn = QPushButton('参照')
        browse_btn.clicked.connect(self.browse_output_dir)
        dir_layout.addWidget(browse_btn)
        
        main_layout.addLayout(dir_layout)
        
        # Splitter for downloads and log
        splitter = QSplitter(Qt.Vertical)
        
        # Downloads section
        downloads_group = QGroupBox('ダウンロード')
        downloads_layout = QVBoxLayout()
        
        # Downloads scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setMinimumHeight(200)
        
        self.downloads_widget = QWidget()
        self.downloads_layout = QVBoxLayout(self.downloads_widget)
        self.downloads_layout.setAlignment(Qt.AlignTop)
        scroll.setWidget(self.downloads_widget)
        
        downloads_layout.addWidget(scroll)
        downloads_group.setLayout(downloads_layout)
        
        splitter.addWidget(downloads_group)
        
        # Log section
        log_group = QGroupBox('ログ')
        log_layout = QVBoxLayout()
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(150)
        log_layout.addWidget(self.log_text)
        
        log_group.setLayout(log_layout)
        splitter.addWidget(log_group)
        
        main_layout.addWidget(splitter)
        
        # Status bar
        self.statusBar().showMessage('準備完了')
        
        self.log_message('アプリケーション起動完了')
    
    def create_menu_bar(self):
        """Create menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('ファイル(&F)')
        
        settings_action = QAction('設定(&S)', self)
        settings_action.setShortcut('Ctrl+,')
        settings_action.triggered.connect(self.open_settings)
        file_menu.addAction(settings_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction('終了(&X)', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Downloads menu
        downloads_menu = menubar.addMenu('ダウンロード(&D)')
        
        clear_completed_action = QAction('完了したタスクをクリア(&C)', self)
        clear_completed_action.triggered.connect(self.clear_completed_downloads)
        downloads_menu.addAction(clear_completed_action)
        
        clear_all_action = QAction('すべてクリア(&A)', self)
        clear_all_action.triggered.connect(self.clear_all_downloads)
        downloads_menu.addAction(clear_all_action)
        
        downloads_menu.addSeparator()
        
        open_folder_action = QAction('保存フォルダを開く(&O)', self)
        open_folder_action.triggered.connect(self.open_output_folder)
        downloads_menu.addAction(open_folder_action)
        
        # Tools menu
        self.tools_menu = menubar.addMenu('ツール(&T)')
        
        check_aria2_action = QAction('aria2c接続確認(&A)', self)
        check_aria2_action.triggered.connect(self.check_aria2)
        self.tools_menu.addAction(check_aria2_action)
        
        check_ffmpeg_action = QAction('ffmpeg確認(&F)', self)
        check_ffmpeg_action.triggered.connect(self.check_ffmpeg)
        self.tools_menu.addAction(check_ffmpeg_action)
        
        self.tools_menu.addSeparator()
        
        reload_plugins_action = QAction('プラグイン再読み込み(&P)', self)
        reload_plugins_action.triggered.connect(self.reload_plugins)
        self.tools_menu.addAction(reload_plugins_action)
        
        # Help menu
        help_menu = menubar.addMenu('ヘルプ(&H)')
        
        check_updates_action = QAction('更新を確認(&U)', self)
        check_updates_action.triggered.connect(lambda: self.check_updates(silent=False))
        help_menu.addAction(check_updates_action)
        
        help_menu.addSeparator()
        
        about_action = QAction('このアプリについて(&A)', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def add_plugin_menu_action(self, menu_name: str, action_name: str, callback):
        """Add plugin menu action"""
        action = QAction(action_name, self)
        action.triggered.connect(callback)
        self.tools_menu.addAction(action)
    
    def start_download(self):
        """Start download"""
        url = self.url_input.text().strip()
        
        if not url:
            QMessageBox.warning(self, 'エラー', 'URLを入力してください')
            return
        
        output_dir = self.output_dir.text()
        
        # Add download task
        self.download_manager.add_download(url, output_dir, self.downloads_layout)
        
        # Clear URL input
        self.url_input.clear()
        
        self.log_message(f'ダウンロード開始: {url}')
    
    def browse_output_dir(self):
        """Browse for output directory"""
        directory = QFileDialog.getExistingDirectory(
            self,
            '保存先フォルダを選択',
            self.output_dir.text()
        )
        
        if directory:
            self.output_dir.setText(directory)
            self.config.set('output_dir', directory)
            self.log_message(f'保存先変更: {directory}')
    
    def open_settings(self):
        """Open settings dialog"""
        dialog = SettingsDialog(self.config, self)
        if dialog.exec_() == QDialog.Accepted:
            # Reload output dir
            self.output_dir.setText(self.config.get('output_dir'))
            self.log_message('設定を保存しました')
    
    def clear_completed_downloads(self):
        """Clear completed download tasks"""
        self.download_manager.clear_completed()
        self.log_message('完了したタスクをクリアしました')
    
    def clear_all_downloads(self):
        """Clear all download tasks"""
        reply = QMessageBox.question(
            self,
            '確認',
            'すべてのダウンロードタスクをクリアしますか？',
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.download_manager.clear_all()
            self.log_message('すべてのタスクをクリアしました')
    
    def open_output_folder(self):
        """Open output folder"""
        self.api.open_file(self.output_dir.text())
    
    def check_aria2(self):
        """Check aria2c connection"""
        result = self.download_manager.aria2_manager.check_connection()
        
        if result['success']:
            QMessageBox.information(
                self,
                'aria2c接続確認',
                f"接続成功\n\nモード: {result['mode']}\nバージョン: {result.get('version', 'N/A')}"
            )
        else:
            QMessageBox.warning(
                self,
                'aria2c接続確認',
                f"接続失敗\n\nエラー: {result.get('error', '不明')}"
            )
    
    def check_ffmpeg(self):
        """Check ffmpeg availability"""
        import subprocess
        
        ffmpeg_path = self.config.get('ffmpeg_path')
        
        try:
            result = subprocess.run(
                [ffmpeg_path, '-version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                version = result.stdout.split('\n')[0]
                QMessageBox.information(self, 'ffmpeg確認', f'ffmpeg利用可能\n\n{version}')
            else:
                QMessageBox.warning(self, 'ffmpeg確認', 'ffmpegの実行に失敗しました')
        except Exception as e:
            QMessageBox.warning(self, 'ffmpeg確認', f'ffmpegが見つかりません\n\nエラー: {e}')
    
    def reload_plugins(self):
        """Reload all plugins"""
        self.plugin_manager.reload_plugins()
        self.log_message('プラグインを再読み込みしました')
        QMessageBox.information(self, 'プラグイン', 'プラグインを再読み込みしました')
    
    def check_updates(self, silent=False):
        """Check for updates"""
        self.log_message('更新を確認中...')
        
        try:
            update_info = self.updater.check_update()
            
            if update_info['update_available']:
                message = (
                    f"新しいバージョンが利用可能です\n\n"
                    f"現在のバージョン: {update_info['current_version']}\n"
                    f"最新バージョン: {update_info['latest_version']}\n\n"
                    f"更新しますか？"
                )
                
                reply = QMessageBox.question(
                    self,
                    '更新通知',
                    message,
                    QMessageBox.Yes | QMessageBox.No
                )
                
                if reply == QMessageBox.Yes:
                    self.log_message('更新をダウンロード中...')
                    if self.updater.download_update():
                        QMessageBox.information(
                            self,
                            '更新完了',
                            'アプリケーションを再起動してください'
                        )
                    else:
                        QMessageBox.warning(
                            self,
                            '更新失敗',
                            '更新のダウンロードに失敗しました'
                        )
            else:
                if not silent:
                    QMessageBox.information(
                        self,
                        '更新確認',
                        '最新バージョンを使用しています'
                    )
        except Exception as e:
            if not silent:
                QMessageBox.warning(
                    self,
                    '更新確認失敗',
                    f'更新の確認に失敗しました\n\nエラー: {e}'
                )
            self.log_message(f'更新確認エラー: {e}')
    
    def show_about(self):
        """Show about dialog"""
        about_text = (
            '<h2>yt-dlp GUI</h2>'
            '<p>バージョン: 1.0.0</p>'
            '<p>PyQt5ベースのyt-dlpグラフィカルインターフェース</p>'
            '<p>機能:</p>'
            '<ul>'
            '<li>aria2c統合（RPC/CLIモード）</li>'
            '<li>プラグインシステム</li>'
            '<li>自動更新機能</li>'
            '<li>進捗バー表示</li>'
            '</ul>'
            '<p>開発: yunfie</p>'
        )
        
        QMessageBox.about(self, 'このアプリについて', about_text)
    
    def log_message(self, message: str):
        """Log message to text area"""
        self.log_text.append(f'[{self.get_timestamp()}] {message}')
        # Auto-scroll to bottom
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    @staticmethod
    def get_timestamp():
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().strftime('%H:%M:%S')
