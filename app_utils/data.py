import pandas as pd

def load_csv(path="data/fitness_data.csv"):
    df = pd.read_csv(path)
    df["date"] = pd.to_datetime(df["date"])
    return df

def filter_df(df, user, start_date, end_date):
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    mask = (df["user"] == user) & (df["date"] >= start_date) & (df["date"] <= end_date)
    return df.loc[mask].copy()
