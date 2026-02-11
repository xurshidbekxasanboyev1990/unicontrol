@echo off
REM UniControl Backend - Run Script (Windows)

echo ================================
echo   UniControl Backend Server
echo ================================

REM Check Python
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo Python is not installed!
    exit /b 1
)

REM Activate virtual environment if exists
if exist "venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
)

REM Check if .env exists
if not exist ".env" (
    echo Warning: .env file not found.
    if exist "..\.env.example" (
        echo Copying from .env.example...
        copy "..\.env.example" ".env"
    )
)

REM Run migrations
echo Running database migrations...
alembic upgrade head

REM Run server
echo Starting server...
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
