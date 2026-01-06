from stockstats import StockDataFrame

def compute_macd(historical_data):
    stock = StockDataFrame.retype(historical_data.copy())
    macd = stock['macd_5,11,4']
    macd_signal = stock['macds_5,11,4']
    macd_histogram = stock['macdh_5,11,4']
    #print(macd)
    return macd, macd_signal, macd_histogram