import pandas as pd


def ema(s: pd.Series, n: int) -> pd.Series:
    return s.ewm(span=n, adjust=False).mean()


def generate(df: pd.DataFrame) -> pd.DataFrame:
    d = df.copy().sort_values("timestamp").reset_index(drop=True)
    d["ema20"] = ema(d["close"], 20)
    d["ema50"] = ema(d["close"], 50)
    d["ema200"] = ema(d["close"], 200)
    d["trend_regime"] = 0
    d.loc[(d["ema50"] > d["ema200"]) & (d["close"] > d["ema200"]), "trend_regime"] = 1
    d.loc[(d["ema50"] < d["ema200"]) & (d["close"] < d["ema200"]), "trend_regime"] = -1

    d["volume_ok"] = d["volume"] > d["volume"].rolling(20).mean()

    d["trend_long"] = (
        (d["trend_regime"] == 1)
        & (d["close"] > d["ema20"])
        & (d["close"].shift(1) <= d["ema20"].shift(1))
        & d["volume_ok"]
    )
    d["trend_short"] = (
        (d["trend_regime"] == -1)
        & (d["close"] < d["ema20"])
        & (d["close"].shift(1) >= d["ema20"].shift(1))
        & d["volume_ok"]
    )

    return d[["timestamp", "trend_regime", "trend_long", "trend_short"]]
