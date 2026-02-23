# Paper Trading Protocol (v1)

## Objective
Validate whether crypto-lens produces a robust edge before live trading.

## Duration
- Minimum forward period: **12 weeks**
- Preferred: **16+ weeks**

## Risk Rules
- Risk per trade: 0.5% notional-equivalent (paper)
- Max daily loss: 2R
- Max weekly loss: 6R
- Loss streak kill switch: 6 consecutive losses -> pause and review

## Trade Lifecycle
1. Regime score recorded (4H)
2. Trigger checklist recorded (1H)
3. Entry/SL/TP logged before "fill"
4. Post-trade tag: continuation / squeeze / fade / invalid setup

## Metrics
- Win rate
- Profit factor
- Expectancy (R)
- Max drawdown (R)
- Average hold time
- Setup-specific performance

## Promotion Gate to Live Pilot
All conditions must pass over rolling 8-week window:
- Profit factor >= 1.30
- Expectancy >= +0.20R
- Max DD <= 12R
- No unresolved rule-drift incidents

## Governance
Any rule change resets validation clock unless change is minor and documented.
