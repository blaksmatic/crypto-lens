# Scoring Weights v1

## 4H Regime Score (0-10)
- Structure alignment: 0-3
- OI trend alignment: 0-2
- Funding regime health: 0-2
- Basis condition: 0-1
- Liquidity map path quality: 0-2

Interpretation:
- 8-10: Strong trend regime
- 5-7: Transition / squeeze-prone
- 0-4: Defensive / mean-reversion only

## 1H Trigger Score (0-4)
- Sweep + reclaim present: 1
- CVD confirms/diverges favorably: 1
- OI/funding micro-shift aligns: 1
- Volume expansion on trigger candle: 1

Entry rule: trigger score >= 3 and regime score >= 5

## Symbol Bias Overrides
- BTC: continuation setups allowed at regime >= 7
- SOL: range/reversal setups allowed at regime 4-6 with strict stops

## Confidence Tier
- Tier A: Regime >= 8 and Trigger 4/4
- Tier B: Regime 6-7 and Trigger 3-4/4
- Tier C: Regime 5 and Trigger 3/4 (reduced size at 0.5x)
