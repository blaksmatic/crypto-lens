def risk_fraction(symbol: str, signal_source: str) -> float:
    base = 0.005  # 0.5%
    if symbol.upper().startswith("SOL"):
        base *= 0.75
    if signal_source == "confluence":
        base *= 1.15
    if signal_source == "squeeze":
        base *= 0.85
    return max(0.001, min(base, 0.0075))
