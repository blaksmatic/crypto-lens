import math
import pandas as pd


def ema(s: pd.Series, n: int) -> pd.Series:
    return s.ewm(span=n, adjust=False).mean()


def atr(df: pd.DataFrame, n: int = 14) -> pd.Series:
    prev_close = df["close"].shift(1)
    tr = pd.concat([
        (df["high"] - df["low"]).abs(),
        (df["high"] - prev_close).abs(),
        (df["low"] - prev_close).abs(),
    ], axis=1).max(axis=1)
    return tr.rolling(n).mean()


def build_regime_from_1h(df1h: pd.DataFrame) -> pd.DataFrame:
    r = df1h.set_index("open_time").resample("4h").agg(
        open=("open", "first"),
        high=("high", "max"),
        low=("low", "min"),
        close=("close", "last"),
        volume=("volume", "sum"),
    ).dropna().reset_index()
    r["close_time"] = r["open_time"] + pd.to_timedelta(4, unit="h")
    r["ema50"] = ema(r["close"], 50)
    r["ema200"] = ema(r["close"], 200)
    r["regime"] = 0
    r.loc[(r["close"] > r["ema200"]) & (r["ema50"] > r["ema200"]), "regime"] = 1
    r.loc[(r["close"] < r["ema200"]) & (r["ema50"] < r["ema200"]), "regime"] = -1
    return r[["close_time", "regime"]]


def run_symbol(df1h: pd.DataFrame, regime_df: pd.DataFrame, symbol: str):
    d = df1h.copy()
    d["ema20"] = ema(d["close"], 20)
    d["vol_ma20"] = d["volume"].rolling(20).mean()
    d["atr14"] = atr(d, 14)

    reg = regime_df.rename(columns={"close_time": "t4h"}).copy()
    d = d.sort_values("close_time")
    reg = reg.sort_values("t4h")
    d = pd.merge_asof(d, reg, left_on="close_time", right_on="t4h", direction="backward")

    trades = []
    pos = None
    max_hold = 24

    for i in range(25, len(d) - 1):
        row = d.iloc[i]
        nxt = d.iloc[i + 1]
        if any(math.isnan(x) for x in [row["ema20"], row["vol_ma20"], row["atr14"]]):
            continue

        if pos is not None:
            pos["bars"] += 1
            hi = row["high"]
            lo = row["low"]
            exit_price = None
            reason = None
            if pos["side"] == "long":
                if lo <= pos["stop"]:
                    exit_price, reason = pos["stop"], "stop"
                elif hi >= pos["tp"]:
                    exit_price, reason = pos["tp"], "tp"
            else:
                if hi >= pos["stop"]:
                    exit_price, reason = pos["stop"], "stop"
                elif lo <= pos["tp"]:
                    exit_price, reason = pos["tp"], "tp"

            if exit_price is None and pos["bars"] >= max_hold:
                exit_price, reason = row["close"], "timeout"

            if exit_price is not None:
                r = (exit_price - pos["entry"]) / pos["risk"] if pos["side"] == "long" else (pos["entry"] - exit_price) / pos["risk"]
                trades.append({
                    "symbol": symbol,
                    "entry_time": pos["entry_time"],
                    "exit_time": row["close_time"],
                    "side": pos["side"],
                    "entry": pos["entry"],
                    "exit": exit_price,
                    "R": r,
                    "reason": reason,
                })
                pos = None
            continue

        regime = int(row.get("regime", 0)) if pd.notna(row.get("regime", 0)) else 0
        vol_ok = row["volume"] > row["vol_ma20"]

        # Simple 1H trigger proxy: reclaim of EMA20 with volume in regime direction
        long_trigger = regime == 1 and row["close"] > row["ema20"] and d.iloc[i - 1]["close"] <= d.iloc[i - 1]["ema20"] and vol_ok
        short_trigger = regime == -1 and row["close"] < row["ema20"] and d.iloc[i - 1]["close"] >= d.iloc[i - 1]["ema20"] and vol_ok

        if long_trigger or short_trigger:
            side = "long" if long_trigger else "short"
            entry = nxt["open"]
            risk = max(row["atr14"], entry * 0.002)
            if side == "long":
                stop = entry - risk
                tp = entry + 2 * risk
            else:
                stop = entry + risk
                tp = entry - 2 * risk
            pos = {
                "side": side,
                "entry": entry,
                "stop": stop,
                "tp": tp,
                "risk": risk,
                "entry_time": nxt["open_time"],
                "bars": 0,
            }

    return pd.DataFrame(trades)


def summarize(trades: pd.DataFrame):
    if trades.empty:
        return {"trades": 0}
    wins = (trades["R"] > 0).sum()
    losses = (trades["R"] <= 0).sum()
    gp = trades.loc[trades["R"] > 0, "R"].sum()
    gl = -trades.loc[trades["R"] <= 0, "R"].sum()
    pf = gp / gl if gl > 0 else float("inf")
    eq = trades["R"].cumsum()
    dd = (eq - eq.cummax()).min()
    return {
        "trades": int(len(trades)),
        "win_rate": round(wins / len(trades), 4),
        "expectancy_R": round(trades["R"].mean(), 4),
        "profit_factor": round(pf, 4),
        "max_dd_R": round(float(dd), 4),
    }


if __name__ == "__main__":
    all_trades = []
    for sym in ["BTCUSD", "SOLUSD"]:
        df1 = pd.read_csv(f"data/{sym}_1h.csv", parse_dates=["open_time", "close_time"])
        reg = build_regime_from_1h(df1)
        t = run_symbol(df1, reg, sym)
        t.to_csv(f"reports/{sym}_trades_v1.csv", index=False)
        s = summarize(t)
        print(sym, s)
        all_trades.append(t)

    all_df = pd.concat(all_trades, ignore_index=True) if all_trades else pd.DataFrame()
    all_df.to_csv("reports/all_trades_v1.csv", index=False)
    print("ALL", summarize(all_df))
