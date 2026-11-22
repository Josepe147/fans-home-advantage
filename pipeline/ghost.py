"""Ghost-period deep dive (descriptive, one-off event so no hold-out possible)."""
import pandas as pd, numpy as np
from reflib import *
rng = np.random.default_rng(11)
m = pd.read_pickle('work/master.pkl')
m['S_pc'] = (m.hw - m.aw) - (m.pc_h - m.pc_a); m['S_po'] = (m.hw - m.aw) - (m.po_h - m.po_a)
m = m.dropna(subset=['pc_h', 'po_h']).copy()
pre = m[(m.crowd == 'full') & (m.season.between(2017, 2019)) & m.att.notna()]
usual = pre.groupby('HomeTeam').att.agg(usual_att='mean', cap='max'); usual['occ'] = usual.usual_att / usual.cap
m = m.join(usual, on='HomeTeam')
g = m[m.crowd == 'ghost'].copy()
g['phase'] = np.select([g.season == 2019, g.Date < '2020-12-01', g.Date < '2021-03-01'], ['1 restart Jun-Jul 2020', '2 Sep-Nov 2020', '3 Dec 2020-Feb 2021'], '4 Mar-May 2021')
def line(x):
    n = len(x); ba = x.aw * x.PSCA - 1; boa = x.aw * x.PSA - 1
    return pd.Series({'n': n, 'home win': x.hw.mean(), 'priced open': x.po_h.mean(), 'priced close': x.pc_h.mean(), 'away win': x.aw.mean(), 'priced away close': x.pc_a.mean(),
                      'S close': x.S_pc.mean(), 'se': x.S_pc.std() / np.sqrt(n), 'back away close %': 100 * ba.mean(), 'back away open %': 100 * boa.mean(), 'se %': 100 * ba.std() / np.sqrt(n)})
pd.set_option('display.width', 250)
print('pre-Covid crowd baseline 2017-Mar 2020:'); print(m[(m.crowd=='full')&m.season.between(2017,2019)].groupby('league').apply(line).round(3).to_string())
print('\nghost games by phase, both leagues:'); print(g.groupby('phase').apply(line).round(3).to_string())
print('\nghost games by league:'); print(g.groupby('league').apply(line).round(3).to_string())
print('\nall ghost games:'); print(line(g).round(3).to_string())
r = (g.aw * g.PSCA - 1).values; b = [rng.choice(r, len(r)).mean() for _ in range(5000)]
print('back every away team at Pinnacle close, all ghost games: %+.1f%% bootstrap 95%% [%+.1f%%, %+.1f%%], share of bootstrap > 0: %.3f' % (100*r.mean(), 100*np.percentile(b,2.5), 100*np.percentile(b,97.5), np.mean(np.array(b) > 0)))
# H5: bigger usual crowd -> bigger shortfall?
h = g.dropna(subset=['usual_att']).copy()
h['la'] = h.groupby('league').usual_att.transform(lambda s: (np.log(s) - np.log(s).mean()) / np.log(s).std())
h['la_all'] = (np.log(h.usual_att) - np.log(h.usual_att).mean()) / np.log(h.usual_att).std()
h['oc'] = (h.occ - h.occ.mean()) / h.occ.std()
for lab, cols in [('log usual crowd (z within league)', ['la']), ('log usual crowd (z across both leagues)', ['la_all']), ('usual occupancy', ['oc']), ('both', ['la_all', 'oc'])]:
    X = np.column_stack([np.ones(len(h))] + [h[c].values for c in cols])
    bb, se = ols(h.S_pc.values, X, cluster=h.HomeTeam.values); _, se2 = ols(h.S_pc.values, X); se = np.maximum(se, se2)
    print(f'H5 ghost S on {lab:42s} n={len(h)}: ' + ' | '.join(f'{c} {bb[i+1]:+.4f} (se {se[i+1]:.4f}, t {bb[i+1]/se[i+1]:+.2f})' for i, c in enumerate(cols)))
# same regression in pre-Covid crowd games as a placebo (should be ~0 if the market prices big clubs correctly)
p = m[(m.crowd == 'full') & m.season.between(2017, 2019)].dropna(subset=['usual_att']).copy()
p['la_all'] = (np.log(p.usual_att) - np.log(h.usual_att).mean()) / np.log(h.usual_att).std()
X = np.column_stack([np.ones(len(p)), p.la_all.values]); bb, se = ols(p.S_pc.values, X); print(f'placebo, crowd games 2017-Mar 2020 n={len(p)}: slope {bb[1]:+.4f} (se {se[1]:.4f})')
h['tercile'] = pd.qcut(h.usual_att, 3, labels=['small crowd', 'mid', 'big crowd'])
print(h.groupby('tercile').apply(line).round(3)[['n','home win','priced close','away win','priced away close','S close','se','back away close %','se %']].to_string())
print(h.groupby('tercile').usual_att.agg(['min','max']).round(0).to_string())
