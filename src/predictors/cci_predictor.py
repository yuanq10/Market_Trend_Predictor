import pandas as pd

def cci_predictor(
    cci: pd.Series,
    buy_level: float,
    sell_level: float
):
    """
    Generate CCI-only buy/sell signals.

    Parameters
    ----------
    cci : pd.Series
        Commodity Channel Index
    buy_level : float
        Buy threshold (e.g. -100)
    sell_level : float
        Sell threshold (e.g. 100)

    Returns
    -------
    pd.DataFrame
        buy_signal, sell_signal
    """
    cci_prev = cci.shift(1)

    buy_signal = (
        (cci <= buy_level) &
        (cci_prev < cci)
    ).astype(int)

    sell_signal = (
        (cci >= sell_level) &
        (cci_prev > cci)
    ).astype(int)

    return pd.DataFrame(
        {
            "buy_signal": buy_signal,
            "sell_signal": sell_signal
        },
        index=cci.index
    )
