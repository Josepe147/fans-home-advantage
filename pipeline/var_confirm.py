"""VAR confirmation, run once (see PLAN_var.md). Dates fixed here before any confirmation result was computed:
treated (top flight, start of season, cross-checked): Eredivisie 2018/19 (KNVB), Swiss Super League 2019/20 (SFL),
Danish Superliga 2020/21 (European Leagues release), J1 League 2021 (J.League), Eliteserien 2023 (NFF, several reports).
Never adopted (controls): EFL Championship, League One, League Two, Allsvenskan.
Excluded: Scottish Premiership (VAR from 21 Oct 2022, mid-season) and every league whose start could not be cross-checked."""
import pandas as pd, numpy as np
from scipy.stats import norm, t as tdist
from scipy.optimize import minimize
CONF = {'N1': 2018, 'SUI': 2019, 'DNK': 2020, 'JPN': 2021, 'NOR': 2023}
NEVER = ['E1', 'E2', 'E3', 'SWE']
A = pd.read_pickle('work/kf.pkl'); X = pd.read_pickle('work/kf_extra.pkl')
d = pd.concat([A, X], ignore_index=True); d = d[(d.regime == 'full') & d.league.isin(list(CONF) + NEVER) & (d.season.between(2012, 2025)) & (d.season != 2020) & ~((d.season == 2019) & (d.Date >= '2020-03-01'))].copy()
def ll(eta, c, y):
    ph = norm.cdf(eta - c); pa = norm.cdf(-eta - c); pdw = np.clip(1 - ph - pa, 1e-12, None)
    return np.where(y == 1, np.log(np.clip(ph, 1e-12, None)), np.where(y == -1, np.log(np.clip(pa, 1e-12, None)), np.log(pdw)))
pre = d[d.Date < '2020-03-01']; a, b = minimize(lambda p: -ll(p[0] + p[1] * pre.mu.values, pre.c.values, pre.y.values).sum(), [0, 1], method='Nelder-Mead').x
e = a + b * d.mu; ph = norm.cdf(e - d.c); pa = norm.cdf(-e - d.c); f1 = norm.pdf(e - d.c); f2 = norm.pdf(e + d.c)
d['info'] = f1 ** 2 / ph + f2 ** 2 / pa + (f2 - f1) ** 2 / (1 - ph - pa); d['z'] = np.where(d.y == 1, f1 / ph, np.where(d.y == -1, -f2 / pa, (f2 - f1) / (1 - ph - pa))) / d['info']; d['wl'] = d.hw - d.aw
P = d.groupby(['league', 'season']).apply(lambda x: pd.Series({'H': b * x.H_post.mean(), 'z': np.average(x.z, weights=x['info']), 'wl': x.wl.mean(), 'n': len(x)})).reset_index()
print(f'calibration a={a:.4f} b={b:.4f} | league-seasons {len(P)}'); print(P.pivot(index='league', columns='season', values='n').fillna(0).astype(int).to_string())
rows = []
for l, s0 in CONF.items():
    bef = [s for s in range(s0 - 4, s0) if s != 2020][-3:]; aft = [s for s in range(s0, s0 + 4) if s != 2020][:3]
    ctrl = [k for k in P.league.unique() if k != l and (k in NEVER or CONF.get(k, 9999) > max(aft))]
    def chg(lg, col):
        x = P[P.league.isin(lg)]; return x[x.season.isin(aft)][col].mean() - x[x.season.isin(bef)][col].mean()
    rows.append([l, s0, str(bef), str(aft), chg([l], 'z') - chg(ctrl, 'z'), chg([l], 'z'), chg([l], 'H') - chg(ctrl, 'H'), chg([l], 'wl') - chg(ctrl, 'wl'), ','.join(ctrl)])
S = pd.DataFrame(rows, columns=['league', 'from', 'before', 'after', 'did_z', 'raw_z', 'did_H', 'did_wl', 'controls'])
print('\nCONFIRMATION, per league:'); print(S.round(4).to_string(index=False))
def summ(col, lab):
    v = S[col].values; m = v.mean(); se = v.std(ddof=1) / np.sqrt(len(v)); p = tdist.cdf(m / se, len(v) - 1); print(f'  {lab:55s} {m:+.4f} (se {se:.4f}, t {m/se:+.2f}, one-sided p {p:.3f})')
summ('did_z', 'PRIMARY: results against price, minus controls'); summ('raw_z', 'secondary: results against price, no control group'); summ('did_H', 'secondary: priced home advantage, minus controls'); summ('did_wl', 'secondary: win-minus-loss share, minus controls (no price model)')
