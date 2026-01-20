import numpy as np
import pandas as pd
from src.predictors.macd_predictor import macd_predictor
from src.simulator.simulator import simulator
from pathlib import Path

def macd_threshold_analyzer(
    close_prices,
    macd,
    histogram,
    buy_lower_range=(-1, 0.5, 0.1),
    buy_upper_range=(0.5, 1.5, 0.1),
    sell_threshold_range=(-0.2, 0.2, 0.01),
    initial_cash=10000,
    save_csv=True,
    output_name="macd_threshold_analysis.csv"
):
    """
    Analyze MACD threshold sensitivity via backtesting.
    """

    results = []

    buy_lows = np.arange(*buy_lower_range)
    buy_highs = np.arange(*buy_upper_range)
    sell_thresholds = np.arange(*sell_threshold_range)

    for low in buy_lows:
        for high in buy_highs:
            if low >= high:
                continue

            for sell_th in sell_thresholds:
                signals = macd_predictor(
                    histogram=histogram,
                    macd=macd,
                    buy_zone=(low, high),
                    sell_threshold=sell_th
                )

                portfolio = simulator(
                    close_prices=close_prices,
                    signal_df=signals,
                    initial_cash=initial_cash
                )

                final_value = portfolio["portfolio_value"].iloc[-1]
                total_return = final_value / initial_cash - 1

                results.append({
                    "buy_low": low,
                    "buy_high": high,
                    "sell_threshold": sell_th,
                    "final_value": final_value,
                    "return_pct": total_return * 100
                })

    results_df = pd.DataFrame(results).sort_values(
        by="final_value", ascending=False
    )

    if save_csv:
        output_dir = Path("analysis")
        output_dir.mkdir(exist_ok=True)

        output_path = output_dir / output_name
        results_df.head(100).to_csv(output_path, index=False)

    return results_df