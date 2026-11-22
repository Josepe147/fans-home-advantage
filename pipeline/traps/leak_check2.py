"""Is the negative kappa a look-ahead artefact? Layer 1 used team strengths fitted on the WHOLE season's prices.
Prices after a match respond to its result, so a month's 'priced home advantage' can leak that month's results.
Test: refit each month's H using only prices up to the end of that month, then re-run the kappa test."""
import pandas as pd, numpy as np
from scipy.stats import norm
from scipy.optimize import minimize
d = pd.read_pickle('work/model.pkl'); d['ym'] = d.Date.dt.to_period('M'); Hfull = pd.read_pickle('work/H.pkl')
def ll(eta, c, y):
    ph = norm.cdf(eta - c); pa = norm.cdf(-eta - c); pdw = np.clip(1 - ph - pa, 1e-12, None)
    return np.where(y == 1, np.log(np.clip(ph, 1e-12, None)), np.where(y == -1, np.log(np.clip(pa, 1e-12, None)), np.log(pdw)))
pre = d[(d.regime == 'full') & (d.Date < '2020-03-01')]
a, b = minimize(lambda p: -ll(p[0] + p[1] * pre.mu.values, pre.c.values, pre.y.values).sum(), [0, 1], method='Nelder-Mead', options={'xatol': 1e-7, 'fatol': 1e-9}).x
rows = []
for (lg, sea), x in d.groupby(['league', 'season']):
    teams = sorted(set(x.HomeTeam) | set(x.AwayTeam)); ti = {t: i for i, t in enumerate(teams)}; months = sorted(x.ym.unique())
    for m in months:
        z = x[x.ym <= m]
        if len(z) < 100: continue
        cells = sorted(set(zip(z.regime, z.ym))); ci = {k: i for i, k in enumerate(cells)}; X = np.zeros((len(z), len(cells) + len(teams)))
        for r, (h, aw, rg, ym) in enumerate(zip(z.HomeTeam, z.AwayTeam, z.regime, z.ym)): X[r, ci[(rg, ym)]] = 1; X[r, len(cells) + ti[h]] = 1; X[r, len(cells) + ti[aw]] = -1
        beta = np.linalg.lstsq(X, z.mu.values, rcond=None)[0]
        for k, i in ci.items():
            if k[1] == m: rows.append([lg, sea, k[0], m, beta[i], int(X[:, i].sum())])
Hp = pd.DataFrame(rows, columns=['league', 'season', 'regime', 'ym', 'H_past', 'n_past'])
Hp = Hp.merge(Hfull[['league', 'season', 'regime', 'ym', 'H', 'H_pre', 'n']], on=['league', 'season', 'regime', 'ym']); Hp.to_pickle('work/H_past.pkl')
print('cells', len(Hp), '| corr(full-season H, past-only H) =', round(np.corrcoef(Hp.H, Hp.H_past)[0, 1], 3))
def kappa(x, col, lab):
    x = x.merge(Hp[['league', 'season', 'regime', 'ym', 'H', 'H_past', 'H_pre', 'n']], on=['league', 'season', 'regime', 'ym']); x = x[x.n >= 15]
    base = (a + b * x.H_pre).values; r = ((a + b * x[col]) / (a + b * x.H_pre)).values; eta0 = (a + b * x.mu).values; c = x.c.values; y = x.y.values
    key = (x.league + x.season.astype(str)).values; rg = pd.Series(r).groupby(key).transform('mean').values; rbar = r.mean()
    # note: the price itself is eta0. We ask whether the month-level deviation v = r - rg should be weighted 1 (as the price does) or something else.
    f = lambda p: -ll(eta0 + p[0] + (p[1] - 1) * base * (r - rg), c, y).sum(); f1 = lambda p: -ll(eta0 + p[0], c, y).sum()
    o = minimize(f, [0.0, 1.0], method='BFGS'); o1 = minimize(f1, [0.0], method='BFGS'); lr = 2 * (o1.fun - o.fun)
    # curvature-based se for kappa
    h = 1e-3; g2 = (f([o.x[0], o.x[1] + h]) - 2 * o.fun + f([o.x[0], o.x[1] - h])) / h ** 2
    print(f'   {lab:44s} n={len(x):6d} kappa_within {o.x[1]:+.2f} (se {1/np.sqrt(g2):.2f}) | LR v kappa=1: {lr:6.2f}')
ord_ = d[(d.regime == 'full') & ((d.Date < '2020-03-01') | (d.season >= 2021))]; cd = d[(d.regime == 'none') & (d.wave == 'first')]
print('Same matches (months with at least 100 earlier prices in the season):')
for lab, x in [('ordinary seasons', ord_), ('closed doors, first wave', cd)]:
    kappa(x, 'H', lab + ', strengths from WHOLE season'); kappa(x, 'H_past', lab + ', strengths from PAST prices only')
