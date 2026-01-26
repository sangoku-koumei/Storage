@echo off
setlocal
cd /d "%~dp0"
echo ==========================================
echo    Auto Accept Engine (UI Automation PRO)
echo ==========================================
echo.
echo [Action]:
echo - Monitoring for "Accept", "OK", etc.
echo - Auto-clicking and Git Saving...
echo.
echo Launching engine...
echo.

"c:\Users\user\Desktop\•ÛŠÇŒÉ\.venv\Scripts\python.exe" "%~dp0..\AutoAccept\auto_accept.py"

if %ERRORLEVEL% neq 0 (
    echo.
    echo [Error] Failed to start Python script.
    pause
)
