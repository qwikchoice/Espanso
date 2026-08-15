@echo off
title Espanso Manager
cd /d "%~dp0.."

:: Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo  ERROR: Python not found.
    echo  Please install Python from https://python.org
    echo  Make sure to check "Add Python to PATH" during install.
    echo.
    pause
    exit /b 1
)

echo  Starting Espanso Manager...
echo  Your browser will open automatically.
echo  Close this window to stop the server.
echo.
python "%~dp0..\espanso_server.py"
if errorlevel 1 (
    echo.
    echo  Server exited with an error.
    pause
)
