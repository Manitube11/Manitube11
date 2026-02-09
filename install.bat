@echo off
echo Installing dependencies...
python -m pip install -r requirements.txt
echo.
if not exist .env (
    echo creating .env from .env.example...
    copy .env.example .env
    echo Please edit .env with your API keys.
) else (
    echo .env already exists.
)
echo Installation complete. You can now run the bot using run.bat
echo Don't forget to edit .env with your API keys!
pause
