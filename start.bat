@echo off
setlocal enabledelayedexpansion
title IncidentIQ - Enterprise Local Incident Analytics & Reporting

echo =====================================================================
echo           IncidentIQ - Enterprise Local Analytics Platform
echo =====================================================================
echo.

cd /d "%~dp0"

:: 1. Check Python
echo [1/4] Checking Python environment...
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python is not found in PATH. Please ensure Python 3.10+ is installed.
    pause
    exit /b 1
)
python -c "import sys; print(f'       Using Python {sys.version.split()[0]}')"

:: 2. Check Database Warehouse
echo [2/4] Verifying local SQLite Warehouse...
if not exist "data\warehouse\incidentiq.db" (
    echo        Warehouse not found. Seeding initial dataset...
    python scripts\generate_dataset.py
    python scripts\init_warehouse.py
) else (
    echo        Warehouse database verified: data\warehouse\incidentiq.db
)

:: 3. Check Frontend Production Build
echo [3/4] Verifying frontend production build...
if not exist "frontend\dist\index.html" (
    echo        Building frontend assets with Vite...
    cd frontend
    call npm run build
    cd ..
) else (
    echo        Compiled frontend bundle ready in frontend\dist\
)

:: 4. Launch Application
echo [4/4] Starting IncidentIQ Server on http://127.0.0.1:8000 ...
echo.
echo =====================================================================
echo  STATUS: Running in Local Air-Gapped Mode
echo  URL:    http://127.0.0.1:8000
echo  Press Ctrl+C to stop the server
echo =====================================================================
echo.

:: Open default browser after 2 seconds
start "" cmd /c "timeout /t 2 /nobreak >nul && start http://127.0.0.1:8000"

:: Run FastAPI server (serves both API and built React frontend)
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
pause
