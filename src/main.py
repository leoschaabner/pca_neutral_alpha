from AlgorithmImports import *
import numpy as np 
import pandas as pd
import datetime as dt
from .helpers import (
    get_fundamental_history_df,
)

DEBUG = True
UNIVERSE_SIZE = 35 if DEBUG else 500
MONTHLY_REBALANCE = False


class PCANeutralAlpha(QCAlgorithm):
    def initialize(self) -> None:
        self.add_equity("SPY", Resolution.DAILY)
        self.set_start_date(2021 if DEBUG else 2000, 1, 1)
        self.set_end_date(2021 if DEBUG else 2026, 6, 1)
        self.set_cash(1_000_000)

        self.set_brokerage_model(
            BrokerageName.INTERACTIVE_BROKERS_BROKERAGE,
            AccountType.CASH,
        )
        self.settings.free_portfolio_value_percentage = 0.005

        self.universe_settings.resolution = Resolution.DAILY
        self.add_universe(self.universe_filter)

        if MONTHLY_REBALANCE:
            self.REBALANCE_DAYS = 21
            self.N_TRAIN_WINDOWS = 12
        else:
            self.REBALANCE_DAYS = 5
            self.N_TRAIN_WINDOWS = 8

        self.LOOKBACK = 220
        self.MIN_HISTORY = (
            self.LOOKBACK
            + self.REBALANCE_DAYS * self.N_TRAIN_WINDOWS
            + 5
        )
        self.UNIVERSE_SIZE = UNIVERSE_SIZE

        self.symbols: list = []
        self._last_rebalance: dt.datetime | None = None

        self.set_warm_up(self.MIN_HISTORY, Resolution.DAILY)

        if MONTHLY_REBALANCE:
            self.schedule.on(
                self.date_rules.month_start("SPY", 1),
                self.time_rules.after_market_open("SPY", 30),
                self.rebalance_portfolio,
            )
        else:
            self.schedule.on(
                self.date_rules.every_day(),
                self.time_rules.after_market_open("SPY", 30),
                self.rebalance_portfolio,
            )

        self.set_benchmark("SPY")

    def universe_filter(self, fundamentals: list) -> list:
        filtered = []
        for f in fundamentals:
            vr = f.valuation_ratios
            bs = f.financial_statements.balance_sheet
            ors = f.operation_ratios
            if (
                f.has_fundamental_data
                and f.market_cap > 1e9
                and f.price > 5
                and vr.pe_ratio not in (0, None)
                and vr.pb_ratio not in (0, None)
                and ors.roe.value not in (0, None)
                and bs.total_debt is not None
                and bs.stockholders_equity is not None
                and bs.stockholders_equity != 0
                and f.volume > 0
                ):
                filtered.append(f)
    
        filtered.sort(key=lambda f: f.dollar_volume, reverse=True)
        self.symbols = [f.symbol for f in filtered[:self.UNIVERSE_SIZE]]
        return self.symbols

    def get_tradable_symbols(self) -> list:
        """Return universe symbols that have received at least one price bar."""
        return [
            sym for sym in self.symbols
            if sym in self.securities
            and self.securities[sym].has_data
            and self.securities[sym].price > 0
        ]

    def get_asset_history(self, symbols: list) -> dict:
        """Batch-fetch daily OHLCV history. Returns {symbol: DataFrame}."""
        result = {}
        # raw df has symbol and timestamp as index
        # and close, high, low, open, volume as columns
        raw = self.history(
            symbols, self.MIN_HISTORY, Resolution.DAILY
        )
        if raw.empty:
            return result
        
        # the DF for each symbol has the timestamp as index 
        # and close, high, low, open, volume as columns
        for sym in symbols:
            if sym not in raw.index.get_level_values(0):
                continue
            result[sym] = raw.loc[sym]
        return result

    def get_fundamental_history(
        self, symbols: list, 
        lookback: int | None = None
        ) -> dict:
        n = lookback or self.MIN_HISTORY
        raw = self.history(Fundamental, symbols, n, Resolution.DAILY)
        if raw.empty:
            return {}
        result = {}
        for sym in symbols:
            if sym not in raw.index.get_level_values(0):
                continue
            subset = raw.loc[sym]
            result[sym] = get_fundamental_history_df(subset)
        return result

    def rebalance_portfolio(self) -> None:
        tradable_symbols = self.get_tradable_symbols()
        asset_history = self.get_asset_history(tradable_symbols)
        tradable_symbols = [i for i in tradable_symbols if i in asset_history]
        fundamental_history = self.get_fundamental_history(tradable_symbols)
        tradable_symbols = [i for i in tradable_symbols if i in fundamental_history]
        if not self.portfolio.invested:
            self.set_holdings("SPY", 1)

    def on_securities_changed(self, changes) -> None:
        for security in changes.removed_securities:
            sym = security.symbol
            if self.portfolio[sym].invested:
                self.liquidate(sym, tag="universe_removal")
