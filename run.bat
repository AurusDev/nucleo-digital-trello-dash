@echo off
echo Starting Nucleo Digital Dashboard...
call .venv\Scripts\activate.bat
streamlit run app.py
pause
