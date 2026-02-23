# crypto-lens

Crypto-native trading research framework focused on **BTC** and **SOL** using a **4H regime + 1H execution** model.

## Goal
Build and validate a durable edge through disciplined paper trading before any live deployment.

## Roadmap
1. Strategy spec (rules-first)
2. Backtest harness
3. Forward paper trading (2-3+ months)
4. Performance review + risk audit
5. Optional tiny-size live pilot

## Initial Structure
- `strategy/` - setup definitions, market lens logic
- `scoring/` - regime and trigger scorecards
- `execution/` - paper-trading protocol + risk controls
- `integrations/coinbase/` - live integration placeholders (disabled)
- `reports/` - daily/weekly performance templates

## Safety First
Live trading is out of scope until paper metrics pass pre-defined thresholds and explicit approval is given.
