# No-Trade Filters v1

## Market Structure Filters
- Skip if 4H regime score is 5-6 and 1H has no clean range boundaries
- Skip if last 6x 1H candles are overlapping with declining volume (dead chop)

## Event Filters
- Skip new entries ±15 min around high-impact US macro events
- Skip during exchange outage/degraded data conditions

## Derivatives Stress Filters
- Skip if funding is > +0.05% (crowded longs) and long setup not a squeeze fade
- Skip if funding is < -0.05% (crowded shorts) and short setup not a squeeze fade
- Skip if abrupt OI spike (>2.5x recent 1H baseline) without clear reclaim confirmation

## Execution Quality Filters
- Skip if spread > 0.04% BTC or > 0.08% SOL
- Skip if expected slippage > 0.10R
- Skip if stop distance implies size below minimum practical lot

## Behavioral Filters
- Skip if daily loss limit already hit
- Skip if setup rationale cannot be written in one sentence
