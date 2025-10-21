# core/backtester.py
import pandas as pd
import logging
from .engine import StrategyEngineBase
from .metrics import compute_metrics

logger = logging.getLogger('backtester')

class Backtester:
    def __init__(self, cfg, strategy):
        self.cfg = cfg
        self.strategy = strategy

    def run(self, csv_path):
        df = pd.read_csv(csv_path, parse_dates=['datetime'])
        if df['datetime'].dt.tz is None:
            df['datetime'] = df['datetime'].dt.tz_localize('UTC')
        df['dt_eastern'] = df['datetime'].dt.tz_convert(self.cfg.get('tz_name','America/New_York'))
        df['date_eastern'] = df['dt_eastern'].dt.date
        df['time_eastern'] = df['dt_eastern'].dt.time
        grouped = df.groupby('date_eastern', sort=True)
        engine = self.strategy.make_engine(broker=None, mode='backtest')
        equity_curve = []
        for date, day_df in grouped:
            day_df = day_df.reset_index(drop=True)
            for idx, _ in day_df.iterrows():
                engine.on_bar(day_df, idx)
            equity_curve.append((date, engine.equity))
        trades = pd.DataFrame(engine.trades)
        eq_df = pd.DataFrame(equity_curve, columns=['date','equity']).set_index('date')
        trades.to_csv('outputs/backtest_trades.csv', index=False)
        eq_df.to_csv('outputs/backtest_equity.csv')
        logger.info('Backtest saved to outputs/')
        print(compute_metrics(eq_df))
