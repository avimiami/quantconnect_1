import pandas as pd
import numpy as np

def compute_returns(df):
    df = df.copy()
    df['returns'] = df['close'].pct_change()
    df['cum_returns'] = (1 + df['returns']).cumprod()

    now = df.index[-1]
    lookup = {
        "1d": now - pd.Timedelta(days=1),
        "1w": now - pd.Timedelta(days=7),
        "1m": now - pd.DateOffset(months=1),
        "3m": now - pd.DateOffset(months=3),
        "ytd": pd.Timestamp(f"{now.year}-01-01")
    }

    result = {}
    for label, ts in lookup.items():
        past = df[df.index <= ts]
        if not past.empty:
            base = past.iloc[-1]["cum_returns"]
            result[label] = df.iloc[-1]["cum_returns"] / base - 1
        else:
            result[label] = None

    return result


def compute_sharpe(df, periods=[90, 180, 360], risk_free_rate=0.03):
    df = df.copy()
    df['daily_return'] = df['close'].pct_change()
    # Annualized risk-free rate to daily
    daily_rf = (1 + risk_free_rate) ** (1/252) - 1
    
    sharpes = {}
    for p in periods:
        subset = df.tail(p)
        if len(subset) < 2:
            sharpes[f"{p}d"] = None
            continue
        mean = subset['daily_return'].mean() - daily_rf
        std = subset['daily_return'].std()
        sharpes[f"{p}d"] = (mean / std) * np.sqrt(252) if std > 0 else None
    return sharpes


def compute_pnl_spark(df, position_size):
    df = df.tail(30).copy()
    df['returns'] = df['close'].pct_change().fillna(0)
    df['cum_return'] = (1 + df['returns']).cumprod()
    df['pnl'] = position_size * (df['cum_return'] - 1)
    return df['pnl'].tolist()


def compute_total_return(df):
    return df['close'].iloc[-1] / df['close'].iloc[0] - 1


def compute_drawdown(df, column='close'):
    """Calculate maximum drawdown"""
    df = df.copy()
    # Calculate the cumulative maximum
    df['cum_max'] = df[column].cummax()
    # Calculate drawdown in percentage terms
    df['drawdown'] = (df[column] / df['cum_max']) - 1
    # Get the maximum drawdown
    max_drawdown = df['drawdown'].min()
    return max_drawdown