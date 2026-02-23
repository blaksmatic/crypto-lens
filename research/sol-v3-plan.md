# SOL-only v3 Plan

## Objective
Increase robustness of SOL strategy before paper deployment.

## Method
- Parameter sweep on sweep/reclaim logic
- Rolling walk-forward (multiple windows)
- Cost-aware performance (fees + slippage)

## Search Space
- lookback: 16, 20, 24, 30
- tp_mult: 1.8, 2.0, 2.2, 2.5
- max_hold: 18, 24, 30

## Selection Criteria
Primary:
- higher average expectancy
- PF > 1.1 on majority of windows
- lower average drawdown

Secondary:
- sufficient trade count per window
- consistency across regimes

## Go/No-Go (paper)
- avg PF >= 1.20
- avg expectancy >= +0.12R
- stability ratio >= 0.60
- no single-window collapse worse than -8R DD
