# -*- coding: utf-8 -*-
"""
ログ管理モジュール
"""

import logging
import sys
from pathlib import Path
from datetime import datetime

def setup_logger(name: str = "ytdlp_gui", level: int = logging.INFO) -> logging.Logger:
    """ロガーをセットアップ"""
    # ログディレクトリを作成
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # ロガー作成
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # 既存のハンドラを削除
    logger.handlers.clear()
    
    # フォーマッター
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # コンソールハンドラ
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # ファイルハンドラ
    log_file = log_dir / f"ytdlp_gui_{datetime.now().strftime('%Y%m%d')}.log"
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger
