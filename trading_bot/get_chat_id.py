import requests
import time
import sys

def get_chat_id():
    print("===========================================")
    print("   Telegram Chat ID Finder (یابنده آی‌دی چت)   ")
    print("===========================================\n")

    print("1. ربات خود را در تلگرام پیدا کنید و دکمه Start را بزنید.")
    print("2. اگر می‌خواهید در کانال استفاده کنید، ربات را در کانال ادمین کنید و یک پیام در کانال بفرستید.")
    print("3. توکن ربات خود را در زیر وارد کنید:\n")

    token = input("Bot Token: ").strip()

    if not token:
        print("Error: Token cannot be empty.")
        return

    url = f"https://api.telegram.org/bot{token}/getUpdates"

    print("\n[INFO] Checking for updates... (درحال بررسی پیام‌ها)")

    try:
        response = requests.get(url, timeout=10)
        data = response.json()

        if not data.get("ok"):
            print(f"\n[ERROR] Telegram API Error: {data.get('description')}")
            print("Please check your Bot Token.")
            return

        updates = data.get("result", [])

        if not updates:
            print("\n[WARNING] No messages found! (هیچ پیامی پیدا نشد)")
            print("لطفاً همین الان به ربات خود یک پیام (مثل 'Hello') بفرستید یا در کانال پستی بگذارید.")
            print("سپس دوباره این برنامه را اجرا کنید.")
        else:
            print("\n" + "="*40)
            print("Latest Messages Found (آخرین پیام‌های دریافتی):")
            print("="*40)
            for update in updates[-3:]: # Show last 3
                if 'message' in update:
                    chat = update['message']['chat']
                    msg_text = update['message'].get('text', '(No Text)')
                    print(f"Type: Private/Group")
                    print(f"Chat Name: {chat.get('first_name', '')} {chat.get('last_name', '')} {chat.get('title', '')}")
                    print(f"Chat ID: {chat['id']}")
                    print(f"Message: {msg_text}")
                    print("-" * 20)
                elif 'channel_post' in update:
                    chat = update['channel_post']['chat']
                    title = chat.get('title', 'No Title')
                    print(f"Type: Channel (کانال)")
                    print(f"Channel Name: {title}")
                    print(f"Chat ID: {chat['id']}")
                    print("-" * 20)

            print("\n[SUCCESS] آی‌دی بالا (Chat ID) را کپی کنید و در فایل main.py قرار دهید.")

    except Exception as e:
        print(f"\n[EXCEPTION] Error connecting to Telegram: {e}")

if __name__ == "__main__":
    get_chat_id()
