import pandas as pd

def simulator(
    close_prices,
    signal_df,
    initial_cash=10000.0
):
    """
    Backtest using a signal DataFrame with date, buy_signal, sell_signal

    Parameters
    ----------
    close_prices : pd.Series
        Close prices indexed by date
    signal_df : pd.DataFrame
        Columns: ['date', 'buy_signal', 'sell_signal']
    initial_cash : float
        Starting capital

    Returns
    -------
    pd.DataFrame
        Portfolio value over time
    """

    # Align signals and prices (important)
    data = pd.concat(
        [close_prices, signal_df[['buy_signal', 'sell_signal']]],
        axis=1
    ).dropna()

    cash = initial_cash
    shares = 0
    records = []

    for date, row in data.iterrows():
        price = row['close']
        buy = row['buy_signal']
        sell = row['sell_signal']

        # BUY: invest all cash
        if buy == 1 and cash > price:
            buy_in = cash // price
            cash -= buy_in * price
            shares += buy_in
            

        # SELL: liquidate all shares
        elif sell == 1 and shares > 0:
            cash += shares * price
            shares = 0

        portfolio_value = cash + shares * price

        records.append({
            "date": date,
            "close": price,
            "cash": cash,
            "shares": shares,
            "portfolio_value": portfolio_value
        })

    return pd.DataFrame(records).set_index("date")
