"""Avenue 2: what moves Pinnacle's line between the early price and the close? Usage: python linemove.py expl|hold
M = (close home prob - close away prob) - (open home prob - open away prob). Positive = money came for the home side."""
import sys, pandas as pd, numpy as np
from reflib import ols, EXPL_END, HOLD_START_SEASON, PIN_END
which = sys.argv[1]
m = pd.read_pickle('work/feat2.pkl'); m['gap_o'] = m.po_h - m.po_a; m['M'] = (m.pc_h - m.pc_a) - m.gap_o
m['latt_z'] = m.groupby(['league']).latt.transform(lambda s: (s - s.mean()) / s.std())
ok = m.pc_h.notna() & m.po_h.notna()
d = m[ok & (m.crowd == 'full') & ((m.season >= 2012) & (m.Date <= EXPL_END) if which == 'expl' else (m.season >= HOLD_START_SEASON) & (m.Date <= PIN_END))].copy()
print(f'{which}: n={len(d)} | mean move {d.M.mean():+.5f} | SD of move {d.M.std():.4f} | SD of result residual {d.S_pc.std():.3f}')
def t(col, lab, data=d, y='M', ctrl=('gap_o',)):
    x = data.dropna(subset=[col, y] + list(ctrl)); v = x[col].values.astype(float)
    if len(np.unique(v)) > 2: v = (v - v.mean()) / v.std()
    b, se = ols(x[y].values, np.column_stack([np.ones(len(x)), v] + [x[c].values for c in ctrl]), cluster=(x.HomeTeam + x.season.astype(str)).values)
    print(f'  {lab:50s} n={len(x):5d} {b[1]:+.5f} (se {se[1]:.5f}, t {b[1]/se[1]:+.2f})')
print('Line movement on each factor (per SD, or per flag), controlling for the opening gap:')
for col, lab in [('latt_z', 'log attendance'), ('runz', 'gate uplift v club mean so far'), ('relz', 'gate uplift v season mean (leaky, for reference)'), ('pred_up', 'predicted uplift'), ('lfan', 'away club fan base'), ('ldist', 'log travel distance'), ('derby', 'derby'), ('far', 'long trip'), ('midweek', 'midweek'), ('far_midweek', 'long trip and midweek')]:
    t(col, lab)
print('Does the move itself carry information the close has not finished absorbing?')
t('M', 'result residual v close on the move', y='S_pc', ctrl=('gap',))
t('M', 'result residual v open on the move', y='S_po', ctrl=('gap_o',))
if which == 'expl':
    g = m[ok & (m.crowd == 'ghost')]; print(f'ghost games: n={len(g)} mean move {g.M.mean():+.5f} (se {g.M.std()/np.sqrt(len(g)):.5f}) | by season:', g.groupby('season').M.mean().round(4).to_dict())
    c = m[ok & (m.crowd == 'full') & (m.season >= 2012)]; print('crowd games mean move by season:', c.groupby('season').M.mean().round(4).to_dict())
