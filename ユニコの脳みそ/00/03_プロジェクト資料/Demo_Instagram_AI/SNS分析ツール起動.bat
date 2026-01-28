@echo off
setlocal
cd /d "%~dp0"

echo ==========================================
echo    Instagram SNS AI Analysis Tool
echo ==========================================
echo.
echo Launching...
echo.

"c:\Users\user\Desktop\•ÛŠÇŒÉ\.venv\Scripts\python.exe" -m streamlit run "%~dp0..\Demo_Instagram_AI\app.py"

if %ERRORLEVEL% neq 0 (
    echo.
    echo [Error] Failed to start Streamlit.
    pause
)
