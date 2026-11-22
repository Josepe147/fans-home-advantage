"""Stress tests for model.py: calibration stability, raw v calibrated market, phases, and placebo seasons.
The placebo is the important one: how far off is the market on home advantage in an ordinary season with crowds?"""
import pandas as pd, numpy as np
from scipy.stats import norm, chi2
from scipy.optimize import minimize
d = pd.read_pickle('work/model.pkl')
def ll(eta, c, y):
    ph = norm.cdf(eta - c); pa = norm.cdf(-eta - c); pdw = np.clip(1 - ph - pa, 1e-12, None)
    return np.where(y == 1, np.log(ph), np.where(y == -1, np.log(pa), np.log(pdw)))
cal = lambda x: minimize(lambda p: -ll(p[0] + p[1] * x.mu.values, x.c.values, x.y.values).sum(), [0, 1], method='Nelder-Mead', options={'xatol': 1e-7, 'fatol': 1e-9}).x
G = np.arange(-0.3, 0.3001, 0.002)
def mle(x, eta):
    s = ll(eta[:, None] + G[None, :], x.c.values[:, None], x.y.values[:, None]).sum(axis=0); i = s.argmax(); cur = -(s[i + 1] - 2 * s[i] + s[i - 1]) / 0.002 ** 2; return G[i], 1 / np.sqrt(cur)
pre = d[(d.regime == 'full') & (d.Date < '2020-03-01')]; a, b = cal(pre); print(f'calibration: a={a:.5f} b={b:.5f} (n={len(pre)})')
g = d[(d.regime == 'none') & (d.wave == 'first')]
dg, sg = mle(g, a + b * g.mu.values)
print('first-wave closed-door games, pooled delta: calibrated market %+.4f (se %.4f) | raw market %+.4f (se %.4f)' % (dg, sg, *mle(g, g.mu.values)))
print('pre-Covid crowd games against the raw market: %+.4f (se %.4f)' % mle(pre, pre.mu.values))
a2, b2 = cal(pre[pre.season >= 2015]); print('calibration on 2015/16-2019/20 only: a=%.4f b=%.4f -> delta %+.4f (se %.4f)' % (a2, b2, *mle(g, a2 + b2 * g.mu.values)))
for lab, lo, hi in [('restart May-Aug 2020', '2020-05-01', '2020-08-31'), ('Sep-Nov 2020', '2020-09-01', '2020-11-30'), ('Dec 2020-Feb 2021', '2020-12-01', '2021-02-28'), ('Mar-Jun 2021', '2021-03-01', '2021-06-30')]:
    x = g[(g.Date >= lo) & (g.Date <= hi)]; print('  %-22s n=%5d delta %+.4f (se %.4f)' % ((lab, len(x)) + mle(x, a + b * x.mu.values)))
print('PLACEBO: pooled delta in each ordinary season with crowds (calibration fitted on the other seasons)')
full = d[(d.regime == 'full') & ((d.Date < '2020-03-01') | (d.season >= 2021)) & (d.season <= 2024)]; res = []
for s in sorted(full.season.unique()):
    ao, bo = cal(full[full.season != s]); x = full[full.season == s]; dl, se = mle(x, ao + bo * x.mu.values); res.append((s, dl, se)); print('  season %d/%02d: delta %+.4f (se %.4f) n=%d' % (s, (s + 1) % 100, dl, se, len(x)))
r = pd.DataFrame(res, columns=['season', 'delta', 'se']); q = ((r.delta / r.se) ** 2).sum()
excess = max(0.0, r.delta.var(ddof=0) - (r.se ** 2).mean())
print(f'spread of season deltas: sd {r.delta.std(ddof=0):.4f} | expected from sampling alone {np.sqrt((r.se**2).mean()):.4f} | chi-square {q:.1f} on {len(r)} df, p = {1-chi2.cdf(q,len(r)):.3f} | season-level noise sd {np.sqrt(excess):.4f}')
tot = np.sqrt(sg ** 2 + excess); print(f'ghost-period delta {dg:+.4f}: {abs(dg)/sg:.2f} sampling SEs from zero, {abs(dg)/tot:.2f} once ordinary season noise is added -> P(home sides over-rated) about {norm.cdf(abs(dg)/tot):.2f}')
print(f'ordinary seasons with a miss at least as large as the ghost period: {(r.delta.abs() >= abs(dg)).sum()} of {len(r)}')
open('work/season_noise_sd.txt', 'w').write(str(np.sqrt(excess)))
