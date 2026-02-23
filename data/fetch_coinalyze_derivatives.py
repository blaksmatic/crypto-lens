import os
import time
from datetime import datetime, timezone

import pandas as pd
import requests

BASE = "https://api.coinalyze.net/v1"


def _get(path: str, params: dict):
    api_key = os.getenv("COINALYZE_API_KEY")
    if not api_key:
        raise RuntimeError("COINALYZE_API_KEY is not set")
    headers = {"api_key": api_key}
    r = requests.get(f"{BASE}{path}", params=params, headers=headers, timeout=30)
    r.raise_for_status()
    return r.json()


def fetch_history(symbol: str, endpoint: str, interval: str, from_ts: int, to_ts: int) -> pd.DataFrame:
    payload = _get(endpoint, {"symbols": symbol, "interval": interval, "from": from_ts, "to": to_ts})
    if not payload:
        return pd.DataFrame()
    # Coinalyze shape may vary by endpoint; normalize [t, value]
    data = payload[0].get("history", []) if isinstance(payload, list) else payload.get("history", [])
    if not data:
        return pd.DataFrame()
    df = pd.DataFrame(data)
    if "t" in df.columns:
        df["timestamp"] = pd.to_datetime(df["t"], unit="s", utc=True)
    elif "time" in df.columns:
        df["timestamp"] = pd.to_datetime(df["time"], unit="s", utc=True)
    return df


def fetch_symbol_pack(symbol: str, interval: str = "1hour", days: int = 365):
    now = int(datetime.now(timezone.utc).timestamp())
    start = now - days * 86400

    oi = fetch_history(symbol, "/open-interest-history", interval, start, now)
    fr = fetch_history(symbol, "/funding-rate-history", interval, start, now)

    out = pd.DataFrame()
    if not oi.empty:
        oi_val_col = "c" if "c" in oi.columns else [c for c in oi.columns if c not in ("t", "time", "timestamp")][0]
        out = oi[["timestamp", oi_val_col]].rename(columns={oi_val_col: "oi"})

    if not fr.empty:
        fr_val_col = "c" if "c" in fr.columns else [c for c in fr.columns if c not in ("t", "time", "timestamp")][0]
        fr_df = fr[["timestamp", fr_val_col]].rename(columns={fr_val_col: "funding"})
        out = fr_df if out.empty else out.merge(fr_df, on="timestamp", how="outer")

    out = out.sort_values("timestamp") if not out.empty else out
    return out


if __name__ == "__main__":
    mappings = {
        "BTCUSD": "BTCUSDT_PERP.A",
        "SOLUSD": "SOLUSDT_PERP.A",
    }
    for sym, c_symbol in mappings.items():
        try:
            df = fetch_symbol_pack(c_symbol, interval="1hour", days=730)
            out = f"data/{sym}_derivatives_1h.csv"
            df.to_csv(out, index=False)
            print(f"saved {out}: {len(df)} rows")
            time.sleep(0.2)
        except Exception as e:
            print(f"skip {sym}: {e}")
