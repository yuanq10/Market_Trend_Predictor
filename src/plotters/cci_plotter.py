import matplotlib.pyplot as plt
from src.utils.paths import PLOTS_DIR

def cci_plotter(symbol, cci):
    plt.figure(figsize=(12, 5))
    plt.plot(cci, label=f'CCI_20')

    # Reference levels
    plt.axhline(100, linestyle='--', alpha=0.5, label='+100 (Overbought)')
    plt.axhline(-100, linestyle='--', alpha=0.5, label='-100 (Oversold)')
    plt.axhline(0, linestyle=':', alpha=0.4)

    plt.title(f'{symbol} Commodity Channel Index (CCI)')
    plt.ylabel('CCI')
    plt.legend()
    plt.grid(alpha=0.3)

    filename = PLOTS_DIR / f"{symbol}_cci_20.png"
    plt.savefig(filename, dpi=150, bbox_inches="tight")
    plt.close()