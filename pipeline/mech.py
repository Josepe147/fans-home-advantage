"""Mechanism: is referee home bias in cards real, persistent, and crowd-dependent? (H4)"""
import pandas as pd, numpy as np
from reflib import *
rng = np.random.default_rng(1)
m = load()
m = m[m.season >= 2002].copy()
m['ysh'] = m.AY / (m.AY + m.HY)            # away share of yellows (robustness, added after the plan)
m['fsh'] = m.AF / (m.AF + m.HF)            # away share of fouls (robustness, added after the plan)
m['ytot'] = m.AY + m.HY
for col in ['yd', 'fdiff', 'ysh', 'fsh', 'ytot']:
    m[col + '_r'] = residualise(m, col)
m['S_r'] = m.S_mk
expl = (m.crowd == 'full') & (m.Date <= EXPL_END)
print('matches with referee and odds:', m.gap.notna().sum(), '| exploration crowd games:', expl.sum())
print('mean away-minus-home yellows: crowd %.3f | ghost %.3f | partial %.3f' % tuple(m[m.crowd == c].yd.mean() for c in ['full', 'ghost', 'partial']))
print('mean away-minus-home fouls:   crowd %.3f | ghost %.3f' % tuple(m[m.crowd == c].fdiff.mean() for c in ['full', 'ghost']))

# 1. heterogeneity: permutation test (shuffle referees within league-season)
def stat(d, col, refs):
    g = pd.DataFrame({'r': refs, 'v': d[col].values}).groupby('r').v.agg(['mean', 'count'])
    return float((g['count'] * g['mean'] ** 2).sum())
for col in ['yd_r', 'fdiff_r', 'ysh_r', 'fsh_r', 'ytot_r', 'S_r']:
    d = m[expl].dropna(subset=[col])
    obs = stat(d, col, d.ref.values)
    keys = (d.league + d.season.astype(str)).values
    idx_by = {k: np.where(keys == k)[0] for k in np.unique(keys)}
    sims = []
    refs = d.ref.values.copy()
    for _ in range(2000):
        pr = refs.copy()
        for k, ix in idx_by.items(): pr[ix] = rng.permutation(refs[ix])
        sims.append(stat(d, col, pr))
    sims = np.array(sims)
    k, sw, tau2 = shrink_k(m, col, expl)
    print(f'{col:8s} heterogeneity: obs/perm-mean = {obs/sims.mean():.3f}, permutation p = {(sims >= obs).mean():.4f} | between-referee SD = {np.sqrt(tau2):.4f} (match SD {np.sqrt(sw):.3f}), k = {k:.0f}')

# 2. persistence and 3. ghost placebo, using lagged bias only
res = {}
for col in ['yd_r', 'fdiff_r', 'ysh_r', 'fsh_r', 'ytot_r']:
    k, _, _ = shrink_k(m, col, expl)
    m[col + '_bias'], m[col + '_n'] = lagged_bias(m, col, k)
    for lab, mask in {'exploration crowd 2012-Mar 2020': (m.season >= 2012) & expl,
                      'ghost games 2020-21': (m.crowd == 'ghost'),
                      'hold-out crowd 2021/22+': (m.season >= 2021) & (m.crowd == 'full')}.items():
        d = m[mask & (m[col + '_n'] >= 30)].dropna(subset=[col])
        X = np.column_stack([np.ones(len(d)), d[col + '_bias'].values])
        b, se = ols(d[col].values, X, cluster=d.ref.values)
        print(f'{col:8s} on own lagged bias | {lab:32s} n={len(d):5d} refs={d.ref.nunique():3d} slope={b[1]:+.2f} (se {se[1]:.2f}) t={b[1]/se[1]:+.1f}')
m.to_pickle('work/mech.pkl')
