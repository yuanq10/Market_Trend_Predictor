from core.data_fetcher import fetch_stock_data, get_stock_info
from core.indicators import calc_cci, calc_macd, calc_kdj, calc_generic_indicator


def _check_crossings(series, thresholds: list, indicator: str, var: str, out: list):
    """Append alert dicts to `out` for every threshold the series crossed on the last bar."""
    if len(series) < 2 or not thresholds:
        return
    prev = float(series.iloc[-2])
    curr = float(series.iloc[-1])
    for th in thresholds:
        if prev < th <= curr:
            out.append({
                "indicator": indicator,
                "signal": "alert",
                "value": round(curr, 4),
                "reason": f"{indicator} {var} crossed above {th} (now {curr:.4f})"
            })
        elif prev > th >= curr:
            out.append({
                "indicator": indicator,
                "signal": "alert",
                "value": round(curr, 4),
                "reason": f"{indicator} {var} crossed below {th} (now {curr:.4f})"
            })


def run_alerts(stocks: list, indicators: list, stock_thresholds: dict = None,
               on_progress=None) -> dict:
    """
    Run alert checks for all stocks against all enabled indicators.
    Returns:
        {
          "alerts": { ticker: [alert_dict, ...] },
          "stats":  { ticker: stat_dict }
        }
    """
    results_alerts = {}
    results_stats = {}

    enabled = [ind for ind in indicators if ind.get("enabled", True)]

    for i, ticker in enumerate(stocks):
        if on_progress:
            on_progress(ticker, i, len(stocks))
        try:
            df = fetch_stock_data(ticker)
            info = get_stock_info(ticker)
        except Exception as e:
            results_alerts[ticker] = [{"indicator": "ERROR", "signal": "error",
                                       "value": None, "reason": str(e)}]
            results_stats[ticker] = {}
            continue

        ticker_alerts = []

        # Price threshold crossings
        if stock_thresholds:
            price_thresholds = stock_thresholds.get(ticker, [])
            if price_thresholds:
                _check_crossings(df["Close"], price_thresholds, "Price", "Close", ticker_alerts)

        stat = {
            "close": info["price"],
            "change_pct": info["change_pct"],
            "volume": info["volume"],
            "cci": None,
            "macd": None,
            "kdj_k": None,
        }

        for ind in enabled:
            itype = ind["type"]
            try:
                thresholds_cfg = ind.get("thresholds", {})

                if itype == "CCI":
                    period = ind.get("period", 20)
                    series = calc_cci(df, period).dropna()
                    if len(series) >= 1:
                        stat["cci"] = round(float(series.iloc[-1]), 2)
                    _check_crossings(series, thresholds_cfg.get("CCI", []),
                                     "CCI", "CCI", ticker_alerts)

                elif itype == "MACD":
                    fast = ind.get("fast", 12)
                    slow = ind.get("slow", 26)
                    signal = ind.get("signal", 9)
                    result = calc_macd(df, fast, slow, signal)
                    macd_s   = result["macd"].dropna()
                    signal_s = result["signal"].dropna()
                    hist_s   = result["histogram"].dropna()
                    if len(macd_s) >= 1:
                        stat["macd"] = round(float(macd_s.iloc[-1]), 4)
                    _check_crossings(macd_s,   thresholds_cfg.get("MACD",      []), "MACD", "MACD",      ticker_alerts)
                    _check_crossings(signal_s, thresholds_cfg.get("Signal",    []), "MACD", "Signal",    ticker_alerts)
                    _check_crossings(hist_s,   thresholds_cfg.get("Histogram", []), "MACD", "Histogram", ticker_alerts)

                elif itype == "KDJ":
                    period   = ind.get("period", 9)
                    k_smooth = ind.get("k_smooth", 3)
                    d_smooth = ind.get("d_smooth", 3)
                    result = calc_kdj(df, period, k_smooth, d_smooth)
                    K = result["K"].dropna()
                    D = result["D"].dropna()
                    J = result["J"].dropna()
                    if len(K) >= 1:
                        stat["kdj_k"] = round(float(K.iloc[-1]), 2)
                    _check_crossings(K, thresholds_cfg.get("K", []), "KDJ", "K", ticker_alerts)
                    _check_crossings(D, thresholds_cfg.get("D", []), "KDJ", "D", ticker_alerts)
                    _check_crossings(J, thresholds_cfg.get("J", []), "KDJ", "J", ticker_alerts)

                else:
                    # Generic TA-Lib indicator
                    SKIP = {"type", "enabled", "thresholds"}
                    ta_params = {k: v for k, v in ind.items() if k not in SKIP and isinstance(v, (int, float))}
                    series = calc_generic_indicator(df, itype, **ta_params).dropna()
                    _check_crossings(series, thresholds_cfg.get(itype.upper(), []),
                                     itype, itype, ticker_alerts)

            except Exception as e:
                ticker_alerts.append({
                    "indicator": itype,
                    "signal": "error",
                    "value": None,
                    "reason": f"{itype} error: {e}"
                })

        results_alerts[ticker] = ticker_alerts
        results_stats[ticker] = stat

    return {"alerts": results_alerts, "stats": results_stats}
