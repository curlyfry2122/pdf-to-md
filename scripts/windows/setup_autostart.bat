@echo off
REM PDF Auto Converter - Autostart Setup Script
REM This script sets up automatic startup without requiring admin privileges

echo ============================================================
echo PDF Auto Converter - Autostart Setup
echo ============================================================
echo.

REM Define paths
set "PROJECT_DIR=c:\Users\jdevine\dev\pdf-to-md"
set "VBS_FILE=%PROJECT_DIR%\start_auto_converter_silent.vbs"
set "STARTUP_DIR=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "STARTUP_VBS=%STARTUP_DIR%\start_auto_converter_silent.vbs"

REM Check if VBS file exists
if not exist "%VBS_FILE%" (
    echo ERROR: VBS file not found!
    echo Expected: %VBS_FILE%
    echo.
    echo Please make sure all files are in the correct location.
    pause
    exit /b 1
)

REM Check if Startup folder exists (should always exist)
if not exist "%STARTUP_DIR%" (
    echo ERROR: Startup folder not found!
    echo Expected: %STARTUP_DIR%
    pause
    exit /b 1
)

REM Copy VBS file to Startup folder
echo Copying launcher to Startup folder...
copy /Y "%VBS_FILE%" "%STARTUP_VBS%" >nul 2>&1

if errorlevel 1 (
    echo ERROR: Failed to copy file to Startup folder!
    echo This might be a permissions issue.
    pause
    exit /b 1
)

echo SUCCESS! Auto-start has been configured.
echo.
echo The PDF Auto Converter will now start automatically when you log in.
echo.
echo Next steps:
echo 1. Restart Windows (or log out and back in)
echo 2. Drop a PDF into the inputs\ folder to test
echo 3. Check outputs\auto_convert.log to verify it's working
echo.
echo To remove auto-start, simply delete this file:
echo %STARTUP_VBS%
echo.
pause
