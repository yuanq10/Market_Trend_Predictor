import yfinance as yf
import pandas as pd


def fetch_stock_data(ticker: str, period: str = "3mo", interval: str = "1d",
                     force: bool = False) -> pd.DataFrame:
    """
    Return OHLCV data for ticker.

    For standard daily requests (interval='1d'), the result is cached in
    SQLite (data/cache.db).  A cached result is returned as-is when the
    last fetch occurred on or after the most recent trade date, unless
    force=True is passed.
    """
    from storage.cache_manager import (
        init_db, is_cache_fresh, load_price_history, save_price_history
    )
    init_db()

    if not force and interval == "1d":
        if is_cache_fresh(ticker):
            cached = load_price_history(ticker)
            if cached is not None and not cached.empty:
                return cached

    df = yf.download(ticker, period=period, interval=interval,
                     auto_adjust=True, progress=False)
    if df.empty:
        raise ValueError(f"No data returned for ticker '{ticker}'")

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df.index = pd.to_datetime(df.index)

    if interval == "1d":
        save_price_history(ticker, df)

    return df


def get_stock_info(ticker: str) -> dict:
    """Return basic info: name, current price, % change, volume."""
    try:
        t = yf.Ticker(ticker)
        info = t.info
        name = info.get("shortName") or info.get("longName") or ticker
        price = info.get("currentPrice") or info.get("regularMarketPrice") or 0.0
        prev_close = info.get("regularMarketPreviousClose") or info.get("previousClose") or price
        change_pct = ((price - prev_close) / prev_close * 100) if prev_close else 0.0
        volume = info.get("regularMarketVolume") or info.get("volume") or 0
        return {
            "ticker": ticker,
            "name": name,
            "price": round(price, 2),
            "change_pct": round(change_pct, 2),
            "volume": volume,
        }
    except Exception:
        return {"ticker": ticker, "name": ticker, "price": 0.0, "change_pct": 0.0, "volume": 0}
