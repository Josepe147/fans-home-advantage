"""Can the market-implied prior weight be recovered? Simulate a market that IS a Bayesian learner with a known prior,
on the real fixture list, add monthly reading noise of the size observed, then fit exactly as market_path.py does."""
import pandas as pd, numpy as np
from scipy.stats import norm
from scipy.optimize import minimize
d = pd.read_pickle('work/kf.pkl'); d = d[d.regime != 'drop'].copy()
def ll(eta, c, y):
    ph = norm.cdf(eta - c); pa = norm.cdf(-eta - c); pdw = np.clip(1 - ph - pa, 1e-12, None)
    return np.where(y == 1, np.log(np.clip(ph, 1e-12, None)), np.where(y == -1, np.log(np.clip(pa, 1e-12, None)), np.log(pdw)))
pre = d[(d.regime == 'full') & (d.Date < '2020-03-01')]
a, b = minimize(lambda p: -ll(p[0] + p[1] * pre.mu.values, pre.c.values, pre.y.values).sum(), [0, 1], method='Nelder-Mead', options={'xatol': 1e-7, 'fatol': 1e-9}).x
Hpre = d[(d.regime == 'full') & (d.season >= 2015) & (d.Date < '2020-03-01')].groupby('league').H_post.mean().rename('H_pre')
g = d[(d.regime == 'none') & (d.Date >= '2020-05-01') & (d.Date <= '2021-06-30')].join(Hpre, on='league').sort_values('Date').reset_index(drop=True)
g['ym'] = g.Date.dt.to_period('M'); g['base'] = a + b * g.H_pre; g['r'] = (a + b * g.H_post) / g.base
strip = (a + b * g.mu - g.base * g.r).values; base = g.base.values; c = g.c.values      # price with home advantage removed
R = np.arange(0.0, 1.6001, 0.01)
M = g.groupby('ym').size(); months = [m for m in M.index if M[m] >= 60]; mid = np.array([np.datetime64(m.start_time + pd.Timedelta(days=14)) for m in months]); wts = M[months].values
before = np.array([(g.Date.values < t) for t in mid])                                  # month x match
f1 = norm.pdf(strip + base * 0.55 - c); f2 = norm.pdf(strip + base * 0.55 + c); p1 = norm.cdf(strip + base * 0.55 - c); p2 = norm.cdf(-strip - base * 0.55 - c)
info = ((f1 ** 2 / p1 + f2 ** 2 / p2 + (f2 - f1) ** 2 / (1 - p1 - p2)) * base ** 2).mean()
def paths(Lsum, rho0, s0):
    lp = Lsum + norm.logpdf(R, rho0, s0)[None, :]; p = np.exp(lp - lp.max(axis=1, keepdims=True)); p /= p.sum(axis=1, keepdims=True); return p @ R
def fit(Lsum, path):
    sse = lambda q: np.average((paths(Lsum, q[0], np.exp(q[1])) - path) ** 2, weights=wts)
    best = min((minimize(sse, [x0, np.log(s)], method='Nelder-Mead', options={'xatol': 1e-4, 'fatol': 1e-10}) for x0 in [0.6, 0.75] for s in [0.03, 0.1]), key=lambda f: f.fun)
    return best.x[0], float(np.exp(best.x[1]))
rng = np.random.default_rng(11); NOISE = 0.03
print(f'one closed-door match carries information {info:.4f} about rho, so prior weight in matches = 1 / (s0^2 x {info:.4f})')
for true_w in [1000, 5000, 20000]:
    s0 = 1 / np.sqrt(true_w * info); out = []
    for _ in range(60):
        e = strip + base * 0.52; u = rng.random(len(e)); ph = norm.cdf(e - c); pa = norm.cdf(-e - c); y = np.where(u < ph, 1, np.where(u < ph + pa, -1, 0))
        L = ll(strip[:, None] + base[:, None] * R[None, :], c[:, None], y[:, None]); Lsum = before.astype(float) @ L
        path = paths(Lsum, 0.67, s0) + rng.normal(0, NOISE, len(months)); r0, s = fit(Lsum, path); out.append(1 / (s ** 2 * info))
    o = np.array(out); print(f'  true weight {true_w:6d} matches: recovered median {np.median(o):8,.0f} | middle 80% {np.percentile(o,10):8,.0f} to {np.percentile(o,90):9,.0f} | share within a factor of 2 of the truth {np.mean((o>true_w/2)&(o<true_w*2)):.2f}')
