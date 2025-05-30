import os
import sys
import argparse
import pandas as pd
from datetime import datetime, timedelta

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import project modules
from utils.data_loader import DataLoader
from utils.json_export import export_portfolio, load_portfolio
from strategies.entries.moving_average_crossover import MovingAverageCrossover
from strategies.exits.exit_trailing_stop import ExitTrailingStop
from utils.stats import compute_returns, compute_sharpe, compute_pnl_spark, compute_total_return
from config import SYMBOLS, STRATEGY_CONFIG

def run_strategy(symbols=None, days=365, api_key=None):
    """Run the trading strategy and generate signals"""
    # Initialize data loader
    data_loader = DataLoader(api_key=api_key)
    
    # Get symbols to analyze
    if symbols is None:
        symbols = [s["symbol"] if isinstance(s, dict) else s for s in SYMBOLS]
    elif isinstance(symbols, str):
        symbols = [symbols]
    
    # Set date range
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    
    # Get historical data
    data = data_loader.get_multiple_symbols(symbols, start_date=start_date, end_date=end_date)
    
    # Initialize strategies
    entry_strategy = MovingAverageCrossover(fast_period=20, slow_period=50)
    exit_strategy = ExitTrailingStop(atr_period=14, atr_multiplier=2.0)
    
    # Process each symbol
    portfolio = {}
    for symbol, df in data.items():
        # Skip if data is empty
        if df.empty:
            continue
        
        # Get entry signals
        entry_df = entry_strategy.generate_signal(df)
        entry_signal = entry_strategy.get_latest_signal(df)
        
        # Get exit signals
        exit_df = exit_strategy.generate_signal(df)
        exit_signal = exit_strategy.get_latest_signal(df)
        
        # Get symbol metadata
        symbol_info = next((s for s in SYMBOLS if isinstance(s, dict) and s["symbol"] == symbol), {"symbol": symbol, "tags": []})
        
        # Calculate position size
        position_size = STRATEGY_CONFIG["default_allocation"] * 100000  # Assuming $100k portfolio
        
        # Calculate statistics
        returns = compute_returns(df)
        sharpe_ratios = compute_sharpe(df)
        pnl_spark = compute_pnl_spark(df, position_size)
        total_return = compute_total_return(df)
        
        # Store results
        portfolio[symbol] = {
            "symbol": symbol,
            "tags": symbol_info.get("tags", []),
            "allocation": STRATEGY_CONFIG["default_allocation"],
            "exit_signal": exit_signal["exit_signal"],
            "entry_signal": entry_signal["entry_long"],
            "latest_indicators": {
                "close": df["close"].iloc[-1],
                "SMA_20": entry_df["SMA_20"].iloc[-1],
                "SMA_50": entry_df["SMA_50"].iloc[-1],
                "ATR": exit_df["ATR"].iloc[-1]
            },
            "position_size_dollars": position_size,
            "pnl_spark_chart": pnl_spark,
            "returns": returns,
            "sharpe_ratios": sharpe_ratios,
            "total_return": total_return,
            "total_pnl_dollars": position_size * total_return
        }
    
    # Export results
    export_path = export_portfolio(portfolio)
    print(f"Portfolio exported to {export_path}")
    
    return portfolio

def main():
    parser = argparse.ArgumentParser(description="Trading Strategy Runner")
    parser.add_argument("--symbols", type=str, help="Comma-separated list of symbols to analyze")
    parser.add_argument("--days", type=int, default=365, help="Number of days of historical data to analyze")
    parser.add_argument("--api-key", type=str, help="Tiingo API key (overrides config)")
    
    args = parser.parse_args()
    
    symbols = args.symbols.split(",") if args.symbols else None
    
    portfolio = run_strategy(symbols=symbols, days=args.days, api_key=args.api_key)
    
    # Print summary
    print("\nPortfolio Summary:")
    print("-" * 80)
    for symbol, data in portfolio.items():
        print(f"{symbol}: Close ${data['latest_indicators']['close']:.2f} | "
              f"Return {data['total_return']:.2%} | "
              f"PnL ${data['total_pnl_dollars']:.2f} | "
              f"{'BUY' if data['entry_signal'] else ''} {'SELL' if data['exit_signal'] else ''}")
    print("-" * 80)

if __name__ == "__main__":
    main()