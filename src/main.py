from src.data import data_fetcher
from src.indicators import *
from src.plotters import *
from src.predictors import predictor
from src.simulator import simulator

def main(symbol):
    data = data_fetcher(symbol)
    macd, signal, histogram = compute_macd(data)
    cci = compute_cci(data)
    k, d, j = compute_kdj(data)
    close, boll_mid, boll_ub, boll_lb = compute_boll(data)
    #print(data)
    #print(macd, signal, histogram)
    macd_plotter(symbol, macd, signal, histogram)
    kdj_plotter(symbol, k, d, j)
    boll_plotter(symbol, close, boll_mid, boll_ub, boll_lb)
    cci_plotter(symbol, cci)

    signal = predictor(data, histogram, cci, k, d, j, boll_mid, boll_lb, boll_ub)
    print(signal.to_string())

    simulation_result = simulator(close, signal)
    print(simulation_result.to_string())
    return