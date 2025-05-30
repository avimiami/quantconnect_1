import pandas as pd
import numpy as np
import sys
import os
import requests
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from utils.indicators import Indicators

class ValueEntry:
    def __init__(self, pe_threshold=20, pb_threshold=3):
        self.name = "Value Entry"
        self.pe_threshold = pe_threshold
        self.pb_threshold = pb_threshold
        self.tags = ["value", "fundamental"]
        self.fundamental_data = {}
    
    def _get_fundamental_data(self, symbol):
        """Placeholder for getting fundamental data
        In a real implementation, this would fetch data from a financial API
        """
        # This is a simplified mock implementation
        # In a real scenario, you would use an API like Tiingo Premium, Alpha Vantage, or IEX Cloud
        # to fetch actual fundamental data
        
        # For demonstration purposes, we'll use mock data
        # In production, replace this with actual API calls
        
        # Check if we already have data for this symbol
        if symbol in self.fundamental_data and (datetime.now() - self.fundamental_data[symbol]['timestamp']).days < 1:
            return self.fundamental_data[symbol]
        
        # Mock data - in production, replace with API call
        mock_data = {
            'AAPL': {'pe_ratio': 28.5, 'pb_ratio': 35.2},
            'XLF': {'pe_ratio': 15.2, 'pb_ratio': 1.8},
            'SPY': {'pe_ratio': 22.1, 'pb_ratio': 4.2},
            # Add more symbols as needed
        }
        
        # Default values if symbol not in mock data
        result = mock_data.get(symbol, {'pe_ratio': 25.0, 'pb_ratio': 3.0})
        result['timestamp'] = datetime.now()
        
        # Cache the result
        self.fundamental_data[symbol] = result
        
        return result
    
    def generate_signal(self, df, symbol):
        """Generate entry signals based on value metrics"""
        # Make a copy to avoid modifying the original
        df = df.copy()
        
        # Get fundamental data
        fundamentals = self._get_fundamental_data(symbol)
        
        # Create columns for fundamental data
        df['pe_ratio'] = fundamentals['pe_ratio']
        df['pb_ratio'] = fundamentals['pb_ratio']
        
        # Generate entry signals based on value thresholds
        df['value_signal'] = 0
        df.loc[(df['pe_ratio'] < self.pe_threshold) & 
               (df['pb_ratio'] < self.pb_threshold), 'value_signal'] = 1
        
        # Generate entry signals on value crossover
        df['entry_signal'] = df['value_signal'].diff().fillna(0)
        df['entry_long'] = (df['entry_signal'] > 0).astype(int)
        df['entry_short'] = 0  # This strategy only generates long entries
        
        return df
    
    def get_latest_signal(self, df, symbol):
        """Get the latest signal from the dataframe"""
        df = self.generate_signal(df, symbol)
        latest = df.iloc[-1]
        
        fundamentals = self._get_fundamental_data(symbol)
        
        return {
            "entry_long": bool(latest['entry_long']),
            "entry_short": bool(latest['entry_short']),
            "current_position": int(latest['value_signal']),
            "indicators": {
                "pe_ratio": fundamentals['pe_ratio'],
                "pb_ratio": fundamentals['pb_ratio']
            }
        }