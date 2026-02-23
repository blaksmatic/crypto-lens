import pandas as pd


def build_symbol(sym: str):
    px = pd.read_csv(f"data/{sym}_1h.csv", parse_dates=["open_time", "close_time"])
    px = px.rename(columns={"close_time": "timestamp"})
    px = px[["timestamp", "open", "high", "low", "close", "volume"]]

    try:
        der = pd.read_csv(f"data/{sym}_derivatives_1h.csv", parse_dates=["timestamp"])
    except FileNotFoundError:
        der = pd.DataFrame(columns=["timestamp", "oi", "funding"])

    out = px.merge(der, on="timestamp", how="left").sort_values("timestamp")
    out["oi"] = out["oi"].astype(float) if "oi" in out else pd.NA
    out["funding"] = out["funding"].astype(float) if "funding" in out else pd.NA

    # price features
    out["ret1"] = out["close"].pct_change()
    out["vol_ma20"] = out["volume"].rolling(20).mean()
    out["hh20"] = out["high"].rolling(20).max()
    out["ll20"] = out["low"].rolling(20).min()

    # derivative features (if present)
    out["oi_chg"] = out["oi"].pct_change()
    out["funding_z"] = (out["funding"] - out["funding"].rolling(50).mean()) / out["funding"].rolling(50).std()

    out.to_csv(f"data/{sym}_features_1h.csv", index=False)
    print(f"saved data/{sym}_features_1h.csv: {len(out)} rows")


if __name__ == "__main__":
    for s in ["BTCUSD", "SOLUSD"]:
        build_symbol(s)
