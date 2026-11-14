@echo off
cd /d "%~dp0"
if exist .venv\Scripts\python.exe (
  .venv\Scripts\python.exe -m streamlit run dashboard/app.py --server.port 8505
) else (
  python -m pip install -r requirements.txt
  python -m streamlit run dashboard/app.py --server.port 8505
)
pause
