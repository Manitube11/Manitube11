import requests
import json

class TelegramNotifier:
    def __init__(self, bot_token=None, chat_id=None):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage" if self.bot_token else None

    def send_vip_signal(self, signal_data):
        """
        Sends a beautifully formatted VIP signal message.
        """
        if not self.bot_token or not self.chat_id:
            return False

        # Emoji Selection based on Signal Type
        if signal_data['Type'] == 'BUY':
            header_emoji = "🟢🟢 **VIP BUY SIGNAL** 🟢🟢"
            side_emoji = "🔼"
        else:
            header_emoji = "🔴🔴 **VIP SELL SIGNAL** 🔴🔴"
            side_emoji = "🔽"

        # Message Construction
        msg = f"""
{header_emoji}

💎 **Asset:** #{signal_data['Symbol'].split()[0]}
{side_emoji} **Action:** {signal_data['Type']} NOW

📉 **Entry Zone:** ${signal_data['Entry']:,.2f}

🛑 **Stop Loss:** ${signal_data['StopLoss']:,.2f}
⚠️ **Risk Level:** {signal_data['RiskLevel']}

💰 **Targets (Take Profit):**
TP1: ${signal_data['TP1']:,.2f} (Scalp)
TP2: ${signal_data['TP2']:,.2f} (Swing)
TP3: ${signal_data['TP3']:,.2f} (Moon)

🧠 **Strategy:** {signal_data['Reason']}
📊 **RSI:** {signal_data['RSI']:.1f}

---------------------------------------
🤖 *ManiTube AI Engine*
"""
        return self.send_message(msg)

    def send_message(self, text):
        try:
            payload = {
                "chat_id": self.chat_id,
                "text": text,
                "parse_mode": "Markdown"
            }
            response = requests.post(self.base_url, json=payload, timeout=5)
            if response.status_code == 200:
                print(f"[TELEGRAM SENT]")
                return True
            else:
                print(f"[TELEGRAM ERROR] {response.text}")
                return False
        except Exception as e:
            print(f"[TELEGRAM EXCEPTION]: {e}")
            return False

if __name__ == "__main__":
    # Test
    # signal_mock = {
    #     "Symbol": "Bitcoin (BTC)",
    #     "Type": "BUY",
    #     "Entry": 45000.50,
    #     "StopLoss": 44000.00,
    #     "TP1": 46000, "TP2": 48000, "TP3": 52000,
    #     "RiskLevel": "Low",
    #     "Reason": "Trend Breakout + Vol",
    #     "RSI": 55.4
    # }
    # notifier = TelegramNotifier("TOKEN", "ID")
    # notifier.send_vip_signal(signal_mock)
    pass
