import time
from datetime import datetime, timedelta, timezone

import pandas as pd
import requests

BASE = "https://api.exchange.coinbase.com/products/{product}/candles"


def fetch_coinbase_candles(product: str, granularity_sec: int, start: datetime, end: datetime) -> pd.DataFrame:
    rows = []
    cursor = start
    step = timedelta(seconds=granularity_sec * 300)  # Coinbase limit: 300 candles

    while cursor < end:
        batch_end = min(cursor + step, end)
        params = {
            "granularity": granularity_sec,
            "start": cursor.isoformat().replace("+00:00", "Z"),
            "end": batch_end.isoformat().replace("+00:00", "Z"),
        }
        r = requests.get(BASE.format(product=product), params=params, timeout=20)
        r.raise_for_status()
        batch = r.json()  # [time, low, high, open, close, volume]

        for item in batch:
            rows.append(item)

        cursor = batch_end
        time.sleep(0.08)

    if not rows:
        return pd.DataFrame(columns=["open_time", "open", "high", "low", "close", "volume", "close_time"])

    df = pd.DataFrame(rows, columns=["time", "low", "high", "open", "close", "volume"]).drop_duplicates("time")
    for c in ["open", "high", "low", "close", "volume"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    df["open_time"] = pd.to_datetime(df["time"], unit="s", utc=True)
    df["close_time"] = df["open_time"] + pd.to_timedelta(granularity_sec, unit="s")
    df = df.sort_values("open_time")
    return df[["open_time", "open", "high", "low", "close", "volume", "close_time"]]


if __name__ == "__main__":
    end = datetime.now(timezone.utc)
    start = end - timedelta(days=730)

    for product in ["BTC-USD", "SOL-USD"]:
        out = f"data/{product.replace('-', '')}_1h.csv"
        df = fetch_coinbase_candles(product, 3600, start, end)
        df.to_csv(out, index=False)
        print(f"saved {out}: {len(df)} rows")
