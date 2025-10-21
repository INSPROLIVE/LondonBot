# core/engine.py
import pandas as pd
import logging
from datetime import datetime

logger = logging.getLogger('engine')

class StrategyEngineBase:
    def __init__(self, cfg, risk_manager, broker, mode='paper'):
        self.cfg = cfg
        self.risk = risk_manager
        self.broker = broker
        self.mode = mode
        self.equity = float(cfg.get('initial_capital',10000.0))
        self.trades = []
        self.session_high_low = {}  # date -> (high,low)
        self.closed_pnl = 0.0
        self.open_positions = []

    def has_entry_for_date(self, date):
        return any(t['date'] == date for t in self.trades)

    def execute_order(self, side, entry_nominal, stop, trigger_row):
        """Model latency+slippage, send order to broker, handle partial fills, retries, and record trade."""
        # determine time to execute (simulate latency)
        latency_ms = int(self.cfg.get('latency_ms', 200))
        ts = pd.Timestamp(trigger_row['dt_eastern']) + pd.Timedelta(milliseconds=latency_ms)
        # Ask broker to place market order (or limit depending on preference)
        quantity_float = self.risk.size_for(entry_nominal, stop, self.equity)
        # map to integer contracts
        contracts = max(1, int(round(quantity_float)))

        # attempt order with retries
        max_retries = 3
        attempt = 0
        filled = 0
        avg_fill_price = 0.0
        while attempt < max_retries and filled < contracts:
            attempt += 1
            try:
                order_resp = self.broker.place_market_order(self.broker.contract, 'BUY' if side=='LONG' else 'SELL', contracts - filled)
                # broker response must include fills and fill price(s)
                fills = self.broker.get_fills(order_resp)
                for f in fills:
                    qty = int(f['qty'])
                    price = float(f['price'])
                    avg_fill_price = (avg_fill_price*filled + price*qty) / (filled+qty) if filled+qty>0 else price
                    filled += qty
                if filled >= contracts:
                    break
            except Exception as e:
                logger.exception('Order attempt failed, retrying...')
        if filled == 0:
            logger.error('Order failed after retries, aborting')
            return

        # Record trade: simulate exit scanning (TP/SL) on same day by caller/backtester
        trade = {'date': pd.Timestamp(trigger_row['dt_eastern']).date(), 'side': side, 'entry_price': avg_fill_price, 'size': contracts, 'stop': stop}
        self.open_positions.append(trade)
        # For simplicity, we close using backtest bars in Backtester; in live we attach IB fill events and run OCO orders
        logger.info(f"Executed {side} {contracts} @ {avg_fill_price}")
        self.trades.append(trade)
        return trade
