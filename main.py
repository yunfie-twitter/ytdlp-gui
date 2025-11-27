#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
yt-dlp GUI Application
PyQt5-based GUI with aria2c integration, plugin system, and auto-update
"""

import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from src.app import YtDlpGUI


def main():
    """Main entry point"""
    # Enable high DPI scaling
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    app = QApplication(sys.argv)
    app.setApplicationName("yt-dlp GUI")
    app.setOrganizationName("yunfie")
    
    window = YtDlpGUI()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
