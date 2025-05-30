import json
import os
import pandas as pd
from datetime import datetime

def export_portfolio(portfolio_data, output_path="../outputs/portfolio.json"):
    """Export portfolio data to JSON file"""
    # Ensure directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Convert any non-serializable objects to strings
    serializable_data = {}
    for symbol, data in portfolio_data.items():
        serializable_data[symbol] = {}
        for key, value in data.items():
            if isinstance(value, (pd.DataFrame, pd.Series)):
                serializable_data[symbol][key] = value.to_dict()
            elif isinstance(value, datetime):
                serializable_data[symbol][key] = value.isoformat()
            elif isinstance(value, (int, float, str, bool, list, dict)) or value is None:
                serializable_data[symbol][key] = value
            else:
                serializable_data[symbol][key] = str(value)
    
    # Write to file
    with open(output_path, 'w') as f:
        json.dump(serializable_data, f, indent=2)
    
    return output_path

def load_portfolio(input_path="../outputs/portfolio.json"):
    """Load portfolio data from JSON file"""
    if not os.path.exists(input_path):
        return {}
    
    with open(input_path, 'r') as f:
        data = json.load(f)
    
    return data