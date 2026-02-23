import pandas as pd


def generate(df: pd.DataFrame, lookback: int = 20) -> pd.DataFrame:
    d = df.copy().sort_values("timestamp").reset_index(drop=True)
    d["low_n"] = d["low"].rolling(lookback).min()
    d["high_n"] = d["high"].rolling(lookback).max()
    d["vol_ok"] = d["volume"] > d["volume"].rolling(20).mean() * 0.9

    long_sweep = (d["low"] < d["low_n"].shift(1)) & (d["close"] > d["low"].shift(1))
    short_sweep = (d["high"] > d["high_n"].shift(1)) & (d["close"] < d["high"].shift(1))

    if "funding" in d.columns:
        funding_ok_long = (d["funding"].fillna(0) <= d["funding"].rolling(50).mean().fillna(0))
        funding_ok_short = (d["funding"].fillna(0) >= d["funding"].rolling(50).mean().fillna(0))
    else:
        funding_ok_long = True
        funding_ok_short = True

    d["squeeze_long"] = long_sweep & d["vol_ok"] & funding_ok_long
    d["squeeze_short"] = short_sweep & d["vol_ok"] & funding_ok_short

    return d[["timestamp", "squeeze_long", "squeeze_short"]]
