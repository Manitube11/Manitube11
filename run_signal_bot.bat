@echo off
echo ===================================================
echo      AI Signal Bot - Starting...
echo ===================================================

echo Checking and installing dependencies...
python -m pip install -r signal_bot/requirements.txt

echo.
echo Starting the Signal Bot App...
echo Your browser should open automatically.
echo.

python -m streamlit run signal_bot/app.py

pause
