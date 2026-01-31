import numpy as np
import pandas as pd
from datetime import datetime, timedelta

class MarketSimulator:
    def __init__(self, start_price=65000.0, volatility=0.8, drift=0.1):
        """
        Initialize the Market Simulator.

        Args:
            start_price (float): Initial price of the asset (e.g., Bitcoin).
            volatility (float): Annualized volatility (e.g., 0.8 for 80%).
            drift (float): Annualized drift (expected return, e.g., 0.1 for 10%).
        """
        self.start_price = start_price
        self.volatility = volatility
        self.drift = drift

    def generate_data(self, days=60):
        """
        Generates synthetic OHLC data using Geometric Brownian Motion.

        Args:
            days (int): Number of days to simulate.

        Returns:
            pd.DataFrame: DataFrame containing 'Date', 'Open', 'High', 'Low', 'Close'.
        """
        dt = 1 / 365.0  # Time step in years
        prices = [self.start_price]
        dates = [datetime.now() - timedelta(days=days - i) for i in range(days)]

        # Generate daily Close prices
        for _ in range(1, days):
            prev_price = prices[-1]
            shock = np.random.normal(0, 1)
            # Geometric Brownian Motion formula
            change = (self.drift - 0.5 * self.volatility**2) * dt + \
                     self.volatility * np.sqrt(dt) * shock
            price = prev_price * np.exp(change)
            prices.append(price)

        # Create DataFrame
        df = pd.DataFrame({'Date': dates, 'Close': prices})
        df['Date'] = df['Date'].dt.date

        # Generate Open, High, Low based on Close
        # Open is usually the previous Close (simplified)
        df['Open'] = df['Close'].shift(1)
        df.loc[0, 'Open'] = self.start_price  # First day open

        # Simulate High and Low
        # We assume High is some percentage above Max(Open, Close)
        # and Low is some percentage below Min(Open, Close)
        # Random noise proportional to daily volatility
        daily_vol = self.volatility * np.sqrt(dt)

        # Vectorized generation of High/Low
        high_noise = np.abs(np.random.normal(0, daily_vol/2, days))
        low_noise = np.abs(np.random.normal(0, daily_vol/2, days))

        df['High'] = df[['Open', 'Close']].max(axis=1) * (1 + high_noise)
        df['Low'] = df[['Open', 'Close']].min(axis=1) * (1 - low_noise)

        # Reorder columns
        return df[['Date', 'Open', 'High', 'Low', 'Close']]

if __name__ == "__main__":
    # Test the simulator
    sim = MarketSimulator()
    df = sim.generate_data(60)
    print(df.head())
    print(df.tail())
