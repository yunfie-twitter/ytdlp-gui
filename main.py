#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
yt-dlp GUI Application
メインエントリーポイント
"""

import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from src.app import YtDlpGUI
from src.core.config import ConfigManager
from src.core.logger import setup_logger

def main():
    """アプリケーションのメインエントリーポイント"""
    # ハイDPI対応
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    app = QApplication(sys.argv)
    app.setApplicationName("yt-dlp GUI")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("yunfie")
    
    # ログセットアップ
    logger = setup_logger()
    logger.info("アプリケーション起動")
    
    # メインウィンドウ作成
    window = YtDlpGUI()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
