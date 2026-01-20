import pandas as pd

def trim_warmup(data, analysis_start_date):
    """
    Trim warm-up period from Series or DataFrame.

    Parameters
    ----------
    data : pd.Series or pd.DataFrame
        Time-indexed data including warm-up period
    analysis_start_date : str or datetime

    Returns
    -------
    Same type as input, trimmed
    """
    analysis_start_date = pd.to_datetime(analysis_start_date)

    # Ensure tz consistency
    if hasattr(data.index, "tz"):
        data = data.copy()
        data.index = data.index.tz_localize(None)

    return data.loc[analysis_start_date:]

def trim_many(analysis_start_date, **series):
    """
    Trim multiple Series/DataFrames to same analysis period.

    Example:
    trim_many("2025-01-01", macd=macd, cci=cci)
    """
    trimmed = {}
    for name, s in series.items():
        trimmed[name] = trim_warmup(s, analysis_start_date)
    return trimmed
