import pandas as pd
import numpy as np
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from utils.indicators import Indicators

class LowVolatilityEntry:
    def __init__(self, atr_period=14, volatility_threshold=0.02, lookback_period=20):
        self.name = "Low Volatility Entry"
        self.atr_period = atr_period
        self.volatility_threshold = volatility_threshold
        self.lookback_period = lookback_period
        self.tags = ["mean_reversion", "volatility"]
    
    def generate_signal(self, df):
        """Generate entry signals when volatility is low"""
        # Make a copy to avoid modifying the original
        df = df.copy()
        
        # Add ATR indicator for volatility measurement
        df = Indicators.add_atr(df, period=self.atr_period)
        
        # Calculate normalized ATR (ATR as percentage of price)
        df['ATR_pct'] = df['ATR'] / df['close']
        
        # Calculate rolling volatility
        df['rolling_vol'] = df['ATR_pct'].rolling(window=self.lookback_period).mean()
        
        # Generate entry signals when volatility is below threshold
        df['low_vol'] = df['rolling_vol'] < self.volatility_threshold
        
        # Only enter when volatility transitions from high to low
        df['entry_signal'] = df['low_vol'].astype(int).diff().fillna(0)
        df['entry_long'] = (df['entry_signal'] > 0).astype(int)
        df['entry_short'] = 0  # This strategy only generates long entries
        
        return df
    
    def get_latest_signal(self, df):
        """Get the latest signal from the dataframe"""
        df = self.generate_signal(df)
        latest = df.iloc[-1]
        
        return {
            "entry_long": bool(latest['entry_long']),
            "entry_short": bool(latest['entry_short']),
            "current_position": int(latest['low_vol']),
            "indicators": {
                "ATR": latest['ATR'],
                "ATR_pct": latest['ATR_pct'],
                "rolling_vol": latest['rolling_vol']
            }
        }