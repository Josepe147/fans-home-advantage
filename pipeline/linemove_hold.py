"""Line movement and travel distance: exploration v hold-out, plus the fixed betting rule. Usage: python linemove_hold.py expl|hold"""
import sys, pandas as pd, numpy as np
from reflib import ols, EXPL_END, HOLD_START_SEASON, PIN_END
which = sys.argv[1]
m = pd.read_pickle('work/feat2.pkl'); m['gap_o'] = m.po_h - m.po_a; m['M'] = (m.pc_h - m.pc_a) - m.gap_o
ok = m.pc_h.notna() & m.po_h.notna() & (m.crowd == 'full')
ex = m[ok & (m.season >= 2012) & (m.Date <= EXPL_END)]; mu, sd = ex.ldist.mean(), ex.ldist.std()
d = (ex if which == 'expl' else m[ok & (m.season >= HOLD_START_SEASON) & (m.Date <= PIN_END)]).copy(); d['lz'] = (d.ldist - mu) / sd
print(f'{which}: n={len(d)}')
b, se = ols(d.M.values, np.column_stack([np.ones(len(d)), d.lz, d.gap_o]), cluster=(d.HomeTeam + d.AwayTeam).values)
print(f'H-L1 slope of move on z(log distance): {b[1]:+.5f} (se {se[1]:.5f}, t {b[1]/se[1]:+.1f})')
for lg in ['E0', 'E1']:
    x = d[d.league == lg]; b, se = ols(x.M.values, np.column_stack([np.ones(len(x)), x.lz, x.gap_o]), cluster=(x.HomeTeam + x.AwayTeam).values); print(f'   {lg}: {b[1]:+.5f} (t {b[1]/se[1]:+.1f}) n={len(x)}')
d['band'] = pd.cut(d.dist, [0, 60, 200, 600], labels=['local <60km', 'middle', 'far >200km'])
print(d.groupby('band').agg(n=('M', 'size'), move=('M', 'mean'), se=('M', lambda s: s.std() / np.sqrt(len(s))), S_open=('S_po', 'mean'), S_close=('S_pc', 'mean'), seS=('S_pc', lambda s: s.std() / np.sqrt(len(s)))).round(4).to_string())
rng = np.random.default_rng(3)
def boot(r): bs = [rng.choice(r, len(r)).mean() for _ in range(4000)]; return f'{r.mean()*100:+.2f}% [{np.percentile(bs,2.5)*100:+.2f}, {np.percentile(bs,97.5)*100:+.2f}]'
loc, far = d[d.dist < 60], d[d.dist > 200]
side_p_open = np.r_[loc.po_a.values, far.po_h.values]; side_p_close = np.r_[loc.pc_a.values, far.pc_h.values]
o_open = np.r_[loc.PSA.values, far.PSH.values].astype(float); o_close = np.r_[loc.PSCA.values, far.PSCH.values].astype(float); win = np.r_[loc.aw.values, far.hw.values]
print(f'H-L2 rule: {len(win)} bets ({len(loc)} away in local games, {len(far)} home on long trips)')
print('  closing-line value, probability points:', boot(side_p_close - side_p_open))
print('  price beaten (early odds / closing odds - 1):', boot(o_open / o_close - 1), '| share of bets that beat the close:', round(float((o_open > o_close).mean()), 3))
print('  return at early odds:', boot(np.where(win == 1, o_open - 1, -1.0)), '| same bets at closing odds:', boot(np.where(win == 1, o_close - 1, -1.0)))
print('  expected return at early odds if the close is the truth:', f'{(side_p_close * o_open - 1).mean()*100:+.2f}%')
opp_open = np.r_[loc.PSH.values, far.PSA.values].astype(float); oppwin = np.r_[loc.hw.values, far.aw.values]
print('  mirror rule (the other side) at early odds:', boot(np.where(oppwin == 1, opp_open - 1, -1.0)))
print('  information test on outcomes v early price, side backed (win - early prob):', boot(win - side_p_open), '| v close:', boot(win - side_p_close))
for lab, x, pc, po, oc, oo, w in [('away side in local games', loc, 'pc_a', 'po_a', 'PSCA', 'PSA', 'aw'), ('home side on long trips', far, 'pc_h', 'po_h', 'PSCH', 'PSH', 'hw')]:
    oo_, oc_ = x[oo].values.astype(float), x[oc].values.astype(float)
    print(f'  {lab}: n={len(x)} | price beaten', boot(oo_ / oc_ - 1), '| return early', boot(np.where(x[w] == 1, oo_ - 1, -1.0)), '| return close', boot(np.where(x[w] == 1, oc_ - 1, -1.0)), '| expected if close true', f'{(x[pc].values * oo_ - 1).mean()*100:+.2f}%')
