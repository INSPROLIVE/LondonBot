# core/strategy.py
from datetime import time
import pandas as pd
import logging
from .engine import StrategyEngineBase

logger = logging.getLogger('strategy')

class LondonStrategy:
    def __init__(self, cfg, risk_manager):
        self.cfg = cfg
        self.risk = risk_manager

    def make_engine(self, broker, mode='paper'):
        return LondonEngine(self.cfg, self.risk, broker, mode)

# The engine implements on_bar streaming API
class LondonEngine(StrategyEngineBase):
    def __init__(self, cfg, risk_manager, broker, mode='paper'):
        super().__init__(cfg, risk_manager, broker, mode)
        self.london_start = time(3,0)
        self.london_end = time(9,0)
        self.no_trades_after = time(11,0)
        self.ticks = cfg['tick']
        self.take_profit_rr = cfg['take_profit_rr']

    def compute_session_high_low(self, day_df):
        mask = day_df['time_eastern'].apply(lambda t: self.london_start <= t < self.london_end)
        session = day_df[mask]
        if session.empty:
            return None, None
        return float(session['high'].max()), float(session['low'].min())

    def on_bar(self, day_df, idx):
        # This method called for each new bar within a day (streamed)
        row = day_df.loc[idx]
        t = row['time_eastern']
        date = row['dt_eastern'].date()
        if not self.session_high_low.get(date):
            h,l = self.compute_session_high_low(day_df)
            self.session_high_low[date] = (h,l)

        high, low = self.session_high_low[date]
        if high is None:
            return
        if t < self.london_end:
            return
        # only one entry per day
        if self.has_entry_for_date(date):
            return

        close = row['close']
        openp = row['open']
        # Long trigger
        if close > high and t < self.no_trades_after:
            trigger_low = row['low']
            self.execute_trade('LONG', row, trigger_anchor_low=trigger_low)
        # Short trigger
        if close < low and t < self.no_trades_after:
            trigger_high = row['high']
            self.execute_trade('SHORT', row, trigger_anchor_high=trigger_high)

    def execute_trade(self, side, trigger_row, trigger_anchor_low=None, trigger_anchor_high=None):
        # compute nominal entry at trigger close, then call engine execute which models latency/slippage
        if side == 'LONG':
            stop = float(trigger_anchor_low) - self.ticks
            entry_nominal = float(trigger_row['close'])
        else:
            stop = float(trigger_anchor_high) + self.ticks
            entry_nominal = float(trigger_row['close'])
        self.execute_order(side, entry_nominal, stop, trigger_row)
