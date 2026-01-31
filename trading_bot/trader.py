import pandas as pd
from datetime import datetime

class TradingEngine:
    def __init__(self, initial_cash=10000.0, notifier=None):
        self.initial_cash = initial_cash
        self.cash = initial_cash
        self.holdings = 0.0
        self.notifier = notifier
        self.ledger = []
        self.entry_price = 0.0
        self.stop_loss_pct = 0.05
        self.take_profit_pct = 0.10

    def run_backtest(self, df):
        """
        Runs the trading strategy on the provided DataFrame.
        """
        # Ensure data is sorted
        df = df.sort_values('Date').reset_index(drop=True)

        for i in range(1, len(df)):
            curr = df.iloc[i]
            prev = df.iloc[i-1]

            date = curr['Date']
            price = curr['Close']
            high = curr['High']
            low = curr['Low']

            signal = "-"
            action = "-"

            # Portfolio Value (before today's action)
            portfolio_value = self.cash + (self.holdings * price)

            # --- Logic ---

            # 1. Check if we are Holding
            if self.holdings > 0:
                # Check Risk Management (SL/TP) - Intraday
                sl_price = self.entry_price * (1 - self.stop_loss_pct)
                tp_price = self.entry_price * (1 + self.take_profit_pct)

                executed_sell = False
                sell_reason = ""
                sell_price = price

                if low <= sl_price:
                    # Stop Loss Hit
                    sell_price = sl_price
                    sell_reason = "Stop Loss (حد ضرر)"
                    executed_sell = True
                elif high >= tp_price:
                    # Take Profit Hit
                    sell_price = tp_price
                    sell_reason = "Take Profit (سود)"
                    executed_sell = True

                # Check Trend Sell Signal (Death Cross)
                # SMA7 crosses below SMA30
                elif (prev['SMA_7'] >= prev['SMA_30']) and (curr['SMA_7'] < curr['SMA_30']):
                    sell_price = price
                    sell_reason = "Death Cross (تقاطع مرگ)"
                    executed_sell = True

                if executed_sell:
                    # Execute Sell
                    revenue = self.holdings * sell_price
                    self.cash += revenue
                    self.holdings = 0
                    self.entry_price = 0

                    signal = "SELL"
                    action = f"Sold at {sell_price:.2f} ({sell_reason})"

                    if self.notifier:
                        self.notifier.send_signal(f"🔴 **فروش (SELL)**\nقیمت: {sell_price:.2f}\nدلیل: {sell_reason}\nتاریخ: {date}")

            # 2. Check if we can Buy (only if not holding)
            # We use 'elif' because if we sold today, we usually don't buy back immediately in this simple logic
            elif self.holdings == 0:
                # Buy Signal: Golden Cross + Momentum (RSI > 50)
                # SMA7 crosses above SMA30
                bullish_cross = (prev['SMA_7'] <= prev['SMA_30']) and (curr['SMA_7'] > curr['SMA_30'])
                momentum = curr['RSI'] > 50

                if bullish_cross and momentum:
                    # Execute Buy
                    buy_price = price
                    amount_to_buy = self.cash / buy_price
                    self.holdings = amount_to_buy
                    self.cash = 0
                    self.entry_price = buy_price

                    signal = "BUY"
                    action = f"Bought at {buy_price:.2f}"

                    if self.notifier:
                        self.notifier.send_signal(f"🟢 **خرید (BUY)**\nقیمت: {buy_price:.2f}\nمومنتوم: RSI {curr['RSI']:.1f}\nتاریخ: {date}")

            # Update Portfolio Value after action
            portfolio_value = self.cash + (self.holdings * price)

            # Log Daily State
            self.ledger.append({
                "Date": date,
                "Price": price,
                "Signal": signal,
                "Action": action,
                "Holdings": self.holdings,
                "Cash": self.cash,
                "Portfolio Value": portfolio_value
            })

        return pd.DataFrame(self.ledger)

    def calculate_performance(self):
        if not self.ledger:
            return {}

        df_ledger = pd.DataFrame(self.ledger)
        initial_val = self.initial_cash
        final_val = df_ledger.iloc[-1]['Portfolio Value']

        total_return_pct = ((final_val - initial_val) / initial_val) * 100

        trades = df_ledger[df_ledger['Signal'].isin(['BUY', 'SELL'])]
        num_trades = len(trades) // 2  # Approximate round trips

        # Calculate Win Rate
        # We need to look at each SELL and compare portfolio value before vs after the trade cycle
        # This is a bit tricky with just a ledger, simplified approach:
        # Check if the SELL was profitable (Price > Buy Price).
        # But we don't store Buy Price easily in the ledger row for the SELL.
        # We can scan the 'Action' column or track PnL per trade.

        win_count = 0
        if num_trades > 0:
            # Extract SELL actions which contain the reason
            sell_actions = df_ledger[df_ledger['Signal'] == 'SELL']['Action']
            for action in sell_actions:
                if "Take Profit" in action:
                    win_count += 1
                elif "Stop Loss" in action:
                    pass # Loss
                elif "Death Cross" in action:
                    # Need to check price vs entry.
                    # Since we don't have easy linking here, we'll approximate:
                    # If the sell price > entry price (which we don't have right here easily without re-parsing).
                    # For this prototype, let's assume Death Cross is usually a small loss or small win.
                    # A better way is to track PnL in the loop.
                    # Let's fix the loop to track trade results if we want accuracy.
                    pass

        # RE-IMPLEMENTING PERFORMANCE METRICS TO BE ACCURATE
        # Let's count wins based on portfolio value changes on SELL days vs the last BUY day.
        buy_val = 0
        wins = 0
        completed_trades = 0

        for index, row in df_ledger.iterrows():
            if row['Signal'] == 'BUY':
                buy_val = row['Portfolio Value'] # Cash turns into holdings
            elif row['Signal'] == 'SELL':
                sell_val = row['Portfolio Value'] # Holdings turn into cash
                if sell_val > buy_val:
                    wins += 1
                completed_trades += 1

        win_rate = (wins / completed_trades * 100) if completed_trades > 0 else 0.0

        # Max Drawdown
        df_ledger['Peak'] = df_ledger['Portfolio Value'].cummax()
        df_ledger['Drawdown'] = (df_ledger['Portfolio Value'] - df_ledger['Peak']) / df_ledger['Peak']
        max_drawdown_pct = df_ledger['Drawdown'].min() * 100

        return {
            "Total Return": total_return_pct,
            "Total Trades": num_trades,
            "Win Rate": win_rate,
            "Max Drawdown": max_drawdown_pct,
            "Final Value": final_val
        }

if __name__ == "__main__":
    # Test
    from market_sim import MarketSimulator
    from analyzer import MarketAnalyzer

    sim = MarketSimulator(volatility=0.8) # High volatility to trigger signals
    df = sim.generate_data(100)
    analyzer = MarketAnalyzer()
    df = analyzer.analyze(df)

    trader = TradingEngine()
    ledger = trader.run_backtest(df)
    print(ledger[['Date', 'Price', 'Signal', 'Action']].tail(10))
    print(trader.calculate_performance())
