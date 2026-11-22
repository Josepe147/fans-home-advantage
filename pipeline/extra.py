"""Follow-up checks: (1) look-ahead leak in the attendance measure, (2) dose tests with clean measures,
(3) raw first-half/second-half split and half-time state, (4) crowd dose by half-time state."""
import pandas as pd, numpy as np
from reflib import ols, EXPL_END
m = pd.read_pickle('work/feat2.pkl')
ex = (m.crowd == 'full') & m.pc_h.notna() & m.po_h.notna() & (m.season >= 2012) & (m.Date <= EXPL_END)
d = m[ex].sort_values('Date').copy()
def reg(x, cols, y='S_pc'):
    x = x.dropna(subset=cols + [y, 'gap']); z = lambda v: (v - v.mean()) / v.std() if len(np.unique(v)) > 2 else v
    X = np.column_stack([np.ones(len(x))] + [z(x[c].values.astype(float)) for c in cols] + [x.gap.values]); b, se = ols(x[y].values, X)
    return f'n={len(x)} ' + ' | '.join(f'{c} {b[i+1]:+.4f} (se {se[i+1]:.4f}, t {b[i+1]/se[i+1]:+.2f})' for i, c in enumerate(cols))
print('1. LOOK-AHEAD CHECK (exploration set, residual v Pinnacle close)')
grp = d.groupby(['HomeTeam', 'season']).att; cs = grp.cumsum(); n = grp.cumcount() + 1; tot = grp.transform('sum'); N = grp.transform('size')
d['back'] = (d.att / ((cs - d.att) / (n - 1)).where(n > 3)).clip(0.8, 1.2); d['fwd'] = (d.att / ((tot - cs) / (N - n)).where((N - n) >= 3)).clip(0.8, 1.2)
print('  gate v season mean (uses later gates):', reg(d, ['relz']))
print('  gate v EARLIER home gates only:       ', reg(d, ['back']))
print('  gate v LATER home gates only:         ', reg(d, ['fwd']))
d['chg'] = np.log(d.groupby(['HomeTeam', 'season']).att.shift(-1) / d.att)
print('  change in next home gate after loss/draw/win:', d.groupby(np.sign(d.gd)).chg.mean().round(4).to_dict())
print('2. CLEAN DOSE TESTS'); print('  predicted uplift:', reg(d, ['pred_up'])); print('  components:', reg(d, ['lfan', 'ldist', 'midweek', 'derby']))
print('3. HALVES, raw, six leagues 2017/18 to 2022/23')
h = pd.read_pickle('work/halves.pkl'); w = h[h.season.between(2017, 2022)]
def did(y, data, label):
    lg = pd.get_dummies(data.league, drop_first=True).values.astype(float)
    b, se = ols(data[y].values, np.column_stack([np.ones(len(data)), data.nocrowd.values, lg]), cluster=(data.league + data.season.astype(str) + data.HomeTeam).values)
    print(f'  {label:34s} crowd mean {data[data.nocrowd==0][y].mean():+.3f} | no-crowd change {b[1]:+.3f} (se {se[1]:.3f}, t {b[1]/se[1]:+.1f})')
for scope, data in [('six leagues', w), ('England', w[w.league.isin(['E0', 'E1'])]), ('other four', w[~w.league.isin(['E0', 'E1'])])]:
    print(' ', scope, len(data), int(data.nocrowd.sum())); did('gd', data, 'full match'); did('gd1', data, 'first half'); did('gd2', data, 'second half')
for st, name in [(1, 'home leading at HT'), (0, 'level at HT'), (-1, 'home trailing at HT')]:
    x = w[w.state == st].assign(hwin=lambda q: (q.gd > 0).astype(float), awin=lambda q: (q.gd < 0).astype(float)); print(' ', name, len(x), int(x.nocrowd.sum()))
    did('gd2', x, 'second-half supremacy'); did('hwin', x, 'P(home wins)'); did('awin', x, 'P(away wins)')
print('4. CROWD DOSE BY HALF-TIME STATE, England crowd games 2012/13 on')
e = m.merge(h[['league', 'Date', 'HomeTeam', 'gd1', 'gd2', 'state']], on=['league', 'Date', 'HomeTeam']); e = e[(e.crowd == 'full') & (e.season >= 2012) & e.pc_h.notna()].copy()
e['latt_z'] = e.groupby('league').latt.transform(lambda s: (s - s.mean()) / s.std())
for col in ['latt_z', 'runz']:
    for st, name in [(1, 'leading'), (0, 'level'), (-1, 'trailing')]:
        x = e[e.state == st].dropna(subset=[col]); b, se = ols(x.gd2.values, np.column_stack([np.ones(len(x)), x[col], x.gap]), cluster=(x.HomeTeam + x.season.astype(str)).values)
        print(f'  {col:7s} home {name:9s} n={len(x):5d} second-half supremacy per SD {b[1]:+.4f} (se {se[1]:.4f}, t {b[1]/se[1]:+.2f})')
