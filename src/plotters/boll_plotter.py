import matplotlib.pyplot as plt
from src.utils.paths import PLOTS_DIR

def boll_plotter(symbol, close, mid, ub, lb):
    plt.figure(figsize=(12, 6))
    plt.plot(close, label='Close Price', linewidth=1)
    plt.plot(mid, label='Middle Band (SMA)')
    plt.plot(ub, label='Upper Band')
    plt.plot(lb, label='Lower Band')

    # Fill the band
    plt.fill_between(
        close.index,
        lb,
        ub,
        alpha=0.15,
        label='Bollinger Band'
    )

    plt.title(f'{symbol} Bollinger Bands')
    plt.ylabel('Price')
    plt.legend()
    plt.grid(alpha=0.3)
    
    filename = PLOTS_DIR / f"{symbol}_bollinger_band.png"
    plt.savefig(filename, dpi=150, bbox_inches="tight")
    plt.close()