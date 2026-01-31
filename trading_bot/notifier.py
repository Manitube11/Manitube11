import requests
import json

class TelegramNotifier:
    def __init__(self, bot_token=None, chat_id=None):
        """
        Initializes the Telegram Notifier.

        Args:
            bot_token (str): Your Telegram Bot Token.
            chat_id (str): Your Telegram Channel/Chat ID.
        """
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage" if self.bot_token else None

    def send_signal(self, message):
        """
        Sends a message to the Telegram channel.
        If credentials are missing, prints to console.
        """
        if not self.bot_token or not self.chat_id or self.bot_token == "YOUR_BOT_TOKEN":
            print(f"\n[MOCK TELEGRAM] (Not Configured): {message}")
            return False

        try:
            payload = {
                "chat_id": self.chat_id,
                "text": message,
                "parse_mode": "Markdown"
            }
            response = requests.post(self.base_url, json=payload, timeout=5)
            if response.status_code == 200:
                print(f"\n[TELEGRAM SENT]: {message}")
                return True
            else:
                print(f"\n[TELEGRAM ERROR] Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            print(f"\n[TELEGRAM EXCEPTION]: {e}")
            return False

if __name__ == "__main__":
    # Test the notifier (will print mock)
    notifier = TelegramNotifier("YOUR_BOT_TOKEN", "YOUR_CHAT_ID")
    notifier.send_signal("🔴 Testing Signal: Sell BTC Now!")
