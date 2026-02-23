# SOL v3.1 Results (frequency-boosted walk-forward)

## What changed
- Added secondary momentum-continuation trigger to increase trade count.
- Added minimum trade density filter in sweep ranking.
- 8-window walk-forward evaluation.

## Best observed config
- lookback: 16
- tp_mult: 2.2
- max_hold: 18
- vol_mult: 0.9

## Metrics (best)
- avg trades/window: 39.38
- avg PF: 1.03
- avg expectancy: +0.009R
- avg max DD: -7.58R
- stability ratio (PF > 1.1 windows): 0.375

## Interpretation
- Good: trade frequency is now adequate for statistical analysis.
- Bad: edge quality is weak and unstable (PF near 1.0, low stability).

## Decision
**NO-GO** for paper deployment under current rules.

## Next targets (v3.2)
1. Reintroduce strict structure quality filter (swing confirmation).
2. Use derivatives context (OI/funding) to avoid low-quality continuation entries.
3. Separate trend and range sub-strategies with independent risk budgets.
4. Add session/time-of-day filter for SOL microstructure behavior.
