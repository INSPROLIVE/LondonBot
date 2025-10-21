# dashboard/textual_ui.py
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static, DataTable
from textual.reactive import reactive
from textual.containers import Vertical
import threading
import time

class TextualAppRunner:
    def __init__(self, engine, cfg):
        self.engine = engine
        self.cfg = cfg
        self.app = None

    def run(self):
        app = TradingApp(self.engine, self.cfg)
        app.run()

class TradingApp(App):
    CSS_PATH = ""
    def __init__(self, engine, cfg):
        super().__init__()
        self.engine = engine
        self.cfg = cfg
        self.title = "London Breakout - Textual TUI"

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        yield Vertical(Static("Equity: ", id="equity"), DataTable(id="trades"))

    def on_mount(self):
        # configure the trades table
        table = self.query_one('#trades', DataTable)
        table.add_columns('date','side','entry','exit','size','pnl')
        # start background updater
        self.set_interval(self.cfg.get('dashboard',{}).get('refresh_seconds',1), self.refresh_view)

    def refresh_view(self):
        eq_w = self.query_one('#equity', Static)
        eq_w.update(f"Equity: {self.engine.equity:.2f}")
        table = self.query_one('#trades', DataTable)
        table.clear()
        for t in list(self.engine.trades)[-50:]:
            entry = t.get('entry_price', t.get('entry', 0.0))
            pnl = t.get('pnl', 0.0)
            table.add_row(str(t.get('date','')), t.get('side',''), f"{entry:.2f}", f"{t.get('exit',0.0):.2f}", str(t.get('size','')), f"{pnl:.2f}")
