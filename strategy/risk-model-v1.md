# Risk Model v1

## Position Risk
- Unit risk: 1R = 0.5% of paper equity
- Max concurrent exposure: 2.0R total open risk
- BTC sizing factor: 1.0x base
- SOL sizing factor: 0.75x base (higher beta)

## Trade Limits
- Max trades/day: 4
- Max losses/day: 3 trades or 2R (whichever first)
- Weekly hard stop: -6R

## Stop Placement
- Structural stop only (beyond sweep/invalid level)
- No widening stop after entry
- Can tighten to breakeven only after TP1 hit or structure confirms

## Profit Taking
- TP1: 1.0R to 1.5R (take 40-60%)
- TP2: opposing liquidity / structure objective
- Runner: optional 10-20% with trailing stop by 1H swing

## Kill Switches
Pause strategy if any condition triggers:
1. 6 consecutive losses
2. 8-week rolling expectancy < 0
3. 8-week rolling profit factor < 1.1
4. Rule-drift incident (manual override outside system)

## Re-Enable Criteria
- Post-mortem completed
- Parameter changes documented
- 10-trade probation with half risk (0.25% per trade)
