@echo off
echo ===================================================
echo      AI Signal Bot - Starting...
echo ===================================================

echo Checking and installing dependencies...
pip install -r signal_bot/requirements.txt

echo.
echo Starting the Signal Bot App...
echo Your browser should open automatically.
echo.

streamlit run signal_bot/app.py

pause
