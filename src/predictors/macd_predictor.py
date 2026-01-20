import pandas as pd

def macd_predictor(
    histogram: pd.Series,
    macd: pd.Series,
    buy_zone: tuple,
    sell_threshold: float
):
    """
    Generate MACD-only buy/sell signals.

    Parameters
    ----------
    histogram : pd.Series
        MACD histogram
    macd : pd.Series
        MACD line
    buy_zone : (float, float)
        Buy zone (lower, upper)
    sell_threshold : float
        Sell threshold

    Returns
    -------
    pd.DataFrame
        buy_signal, sell_signal
    """
    h_t = histogram
    h_t1 = histogram.shift(1)

    buy_signal = (
        (h_t1 < h_t) &
        (h_t1 < 0) &
        (h_t >= buy_zone[0]) &
        (h_t <= buy_zone[1])
    ).astype(int)

    sell_signal = (
        (h_t1 > h_t) &
        (h_t1 > 0) &
        (h_t < sell_threshold)
    ).astype(int)

    return pd.DataFrame(
        {
            "buy_signal": buy_signal,
            "sell_signal": sell_signal
        },
        index=histogram.index
    )
