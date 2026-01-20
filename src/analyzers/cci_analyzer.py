import numpy as np
import pandas as pd
from pathlib import Path

from src.predictors.cci_predictor import cci_predictor
from src.simulator.simulator import simulator

def cci_threshold_analyzer(
    close_prices: pd.Series,
    cci: pd.Series,
    buy_level_range=(-300, 0, 2),
    sell_level_range=(0, 300, 2),
    initial_cash=10000,
    save_csv=True,
    output_name="cci_threshold_analysis.csv"
):
    """
    Analyze CCI threshold sensitivity via backtesting.
    """

    results = []

    buy_levels = np.arange(*buy_level_range)
    sell_levels = np.arange(*sell_level_range)

    for buy_level in buy_levels:
        for sell_level in sell_levels:
            if buy_level >= sell_level:
                continue

            signals = cci_predictor(
                cci=cci,
                buy_level=buy_level,
                sell_level=sell_level
            )

            portfolio = simulator(
                close_prices=close_prices,
                signal_df=signals,
                initial_cash=initial_cash
            )

            final_value = portfolio["portfolio_value"].iloc[-1]
            total_return = final_value / initial_cash - 1

            results.append({
                "buy_level": buy_level,
                "sell_level": sell_level,
                "final_value": final_value,
                "return_pct": total_return * 100
            })

    results_df = pd.DataFrame(results).sort_values(
        by="final_value", ascending=False
    )

    if save_csv:
        output_dir = Path("analysis")
        output_dir.mkdir(exist_ok=True)

        results_df.head(100).to_csv(
            output_dir / output_name,
            index=False
        )

    return results_df
