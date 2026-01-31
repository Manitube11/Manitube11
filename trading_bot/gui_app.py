import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import threading
import time
from datetime import datetime
import sys
import os
import json
import subprocess
import platform

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data_feed import RealTimeDataFeed
from analyzer import MarketAnalyzer
from notifier import TelegramNotifier
from visualizer import Visualizer

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

class TradingApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("ManiTube AI Trading Bot - PRO VERSION")
        self.geometry("1200x800")

        # --- State ---
        self.running = False
        self.feed = RealTimeDataFeed()
        self.analyzer = MarketAnalyzer()
        self.viz = Visualizer()
        self.notifier = None
        self.last_signals = {}
        self.config_file = "config.json"
        self.latest_analysis_data = {} # Store df for chart viewing
        self.last_analysis_time = {} # Timestamp for last heavy analysis per asset

        # --- Layout ---
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Side Navigation
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(4, weight=1)

        self.logo_label = ctk.CTkLabel(self.sidebar, text="ManiTube AI\nPRO 3.0", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=20)

        self.btn_dashboard = ctk.CTkButton(self.sidebar, text="📊 Live Market", command=self.show_dashboard)
        self.btn_dashboard.grid(row=1, column=0, padx=20, pady=10)

        self.btn_config = ctk.CTkButton(self.sidebar, text="⚙️ Configuration", command=self.show_config)
        self.btn_config.grid(row=2, column=0, padx=20, pady=10)

        self.lbl_status = ctk.CTkLabel(self.sidebar, text="STATUS: OFFLINE", text_color="red")
        self.lbl_status.grid(row=5, column=0, padx=20, pady=10)

        # Main Area
        self.main_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

        # Create Tabs (Hidden, managed manually)
        self.frame_dashboard = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.frame_config = ctk.CTkFrame(self.main_frame, fg_color="transparent")

        self._build_dashboard()
        self._build_config()

        self.show_dashboard()
        self.load_settings()
        self.log("System Initialized. Ready.")

    def show_dashboard(self):
        self.frame_config.pack_forget()
        self.frame_dashboard.pack(fill="both", expand=True)

    def show_config(self):
        self.frame_dashboard.pack_forget()
        self.frame_config.pack(fill="both", expand=True)

    def _build_dashboard(self):
        # Top Controls
        ctrl_frame = ctk.CTkFrame(self.frame_dashboard)
        ctrl_frame.pack(fill="x", pady=10)

        self.btn_start = ctk.CTkButton(ctrl_frame, text="▶ START AI ENGINE", fg_color="green", command=self.start_trading_loop)
        self.btn_start.pack(side="left", padx=10, pady=10)

        self.btn_stop = ctk.CTkButton(ctrl_frame, text="⏹ STOP", fg_color="red", state="disabled", command=self.stop_trading_loop)
        self.btn_stop.pack(side="left", padx=10, pady=10)

        self.btn_chart = ctk.CTkButton(ctrl_frame, text="📈 View Selected Chart", command=self.view_selected_chart)
        self.btn_chart.pack(side="right", padx=10, pady=10)

        # Treeview (using ttk needs styling)
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview",
                        background="#2b2b2b",
                        foreground="white",
                        fieldbackground="#2b2b2b",
                        rowheight=30,
                        font=("Arial", 11))
        style.configure("Treeview.Heading", background="#1f1f1f", foreground="white", font=("Arial", 12, "bold"))
        style.map("Treeview", background=[("selected", "#1f538d")])

        cols = ("Symbol", "Price", "Trend", "MACD", "RSI", "Status", "Signal", "Time")
        self.tree = ttk.Treeview(self.frame_dashboard, columns=cols, show="headings", height=15)

        for col in cols:
            self.tree.heading(col, text=col)
            width = 250 if col == "Status" else 100
            self.tree.column(col, width=width, anchor="center")

        self.tree.pack(fill="both", expand=True, pady=10)

        # Log
        self.log_box = ctk.CTkTextbox(self.frame_dashboard, height=150, font=("Consolas", 12))
        self.log_box.pack(fill="x", pady=10)
        self.log_box.configure(state="disabled")

    def _build_config(self):
        # Telegram
        f_tg = ctk.CTkFrame(self.frame_config)
        f_tg.pack(fill="x", pady=10)

        ctk.CTkLabel(f_tg, text="Telegram Settings", font=("Arial", 16, "bold")).pack(pady=10)

        self.entry_token = ctk.CTkEntry(f_tg, placeholder_text="Bot Token", width=400)
        self.entry_token.pack(pady=5)

        self.entry_chat = ctk.CTkEntry(f_tg, placeholder_text="Chat ID", width=400)
        self.entry_chat.pack(pady=5)

        btn_row = ctk.CTkFrame(f_tg, fg_color="transparent")
        btn_row.pack(pady=10)

        ctk.CTkButton(btn_row, text="Save & Connect", command=self.save_settings).pack(side="left", padx=5)
        ctk.CTkButton(btn_row, text="Force Test Signal", command=self.force_test_signal).pack(side="left", padx=5)

        # Assets
        f_asset = ctk.CTkFrame(self.frame_config)
        f_asset.pack(fill="x", pady=10)

        ctk.CTkLabel(f_asset, text="Asset Management", font=("Arial", 16, "bold")).pack(pady=10)

        ctk.CTkButton(f_asset, text="Add New Asset", command=self.add_asset_dialog).pack(side="left", padx=20, pady=20)
        ctk.CTkButton(f_asset, text="Remove Selected", command=self.remove_asset_dialog, fg_color="red").pack(side="left", padx=20, pady=20)

    def log(self, message):
        t = datetime.now().strftime("%H:%M:%S")
        msg = f"[{t}] {message}\n"
        self.log_box.configure(state="normal")
        self.log_box.insert("end", msg)
        self.log_box.see("end")
        self.log_box.configure(state="disabled")

    def start_trading_loop(self):
        self.running = True
        self.btn_start.configure(state="disabled")
        self.btn_stop.configure(state="normal")
        self.lbl_status.configure(text="STATUS: ONLINE 🟢", text_color="green")
        self.log("AI Engine Started (Dual-Loop Mode).")
        threading.Thread(target=self._run_loop, daemon=True).start()

    def stop_trading_loop(self):
        self.running = False
        self.btn_start.configure(state="normal")
        self.btn_stop.configure(state="disabled")
        self.lbl_status.configure(text="STATUS: OFFLINE 🔴", text_color="red")
        self.log("AI Engine Stopped.")

    def _run_loop(self):
        """
        Dual-Rate Loop Implementation:
        - Fast Loop: Fetches current price every cycle (improves UI responsiveness).
        - Slow Loop: Fetches full history & analyzes signals every 60s.
        """
        while self.running:
            assets = list(self.feed.assets.keys())

            for asset in assets:
                if not self.running: break

                # Check if we need heavy analysis (Slow Loop)
                last_time = self.last_analysis_time.get(asset, 0)
                current_time = time.time()

                if current_time - last_time > 60: # 60 Seconds Interval for Analysis
                    self._perform_heavy_analysis(asset)
                    self.last_analysis_time[asset] = current_time
                else:
                    # Fast Loop: Just update price
                    self._perform_fast_price_update(asset)

                # Short sleep between assets to prevent freezing UI thread if using main thread (but we are in thread)
                # We still sleep to avoid hitting API rate limits too hard
                time.sleep(0.5)

            # Small pause between full cycles, but much shorter than before
            # We want to loop back to the first asset relatively quickly
            for _ in range(5): # 5 seconds pause instead of 20
                if not self.running: break
                time.sleep(1)

    def _perform_fast_price_update(self, asset):
        try:
            # 1. Fetch LIVE Price only (Fast)
            price, source = self.feed.get_live_price(asset)

            if price is not None:
                # Update UI Price Column only
                self.after(0, self._update_price_only, asset, price, source)

        except Exception as e:
            pass # Silent fail on fast path

    def _perform_heavy_analysis(self, asset):
        try:
            # 1. Fetch Full History (Slow)
            df, source = self.feed.fetch_history(asset, days=300)

            # Update Status Indicator
            if source == "SIM":
                self.after(0, lambda: self.lbl_status.configure(text="STATUS: SIMULATION ⚠", text_color="orange"))
            elif source == "LIVE" and self.running:
                    self.after(0, lambda: self.lbl_status.configure(text="STATUS: ONLINE 🟢", text_color="green"))

            analyzed = self.analyzer.analyze(df)

            # Store for chart viewing
            self.latest_analysis_data[asset] = analyzed

            signal = self.analyzer.generate_signal(analyzed, asset)
            latest = analyzed.iloc[-1]

            # Determine Trend String
            if latest['Close'] > latest['EMA_50']:
                trend = "UP ↗"
            else:
                trend = "DOWN ↘"

            # Update UI (Full Row)
            self.after(0, self._update_row, asset, latest, trend, signal, source)

            # Handle Signal
            if signal['Type'] in ['BUY', 'SELL']:
                    last_sig = self.last_signals.get(asset)
                    if signal['Type'] != last_sig:
                        self.log(f"🔥 SIGNAL: {asset} -> {signal['Type']}")

                        # Generate Visuals
                        chart_path = self.viz.generate_chart(analyzed, asset)

                        if self.notifier:
                            # Send signal with Source warning if needed
                            if source == "SIM":
                                signal['Reason'] += " (SIMULATED DATA)"
                            self.notifier.send_vip_signal(signal, image_path=chart_path)

                        self.last_signals[asset] = signal['Type']

        except Exception as e:
            print(f"Error Analysis {asset}: {e}")

    def _update_price_only(self, asset, price, source):
        """Updates just the price column to keep it looking 'live'."""
        if self.tree.exists(asset):
            # We need to get current values to preserve other columns
            current_values = list(self.tree.item(asset, "values"))
            if len(current_values) > 1:
                current_values[1] = f"${price:,.2f}" # Update Price
                # current_values[7] = datetime.now().strftime("%H:%M") # Update Time? Maybe too distracting
                self.tree.item(asset, values=current_values)

    def _update_row(self, asset, row, trend, signal, source):
        # Format Status Text
        status_text = signal.get('Reason', 'Scan...')
        if source == "SIM":
            status_text = f"[SIM] {status_text}"
        else:
            status_text = f"[LIVE] {status_text}"

        vals = (
            asset,
            f"${row['Close']:,.2f}",
            trend,
            f"{row['MACD']:.2f}",
            f"{row['RSI']:.1f}",
            status_text,
            signal['Type'],
            datetime.now().strftime("%H:%M")
        )

        if self.tree.exists(asset):
            self.tree.item(asset, values=vals)
        else:
            self.tree.insert("", "end", iid=asset, values=vals)

    def view_selected_chart(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Warning", "Select an asset from the table first.")
            return

        asset = sel[0]
        if asset in self.latest_analysis_data:
            df = self.latest_analysis_data[asset]
            path = self.viz.generate_chart(df, asset)
            if path:
                self.log(f"Opening Chart for {asset}...")
                if platform.system() == 'Darwin':       # macOS
                    subprocess.call(('open', path))
                elif platform.system() == 'Windows':    # Windows
                    os.startfile(path)
                else:                                   # linux variants
                    subprocess.call(('xdg-open', path))
        else:
            messagebox.showinfo("Info", "No data available yet. Wait for scan.")

    # --- Config Methods ---
    def save_settings(self):
        t = self.entry_token.get()
        c = self.entry_chat.get()
        custom = {k: v for k, v in self.feed.assets.items() if k not in self.feed.default_assets}

        with open(self.config_file, 'w') as f:
            json.dump({"token": t, "chat_id": c, "custom_assets": custom}, f)

        self.notifier = TelegramNotifier(t, c)
        self.log("Settings Saved & Telegram Connected.")
        messagebox.showinfo("Success", "Settings Saved")

    def load_settings(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file) as f:
                    cfg = json.load(f)
                    self.entry_token.insert(0, cfg.get("token", ""))
                    self.entry_chat.insert(0, cfg.get("chat_id", ""))

                    if cfg.get("token"):
                        self.notifier = TelegramNotifier(cfg["token"], cfg["chat_id"])

                    cust = cfg.get("custom_assets", {})
                    self.feed.assets.update(cust)

                # Init Tree
                for asset in self.feed.assets:
                    self.tree.insert("", "end", iid=asset, values=(asset, "...", "...", "...", "...", "Init...", "WAIT", "-"))
            except Exception as e:
                self.log(f"Config Load Error: {e}")

    def add_asset_dialog(self):
        name = simpledialog.askstring("Add", "Asset Name (e.g. Bonk):")
        if not name: return
        ticker = simpledialog.askstring("Add", "Yahoo Ticker (e.g. BONK-USD):")
        if not ticker: return
        self.feed.add_asset(name, ticker)
        self.tree.insert("", "end", iid=name, values=(name, "...", "...", "...", "...", "Added", "WAIT", "-"))
        self.log(f"Added {name}")

    def remove_asset_dialog(self):
        sel = self.tree.selection()
        if not sel: return
        asset = sel[0]
        self.feed.remove_asset(asset)
        self.tree.delete(asset)
        self.log(f"Removed {asset}")

    def force_test_signal(self):
        if not self.notifier:
            messagebox.showerror("Error", "Save Telegram Settings first.")
            return

        dummy = {
            "Symbol": "TEST-COIN",
            "Type": "BUY",
            "Entry": 100.00,
            "StopLoss": 90.00,
            "TP1": 110, "TP2": 120, "TP3": 150,
            "RiskLevel": "Low",
            "Reason": "Manual Test Request",
            "RSI": 50
        }
        # Create a dummy chart for test
        self.log("Sending Test Signal...")
        self.notifier.send_vip_signal(dummy) # No image for simple test
        messagebox.showinfo("Sent", "Test signal sent!")

if __name__ == "__main__":
    app = TradingApp()
    app.mainloop()
