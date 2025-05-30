import pandas as pd
import numpy as np
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from utils.stats import compute_drawdown

class ExitDrawdownLimit:
    def __init__(self, max_drawdown=-0.05):
        self.name = "Drawdown Limit Exit"
        self.max_drawdown = max_drawdown  # -0.05 means 5% drawdown
        self.tags = ["risk_management", "position_management"]
    
    def generate_signal(self, df, entry_price=None):
        """Generate exit signals based on maximum drawdown threshold"""
        # Make a copy to avoid modifying the original
        df = df.copy()
        
        if entry_price is not None:
            # Calculate drawdown from entry price
            df['entry_price'] = entry_price
            df['drawdown_from_entry'] = (df['close'] / entry_price) - 1
            
            # Generate exit signals when drawdown exceeds threshold
            df['exit_long'] = (df['drawdown_from_entry'] <= self.max_drawdown).astype(int)
            df['exit_short'] = (df['drawdown_from_entry'] >= -self.max_drawdown).astype(int)
        else:
            # Calculate rolling drawdown if no entry price is provided
            df['cum_max'] = df['close'].cummax()
            df['cum_min'] = df['close'].cummin()
            
            # Calculate drawdown for long and short positions
            df['drawdown_long'] = (df['close'] / df['cum_max']) - 1
            df['drawdown_short'] = (df['close'] / df['cum_min']) - 1
            
            # Generate exit signals when drawdown exceeds threshold
            df['exit_long'] = (df['drawdown_long'] <= self.max_drawdown).astype(int)
            df['exit_short'] = (df['drawdown_short'] >= -self.max_drawdown).astype(int)
        
        return df
    
    def get_latest_signal(self, df, position_type="long", entry_price=None):
        """Get the latest signal from the dataframe"""
        df = self.generate_signal(df, entry_price)
        latest = df.iloc[-1]
        
        if position_type.lower() == "long":
            exit_signal = bool(latest['exit_long'])
            if entry_price is not None:
                current_drawdown = latest['drawdown_from_entry']
            else:
                current_drawdown = latest['drawdown_long']
        else:  # short
            exit_signal = bool(latest['exit_short'])
            if entry_price is not None:
                current_drawdown = -latest['drawdown_from_entry']
            else:
                current_drawdown = latest['drawdown_short']
        
        return {
            "exit_signal": exit_signal,
            "current_drawdown": current_drawdown,
            "max_drawdown_limit": self.max_drawdown
        }