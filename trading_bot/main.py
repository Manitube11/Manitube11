import tkinter as tk
import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from gui_app import TradingApp

def main():
    try:
        root = tk.Tk()
        # Set icon if available (optional)
        # root.iconbitmap('icon.ico')
        app = TradingApp(root)
        root.mainloop()
    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()
