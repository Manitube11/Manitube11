import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
PROXY_URL = os.getenv("PROXY_URL")

if not TELEGRAM_TOKEN:
    print("Warning: TELEGRAM_TOKEN is not set in environment variables.")
if not GEMINI_API_KEY:
    print("Warning: GEMINI_API_KEY is not set in environment variables.")
