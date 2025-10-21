# core/risk.py
class RiskManager:
    def __init__(self, cfg):
        self.cfg = cfg
        self.initial = cfg.get('initial_capital', 10000.0)

    def size_for(self, entry, stop, equity):
        per_unit = abs(entry - stop)
        if per_unit <= 0:
            return 0.0
        if self.cfg.get('risk_mode','fixed') == 'fixed':
            risk = float(self.cfg.get('risk_per_trade', 100.0))
        else:
            risk = float(self.cfg.get('risk_percent', 0.01)) * equity
        size = risk / per_unit
        return size

    def check_daily_kill(self, pnl_today):
        max_loss = float(self.cfg.get('max_daily_loss', -1000.0))
        return pnl_today <= max_loss
