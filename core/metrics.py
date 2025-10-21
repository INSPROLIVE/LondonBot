# core/metrics.py
import pandas as pd
import math

def compute_metrics(eq_df):
    # eq_df: index=date, column equity
    if eq_df.empty:
        return {}
    series = eq_df['equity'].astype(float)
    running_max = series.cummax()
    drawdown = series - running_max
    max_dd = drawdown.min()
    max_dd_pct = (series / running_max - 1).min()
    # CAGR
    start = pd.to_datetime(series.index[0])
    end = pd.to_datetime(series.index[-1])
    years = max(1/365.25, (end-start).days / 365.25)
    cagr = (series.iloc[-1] / series.iloc[0]) ** (1/years) - 1
    # Sharpe
    rets = series.pct_change().dropna()
    sharpe = (rets.mean() / rets.std() * math.sqrt(252)) if rets.std() != 0 else 0.0
    return {'max_dd': float(max_dd), 'max_dd_pct': float(max_dd_pct), 'cagr': cagr, 'sharpe': sharpe}
