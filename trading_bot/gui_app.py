import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, simpledialog
import threading
import time
from datetime import datetime
import sys
import os
import json

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data_feed import RealTimeDataFeed
from analyzer import MarketAnalyzer
from notifier import TelegramNotifier

class TradingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ManiTube AI Trading Bot - VIP Edition")
        self.root.geometry("1100x700")

        style = ttk.Style()
        style.theme_use('clam')

        # --- State ---
        self.running = False
        self.feed = RealTimeDataFeed()
        self.analyzer = MarketAnalyzer()
        self.notifier = None
        self.last_signals = {}
        self.config_file = "config.json"

        # --- Layout ---
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(expand=True, fill='both', padx=10, pady=10)

        self.tab_dashboard = ttk.Frame(self.notebook)
        self.tab_settings = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_dashboard, text='  📊 Live Market (بازار زنده)  ')
        self.notebook.add(self.tab_settings, text='  ⚙️ Config (تنظیمات)  ')

        self._build_settings_tab()
        self._build_dashboard_tab()

        self.load_settings()
        self.log("VIP Engine Initialized. Waiting for Start...")

    def _build_settings_tab(self):
        # --- Telegram Config ---
        frame_tg = ttk.LabelFrame(self.tab_settings, text="Telegram Configuration", padding=20)
        frame_tg.pack(fill="x", padx=20, pady=20)

        ttk.Label(frame_tg, text="Bot Token:").grid(row=0, column=0, sticky="w", pady=5)
        self.entry_token = ttk.Entry(frame_tg, width=50)
        self.entry_token.grid(row=0, column=1, sticky="w", pady=5)

        ttk.Label(frame_tg, text="Chat ID:").grid(row=1, column=0, sticky="w", pady=5)
        self.entry_chat_id = ttk.Entry(frame_tg, width=20)
        self.entry_chat_id.grid(row=1, column=1, sticky="w", pady=5)

        btn_frame = ttk.Frame(frame_tg)
        btn_frame.grid(row=2, column=1, sticky="w", pady=10)

        ttk.Button(btn_frame, text="Save & Connect", command=self.save_settings).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Test Message", command=self.test_telegram).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Force Test Signal", command=self.force_test_signal).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Help (Channel ID)", command=self.show_help).pack(side="left", padx=5)

        # --- Asset Management ---
        frame_asset = ttk.LabelFrame(self.tab_settings, text="Asset Management", padding=20)
        frame_asset.pack(fill="x", padx=20, pady=10)

        ttk.Button(frame_asset, text="Add New Asset", command=self.add_asset_dialog).pack(side="left", padx=5)
        ttk.Button(frame_asset, text="Remove Selected from Dashboard", command=self.remove_asset_dialog).pack(side="left", padx=5)

    def _build_dashboard_tab(self):
        ctrl_frame = ttk.Frame(self.tab_dashboard, padding=10)
        ctrl_frame.pack(fill="x")

        self.btn_start = ttk.Button(ctrl_frame, text="▶ ACTIVATE AI (فعال‌سازی هوش مصنوعی)", command=self.start_trading_loop)
        self.btn_start.pack(side="left", padx=10)

        self.btn_stop = ttk.Button(ctrl_frame, text="⏹ DEACTIVATE (غیرفعال‌سازی)", command=self.stop_trading_loop, state="disabled")
        self.btn_stop.pack(side="left", padx=10)

        self.lbl_status = ttk.Label(ctrl_frame, text="Status: OFFLINE", foreground="red", font=("Arial", 10, "bold"))
        self.lbl_status.pack(side="left", padx=20)

        # Expanded Table Columns with Scrollbar
        tree_frame = ttk.Frame(self.tab_dashboard)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=5)

        columns = ("Symbol", "Price", "Trend", "MACD", "RSI", "Status", "Signal", "Time")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=12)

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        for col in columns:
            self.tree.heading(col, text=col)
            # Make Status column wider
            if col == "Status":
                self.tree.column(col, width=200, anchor="center")
            else:
                self.tree.column(col, width=90, anchor="center")

        # Initial Population
        self.refresh_tree_items()

        log_frame = ttk.LabelFrame(self.tab_dashboard, text="AI Analysis Log (تحلیل‌های لحظه‌ای)", padding=5)
        log_frame.pack(expand=True, fill="both", padx=10, pady=10)

        self.txt_log = scrolledtext.ScrolledText(log_frame, height=8, state='disabled', font=("Consolas", 9))
        self.txt_log.pack(expand=True, fill="both")

    def refresh_tree_items(self):
        """Clears and repopulates the treeview items based on current assets."""
        for item in self.tree.get_children():
            self.tree.delete(item)

        for asset in self.feed.assets.keys():
            self.tree.insert("", "end", iid=asset, values=(asset, "...", "...", "...", "...", "Initializing...", "WAIT", "-"))

    def log(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        final_msg = f"[{timestamp}] {message}\n"
        self.txt_log.config(state='normal')
        self.txt_log.insert('end', final_msg)
        self.txt_log.see('end')
        self.txt_log.config(state='disabled')

    def save_settings(self):
        token = self.entry_token.get().strip()
        chat_id = self.entry_chat_id.get().strip()

        if not token or not chat_id:
            messagebox.showerror("Error", "Missing Credentials")
            return

        self.notifier = TelegramNotifier(token, chat_id)

        # Save config including Custom Assets (only differences from default)
        custom_assets = {k: v for k, v in self.feed.assets.items() if k not in self.feed.default_assets}

        try:
            with open(self.config_file, "w") as f:
                json.dump({
                    "token": token,
                    "chat_id": chat_id,
                    "custom_assets": custom_assets
                }, f)
            self.log("Configuration Saved (including custom assets).")
            messagebox.showinfo("Success", "Configuration Saved.")
        except Exception as e:
            messagebox.showerror("Error", f"Could not save config: {e}")

    def load_settings(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r") as f:
                    config = json.load(f)
                    token = config.get("token", "")
                    chat_id = config.get("chat_id", "")
                    custom_assets = config.get("custom_assets", {})

                    self.entry_token.insert(0, token)
                    self.entry_chat_id.insert(0, chat_id)

                    # Merge custom assets
                    if custom_assets:
                        self.feed.assets.update(custom_assets)
                        self.refresh_tree_items()
                        self.log(f"Loaded {len(custom_assets)} custom assets.")

                    if token and chat_id:
                        self.notifier = TelegramNotifier(token, chat_id)
                        self.log("Telegram Connected.")
            except Exception as e:
                self.log(f"Failed to load config: {e}")

    def add_asset_dialog(self):
        name = simpledialog.askstring("Add Asset", "Enter Asset Name (e.g. Pepe):")
        if not name: return
        ticker = simpledialog.askstring("Add Asset", "Enter Yahoo Ticker (e.g. PEPE-USD):")
        if not ticker: return

        self.feed.add_asset(name, ticker)
        self.refresh_tree_items()
        self.log(f"Added Asset: {name} ({ticker})")
        messagebox.showinfo("Success", "Asset Added. Click 'Save & Connect' to persist.")

    def remove_asset_dialog(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Select an asset in the table first.")
            return

        asset_name = selection[0]
        if messagebox.askyesno("Confirm", f"Remove {asset_name}?"):
            self.feed.remove_asset(asset_name)
            self.refresh_tree_items()
            self.log(f"Removed Asset: {asset_name}")

    def test_telegram(self):
        if not self.notifier:
            messagebox.showwarning("Warning", "Save settings first.")
            return
        self.notifier.send_message("🔔 VIP System Connected Successfully.")

    def force_test_signal(self):
        if not self.notifier:
            messagebox.showwarning("Warning", "Save settings first.")
            return

        dummy_signal = {
            'Symbol': 'TEST-SIGNAL',
            'Type': '🟢 TEST BUY',
            'Entry': 12345.67,
            'StopLoss': 12000.00,
            'TP1': 12500.00,
            'TP2': 13000.00,
            'TP3': 14000.00,
            'RiskLevel': 'Low (Test)',
            'Reason': 'User Requested Test',
            'RSI': 50.0
        }
        self.notifier.send_vip_signal(dummy_signal)
        messagebox.showinfo("Sent", "Test Signal sent to Telegram. Check your Channel!")

    def show_help(self):
        help_text = (
            "How to get Channel ID:\n\n"
            "1. Add the bot to your Channel as an Administrator.\n"
            "2. Send a message to the channel.\n"
            "3. Forward that message to @userinfobot or check API updates.\n"
            "4. Channel IDs usually start with -100 (e.g., -100123456789)."
        )
        messagebox.showinfo("Telegram Help", help_text)

    def start_trading_loop(self):
        if not self.notifier:
            if not messagebox.askyesno("Confirm", "No Telegram Configured. Run without alerts?"):
                return

        self.running = True
        self.btn_start.config(state="disabled")
        self.btn_stop.config(state="normal")
        self.lbl_status.config(text="Status: AI SCANNING...", foreground="green")
        self.log("AI Scanner Started. Fetching market data...")

        self.thread = threading.Thread(target=self._update_loop, daemon=True)
        self.thread.start()

    def stop_trading_loop(self):
        self.running = False
        self.btn_start.config(state="normal")
        self.btn_stop.config(state="disabled")
        self.lbl_status.config(text="Status: OFFLINE", foreground="red")
        self.log("Scanner Stopped.")

    def _update_loop(self):
        while self.running:
            # Create a copy of keys to avoid runtime error if dictionary changes during iteration
            current_assets = list(self.feed.assets.keys())

            for asset in current_assets:
                if not self.running: break

                try:
                    # Fetch enough history for EMA 200
                    hist = self.feed.fetch_history(asset, days=300)

                    if hist.empty:
                        continue

                    analyzed = self.analyzer.analyze(hist)
                    latest = analyzed.iloc[-1]

                    # Generate VIP Signal
                    signal_data = self.analyzer.generate_signal(analyzed, asset)

                    # Trend Status
                    if latest['Close'] > latest['EMA_50']:
                        trend = "UP ↗"
                    else:
                        trend = "DOWN ↘"

                    # Update Table
                    self.root.after(0, self._update_tree, asset, latest, trend, signal_data)

                    # Handle Signal
                    if signal_data and signal_data['Type'] in ['BUY', 'SELL']:
                        sig_type = signal_data['Type']
                        # Prevent repeating same signal type consecutively
                        last_sig = self.last_signals.get(asset)

                        if sig_type != last_sig:
                            self.log(f"🔥 VIP SIGNAL: {asset} -> {sig_type}")
                            if self.notifier:
                                self.notifier.send_vip_signal(signal_data)
                            self.last_signals[asset] = sig_type

                except Exception as e:
                    print(f"Error analyzing {asset}: {e}")

                time.sleep(0.5) # Fast scan

            # Wait before next full scan cycle
            for _ in range(30):
                if not self.running: break
                time.sleep(1)

    def _update_tree(self, asset, row, trend, signal_data):
        price = f"${row['Close']:,.2f}"
        macd = f"{row['MACD']:.2f}"
        rsi = f"{row['RSI']:.1f}"

        sig_str = signal_data['Type']
        status = signal_data.get('Reason', 'Scanning...')

        # Check if item exists (it might have been removed)
        if self.tree.exists(asset):
            self.tree.item(asset, values=(asset, price, trend, macd, rsi, status, sig_str, datetime.now().strftime("%H:%M")))

if __name__ == "__main__":
    root = tk.Tk()
    app = TradingApp(root)
    root.mainloop()
