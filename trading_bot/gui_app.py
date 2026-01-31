import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import time
from datetime import datetime
import sys
import os

# Ensure imports work
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data_feed import RealTimeDataFeed
from analyzer import MarketAnalyzer
from notifier import TelegramNotifier

class TradingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ManiTube Trading Bot - Live Dashboard")
        self.root.geometry("900x650")

        # Styles
        style = ttk.Style()
        style.theme_use('clam')

        # --- State ---
        self.running = False
        self.feed = RealTimeDataFeed()
        self.analyzer = MarketAnalyzer()
        self.notifier = None
        self.last_signals = {} # To prevent spamming signals every second

        # --- Layout ---
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(expand=True, fill='both', padx=10, pady=10)

        # Tabs
        self.tab_dashboard = ttk.Frame(self.notebook)
        self.tab_settings = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_dashboard, text='  📊 Dashboard (داشبورد)  ')
        self.notebook.add(self.tab_settings, text='  ⚙️ Settings (تنظیمات)  ')

        self._build_settings_tab()
        self._build_dashboard_tab()

        # Initial Log
        self.log("برنامه آماده است. لطفاً ابتدا تنظیمات تلگرام را انجام دهید.")

    def _build_settings_tab(self):
        frame = ttk.LabelFrame(self.tab_settings, text="Telegram Configuration (تنظیمات تلگرام)", padding=20)
        frame.pack(fill="x", padx=20, pady=20)

        # Bot Token
        ttk.Label(frame, text="Bot Token:").grid(row=0, column=0, sticky="w", pady=5)
        self.entry_token = ttk.Entry(frame, width=50)
        self.entry_token.grid(row=0, column=1, sticky="w", pady=5)
        # Pre-fill if known (Optional, removed specific hardcode for cleanliness, but user can fill)
        self.entry_token.insert(0, "")

        # Chat ID
        ttk.Label(frame, text="Chat ID:").grid(row=1, column=0, sticky="w", pady=5)
        self.entry_chat_id = ttk.Entry(frame, width=20)
        self.entry_chat_id.grid(row=1, column=1, sticky="w", pady=5)
        self.entry_chat_id.insert(0, "")

        # Buttons
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=2, column=1, sticky="w", pady=10)

        ttk.Button(btn_frame, text="Save & Connect (ذخیره)", command=self.save_settings).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Test Message (تست)", command=self.test_telegram).pack(side="left", padx=5)

        # Instructions
        info_text = """
        راهنما:
        1. توکن ربات را از @BotFather بگیرید.
        2. برای Chat ID، اگر نمی‌دانید، فایل get_chat_id.py را اجرا کنید یا به ربات پیام دهید.
        3. دکمه Save را بزنید.
        4. دکمه Test را بزنید تا مطمئن شوید پیام می‌رسد.
        """
        lbl_info = ttk.Label(frame, text=info_text, foreground="gray")
        lbl_info.grid(row=3, column=0, columnspan=2, sticky="w")

    def _build_dashboard_tab(self):
        # Top Controls
        ctrl_frame = ttk.Frame(self.tab_dashboard, padding=10)
        ctrl_frame.pack(fill="x")

        self.btn_start = ttk.Button(ctrl_frame, text="▶ START TRADING (شروع)", command=self.start_trading_loop)
        self.btn_start.pack(side="left", padx=10)

        self.btn_stop = ttk.Button(ctrl_frame, text="⏹ STOP (توقف)", command=self.stop_trading_loop, state="disabled")
        self.btn_stop.pack(side="left", padx=10)

        self.lbl_status = ttk.Label(ctrl_frame, text="Status: STOPPED", foreground="red", font=("Arial", 10, "bold"))
        self.lbl_status.pack(side="left", padx=20)

        # Asset Table
        columns = ("Symbol", "Price", "SMA7", "SMA30", "RSI", "Signal", "Time")
        self.tree = ttk.Treeview(self.tab_dashboard, columns=columns, show="headings", height=8)
        self.tree.pack(fill="x", padx=10, pady=5)

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100, anchor="center")

        # Initial Assets
        self.watched_assets = ["Bitcoin (BTC)", "Ethereum (ETH)", "Gold (XAU)", "Oil (Crude)"]
        for asset in self.watched_assets:
            self.tree.insert("", "end", iid=asset, values=(asset, "Loading...", "-", "-", "-", "WAIT", "-"))

        # Log Area
        log_frame = ttk.LabelFrame(self.tab_dashboard, text="Live Logs (گزارش زنده)", padding=5)
        log_frame.pack(expand=True, fill="both", padx=10, pady=10)

        self.txt_log = scrolledtext.ScrolledText(log_frame, height=10, state='disabled', font=("Consolas", 9))
        self.txt_log.pack(expand=True, fill="both")

    def log(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        final_msg = f"[{timestamp}] {message}\n"

        self.txt_log.config(state='normal')
        self.txt_log.insert('end', final_msg)
        self.txt_log.see('end')
        self.txt_log.config(state='disabled')
        print(final_msg.strip())

    def save_settings(self):
        token = self.entry_token.get().strip()
        chat_id = self.entry_chat_id.get().strip()

        if not token or not chat_id:
            messagebox.showerror("Error", "لطفاً توکن و Chat ID را وارد کنید.")
            return

        self.notifier = TelegramNotifier(token, chat_id)
        self.log("تنظیمات تلگرام ذخیره شد.")
        messagebox.showinfo("Success", "تنظیمات ذخیره شد.")

    def test_telegram(self):
        if not self.notifier:
            messagebox.showwarning("Warning", "ابتدا تنظیمات را ذخیره کنید.")
            return

        success = self.notifier.send_signal("🔔 این یک پیام تست از ربات مانی‌تیوب است.")
        if success:
            self.log("پیام تست با موفقیت ارسال شد.")
            messagebox.showinfo("Success", "پیام ارسال شد! ربات فعال است.")
        else:
            self.log("خطا در ارسال پیام تست. لاگ را بررسی کنید.")
            messagebox.showerror("Error", "خطا در ارسال. لطفاً مطمئن شوید ربات Start شده است.")

    def start_trading_loop(self):
        if not self.notifier:
            resp = messagebox.askyesno("Warning", "تنظیمات تلگرام انجام نشده است. آیا ادامه می‌دهید؟ (سیگنال ارسال نخواهد شد)")
            if not resp:
                return

        self.running = True
        self.btn_start.config(state="disabled")
        self.btn_stop.config(state="normal")
        self.lbl_status.config(text="Status: RUNNING (LIVE DATA)", foreground="green")
        self.log("شروع موتور معاملاتی...")

        # Start thread
        self.thread = threading.Thread(target=self._update_loop, daemon=True)
        self.thread.start()

    def stop_trading_loop(self):
        self.running = False
        self.btn_start.config(state="normal")
        self.btn_stop.config(state="disabled")
        self.lbl_status.config(text="Status: STOPPED", foreground="red")
        self.log("توقف موتور.")

    def _update_loop(self):
        while self.running:
            for asset in self.watched_assets:
                if not self.running: break

                try:
                    # 1. Fetch History for Indicators
                    hist = self.feed.fetch_history(asset, days=50)

                    if hist.empty:
                        self.log(f"خطا در دریافت داده برای {asset}")
                        continue

                    # 2. Analyze
                    analyzed = self.analyzer.analyze(hist)
                    latest = analyzed.iloc[-1]

                    price = latest['Close']
                    sma7 = latest['SMA_7']
                    sma30 = latest['SMA_30']
                    rsi = latest['RSI']
                    date_time = datetime.now().strftime("%H:%M:%S")

                    # 3. Strategy Logic
                    signal = "HOLD"
                    # Simple Golden Cross check
                    if sma7 > sma30 and rsi > 50:
                        signal = "BUY"
                    elif sma7 < sma30:
                        signal = "SELL"

                    # 4. Notify if Signal Changed
                    last_sig = self.last_signals.get(asset, "HOLD")
                    if signal != last_sig and signal != "HOLD":
                        msg = f"🚀 سیگنال جدید برای {asset}\n" \
                              f"نوع: {signal}\n" \
                              f"قیمت: {price:,.2f}\n" \
                              f"RSI: {rsi:.1f}"
                        self.log(f"SIGNAL DETECTED: {asset} -> {signal}")
                        if self.notifier:
                            self.notifier.send_signal(msg)
                        self.last_signals[asset] = signal

                    # 5. Update UI (Thread safe way)
                    self.root.after(0, self._update_tree, asset, price, sma7, sma30, rsi, signal, date_time)

                except Exception as e:
                    print(f"Loop Error: {e}")

                # Small pause between assets to avoid rate limits
                time.sleep(1)

            # Wait 60 seconds before next cycle (1-minute candles)
            for _ in range(60):
                if not self.running: break
                time.sleep(1)

    def _update_tree(self, asset, price, sma7, sma30, rsi, signal, time_str):
        # Format values
        f_price = f"{price:,.2f}"
        f_sma7 = f"{sma7:,.2f}"
        f_sma30 = f"{sma30:,.2f}"
        f_rsi = f"{rsi:.1f}"

        self.tree.item(asset, values=(asset, f_price, f_sma7, f_sma30, f_rsi, signal, time_str))

if __name__ == "__main__":
    root = tk.Tk()
    app = TradingApp(root)
    root.mainloop()
