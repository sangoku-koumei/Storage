@echo off
setlocal
cd /d "%~dp0"
echo 仮想脳 ツール管理ダッシュボードを起動しています...
start /b pythonw dashboard.py
exit
