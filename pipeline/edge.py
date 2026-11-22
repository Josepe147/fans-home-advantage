"""Edge tests H1-H3 for the referee x crowd plan. Usage: python edge.py expl | hold"""
import sys, pandas as pd, numpy as np
from reflib import *
which = sys.argv[1]
rng = np.random.default_rng(7)
m = pd.read_pickle('work/mech.pkl')
expl_mask = (m.crowd == 'full') & (m.Date <= EXPL_END)
k, _, _ = shrink_k(m, 'S_r', expl_mask)
m['S_r_bias'], m['S_r_n'] = lagged_bias(m, 'S_r', k)
if which == 'expl':
    d = m[(m.season >= 2012) & expl_mask].copy()
else:
    d = m[(m.season >= HOLD_START_SEASON) & (m.crowd == 'full') & (m.Date <= PIN_END)].copy()
d = d.dropna(subset=['pc_h', 'po_h'])
print(f'sample={which} matches={len(d)} (EPL {(d.league=="E0").sum()}, Championship {(d.league=="E1").sum()}) | share with known referee history {(d.yd_r_n>=30).mean():.2f}')
print(f'mean S vs close {d.S_pc.mean():+.4f} (se {d.S_pc.std()/np.sqrt(len(d)):.4f}) | home win {d.hw.mean():.3f} vs priced {d.pc_h.mean():.3f}')
def z(s): return (s - s.mean()) / s.std()
for name, col in [('PRIMARY yellow-card bias', 'yd_r_bias'), ('secondary A foul bias', 'fdiff_r_bias'), ('secondary B result bias', 'S_r_bias')]:
    d['z'] = z(d[col])
    X = np.column_stack([np.ones(len(d)), d.z.values])
    for lab, y in [('H1 close', d.S_pc), ('H1 open ', d.S_po), ('H2 move ', (d.pc_h - d.pc_a) - (d.po_h - d.po_a))]:
        b, se = ols(y.values, X, cluster=d.ref.values); _, se2 = ols(y.values, X)
        s = max(se[1], se2[1])   # report the more conservative of cluster-robust and heteroskedasticity-robust
        print(f'  {name:26s} {lab}: slope per z = {b[1]:+.4f} (se {s:.4f}) t = {b[1]/s:+.2f}')
    # H3: interaction with attendance (z within league), where attendance is known
    a = d.dropna(subset=['att']).copy()
    if len(a) > 500:
        a['az'] = a.groupby('league').att.transform(lambda s: (np.log(s) - np.log(s).mean()) / np.log(s).std())
        X3 = np.column_stack([np.ones(len(a)), a.z.values, a.az.values, a.z.values * a.az.values])
        b, se = ols(a.S_pc.values, X3, cluster=a.ref.values); _, se2 = ols(a.S_pc.values, X3); se = np.maximum(se, se2)
        print(f'  {name:26s} H3 (n={len(a)}): bias {b[1]:+.4f} ({se[1]:.4f}) | crowd {b[2]:+.4f} ({se[2]:.4f}) | bias x crowd {b[3]:+.4f} ({se[3]:.4f}) t = {b[3]/se[3]:+.2f}')
# betting rule
d['z'] = z(d['yd_r_bias'])
def roi(sel, side, odds_h, odds_a):
    x = d[sel]
    ret = np.where(side == 'h', x.hw * x[odds_h] - 1, x.aw * x[odds_a] - 1)
    if len(ret) == 0: return np.array([])
    return ret
for lab, oh, oa in [('closing', 'PSCH', 'PSCA'), ('opening', 'PSH', 'PSA')]:
    r = np.concatenate([roi(d.z >= 1, 'h', oh, oa), roi(d.z <= -1, 'a', oh, oa)])
    boot = [rng.choice(r, len(r)).mean() for _ in range(5000)] if len(r) else [np.nan]
    print(f'betting rule at {lab} odds: bets={len(r)} (home {int((d.z>=1).sum())}, away {int((d.z<=-1).sum())}) return {100*r.mean():+.2f}% | bootstrap 95% [{100*np.percentile(boot,2.5):+.1f}%, {100*np.percentile(boot,97.5):+.1f}%]')
# benchmark: back every home / every away at closing
print(f'benchmarks at closing odds: all home {100*((d.hw*d.PSCH).mean()-1):+.2f}% | all away {100*((d.aw*d.PSCA).mean()-1):+.2f}%')
