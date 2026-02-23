import os
import sys
import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from signals.trend_module_v1 import generate as trend_generate
from signals.squeeze_module_v1 import generate as squeeze_generate
from signals.ensemble_router_v1 import route

FEE_BPS = 5
SLIP_BPS = 2


def atr(df, n=14):
    pc = df['close'].shift(1)
    tr = pd.concat([(df['high']-df['low']).abs(), (df['high']-pc).abs(), (df['low']-pc).abs()], axis=1).max(axis=1)
    return tr.rolling(n).mean()


def summarize(t):
    if t.empty:
        return {'trades': 0, 'win_rate': 0, 'expectancy_R': 0, 'profit_factor': 0, 'max_dd_R': 0}
    wins = (t['R'] > 0).sum()
    gp = t.loc[t['R'] > 0, 'R'].sum()
    gl = -t.loc[t['R'] <= 0, 'R'].sum()
    pf = gp / gl if gl > 0 else np.nan
    eq = t['R'].cumsum()
    dd = (eq - eq.cummax()).min()
    return {'trades': int(len(t)), 'win_rate': round(float(wins/len(t)),4), 'expectancy_R': round(float(t['R'].mean()),4), 'profit_factor': round(float(pf),4) if pd.notna(pf) else None, 'max_dd_R': round(float(dd),4)}


def run_symbol(symbol):
    d0 = pd.read_csv(f'data/{symbol}_features_1h.csv', parse_dates=['timestamp']).sort_values('timestamp').reset_index(drop=True)
    trend = trend_generate(d0)
    squeeze = squeeze_generate(d0)
    d = route(d0, trend, squeeze)
    d['atr14'] = atr(d, 14)
    d['vol_ma20'] = d['volume'].rolling(20).mean()
    d['vol_ok_strict'] = d['volume'] > d['vol_ma20'] * 1.2
    d['abs_ret'] = d['close'].pct_change().abs()

    # stricter gating: only confluence or high-quality squeeze w/ funding extreme
    funding_col = 'funding' if 'funding' in d.columns else None
    if funding_col:
        d['funding_z'] = (d['funding'] - d['funding'].rolling(100).mean()) / d['funding'].rolling(100).std()
    else:
        d['funding_z'] = np.nan

    d['hq_long'] = d['long_signal'] & d['vol_ok_strict'] & (d['abs_ret'] > 0.0015)
    d['hq_short'] = d['short_signal'] & d['vol_ok_strict'] & (d['abs_ret'] > 0.0015)

    # require confluence OR funding extreme + squeeze source
    d['allow_long'] = False
    d['allow_short'] = False
    d.loc[(d['signal_source'] == 'confluence') & d['hq_long'], 'allow_long'] = True
    d.loc[(d['signal_source'] == 'confluence') & d['hq_short'], 'allow_short'] = True
    d.loc[(d['signal_source'] == 'squeeze') & d['hq_long'] & (d['funding_z'] < -1.0), 'allow_long'] = True
    d.loc[(d['signal_source'] == 'squeeze') & d['hq_short'] & (d['funding_z'] > 1.0), 'allow_short'] = True

    pos = None
    trades = []
    cooldown = 0

    for i in range(240, len(d)-1):
        row = d.iloc[i]
        nxt = d.iloc[i+1]

        if cooldown > 0:
            cooldown -= 1

        if pos is not None:
            hi, lo = row['high'], row['low']
            exit_px, reason = None, None
            if pos['side'] == 'long':
                if lo <= pos['stop']:
                    exit_px, reason = pos['stop'], 'stop'
                elif hi >= pos['tp']:
                    exit_px, reason = pos['tp'], 'tp'
            else:
                if hi >= pos['stop']:
                    exit_px, reason = pos['stop'], 'stop'
                elif lo <= pos['tp']:
                    exit_px, reason = pos['tp'], 'tp'
            pos['bars'] += 1
            if exit_px is None and pos['bars'] >= 18:
                exit_px, reason = row['close'], 'timeout'
            if exit_px is not None:
                gross = (exit_px - pos['entry'])/pos['risk'] if pos['side']=='long' else (pos['entry'] - exit_px)/pos['risk']
                costs = ((FEE_BPS + SLIP_BPS) * 2 / 10000) * (pos['entry']/pos['risk'])
                r = gross - costs
                trades.append({'symbol': symbol, 'entry_time': pos['entry_time'], 'exit_time': row['timestamp'], 'side': pos['side'], 'source': pos['source'], 'R': r, 'reason': reason})
                pos = None
                cooldown = 2
            continue

        if cooldown > 0 or pd.isna(row['atr14']):
            continue

        if bool(row['allow_long']) == bool(row['allow_short']):
            continue

        side = 'long' if bool(row['allow_long']) else 'short'
        entry = float(nxt['open'])
        risk = max(float(row['atr14']), entry * 0.002)
        tp_mult = 2.4
        stop = entry - risk if side == 'long' else entry + risk
        tp = entry + tp_mult*risk if side == 'long' else entry - tp_mult*risk
        pos = {'side': side, 'entry': entry, 'risk': risk, 'stop': stop, 'tp': tp, 'source': row.get('signal_source', 'unknown'), 'entry_time': nxt['timestamp'], 'bars': 0}

    t = pd.DataFrame(trades)
    t.to_csv(f'reports/{symbol}_trades_v4_1.csv', index=False)
    return summarize(t)


if __name__ == '__main__':
    rows = []
    for sym in ['SOLUSD', 'BTCUSD']:
        s = run_symbol(sym)
        print(sym, s)
        rows.append({'symbol': sym, **s})
    pd.DataFrame(rows).to_csv('reports/v4_1_summary.csv', index=False)
