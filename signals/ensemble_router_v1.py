import pandas as pd


def route(df: pd.DataFrame, trend_df: pd.DataFrame, squeeze_df: pd.DataFrame) -> pd.DataFrame:
    d = df.merge(trend_df, on="timestamp", how="left").merge(squeeze_df, on="timestamp", how="left")

    d["long_signal"] = d["trend_long"].fillna(False) | d["squeeze_long"].fillna(False)
    d["short_signal"] = d["trend_short"].fillna(False) | d["squeeze_short"].fillna(False)

    # attribution tag
    d["signal_source"] = "none"
    d.loc[d["trend_long"] | d["trend_short"], "signal_source"] = "trend"
    d.loc[d["squeeze_long"] | d["squeeze_short"], "signal_source"] = "squeeze"
    d.loc[(d["trend_long"] | d["trend_short"]) & (d["squeeze_long"] | d["squeeze_short"]), "signal_source"] = "confluence"

    return d
