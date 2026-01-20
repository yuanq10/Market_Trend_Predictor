import yfinance as yf

def data_fetcher(symbol, start_date, end_date):
    ticker = yf.Ticker(symbol)
    #historical_data = ticker.history(period="2y")  # data for the last year by period = "y"
    historical_data = ticker.history(start=start_date, end=end_date)  # data for the last year by date
    return historical_data
