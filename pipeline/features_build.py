"""Builds work/feat2.pkl: master table plus crowd-dose and away-support features. Run after build_master.py."""
import pandas as pd, numpy as np
from reflib import ols, EXPL_END
from features import add
m = add(pd.read_pickle('work/master.pkl'))
full = m[(m.crowd == 'full') & m.att.notna()]
# away club fan-base size = its own mean home gate in the previous season (knowable in advance)
g = full.groupby(['HomeTeam', 'season']).att.mean().reset_index(); g['season'] += 1
m = m.merge(g.rename(columns={'HomeTeam': 'AwayTeam', 'att': 'away_fanbase'}), on=['AwayTeam', 'season'], how='left'); m['lfan'] = np.log(m.away_fanbase)
# realised uplift v the club's season mean. WARNING: uses later gates, so it leaks results (see leak check in extra.py)
m['relw'] = m.rel_att.clip(0.8, 1.2); m['relz'] = m.groupby('league').relw.transform(lambda s: (s - s.mean()) / s.std())
# clean version: uplift v the mean of the club's EARLIER home gates this season, at least 3 of them
m['n_prior'] = m[m.crowd == 'full'].groupby(['HomeTeam', 'season']).cumcount()
m['runw'] = m.rel_run.clip(0.8, 1.2).where(m.n_prior >= 3); m['runz'] = m.groupby('league').runw.transform(lambda s: (s - s.mean()) / s.std())
# exogenous predicted uplift, fitted on the exploration set only
ex = (m.crowd == 'full') & m.pc_h.notna() & m.po_h.notna() & (m.season >= 2012) & (m.Date <= EXPL_END)
Xf = lambda d: np.column_stack([np.ones(len(d)), d.lfan, d.ldist, d.midweek, d.derby, (d.league == 'E1').astype(float), (d.league == 'E1') * d.lfan])
x = m[ex].dropna(subset=['relz', 'lfan', 'ldist']); beta, _ = ols(x.relz.values, Xf(x))
ok = m.lfan.notna() & m.ldist.notna(); m.loc[ok, 'pred_up'] = Xf(m[ok]) @ beta
m.to_pickle('work/feat2.pkl'); print('feat2 rows', len(m), 'uplift model', np.round(beta, 3))
