import sys
import os

# Ensure we can import from the same directory
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from gui_app import TradingApp

if __name__ == "__main__":
    try:
        app = TradingApp()
        app.mainloop()
    except Exception as e:
        print(f"Critical Error: {e}")
        input("Press Enter to Exit...")
