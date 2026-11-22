"""Build one row per match: EPL (E0) and Championship (E1), 2000/01 to 2026/27.
Sources: football-data.co.uk (results, cards, fouls, referee, odds) and Transfermarkt (attendance)."""
import pandas as pd, numpy as np, glob, re, os

def season_start(code):  # '1920' -> 2019
    y = int(code[:2]); return 2000 + y if y < 90 else 1900 + y

def norm_ref(x):
    if not isinstance(x, str) or not x.strip(): return np.nan
    x = re.sub(r'[^A-Za-z\' \-]', ' ', x).strip()
    parts = x.split()
    if len(parts) == 1: return parts[0].title()
    return parts[0][0].upper() + ' ' + parts[-1].title()

def devig(df, cols):
    inv = 1 / df[cols].astype(float)
    return inv.div(inv.sum(axis=1), axis=0)

rows = []
for f in sorted(glob.glob('fd/E[01]_*.csv')):
    lg, code = os.path.basename(f)[:2], os.path.basename(f)[3:7]
    d = pd.read_csv(f, encoding='latin1', on_bad_lines='skip')
    d = d.dropna(subset=['FTHG', 'HomeTeam']).copy()
    d['league'] = lg; d['season'] = season_start(code)
    d['Date'] = pd.to_datetime(d['Date'], dayfirst=True, format='mixed')
    for a, b in [('BbAvH', 'AvgH'), ('BbAvD', 'AvgD'), ('BbAvA', 'AvgA')]:
        if b not in d and a in d: d[b] = d[a]
    keep = ['league', 'season', 'Date', 'Time', 'HomeTeam', 'AwayTeam', 'FTHG', 'FTAG', 'Referee',
            'HS', 'AS', 'HST', 'AST', 'HF', 'AF', 'HC', 'AC', 'HY', 'AY', 'HR', 'AR',
            'PSH', 'PSD', 'PSA', 'PSCH', 'PSCD', 'PSCA', 'B365H', 'B365D', 'B365A',
            'AvgH', 'AvgD', 'AvgA', 'AvgCH', 'AvgCD', 'AvgCA', 'BFECH', 'BFECD', 'BFECA', 'AHh', 'AHCh']
    for k in keep:
        if k not in d: d[k] = np.nan
    rows.append(d[keep])
m = pd.concat(rows, ignore_index=True)
m['ref'] = m.Referee.map(norm_ref)
for c in ['FTHG','FTAG','HS','AS','HST','AST','HF','AF','HC','AC','HY','AY','HR','AR']:
    m[c] = pd.to_numeric(m[c], errors='coerce')
# market probabilities: Pinnacle close, Pinnacle open, Bet365 (long history), market average
for tag, cols in {'pc': ['PSCH','PSCD','PSCA'], 'po': ['PSH','PSD','PSA'], 'b365': ['B365H','B365D','B365A'], 'avg': ['AvgH','AvgD','AvgA']}.items():
    p = devig(m, cols); m[tag+'_h'], m[tag+'_d'], m[tag+'_a'] = p.iloc[:,0], p.iloc[:,1], p.iloc[:,2]
# best available prior for team strength control (not for edge tests)
m['mk_h'] = m.pc_h.fillna(m.b365_h).fillna(m.avg_h); m['mk_a'] = m.pc_a.fillna(m.b365_a).fillna(m.avg_a)
m['hw'] = (m.FTHG > m.FTAG).astype(float); m['aw'] = (m.FTHG < m.FTAG).astype(float); m['gd'] = m.FTHG - m.FTAG

# attendance from Transfermarkt
tm = []
for f in sorted(glob.glob('tm/GB[12]_*.csv')):
    t = pd.read_csv(f); t['league'] = 'E0' if 'GB1' in f else 'E1'; tm.append(t)
if tm:
    tm = pd.concat(tm, ignore_index=True)
    tm['Date'] = pd.to_datetime(tm.date, dayfirst=True)
    tm['FTHG'] = tm.score.str.split(':').str[0].astype(float); tm['FTAG'] = tm.score.str.split(':').str[1].astype(float)
    tm['att'] = pd.to_numeric(tm.attendance, errors='coerce')
    # learn name mapping from same date + same score
    j = m.merge(tm, on=['league', 'season', 'Date', 'FTHG', 'FTAG'])
    mp = j.groupby(['HomeTeam', 'home']).size().reset_index(name='n').sort_values('n').groupby('HomeTeam').tail(1)
    mp = dict(zip(mp.HomeTeam, mp.home))
    m['tm_home'] = m.HomeTeam.map(mp)
    tmk = tm.drop_duplicates(['league', 'Date', 'home'])[['league', 'Date', 'home', 'att', 'referee']].rename(columns={'home': 'tm_home', 'referee': 'tm_referee'})
    tmk['tm_seen'] = 1
    m = m.merge(tmk, on=['league', 'Date', 'tm_home'], how='left')
else:
    m['att'] = np.nan; m['tm_seen'] = np.nan
m['att'] = m['att'].where(m.tm_seen == 1)
# crowd status. Ghost = Transfermarkt page found and no attendance listed, inside the Covid window.
covid = (m.Date >= '2020-03-12') & (m.Date <= '2022-02-28')
m['crowd'] = 'full'
m.loc[covid & (m.tm_seen == 1) & m.att.isna(), 'crowd'] = 'ghost'
m.loc[covid & (m.season == 2020) & m.att.notna(), 'crowd'] = 'partial'
# fallback by date where no Transfermarkt row
nod = covid & (m.tm_seen != 1) & (m.Date >= '2020-06-01') & (m.Date <= '2021-06-30')
m.loc[nod, 'crowd'] = 'ghost'
m.to_pickle('work/master.pkl')
print(len(m), 'matches;', m.ref.nunique(), 'referees')
print(m.groupby(['league','crowd']).size())
print('attendance matched share by league-season (2012+):')
print(m[m.season >= 2012].groupby(['league','season']).tm_seen.apply(lambda s: round(s.notna().mean(), 3)).unstack(0).T)
