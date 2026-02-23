# Results Summary v2 (sweep/reclaim + cost-aware holdout)

## What changed from v1
- 1H trigger upgraded to sweep/reclaim proxy (20-bar liquidity sweep + reclaim)
- Added transaction cost model (fee + slippage assumptions)
- Holdout-only evaluation (~last 30% of data)
- Optional derivatives hooks (OI/funding) now supported if present

## Data
- Coinbase candles (BTCUSD, SOLUSD), ~2 years 1H
- Derivatives columns optional (currently empty unless API configured)

## Results (holdout)

### BTCUSD
- Trades: 10
- Win rate: 20.00%
- Expectancy: -0.6142R
- Profit factor: 0.3879
- Max DD: -8.7762R

### SOLUSD
- Trades: 8
- Win rate: 62.50%
- Expectancy: +0.7650R
- Profit factor: 2.8441
- Max DD: -1.1153R

### Combined
- Trades: 18
- Win rate: 38.89%
- Expectancy: -0.0012R
- Profit factor: 0.9984
- Max DD: -8.7762R

## Read
- v2 is too selective and unstable across symbols.
- SOL profile looked promising in this slice; BTC profile degraded.
- Not yet robust enough for promotion.

## Next improvements
1. Parameter grid by symbol (BTC != SOL trigger sensitivity).
2. Add proper swing-point logic for reclaim validation.
3. Plug OI/funding data and enforce regime-quality filters.
4. Expand walk-forward to rolling windows and monthly stability table.
