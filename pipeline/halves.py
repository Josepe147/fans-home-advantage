"""Where in the match did the crowd effect sit? First half vs second half, and by half-time game state.
Six leagues. 'No crowd' = exact ghost flags for England, Covid date window (May 2020 to June 2021) elsewhere."""
import pandas as pd, numpy as np, glob, os
from reflib import ols
mm = pd.read_pickle('work/master.pkl')[['league', 'Date', 'HomeTeam', 'crowd']]
rows = []
for f in sorted(glob.glob('fd/*_*.csv')):
    lg, code = os.path.basename(f)[:-9], os.path.basename(f)[-8:-4]
    y = int(code[:2]); sea = 2000 + y
    if sea < 2012: continue
    d = pd.read_csv(f, encoding='latin1', on_bad_lines='skip').dropna(subset=['FTHG', 'HTHG'])
    d['league'] = lg; d['season'] = sea; d['Date'] = pd.to_datetime(d.Date, dayfirst=True, format='mixed')
    for c in ['PSCH', 'PSCD', 'PSCA', 'B365H', 'B365D', 'B365A']:
        if c not in d: d[c] = np.nan
    rows.append(d[['league', 'season', 'Date', 'HomeTeam', 'AwayTeam', 'FTHG', 'FTAG', 'HTHG', 'HTAG', 'PSCH', 'PSCD', 'PSCA', 'B365H', 'B365D', 'B365A']])
d = pd.concat(rows, ignore_index=True)
for c in ['FTHG', 'FTAG', 'HTHG', 'HTAG']: d[c] = pd.to_numeric(d[c], errors='coerce')
def dv(cols):
    inv = 1 / d[cols].astype(float); p = inv.div(inv.sum(axis=1), axis=0); return p.iloc[:, 0] - p.iloc[:, 2]
d['gap'] = dv(['PSCH', 'PSCD', 'PSCA']).fillna(dv(['B365H', 'B365D', 'B365A']))
d = d.merge(mm, on=['league', 'Date', 'HomeTeam'], how='left')
eng = d.league.isin(['E0', 'E1'])
window = (d.Date >= '2020-05-01') & (d.Date <= '2021-06-30')
d['nocrowd'] = np.where(eng, (d.crowd == 'ghost'), window).astype(float)
d = d[~(eng & (d.crowd == 'partial'))].dropna(subset=['gap'])
d['gd1'] = d.HTHG - d.HTAG; d['gd2'] = (d.FTHG - d.FTAG) - d.gd1; d['gd'] = d.FTHG - d.FTAG
d['g1'] = d.HTHG + d.HTAG; d['g2'] = d.FTHG + d.FTAG - d.g1
d['state'] = np.sign(d.gd1)
print('matches', len(d), '| no-crowd', int(d.nocrowd.sum()), '| by league no-crowd:', d[d.nocrowd == 1].groupby('league').size().to_dict())
d.to_pickle('work/halves.pkl')
def did(y, data, label):
    lg = pd.get_dummies(data.league, drop_first=True).values.astype(float)
    X = np.column_stack([np.ones(len(data)), data.nocrowd.values, data.gap.values, lg])
    b, se = ols(data[y].values, X, cluster=(data.league + data.season.astype(str) + data.HomeTeam).values)
    print(f'  {label:44s} crowd mean {data[data.nocrowd==0][y].mean():+.3f} | no-crowd effect {b[1]:+.3f} (se {se[1]:.3f}, t {b[1]/se[1]:+.1f})')
    return b[1], se[1]
print('1. Home goal supremacy by half (no-crowd effect controls for price gap and league)')
for scope, data in [('all six leagues', d), ('England only', d[eng]), ('other four', d[~eng])]:
    print(scope, f'n={len(data)} no-crowd={int(data.nocrowd.sum())}')
    did('gd', data, 'full match'); did('gd1', data, 'first half'); did('gd2', data, 'second half')
print('2. Second-half home supremacy by half-time state')
for st, name in [(1, 'home leading at HT'), (0, 'level at HT'), (-1, 'home trailing at HT')]:
    x = d[d.state == st]
    print(name, f'n={len(x)} no-crowd={int(x.nocrowd.sum())}')
    did('gd2', x, '  second-half supremacy')
    x = x.assign(hwin=(x.gd > 0).astype(float), awin=(x.gd < 0).astype(float), hpts=np.select([x.gd > 0, x.gd == 0], [3, 1], 0))
    did('hwin', x, '  P(home wins)'); did('awin', x, '  P(away wins)')
print('3. Goals per half'); did('g1', d, 'first-half goals'); did('g2', d, 'second-half goals')
