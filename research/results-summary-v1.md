# Results Summary v1 (price-only proxy backtest)

## Data
- Source: Coinbase Exchange candles (public)
- Symbols: BTCUSD, SOLUSD
- Horizon: ~2 years of 1H bars
- 4H regime derived from 1H resampling

## Strategy Under Test
A simplified v1 proxy:
- 4H regime: EMA50/EMA200 trend filter
- 1H trigger: EMA20 reclaim + volume confirmation
- Exit: 1 ATR stop, 2 ATR take-profit, 24-bar timeout

## Baseline Results

### BTCUSD
- Trades: 371
- Win rate: 35.31%
- Expectancy: +0.0465R
- Profit factor: 1.0736
- Max drawdown: -18.646R

### SOLUSD
- Trades: 395
- Win rate: 36.71%
- Expectancy: +0.0863R
- Profit factor: 1.1370
- Max drawdown: -28.4045R

### Combined
- Trades: 766
- Win rate: 36.03%
- Expectancy: +0.0670R
- Profit factor: 1.1062
- Max drawdown: -30.6319R

## Interpretation
- Positive but weak edge in this proxy model.
- Profit factor is below desired forward-test gate (1.20+).
- Drawdown profile is too deep for deployment.

## Next Iteration Priorities
1. Add structure-aware trigger (sweep + reclaim logic, not EMA-only).
2. Add regime-specific sizing and stricter no-trade filters.
3. Add fee/slippage modeling explicitly.
4. Add out-of-sample and walk-forward reporting tables.

This is a starting baseline, not production-ready performance.
