import pandas as pd
import numpy as np

class Indicators:
    @staticmethod
    def add_sma(df, period=50, column='close'):
        """Add Simple Moving Average"""
        df = df.copy()
        df[f'SMA_{period}'] = df[column].rolling(window=period).mean()
        return df
    
    @staticmethod
    def add_ema(df, period=20, column='close'):
        """Add Exponential Moving Average"""
        df = df.copy()
        df[f'EMA_{period}'] = df[column].ewm(span=period, adjust=False).mean()
        return df
    
    @staticmethod
    def add_macd(df, fast=12, slow=26, signal=9, column='close'):
        """Add MACD (Moving Average Convergence Divergence)"""
        df = df.copy()
        # Calculate MACD line
        df['EMA_fast'] = df[column].ewm(span=fast, adjust=False).mean()
        df['EMA_slow'] = df[column].ewm(span=slow, adjust=False).mean()
        df['MACD'] = df['EMA_fast'] - df['EMA_slow']
        
        # Calculate Signal line
        df['MACD_signal'] = df['MACD'].ewm(span=signal, adjust=False).mean()
        
        # Calculate Histogram
        df['MACD_hist'] = df['MACD'] - df['MACD_signal']
        
        # Clean up
        df.drop(['EMA_fast', 'EMA_slow'], axis=1, inplace=True)
        
        return df
    
    @staticmethod
    def add_rsi(df, period=14, column='close'):
        """Add Relative Strength Index"""
        df = df.copy()
        delta = df[column].diff()
        
        # Make two series: one for gains and one for losses
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        
        # Calculate average gain and loss
        avg_gain = gain.rolling(window=period).mean()
        avg_loss = loss.rolling(window=period).mean()
        
        # Calculate RS (Relative Strength)
        rs = avg_gain / avg_loss
        
        # Calculate RSI
        df['RSI'] = 100 - (100 / (1 + rs))
        
        return df
    
    @staticmethod
    def add_bollinger_bands(df, period=20, std_dev=2, column='close'):
        """Add Bollinger Bands"""
        df = df.copy()
        df['BB_middle'] = df[column].rolling(window=period).mean()
        df['BB_std'] = df[column].rolling(window=period).std()
        df['BB_upper'] = df['BB_middle'] + (df['BB_std'] * std_dev)
        df['BB_lower'] = df['BB_middle'] - (df['BB_std'] * std_dev)
        
        # Clean up
        df.drop(['BB_std'], axis=1, inplace=True)
        
        return df
    
    @staticmethod
    def add_atr(df, period=14):
        """Add Average True Range"""
        df = df.copy()
        df['tr0'] = abs(df['high'] - df['low'])
        df['tr1'] = abs(df['high'] - df['close'].shift())
        df['tr2'] = abs(df['low'] - df['close'].shift())
        df['tr'] = df[['tr0', 'tr1', 'tr2']].max(axis=1)
        df['ATR'] = df['tr'].rolling(window=period).mean()
        
        # Clean up
        df.drop(['tr0', 'tr1', 'tr2', 'tr'], axis=1, inplace=True)
        
        return df