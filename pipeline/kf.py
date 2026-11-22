"""Layer 1 done properly: read the market's belief about home advantage from prices in real time, with a Kalman filter.
State per league: home advantage under each crowd regime (full, none, partial) and one strength per team, all random walks.
Observation per match: mu = H_regime + s_home - s_away + noise. Only prices are used, never results, and each estimate
uses prices from strictly earlier dates (H_prior) or up to and including the match date (H_post)."""
import pandas as pd, numpy as np, sys
from scipy.optimize import minimize
d = pd.read_pickle('work/model_all.pkl').sort_values('Date').reset_index(drop=True)
d['reg'] = d.regime.map({'full': 0, 'none': 1, 'partial': 2, 'drop': 0}).astype(int)
def run(x, qs, qh, qbreak, R, out=False):
    teams = sorted(set(x.HomeTeam) | set(x.AwayTeam)); ti = {t: i + 3 for i, t in enumerate(teams)}; n = len(teams) + 3
    m = np.zeros(n); m[:3] = [0.22, 0.20, 0.20]; P = np.eye(n) * 0.5 ** 2; P[0, 0] = 0.1 ** 2; P[1, 1] = P[2, 2] = 0.15 ** 2
    seen = np.zeros(n, bool); llk = 0.0; res = []; last = None
    dates = x.Date.values; hs = x.HomeTeam.map(ti).values; as_ = x.AwayTeam.map(ti).values; rg = x.reg.values; mu = x.mu.values; idx = x.index.values
    i = 0; N = len(x)
    while i < N:
        j = i
        while j < N and dates[j] == dates[i]: j += 1
        if last is not None:
            dt = (dates[i] - last) / np.timedelta64(1, 'D'); dg = np.r_[np.full(3, qh * dt), np.full(n - 3, qs * dt + (qbreak if dt > 45 else 0.0))]
            dg[[1, 2]] = np.where(seen[[1, 2]], dg[[1, 2]], 0.0)       # an unused regime keeps its prior until first seen
            P[np.diag_indices(n)] += dg
        last = dates[i]; prior = [(m[rg[k]], P[rg[k], rg[k]]) for k in range(i, j)]
        for k in range(i, j):
            h, a_, r = hs[k], as_[k], rg[k]; Ph = P[:, r] + P[:, h] - P[:, a_]; S = Ph[r] + Ph[h] - Ph[a_] + R; e = mu[k] - (m[r] + m[h] - m[a_])
            llk += -0.5 * (np.log(2 * np.pi * S) + e * e / S); K = Ph / S; m += K * e; P -= np.outer(K, Ph); seen[r] = True
            if out: res.append([idx[k], e, S])
        if out:
            for k in range(i, j): res[k - j][3:] = []; res[k - j] += [prior[k - i][0], prior[k - i][1], m[rg[k]], P[rg[k], rg[k]], m[0]]
        i = j
    return (llk, pd.DataFrame(res, columns=['i', 'innov', 'S', 'H_prior', 'V_prior', 'H_post', 'V_post', 'H_full_post']).set_index('i')) if out else llk
if len(sys.argv) > 1 and sys.argv[1] == 'fit':
    sub = {lg: d[d.league == lg] for lg in ['E0', 'D1', 'SP2', 'N1']}
    f = lambda p: -sum(run(x, *np.exp(p)) for x in sub.values())
    o = minimize(f, np.log([2e-5, 2e-7, 0.01, 0.006]), method='Nelder-Mead', options={'xatol': 0.05, 'fatol': 0.5, 'maxiter': 160}); print('fitted (qs/day, qh/day, qbreak, R):', np.exp(o.x), 'loglik', -o.fun); np.save('work/kf_par.npy', np.exp(o.x))
par = np.load('work/kf_par.npy'); print('hyperparameters: strength sd per week %.4f | home advantage sd per week %.5f | summer break sd %.3f | match noise sd %.3f' % (np.sqrt(par[0] * 7), np.sqrt(par[1] * 7), np.sqrt(par[2]), np.sqrt(par[3])))
outs = []; tot = 0
for lg, x in d.groupby('league'):
    l, o = run(x, *par, out=True); outs.append(o); tot += l
K = pd.concat(outs); d = d.join(K); d.to_pickle('work/kf.pkl')
print('total log-likelihood', round(tot, 1), '| innovation sd', round(d.innov.std(), 4), '| mean H_post by regime:', d.groupby('regime').H_post.mean().round(3).to_dict())
print('posterior sd of H in real time (typical):', d.groupby('regime').V_post.apply(lambda s: np.sqrt(s.median())).round(4).to_dict())
