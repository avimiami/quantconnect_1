import pandas as pd
import numpy as np
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from utils.indicators import Indicators

class ExitTrailingStop:
    def __init__(self, atr_period=14, atr_multiplier=2.0):
        self.name = "Trailing Stop Exit"
        self.atr_period = atr_period
        self.atr_multiplier = atr_multiplier
        self.tags = ["risk_management", "trend_following"]
    
    def generate_signal(self, df, entry_price=None):
        """Generate exit signals based on trailing stop"""
        # Make a copy to avoid modifying the original
        df = df.copy()
        
        # Add ATR indicator
        df = Indicators.add_atr(df, period=self.atr_period)
        
        # Calculate trailing stop levels
        df['stop_distance'] = df['ATR'] * self.atr_multiplier
        
        # For long positions
        df['trailing_stop_long'] = df['close'].rolling(window=len(df), min_periods=1).max() - df['stop_distance']
        
        # For short positions
        df['trailing_stop_short'] = df['close'].rolling(window=len(df), min_periods=1).min() + df['stop_distance']
        
        # Generate exit signals
        df['exit_long'] = (df['close'] < df['trailing_stop_long']).astype(int)
        df['exit_short'] = (df['close'] > df['trailing_stop_short']).astype(int)
        
        return df
    
    def get_latest_signal(self, df, position_type="long", entry_price=None):
        """Get the latest signal from the dataframe"""
        df = self.generate_signal(df, entry_price)
        latest = df.iloc[-1]
        
        if position_type.lower() == "long":
            exit_signal = bool(latest['exit_long'])
            stop_level = latest['trailing_stop_long']
        else:  # short
            exit_signal = bool(latest['exit_short'])
            stop_level = latest['trailing_stop_short']
        
        return {
            "exit_signal": exit_signal,
            "stop_level": stop_level,
            "indicators": {
                "ATR": latest['ATR'],
                "stop_distance": latest['stop_distance']
            }
        }