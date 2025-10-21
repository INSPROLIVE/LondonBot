# brokers/ib_broker.py
from ib_insync import IB, Future, MarketOrder, LimitOrder
import logging

logger = logging.getLogger('ib_broker')

class IBBroker:
    def __init__(self, host='127.0.0.1', port=7497, client_id=1):
        self.ib = IB()
        self.ib.connect(host, port, clientId=client_id)
        self.contract = None
        logger.info('Connected to IB')

    def make_future_contract(self, symbol, exchange='GLOBEX', currency='USD', lastTradeDateOrContractMonth=None):
        # lastTradeDateOrContractMonth e.g. '202512'
        c = Future(symbol=symbol, lastTradeDateOrContractMonth=lastTradeDateOrContractMonth, exchange=exchange, currency=currency)
        self.contract = c
        return c

    def place_market_order(self, contract, action, quantity):
        order = MarketOrder(action, quantity)
        trade = self.ib.placeOrder(contract, order)
        # Wait for fills (non-blocking usage in real code better)
        self.ib.sleep(0.1)
        return trade

    def place_limit_order(self, contract, action, quantity, price):
        order = LimitOrder(action, quantity, price)
        trade = self.ib.placeOrder(contract, order)
        self.ib.sleep(0.1)
        return trade

    def get_fills(self, trade):
        # translate trade.fills to list of dicts: {'qty':int,'price':float}
        fills = []
        for f in trade.fills:
            fills.append({'qty': int(f.execution.shares), 'price': float(f.execution.price)})
        return fills

    def disconnect(self):
        self.ib.disconnect()
