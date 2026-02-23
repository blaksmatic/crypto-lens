# v4 Roadmap

## Completed in this commit
- v4 architecture spec
- trend module v1
- squeeze module v1
- ensemble signal router v1
- risk helpers (position sizing + kill switch)
- v4 signal runner scaffold

## Next (immediate)
1. Add execution simulator to `backtest/v4_runner.py`
2. Add monthly walk-forward metrics + stability table
3. Add signal attribution PnL (trend vs squeeze vs confluence)
4. Integrate derivatives feed into squeeze quality filter

## Objective
Move from promising prototypes to robust, auditable strategy process.
