"""Avenue 1: closed stadiums outside the discovery sample. See PLAN_closures.md (rules fixed before results were seen).
Builds work/eu.pkl (all leagues with Pinnacle odds, attendance where scraped) and prints samples A, B, C."""
import pandas as pd, numpy as np, glob, os, sys
TM = {'D1': 'L1', 'D2': 'L2', 'SP1': 'ES1', 'SP2': 'ES2', 'I1': 'IT1', 'I2': 'IT2', 'F1': 'FR1', 'F2': 'FR2', 'N1': 'NL1', 'B1': 'BE1', 'P1': 'PO1', 'T1': 'TR1', 'G1': 'GR1', 'SC0': 'SC1', 'E2': 'GB3', 'E3': 'GB4'}
rows = []
for f in sorted(glob.glob('fd2/*.csv')):
    lg, code = os.path.basename(f)[:-9], os.path.basename(f)[-8:-4]
    try: d = pd.read_csv(f, encoding='latin1', on_bad_lines='skip')
    except Exception: continue
    if 'FTHG' not in d or 'HomeTeam' not in d: continue
    d = d.dropna(subset=['FTHG', 'HomeTeam', 'Date']); d['league'] = lg; d['season'] = 2000 + int(code[:2]); d['Date'] = pd.to_datetime(d.Date, dayfirst=True, format='mixed')
    for c in ['PSH', 'PSD', 'PSA', 'PSCH', 'PSCD', 'PSCA', 'MaxCH', 'MaxCD', 'MaxCA', 'AvgCH', 'AvgCD', 'AvgCA', 'B365H', 'B365D', 'B365A']:
        if c not in d: d[c] = np.nan
    rows.append(d[['league', 'season', 'Date', 'HomeTeam', 'AwayTeam', 'FTHG', 'FTAG', 'PSH', 'PSD', 'PSA', 'PSCH', 'PSCD', 'PSCA', 'MaxCH', 'MaxCD', 'MaxCA', 'AvgCH', 'AvgCD', 'AvgCA', 'B365H', 'B365D', 'B365A']])
e = pd.concat(rows, ignore_index=True)
for c in e.columns[5:]: e[c] = pd.to_numeric(e[c], errors='coerce')
def dv(h, d, a, p):
    inv = 1 / e[[h, d, a]]; q = inv.div(inv.sum(axis=1), axis=0); e[p + '_h'], e[p + '_d'], e[p + '_a'] = q.iloc[:, 0], q.iloc[:, 1], q.iloc[:, 2]
dv('PSCH', 'PSCD', 'PSCA', 'pc'); dv('PSH', 'PSD', 'PSA', 'po'); dv('AvgCH', 'AvgCD', 'AvgCA', 'avg')
e['hw'] = (e.FTHG > e.FTAG).astype(int); e['aw'] = (e.FTHG < e.FTAG).astype(int)
e['S_pc'] = (e.hw - e.aw) - (e.pc_h - e.pc_a); e['S_po'] = (e.hw - e.aw) - (e.po_h - e.po_a); e['S_avg'] = (e.hw - e.aw) - (e.avg_h - e.avg_a)
# attendance from Transfermarkt
tm = []
for f in sorted(glob.glob('tm2/*.csv')):
    comp, sea = os.path.basename(f)[:-4].rsplit('_', 1); t = pd.read_csv(f)
    if len(t) == 0: continue
    t['tmcomp'] = comp; t['Date'] = pd.to_datetime(t.date, dayfirst=True); t[['hg', 'ag']] = t.score.str.split(':', expand=True).astype(int); tm.append(t)
tm = pd.concat(tm, ignore_index=True); tm['league'] = tm.tmcomp.map({v: k for k, v in TM.items()})
e['att'] = np.nan; e['tm_seen'] = False
for (lg, sea), t in tm.groupby(['league', 'season']):
    x = e[(e.league == lg) & (e.season == sea)]
    if len(x) == 0: continue
    j = x.merge(t, left_on=['Date', 'FTHG', 'FTAG'], right_on=['Date', 'hg', 'ag'])
    # keep date+score pairs that are unique on both sides, then vote on names
    j = j[~j.duplicated(['Date', 'FTHG', 'FTAG'], keep=False)]
    hmap = j.groupby('home').HomeTeam.agg(lambda s: s.value_counts().index[0]).to_dict(); amap = j.groupby('away').AwayTeam.agg(lambda s: s.value_counts().index[0]).to_dict(); hmap = {**amap, **hmap}
    t = t.assign(H=t.home.map(hmap), A=t.away.map(hmap)).dropna(subset=['H', 'A'])
    for off in [0, 1, -1, 2, -2]:
        k = t.assign(Date=t.Date + pd.Timedelta(days=off)).drop_duplicates(['Date', 'H', 'A']).set_index(['Date', 'H', 'A'])
        idx = x.index[~e.loc[x.index, 'tm_seen']]; key = pd.MultiIndex.from_frame(e.loc[idx, ['Date', 'HomeTeam', 'AwayTeam']])
        hit = key.isin(k.index)
        e.loc[idx[hit], 'att'] = k.loc[key[hit], 'attendance'].values; e.loc[idx[hit], 'tm_seen'] = True
e['noatt'] = e.tm_seen & e.att.isna()
e.to_pickle('work/eu.pkl')
cov = e[e.season.isin(tm.season.unique())].groupby(['league', 'season']).agg(n=('hw', 'size'), seen=('tm_seen', 'sum'), blank=('noatt', 'sum'), pin=('PSCH', lambda s: s.notna().sum()))
print(cov[cov.seen > 0].to_string())
if len(sys.argv) > 1 and sys.argv[1] == 'coverage': sys.exit()
rng = np.random.default_rng(7)
def roi(x, col, win):
    o = x[col].values.astype(float); r = np.where(x[win] == 1, o - 1, -1.0); r = r[~np.isnan(o)]
    if len(r) < 5: return 'n/a'
    bs = [rng.choice(r, len(r)).mean() for _ in range(4000)]; return f'{r.mean()*100:+6.1f}% [{np.percentile(bs,2.5)*100:+6.1f}, {np.percentile(bs,97.5)*100:+6.1f}]'
def rep(lab, x):
    x = x[x.PSCH.notna()]
    if len(x) == 0: print(f'{lab:40s} n=0'); return
    s = x.S_pc; t = s.mean() / (s.std() / np.sqrt(len(x))) if len(x) > 1 else np.nan
    print(f'{lab:40s} n={len(x):5d} S {s.mean():+.4f} (se {s.std()/np.sqrt(len(x)):.4f}, t {t:+.2f}) | away: close {roi(x,"PSCA","aw")} open {roi(x,"PSA","aw")} best {roi(x,"MaxCA","aw")} | home close {roi(x,"PSCH","hw")}')
print('\nBASELINE: crowd games, same leagues, 2015/16 to Feb 2020'); rep('all non-English leagues', e[(e.Date >= '2015-07-01') & (e.Date < '2020-03-01')])
print('\nSAMPLE A: replication, other leagues, first wave')
restart = e[(e.Date >= '2020-05-01') & (e.Date <= '2020-08-31')]; s20 = e[(e.season == 2020) & e.noatt & (e.Date <= '2021-06-30')]
A = pd.concat([restart, s20]); rep('A all (restart by date + 2020/21 blanks)', A); rep('  restart May-Aug 2020 (date window)', restart); rep('  2020/21 no attendance recorded', s20)
for lg, x in A.groupby('league'): rep(f'    {lg}', x)
part20 = e[(e.season == 2020) & e.tm_seen & e.att.notna()]; rep('  2020/21 with some crowd recorded', part20)
print('\nSAMPLE B: confirmation, closures from 1 July 2021')
late = e[(e.Date >= '2021-07-01') & e.tm_seen].sort_values(['league', 'Date']).copy()
late['run'] = 0
for lg, x in late.groupby('league'):
    b = x[x.noatt]
    for i, r in b.iterrows():
        late.loc[i, 'run'] = int(((b.Date >= r.Date - pd.Timedelta(days=15)) & (b.Date <= r.Date + pd.Timedelta(days=15))).sum())
B = late[late.noatt & (late.run >= 5)]; iso = late[late.noatt & (late.run < 5)]
rep('B all blanket closures', B)
for (lg, sea), x in B.groupby(['league', 'season']): rep(f'    {lg} {sea}/{sea+1-2000} ({x.Date.min().date()} to {x.Date.max().date()})', x)
rep('isolated blanks (punishment or missing data)', iso)
print('\nSAMPLE C: capped crowds from 1 July 2021 (gate under 25% of the club median that season)')
late['med'] = late.groupby(['league', 'season', 'HomeTeam']).att.transform('median'); C = late[late.att.notna() & (late.att < 0.25 * late.med)]
rep('C capped crowds', C)
for (lg, sea), x in C.groupby(['league', 'season']): rep(f'    {lg} {sea}', x)
rep('crowd games 2021/22 on, same league-seasons', late[late.att.notna() & (late.att >= 0.25 * late.med)])
print('\nA + B pooled (all closed-door games outside England)'); rep('A + B', pd.concat([A, B]))
