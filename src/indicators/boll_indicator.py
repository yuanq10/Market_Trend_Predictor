from stockstats import StockDataFrame

def compute_boll(historical_data):
    stock = StockDataFrame.retype(historical_data.copy())
    close = stock['close']
    boll_mid = stock['boll']
    boll_up = stock['boll_ub']
    boll_low = stock['boll_lb']
    #print(boll)
    return close, boll_mid, boll_up, boll_low