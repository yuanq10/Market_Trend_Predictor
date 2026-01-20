from src.analyzers.macd_analyzer import macd_threshold_analyzer
from src.predictors.macd_predictor import macd_predictor
from src.simulator.simulator import simulator
from src.utils.date_slice import slice_period

def macd_walkforward(
    close_prices,
    macd,
    histogram,
    train_period,
    test_period,
    initial_cash=10000
):
    # --- TRAIN ---
    close_train = slice_period(close_prices, *train_period)
    macd_train = slice_period(macd, *train_period)
    hist_train = slice_period(histogram, *train_period)

    analysis = macd_threshold_analyzer(
        close_prices=close_train,
        macd=macd_train,
        histogram=hist_train,
        save_csv=False
    )

    best = analysis.iloc[0]

    best_buy_zone = (best["buy_low"], best["buy_high"])
    best_sell_th = best["sell_threshold"]

    # --- TEST ---
    test_slice = slice_period(close_prices.index.to_series(), *test_period).index

    close_test = close_prices.loc[test_slice]
    macd_test  = macd.loc[test_slice]
    hist_test  = histogram.loc[test_slice]


    signals = macd_predictor(
        histogram=hist_test,
        macd=macd_test,
        buy_zone=best_buy_zone,
        sell_threshold=best_sell_th
    )

    signals = signals.loc[close_test.index]
    close_test = close_test.loc[signals.index]

    portfolio = simulator(
        close_prices=close_test,
        signal_df=signals,
        initial_cash=initial_cash
    )

    return {
        "best_params": {
            "buy_zone": best_buy_zone,
            "sell_threshold": best_sell_th
        },
        "train_return_pct": best["return_pct"],
        "test_final_value": portfolio["portfolio_value"].iloc[-1],
        "test_return_pct": (
            portfolio["portfolio_value"].iloc[-1] / initial_cash - 1
        ) * 100,
        "portfolio": portfolio
    }
