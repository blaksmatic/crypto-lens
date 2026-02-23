# Coinalyze Integration

## Purpose
Provide derivatives context for crypto-native signals:
- Open Interest (OI)
- Funding rates

## Setup
1. Create API key at Coinalyze.
2. Export env var:
   - PowerShell: `$env:COINALYZE_API_KEY="your_key"`
3. Run:
   - `python data/fetch_coinalyze_derivatives.py`
   - `python data/build_features_v1.py`

## Output
- `data/BTCUSD_derivatives_1h.csv`
- `data/SOLUSD_derivatives_1h.csv`
- merged into `data/*_features_1h.csv`

## Notes
The symbol mapping in script uses perpetual index aliases and may need adjustment based on account/data plan.
