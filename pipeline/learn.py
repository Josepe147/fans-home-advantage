"""The learning model. Truth: home advantage behind closed doors is a fraction rho of each league's normal level.
Market: its priced fraction r is read from prices in real time by the Kalman filter in kf.py. Results inform rho through the ordered-probit likelihood.
Everything is exact on a grid of rho. Usage: python learn.py [noEngland]"""
import sys, pandas as pd, numpy as np
from scipy.stats import norm
from scipy.optimize import minimize
NOENG = len(sys.argv) > 1 and sys.argv[1] == 'noEngland'
d = pd.read_pickle('work/kf.pkl'); d = d[d.regime != 'drop'].copy(); d['wave'] = np.where((d.regime == 'none') & (d.Date >= '2021-07-01'), 'later', np.where(d.regime == 'none', 'first', ''))
def ll(eta, c, y):
    ph = norm.cdf(eta - c); pa = norm.cdf(-eta - c); pdw = np.clip(1 - ph - pa, 1e-12, None)
    return np.where(y == 1, np.log(np.clip(ph, 1e-12, None)), np.where(y == -1, np.log(np.clip(pa, 1e-12, None)), np.log(pdw)))
pre = d[(d.regime == 'full') & (d.Date < '2020-03-01')]
a, b = minimize(lambda p: -ll(p[0] + p[1] * pre.mu.values, pre.c.values, pre.y.values).sum(), [0, 1], method='Nelder-Mead', options={'xatol': 1e-7, 'fatol': 1e-9}).x
# market's priced home advantage in real time, from the Kalman filter on prices (kf.py). H_post uses prices up to the match date, never results.
Hpre = d[(d.regime == 'full') & (d.season >= 2015) & (d.Date < '2020-03-01')].groupby('league').H_post.mean().rename('H_pre')
g = d[(d.regime == 'none') & (d.wave == 'first')].copy(); g['ym'] = g.Date.dt.to_period('M'); g['H'] = g.H_post
if NOENG: g = g[~g.league.isin(['E0', 'E1'])]
g = g.join(Hpre, on='league').sort_values('Date').reset_index(drop=True)
g['base'] = a + b * g.H_pre; g['r'] = (a + b * g.H) / g.base; g['eta0'] = a + b * g.mu
print(f'{"WITHOUT ENGLAND " if NOENG else ""}closed-door first wave: n={len(g)}, leagues={g.league.nunique()} | mean priced fraction r = {g.r.mean():.3f}')
R = np.arange(0.0, 1.6001, 0.01)                                   # grid for rho
E = g.eta0.values[:, None] + g.base.values[:, None] * (R[None, :] - g.r.values[:, None]); L = ll(E, g.c.values[:, None], g.y.values[:, None])   # match x rho
l_mkt = ll(g.eta0.values, g.c.values, g.y.values)                   # the market's own log score per match
PH = norm.cdf(E - g.c.values[:, None]); PA = norm.cdf(-E - g.c.values[:, None]); PY = np.where((g.y.values == 1)[:, None], PH, np.where((g.y.values == -1)[:, None], PA, 1 - PH - PA))
cuts = pd.date_range('2020-05-11', '2021-07-05', freq='7D'); wk = np.searchsorted(cuts.values, g.Date.values, side='right') - 1; nW = len(cuts)
Lw = np.zeros((nW, len(R))); np.add.at(Lw, wk, L); cumL = np.vstack([np.zeros(len(R)), np.cumsum(Lw, axis=0)])   # cumL[k] = all matches before week k
# information-weighted market fraction per week
ph0 = norm.cdf(g.eta0 - g.c); pa0 = norm.cdf(-g.eta0 - g.c); phi1 = norm.pdf(g.eta0 - g.c); phi2 = norm.pdf(g.eta0 + g.c)
info = (phi1 ** 2 / ph0 + phi2 ** 2 / pa0 + (phi2 - phi1) ** 2 / (1 - ph0 - pa0)) * g.base ** 2
rw = np.array([np.average(g.r[wk == k], weights=info[wk == k]) if (wk == k).any() else np.nan for k in range(nW)]); nw = np.bincount(wk, minlength=nW)
def post_const(k, rho0, s0):
    lp = cumL[k] + norm.logpdf(R, rho0, s0); p = np.exp(lp - lp.max()); return p / p.sum()
def stats(p): m = (p * R).sum(); return m, np.sqrt((p * (R - m) ** 2).sum())
# ---- 1. the whole period, constant truth, flat prior
pF = post_const(nW, 1.0, 5.0); mF, sF = stats(pF); cum = np.cumsum(pF)
print(f'\n1. TRUE FRACTION OF HOME ADVANTAGE LEFT, constant over the period, flat prior: rho = {mF:.3f} (sd {sF:.3f}, 95% {R[np.searchsorted(cum,0.025)]:.2f} to {R[np.searchsorted(cum,0.975)]:.2f}) | market priced {np.average(g.r, weights=info):.3f} on average')
# ---- 2. the market's path and the learner's path
print('\n2. PATHS BY MONTH: market priced fraction, and what a learner knew at the START of each month (flat prior, and a prior at the market\'s first price)')
r_first = np.nanmean(rw[:3])
for mth in pd.period_range('2020-06', '2021-06', freq='M'):
    k = int(np.searchsorted(cuts.values, np.datetime64(mth.start_time))); sel = (g.ym == mth).values
    if not sel.any(): continue
    m1, s1 = stats(post_const(k, 1.0, 5.0)); m2, s2 = stats(post_const(k, r_first, 0.15))
    print(f'   {mth}: matches so far {int(nw[:k].sum()):5d} | market {np.average(g.r[sel], weights=info[sel]):.2f} | flat-prior learner {m1:.2f} (sd {s1:.2f}) | learner starting at the market\'s first price {m2:.2f} (sd {s2:.2f})')
# ---- 3. what prior makes the market's path look like Bayesian learning?
valid = ~np.isnan(rw) & (np.arange(nW) >= 1)
def path(rho0, s0): return np.array([stats(post_const(k, rho0, s0))[0] for k in range(nW)])
def sse(p): return np.average((path(p[0], np.exp(p[1]))[valid] - rw[valid]) ** 2, weights=nw[valid])
best = min((minimize(sse, [x0, np.log(s)], method='Nelder-Mead', options={'xatol': 1e-4, 'fatol': 1e-9}) for x0 in [0.6, 0.8] for s in [0.02, 0.1]), key=lambda f: f.fun)
rho0_m, s0_m = best.x[0], float(np.exp(best.x[1])); info_match = info.mean()
print(f'\n3. MARKET-IMPLIED PRIOR: the market\'s weekly path is best matched by a learner with prior mean {rho0_m:.3f} and prior sd {s0_m:.4f} (rms gap {np.sqrt(best.fun):.3f})')
print(f'   prior sd {s0_m:.4f} carries the weight of about {1/(s0_m**2*info_match):,.0f} matches of evidence (one match carries information {info_match:.4f} about rho)')
print(f'   for comparison a never-updating market at its average price: rms gap {np.sqrt(np.average((np.average(rw[valid],weights=nw[valid])-rw[valid])**2,weights=nw[valid])):.3f}')
# ---- 4. prequential scores: who predicted next week's results best?
rng = np.random.default_rng(5)
def preq_const(rho0, s0):
    out = np.zeros(len(g))
    for k in range(nW):
        sel = wk == k
        if sel.any(): out[sel] = np.log(PY[sel] @ post_const(k, rho0, s0))
    return out
def preq_rw(rho0, s0, q):                      # truth drifts as a random walk, weekly step sd q: grid forward filter
    K = norm.pdf(R[:, None], R[None, :], q); K /= K.sum(axis=0, keepdims=True); p = norm.pdf(R, rho0, s0); p /= p.sum(); out = np.zeros(len(g)); track = []
    for k in range(nW):
        sel = wk == k; track.append(stats(p))
        if sel.any(): out[sel] = np.log(PY[sel] @ p); p = p * np.exp(Lw[k] - Lw[k].max()); p /= p.sum()
        p = K @ p
    return out, track
def cmp(lab, s):
    dlt = s - l_mkt; wsum = np.bincount(wk, weights=dlt, minlength=nW); bs = [rng.choice(wsum, nW).sum() for _ in range(4000)]
    print(f'   {lab:58s} total log score v market {dlt.sum():+7.2f}  (weekly bootstrap 95% {np.percentile(bs,2.5):+6.1f} to {np.percentile(bs,97.5):+6.1f})')
    return dlt.sum()
print(f'\n4. OUT-OF-SAMPLE LOG SCORE against the market, {len(g)} matches (positive = predicted better than the calibrated price)')
cmp('learner, flat prior', preq_const(1.0, 5.0)); cmp('learner, sceptic prior at no change (1.00, sd 0.25)', preq_const(1.0, 0.25))
for s0 in [0.03, 0.06, 0.10, 0.15, 0.25, 0.50]: cmp(f'learner starting at the market\'s first price ({r_first:.2f}), prior sd {s0:.2f}', preq_const(r_first, s0))
cmp(f'learner with the market-implied prior ({rho0_m:.2f}, sd {s0_m:.3f})', preq_const(rho0_m, s0_m))
for q in [0.01, 0.03]: cmp(f'drifting truth, weekly step sd {q:.2f}, start {r_first:.2f} sd 0.15', preq_rw(r_first, 0.15, q)[0])
# ---- 5. (moved) whether the market's revisions carry information is tested in kappa_clean.py, which avoids two biases found on the way
# ---- 6. criteria C1 and C2
D = np.arange(-0.30, 0.3001, 0.002); Ld = np.zeros((nW, len(D))); np.add.at(Ld, wk, ll(g.eta0.values[:, None] + D[None, :], g.c.values[:, None], g.y.values[:, None]))
cumD = np.cumsum(Ld, axis=0); i0 = np.argmin(np.abs(D)); pi_neg = np.where(D < -1e-9, norm.pdf(D, 0, 0.05), 0); pi_neg /= pi_neg.sum(); pi_two = norm.pdf(D, 0, 0.05); pi_two /= pi_two.sum()
M1 = np.exp(cumD - cumD[:, [i0]]) @ pi_neg; M2 = np.exp(cumD - cumD[:, [i0]]) @ pi_two
print(f'\n6. C1, ANYTIME-VALID TEST of "the calibrated market is right": running ratio peaks at {M1.max():.1f} in the week of {cuts[M1.argmax()].date()} (needs 20). Anytime-valid p = {min(1,1/M1.max()):.3f}. Final ratio {M1[-1]:.1f}. Two-sided version peaks at {M2.max():.1f}.')
early = ((g.Date >= '2020-09-01') & (g.Date <= '2020-11-30')).values; latep = ((g.Date >= '2021-03-01') & (g.Date <= '2021-06-30')).values
rE, rL = np.average(g.r[early], weights=info[early]), np.average(g.r[latep], weights=info[latep])
pc = (pF[np.abs(R - rL) < np.abs(R - rE)]).sum()
print(f'   C2, CORRECTION: market priced {rE:.3f} in Sep-Nov 2020 and {rL:.3f} in Mar-Jun 2021. Constant truth: P(late error smaller than early error) = {pc:.3f}')
# drifting truth: smoothed posterior of rho in each window via forward-backward on the grid
def smooth(q):
    K = norm.pdf(R[:, None], R[None, :], q); K /= K.sum(axis=0, keepdims=True); f = []; p = np.ones(len(R)) / len(R)
    for k in range(nW): p = p * np.exp(Lw[k] - Lw[k].max()); p /= p.sum(); f.append(p.copy()); p = K @ p
    bk = np.ones(len(R)); sm = [None] * nW
    for k in range(nW - 1, -1, -1):
        s = f[k] * bk; sm[k] = s / s.sum(); bk = K.T @ (bk * np.exp(Lw[k] - Lw[k].max())); bk /= bk.max()
    return np.array(sm)
for q in [0.01, 0.03]:
    sm = smooth(q); wE = np.unique(wk[early]); wL = np.unique(wk[latep]); rs = np.random.default_rng(1); cnt = 0; draws = 4000
    # joint draws need the full path; approximate with independent draws from the two window-average marginals (windows are 3+ months apart)
    pE = sm[wE].mean(axis=0); pL = sm[wL].mean(axis=0); xe = rs.choice(R, draws, p=pE / pE.sum()); xl = rs.choice(R, draws, p=pL / pL.sum())
    print(f'   drifting truth (weekly step sd {q:.2f}): truth Sep-Nov {(pE*R).sum():.2f}, Mar-Jun {(pL*R).sum():.2f} | P(late error smaller than early error) = {(np.abs(xl-rL) < np.abs(xe-rE)).mean():.3f}')
np.savez('work/learn_paths.npz', cuts=cuts.values.astype('datetime64[D]').astype(str), rw=rw, nw=nw, flat=np.array([stats(post_const(k, 1.0, 5.0)) for k in range(nW)]), mktprior=np.array([stats(post_const(k, rho0_m, s0_m)) for k in range(nW)]), M1=M1, rho0_m=rho0_m, s0_m=s0_m, r_first=r_first)
