import matplotlib.pyplot as plt
from src.utils.paths import PLOTS_DIR

def macd_plotter(symbol, macd, signal, hist):   
    plt.figure(figsize=(12, 6))
    plt.plot(macd, label='MACD')
    plt.plot(signal, label='Signal')
    plt.bar(hist.index, hist, label='Histogram', alpha=0.8)

    plt.legend()
    plt.title(f'{symbol} MACD Indicator')

    filename = PLOTS_DIR / f"{symbol}_MACD.png"
    plt.savefig(filename, dpi=150, bbox_inches="tight")
    plt.close()