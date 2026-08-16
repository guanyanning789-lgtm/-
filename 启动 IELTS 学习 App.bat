@echo off
cd /d "%~dp0"
where py >nul 2>nul
if %errorlevel%==0 (
  py -m pip show edge-tts >nul 2>nul || py -m pip install edge-tts -q
  start "" pyw natural_voice_v5.py
  exit /b
)
where pythonw >nul 2>nul
if %errorlevel%==0 (
  python -m pip show edge-tts >nul 2>nul || python -m pip install edge-tts -q
  start "" pythonw natural_voice_v5.py
  exit /b
)
python -m pip install -r requirements.txt
python natural_voice_v5.py
