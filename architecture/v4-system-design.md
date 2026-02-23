# crypto-lens v4 System Design

## Goal
Build a robust crypto-native research and execution architecture with clear separation between signal generation, risk governance, and execution plumbing.

## Layers

### 1) Data Layer
- `data/fetch_coinbase_ohlcv.py` (existing equivalent)
- `data/fetch_coinalyze_derivatives.py`
- Unified schema output:
  - `timestamp, symbol, open, high, low, close, volume, oi, funding, basis, liq_long, liq_short`

### 2) Feature Layer
- `features/build_core_features.py`
- `features/build_microstructure_features.py`
- Outputs:
  - trend state
  - squeeze pressure metrics
  - liquidation proximity proxies

### 3) Signal Layer
- `signals/trend_module_v1.py`
- `signals/squeeze_module_v1.py`
- Strategy combiner:
  - `signals/ensemble_router_v1.py`

### 4) Risk Layer
- `risk/position_sizing.py`
- `risk/kill_switch.py`
- `risk/exposure_budget.py`

### 5) Backtest Layer
- `backtest/v4_runner.py`
- rolling walk-forward reports
- per-module attribution + blended attribution

### 6) Deployment Layer (future)
- paper trader first
- optional live router after promotion gate pass

## Promotion Gate
- Avg PF >= 1.20
- Avg Expectancy >= +0.12R
- Stability ratio >= 0.60
- Max rolling DD <= 10R
- No single month > 30% of total PnL
