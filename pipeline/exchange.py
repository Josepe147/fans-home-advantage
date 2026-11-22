"""Other prices: (1) the ghost-period shortfall at best-market and average closing prices, not just Pinnacle,
(2) Betfair Exchange closing prices 2024/25 onwards against Pinnacle, (3) crowd features against the exchange price."""
import pandas as pd, numpy as np, glob, os
from reflib import ols
m = pd.read_pickle('work/feat2.pkl')
raw = []
for f in sorted(glob.glob('fd/E[01]_*.csv')):
    d = pd.read_csv(f, encoding='latin1', on_bad_lines='skip')
    if 'MaxCH' not in d: continue
    d['league'] = os.path.basename(f)[:2]; d['Date'] = pd.to_datetime(d.Date, dayfirst=True, format='mixed')
    raw.append(d[['league', 'Date', 'HomeTeam'] + [c for c in ['MaxCH', 'MaxCD', 'MaxCA', 'MaxH', 'MaxD', 'MaxA', 'BFEH', 'BFED', 'BFEA'] if c in d]])
m = m.merge(pd.concat(raw), on=['league', 'Date', 'HomeTeam'], how='left')
rng = np.random.default_rng(1)
def roi(x, col, win, comm=0.0):
    o = x[col].astype(float); r = np.where(x[win] == 1, (o - 1) * (1 - comm), -1.0); r = r[~np.isnan(o)]
    bs = [rng.choice(r, len(r)).mean() for _ in range(4000)]
    return f'{r.mean()*100:+5.1f}% [{np.percentile(bs,2.5)*100:+5.1f}, {np.percentile(bs,97.5)*100:+5.1f}] n={len(r)}'
print('1. GHOST GAMES: back every away team, by price source')
g = m[m.crowd == 'ghost']
for name, x in [('both leagues', g), ('EPL', g[g.league == 'E0']), ('Championship', g[g.league == 'E1'])]:
    print(f' {name}')
    for lab, col in [('Pinnacle close', 'PSCA'), ('Pinnacle open', 'PSA'), ('Bet365', 'B365A'), ('market average close', 'AvgCA'), ('best price at close', 'MaxCA')]:
        print(f'   {lab:22s} {roi(x, col, "aw")}')
pre = m[(m.crowd == 'full') & (m.season.between(2015, 2019)) & (m.Date <= '2020-03-11')]
print(' pre-Covid crowd games 2015/16 to Mar 2020, away at Pinnacle close:', roi(pre, 'PSCA', 'aw'), '| best price (2019/20 only):', roi(pre, 'MaxCA', 'aw'))
print('2. BETFAIR EXCHANGE v PINNACLE, closing prices, crowd games 2024/25 on')
x = m[m.BFECH.notna() & m.PSCH.notna() & (m.crowd == 'full')].copy()
inv = 1 / x[['BFECH', 'BFECD', 'BFECA']].astype(float); x['book_bf'] = inv.sum(axis=1); p = inv.div(inv.sum(axis=1), axis=0); x['bf_h'], x['bf_d'], x['bf_a'] = p.iloc[:, 0], p.iloc[:, 1], p.iloc[:, 2]
x['book_ps'] = (1 / x[['PSCH', 'PSCD', 'PSCA']].astype(float)).sum(axis=1)
x['dw'] = ((x.hw == 0) & (x.aw == 0)).astype(float)
ll = lambda h, dd, a: -np.mean(np.log(np.where(x.hw == 1, h, np.where(x.aw == 1, a, dd))))
print(f' n={len(x)} | book %: Betfair {x.book_bf.mean()*100:.2f}, Pinnacle {x.book_ps.mean()*100:.2f}')
print(f' log loss: Betfair {ll(x.bf_h,x.bf_d,x.bf_a):.5f} | Pinnacle {ll(x.pc_h,x.pc_d,x.pc_a):.5f} | 50/50 blend {ll((x.bf_h+x.pc_h)/2,(x.bf_d+x.pc_d)/2,(x.bf_a+x.pc_a)/2):.5f}')
print(f' mean |Betfair - Pinnacle| home prob {np.abs(x.bf_h-x.pc_h).mean():.4f}; corr {np.corrcoef(x.bf_h,x.pc_h)[0,1]:.5f}')
# does the Pinnacle-minus-Betfair difference predict the result given Betfair? (who has the extra information)
X = np.column_stack([np.ones(len(x)), (x.pc_h - x.pc_a) - (x.bf_h - x.bf_a)])
b, se = ols(((x.hw - x.aw) - (x.bf_h - x.bf_a)).values, X); print(f' result residual vs Betfair on (Pinnacle - Betfair) gap: slope {b[1]:+.2f} (se {se[1]:.2f})  [1 = Pinnacle right, 0 = Betfair right]')
for lab, col, win in [('home', 'H', 'hw'), ('draw', 'D', 'dw'), ('away', 'A', 'aw')]:
    print(f'   back every {lab}: Pinnacle {roi(x, "PSC"+col, win)} | Betfair 2% comm {roi(x, "BFEC"+col, win, 0.02)} | best of the two {roi(x.assign(best=np.maximum(x["PSC"+col], 1+(x["BFEC"+col]-1)*0.98)), "best", win)}')
print('3. CROWD FEATURES against the exchange price (all crowd games with a Betfair close, incl. after Pinnacle data ends)')
y = m[m.BFECH.notna() & (m.crowd != 'ghost')].copy()
inv = 1 / y[['BFECH', 'BFECD', 'BFECA']].astype(float); p = inv.div(inv.sum(axis=1), axis=0); y['gapbf'] = p.iloc[:, 0] - p.iloc[:, 2]; y['S_bf'] = (y.hw - y.aw) - y.gapbf
print(f' n={len(y)}, {y.Date.min().date()} to {y.Date.max().date()}, mean S {y.S_bf.mean():+.4f} (se {y.S_bf.std()/np.sqrt(len(y)):.4f})')
for col, lab in [('runz', 'gate uplift v club mean so far'), ('latt', 'log attendance'), ('pred_up', 'predicted uplift (away fan base, distance, midweek)'), ('ldist', 'log travel distance'), ('midweek', 'midweek')]:
    z = y.dropna(subset=[col]); v = z[col].values.astype(float)
    if len(np.unique(v)) > 2: v = (v - v.mean()) / v.std()
    b, se = ols(z.S_bf.values, np.column_stack([np.ones(len(z)), v, z.gapbf.values])); print(f'   {lab:52s} n={len(z):4d} {b[1]:+.4f} (se {se[1]:.4f}, t {b[1]/se[1]:+.2f})')
