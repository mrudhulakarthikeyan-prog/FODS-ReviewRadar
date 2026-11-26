@echo off
setlocal
cd /d "%~dp0"
title ReviewRadar - Setup and Launch
color 1F

echo ========================================================
echo                 REVIEWRADAR
echo        Product Review Analysis Workspace
echo ========================================================
echo.
where py >nul 2>nul
if errorlevel 1 goto no_python
where node >nul 2>nul
if errorlevel 1 goto no_node
if not exist .venv\Scripts\python.exe (
  echo [1/5] Preparing Python environment...
  py -m venv .venv
  if errorlevel 1 goto failed
)
echo [2/5] Installing required packages...
.venv\Scripts\python.exe -m pip install --disable-pip-version-check --upgrade pip
if errorlevel 1 goto failed
.venv\Scripts\python.exe -m pip install --disable-pip-version-check -r requirements.txt
if errorlevel 1 goto failed
if not exist frontend\node_modules\vite\bin\vite.js (
  echo [3/5] Installing website packages...
  pushd frontend
  call npm install
  if errorlevel 1 goto npm_failed
  popd
) else (
  echo [3/5] Website packages already installed.
)
if not exist backend\models\sentiment_model.pkl (
  echo [4/5] Downloading public review data and training models...
  echo This needs internet and may take a few minutes. Please wait...
  .venv\Scripts\python.exe -m backend.bootstrap
  if errorlevel 1 goto failed
) else (
  echo [4/5] Trained sentiment model found. Skipping training.
)
echo [5/5] Starting ReviewRadar...
start "ReviewRadar Backend" cmd /k "cd /d ""%~dp0"" && ""%~dp0.venv\Scripts\python.exe"" -m backend.app"
timeout /t 3 /nobreak >nul
start "ReviewRadar Website" cmd /k "cd /d ""%~dp0frontend"" && npm run dev -- --host 127.0.0.1"
timeout /t 5 /nobreak >nul
start "" http://localhost:5173
echo.
echo ReviewRadar is starting. Keep both terminal windows open.
echo Website: http://localhost:5173
echo Close both terminal windows to stop the application.
pause
exit /b 0

:npm_failed
popd
goto failed
:no_python
echo Python was not found. Install Python 3.11 or newer and enable PATH.
pause
exit /b 1
:no_node
echo Node.js was not found. Install the Node.js LTS version and try again.
pause
exit /b 1
:failed
echo.
echo Setup or model training could not finish.
echo Check the error above. Confirm internet access and run this file again.
pause
exit /b 1