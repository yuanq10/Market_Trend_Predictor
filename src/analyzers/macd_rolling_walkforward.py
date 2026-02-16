import pandas as pd
from src.analyzers.macd_analyzer import macd_threshold_analyzer
from src.predictors.macd_predictor import macd_predictor
from src.simulator.simulator import simulator
from src.utils.date_slice import slice_period


def macd_rolling_walkforward(
    close_prices,
    macd,
    histogram,
    train_window_months=12,
    test_window_months=1,
    initial_cash=10000
):
    """
    Rolling walk-forward optimization for MACD thresholds.

    Returns
    -------
    pd.DataFrame
        One row per test window with:
        - train_start / train_end
        - test_start / test_end
        - buy_low / buy_high / sell_threshold
        - train_return_pct
        - test_return_pct
        - final_portfolio_value
    """

    index = close_prices.index
    results = []

    # Generate rolling windows
    dates = pd.date_range(
        start=index.min(),
        end=index.max(),
        freq="MS"  # month start
    )

    for i in range(train_window_months, len(dates) - test_window_months):
        train_start = dates[i - train_window_months]
        train_end   = dates[i]
        test_start  = dates[i]
        test_end    = dates[i + test_window_months]

        # --- TRAIN ---
        close_train = slice_period(close_prices, train_start, train_end)
        macd_train  = slice_period(macd, train_start, train_end)
        hist_train  = slice_period(histogram, train_start, train_end)

        if len(close_train) < 50:
            continue  # skip insufficient data

        analysis = macd_threshold_analyzer(
            close_prices=close_train,
            macd=macd_train,
            histogram=hist_train,
            save_csv=False
        )

        best = analysis.iloc[0]

        buy_zone = (best["buy_low"], best["buy_high"])
        sell_th  = best["sell_threshold"]

        # --- TEST ---
        close_test = slice_period(close_prices, test_start, test_end)
        macd_test  = slice_period(macd, test_start, test_end)
        hist_test  = slice_period(histogram, test_start, test_end)

        if close_test.empty:
            continue

        signals = macd_predictor(
            histogram=hist_test,
            macd=macd_test,
            buy_zone=buy_zone,
            sell_threshold=sell_th
        )

        portfolio = simulator(
            close_prices=close_test,
            signal_df=signals,
            initial_cash=initial_cash
        )

        final_value = portfolio["portfolio_value"].iloc[-1]
        test_return = (final_value / initial_cash - 1) * 100

        results.append({
            "train_start": train_start,
            "train_end": train_end,
            "test_start": test_start,
            "test_end": test_end,
            "buy_low": buy_zone[0],
            "buy_high": buy_zone[1],
            "sell_threshold": sell_th,
            "train_return_pct": best["return_pct"],
            "test_return_pct": test_return,
            "final_value": final_value
        })

    return pd.DataFrame(results)
