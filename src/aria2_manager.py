#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
aria2c Manager - RPC and CLI modes
"""

import os
import subprocess
import json
import time
import requests
from typing import Optional, Dict, Callable


class Aria2Manager:
    """Manages aria2c downloads (RPC and CLI modes)"""
    
    def __init__(self, config):
        self.config = config
        self.use_rpc = config.get('aria2c_use_rpc', True)
        self.rpc_url = config.get('aria2c_rpc_url', 'http://localhost:6800/jsonrpc')
        self.rpc_secret = config.get('aria2c_rpc_secret', '')
        self.aria2c_path = config.get('aria2c_path', 'aria2c')
    
    def check_connection(self) -> Dict:
        """Check aria2c connection"""
        if self.use_rpc:
            return self._check_rpc_connection()
        else:
            return self._check_cli_available()
    
    def _check_rpc_connection(self) -> Dict:
        """Check RPC connection"""
        try:
            response = self._rpc_call('aria2.getVersion')
            
            if response:
                return {
                    'success': True,
                    'mode': 'RPC',
                    'version': response.get('version', 'Unknown')
                }
            else:
                return {
                    'success': False,
                    'mode': 'RPC',
                    'error': 'RPC接続失敗'
                }
        
        except Exception as e:
            return {
                'success': False,
                'mode': 'RPC',
                'error': str(e)
            }
    
    def _check_cli_available(self) -> Dict:
        """Check CLI availability"""
        try:
            result = subprocess.run(
                [self.aria2c_path, '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                version_line = result.stdout.split('\n')[0]
                return {
                    'success': True,
                    'mode': 'CLI',
                    'version': version_line
                }
            else:
                return {
                    'success': False,
                    'mode': 'CLI',
                    'error': 'aria2cの実行に失敗しました'
                }
        
        except Exception as e:
            return {
                'success': False,
                'mode': 'CLI',
                'error': str(e)
            }
    
    def download(self, url: str, output_dir: str, filename: str, 
                 progress_callback: Optional[Callable] = None) -> Dict:
        """Download file"""
        if self.use_rpc:
            result = self._download_rpc(url, output_dir, filename, progress_callback)
            
            # Fallback to CLI if RPC fails
            if not result['success']:
                self.use_rpc = False
                return self._download_cli(url, output_dir, filename, progress_callback)
            
            return result
        else:
            return self._download_cli(url, output_dir, filename, progress_callback)
    
    def _download_rpc(self, url: str, output_dir: str, filename: str,
                      progress_callback: Optional[Callable] = None) -> Dict:
        """Download using RPC"""
        try:
            # Prepare options
            options = {
                'dir': output_dir,
                'out': filename,
                'max-connection-per-server': str(self.config.get('aria2c_max_connections', 16)),
                'split': str(self.config.get('aria2c_split', 16)),
                'continue': 'true'
            }
            
            # Add download
            response = self._rpc_call('aria2.addUri', [[url], options])
            
            if not response:
                return {'success': False, 'error': 'ダウンロード追加失敗'}
            
            gid = response
            
            # Monitor progress
            if progress_callback:
                self._monitor_rpc_progress(gid, progress_callback)
            
            return {'success': True, 'gid': gid}
        
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _download_cli(self, url: str, output_dir: str, filename: str,
                      progress_callback: Optional[Callable] = None) -> Dict:
        """Download using CLI"""
        try:
            cmd = [
                self.aria2c_path,
                f'-x{self.config.get("aria2c_max_connections", 16)}',
                f'-s{self.config.get("aria2c_split", 16)}',
                f'-d{output_dir}',
                f'-o{filename}',
                '--continue=true',
                url
            ]
            
            # Run aria2c
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            
            # Monitor progress
            if progress_callback:
                for line in process.stdout:
                    # Parse progress from output
                    if '%' in line:
                        try:
                            parts = line.split()
                            for i, part in enumerate(parts):
                                if '%' in part:
                                    progress = int(part.replace('%', '').replace('(', ''))
                                    progress_callback(progress)
                                    break
                        except:
                            pass
            
            # Wait for completion
            process.wait()
            
            if process.returncode == 0:
                if progress_callback:
                    progress_callback(100)
                return {'success': True}
            else:
                return {'success': False, 'error': f'aria2c終了コード: {process.returncode}'}
        
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _rpc_call(self, method: str, params: Optional[list] = None) -> Optional[any]:
        """Make RPC call"""
        payload = {
            'jsonrpc': '2.0',
            'id': 'ytdlp-gui',
            'method': method,
            'params': []
        }
        
        # Add secret token if configured
        if self.rpc_secret:
            payload['params'].append(f'token:{self.rpc_secret}')
        
        # Add method params
        if params:
            payload['params'].extend(params)
        
        try:
            response = requests.post(
                self.rpc_url,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('result')
            
            return None
        
        except Exception:
            return None
    
    def _monitor_rpc_progress(self, gid: str, progress_callback: Callable):
        """Monitor RPC download progress"""
        while True:
            try:
                status = self._rpc_call('aria2.tellStatus', [gid])
                
                if not status:
                    break
                
                # Calculate progress
                completed = int(status.get('completedLength', 0))
                total = int(status.get('totalLength', 1))
                
                if total > 0:
                    progress = int((completed / total) * 100)
                    progress_callback(progress)
                
                # Check if completed
                if status.get('status') == 'complete':
                    progress_callback(100)
                    break
                elif status.get('status') == 'error':
                    break
                
                time.sleep(1)
            
            except Exception:
                break
