import pandas as pd
import numpy as np
import sys
import os
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

class ExitRebalanceDate:
    def __init__(self, rebalance_freq='monthly', specific_dates=None):
        self.name = "Rebalance Date Exit"
        self.rebalance_freq = rebalance_freq.lower()  # 'monthly', 'quarterly', 'yearly'
        self.specific_dates = specific_dates  # List of specific dates for rebalancing
        self.tags = ["portfolio_management", "systematic"]
    
    def _is_rebalance_date(self, date):
        """Check if the given date is a rebalance date"""
        # If specific dates are provided, check against those
        if self.specific_dates is not None:
            for rebal_date in self.specific_dates:
                if isinstance(rebal_date, str):
                    rebal_date = pd.Timestamp(rebal_date)
                if date.date() == rebal_date.date():
                    return True
            return False
        
        # Otherwise, use frequency-based rebalancing
        if self.rebalance_freq == 'monthly':
            # Last trading day of the month
            next_month = date.replace(day=28) + pd.DateOffset(days=4)
            last_day = next_month - pd.DateOffset(days=next_month.day)
            return date.date() == last_day.date()
        
        elif self.rebalance_freq == 'quarterly':
            # Last trading day of the quarter
            if date.month in [3, 6, 9, 12] and date.day >= 28:
                next_month = date.replace(day=28) + pd.DateOffset(days=4)
                last_day = next_month - pd.DateOffset(days=next_month.day)
                return date.date() == last_day.date()
            return False
        
        elif self.rebalance_freq == 'yearly':
            # Last trading day of the year
            return date.month == 12 and date.day >= 28 and date.day == date.days_in_month
        
        return False
    
    def generate_signal(self, df):
        """Generate exit signals based on rebalance dates"""
        # Make a copy to avoid modifying the original
        df = df.copy()
        
        # Check each date for rebalancing
        df['rebalance_day'] = df.index.map(self._is_rebalance_date)
        
        # Generate exit signals on rebalance days
        df['exit_long'] = df['rebalance_day'].astype(int)
        df['exit_short'] = df['rebalance_day'].astype(int)
        
        return df
    
    def get_latest_signal(self, df, position_type="long"):
        """Get the latest signal from the dataframe"""
        df = self.generate_signal(df)
        latest = df.iloc[-1]
        
        exit_signal = bool(latest['rebalance_day'])
        
        # Calculate days until next rebalance (simplified)
        today = pd.Timestamp.now().normalize()
        days_to_rebalance = None
        
        if self.specific_dates is not None:
            # Find the next specific rebalance date
            future_dates = [d for d in self.specific_dates if pd.Timestamp(d) > today]
            if future_dates:
                next_date = min(future_dates)
                days_to_rebalance = (pd.Timestamp(next_date) - today).days
        else:
            # Estimate based on frequency (simplified)
            if self.rebalance_freq == 'monthly':
                next_month = today.replace(day=28) + pd.DateOffset(days=4)
                last_day = next_month - pd.DateOffset(days=next_month.day)
                days_to_rebalance = (last_day - today).days
            elif self.rebalance_freq == 'quarterly':
                # Find the end of the current quarter
                quarter_end_month = ((today.month - 1) // 3 + 1) * 3
                quarter_end = pd.Timestamp(today.year, quarter_end_month, 1) + pd.DateOffset(months=1, days=-1)
                days_to_rebalance = (quarter_end - today).days
            elif self.rebalance_freq == 'yearly':
                year_end = pd.Timestamp(today.year, 12, 31)
                days_to_rebalance = (year_end - today).days
        
        return {
            "exit_signal": exit_signal,
            "days_to_next_rebalance": days_to_rebalance,
            "rebalance_frequency": self.rebalance_freq
        }