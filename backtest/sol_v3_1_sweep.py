import itertools
import numpy as np
import pandas as pd


def ema(s, n):
    return s.ewm(span=n, adjust=False).mean()


def atr(df, n=14):
    pc = df['close'].shift(1)
    tr = pd.concat([(df['high']-df['low']).abs(), (df['high']-pc).abs(), (df['low']-pc).abs()], axis=1).max(axis=1)
    return tr.rolling(n).mean()


def run(df, lookback=24, tp_mult=2.2, max_hold=24, vol_mult=1.0, fee_bps=5, slip_bps=2):
    d = df.copy().sort_values('timestamp').reset_index(drop=True)
    d['ema20'] = ema(d['close'], 20)
    d['ema50'] = ema(d['close'], 50)
    d['ema200'] = ema(d['close'], 200)
    d['vol_ma20'] = d['volume'].rolling(20).mean()
    d['atr14'] = atr(d, 14)
    d['ret1'] = d['close'].pct_change()
    d['regime'] = 0
    d.loc[(d['ema50'] > d['ema200']) & (d['close'] > d['ema200']), 'regime'] = 1
    d.loc[(d['ema50'] < d['ema200']) & (d['close'] < d['ema200']), 'regime'] = -1

    trades, pos = [], None
    for i in range(max(220, lookback + 5), len(d)-1):
        row, prev, nxt = d.iloc[i], d.iloc[i-1], d.iloc[i+1]

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
            if exit_px is None and pos['bars'] >= max_hold:
                exit_px, reason = row['close'], 'timeout'
            if exit_px is not None:
                gross = (exit_px - pos['entry']) / pos['risk'] if pos['side'] == 'long' else (pos['entry'] - exit_px) / pos['risk']
                costs = ((fee_bps + slip_bps) * 2 / 10000) * (pos['entry'] / pos['risk'])
                trades.append({'R': gross - costs, 'entry_time': pos['entry_time'], 'exit_time': row['timestamp'], 'side': pos['side'], 'reason': reason})
                pos = None
            continue

        if np.isnan(row['atr14']) or np.isnan(row['vol_ma20']):
            continue

        low_n = d.iloc[i-lookback:i]['low'].min()
        high_n = d.iloc[i-lookback:i]['high'].max()
        vol_ok = row['volume'] > row['vol_ma20'] * vol_mult

        # primary: sweep + reclaim
        long_a = row['regime'] == 1 and row['low'] < low_n and row['close'] > prev['low'] and row['close'] > row['ema20'] and vol_ok
        short_a = row['regime'] == -1 and row['high'] > high_n and row['close'] < prev['high'] and row['close'] < row['ema20'] and vol_ok

        # secondary: momentum continuation after pullback (frequency booster)
        long_b = row['regime'] == 1 and prev['close'] < prev['ema20'] and row['close'] > row['ema20'] and row['ret1'] > 0.002 and vol_ok
        short_b = row['regime'] == -1 and prev['close'] > prev['ema20'] and row['close'] < row['ema20'] and row['ret1'] < -0.002 and vol_ok

        long_t = long_a or long_b
        short_t = short_a or short_b

        if long_t or short_t:
            side = 'long' if long_t else 'short'
            entry = nxt['open']
            risk = max(row['atr14'], entry * 0.002)
            stop = entry - risk if side == 'long' else entry + risk
            tp = entry + tp_mult * risk if side == 'long' else entry - tp_mult * risk
            pos = {'side': side, 'entry': entry, 'risk': risk, 'stop': stop, 'tp': tp, 'entry_time': nxt['timestamp'], 'bars': 0}

    return pd.DataFrame(trades)


def metrics(t):
    if t.empty:
        return {'trades': 0, 'pf': np.nan, 'exp': np.nan, 'dd': np.nan, 'wr': np.nan}
    wins = (t['R'] > 0).sum()
    gp = t.loc[t['R'] > 0, 'R'].sum()
    gl = -t.loc[t['R'] <= 0, 'R'].sum()
    pf = gp / gl if gl > 0 else np.nan
    eq = t['R'].cumsum()
    dd = (eq - eq.cummax()).min()
    return {'trades': int(len(t)), 'pf': float(pf), 'exp': float(t['R'].mean()), 'dd': float(dd), 'wr': float(wins/len(t))}


def walk_forward(d, params, windows=10):
    n = len(d)
    chunk = n // windows
    rows = []
    for i in range(2, windows):
        test = d.iloc[i*chunk:(i+1)*chunk].copy()
        m = metrics(run(test, **params))
        m['window'] = i
        rows.append(m)
    return pd.DataFrame(rows)


if __name__ == '__main__':
    d = pd.read_csv('data/SOLUSD_features_1h.csv', parse_dates=['timestamp'])
    grid = {
        'lookback': [16, 20, 24],
        'tp_mult': [1.8, 2.0, 2.2],
        'max_hold': [18, 24],
        'vol_mult': [0.9, 1.0],
    }

    results = []
    for lookback, tp_mult, max_hold, vol_mult in itertools.product(grid['lookback'], grid['tp_mult'], grid['max_hold'], grid['vol_mult']):
        p = {'lookback': lookback, 'tp_mult': tp_mult, 'max_hold': max_hold, 'vol_mult': vol_mult}
        wf = walk_forward(d, p)
        if wf.empty:
            continue
        avg_trades = wf['trades'].mean()
        if avg_trades < 4:
            continue
        stable = (wf['pf'] > 1.1).mean()
        score = wf['exp'].mean() - 0.03 * abs(wf['dd'].mean()) + 0.02 * avg_trades
        results.append({
            **p,
            'wf_windows': int(len(wf)),
            'avg_trades_per_window': float(avg_trades),
            'avg_pf': float(wf['pf'].mean(skipna=True)),
            'avg_exp': float(wf['exp'].mean()),
            'avg_dd': float(wf['dd'].mean()),
            'stability_ratio': float(stable),
            'score': float(score),
        })

    out = pd.DataFrame(results)
    if out.empty:
        print('BEST', {})
    else:
        out = out.sort_values(['score', 'avg_pf', 'avg_exp'], ascending=False)
        out.to_csv('reports/sol_v3_1_sweep.csv', index=False)
        print('BEST', out.head(1).iloc[0].to_dict())
