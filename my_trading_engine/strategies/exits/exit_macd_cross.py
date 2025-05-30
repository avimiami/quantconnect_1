import pandas as pd
import numpy as np
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from utils.indicators import Indicators

class ExitMACDCross:
    def __init__(self, fast=12, slow=26, signal=9):
        self.name = "MACD Cross Exit"
        self.fast = fast
        self.slow = slow
        self.signal = signal
        self.tags = ["momentum", "trend_following"]
    
    def generate_signal(self, df):
        """Generate exit signals based on MACD crossing signal line"""
        # Make a copy to avoid modifying the original
        df = df.copy()
        
        # Add MACD indicator
        df = Indicators.add_macd(df, fast=self.fast, slow=self.slow, signal=self.signal)
        
        # Previous values for crossover detection
        df['prev_MACD'] = df['MACD'].shift(1)
        df['prev_MACD_signal'] = df['MACD_signal'].shift(1)
        
        # Generate exit signals
        # For long positions: exit when MACD crosses below signal line
        df['exit_long'] = ((df['prev_MACD'] > df['prev_MACD_signal']) & 
                          (df['MACD'] < df['MACD_signal'])).astype(int)
        
        # For short positions: exit when MACD crosses above signal line
        df['exit_short'] = ((df['prev_MACD'] < df['prev_MACD_signal']) & 
                           (df['MACD'] > df['MACD_signal'])).astype(int)
        
        return df
    
    def get_latest_signal(self, df, position_type="long"):
        """Get the latest signal from the dataframe"""
        df = self.generate_signal(df)
        latest = df.iloc[-1]
        
        if position_type.lower() == "long":
            exit_signal = bool(latest['exit_long'])
        else:  # short
            exit_signal = bool(latest['exit_short'])
        
        return {
            "exit_signal": exit_signal,
            "indicators": {
                "MACD": latest['MACD'],
                "MACD_signal": latest['MACD_signal'],
                "MACD_hist": latest['MACD_hist']
            }
        }