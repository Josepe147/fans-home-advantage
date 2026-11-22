"""Leak-free kappa test. Regressor: the market's real-time priced home advantage H_prior from the Kalman filter,
built from prices on strictly earlier dates. Under an efficient price its within-league-season variation should carry
weight 1 (kappa = 1). One-step score regression with league-season fixed effects, weights = Fisher information."""
import pandas as pd, numpy as np
from scipy.stats import norm
from scipy.optimize import minimize
d = pd.read_pickle('work/kf.pkl'); d = d[d.regime != 'drop'].copy(); d['ym'] = d.Date.dt.to_period('M')
def ll(eta, c, y):
    ph = norm.cdf(eta - c); pa = norm.cdf(-eta - c); pdw = np.clip(1 - ph - pa, 1e-12, None)
    return np.where(y == 1, np.log(np.clip(ph, 1e-12, None)), np.where(y == -1, np.log(np.clip(pa, 1e-12, None)), np.log(pdw)))
pre = d[(d.regime == 'full') & (d.Date < '2020-03-01')]
a, b = minimize(lambda p: -ll(p[0] + p[1] * pre.mu.values, pre.c.values, pre.y.values).sum(), [0, 1], method='Nelder-Mead', options={'xatol': 1e-7, 'fatol': 1e-9}).x
e = a + b * d.mu; ph = norm.cdf(e - d.c); pa = norm.cdf(-e - d.c); pdw = 1 - ph - pa; f1 = norm.pdf(e - d.c); f2 = norm.pdf(e + d.c)
d['score'] = np.where(d.y == 1, f1 / ph, np.where(d.y == -1, -f2 / pa, (f2 - f1) / pdw)); d['info'] = f1 ** 2 / ph + f2 ** 2 / pa + (f2 - f1) ** 2 / pdw; d['z'] = d.score / d['info']
d['grp'] = d.league + d.season.astype(str) + d.regime; d['clu'] = d.league + d.ym.astype(str)
def test(x, col, lab, fe=True):
    x = x.dropna(subset=[col]).copy(); w = x['info'].values
    if fe:
        for c_ in ['z', col]: x[c_ + '_d'] = x[c_] - (x[c_] * x['info']).groupby(x.grp).transform('sum') / x['info'].groupby(x.grp).transform('sum')
    else:
        for c_ in ['z', col]: x[c_ + '_d'] = x[c_] - np.average(x[c_], weights=w)
    v = b * x[col + '_d'].values; z = x.z_d.values; th = (w * v * z).sum() / (w * v * v).sum(); r = z - th * v
    g = pd.DataFrame({'c': x.clu.values, 's': w * v * r}).groupby('c').s.sum(); se = np.sqrt((g ** 2).sum()) / (w * v * v).sum()
    print(f'   {lab:60s} n={len(x):6d} kappa {1+th:+.2f} (se {se:.2f}) | distance from 1: {th/se:+.2f} se | sd of regressor {x[col+"_d"].std():.4f}')
    return 1 + th, se
ordn = d[(d.regime == 'full') & ((d.Date < '2020-03-01') | (d.season >= 2021)) & (d.season >= 2013)]; cd = d[(d.regime == 'none') & (d.Date <= '2021-06-30')]
print('A. Real-time priced home advantage from strictly earlier prices (H_prior), within league-season:')
test(ordn, 'H_prior', 'ordinary seasons 2013/14 on'); test(ordn[ordn.Date < '2020-03-01'], 'H_prior', '  to Feb 2020'); test(ordn[ordn.season >= 2021], 'H_prior', '  2021/22 on'); test(cd, 'H_prior', 'closed doors, first wave')
print('B. Same, but including prices up to and on the match date (H_post):')
test(ordn, 'H_post', 'ordinary seasons 2013/14 on'); test(cd, 'H_post', 'closed doors, first wave')
print('C. The whole-season fixed-effect version from Layer 1 (known to leak results), same score method, for comparison:')
H = pd.read_pickle('work/H.pkl'); x = ordn.merge(H[['league', 'season', 'regime', 'ym', 'H']], on=['league', 'season', 'regime', 'ym'], how='left'); test(x, 'H', 'ordinary seasons 2013/14 on, whole-season strengths')
x = cd.merge(H[['league', 'season', 'regime', 'ym', 'H']], on=['league', 'season', 'regime', 'ym'], how='left'); test(x, 'H', 'closed doors, whole-season strengths')
print('D. Does the market\'s NEWS about a match carry its weight? innovation = price minus what earlier prices predicted')
test(ordn, 'innov', 'ordinary seasons, match-level innovation', fe=True); test(cd, 'innov', 'closed doors, match-level innovation', fe=True)
print('E. Between leagues and seasons: does the level of priced home advantage carry its weight? (no fixed effects)')
test(ordn, 'H_prior', 'ordinary seasons, all variation in H_prior', fe=False); test(cd, 'H_prior', 'closed doors, all variation in H_prior', fe=False)
print('F. NO FIXED EFFECTS (fixed effects demean with future values of a regressor that reacts to past results, which biases the estimate).')
print('   Causal split: priced home advantage at the season start, and the real-time change since then. Both known before kick-off.')
d = d.sort_values('Date'); d['H_start'] = d.groupby(['league', 'season']).H_prior.transform('first'); d['dH'] = d.H_prior - d.H_start
d['nseq'] = d.groupby(['league', 'season']).cumcount()
def test2(x, lab):
    x = x.dropna(subset=['dH']); w = x['info'].values; X = np.column_stack([np.ones(len(x)), b * x.H_start.values, b * x.dH.values]); z = x.z.values
    XtW = X.T * w; beta = np.linalg.solve(XtW @ X, XtW @ z); r = z - X @ beta; G = pd.DataFrame(X * (w * r)[:, None]).groupby(x.clu.values).sum().values; V = np.linalg.inv(XtW @ X) @ (G.T @ G) @ np.linalg.inv(XtW @ X); se = np.sqrt(np.diag(V))
    print(f'   {lab:44s} n={len(x):6d} kappa on season-start level {1+beta[1]:+.2f} (se {se[1]:.2f}) | kappa on change since season start {1+beta[2]:+.2f} (se {se[2]:.2f}, {beta[2]/se[2]:+.2f} se from 1) | sd of change {x.dH.std():.4f}')
ordn = d[(d.regime == 'full') & ((d.Date < '2020-03-01') | (d.season >= 2021)) & (d.season >= 2013)]; cd = d[(d.regime == 'none') & (d.Date <= '2021-06-30')]
test2(ordn, 'ordinary seasons 2013/14 on'); test2(ordn[ordn.Date < '2020-03-01'], '  to Feb 2020'); test2(ordn[ordn.season >= 2021], '  2021/22 on'); test2(cd, 'closed doors, first wave')
print('G. Simulation of the fixed-effects bias: results drawn from the price itself (kappa = 1 by construction), prices untouched.')
print('   This cannot reproduce feedback from results to later prices, so it only shows the method is unbiased when there is no feedback.')
rng = np.random.default_rng(3); x = ordn.dropna(subset=['H_prior']).copy(); e = a + b * x.mu.values; ph = norm.cdf(e - x.c.values); pa = norm.cdf(-e - x.c.values); f1 = norm.pdf(e - x.c.values); f2 = norm.pdf(e + x.c.values); out = []
for _ in range(200):
    u = rng.random(len(x)); y = np.where(u < ph, 1, np.where(u < ph + pa, -1, 0)); sc = np.where(y == 1, f1 / ph, np.where(y == -1, -f2 / pa, (f2 - f1) / (1 - ph - pa))); x['z'] = sc / x['info'].values
    w = x['info'].values; zc = x.z - (x.z * x['info']).groupby(x.grp).transform('sum') / x['info'].groupby(x.grp).transform('sum'); vc = b * (x.H_prior - (x.H_prior * x['info']).groupby(x.grp).transform('sum') / x['info'].groupby(x.grp).transform('sum')); out.append(1 + (w * vc * zc).sum() / (w * vc * vc).sum())
print(f'   fixed-effects kappa under no feedback: mean {np.mean(out):+.2f}, sd {np.std(out):.2f}')
