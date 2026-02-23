# Backtesting Plan v1 (BTC/SOL, 1H/4H)

## Principle
No "wisdom" without evidence. We test hypotheses, then keep only what survives.

## Data Requirements
- OHLCV: 1H and 4H bars for BTC-USD, SOL-USD
- Derivatives proxies where available: OI, funding, basis
- Minimum history: 24 months preferred

## Test Layers
1. **Rule fidelity test**
   - Ensure setups can be labeled deterministically from data
2. **In-sample / out-of-sample split**
   - 70% development, 30% holdout by time
3. **Walk-forward test**
   - Monthly re-evaluation with fixed rule set
4. **Stress windows**
   - High-volatility periods
   - Low-liquidity/chop periods

## Evaluation Metrics
- Expectancy (R)
- Profit factor
- Max drawdown (R)
- Return over max DD
- Hit rate by setup type
- Stability across months (consistency > peak performance)

## Robustness Checks
- Slippage sensitivity: +25%, +50%, +100%
- Fee sensitivity by venue profile
- Entry timing perturbation (+/-1 candle)
- Stop perturbation (+/-10%)

## Acceptance Criteria for Forward Paper
- PF >= 1.20 in holdout
- Expectancy >= +0.10R
- No single month contributes >35% of total edge
- No catastrophic regime dependency

## Deliverables
- `research/results-summary-v1.md`
- `reports/monthly-metrics.csv`
- setup-level confusion/edge table
