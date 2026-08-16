@echo off
cd /d "%~dp0"
where py >nul 2>nul
if %errorlevel%==0 (
  start "" pyw learning_engine_v2.py
  exit /b
)
where pythonw >nul 2>nul
if %errorlevel%==0 (
  start "" pythonw learning_engine_v2.py
  exit /b
)
python learning_engine_v2.py
