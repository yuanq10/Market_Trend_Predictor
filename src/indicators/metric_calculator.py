from stockstats import StockDataFrame

def macd_calculator(historical_data):
    stock = StockDataFrame.retype(historical_data.copy())
    # MACD
    macd = stock['macd_5,11,4']
    macd_signal = stock['macds_5,11,4']
    macd_histogram = stock['macdh_5,11,4']
    #print(macd)
    return macd, macd_signal, macd_histogram

def kdj_calculator(historical_data):
    stock = StockDataFrame.retype(historical_data.copy())
    # KDJ
    kdj_k = stock['kdjk']
    kdj_d = stock['kdjd']
    kdj_j = stock['kdjj']
    #print(kdj)
    return kdj_k, kdj_d, kdj_j

def boll_calculator(historical_data):
    stock = StockDataFrame.retype(historical_data.copy())
    # Boll
    close = stock['close']
    boll_mid = stock['boll']
    boll_up = stock['boll_ub']
    boll_low = stock['boll_lb']
    #print(boll)
    return close, boll_mid, boll_up, boll_low

def cci_calculator(historical_data):
    stock = StockDataFrame.retype(historical_data.copy())
    # CCI
    cci = stock['cci_20']
    return cci