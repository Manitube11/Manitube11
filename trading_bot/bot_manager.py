import requests
import json
import time
import threading
import os
from datetime import datetime
from .education import get_definition, get_all_topics
from .news_sentiment import NewsAnalyzer

class BotManager:
    def __init__(self, token, chat_id=None, users_file="users.json", signals_file="signals.json"):
        self.token = token
        self.admin_chat_id = chat_id # Legacy support for single chat_id
        self.base_url = f"https://api.telegram.org/bot{token}"
        self.users_file = users_file
        self.signals_file = signals_file
        self.running = False
        self.offset = 0
        self.news_analyzer = NewsAnalyzer()

        self.users = self.load_users()

        # If admin_chat_id is provided, ensure it's in users
        if self.admin_chat_id and str(self.admin_chat_id) not in self.users:
            self.register_user(str(self.admin_chat_id))

    def load_users(self):
        if os.path.exists(self.users_file):
            try:
                with open(self.users_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def save_users(self):
        with open(self.users_file, 'w') as f:
            json.dump(self.users, f, indent=4)

    def register_user(self, chat_id):
        if chat_id not in self.users:
            self.users[chat_id] = {
                "subscriptions": ["ALL"], # ALL, Crypto, Stock, Commodity, Forex
                "risk_tolerance": "Medium", # Low, Medium, High
                "joined_at": str(datetime.now())
            }
            self.save_users()
            return True
        return False

    def start(self):
        if self.running: return
        self.running = True
        threading.Thread(target=self._poll_loop, daemon=True).start()
        print("[BOT] Started Polling...")

    def stop(self):
        self.running = False

    def _poll_loop(self):
        while self.running:
            try:
                url = f"{self.base_url}/getUpdates?offset={self.offset}&timeout=30"
                resp = requests.get(url, timeout=40)
                if resp.status_code == 200:
                    data = resp.json()
                    if data['ok']:
                        for result in data['result']:
                            self.offset = result['update_id'] + 1
                            self._handle_update(result)
            except Exception as e:
                # print(f"[BOT] Polling Error: {e}") # Reduce noise
                time.sleep(5)
            time.sleep(1)

    def _handle_update(self, update):
        if 'message' in update and 'text' in update['message']:
            msg = update['message']
            chat_id = str(msg['chat']['id'])
            text = msg['text']

            # Auto-register
            if chat_id not in self.users:
                self.register_user(chat_id)

            if text.startswith('/'):
                self._handle_command(chat_id, text)

    def _handle_command(self, chat_id, text):
        parts = text.split()
        cmd = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []

        if cmd == "/start":
            self.send_message(chat_id, "👋 Welcome to ManiTube AI Trading Bot!\n\nUse /help to see available commands.")

        elif cmd == "/help":
            help_text = """
🤖 **Bot Commands:**

/subscribe [type] - Subscribe to signals (crypto, stock, commodity, forex, all)
/unsubscribe [type] - Unsubscribe
/risk [level] - Set risk (low, medium, high)
/news - Get market sentiment
/stats - View signal performance
/learn [term] - Educational definitions
/settings - View your settings
"""
            self.send_message(chat_id, help_text)

        elif cmd == "/settings":
            user = self.users.get(chat_id)
            if user:
                msg = f"⚙️ **Your Settings:**\n\nSubscriptions: {', '.join(user['subscriptions'])}\nRisk Tolerance: {user['risk_tolerance']}"
                self.send_message(chat_id, msg)

        elif cmd == "/subscribe":
            if not args:
                self.send_message(chat_id, "Usage: /subscribe [crypto|stock|commodity|forex|all]")
                return

            sub_type = args[0].upper()
            valid = ["CRYPTO", "STOCK", "COMMODITY", "FOREX", "ALL"]
            if sub_type not in valid:
                 self.send_message(chat_id, f"Invalid type. Choose: {', '.join(valid)}")
                 return

            user_subs = self.users[chat_id]['subscriptions']
            if "ALL" in user_subs: user_subs.remove("ALL")

            if sub_type == "ALL":
                user_subs = ["ALL"]
            elif sub_type not in user_subs:
                user_subs.append(sub_type)

            self.users[chat_id]['subscriptions'] = user_subs
            self.save_users()
            self.send_message(chat_id, f"✅ Subscribed to {sub_type}")

        elif cmd == "/unsubscribe":
             if not args:
                self.send_message(chat_id, "Usage: /unsubscribe [type]")
                return
             sub_type = args[0].upper()
             user_subs = self.users[chat_id]['subscriptions']
             if sub_type in user_subs:
                 user_subs.remove(sub_type)
                 if not user_subs: user_subs = ["ALL"] # Default back to all if empty? Or empty. Let's leave empty.
                 self.users[chat_id]['subscriptions'] = user_subs
                 self.save_users()
                 self.send_message(chat_id, f"❌ Unsubscribed from {sub_type}")

        elif cmd == "/risk":
            if not args:
                self.send_message(chat_id, "Usage: /risk [low|medium|high]")
                return
            level = args[0].capitalize()
            if level not in ["Low", "Medium", "High"]:
                self.send_message(chat_id, "Invalid level. Choose: Low, Medium, High")
                return

            self.users[chat_id]['risk_tolerance'] = level
            self.save_users()
            self.send_message(chat_id, f"✅ Risk Tolerance set to {level}")

        elif cmd == "/news":
            self.send_message(chat_id, "⏳ Fetching Sentiment...")
            try:
                sentiment, score = self.news_analyzer.fetch_sentiment()
                msg = f"📰 **Market Sentiment**\n\nStatus: {sentiment}\nScore: {score}/100"
                self.send_message(chat_id, msg)
            except Exception as e:
                self.send_message(chat_id, "Failed to fetch news.")

        elif cmd == "/learn":
            if not args:
                topics = get_all_topics()
                self.send_message(chat_id, f"🎓 **Education Topics:**\n{topics}\n\nUsage: /learn [topic]")
            else:
                term = " ".join(args)
                defn = get_definition(term)
                self.send_message(chat_id, defn)

        elif cmd == "/stats":
             self._send_stats(chat_id)

    def _send_stats(self, chat_id):
        # Read signals.json
        count = 0
        if os.path.exists(self.signals_file):
            with open(self.signals_file, 'r') as f:
                try:
                    data = json.load(f)
                    count = len(data)
                except: pass

        self.send_message(chat_id, f"📊 **Performance Tracking**\n\nTotal Signals Generated: {count}\n(Win Rate calculation requires live tracking history)")

    def send_message(self, chat_id, text):
        try:
            payload = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
            requests.post(f"{self.base_url}/sendMessage", json=payload, timeout=5)
        except Exception as e:
            print(f"Send Error: {e}")

    def send_photo(self, chat_id, photo_path, caption):
         try:
            with open(photo_path, 'rb') as f:
                files = {'photo': f}
                data = {'chat_id': chat_id, 'caption': caption, 'parse_mode': 'Markdown'}
                requests.post(f"{self.base_url}/sendPhoto", files=files, data=data, timeout=20)
         except Exception as e:
            print(f"Photo Error: {e}")

    def broadcast_signal(self, signal, image_path=None):
        """
        Broadcasts signal to all subscribed users.
        """
        # 1. Save Signal
        self._log_signal(signal)

        # 2. Determine Asset Type
        asset_type = self._get_asset_type(signal['Symbol'])
        risk_level = signal.get('RiskLevel', 'Medium') # e.g. "Low (کم ریسک)"

        # Normalize Risk
        if "Low" in risk_level: r_val = 1
        elif "Medium" in risk_level: r_val = 2
        else: r_val = 3

        # 3. Iterate Users
        for chat_id, prefs in self.users.items():
            # Check Subscription
            subs = prefs.get('subscriptions', ['ALL'])
            if 'ALL' not in subs and asset_type not in subs:
                continue

            # Check Risk
            u_risk = prefs.get('risk_tolerance', 'Medium')
            # If user wants Low risk only (1), reject Medium (2) and High (3).
            # If user wants Medium (2), reject High (3).

            if u_risk == "Low" and r_val > 1: continue
            if u_risk == "Medium" and r_val > 2: continue

            # Send
            caption = self._format_signal(signal)
            if image_path:
                self.send_photo(chat_id, image_path, caption)
            else:
                self.send_message(chat_id, caption)

    def _get_asset_type(self, symbol):
        s = symbol.upper()
        if "BTC" in s or "ETH" in s or "-USD" in s: return "CRYPTO"
        if "=F" in s or "GOLD" in s or "OIL" in s: return "COMMODITY"
        if "=X" in s or "/" in s: return "FOREX"
        return "STOCK"

    def _log_signal(self, signal):
        data = []
        if os.path.exists(self.signals_file):
            try:
                with open(self.signals_file, 'r') as f:
                    data = json.load(f)
            except: pass

        # Avoid huge file
        if len(data) > 1000: data.pop(0)
        data.append(signal)

        with open(self.signals_file, 'w') as f:
            json.dump(data, f, indent=4)

    def _format_signal(self, signal):
        # Reuse logic from notifier.py but refined
        direction = "Buy" if 'BUY' in signal['Type'] else "Sell"
        emoji = "🟢" if direction == "Buy" else "🔴"

        # Simple string for Symbol (remove parens if any)
        sym = signal['Symbol']

        return f"""
{emoji} **#{sym}**
**Signal Type:** {direction}

**Entry:** {signal['Entry']:,.2f}

**Targets:**
1) {signal['TP1']:,.2f}
2) {signal['TP2']:,.2f}
3) {signal['TP3']:,.2f}

**Stop Loss:** {signal['StopLoss']:,.2f}

-------------------
Risk: {signal.get('RiskLevel', '-')}
Reason: {signal.get('Reason', 'AI Analysis')}
"""
