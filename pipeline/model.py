"""How fast should the market have learned? Hierarchical real-time model of the market's error in home advantage.
Layer 1: what home advantage did prices imply (H_mkt), by league and month, team-season strengths removed.
Layer 2: delta = true latent home supremacy minus the calibrated market's, by crowd regime, pooled across leagues
         (delta_league ~ N(delta_bar, tau^2)). Posterior on a grid, updated week by week using past matches only.
Usage: python model.py [prior_sd]   (prior sd of delta_bar, default 0.05)"""
import sys, pandas as pd, numpy as np
from scipy.stats import norm
from scipy.optimize import minimize
PRIOR_SD = float(sys.argv[1]) if len(sys.argv) > 1 else 0.05
d = pd.read_pickle('work/model.pkl')
def ll(eta, c, y):
    ph = norm.cdf(eta - c); pa = norm.cdf(-eta - c); pd_ = np.clip(1 - ph - pa, 1e-12, None)
    return np.where(y == 1, np.log(np.clip(ph, 1e-12, None)), np.where(y == -1, np.log(np.clip(pa, 1e-12, None)), np.log(pd_)))
# ---- calibration on normal crowd games before Covid: eta = a + b * mu
pre = d[(d.regime == 'full') & (d.Date < '2020-03-01')]
fit = minimize(lambda p: -ll(p[0] + p[1] * pre.mu.values, pre.c.values, pre.y.values).sum(), [0, 1], method='BFGS')
a, b = fit.x; se_a, se_b = np.sqrt(np.diag(fit.hess_inv))
print(f'CALIBRATION, {len(pre)} crowd games to Feb 2020: a = {a:+.4f} (se {se_a:.4f}), b = {b:.4f} (se {se_b:.4f})')
d['eta0'] = a + b * d.mu
# ---- layer 1: market-implied home advantage with team-season strengths removed
rows = []
d['ym'] = d.Date.dt.to_period('M')
for (lg, sea), x in d.groupby(['league', 'season']):
    teams = sorted(set(x.HomeTeam) | set(x.AwayTeam)); ti = {t: i for i, t in enumerate(teams)}
    cells = sorted(set(zip(x.regime, x.ym))); ci = {k: i for i, k in enumerate(cells)}
    X = np.zeros((len(x), len(cells) + len(teams)))
    for r, (h, aw, rg, ym) in enumerate(zip(x.HomeTeam, x.AwayTeam, x.regime, x.ym)):
        X[r, ci[(rg, ym)]] = 1; X[r, len(cells) + ti[h]] = 1; X[r, len(cells) + ti[aw]] = -1
    beta = np.linalg.lstsq(X, x.mu.values, rcond=None)[0]
    for k, i in ci.items(): rows.append([lg, sea, k[0], k[1], beta[i], int(X[:, i].sum())])
H = pd.DataFrame(rows, columns=['league', 'season', 'regime', 'ym', 'H', 'n'])
wm = lambda g: np.average(g.H, weights=g.n)
Hpre = H[(H.regime == 'full') & (H.season.between(2015, 2019))].groupby('league').apply(wm).rename('H_pre')
H = H.join(Hpre, on='league'); H['mkt_true_scale'] = a + b * H.H; H['pre_true_scale'] = a + b * H.H_pre
H.to_pickle('work/H.pkl')
print('\nLAYER 1: home advantage implied by prices (latent units, team strengths removed)')
byseason = H[H.regime == 'full'].groupby('season').apply(lambda g: pd.Series({'H_full': np.average(g.H, weights=g.n), 'n': g.n.sum()}))
print('  crowd games by season:', {int(k): round(v, 3) for k, v in byseason.H_full.items()})
gh = H[H.regime == 'none']; pooled_pre = np.average(H[(H.regime == 'full') & H.season.between(2015, 2019)].H, weights=H[(H.regime == 'full') & H.season.between(2015, 2019)].n)
print(f'  pre-Covid 2015/16-2019/20 crowd games: {pooled_pre:.3f} | closed-door games, first wave: {np.average(gh[gh.ym < "2021-07"].H, weights=gh[gh.ym < "2021-07"].n):.3f} | later closures: {np.average(gh[gh.ym >= "2021-07"].H, weights=gh[gh.ym >= "2021-07"].n):.3f} | partial: {wm(H[H.regime == "partial"]):.3f}')
# ---- layer 2: grid posterior for delta in closed-door games
G = np.arange(-0.30, 0.3001, 0.004); DB = np.arange(-0.16, 0.1601, 0.004); TAU = np.array([0.002, 0.01, 0.02, 0.03, 0.04, 0.06, 0.08, 0.10])
prior = norm.pdf(DB, 0, PRIOR_SD)[:, None] * norm.pdf(TAU, 0, 0.05)[None, :]   # skeptical: centred on "the market is right"
W = norm.pdf(G[None, None, :], DB[:, None, None], TAU[None, :, None]); W /= W.sum(axis=2, keepdims=True)   # P(delta_l | delta_bar, tau)
g = d[d.regime == 'none'].copy().reset_index(drop=True)
L = ll(g.eta0.values[:, None] + G[None, :], g.c.values[:, None], g.y.values[:, None])   # match x grid log-likelihood
leagues = sorted(g.league.unique())
def posterior(mask):
    """Posterior over (delta_bar, tau) and shrunk league effects, from the matches in mask."""
    logp = np.log(prior); lik = {}
    for lg in leagues:
        s = L[mask & (g.league.values == lg)].sum(axis=0); li = np.exp(s - s.max()); lik[lg] = li
        logp = logp + np.log(W @ li)
    p = np.exp(logp - logp.max()); p /= p.sum()
    dl = {lg: float((p * ((W * (lik[lg] * G)).sum(axis=2) / (W @ lik[lg]))).sum()) for lg in leagues}
    mb = float((p.sum(axis=1) * DB).sum()); sb = float(np.sqrt((p.sum(axis=1) * (DB - mb) ** 2).sum()))
    return dict(mean=mb, sd=sb, p_neg=float(p.sum(axis=1)[DB < 0].sum() + 0.5 * p.sum(axis=1)[np.isclose(DB, 0)].sum()), tau=float((p.sum(axis=0) * TAU).sum()), league=dl, lo=float(DB[np.searchsorted(np.cumsum(p.sum(axis=1)), 0.025)]), hi=float(DB[np.searchsorted(np.cumsum(p.sum(axis=1)), 0.975)]))
allm = np.ones(len(g), bool); first = (g.wave == 'first').values
P = posterior(first)
print(f'\nLAYER 2, all first-wave closed-door games (n={first.sum()}), prior sd {PRIOR_SD}:')
print(f'  delta_bar = {P["mean"]:+.4f} (sd {P["sd"]:.4f}, 95% {P["lo"]:+.3f} to {P["hi"]:+.3f}) | P(market over-rated home sides) = {P["p_neg"]:.3f} | between-league sd tau = {P["tau"]:.3f}')
print('  shrunk league effects:', {k: round(v, 3) for k, v in sorted(P['league'].items(), key=lambda kv: kv[1])})
# what it means in the currency people use
Hg = np.average(gh[gh.ym < "2021-07"].H, weights=gh[gh.ym < "2021-07"].n); cbar = d.c.mean()
sup = lambda eta: norm.cdf(eta - cbar) - norm.cdf(-eta - cbar)
t_pre, t_mkt, t_true = a + b * pooled_pre, a + b * Hg, a + b * Hg + P['mean']
print(f'  home advantage, even match, home win minus away win probability: with crowds {sup(t_pre)*100:.1f} pts | closed doors as priced {sup(t_mkt)*100:.1f} pts | closed doors, model {sup(t_true)*100:.1f} pts (95% {sup(a+b*Hg+P["lo"])*100:.1f} to {sup(a+b*Hg+P["hi"])*100:.1f})')
print(f'  share of home advantage removed: market priced {100*(1-t_mkt/t_pre):.0f}% | model estimate {100*(1-t_true/t_pre):.0f}% (95% {100*(1-(a+b*Hg+P["hi"])/t_pre):.0f}% to {100*(1-(a+b*Hg+P["lo"])/t_pre):.0f}%)')
# ---- real time: weekly cut-offs, posterior from strictly earlier matches, then score the following week
cuts = pd.date_range('2020-05-11', g.Date.max() + pd.Timedelta(days=7), freq='7D'); track = []; g['dhat'] = 0.0; g['dbar'] = 0.0
for c0, c1 in zip(cuts[:-1], cuts[1:]):
    wk = ((g.Date >= c0) & (g.Date < c1)).values
    if not wk.any(): continue
    past = (g.Date < c0).values
    Pp = posterior(past) if past.any() else dict(mean=0.0, sd=PRIOR_SD, p_neg=0.5, league={lg: 0.0 for lg in leagues}, lo=-1.96 * PRIOR_SD, hi=1.96 * PRIOR_SD, tau=0.04)
    g.loc[wk, 'dhat'] = g.loc[wk, 'league'].map(Pp['league']).values; g.loc[wk, 'dbar'] = Pp['mean']
    hm = H[(H.regime == 'none') & (H.ym == c0.to_period('M'))]
    track.append([c0, int(past.sum()), Pp['mean'], Pp['sd'], Pp['lo'], Pp['hi'], Pp['p_neg'], np.average(hm.H, weights=hm.n) if len(hm) else np.nan, np.average(hm.H_pre, weights=hm.n) if len(hm) else np.nan])
T = pd.DataFrame(track, columns=['week', 'n_seen', 'mean', 'sd', 'lo', 'hi', 'p_neg', 'H_mkt', 'H_pre']); T.to_csv('work/model_track.csv', index=False)
print('\nREAL-TIME LEARNER (posterior for delta_bar from matches before each date):')
for dt in ['2020-06-08', '2020-07-06', '2020-08-03', '2020-10-05', '2020-11-02', '2020-12-07', '2021-01-04', '2021-02-01', '2021-03-01', '2021-04-05', '2021-05-03', '2021-11-22', '2022-01-10', '2023-12-18']:
    r = T[T.week <= dt].iloc[-1]; print(f'  {r.week.date()}  seen {int(r.n_seen):5d}  delta_bar {r["mean"]:+.4f} (sd {r.sd:.4f})  P(home sides over-rated) {r.p_neg:.2f}')
# ---- prequential score: could the learner beat the price, out of sample?
def probs(eta, c): ph = norm.cdf(eta - c); pa = norm.cdf(-eta - c); return ph, 1 - ph - pa, pa
rng = np.random.default_rng(21)
def score(x, lab):
    y = x.y.values; out = {}
    for name, eta in [('market', x.mu.values), ('calibrated market', x.eta0.values), ('learner, pooled', x.eta0.values + x.dbar.values), ('learner, by league', x.eta0.values + x.dhat.values)]:
        out[name] = ll(eta, x.c.values, y)
    base = out['calibrated market']
    print(f'  {lab} (n={len(x)}): log loss  ' + ' | '.join(f'{k} {-v.mean():.5f}' for k, v in out.items()))
    for k in ['learner, pooled', 'learner, by league']:
        dlt = out[k] - base; print(f'      {k} minus calibrated market, per match: {dlt.mean():+.6f} (se {dlt.std()/np.sqrt(len(x)):.6f}, t {dlt.mean()/(dlt.std()/np.sqrt(len(x))):+.2f})')
    # betting: stake 1 on any outcome whose learner probability times Pinnacle closing odds exceeds 1.02
    ph, pdw, pa = probs(x.eta0.values + x.dbar.values, x.c.values); O = x[['PSCH', 'PSCD', 'PSCA']].values.astype(float); Pm = np.column_stack([ph, pdw, pa]); won = np.column_stack([y == 1, y == 0, y == -1])
    for thr in [1.0, 1.02]:
        sel = (Pm * O > thr); r = np.where(won, O - 1, -1.0)[sel]
        if len(r) > 20:
            bs = [rng.choice(r, len(r)).mean() for _ in range(3000)]; print(f'      bets where learner EV > {100*(thr-1):.0f}%: {len(r)} bets ({int(sel[:,2].sum())} away, {int(sel[:,0].sum())} home, {int(sel[:,1].sum())} draw), return {r.mean()*100:+.1f}% [{np.percentile(bs,2.5)*100:+.1f}, {np.percentile(bs,97.5)*100:+.1f}]')
print('\nOUT-OF-SAMPLE SCORE (each match predicted with the posterior from earlier weeks only):')
score(g[first], 'first wave'); score(g[first & (g.Date >= '2020-09-01').values], 'first wave from Sep 2020'); score(g[~first], 'later closures')
g.to_pickle('work/model_ghost.pkl')
# ---- other regimes for reference: single pooled delta by maximum likelihood
print('\nREFERENCE REGIMES (pooled delta, maximum likelihood on the same scale):')
for lab, x in [('partial crowds 2020/21 and capped 2021/22', d[d.regime == 'partial']), ('crowd games 2021/22 on (return of fans)', d[(d.regime == 'full') & (d.Date >= '2021-07-01')]), ('crowd games 2021/22 only', d[(d.regime == 'full') & (d.season == 2021)]), ('placebo: crowd games 2018/19', d[(d.regime == 'full') & (d.season == 2018)]), ('later closures alone', d[(d.regime == 'none') & (d.wave == 'later')])]:
    s = ll(x.eta0.values[:, None] + G[None, :], x.c.values[:, None], x.y.values[:, None]).sum(axis=0); i = s.argmax(); cur = -(s[i + 1] - 2 * s[i] + s[i - 1]) / 0.004 ** 2
    print(f'  {lab:44s} n={len(x):6d} delta {G[i]:+.3f} (se {1/np.sqrt(cur):.3f})')
