from src.data import data_fetcher
from src.indicators import *
from src.plotters import *
from src.predictors import predictor
from src.simulator import simulator
from src.analyzers import *
from src.utils import trim_many

def main(symbol):
    # Define the variables
    data_start_date = "2023-01-01"
    data_end_date = "2026-01-01"
    analysis_start_date = "2024-01-01"
    data = data_fetcher(symbol, data_start_date, data_end_date)
    macd, macd_signal, macd_histogram = compute_macd(data)
    cci = compute_cci(data)
    kdj_k, kdj_d, kdj_j = compute_kdj(data)
    close, boll_mid, boll_ub, boll_lb = compute_boll(data)

    # Trim off the warmup period
    trimmed_data = trim_many(
        analysis_start_date,
        macd=macd,
        macd_signal=macd_signal,
        macd_histogram=macd_histogram,
        cci=cci,
        kdj_k=kdj_k,
        kdj_d=kdj_d,
        kdj_j=kdj_j,
        close=close,
        boll_mid=boll_mid,
        boll_ub=boll_ub,
        boll_lb=boll_lb
    )
    macd = trimmed_data["macd"]
    macd_signal = trimmed_data["macd_signal"]
    macd_histogram = trimmed_data["macd_histogram"]
    cci = trimmed_data["cci"]
    kdj_k = trimmed_data["kdj_k"]
    kdj_d = trimmed_data["kdj_d"]
    kdj_j = trimmed_data["kdj_j"]
    close = trimmed_data["close"]
    boll_mid = trimmed_data["boll_mid"]
    boll_ub = trimmed_data["boll_ub"]
    boll_lb = trimmed_data["boll_lb"]
    
    # Plot out the indicators
    macd_plotter(symbol, macd, macd_signal, macd_histogram)
    kdj_plotter(symbol, kdj_k, kdj_d, kdj_j)
    boll_plotter(symbol, close, boll_mid, boll_ub, boll_lb)
    cci_plotter(symbol, cci)

    # Simulate using the buy sell signal
    buy_sell_signal = predictor(data, macd, macd_signal, macd_histogram, cci, kdj_k, kdj_d, kdj_j, boll_mid, boll_lb, boll_ub)
    print(buy_sell_signal.to_string())

    simulation_result = simulator(close, buy_sell_signal)
    print(simulation_result.to_string())

    # Indicator analysis
    # MACD
    #macd_threshold_analyzer(close, macd, macd_histogram)

    result = macd_walkforward(
        close_prices=close,
        macd=macd,
        histogram=macd_histogram,
        train_period=("2024-01-01", "2025-01-01"),
        test_period=("2025-01-01", "2026-01-01")
    )

    print("Best params:", result["best_params"])
    print("Train return:", result["train_return_pct"])
    print("Test return:", result["test_return_pct"])

    #cci_threshold_analyzer(close, cci)
    return