"""Model step 1: one table for all 18 leagues with the market's latent supremacy and a crowd regime per match.
Ordered probit reading of a price: P(home) = Phi(mu - c), P(away) = Phi(-mu - c). Given de-vigged probabilities this inverts exactly:
mu = (z_h - z_a) / 2, c = -(z_h + z_a) / 2 with z = Phi^-1(p)."""
import pandas as pd, numpy as np
from scipy.stats import norm
m = pd.read_pickle('work/master.pkl'); e = pd.read_pickle('work/eu.pkl')
a = m[m.season >= 2012][['league', 'season', 'Date', 'HomeTeam', 'AwayTeam', 'hw', 'aw', 'pc_h', 'pc_d', 'pc_a', 'PSCH', 'PSCD', 'PSCA', 'crowd']].copy()
a['regime'] = a.crowd.map({'full': 'full', 'ghost': 'none', 'partial': 'partial'})
b = e[['league', 'season', 'Date', 'HomeTeam', 'AwayTeam', 'hw', 'aw', 'pc_h', 'pc_d', 'pc_a', 'PSCH', 'PSCD', 'PSCA', 'att', 'tm_seen', 'noatt']].copy()
b['regime'] = 'full'
b.loc[(b.Date >= '2020-03-01') & (b.Date <= '2020-04-30'), 'regime'] = 'drop'          # ambiguous weeks
b.loc[(b.Date >= '2020-05-01') & (b.Date <= '2020-08-31'), 'regime'] = 'none'          # restart, all behind closed doors
s20 = b.season == 2020
b.loc[s20 & b.noatt, 'regime'] = 'none'; b.loc[s20 & b.tm_seen & b.att.notna(), 'regime'] = 'partial'; b.loc[s20 & ~b.tm_seen, 'regime'] = 'drop'
late = b[(b.Date >= '2021-07-01') & b.tm_seen].sort_values(['league', 'Date'])
for lg, x in late.groupby('league'):
    bl = x[x.noatt]
    run = pd.Series([int(((bl.Date >= d - pd.Timedelta(days=15)) & (bl.Date <= d + pd.Timedelta(days=15))).sum()) for d in bl.Date], index=bl.index)
    b.loc[run.index[run >= 5], 'regime'] = 'none'
med = late.groupby(['league', 'season', 'HomeTeam']).att.transform('median'); cap = late.index[late.att.notna() & (late.att < 0.25 * med)]
b.loc[cap, 'regime'] = 'partial'
d = pd.concat([a.drop(columns='crowd'), b.drop(columns=['att', 'tm_seen', 'noatt'])], ignore_index=True)
d = d[d.pc_h.notna() & (d.season >= 2012)].sort_values('Date').reset_index(drop=True)
_zh, _za = norm.ppf(d.pc_h), norm.ppf(d.pc_a); d['mu'] = (_zh - _za) / 2; d['c'] = -(_zh + _za) / 2; d['y'] = d.hw - d.aw
d.to_pickle('work/model_all.pkl')      # every priced match, including the ambiguous weeks, for tracking team strength in kf.py
d = d[d.regime != 'drop'].reset_index(drop=True)
d['y'] = d.hw - d.aw
zh, za = norm.ppf(d.pc_h), norm.ppf(d.pc_a); d['mu'] = (zh - za) / 2; d['c'] = -(zh + za) / 2
d['wave'] = np.where((d.regime == 'none') & (d.Date >= '2021-07-01'), 'later', np.where(d.regime == 'none', 'first', ''))
d.to_pickle('work/model.pkl')
print(len(d), 'matches |', d.league.nunique(), 'leagues |', d.Date.min().date(), 'to', d.Date.max().date())
print(d.groupby('regime').size().to_dict(), '| none by wave', d[d.regime == 'none'].wave.value_counts().to_dict())
print('typical match: mu', round(d.mu.mean(), 3), 'c', round(d.c.mean(), 3))
