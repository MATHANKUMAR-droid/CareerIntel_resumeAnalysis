@echo off
setlocal
cd /d "%~dp0"
title CareerIntel Setup

echo.
echo ========================================
echo          CAREERINTEL - WINDOWS
echo ========================================
echo.

where python >nul 2>nul
if errorlevel 1 (
  echo ERROR: Python was not found on PATH.
  echo Install Python 3.11 or newer and enable "Add Python to PATH".
  pause
  exit /b 1
)

if not exist "requirements.txt" (
  echo ERROR: requirements.txt is missing.
  echo Extract the ZIP and run this file from the folder containing app\ and static\.
  pause
  exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
  echo [1/5] Creating virtual environment...
  python -m venv .venv
  if errorlevel 1 goto :error
) else (
  echo [1/5] Virtual environment already exists.
)

set "PY=.venv\Scripts\python.exe"
echo [2/5] Upgrading pip...
"%PY%" -m pip install --upgrade pip
if errorlevel 1 goto :error

echo [3/5] Installing project libraries...
"%PY%" -m pip install -r requirements.txt
if errorlevel 1 goto :error

if not exist ".env" (
  echo [4/5] Creating .env from .env.example...
  copy /Y ".env.example" ".env" >nul
  if errorlevel 1 goto :error
) else (
  echo [4/5] Existing .env found; keeping your settings.
)

echo [5/5] Starting CareerIntel at http://127.0.0.1:8000
start "CareerIntel" http://127.0.0.1:8000
"%PY%" -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
if errorlevel 1 goto :error
exit /b 0

:error
echo.
echo SETUP FAILED. Read the error above.
echo Check the package error above. This project uses core Uvicorn without optional compiled extras.
pause
exit /b 1
