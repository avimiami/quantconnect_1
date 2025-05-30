import pandas as pd
import numpy as np
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from utils.indicators import Indicators

class MovingAverageCrossover:
    def __init__(self, fast_period=20, slow_period=50):
        self.name = "Moving Average Crossover"
        self.fast_period = fast_period
        self.slow_period = slow_period
        self.tags = ["momentum", "trend_following"]
    
    def generate_signal(self, df):
        """Generate entry signals based on MA crossover"""
        # Make a copy to avoid modifying the original
        df = df.copy()
        
        # Add indicators
        df = Indicators.add_sma(df, period=self.fast_period)
        df = Indicators.add_sma(df, period=self.slow_period)
        
        # Calculate crossover
        df['signal'] = 0
        df.loc[df[f'SMA_{self.fast_period}'] > df[f'SMA_{self.slow_period}'], 'signal'] = 1
        df.loc[df[f'SMA_{self.fast_period}'] < df[f'SMA_{self.slow_period}'], 'signal'] = -1
        
        # Generate entry signals on crossover
        df['entry_signal'] = df['signal'].diff().fillna(0)
        df['entry_long'] = (df['entry_signal'] > 0).astype(int)
        df['entry_short'] = (df['entry_signal'] < 0).astype(int)
        
        return df
    
    def get_latest_signal(self, df):
        """Get the latest signal from the dataframe"""
        df = self.generate_signal(df)
        latest = df.iloc[-1]
        
        return {
            "entry_long": bool(latest['entry_long']),
            "entry_short": bool(latest['entry_short']),
            "current_position": int(latest['signal']),
            "indicators": {
                f"SMA_{self.fast_period}": latest[f'SMA_{self.fast_period}'],
                f"SMA_{self.slow_period}": latest[f'SMA_{self.slow_period}']
            }
        }