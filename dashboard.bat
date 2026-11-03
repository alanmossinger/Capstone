@echo off
rem Beyond Prediction - open the dashboard (double-click, or run from a terminal).
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo The project environment is missing: run "make setup" first.
  pause
  exit /b 1
)
echo Starting the dashboard from the project .venv - it opens in your browser at http://localhost:8501
echo Close this window to stop it.
.venv\Scripts\python.exe -m streamlit run app/app.py
pause
