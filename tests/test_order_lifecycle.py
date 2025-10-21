# tests/test_order_lifecycle.py
import pytest
from unittest.mock import MagicMock
from core.engine import StrategyEngineBase

class DummyBroker:
    def __init__(self):
        self.contract = None
    def place_market_order(self, contract, action, quantity, on_fill_callback=None, max_retries=3, timeout=10):
        # return a dummy trade object with fills attribute
        t = MagicMock()
        t.fills = []
        # simulate a fill
        t.fills.append(MagicMock(execution=MagicMock(shares=quantity, price=25000.0)))
        t.order = MagicMock()
        t.order.permId = 12345
        return t
    def get_fills(self, trade):
        return [{'qty': int(trade.fills[0].execution.shares), 'price': float(trade.fills[0].execution.price)}]
    def wait_for_fill(self, trade, timeout=10):
        return self.get_fills(trade)

class DummyRisk:
    def size_for(self, entry, stop, equity):
        return 1.0


def test_execute_order_success(tmp_path):
    cfg = {'latency_ms':200, 'contract_multiplier':10.0, 'slack_webhook_url': ''}
    engine = StrategyEngineBase(cfg, DummyRisk(), DummyBroker(), mode='paper')
    # create a fake trigger row
    import pandas as pd
    row = pd.Series({'dt_eastern': pd.Timestamp('2025-10-21 12:00:00-05:00'), 'close':25000.0, 'open':24990.0, 'low':24980.0, 'high':25010.0})
    rec = engine.execute_order('LONG', 25000.0, 24980.0, row)
    assert rec is not None
    assert 'entry_price' in rec or 'entry' in rec
