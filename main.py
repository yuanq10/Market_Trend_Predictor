from data_fethcher import data_fetcher
from metric_calculator import *
from plotter import *
from predictor import predictor
from simulator import simulator

def main(symbol):
    data = data_fetcher(symbol)
    macd, signal, histogram = macd_calculator(data)
    cci = cci_calculator(data)
    k, d, j = kdj_calculator(data)
    close, boll_mid, boll_ub, boll_lb = boll_calculator(data)
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

if __name__ == "__main__":
    main("TSLA")