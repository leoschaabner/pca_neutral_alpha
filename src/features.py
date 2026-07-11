# region imports
from AlgorithmImports import *
# endregion
import numpy as np


def get_parkinson_volatility(high, low):
    """
    Calculate the Parkinson volatility estimator.
    $$
    \sigma_{\text{Parkinson}} = \sqrt{\frac{1}{4 \ln(2)} \left[ 
    \ln\left(\frac{\text{High}}{\text{Low}}\right) \right]^2}
    $$
    """
    const = 1 / (4 * np.log(2))
    hl = np.log(high / low) ** 2
    return np.sqrt(const * hl)
    

def get_upper_shadow(close, high, open):
    return high - np.maximum(close, open)


def get_upper_relative_shadow(close, high, open):
    return get_upper_shadow(close, high, open) / close


def get_lower_shadow(close, low, open):
    return np.minimum(close, open) - low


def get_lower_relative_shadow(close, low, open):
    return get_lower_shadow(close, low, open) / close

