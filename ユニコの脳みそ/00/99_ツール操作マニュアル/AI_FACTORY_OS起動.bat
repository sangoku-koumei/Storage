@echo off
setlocal
cd /d "%~dp0"

echo ==========================================
echo    AI Factory OS: Digital Management Hub
echo ==========================================
echo.
echo Launching...
echo.

"c:\Users\user\Desktop\•ÛŠÇŒÉ\.venv\Scripts\python.exe" -m streamlit run "%~dp0..\AI_Factory_System\AI_Factory_OS_Dispatcher.py"

if %ERRORLEVEL% neq 0 (
    echo.
    echo [Error] Failed to start Streamlit.
    pause
)
