import matplotlib.pyplot as plt
from pathlib import Path

def macd_plotter(symbol, macd, signal, hist):
    PLOTS_DIR = Path("plots")
    PLOTS_DIR.mkdir(exist_ok=True)
    
    plt.figure(figsize=(12, 6))

    plt.plot(macd, label='MACD')
    plt.plot(signal, label='Signal')

    plt.bar(hist.index, hist, label='Histogram', alpha=0.8)

    plt.legend()
    plt.title(f'{symbol} MACD Indicator')

    filename = PLOTS_DIR / f"{symbol}_MACD.png"
    plt.savefig(filename, dpi=150, bbox_inches="tight")
    plt.close()

def kdj_plotter(symbol, k, d, j):
    PLOTS_DIR = Path("plots")
    PLOTS_DIR.mkdir(exist_ok=True)
    
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

def boll_plotter(symbol, close, mid, ub, lb):
    PLOTS_DIR = Path("plots")
    PLOTS_DIR.mkdir(exist_ok=True)

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

def cci_plotter(symbol, cci):

    # Ensure output directory exists
    plots_dir = Path("plots")
    plots_dir.mkdir(exist_ok=True)

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

    filename = plots_dir / f"{symbol}_cci_20.png"
    plt.savefig(filename, dpi=150, bbox_inches="tight")
    plt.close()