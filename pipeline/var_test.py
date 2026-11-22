"""VAR as a natural experiment for the referee channel. VAR removes referee discretion on goals, penalties, straight reds
and mistaken identity, and leaves everything else alone. If part of home advantage runs through those decisions, home
advantage should fall when VAR arrives, relative to leagues that did not adopt it in the same seasons.
Dates confirmed from league and press sources (16-17 Nov). Leagues with unconfirmed dates are excluded."""
import pandas as pd, numpy as np
from scipy.stats import norm
from scipy.optimize import minimize
VAR = {'D1': 2017, 'I1': 2017, 'P1': 2017, 'SP1': 2018, 'F1': 2018, 'E0': 2019, 'D2': 2019}
NEVER = ['E1', 'E2', 'E3']
d = pd.read_pickle('work/kf.pkl'); d = d[(d.regime == 'full') & (d.season.between(2012, 2025)) & (d.season != 2020) & ~((d.season == 2019) & (d.Date >= '2020-03-01'))].copy()
d = d[d.league.isin(list(VAR) + NEVER)]
def ll(eta, c, y):
    ph = norm.cdf(eta - c); pa = norm.cdf(-eta - c); pdw = np.clip(1 - ph - pa, 1e-12, None)
    return np.where(y == 1, np.log(np.clip(ph, 1e-12, None)), np.where(y == -1, np.log(np.clip(pa, 1e-12, None)), np.log(pdw)))
pre = d[d.Date < '2020-03-01']; a, b = minimize(lambda p: -ll(p[0] + p[1] * pre.mu.values, pre.c.values, pre.y.values).sum(), [0, 1], method='Nelder-Mead').x
e = a + b * d.mu; ph = norm.cdf(e - d.c); pa = norm.cdf(-e - d.c); f1 = norm.pdf(e - d.c); f2 = norm.pdf(e + d.c)
d['info'] = f1 ** 2 / ph + f2 ** 2 / pa + (f2 - f1) ** 2 / (1 - ph - pa); d['z'] = np.where(d.y == 1, f1 / ph, np.where(d.y == -1, -f2 / pa, (f2 - f1) / (1 - ph - pa))) / d['info']
d['gd'] = d.hw - d.aw
P = d.groupby(['league', 'season']).apply(lambda x: pd.Series({'H': b * x.H_post.mean(), 'z': np.average(x.z, weights=x['info']), 'zse': 1 / np.sqrt(x['info'].sum()), 'n': len(x)})).reset_index()
P['treated'] = [int(l in VAR and s >= VAR[l]) for l, s in zip(P.league, P.season)]
print('priced home advantage (latent units) by league and season:'); print(P.pivot(index='league', columns='season', values='H').round(3).to_string())
# stacked comparison: each adopting league, 3 seasons before against 3 seasons after (skipping 2020), against leagues not treated in that window
rows = []
for l, s0 in VAR.items():
    bef = [s for s in range(s0 - 3, s0) if s != 2020]; aft = [s for s in range(s0, s0 + 4) if s != 2020][:3]
    ctrl = [k for k in P.league.unique() if k != l and (k in NEVER or VAR.get(k, 9999) > max(aft))]
    def chg(lg, col):
        x = P[P.league.isin(lg) if isinstance(lg, list) else (P.league == lg)]; return x[x.season.isin(aft)][col].mean() - x[x.season.isin(bef)][col].mean()
    rows.append([l, s0, chg(l, 'H'), chg(ctrl, 'H'), chg(l, 'z'), chg(ctrl, 'z'), ','.join(ctrl)])
S = pd.DataFrame(rows, columns=['league', 'from', 'dH_treated', 'dH_control', 'dz_treated', 'dz_control', 'controls']); S['did_H'] = S.dH_treated - S.dH_control; S['did_z'] = S.dz_treated - S.dz_control
print('\nSTACKED COMPARISON, 3 seasons before against 3 after (latent units; league home advantage is about 0.22):'); print(S.drop(columns='controls').round(4).to_string(index=False))
HA = P[P.season < 2017].H.mean()
for col, lab in [('did_H', 'priced home advantage (the market\'s view)'), ('did_z', 'results against the price (the market\'s error)')]:
    v = S[col].values; se = v.std(ddof=1) / np.sqrt(len(v)); print(f'  average change in {lab}: {v.mean():+.4f} (se across the 7 leagues {se:.4f}, t {v.mean()/se:+.2f}) = {v.mean()/HA:+.0%} of home advantage')
tot = S.did_H + S.did_z; print(f'  total (priced + error) = change in true home advantage: {tot.mean():+.4f} (se {tot.std(ddof=1)/np.sqrt(len(tot)):.4f}) = {tot.mean()/HA:+.0%} of home advantage')
# placebo: pretend VAR arrived 3 seasons earlier
rows = []
for l, s0 in VAR.items():
    s1 = s0 - 3; bef = [s for s in range(s1 - 3, s1) if s >= 2012]; aft = list(range(s1, s0))
    if len(bef) < 2: continue
    ctrl = [k for k in P.league.unique() if k != l and (k in NEVER or VAR.get(k, 9999) > max(aft))]
    x = P[P.league == l]; c = P[P.league.isin(ctrl)]
    rows.append((x[x.season.isin(aft)].H.mean() - x[x.season.isin(bef)].H.mean()) - (c[c.season.isin(aft)].H.mean() - c[c.season.isin(bef)].H.mean()))
print(f'  PLACEBO (VAR moved 3 seasons earlier, before it existed): {np.mean(rows):+.4f} (n {len(rows)} leagues, spread sd {np.std(rows,ddof=1):.4f})')
print('\nROBUSTNESS')
# (1) results-against-price placebo
rows = []
for l, s0 in VAR.items():
    s1 = s0 - 3; bef = [s for s in range(s1 - 3, s1) if s >= 2012]; aft = list(range(s1, s0))
    if len(bef) < 2: continue
    ctrl = [k for k in P.league.unique() if k != l and (k in NEVER or VAR.get(k, 9999) > max(aft))]; x = P[P.league == l]; c = P[P.league.isin(ctrl)]
    rows.append((x[x.season.isin(aft)].z.mean() - x[x.season.isin(bef)].z.mean()) - (c[c.season.isin(aft)].z.mean() - c[c.season.isin(bef)].z.mean()))
print(f'  (1) placebo on results against price, VAR moved 3 seasons earlier: {np.mean(rows):+.4f} (sd across leagues {np.std(rows,ddof=1):.4f}, n {len(rows)})')
# (2) event study: each treated league-season relative to adoption, minus the EFL mean that season
efl = P[P.league.isin(NEVER)].groupby('season')[['H', 'z']].mean()
T = P[P.league.isin(VAR)].copy(); T['k'] = T.season - T.league.map(VAR); T['k'] = np.where((T.season > 2020) & (T.season - T.league.map(VAR) > 0), T.k - 1, T.k)   # 2020 skipped
T['H_rel'] = T.H - T.season.map(efl.H); T['z_rel'] = T.z - T.season.map(efl.z); T['z_raw'] = T.z
print('  (2) event study, seasons relative to VAR (k = 0 is the first VAR season):')
print(T[T.k.between(-4, 3)].groupby('k').agg(leagues=('z', 'size'), priced_H_v_EFL=('H_rel', 'mean'), results_v_price_v_EFL=('z_rel', 'mean'), results_v_price_raw=('z_raw', 'mean')).round(4).to_string())
# (3) no control group: treated leagues' own before/after change in results against the price
v = []
for l, s0 in VAR.items():
    bef = [s for s in range(s0 - 3, s0) if s != 2020]; aft = [s for s in range(s0, s0 + 4) if s != 2020][:3]; x = P[P.league == l]; v.append(x[x.season.isin(aft)].z.mean() - x[x.season.isin(bef)].z.mean())
print(f'  (3) no control group, change in results against price: {np.mean(v):+.4f} (se {np.std(v,ddof=1)/np.sqrt(len(v)):.4f})')
# (4) 2017 cohort only (clean of Covid)
s = S[S['from'] == 2017]; print(f'  (4) 2017 cohort only (Germany, Italy, Portugal, no Covid seasons): priced {s.did_H.mean():+.4f}, results v price {s.did_z.mean():+.4f}')
# (5) results only, no price model: home goal difference per match in a balanced league season
G = d.groupby(['league', 'season']).gd.mean().rename('gdm').reset_index()
rows = []
for l, s0 in VAR.items():
    bef = [s for s in range(s0 - 3, s0) if s != 2020]; aft = [s for s in range(s0, s0 + 4) if s != 2020][:3]
    ctrl = [k for k in G.league.unique() if k != l and (k in NEVER or VAR.get(k, 9999) > max(aft))]; x = G[G.league == l]; c = G[G.league.isin(ctrl)]
    rows.append((x[x.season.isin(aft)].gdm.mean() - x[x.season.isin(bef)].gdm.mean()) - (c[c.season.isin(aft)].gdm.mean() - c[c.season.isin(bef)].gdm.mean()))
pre_gd = G[G.season < 2017].gdm.mean(); print(f'  (5) home goal difference per match, no price model: change {np.mean(rows):+.3f} goals (se {np.std(rows,ddof=1)/np.sqrt(len(rows)):.3f}) against a pre-2017 level of {pre_gd:.3f} = {np.mean(rows)/pre_gd:+.0%}')
