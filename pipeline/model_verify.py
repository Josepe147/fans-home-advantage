"""Verification of the base model.
A. Recovery: simulate results from the model with a known delta and check the posterior finds it, with honest intervals.
B. Peeking: under 'the market is exactly right', how often does the weekly running posterior cross 0.95 or 0.99 at some point?
C. Draw width: does the market's draw probability need its own calibration?
D. Reliability of the calibrated price in normal games.
E. De-vig method: proportional against power.
F. One worked match."""
import pandas as pd, numpy as np, time
from scipy.stats import norm, chi2
from scipy.optimize import minimize, brentq
rng = np.random.default_rng(2026)
d = pd.read_pickle('work/model.pkl')
def ll(eta, c, y):
    ph = norm.cdf(eta - c); pa = norm.cdf(-eta - c); pdw = np.clip(1 - ph - pa, 1e-12, None)
    return np.where(y == 1, np.log(np.clip(ph, 1e-12, None)), np.where(y == -1, np.log(np.clip(pa, 1e-12, None)), np.log(pdw)))
pre = d[(d.regime == 'full') & (d.Date < '2020-03-01')]
a, b = minimize(lambda p: -ll(p[0] + p[1] * pre.mu.values, pre.c.values, pre.y.values).sum(), [0, 1], method='Nelder-Mead', options={'xatol': 1e-7, 'fatol': 1e-9}).x
g = d[(d.regime == 'none') & (d.wave == 'first')].sort_values('Date').reset_index(drop=True); eta0 = (a + b * g.mu).values; c = g.c.values
G = np.arange(-0.30, 0.3001, 0.004); DB = np.arange(-0.16, 0.1601, 0.004); TAU = np.array([0.002, 0.01, 0.02, 0.03, 0.04, 0.06, 0.08, 0.10])
prior = norm.pdf(DB, 0, 0.05)[:, None] * norm.pdf(TAU, 0, 0.05)[None, :]
W = norm.pdf(G[None, None, :], DB[:, None, None], TAU[None, :, None]); W /= W.sum(axis=2, keepdims=True)
lg = g.league.values; leagues = sorted(set(lg)); idx = {l: np.where(lg == l)[0] for l in leagues}
# precompute the three outcome log-likelihood surfaces once: they depend on eta0, c and the grid only
PH = norm.cdf(eta0[:, None] + G[None, :] - c[:, None]); PA = norm.cdf(-(eta0[:, None] + G[None, :]) - c[:, None]); LH, LA, LD = np.log(PH), np.log(PA), np.log(np.clip(1 - PH - PA, 1e-12, None))
def post_from_sums(S):   # S: dict league -> summed log-lik over the grid
    logp = np.log(prior)
    for l in leagues:
        s = S[l]; logp = logp + np.log(W @ np.exp(s - s.max()))
    p = np.exp(logp - logp.max()); p /= p.sum(); m = p.sum(axis=1); mean = (m * DB).sum(); cum = np.cumsum(m)
    return mean, DB[np.searchsorted(cum, 0.025)], DB[np.searchsorted(cum, 0.975)], m[DB < -1e-9].sum() + 0.5 * m[np.abs(DB) < 1e-9].sum(), (p.sum(axis=0) * TAU).sum()
def simulate(dbar, tau):
    dl = {l: rng.normal(dbar, tau) for l in leagues}; e = eta0 + np.array([dl[l] for l in lg]); u = rng.random(len(e)); ph = norm.cdf(e - c); pa = norm.cdf(-e - c)
    return np.where(u < ph, 1, np.where(u < ph + pa, -1, 0))
def Lmat(y): return np.where((y == 1)[:, None], LH, np.where((y == -1)[:, None], LA, LD))
print(f'A. RECOVERY on the real fixture list ({len(g)} matches, {len(leagues)} leagues), 300 simulated seasons per setting')
for dbar, tau in [(0.0, 0.0), (-0.03, 0.0), (-0.03, 0.02), (-0.06, 0.02), (0.0, 0.02)]:
    out = []
    for _ in range(300):
        L = Lmat(simulate(dbar, tau)); out.append(post_from_sums({l: L[idx[l]].sum(axis=0) for l in leagues}))
    o = np.array(out); print(f'   true delta_bar {dbar:+.2f}, tau {tau:.2f}: posterior mean averages {o[:,0].mean():+.4f} (sd across sims {o[:,0].std():.4f}) | 95% interval covers the truth {100*((o[:,1]<=dbar+1e-9)&(o[:,2]>=dbar-1e-9)).mean():.0f}% | mean tau estimate {o[:,4].mean():.3f} | P(delta<0)>0.95 in {100*(o[:,3]>0.95).mean():.0f}% of sims')
print('B. PEEKING: the market is exactly right (delta = 0, tau = 0). Weekly running posterior from 1 Sep 2020 to 30 Jun 2021.')
cuts = pd.date_range('2020-09-07', '2021-06-28', freq='7D'); pos = {l: np.searchsorted(g.Date.values[idx[l]], cuts.values) for l in leagues}; mx = []
for _ in range(300):
    L = Lmat(simulate(0.0, 0.0)); cs = {l: np.vstack([np.zeros(len(G)), np.cumsum(L[idx[l]], axis=0)]) for l in leagues}
    pn = [post_from_sums({l: cs[l][pos[l][k]] for l in leagues})[3] for k in range(len(cuts))]; mx.append((max(pn), min(pn), pn[-1]))
mx = np.array(mx)
print(f'   {len(cuts)} weekly looks. Running P(home sides over-rated) reached 0.95 at some look in {100*(mx[:,0]>=0.95).mean():.0f}% of seasons, 0.99 in {100*(mx[:,0]>=0.99).mean():.0f}%. At the final look alone: 0.95 in {100*(mx[:,2]>=0.95).mean():.0f}%, 0.99 in {100*(mx[:,2]>=0.99).mean():.0f}%.')
print(f'   either direction (over- or under-rated) reaching 0.99 at some look: {100*((mx[:,0]>=0.99)|(mx[:,1]<=0.01)).mean():.0f}%')
NOISE = float(open('work/season_noise_sd.txt').read()); mx2 = []
for _ in range(300):
    L = Lmat(simulate(rng.normal(0, NOISE), 0.0)); cs = {l: np.vstack([np.zeros(len(G)), np.cumsum(L[idx[l]], axis=0)]) for l in leagues}
    pn = [post_from_sums({l: cs[l][pos[l][k]] for l in leagues})[3] for k in range(len(cuts))]; mx2.append((max(pn), min(pn), pn[-1]))
mx2 = np.array(mx2)
print(f'   B2. Same, but the market is only as right as in an ordinary season (season miss drawn from N(0, {NOISE:.4f}^2)): reached 0.95 at some look in {100*(mx2[:,0]>=0.95).mean():.0f}% of seasons, 0.99 in {100*(mx2[:,0]>=0.99).mean():.0f}% | either direction 0.99: {100*((mx2[:,0]>=0.99)|(mx2[:,1]<=0.01)).mean():.0f}% | final look 0.92 or more: {100*(mx2[:,2]>=0.92).mean():.0f}%')
print('C. DRAW WIDTH: eta = a + b*mu, c scaled by k')
f3 = minimize(lambda p: -ll(p[0] + p[1] * pre.mu.values, p[2] * pre.c.values, pre.y.values).sum(), [0, 1, 1], method='Nelder-Mead', options={'xatol': 1e-7, 'fatol': 1e-9})
l2 = ll(a + b * pre.mu.values, pre.c.values, pre.y.values).sum(); lr = 2 * (-f3.fun - l2)
print(f'   a={f3.x[0]:+.4f} b={f3.x[1]:.4f} k={f3.x[2]:.4f} | likelihood ratio v k=1: {lr:.2f}, p = {1-chi2.cdf(lr,1):.3f}')
Gf = np.arange(-0.3, 0.3001, 0.002)
def mle(eta, cc, y):
    s = ll(eta[:, None] + Gf[None, :], cc[:, None], y[:, None]).sum(axis=0); i = s.argmax(); return Gf[i], 1 / np.sqrt(-(s[i + 1] - 2 * s[i] + s[i - 1]) / 0.002 ** 2)
print('   closed-door delta with k fitted: %+.4f (se %.4f) | with k = 1: %+.4f (se %.4f)' % (mle(f3.x[0] + f3.x[1] * g.mu.values, f3.x[2] * c, g.y.values) + mle(eta0, c, g.y.values)))
print('D. RELIABILITY of the calibrated price, normal games to Feb 2020 (deciles of predicted probability)')
e = a + b * pre.mu.values; P = {'home': norm.cdf(e - pre.c.values), 'away': norm.cdf(-e - pre.c.values)}; P['draw'] = 1 - P['home'] - P['away']; O = {'home': pre.y.values == 1, 'away': pre.y.values == -1, 'draw': pre.y.values == 0}
for k in ['home', 'draw', 'away']:
    q = pd.qcut(P[k], 10, labels=False, duplicates='drop'); t = pd.DataFrame({'p': P[k], 'o': O[k], 'q': q}).groupby('q').agg(p=('p', 'mean'), o=('o', 'mean'), n=('o', 'size')); hl = (t.n * (t.o - t.p) ** 2 / (t.p * (1 - t.p))).sum()
    print(f'   {k}: largest gap between predicted and observed {100*(t.o-t.p).abs().max():.1f} points | chi-square {hl:.1f} on {len(t)} bins, p = {1-chi2.cdf(hl,len(t)-2):.2f}')
print('E. DE-VIG METHOD: power method (probabilities = (1/odds)^k, k solved per match) in place of proportional')
def power(o):
    inv = 1 / o; k = np.array([brentq(lambda kk: (r ** kk).sum() - 1, 0.5, 3) for r in inv]); return inv ** k[:, None]
def redo(x):
    p = power(x[['PSCH', 'PSCD', 'PSCA']].values.astype(float)); zh, za = norm.ppf(p[:, 0]), norm.ppf(p[:, 2]); return (zh - za) / 2, -(zh + za) / 2
mu_p, c_p = redo(pre); ap, bp = minimize(lambda p: -ll(p[0] + p[1] * mu_p, c_p, pre.y.values).sum(), [0, 1], method='Nelder-Mead').x; mu_g, c_g = redo(g)
print('   calibration a=%+.4f b=%.4f | closed-door delta %+.4f (se %.4f)' % ((ap, bp) + mle(ap + bp * mu_g, c_g, g.y.values)))
print('F. WORKED MATCH')
r = g[(g.league == 'E0') & (g.HomeTeam == 'Liverpool')].iloc[0]; inv = 1 / np.array([r.PSCH, r.PSCD, r.PSCA]); e0 = a + b * r.mu
print(f'   {r.HomeTeam} v {r.AwayTeam}, {r.Date.date()}, closed doors. Pinnacle close {r.PSCH}/{r.PSCD}/{r.PSCA}. Book {100*inv.sum():.1f}%. Fair probs {r.pc_h:.3f}/{r.pc_d:.3f}/{r.pc_a:.3f}')
print(f'   z_home {norm.ppf(r.pc_h):+.3f}, z_away {norm.ppf(r.pc_a):+.3f} -> mu {r.mu:.3f}, c {r.c:.3f} | calibrated eta0 {e0:.3f}')
for dl in [0.0, -0.020]:
    print(f'   delta {dl:+.3f}: home {norm.cdf(e0+dl-r.c):.3f} draw {1-norm.cdf(e0+dl-r.c)-norm.cdf(-e0-dl-r.c):.3f} away {norm.cdf(-e0-dl-r.c):.3f}')
m2 = d[(d.pc_h.between(0.44, 0.46)) & (d.pc_a.between(0.27, 0.29))].iloc[0]; print(f'   an even-ish match for scale: fair probs {m2.pc_h:.3f}/{m2.pc_d:.3f}/{m2.pc_a:.3f} -> mu {m2.mu:.3f}, c {m2.c:.3f}')
