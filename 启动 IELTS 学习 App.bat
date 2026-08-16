@echo off
cd /d "%~dp0"
where py >nul 2>nul
if %errorlevel%==0 (
  start "" pyw task_engine_v4.py
  exit /b
)
where pythonw >nul 2>nul
if %errorlevel%==0 (
  start "" pythonw task_engine_v4.py
  exit /b
)
python task_engine_v4.py
