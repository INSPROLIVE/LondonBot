import argparse
import logging
import os
import yaml
from core.strategy import LondonStrategy
from core.backtester import Backtester
from core.risk import RiskManager
from brokers.ib_broker import IBBroker
from dashboard.textual_ui import TextualAppRunner

# Setup
ROOT = os.path.dirname(__file__)
DEFAULT_CFG = os.path.join(ROOT, 'config.yaml')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('london_main')

def load_config(path):
    with open(path, 'r') as f:
        return yaml.safe_load(f)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', choices=['backtest','paper','live'], default='paper')
    parser.add_argument('--csv', help='Path to 5-min OHLCV CSV (used for backtest/paper)')
    parser.add_argument('--config', default=DEFAULT_CFG)
    args = parser.parse_args()

    cfg = load_config(args.config)
    mode = args.mode

    # create components
    risk = RiskManager(cfg)
    strategy = LondonStrategy(cfg, risk)

    if mode == 'backtest':
        bt = Backtester(cfg, strategy)
        bt.run(args.csv)
        return

    # Paper / Live: connect IB broker
    ib_cfg = cfg['ib']
    ib = IBBroker(ib_cfg['host'], ib_cfg['port'], ib_cfg['client_id'])
    engine = strategy.make_engine(broker=ib, mode=mode)

    # Dashboard
    if cfg.get('dashboard', {}).get('enable_textual', True):
        app = TextualAppRunner(engine, cfg)
        app.run()
    else:
        engine.run_from_csv(args.csv)

if __name__ == '__main__':
    main()
