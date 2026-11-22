"""The dose curve: home advantage against crowd size, first-wave window, 18 + extra leagues. See PLAN_dose.md."""
import pandas as pd, numpy as np, sys
from scipy.stats import norm
from scipy.optimize import minimize
def ll(eta, c, y):
    ph = norm.cdf(eta - c); pa = norm.cdf(-eta - c); pdw = np.clip(1 - ph - pa, 1e-12, None)
    return np.where(y == 1, np.log(np.clip(ph, 1e-12, None)), np.where(y == -1, np.log(np.clip(pa, 1e-12, None)), np.log(pdw)))
A = pd.read_pickle('work/kf.pkl'); X = pd.read_pickle('work/kf_extra.pkl')
pre = A[(A.regime == 'full') & (A.Date < '2020-03-01')]
a, b = minimize(lambda p: -ll(p[0] + p[1] * pre.mu.values, pre.c.values, pre.y.values).sum(), [0, 1], method='Nelder-Mead', options={'xatol': 1e-7, 'fatol': 1e-9}).x
# attendance for the 18 leagues
eu = pd.read_pickle('work/eu.pkl')[['league', 'Date', 'HomeTeam', 'att']]; ms = pd.read_pickle('work/master.pkl')[['league', 'Date', 'HomeTeam', 'att']]
att = pd.concat([eu, ms]).dropna(subset=['att']).drop_duplicates(['league', 'Date', 'HomeTeam'])
A = A.merge(att, on=['league', 'Date', 'HomeTeam'], how='left')
D = pd.concat([A, X], ignore_index=True)
win = (D.Date >= '2020-05-01') & (D.Date <= '2021-06-30')
Hpre = D[(D.regime == 'full') & (D.season >= 2015) & (D.Date < '2020-03-01')].groupby('league').H_post.mean().rename('H_pre')
g = D[win & D.regime.isin(['none', 'partial'])].join(Hpre, on='league').dropna(subset=['H_pre']).copy()
g.loc[g.regime == 'partial', 'att'] = g.loc[g.regime == 'partial', 'att']
g['gate'] = np.where(g.regime == 'none', 0.0, g.att.fillna(-1)); g.loc[(g.regime == 'partial') & (g.gate <= 100) & (g.gate >= 0), 'gate'] = 0.0
g = g[g.gate >= 0].reset_index(drop=True)
g['base'] = a + b * g.H_pre; g['strip'] = b * (g.mu - g.H_post)
if len(sys.argv) > 1 and sys.argv[1] == 'noJPN': g = g[g.league != 'JPN'].reset_index(drop=True)
if len(sys.argv) > 1 and sys.argv[1] == 'england': g = g[g.league.isin(['E0', 'E1', 'E2', 'E3'])].reset_index(drop=True)
if len(sys.argv) > 1 and sys.argv[1] == 'samemonths':
    g['ym'] = g.Date.dt.to_period('M'); keep = set(g[g.gate > 0][['league', 'ym']].itertuples(index=False, name=None)); g = g[[k in keep for k in zip(g.league, g.ym)]].reset_index(drop=True)
print(f'{len(g)} matches, {g.league.nunique()} leagues | closed {int((g.gate==0).sum())} | with crowd {int((g.gate>0).sum())} (median gate {g[g.gate>0].gate.median():.0f})')
print('market priced fraction, closed v crowd:', round(((a + b * g.H_post) / g.base)[g.gate == 0].mean(), 3), round(((a + b * g.H_post) / g.base)[g.gate > 0].mean(), 3))
# 1. bands, each estimated freely on a grid
R = np.arange(-0.6, 2.4001, 0.01)
bands = [(0, 0, 'closed doors'), (100, 1000, '101 to 1,000'), (1000, 2000, '1,001 to 2,000'), (2000, 5000, '2,001 to 5,000'), (5000, 1e7, 'over 5,000')]
print('\n1. HOME ADVANTAGE BY GATE (normal with full crowds = 1), flat prior')
rows = []
for lo, hi, lab in bands:
    s = (g.gate == 0) if hi == 0 else ((g.gate > lo) & (g.gate <= hi)); x = g[s]
    L = ll(x.strip.values[:, None] + x.base.values[:, None] * R[None, :], x.c.values[:, None], x.y.values[:, None]).sum(axis=0); p = np.exp(L - L.max()); p /= p.sum(); m = (p * R).sum(); sd = np.sqrt((p * (R - m) ** 2).sum()); cum = np.cumsum(p)
    pr = ((a + b * x.H_post) / x.base).mean(); rows.append([lab, len(x), x.league.nunique(), m, sd, R[np.searchsorted(cum, .025)], R[np.searchsorted(cum, .975)], pr])
    print(f'   {lab:16s} n={len(x):5d} leagues={x.league.nunique():2d} | true {m:.2f} (sd {sd:.2f}, 95% {R[np.searchsorted(cum,.025)]:.2f} to {R[np.searchsorted(cum,.975)]:.2f}) | market priced {pr:.2f}')
pd.DataFrame(rows, columns=['band', 'n', 'leagues', 'mean', 'sd', 'lo', 'hi', 'priced']).to_csv('work/dose_bands.csv', index=False)
# 2. shapes, maximum likelihood and leave-one-league-out
def f(th, gate, shape):
    if shape == 'S0': return np.full_like(gate, th[0])
    if shape == 'S1': return np.where(gate > 0, th[1], th[0])
    if shape == 'S2': return th[0] + (1 - th[0]) * (1 - np.exp(-gate / np.exp(th[1])))
    if shape == 'S3': return th[0] + th[1] * np.log1p(gate / 1000)
init = {'S0': [0.55], 'S1': [0.5, 0.9], 'S2': [0.5, np.log(1500)], 'S3': [0.5, 0.2]}
def fit(x, shape):
    nll = lambda th: -ll(x.strip.values + x.base.values * f(th, x.gate.values, shape), x.c.values, x.y.values).sum()
    best = min((minimize(nll, np.array(init[shape]) + j * 0.1, method='Nelder-Mead', options={'xatol': 1e-5, 'fatol': 1e-6}) for j in range(3)), key=lambda o: o.fun); return best.x, best.fun
print('\n2. SHAPES, all data: maximum likelihood')
for sh in ['S0', 'S1', 'S2', 'S3']:
    th, nl = fit(g, sh); extra = f' | k = {np.exp(th[1]):,.0f} fans restore 63% of the gap' if sh == 'S2' else ''
    print(f'   {sh}: parameters {np.round(th,3)} | log-likelihood {-nl:.2f}{extra}')
print('\n3. LEAVE-ONE-LEAGUE-OUT log score (fit on the rest, score the held-out league)')
leagues = sorted(g.league.unique()); sc = {sh: {} for sh in init}
for lg in leagues:
    tr, te = g[g.league != lg], g[g.league == lg]
    for sh in init:
        th, _ = fit(tr, sh); sc[sh][lg] = ll(te.strip.values + te.base.values * f(th, te.gate.values, sh), te.c.values, te.y.values).sum()
S = pd.DataFrame(sc); rng = np.random.default_rng(3)
for sh in ['S1', 'S2', 'S3']:
    dlt = (S[sh] - S['S0']).values; bs = [rng.choice(dlt, len(dlt)).sum() for _ in range(5000)]
    print(f'   {sh} minus S0: {dlt.sum():+.2f} (bootstrap over leagues 95% {np.percentile(bs,2.5):+.2f} to {np.percentile(bs,97.5):+.2f}) | leagues where {sh} better: {(dlt>0).sum()} of {len(dlt)}')
dlt = (S['S2'] - S['S1']).values; bs = [rng.choice(dlt, len(dlt)).sum() for _ in range(5000)]; print(f'   S2 minus S1: {dlt.sum():+.2f} (95% {np.percentile(bs,2.5):+.2f} to {np.percentile(bs,97.5):+.2f})')
