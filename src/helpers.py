# region imports
from AlgorithmImports import *
# endregion
import numpy as np
import pandas as pd 


def get_fundamental_history_df(fundamental_data_subset):
    other_relevant_fundamental_cols = [
        "volume",
        "marketcap",
        "market",
        "hasfundamentaldata",
        "dollarvolume",
        "adjustedprice",
    ]
    return pd.concat([
        fundamental_data_subset.apply(get_row_valuation_data, axis=1),
        fundamental_data_subset[other_relevant_fundamental_cols],
        ], axis=1
        )


def get_row_valuation_data(row):
    valuation = row.valuationratios
    relevant_keys = [
        "PERatio", "PCFRatio",
        "PBRatio", "PSRatio", "PEGRatio"
        ]
    row_data = {}
    for key in relevant_keys:
        row_data[key] = getattr(valuation, key, np.nan) 
    return pd.Series(row_data)
    

def filter_universe(fundamentals: list, universe_size: int) -> list:
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
    return [f.symbol for f in filtered[:universe_size]]


def filter_tradable_securities(symbols: list, securities: dict) -> list:
    """Filter symbols to those that are tradable (have data and price > 0)."""
    return [
        sym for sym in symbols
        if sym in securities
        and securities[sym].has_data
        and securities[sym].price > 0
    ]
