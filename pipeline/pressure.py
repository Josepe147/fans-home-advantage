"""Avenue 4: does a home crowd turn on a struggling side? Home slumps and relegation pressure against the closing price,
with ghost games as the placebo. Usage: python pressure.py"""
import pandas as pd, numpy as np
from reflib import ols, EXPL_END, HOLD_START_SEASON, PIN_END
m = pd.read_pickle('work/feat2.pkl').sort_values('Date').reset_index(drop=True)
m = m[(m.season >= 2012) & m.pc_h.notna()].copy()
m['u_home'] = m.S_pc; m['u_away'] = -m.S_pc
m['pts_h'] = np.select([m.hw == 1, m.aw == 1], [3, 0], 1); m['pts_a'] = np.select([m.aw == 1, m.hw == 1], [3, 0], 1)
# surprise v the market in the side's last 3 home games (home side) and last 3 away games (away side), same season
m['h_slump'] = m.groupby(['HomeTeam', 'season']).u_home.transform(lambda s: s.shift(1).rolling(3).mean())
m['a_slump'] = m.groupby(['AwayTeam', 'season']).u_away.transform(lambda s: s.shift(1).rolling(3).mean())
m['h_lost3'] = m.groupby(['HomeTeam', 'season']).hw.transform(lambda s: (s.shift(1).rolling(3).sum() == 0)).astype(float) * m.groupby(['HomeTeam', 'season']).aw.transform(lambda s: (s.shift(1).rolling(2).sum() == 2)).astype(float)
# league table before each match
long = pd.concat([m[['league', 'season', 'Date', 'HomeTeam', 'pts_h']].rename(columns={'HomeTeam': 'team', 'pts_h': 'pts'}), m[['league', 'season', 'Date', 'AwayTeam', 'pts_a']].rename(columns={'AwayTeam': 'team', 'pts_a': 'pts'})]).sort_values('Date')
long['cum'] = long.groupby(['league', 'season', 'team']).pts.transform(lambda s: s.shift(1).fillna(0).cumsum()); long['played'] = long.groupby(['league', 'season', 'team']).cumcount()
long['ppg'] = long.cum / long.played.clip(lower=1)
tab = long.set_index(['league', 'season', 'Date', 'team'])
m = m.join(tab[['ppg', 'played']].rename(columns={'ppg': 'h_ppg', 'played': 'h_played'}), on=['league', 'season', 'Date', 'HomeTeam']).join(tab[['ppg']].rename(columns={'ppg': 'a_ppg'}), on=['league', 'season', 'Date', 'AwayTeam'])
# rank by points per game among sides in the league-season at that date (approximate table)
def rank_at(g):
    last = {}
    out = []
    for _, r in g.iterrows():
        last.setdefault(r.HomeTeam, 0.0); last.setdefault(r.AwayTeam, 0.0)
        order = sorted(last, key=lambda t: last[t]); out.append(order.index(r.HomeTeam) + 1)  # 1 = bottom
        last[r.HomeTeam] = r.h_ppg_next; last[r.AwayTeam] = r.a_ppg_next
    return pd.Series(out, index=g.index)
m['h_ppg_next'] = (m.h_ppg * m.h_played + m.pts_h) / (m.h_played + 1)
ap = tab[['played']].rename(columns={'played': 'a_played'}); m = m.join(ap, on=['league', 'season', 'Date', 'AwayTeam']); m['a_ppg_next'] = (m.a_ppg * m.a_played + m.pts_a) / (m.a_played + 1)
m['h_from_bottom'] = m.groupby(['league', 'season'], group_keys=False).apply(rank_at)
m['releg'] = ((m.h_from_bottom <= 4) & (m.h_played >= 24)).astype(float)   # bottom four, final third of the season
m['late'] = (m.h_played >= 24).astype(float)
def test(x, col, lab, ctrl=('gap',)):
    x = x.dropna(subset=[col] + list(ctrl)); v = x[col].values.astype(float); flag = len(np.unique(v)) <= 2
    if not flag: v = (v - v.mean()) / v.std()
    b, se = ols(x.S_pc.values, np.column_stack([np.ones(len(x)), v] + [x[c].values for c in ctrl]))
    print(f'    {lab:44s} n={len(x):5d}{" (flag on: %d)" % int(v.sum()) if flag else ""} {b[1]:+.4f} (se {se[1]:.4f}, t {b[1]/se[1]:+.2f})')
sets = {'exploration crowd': m[(m.crowd == 'full') & (m.Date <= EXPL_END)], 'ghost': m[m.crowd == 'ghost'], 'hold-out crowd': m[(m.crowd == 'full') & (m.season >= HOLD_START_SEASON) & (m.Date <= PIN_END)]}
for name in ['exploration crowd', 'ghost']:
    x = sets[name]; print(name, len(x))
    test(x, 'h_slump', 'home side surprise in last 3 home games'); test(x, 'a_slump', 'away side surprise in last 3 away games')
    test(x, 'h_lost3', 'home side lost last 2+ at home, no win in 3'); test(x, 'releg', 'home side bottom four, final third'); test(x, 'late', 'final third of season')
    for lg in ['E0', 'E1']: test(x[x.league == lg], 'h_slump', f'  {lg}: home surprise last 3 home')
m.to_pickle('work/pressure.pkl')
