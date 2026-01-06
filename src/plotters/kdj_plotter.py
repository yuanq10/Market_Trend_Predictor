import matplotlib.pyplot as plt
from src.utils.paths import PLOTS_DIR

def kdj_plotter(symbol, k, d, j):   
    plt.figure(figsize=(12, 6))
    plt.plot(k, label='K')
    plt.plot(d, label='D')
    plt.plot(j, label='J')

    # Common KDJ reference lines
    plt.axhline(80, linestyle='--', alpha=0.4)
    plt.axhline(20, linestyle='--', alpha=0.4)

    plt.title(f'{symbol} KDJ Indicator')
    plt.ylabel('Value')
    plt.legend()
    plt.grid(alpha=0.3)

    filename = PLOTS_DIR / f"{symbol}_KDJ.png"
    plt.savefig(filename, dpi=150, bbox_inches="tight")
    plt.close()