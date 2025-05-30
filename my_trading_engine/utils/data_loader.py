import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import requests
from tiingo import TiingoClient
from dotenv import load_dotenv
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import API_CONFIG

load_dotenv()  # Load environment variables from .env file if present

class DataLoader:
    def __init__(self, api_key=None, data_source=None):
        self.api_key = api_key or os.getenv("TIINGO_API_KEY") or API_CONFIG.get("tiingo_api_key")
        self.data_source = data_source or API_CONFIG.get("data_source", "tiingo")
        
        if self.data_source == "tiingo":
            self._init_tiingo()
    
    def _init_tiingo(self):
        if not self.api_key:
            raise ValueError("Tiingo API key is required. Set it in config.py or as an environment variable.")
            
        self.client = TiingoClient({"api_key": self.api_key})
    
    def get_historical_data(self, symbol, start_date=None, end_date=None, timeframe="daily"):
        """Get historical price data for a symbol"""
        if not end_date:
            end_date = datetime.now().strftime("%Y-%m-%d")
        
        if not start_date:
            # Default to 1 year of data
            start_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
        
        if self.data_source == "tiingo":
            return self._get_tiingo_data(symbol, start_date, end_date, timeframe)
        else:
            raise NotImplementedError(f"Data source {self.data_source} not implemented")
    
    def _get_tiingo_data(self, symbol, start_date, end_date, timeframe):
        """Get data from Tiingo API"""
        try:
            if timeframe == "daily":
                data = self.client.get_ticker_price(
                    ticker=symbol,
                    fmt='json',
                    startDate=start_date,
                    endDate=end_date,
                    frequency='daily'
                )
            else:
                # For intraday data (requires premium Tiingo subscription)
                raise NotImplementedError(f"Timeframe {timeframe} not implemented for Tiingo")
                
            # Convert to DataFrame
            df = pd.DataFrame(data)
            
            # Rename columns to standardized format
            df = df.rename(columns={
                'date': 'date',
                'open': 'open',
                'high': 'high',
                'low': 'low',
                'close': 'close',
                'volume': 'volume',
                'adjOpen': 'adj_open',
                'adjHigh': 'adj_high',
                'adjLow': 'adj_low',
                'adjClose': 'adj_close',
                'adjVolume': 'adj_volume'
            })
            
            # Set date as index
            df['date'] = pd.to_datetime(df['date'])
            df.set_index('date', inplace=True)
            
            return df
            
        except Exception as e:
            print(f"Error fetching data for {symbol}: {str(e)}")
            return pd.DataFrame()
    
    def get_multiple_symbols(self, symbols, start_date=None, end_date=None, timeframe="daily"):
        """Get historical data for multiple symbols"""
        data = {}
        for symbol in symbols:
            symbol_data = self.get_historical_data(
                symbol=symbol if isinstance(symbol, str) else symbol["symbol"],
                start_date=start_date,
                end_date=end_date,
                timeframe=timeframe
            )
            if not symbol_data.empty:
                data[symbol if isinstance(symbol, str) else symbol["symbol"]] = symbol_data
        
        return data