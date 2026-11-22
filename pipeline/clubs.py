"""Club home advantage: priced (from prices only) and mispriced (results against the calibrated price). Usage: python clubs.py expl | hold"""
import sys, pandas as pd, numpy as np
from scipy.stats import norm
from scipy.optimize import minimize
which = sys.argv[1]
d = pd.read_pickle('work/kf.pkl'); d = d[d.regime == 'full'].copy()
def ll(eta, c, y):
    ph = norm.cdf(eta - c); pa = norm.cdf(-eta - c); pdw = np.clip(1 - ph - pa, 1e-12, None)
    return np.where(y == 1, np.log(np.clip(ph, 1e-12, None)), np.where(y == -1, np.log(np.clip(pa, 1e-12, None)), np.log(pdw)))
pre = d[d.Date < '2020-03-01']
a, b = minimize(lambda p: -ll(p[0] + p[1] * pre.mu.values, pre.c.values, pre.y.values).sum(), [0, 1], method='Nelder-Mead', options={'xatol': 1e-7, 'fatol': 1e-9}).x
e = a + b * d.mu; ph = norm.cdf(e - d.c); pa = norm.cdf(-e - d.c); f1 = norm.pdf(e - d.c); f2 = norm.pdf(e + d.c)
d['score'] = np.where(d.y == 1, f1 / ph, np.where(d.y == -1, -f2 / pa, (f2 - f1) / (1 - ph - pa))); d['info'] = f1 ** 2 / ph + f2 ** 2 / pa + (f2 - f1) ** 2 / (1 - ph - pa); d['z'] = d.score / d['info']
d['ls'] = d.league + d.season.astype(str)
def club_season(x):
    """g_hat, m_hat, their noise variances, and priced h per club-season"""
    x = x.copy(); x['zc'] = x.z - (x.z * x['info']).groupby(x.ls).transform('sum') / x['info'].groupby(x.ls).transform('sum')
    hm = x.groupby(['ls', 'HomeTeam']).apply(lambda q: pd.Series({'zh': np.average(q.zc, weights=q['info']), 'vh': 1 / q['info'].sum(), 'nh': len(q)}))
    aw = x.groupby(['ls', 'AwayTeam']).apply(lambda q: pd.Series({'za': np.average(q.zc, weights=q['info']), 'va': 1 / q['info'].sum(), 'na': len(q)}))
    hm.index.names = aw.index.names = ['ls', 'team']; t = hm.join(aw, how='inner'); t = t[(t.nh >= 8) & (t.na >= 8)]
    t['g'] = t.zh + t.za; t['m'] = (t.zh - t.za) / 2; t['vg'] = t.vh + t.va; t['vm'] = (t.vh + t.va) / 4
    rows = []                                                       # priced club home advantage, round robin within league-season
    for ls, q in x.groupby('ls'):
        teams = sorted(set(q.HomeTeam) | set(q.AwayTeam)); n = len(teams); ti = {k: i for i, k in enumerate(teams)}; X = np.zeros((len(q), 2 * n))
        for r, (h, aw_) in enumerate(zip(q.HomeTeam, q.AwayTeam)): X[r, ti[h]] = 1; X[r, n + ti[aw_]] = -1
        beta = np.linalg.lstsq(X, q.mu.values, rcond=None)[0]; hh = beta[:n] - beta[n:]; hh = hh - hh.mean(); s2 = ((q.mu.values - X @ beta) ** 2).sum() / max(1, len(q) - 2 * n); C = s2 * np.linalg.pinv(X.T @ X)
        for k, i in ti.items(): rows.append([ls, k, b * hh[i], b * b * (C[i, i] + C[n + i, n + i] - 2 * C[i, n + i])])
    P = pd.DataFrame(rows, columns=['ls', 'team', 'h', 'vhh']).set_index(['ls', 'team'])
    t = t.join(P, how='left').reset_index(); t['league'] = t.ls.str[:-4]; t['season'] = t.ls.str[-4:].astype(int); return t
if which == 'expl':
    x = d[(d.season >= 2012) & (d.Date < '2020-03-01')]; T = club_season(x); T.to_pickle('work/club_expl.pkl')
    print(f'EXPLORATION: {len(x)} crowd matches, {len(T)} club-seasons, {T.team.nunique()} clubs')
    print(f'  one club-season: noise sd of g_hat {np.sqrt(T.vg.median()):.3f}, of m_hat {np.sqrt(T.vm.median()):.3f}, of priced h {np.sqrt(T.vhh.median()):.3f}. League home advantage for scale: {b*d.H_post.mean():.3f}')
    print(f'  raw spread across club-seasons: g {T.g.std():.3f}, m {T.m.std():.3f}, priced h {T.h.std():.3f}')
    T = T.sort_values(['team', 'season']); rng = np.random.default_rng(4); out = {}
    def lagcov(T, col, L):
        A = T[['team', 'season', col]].rename(columns={col: 'v0'}); B = T[['team', 'season', col]].rename(columns={col: 'v1'}); B['season'] -= L
        J = A.merge(B, on=['team', 'season']); return (J.v0 * J.v1).mean(), len(J), J
    clubs = T.team.unique()
    for col, lab in [('g', 'home-advantage mispricing g'), ('m', 'overall mispricing m'), ('h', 'priced club home advantage h')]:
        line = []
        for L in [1, 2, 3]:
            c, n, J = lagcov(T, col, L); bs = []
            for _ in range(400):
                pick = rng.choice(clubs, len(clubs)); w = pd.Series(pick).value_counts(); jj = J[J.team.isin(w.index)]; ww = jj.team.map(w).values; bs.append(np.average(jj.v0 * jj.v1, weights=ww))
            line.append(f'lag {L}: cov {c:+.5f} (se {np.std(bs):.5f}, n {n})'); out[(col, L)] = (c, np.std(bs))
        cs = [out[(col, L)] for L in [1, 2, 3]]; w = np.array([1 / s ** 2 for _, s in cs]); v = (w * np.array([c for c, _ in cs])).sum() / w.sum(); se = 1 / np.sqrt(w.sum())
        print(f'  {lab:32s} ' + ' | '.join(line)); print(f'  {"":32s} persistent variance (lags 1-3 pooled) {v:+.5f} (se {se:.5f}) -> sd {np.sqrt(max(v,0)):.3f}, 95% upper bound sd {np.sqrt(max(v+1.96*se,0)):.3f}')
        out[col] = (v, se)
    c, n, J = lagcov(T.assign(gh=T.g, hh=T.h), 'g', 0)
    J2 = T[['team', 'season', 'g', 'h']].merge(T[['team', 'season', 'g', 'h']].assign(season=T.season - 1), on=['team', 'season'], suffixes=('', '_n'))
    print(f'  does priced h track true g? cov(h this season, g next season) {(J2.h * J2.g_n).mean():+.5f} | cov(g this season, h next season) {(J2.g * J2.h_n).mean():+.5f} (n {len(J2)})')
    # implied club home advantage, true = priced + mispriced, as a share of league home advantage
    HA = b * d[d.Date < '2020-03-01'].H_post.mean(); vg, vh = max(out['g'][0], 0), max(out['h'][0], 0)
    print(f'\n  SUMMARY in share of a typical league home advantage ({HA:.3f}): priced club spread sd {np.sqrt(vh)/HA:.0%} | mispriced club spread sd {np.sqrt(vg)/HA:.0%} (upper 95% {np.sqrt(max(out["g"][0]+1.96*out["g"][1],0))/HA:.0%})')
    pd.to_pickle({'Vg': out['g'], 'Vm': out['m'], 'Vh': out['h']}, 'work/club_var.pkl')
if which == 'hold':
    T = pd.read_pickle('work/club_expl.pkl'); V = pd.read_pickle('work/club_var.pkl'); Vg = max(V['Vg'][0], 0); Vm = max(V['Vm'][0], 0)
    S = T.groupby('team').agg(k=('g', 'size'), g=('g', 'mean'), m=('m', 'mean'), vg=('vg', 'mean'), vm=('vm', 'mean'))
    S['wg'] = Vg / (Vg + S.vg / S.k); S['wm'] = Vm / (Vm + S.vm / S.k); S['gs'] = S.wg * S.g; S['ms'] = S.wm * S.m
    print(f'shrinkage: median weight on a club\'s own record, g {S.wg.median():.2f}, m {S.wm.median():.2f} | sd of shrunk effects g {S.gs.std():.3f}, m {S.ms.std():.3f}')
    h = d[(d.Date >= '2021-08-01') & (d.Date <= '2026-01-08') & d.PSCH.notna()].copy()
    gs = S.gs.to_dict(); ms = S.ms.to_dict()
    h['zp_g'] = (h.HomeTeam.map(gs).fillna(0) + h.AwayTeam.map(gs).fillna(0)) / 2; h['zp_m'] = h.HomeTeam.map(ms).fillna(0) - h.AwayTeam.map(ms).fillna(0)
    h['clu'] = h.league + h.Date.dt.to_period('M').astype(str); h['zc'] = h.z - (h.z * h['info']).groupby(h.ls).transform('sum') / h['info'].groupby(h.ls).transform('sum')
    print(f'HOLD-OUT: {len(h)} crowd matches, {h.HomeTeam.isin(gs).mean():.0%} with the home club seen in exploration')
    def slope(col):
        w = h['info'].values; v = h[col].values - np.average(h[col], weights=w); z = h.zc.values; th = (w * v * z).sum() / (w * v * v).sum(); r = z - th * v
        G = pd.DataFrame({'c': h.clu.values, 's': w * v * r}).groupby('c').s.sum(); se = np.sqrt((G ** 2).sum()) / (w * v * v).sum()
        from scipy.stats import norm as N; return th, se, 1 - N.cdf(th / se)
    th, se, p = slope('zp_g'); print(f'  PRIMARY: slope of hold-out residual on predicted club home-advantage mispricing {th:+.2f} (se {se:.2f}), one-sided p = {p:.3f}  [1 = effects fully real, 0 = none]')
    th2, se2, p2 = slope('zp_m'); print(f'  secondary: slope on predicted overall club mispricing {th2:+.2f} (se {se2:.2f}), one-sided p = {p2:.3f}')
    if p < 0.05:
        q1, q9 = h.zp_g.quantile([0.1, 0.9]); hb = h[h.zp_g >= q9]; ab = h[h.zp_g <= q1]
        r = np.r_[np.where(hb.hw == 1, hb.PSCH - 1, -1.0), np.where(ab.aw == 1, ab.PSCA - 1, -1.0)]; rng = np.random.default_rng(9); bs = [rng.choice(r, len(r)).mean() for _ in range(3000)]
        print(f'  RULE: {len(r)} bets, return at Pinnacle close {r.mean()*100:+.1f}% [{np.percentile(bs,2.5)*100:+.1f}, {np.percentile(bs,97.5)*100:+.1f}]')
    else: print('  primary fails, so the betting rule is not run (as planned)')
