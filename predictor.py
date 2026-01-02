import pandas as pd
def predictor(data, histogram, cci, k, d, j, boll_mid, boll_lb, boll_ub):

    # MACD conditions
    macd_buy_zone = (-0.2, 1)
    macd_sell_threshold = 0.2
    """
    Binary BUY / SELL predictors using 2-day MACD histogram trend

    Parameters
    ----------
    macdh : pd.Series
        MACD histogram time series
    buy_zone : tuple
        (lower, upper) bounds for buy zone
    sell_threshold : float
        Upper bound for sell zone

    Returns
    -------
    pd.DataFrame
        Columns:
        - buy_signal  (1 or 0)
        - sell_signal (1 or 0)
    """
    h_t   = histogram
    h_t1  = histogram.shift(1)

    # BUY conditions
    macd_buy_signal = (
        (h_t1 < h_t) &
        (h_t1 < 0) &
        (h_t >= macd_buy_zone[0]) &
        (h_t <= macd_buy_zone[1])
    ).astype(int)

    # SELL conditions
    macd_sell_signal = (
        (h_t1 > h_t) &
        (h_t1 > 0) &
        (h_t < macd_sell_threshold)
    ).astype(int)

    # CCI Conditions

    """
    Binary BUY / SELL predictor based on CCI thresholds

    Parameters
    ----------
    cci : pd.Series
        Commodity Channel Index series
    buy_level : float
        Buy threshold (default -100)
    sell_level : float
        Sell threshold (default 100)

    Returns
    -------
    pd.DataFrame
        Columns:
        - buy_signal
        - sell_signal
    """
    cci_buy_level = -80
    cci_sell_level = 50

    cci_prev = cci.shift(1)

    cci_buy_signal = (
        (cci <= cci_buy_level) &
        (cci_prev < cci)
    ).astype(int)

    cci_sell_signal = (
        (cci <= cci_sell_level) &
        (cci_prev > cci_sell_level)
    ).astype(int)

    # KDJ Conditions

    """
    Binary BUY / SELL signals based on KDJ J-line behavior

    Parameters
    ----------
    k, d, j : pd.Series
        KDJ K, D, J time series

    Returns
    -------
    pd.DataFrame
        Columns:
        - buy_signal
        - sell_signal
    """
    j_prev = j.shift(1)

    # BUY: J below K & D and rising
    kdj_buy_signal = (
        ((abs(k - j) < 15) | (abs(d - j) < 15)) &
        (j < k) &
        (j < d) &
        (j_prev < j)
    ).astype(int)

    # SELL: J above K & D and falling
    kdj_sell_signal = (
        (j > k) &
        (j > d) &
        (j_prev > j)
    ).astype(int)

    buy_signal = ((cci_buy_signal) | (macd_buy_signal)).astype(int)
    sell_signal = ((cci_sell_signal) | (macd_sell_signal)).astype(int)
    return pd.DataFrame(
        {
            "buy_signal": buy_signal,
            "sell_signal": sell_signal
        },
        index=j.index
    )