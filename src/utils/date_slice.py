import pandas as pd

def slice_period(data, start_date, end_date):
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    return data.loc[start_date:end_date]
