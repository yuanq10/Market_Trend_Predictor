from src.data import data_fetcher
from src.indicators import *
from src.plotters import *
from src.predictors import predictor
from src.simulator import simulator
from src.analyzers import *

def main(symbol):
    analysis_start_date = "2025-01-01"
    data = data_fetcher(symbol)
    macd, signal, histogram = compute_macd(data, analysis_start_date)
    cci = compute_cci(data, analysis_start_date)
    k, d, j = compute_kdj(data, analysis_start_date)
    close, boll_mid, boll_ub, boll_lb = compute_boll(data, analysis_start_date)
    #print(data)
    #print(macd, signal, histogram)
    macd_plotter(symbol, macd, signal, histogram)
    kdj_plotter(symbol, k, d, j)
    boll_plotter(symbol, close, boll_mid, boll_ub, boll_lb)
    cci_plotter(symbol, cci)

    signal = predictor(data, macd, signal, histogram, cci, k, d, j, boll_mid, boll_lb, boll_ub)
    print(signal.to_string())

    simulation_result = simulator(close, signal)
    print(simulation_result.to_string())
    #macd_threshold_analyzer(close, macd, histogram)
    #cci_threshold_analyzer(close, cci)
    return