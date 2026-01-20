from stockstats import StockDataFrame
import pandas as pd

def compute_macd(historical_data):
    """
    Compute MACD Using parameters 5, 11, 4.

    Parameters
    ----------
    historical_data : DataFrame
        Data including warm-up + analysis period

    Returns
    -------
    macd : Series
    macd_signal : Series
    macd_histogram : Series
    """
    stock = StockDataFrame.retype(historical_data.copy())
    stock.index = stock.index.tz_localize(None)

    macd = stock['macd_5,11,4']
    macd_signal = stock['macds_5,11,4']
    macd_histogram = stock['macdh_5,11,4']
    #print(macd)

    return macd, macd_signal, macd_histogram