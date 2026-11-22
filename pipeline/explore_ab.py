"""Exploratory: crowd dose (A) and away-support proxies (B) against Pinnacle's closing price.
Usage: python explore_ab.py expl | hold.  Rules for the hold-out are fixed from the exploration run only."""
import sys, pandas as pd, numpy as np
from reflib import *
from features import add
which = sys.argv[1]
m = add(pd.read_pickle('work/master.pkl'))
base = (m.crowd == 'full') & m.pc_h.notna() & m.po_h.notna()
d = m[base & (m.season >= 2012) & (m.Date <= EXPL_END)] if which == 'expl' else m[base & (m.season >= HOLD_START_SEASON) & (m.Date <= PIN_END)]
d = d.copy()
print(f'{which}: n={len(d)}  mean S {d.S_pc.mean():+.4f}')
def test(col, label, data=d, controls=('gap',)):
    x = data.dropna(subset=[col, 'S_pc'] + list(controls))
    v = x[col].values.astype(float)
    if len(np.unique(v)) > 2: v = (v - v.mean()) / v.std()
    X = np.column_stack([np.ones(len(x)), v] + [x[c].values for c in controls])
    b, se = ols(x.S_pc.values, X)
    bo, seo = ols(x.S_po.values, X)
    print(f'  {label:52s} n={len(x):5d} close {b[1]:+.4f} (se {se[1]:.4f}, t {b[1]/se[1]:+.2f}) | open {bo[1]:+.4f} (t {bo[1]/seo[1]:+.2f})')
print('A. crowd dose (z-scored unless a 0/1 flag), controlling for the price gap')
test('latt', 'log attendance')
for lg in ['E0', 'E1']: test('latt', f'log attendance, {lg} only', d[d.league == lg])
test('occ', 'occupancy (gate / season max gate)')
for lg in ['E0', 'E1']: test('occ', f'occupancy, {lg} only', d[d.league == lg])
test('rel_att', 'gate relative to club season mean')
test('rel_run', 'gate relative to club mean so far this season')
for lg in ['E0', 'E1']: test('rel_run', f'gate relative to mean so far, {lg} only', d[d.league == lg])
print('B. away-support proxies')
test('ldist', 'log travel distance')
test('derby', 'derby (< 40 km)')
test('far', 'long trip (> 250 km)')
test('midweek', 'midweek (Tue-Thu)')
test('far_midweek', 'long trip AND midweek')
for lg in ['E0', 'E1']: test('ldist', f'log travel distance, {lg} only', d[d.league == lg])
