#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Settings Dialog
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QPushButton, QCheckBox, QSpinBox,
    QComboBox, QFileDialog, QTabWidget, QWidget,
    QLabel, QGroupBox
)
from PyQt5.QtCore import Qt


class SettingsDialog(QDialog):
    """Settings dialog"""
    
    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI"""
        self.setWindowTitle('設定')
        self.setMinimumSize(500, 400)
        
        layout = QVBoxLayout(self)
        
        # Tab widget
        tabs = QTabWidget()
        
        # General tab
        general_tab = self.create_general_tab()
        tabs.addTab(general_tab, '一般')
        
        # Download tab
        download_tab = self.create_download_tab()
        tabs.addTab(download_tab, 'ダウンロード')
        
        # aria2c tab
        aria2_tab = self.create_aria2_tab()
        tabs.addTab(aria2_tab, 'aria2c')
        
        # Update tab
        update_tab = self.create_update_tab()
        tabs.addTab(update_tab, '更新')
        
        layout.addWidget(tabs)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        save_btn = QPushButton('保存')
        save_btn.clicked.connect(self.save_settings)
        button_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton('キャンセル')
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
    
    def create_general_tab(self):
        """Create general settings tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Output directory
        output_group = QGroupBox('保存先')
        output_layout = QHBoxLayout()
        
        self.output_dir_input = QLineEdit(self.config.get('output_dir'))
        self.output_dir_input.setReadOnly(True)
        output_layout.addWidget(self.output_dir_input)
        
        browse_btn = QPushButton('参照')
        browse_btn.clicked.connect(self.browse_output_dir)
        output_layout.addWidget(browse_btn)
        
        output_group.setLayout(output_layout)
        layout.addWidget(output_group)
        
        # ffmpeg path
        ffmpeg_group = QGroupBox('ffmpeg')
        ffmpeg_layout = QFormLayout()
        
        self.ffmpeg_path_input = QLineEdit(self.config.get('ffmpeg_path'))
        ffmpeg_layout.addRow('ffmpegパス:', self.ffmpeg_path_input)
        
        ffmpeg_group.setLayout(ffmpeg_layout)
        layout.addWidget(ffmpeg_group)
        
        layout.addStretch()
        
        return tab
    
    def create_download_tab(self):
        """Create download settings tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        form_layout = QFormLayout()
        
        # Download format
        self.format_input = QComboBox()
        self.format_input.addItems(['best', 'bestvideo+bestaudio', 'worst'])
        current_format = self.config.get('download_format', 'best')
        index = self.format_input.findText(current_format)
        if index >= 0:
            self.format_input.setCurrentIndex(index)
        form_layout.addRow('フォーマット:', self.format_input)
        
        # Extract audio
        self.extract_audio_check = QCheckBox()
        self.extract_audio_check.setChecked(self.config.get('extract_audio', False))
        form_layout.addRow('音声のみ抽出:', self.extract_audio_check)
        
        # Audio format
        self.audio_format_input = QComboBox()
        self.audio_format_input.addItems(['mp3', 'aac', 'flac', 'wav', 'm4a'])
        current_audio = self.config.get('audio_format', 'mp3')
        index = self.audio_format_input.findText(current_audio)
        if index >= 0:
            self.audio_format_input.setCurrentIndex(index)
        form_layout.addRow('音声フォーマット:', self.audio_format_input)
        
        # Embed thumbnail
        self.embed_thumbnail_check = QCheckBox()
        self.embed_thumbnail_check.setChecked(self.config.get('embed_thumbnail', True))
        form_layout.addRow('サムネイル埋め込み:', self.embed_thumbnail_check)
        
        # Embed metadata
        self.embed_metadata_check = QCheckBox()
        self.embed_metadata_check.setChecked(self.config.get('embed_metadata', True))
        form_layout.addRow('メタデータ埋め込み:', self.embed_metadata_check)
        
        layout.addLayout(form_layout)
        layout.addStretch()
        
        return tab
    
    def create_aria2_tab(self):
        """Create aria2c settings tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Mode
        mode_group = QGroupBox('接続モード')
        mode_layout = QFormLayout()
        
        self.use_rpc_check = QCheckBox()
        self.use_rpc_check.setChecked(self.config.get('aria2c_use_rpc', True))
        mode_layout.addRow('RPCモード使用:', self.use_rpc_check)
        
        mode_group.setLayout(mode_layout)
        layout.addWidget(mode_group)
        
        # RPC settings
        rpc_group = QGroupBox('RPC設定')
        rpc_layout = QFormLayout()
        
        self.rpc_url_input = QLineEdit(self.config.get('aria2c_rpc_url'))
        rpc_layout.addRow('RPC URL:', self.rpc_url_input)
        
        self.rpc_secret_input = QLineEdit(self.config.get('aria2c_rpc_secret'))
        self.rpc_secret_input.setEchoMode(QLineEdit.Password)
        rpc_layout.addRow('RPCシークレット:', self.rpc_secret_input)
        
        rpc_group.setLayout(rpc_layout)
        layout.addWidget(rpc_group)
        
        # CLI settings
        cli_group = QGroupBox('CLI設定')
        cli_layout = QFormLayout()
        
        self.aria2c_path_input = QLineEdit(self.config.get('aria2c_path'))
        cli_layout.addRow('aria2cパス:', self.aria2c_path_input)
        
        cli_group.setLayout(cli_layout)
        layout.addWidget(cli_group)
        
        # Download settings
        dl_group = QGroupBox('ダウンロード設定')
        dl_layout = QFormLayout()
        
        self.max_connections_input = QSpinBox()
        self.max_connections_input.setMinimum(1)
        self.max_connections_input.setMaximum(32)
        self.max_connections_input.setValue(self.config.get('aria2c_max_connections', 16))
        dl_layout.addRow('最大接続数:', self.max_connections_input)
        
        self.split_input = QSpinBox()
        self.split_input.setMinimum(1)
        self.split_input.setMaximum(32)
        self.split_input.setValue(self.config.get('aria2c_split', 16))
        dl_layout.addRow('分割数:', self.split_input)
        
        dl_group.setLayout(dl_layout)
        layout.addWidget(dl_group)
        
        layout.addStretch()
        
        return tab
    
    def create_update_tab(self):
        """Create update settings tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        form_layout = QFormLayout()
        
        # Auto check updates
        self.auto_check_check = QCheckBox()
        self.auto_check_check.setChecked(self.config.get('auto_check_updates', True))
        form_layout.addRow('起動時に更新確認:', self.auto_check_check)
        
        # Auto update
        self.auto_update_check = QCheckBox()
        self.auto_update_check.setChecked(self.config.get('auto_update', False))
        form_layout.addRow('自動更新:', self.auto_update_check)
        
        # Manifest URL
        self.manifest_url_input = QLineEdit(self.config.get('update_manifest_url'))
        form_layout.addRow('マニフェストURL:', self.manifest_url_input)
        
        layout.addLayout(form_layout)
        layout.addStretch()
        
        return tab
    
    def browse_output_dir(self):
        """Browse for output directory"""
        directory = QFileDialog.getExistingDirectory(
            self,
            '保存先フォルダを選択',
            self.output_dir_input.text()
        )
        
        if directory:
            self.output_dir_input.setText(directory)
    
    def save_settings(self):
        """Save settings"""
        # General
        self.config.set('output_dir', self.output_dir_input.text())
        self.config.set('ffmpeg_path', self.ffmpeg_path_input.text())
        
        # Download
        self.config.set('download_format', self.format_input.currentText())
        self.config.set('extract_audio', self.extract_audio_check.isChecked())
        self.config.set('audio_format', self.audio_format_input.currentText())
        self.config.set('embed_thumbnail', self.embed_thumbnail_check.isChecked())
        self.config.set('embed_metadata', self.embed_metadata_check.isChecked())
        
        # aria2c
        self.config.set('aria2c_use_rpc', self.use_rpc_check.isChecked())
        self.config.set('aria2c_rpc_url', self.rpc_url_input.text())
        self.config.set('aria2c_rpc_secret', self.rpc_secret_input.text())
        self.config.set('aria2c_path', self.aria2c_path_input.text())
        self.config.set('aria2c_max_connections', self.max_connections_input.value())
        self.config.set('aria2c_split', self.split_input.value())
        
        # Update
        self.config.set('auto_check_updates', self.auto_check_check.isChecked())
        self.config.set('auto_update', self.auto_update_check.isChecked())
        self.config.set('update_manifest_url', self.manifest_url_input.text())
        
        self.accept()
