"""Does crowd size move referee decisions match by match? Away-minus-home yellows and fouls on crowd dose,
within club-season (home-team-season fixed effects), England, crowd games. Outcome test only, no prices."""
import pandas as pd, numpy as np
from reflib import ols, EXPL_END
m = pd.read_pickle('work/feat2.pkl'); m = m[(m.crowd == 'full') & (m.season >= 2012) & m.pc_h.notna() & m.HY.notna() & m.HF.notna()].copy()
m['yd'] = m.AY - m.HY; m['fd'] = m.AF - m.HF; m['ytot'] = m.AY + m.HY; m['hs'] = m.HomeTeam + m.season.astype(str)
m['lrel'] = np.log(m.att / m.seas_mean); m['lrun'] = np.log(m.rel_run.where(m.n_prior >= 3))
def within(x, cols):
    x = x.dropna(subset=cols).copy(); x[cols] = x[cols] - x.groupby('hs')[cols].transform('mean'); return x
def run(x, y, dose, lab):
    cols = [y, dose, 'gap', 'ldist', 'midweek']; x = within(x, cols); v = x[dose] / x[dose].std()
    b, se = ols(x[y].values, np.column_stack([np.ones(len(x)), v, x.gap, x.ldist, x.midweek]), cluster=x.hs.values)
    print(f'    {lab:34s} n={len(x):5d} per SD of dose {b[1]:+.4f} (se {se[1]:.4f}, t {b[1]/se[1]:+.2f})')
for name, x in [('ALL crowd games 2012/13 on', m), ('to March 2020', m[m.Date <= EXPL_END]), ('2021/22 on', m[m.season >= 2021]), ('Premier League', m[m.league == 'E0']), ('Championship', m[m.league == 'E1'])]:
    print(name)
    for y, yl in [('yd', 'yellows, away minus home'), ('fd', 'fouls, away minus home'), ('ytot', 'total yellows')]:
        run(x, y, 'lrun', yl + ' | gate v earlier gates'); 
    run(x, 'yd', 'lrel', 'yellows a-h | gate v season mean'); run(x, 'fd', 'lrel', 'fouls a-h | gate v season mean')
print('SD of within-club log gate uplift:', round(within(m, ['lrun']).lrun.std(), 3), '(about that many log points, so 1 SD is roughly a', round(100 * (np.exp(within(m, ['lrun']).lrun.std()) - 1)), '% bigger gate)')
