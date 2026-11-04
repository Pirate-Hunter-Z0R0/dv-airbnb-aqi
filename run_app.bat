@echo off
title Clean Air Airbnb - Launch Setup
echo ========================================================
echo   🌿 Clean Air Airbnb - One-Click Launcher
echo ========================================================
echo.

cd /d "%~dp0"

echo [1/3] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not found! Please install Python 3.10+ and add it to PATH.
    pause
    exit /b
)

echo [2/3] Checking and installing dependencies...
pip install -r requirements.txt

echo.
echo [3/3] Launching Streamlit Dashboard...
echo Dashboard will open at http://localhost:8501
echo.
python -m streamlit run app/main.py

pause
