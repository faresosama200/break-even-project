@echo off
chcp 65001 >nul
title SmartBEP - Quick Start
color 0A

echo ============================================
echo   SmartBEP - Intelligent Break-Even System
echo   Quick Start Script
echo ============================================
echo.

:: Check Python
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Python is not installed or not in PATH.
    echo Please install Python 3.10+ from https://python.org
    pause
    exit /b 1
)

:: Check virtual environment
if not exist ".venv\Scripts\activate.bat" (
    echo [1/5] Creating virtual environment...
    python -m venv .venv
    if %ERRORLEVEL% neq 0 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
    echo       Done.
) else (
    echo [1/5] Virtual environment found.
)

:: Activate virtual environment
echo [2/5] Activating virtual environment...
call .venv\Scripts\activate.bat

:: Install dependencies
echo [3/5] Installing dependencies...
pip install -r requirements.txt --quiet
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Failed to install dependencies.
    pause
    exit /b 1
)
echo       Done.

:: Initialize database
echo [4/5] Initializing database...
python -c "from app import create_app; from app.models.database import db; app = create_app(); app.app_context().push(); db.create_all(); print('       Done.')"
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Failed to initialize database.
    pause
    exit /b 1
)

:: Ask about seed data
if not exist "data\breakeven.db" (
    echo [INFO] No existing database found. Seeding sample data...
    python seed_data.py
) else (
    echo [INFO] Database already exists. Skipping seed data.
)

:: Start the application
echo [5/5] Starting SmartBEP server...
echo.
echo ============================================
echo   Server running at: http://localhost:5000
echo   Press Ctrl+C to stop the server
echo ============================================
echo.

:: Open browser automatically after a short delay
start "" cmd /c "timeout /t 2 /nobreak >nul & start http://localhost:5000"

set FLASK_ENV=development
python run.py

pause
