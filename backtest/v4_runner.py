import os
import sys
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from signals.trend_module_v1 import generate as trend_generate
from signals.squeeze_module_v1 import generate as squeeze_generate
from signals.ensemble_router_v1 import route


def run(symbol: str = "SOLUSD"):
    df = pd.read_csv(f"data/{symbol}_features_1h.csv", parse_dates=["timestamp"])
    tdf = trend_generate(df)
    sdf = squeeze_generate(df)
    routed = route(df, tdf, sdf)

    # summary only (execution sim hooks in next step)
    out = pd.DataFrame({
        "timestamp": routed["timestamp"],
        "long_signal": routed["long_signal"],
        "short_signal": routed["short_signal"],
        "signal_source": routed["signal_source"],
    })
    out.to_csv(f"reports/{symbol}_signals_v4.csv", index=False)

    stats = {
        "symbol": symbol,
        "long_signals": int(out["long_signal"].sum()),
        "short_signals": int(out["short_signal"].sum()),
        "trend_signals": int((out["signal_source"] == "trend").sum()),
        "squeeze_signals": int((out["signal_source"] == "squeeze").sum()),
        "confluence_signals": int((out["signal_source"] == "confluence").sum()),
    }
    return stats


if __name__ == "__main__":
    for sym in ["SOLUSD", "BTCUSD"]:
        print(run(sym))
