import datetime

from AlgorithmImports import *
import numpy as np 
import pandas as pd
import datetime as dt

UNIVERSE_SIZE = 500
MONTHLY_REBALANCE = False


class PCANeutralAlpha(QCAlgorithm):
    def initialize(self) -> None:

        self.set_start_date(2021, 1, 1)
        self.set_end_date(2022, 1, 1)
        self.set_cash(1_000_000)

        self.set_brokerage_model(
            BrokerageName.INTERACTIVE_BROKERS_BROKERAGE,
            AccountType.CASH,
        )
        self.settings.free_portfolio_value_percentage = 0.005



        self.universe_settings.resolution = Resolution.DAILY
        self.add_universe(self._universe_filter)

        if MONTHLY_REBALANCE:
            self.REBALANCE_DAYS  = 21
            self.N_TRAIN_WINDOWS = 12
        else:
            self.REBALANCE_DAYS  = 5
            self.N_TRAIN_WINDOWS = 8

        self.LOOKBACK      = 220
        self.MIN_HISTORY   = (
            self.LOOKBACK
            + self.REBALANCE_DAYS * self.N_TRAIN_WINDOWS
            + 5
        )
        self.UNIVERSE_SIZE = UNIVERSE_SIZE

        self._symbols: list            = []
        self._last_rebalance: dt.datetime | None = None

        self.set_warm_up(self.MIN_HISTORY, Resolution.DAILY)

        if MONTHLY_REBALANCE:
            self.schedule.on(
                self.date_rules.month_start("SPY", 1),
                self.time_rules.after_market_open("SPY", 30),
                self._rebalance,
            )
        else:
            self.schedule.on(
                self.date_rules.every_day(),
                self.time_rules.after_market_open("SPY", 30),
                self._rebalance,
            )

        self.set_benchmark("SPY")

    def _universe_filter(self, fundamentals: list) -> list:
        filtered = [
            f for f in fundamentals
            if f.has_fundamental_data
            and f.market_cap > 1e9
            and f.price > 5
            and f.valuation_ratios.pe_ratio not in (0, None)
            and f.valuation_ratios.pb_ratio not in (0, None)
            and f.operation_ratios.roe.value not in (0, None)
            and f.financial_statements.balance_sheet.total_debt is not None
            and f.financial_statements.balance_sheet.stockholders_equity is not None
            and f.financial_statements.balance_sheet.stockholders_equity != 0
            and f.volume > 0
        ]
        filtered.sort(key=lambda f: f.dollar_volume, reverse=True)
        self._symbols = [f.symbol for f in filtered[: self.UNIVERSE_SIZE]]
        return self._symbols

    def _get_tradable_symbols(self) -> list:
        """Return universe symbols that have received at least one price bar."""
        return [
            sym for sym in self._symbols
            if sym in self.securities
            and self.securities[sym].has_data
            and self.securities[sym].price > 0
        ]

    def _fetch_asset_history(self, symbols: list) -> dict:
        """Batch-fetch daily OHLCV history. Returns {symbol: DataFrame}."""
        result = {}
        try:
            raw = self.history(
                symbols, self.MIN_HISTORY, Resolution.DAILY
            )
            if raw.empty:
                return result
            for sym in symbols:
                try:
                    result[sym] = raw.loc[sym]
                except KeyError:
                    pass
        except Exception as e:
            self.log(f"Asset history error: {e}")
        return result

    def on_data(self, data: Slice):
        if not self.portfolio.invested:
            self.set_holdings("SPY", 1)
