import unittest
import sys
import os
import pandas as pd
import numpy as np
from unittest.mock import MagicMock, patch

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.indicators import analyze_market
from src.data_fetcher import CryptoFetcher, StockFetcher

class TestIntegration(unittest.TestCase):
    def test_indicators_logic(self):
        # Create dummy data
        df = pd.DataFrame({
            'Close': np.linspace(100, 200, 100)
        })
        result = analyze_market(df)
        self.assertIn('signal', result)
        self.assertIn('score', result)
        self.assertIn('indicators', result)
        # Check types
        self.assertIsInstance(result['score'], int)
        self.assertIsInstance(result['indicators']['RSI'], float)

    @patch('src.data_fetcher.requests.get')
    def test_crypto_fetcher(self, mock_get):
        # Mock API response
        mock_response = MagicMock()
        mock_response.json.return_value = [
            [1672531200000, 100, 110, 90, 105],
            [1672617600000, 105, 115, 95, 110]
        ]
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        fetcher = CryptoFetcher()
        df = fetcher.get_historical_data('BTC')
        self.assertFalse(df.empty)
        self.assertEqual(len(df), 2)
        self.assertIn('Close', df.columns)

    @patch('src.data_fetcher.yf.Ticker')
    def test_stock_fetcher(self, mock_ticker):
        # Mock yfinance Ticker
        mock_instance = MagicMock()
        mock_df = pd.DataFrame({
            'Open': [100], 'High': [110], 'Low': [90], 'Close': [105], 'Volume': [1000]
        }, index=pd.to_datetime(['2023-01-01']))
        mock_instance.history.return_value = mock_df
        mock_ticker.return_value = mock_instance

        fetcher = StockFetcher()
        df = fetcher.get_historical_data('AAPL')
        self.assertFalse(df.empty)
        self.assertEqual(len(df), 1)

if __name__ == '__main__':
    unittest.main()
