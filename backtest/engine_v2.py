import numpy as np
import pandas as pd


FEE_BPS = 5  # per side
SLIP_BPS = 2  # per side


def ema(s: pd.Series, n: int) -> pd.Series:
    return s.ewm(span=n, adjust=False).mean()


def atr(df: pd.DataFrame, n: int = 14):
    pc = df["close"].shift(1)
    tr = pd.concat([(df["high"] - df["low"]).abs(), (df["high"] - pc).abs(), (df["low"] - pc).abs()], axis=1).max(axis=1)
    return tr.rolling(n).mean()


def add_regime(df: pd.DataFrame):
    d = df.copy()
    d["ema50"] = ema(d["close"], 50)
    d["ema200"] = ema(d["close"], 200)
    d["regime"] = 0
    d.loc[(d["ema50"] > d["ema200"]) & (d["close"] > d["ema200"]), "regime"] = 1
    d.loc[(d["ema50"] < d["ema200"]) & (d["close"] < d["ema200"]), "regime"] = -1
    return d


def trigger_sweep_reclaim(d: pd.DataFrame, i: int):
    row = d.iloc[i]
    prev = d.iloc[i - 1]
    low_n = d.iloc[i - 20:i]["low"].min()
    high_n = d.iloc[i - 20:i]["high"].max()
    vol_ok = row["volume"] > row["vol_ma20"]

    long_cond = (
        row["regime"] == 1
        and row["low"] < low_n
        and row["close"] > prev["low"]
        and row["close"] > row["ema20"]
        and vol_ok
    )
    short_cond = (
        row["regime"] == -1
        and row["high"] > high_n
        and row["close"] < prev["high"]
        and row["close"] < row["ema20"]
        and vol_ok
    )

    # Optional derivative confirmation (if available)
    if long_cond and pd.notna(row.get("oi_chg", np.nan)):
        long_cond = long_cond and (row["oi_chg"] > -0.03)
    if short_cond and pd.notna(row.get("oi_chg", np.nan)):
        short_cond = short_cond and (row["oi_chg"] > -0.03)

    return long_cond, short_cond


def run(df: pd.DataFrame, symbol: str):
    d = add_regime(df)
    d["ema20"] = ema(d["close"], 20)
    d["vol_ma20"] = d["volume"].rolling(20).mean()
    d["atr14"] = atr(d, 14)

    trades = []
    pos = None

    for i in range(220, len(d) - 1):
        row = d.iloc[i]
        nxt = d.iloc[i + 1]

        if pos is not None:
            hi, lo = row["high"], row["low"]
            exit_px = None
            reason = None
            if pos["side"] == "long":
                if lo <= pos["stop"]:
                    exit_px, reason = pos["stop"], "stop"
                elif hi >= pos["tp"]:
                    exit_px, reason = pos["tp"], "tp"
            else:
                if hi >= pos["stop"]:
                    exit_px, reason = pos["stop"], "stop"
                elif lo <= pos["tp"]:
                    exit_px, reason = pos["tp"], "tp"

            pos["bars"] += 1
            if exit_px is None and pos["bars"] >= 24:
                exit_px, reason = row["close"], "timeout"

            if exit_px is not None:
                costs = (FEE_BPS + SLIP_BPS) * 2 / 10000
                gross = (exit_px - pos["entry"]) / pos["risk"] if pos["side"] == "long" else (pos["entry"] - exit_px) / pos["risk"]
                net = gross - costs * (pos["entry"] / pos["risk"])
                trades.append({"symbol": symbol, "entry_time": pos["entry_time"], "exit_time": row["timestamp"], "side": pos["side"], "R": net, "reason": reason})
                pos = None
            continue

        if pd.isna(row["atr14"]) or pd.isna(row["vol_ma20"]):
            continue

        long_t, short_t = trigger_sweep_reclaim(d, i)
        if not long_t and not short_t:
            continue

        side = "long" if long_t else "short"
        entry = nxt["open"]
        risk = max(row["atr14"], entry * 0.002)
        tp_mult = 2.2 if symbol == "BTCUSD" else 2.0

        if side == "long":
            stop = entry - risk
            tp = entry + tp_mult * risk
        else:
            stop = entry + risk
            tp = entry - tp_mult * risk

        pos = {"side": side, "entry": entry, "risk": risk, "stop": stop, "tp": tp, "entry_time": nxt["timestamp"], "bars": 0}

    return pd.DataFrame(trades)


def summary(df: pd.DataFrame):
    if df.empty:
        return {"trades": 0}
    wins = (df["R"] > 0).sum()
    gp = df.loc[df["R"] > 0, "R"].sum()
    gl = -df.loc[df["R"] <= 0, "R"].sum()
    pf = gp / gl if gl > 0 else np.inf
    eq = df["R"].cumsum()
    dd = (eq - eq.cummax()).min()
    return {"trades": int(len(df)), "win_rate": round(float(wins / len(df)), 4), "expectancy_R": round(float(df["R"].mean()), 4), "profit_factor": round(float(pf), 4), "max_dd_R": round(float(dd), 4)}


def walk_forward(df: pd.DataFrame, symbol: str):
    d = df.sort_values("timestamp").reset_index(drop=True)
    n = len(d)
    train = int(n * 0.7)
    # fixed-rule walk-forward proxy: evaluate holdout only
    holdout = d.iloc[train:].copy()
    t = run(holdout, symbol)
    return t


if __name__ == "__main__":
    all_t = []
    for sym in ["BTCUSD", "SOLUSD"]:
        d = pd.read_csv(f"data/{sym}_features_1h.csv", parse_dates=["timestamp"])
        t = walk_forward(d, sym)
        t.to_csv(f"reports/{sym}_trades_v2.csv", index=False)
        print(sym, summary(t))
        all_t.append(t)

    z = pd.concat(all_t, ignore_index=True) if all_t else pd.DataFrame()
    z.to_csv("reports/all_trades_v2.csv", index=False)
    print("ALL", summary(z))
