from stockstats import StockDataFrame

def compute_kdj(historical_data):
    stock = StockDataFrame.retype(historical_data.copy())
    kdj_k = stock['kdjk']
    kdj_d = stock['kdjd']
    kdj_j = stock['kdjj']
    #print(kdj)
    return kdj_k, kdj_d, kdj_j