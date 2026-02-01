import requests
import json
import os

class TelegramNotifier:
    def __init__(self, bot_token=None, chat_id=None):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.msg_url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage" if self.bot_token else None
        self.photo_url = f"https://api.telegram.org/bot{self.bot_token}/sendPhoto" if self.bot_token else None

    def send_vip_signal(self, signal_data, image_path=None):
        """
        Sends a VIP signal message (Cornix Style) with an optional chart image.
        """
        if not self.bot_token or not self.chat_id:
            return False

        # Extract Symbol for Hashtag (e.g. "Bitcoin (BTC)" -> "#BTC")
        symbol_raw = signal_data['Symbol']
        if '(' in symbol_raw:
            ticker = symbol_raw.split('(')[1].replace(')', '')
        else:
            ticker = symbol_raw.replace(' ', '')

        # Cornix/Standard Format
        direction = "Buy" if 'BUY' in signal_data['Type'] else "Sell"
        emoji = "🟢" if direction == "Buy" else "🔴"

        caption = f"""
{emoji} **#{ticker}/USDT**
**Signal Type:** {direction}

**Entry:** {signal_data['Entry']:,.2f}

**Targets:**
1) {signal_data['TP1']:,.2f}
2) {signal_data['TP2']:,.2f}
3) {signal_data['TP3']:,.2f}

**Stop Loss:** {signal_data['StopLoss']:,.2f}

-------------------
Risk: {signal_data.get('RiskLevel', 'Medium')}
Strategy: {signal_data.get('Reason', 'AI Analysis')}
"""

        if image_path and os.path.exists(image_path):
            return self.send_photo(image_path, caption)
        else:
            return self.send_message(caption)

    def send_message(self, text):
        try:
            payload = {
                "chat_id": self.chat_id,
                "text": text,
                "parse_mode": "Markdown"
            }
            response = requests.post(self.msg_url, json=payload, timeout=5)
            if response.status_code == 200:
                print(f"[TELEGRAM SENT]")
                return True
            else:
                print(f"[TELEGRAM ERROR] {response.text}")
                return False
        except Exception as e:
            print(f"[TELEGRAM EXCEPTION]: {e}")
            return False

    def send_photo(self, photo_path, caption):
        try:
            with open(photo_path, 'rb') as f:
                files = {'photo': f}
                data = {
                    'chat_id': self.chat_id,
                    'caption': caption,
                    'parse_mode': 'Markdown'
                }
                response = requests.post(self.photo_url, files=files, data=data, timeout=15)

            if response.status_code == 200:
                print(f"[TELEGRAM PHOTO SENT]")
                return True
            else:
                print(f"[TELEGRAM PHOTO ERROR] {response.text}")
                return False
        except Exception as e:
            print(f"[TELEGRAM PHOTO EXCEPTION]: {e}")
            return False

if __name__ == "__main__":
    pass
