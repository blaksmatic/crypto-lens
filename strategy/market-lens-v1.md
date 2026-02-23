# Market Lens v1 (BTC/SOL)

## Timeframe Roles
- **4H:** Regime / directional bias
- **1H:** Entry and risk execution

## 4H Regime Score (0-10)
1. Structure (HH/HL vs LH/LL)
2. Open Interest trend vs price
3. Funding regime (persistent + / - / flip)
4. Basis condition (healthy / stretched / backwardation)
5. Nearby liquidation clusters

Interpretation:
- 8-10: Trend continuation regime
- 5-7: Transitional / squeeze-prone
- 0-4: Mean-reversion / defensive

## 1H Trigger Rules
Require >=3 confirmations:
- Liquidity sweep + reclaim
- CVD divergence or confirmation
- OI/funding micro-shift aligned with direction
- Relative volume expansion on reclaim candle

## Instruments
- Primary: BTC-USD, SOL-USD (spot/perp references)

## Invalidation
- Long: 1H reclaim low broken
- Short: 1H reclaim high broken

## Notes
No discretionary overrides in v1. Rule changes must be versioned.
