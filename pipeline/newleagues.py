"""Bring the extra leagues (football-data 'new' files) into the price model: match Transfermarkt attendance, set crowd
regimes, compute mu and c from Pinnacle closing prices, run the Kalman filter with the settings already fitted."""
import pandas as pd, numpy as np, glob, os, importlib.util, sys
from scipy.stats import norm
FD = {'AUT': 'A1', 'DNK': 'DK1', 'ROU': 'RO1', 'SUI': 'C1', 'JPN': 'JAP1', 'POL': 'PL1', 'RUS': 'RU1', 'SWE': 'SE1', 'NOR': 'NO1', 'FIN': 'FI1', 'IRL': 'IR1'}
rows = []
for code, tmc in FD.items():
    x = pd.read_csv(f'fd3/{code}.csv', encoding='latin1'); x = x.dropna(subset=['HG', 'AG', 'Date', 'PSCH', 'PSCD', 'PSCA'])
    x['league'] = code; x['Date'] = pd.to_datetime(x.Date, dayfirst=True, format='mixed'); x['season'] = x.Season.astype(str).str[:4].astype(int)
    x = x.rename(columns={'Home': 'HomeTeam', 'Away': 'AwayTeam', 'HG': 'FTHG', 'AG': 'FTAG'}); x['tmc'] = tmc; rows.append(x[['league', 'tmc', 'season', 'Date', 'HomeTeam', 'AwayTeam', 'FTHG', 'FTAG', 'PSCH', 'PSCD', 'PSCA']])
e = pd.concat(rows, ignore_index=True); e = e[e.season >= 2012].copy()
for c in ['FTHG', 'FTAG', 'PSCH', 'PSCD', 'PSCA']: e[c] = pd.to_numeric(e[c], errors='coerce')
e['att'] = np.nan; e['tm_seen'] = False
for f in glob.glob('tm2/*.csv'):
    comp, sea = os.path.basename(f)[:-4].rsplit('_', 1); sea = int(sea)
    if comp not in FD.values(): continue
    t = pd.read_csv(f)
    if len(t) == 0: continue
    t['Date'] = pd.to_datetime(t.date, dayfirst=True); t[['hg', 'ag']] = t.score.str.split(':', expand=True).astype(int)
    x = e[(e.tmc == comp) & (e.Date >= t.Date.min() - pd.Timedelta(days=3)) & (e.Date <= t.Date.max() + pd.Timedelta(days=3))]
    if len(x) == 0: continue
    j = x.merge(t, left_on=['Date', 'FTHG', 'FTAG'], right_on=['Date', 'hg', 'ag']); j = j[~j.duplicated(['Date', 'FTHG', 'FTAG'], keep=False)]
    hmap = {**j.groupby('away').AwayTeam.agg(lambda s: s.value_counts().index[0]).to_dict(), **j.groupby('home').HomeTeam.agg(lambda s: s.value_counts().index[0]).to_dict()}
    t = t.assign(H=t.home.map(hmap), A=t.away.map(hmap)).dropna(subset=['H', 'A'])
    for off in [0, 1, -1, 2, -2]:
        k = t.assign(Date=t.Date + pd.Timedelta(days=off)).drop_duplicates(['Date', 'H', 'A']).set_index(['Date', 'H', 'A'])
        idx = x.index[~e.loc[x.index, 'tm_seen']]; key = pd.MultiIndex.from_frame(e.loc[idx, ['Date', 'HomeTeam', 'AwayTeam']]); hit = key.isin(k.index)
        e.loc[idx[hit], 'att'] = pd.to_numeric(k.loc[key[hit], 'attendance'], errors='coerce').values; e.loc[idx[hit], 'tm_seen'] = True
    print(f'  {comp} {sea}: {len(t)} scraped, {int(e[(e.tmc==comp)&e.tm_seen&(e.Date>=t.Date.min()-pd.Timedelta(days=3))&(e.Date<=t.Date.max()+pd.Timedelta(days=3))].shape[0])} matched')
e['closed'] = e.tm_seen & (e.att.isna() | (e.att <= 100))
fw = (e.Date >= '2020-05-01') & (e.Date <= '2021-06-30')
e['regime'] = 'full'
e.loc[(e.Date >= '2020-03-01') & (e.Date < '2020-05-01'), 'regime'] = 'drop'
e.loc[fw & ~e.tm_seen, 'regime'] = 'drop'; e.loc[fw & e.closed, 'regime'] = 'none'; e.loc[fw & e.tm_seen & ~e.closed, 'regime'] = 'partial'
e.loc[(e.Date > '2021-06-30') & e.closed, 'regime'] = 'none'
inv = 1 / e[['PSCH', 'PSCD', 'PSCA']]; p = inv.div(inv.sum(axis=1), axis=0); e['pc_h'], e['pc_d'], e['pc_a'] = p.iloc[:, 0], p.iloc[:, 1], p.iloc[:, 2]
zh, za = norm.ppf(e.pc_h), norm.ppf(e.pc_a); e['mu'] = (zh - za) / 2; e['c'] = -(zh + za) / 2
e['hw'] = (e.FTHG > e.FTAG).astype(int); e['aw'] = (e.FTHG < e.FTAG).astype(int); e['y'] = e.hw - e.aw
e = e.sort_values('Date').reset_index(drop=True)
fw = (e.Date >= '2020-05-01') & (e.Date <= '2021-06-30')
print('extra leagues, first-wave window, by regime and league:'); print(e[fw].groupby(['league', 'regime']).size().unstack(fill_value=0).to_string())
# Kalman filter with the settings already fitted (kf.py)
src = open('kf.py').read(); ns = {}; exec(src[:src.index("if len(sys.argv) > 1 and sys.argv[1] == 'fit':")], ns)
par = np.load('work/kf_par.npy'); e['reg'] = e.regime.map({'full': 0, 'none': 1, 'partial': 2, 'drop': 0}).astype(int); outs = []
for lg, x in e.groupby('league'): outs.append(ns['run'](x, *par, out=True)[1])
e = e.join(pd.concat(outs)); e.to_pickle('work/kf_extra.pkl'); print('saved', len(e))
