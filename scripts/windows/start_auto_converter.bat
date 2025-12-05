@echo off
REM PDF Auto Converter - Startup Script
REM This script starts the PDF auto converter in watch mode

REM Change to the project directory
cd /d "c:\Users\jdevine\dev\pdf-to-md"

REM Check if the directory exists
if not exist "c:\Users\jdevine\dev\pdf-to-md" (
    echo ERROR: Project directory not found!
    echo Expected: c:\Users\jdevine\dev\pdf-to-md
    pause
    exit /b 1
)

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found!
    echo Please ensure Python is installed and in your PATH
    pause
    exit /b 1
)

REM Check if auto_convert.py exists
if not exist "auto_convert.py" (
    echo ERROR: auto_convert.py not found in project directory!
    pause
    exit /b 1
)

REM Create outputs directory if it doesn't exist
if not exist "outputs" mkdir outputs

REM Start the auto converter
echo Starting PDF Auto Converter...
echo Log file: outputs\auto_convert.log
echo Press Ctrl+C to stop
echo.

python auto_convert.py
