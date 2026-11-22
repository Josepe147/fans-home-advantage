"""Checks on the learning model.
A. Is the kappa result (market's within-league revisions of home advantage carry no information) special to the closed-door
   period, or does it show up in ordinary seasons too?  B. How well pinned down is the market-implied prior weight?"""
import pandas as pd, numpy as np
from scipy.stats import norm
from scipy.optimize import minimize
d = pd.read_pickle('work/model.pkl'); H = pd.read_pickle('work/H.pkl'); d['ym'] = d.Date.dt.to_period('M')
def ll(eta, c, y):
    ph = norm.cdf(eta - c); pa = norm.cdf(-eta - c); pdw = np.clip(1 - ph - pa, 1e-12, None)
    return np.where(y == 1, np.log(np.clip(ph, 1e-12, None)), np.where(y == -1, np.log(np.clip(pa, 1e-12, None)), np.log(pdw)))
pre = d[(d.regime == 'full') & (d.Date < '2020-03-01')]
a, b = minimize(lambda p: -ll(p[0] + p[1] * pre.mu.values, pre.c.values, pre.y.values).sum(), [0, 1], method='Nelder-Mead', options={'xatol': 1e-7, 'fatol': 1e-9}).x
def kappa(x, lab, group=('league',)):
    x = x.merge(H[['league', 'season', 'regime', 'ym', 'H', 'H_pre', 'n']], on=['league', 'season', 'regime', 'ym'], how='left').dropna(subset=['H', 'H_pre'])
    x = x[x.n >= 15].copy()                                   # cells with too few matches give a noisy H
    base = (a + b * x.H_pre).values; r = ((a + b * x.H) / (a + b * x.H_pre)).values; eta0 = (a + b * x.mu).values; c = x.c.values; y = x.y.values
    key = x[list(group)].astype(str).agg('|'.join, axis=1); rg = pd.Series(r).groupby(key.values).transform('mean').values; rbar = r.mean()
    f = lambda p: -ll(eta0 + base * (p[0] - r) + p[1] * base * (rg - rbar) + p[2] * base * (r - rg), c, y).sum()
    o = minimize(f, [r.mean(), 1.0, 1.0], method='BFGS'); se = np.sqrt(np.diag(o.hess_inv))
    # likelihood-ratio test of kappa_within = 1
    f1 = lambda p: -ll(eta0 + base * (p[0] - r) + p[1] * base * (rg - rbar) + 1.0 * base * (r - rg), c, y).sum(); o1 = minimize(f1, [r.mean(), 1.0], method='BFGS')
    print(f'  {lab:46s} n={len(x):6d} | between {o.x[1]:+.2f} (se {se[1]:.2f}) | within, over time {o.x[2]:+.2f} (se {se[2]:.2f}) | LR test of within = 1: {2*(o1.fun-o.fun):.2f} | sd of within variation {np.std(r-rg):.3f}')
    return o.x[2], se[2]
print('A. KAPPA: 1 = the market\'s variation in priced home advantage is fully informative, 0 = it is noise')
print(' group = league (as in learn.py: between leagues, and within league across months)')
kappa(d[(d.regime == 'none') & (d.wave == 'first')], 'closed doors, first wave')
print(' group = league-season (between league-seasons, and month to month within a season)')
kappa(d[(d.regime == 'none') & (d.wave == 'first')], 'closed doors, first wave', ('league', 'season'))
res = []
for lab, x in [('crowd games 2012/13 to Feb 2020', d[(d.regime == 'full') & (d.Date < '2020-03-01')]), ('crowd games 2021/22 on', d[(d.regime == 'full') & (d.season >= 2021)])]:
    kappa(x, lab, ('league', 'season'))
print(' each ordinary season on its own:')
for s in list(range(2012, 2020)) + [2021, 2022, 2023, 2024]:
    x = d[(d.regime == 'full') & (d.season == s) & ((d.Date < '2020-03-01') | (d.season >= 2021))]; res.append(kappa(x, f'season {s}/{(s+1)%100:02d}', ('league', 'season')))
r = np.array(res); w = 1 / r[:, 1] ** 2; print(f'  ordinary seasons: weighted mean of within-kappa {np.average(r[:,0], weights=w):+.2f} (se {1/np.sqrt(w.sum()):.2f}), spread across seasons sd {r[:,0].std():.2f}, lowest {r[:,0].min():+.2f}')
