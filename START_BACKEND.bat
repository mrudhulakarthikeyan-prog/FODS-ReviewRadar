@echo off
cd /d "%~dp0"
if not exist .venv\Scripts\python.exe py -m venv .venv
.venv\Scripts\python.exe -m pip install --disable-pip-version-check -r requirements.txt
.venv\Scripts\python.exe -m backend.app
pause
