from stockstats import StockDataFrame
import pandas as pd

def compute_cci(historical_data):
    stock = StockDataFrame.retype(historical_data.copy())
    stock.index = stock.index.tz_localize(None)

    cci = stock['cci_20']

    return cci