@echo off
cd %~dp0

if not exist .env (
    echo Creating .env file from .env.example...
    copy .env.example .env >nul
    echo Please edit the .env file and add your TELEGRAM_TOKEN and GEMINI_API_KEY.
    echo Then run this script again.
    pause
    exit /b
)

python -m src.bot
pause
