import os
import sys
import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from signals.trend_module_v1 import generate as trend_generate
from signals.squeeze_module_v1 import generate as squeeze_generate
from signals.ensemble_router_v1 import route

FEE_BPS = 5
SLIP_BPS = 2


def atr(df: pd.DataFrame, n: int = 14):
    pc = df["close"].shift(1)
    tr = pd.concat([
        (df["high"] - df["low"]).abs(),
        (df["high"] - pc).abs(),
        (df["low"] - pc).abs(),
    ], axis=1).max(axis=1)
    return tr.rolling(n).mean()


def summarize(t: pd.DataFrame):
    if t.empty:
        return {"trades": 0, "win_rate": 0, "expectancy_R": 0, "profit_factor": 0, "max_dd_R": 0}
    wins = (t["R"] > 0).sum()
    gp = t.loc[t["R"] > 0, "R"].sum()
    gl = -t.loc[t["R"] <= 0, "R"].sum()
    pf = gp / gl if gl > 0 else np.nan
    eq = t["R"].cumsum()
    dd = (eq - eq.cummax()).min()
    return {
        "trades": int(len(t)),
        "win_rate": round(float(wins / len(t)), 4),
        "expectancy_R": round(float(t["R"].mean()), 4),
        "profit_factor": round(float(pf), 4) if pd.notna(pf) else None,
        "max_dd_R": round(float(dd), 4),
    }


def run_symbol(symbol: str):
    df = pd.read_csv(f"data/{symbol}_features_1h.csv", parse_dates=["timestamp"])
    trend = trend_generate(df)
    squeeze = squeeze_generate(df)
    d = route(df, trend, squeeze).sort_values("timestamp").reset_index(drop=True)
    d["atr14"] = atr(d, 14)

    pos = None
    trades = []

    for i in range(220, len(d) - 1):
        row = d.iloc[i]
        nxt = d.iloc[i + 1]

        if pos is not None:
            hi, lo = row["high"], row["low"]
            exit_px, reason = None, None
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
                gross = (exit_px - pos["entry"]) / pos["risk"] if pos["side"] == "long" else (pos["entry"] - exit_px) / pos["risk"]
                costs = ((FEE_BPS + SLIP_BPS) * 2 / 10000) * (pos["entry"] / pos["risk"])
                net = gross - costs
                trades.append({
                    "symbol": symbol,
                    "entry_time": pos["entry_time"],
                    "exit_time": row["timestamp"],
                    "side": pos["side"],
                    "source": pos["source"],
                    "R": net,
                    "reason": reason,
                })
                pos = None
            continue

        if pd.isna(row["atr14"]):
            continue

        if bool(row["long_signal"]) == bool(row["short_signal"]):
            continue

        side = "long" if bool(row["long_signal"]) else "short"
        entry = float(nxt["open"])
        risk = max(float(row["atr14"]), entry * 0.002)

        if side == "long":
            stop, tp = entry - risk, entry + 2.2 * risk
        else:
            stop, tp = entry + risk, entry - 2.2 * risk

        pos = {
            "side": side,
            "entry": entry,
            "risk": risk,
            "stop": stop,
            "tp": tp,
            "source": row.get("signal_source", "unknown"),
            "entry_time": nxt["timestamp"],
            "bars": 0,
        }

    tdf = pd.DataFrame(trades)
    tdf.to_csv(f"reports/{symbol}_trades_v4.csv", index=False)

    overall = summarize(tdf)
    by_source = {}
    if not tdf.empty:
        for s, g in tdf.groupby("source"):
            by_source[s] = summarize(g)

    return overall, by_source


if __name__ == "__main__":
    rows = []
    for sym in ["SOLUSD", "BTCUSD"]:
        ov, src = run_symbol(sym)
        print(sym, ov)
        for k, v in src.items():
            print(f"  {k}: {v}")
        rows.append({"symbol": sym, **ov})

    out = pd.DataFrame(rows)
    out.to_csv("reports/v4_summary.csv", index=False)
