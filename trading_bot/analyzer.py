import pandas as pd
import numpy as np

class MarketAnalyzer:
    def __init__(self):
        pass

    def calculate_rsi(self, series, period=14):
        """
        Calculates the Relative Strength Index (RSI).
        """
        delta = series.diff()
        gain = (delta.where(delta > 0, 0))
        loss = (-delta.where(delta < 0, 0))

        # Wilder's Smoothing (standard for RSI)
        avg_gain = gain.ewm(com=period - 1, min_periods=period).mean()
        avg_loss = loss.ewm(com=period - 1, min_periods=period).mean()

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    def analyze(self, df):
        """
        Adds technical indicators to the DataFrame.

        Args:
            df (pd.DataFrame): DataFrame with 'Close' column.

        Returns:
            pd.DataFrame: DataFrame with added indicator columns.
        """
        df = df.copy()

        # 1. Moving Averages
        df['SMA_7'] = df['Close'].rolling(window=7).mean()
        df['SMA_30'] = df['Close'].rolling(window=30).mean()

        # 2. RSI (Momentum)
        df['RSI'] = self.calculate_rsi(df['Close'])

        # 3. Daily Returns
        df['Daily_Return'] = df['Close'].pct_change()

        # 4. Volatility (Rolling standard deviation of returns, annualized)
        # We use a 7-day rolling window for short-term volatility perception
        df['Volatility'] = df['Daily_Return'].rolling(window=7).std() * np.sqrt(365)

        # Fill NaN values (optional, but good for clean output,
        # though strategies usually just skip NaN rows)
        # df.fillna(0, inplace=True)

        return df

if __name__ == "__main__":
    # Test the analyzer
    from market_sim import MarketSimulator

    sim = MarketSimulator()
    df = sim.generate_data(60)

    analyzer = MarketAnalyzer()
    analyzed_df = analyzer.analyze(df)

    print(analyzed_df[['Date', 'Close', 'SMA_7', 'SMA_30', 'RSI']].tail(10))
