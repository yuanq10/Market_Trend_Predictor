import yfinance as yf

def data_fetcher(symbol):
    ticker = yf.Ticker(symbol)
    historical_data = ticker.history(period="1y")  # data for the last year
    #historical_data = ticker.history(start="2024-01-01", end="2025-01-01")  # data for the last year
    #print("Historical Data:")
    #print(historical_data)
    return historical_data
