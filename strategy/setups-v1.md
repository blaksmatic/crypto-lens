# Setups v1 (BTC/SOL)

## Scope
- Symbols: BTC-USD, SOL-USD
- Timeframes: 4H (bias), 1H (execution)
- Allowed directions: both long and short

## Setup A — Trend Continuation Pullback (primary for BTC)

### Long
1. 4H trend = bullish (HH/HL structure)
2. 1H pulls back into prior demand zone / VWAP band
3. Liquidity sweep below local 1H swing low
4. Reclaim close back above sweep level
5. Trigger confirmation >= 3/4:
   - CVD confirms buyers stepping in
   - OI stabilizes or rises with reclaim
   - Funding not excessively crowded long
   - Reclaim candle volume > 20-period average

Entry: close of reclaim candle or 50% retrace of reclaim wick
Stop: below sweep low
Invalidation: 1H closes below sweep low
Targets: TP1 at prior 1H high, TP2 at 4H liquidity target

### Short
Mirror logic in bearish regime.

---

## Setup B — Squeeze Reversal (secondary for BTC, common for SOL)

### Long (short squeeze)
1. 4H not strongly bearish (score >= 5)
2. Funding negative and crowded short profile
3. OI drops while price stops making new lows (pressure release)
4. 1H sweep + reclaim of local range low
5. Trigger confirmation >= 3/4

Entry/Stop/Targets same structure as Setup A.

### Short (long squeeze)
Mirror logic with positive crowded funding and overhead sweep.

---

## Setup C — Range Rotation (primary for SOL in chop)

### Preconditions
1. 4H regime score 4-6 (transitional/chop)
2. Range boundaries clear on 1H (at least 3 touches total)

### Long
1. Sweep of range low
2. Reclaim inside range on above-average volume
3. OI does not expand aggressively against long
4. Trigger confirmation >= 3/4

Target: range mid then range high
Stop: below sweep extremity

### Short
Mirror at range high.

---

## Hard Exclusions
- No new entries within ±15 min of major high-impact macro releases
- No entry if spread/slippage exceeds instrument threshold
- No entry when trigger pass count < 3/4

## Versioning Rule
Any setup condition changes must be logged in `CHANGELOG.md` and tagged with date.
