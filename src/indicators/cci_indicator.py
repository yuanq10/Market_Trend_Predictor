from stockstats import StockDataFrame

def compute_cci(historical_data):
    stock = StockDataFrame.retype(historical_data.copy())
    cci = stock['cci_20']
    return cci