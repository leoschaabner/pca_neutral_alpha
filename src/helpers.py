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
    