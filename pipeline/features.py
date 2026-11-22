"""Crowd-related match features added to the master table (used by explore_ab.py)."""
import pandas as pd, numpy as np
XY = {'Arsenal':(51.555,-0.108),'Aston Villa':(52.509,-1.885),'Barnsley':(53.552,-1.468),'Birmingham':(52.476,-1.868),'Blackburn':(53.729,-2.489),'Blackpool':(53.805,-3.048),'Bolton':(53.581,-2.536),'Bournemouth':(50.735,-1.838),'Brentford':(51.491,-0.289),'Brighton':(50.862,-0.083),'Bristol City':(51.440,-2.620),'Burnley':(53.789,-2.230),'Burton':(52.822,-1.627),'Cardiff':(51.473,-3.203),'Charlton':(51.486,0.036),'Chelsea':(51.482,-0.191),'Coventry':(52.448,-1.496),'Crystal Palace':(51.398,-0.086),'Derby':(52.915,-1.447),'Doncaster':(53.510,-1.114),'Everton':(53.439,-2.966),'Fulham':(51.475,-0.222),'Huddersfield':(53.654,-1.768),'Hull':(53.746,-0.368),'Ipswich':(52.055,1.145),'Leeds':(53.778,-1.572),'Leicester':(52.620,-1.142),'Lincoln':(53.218,-0.541),'Liverpool':(53.431,-2.961),'Luton':(51.884,-0.432),'Man City':(53.483,-2.200),'Man United':(53.463,-2.291),'Middlesbrough':(54.578,-1.217),'Millwall':(51.486,-0.051),'Milton Keynes Dons':(52.010,-0.734),'Newcastle':(54.976,-1.622),'Norwich':(52.622,1.309),"Nott'm Forest":(52.940,-1.133),'Oxford':(51.716,-1.208),'Peterboro':(52.565,-0.240),'Plymouth':(50.388,-4.151),'Portsmouth':(50.796,-1.064),'Preston':(53.772,-2.688),'QPR':(51.509,-0.232),'Reading':(51.422,-0.983),'Rotherham':(53.428,-1.362),'Sheffield United':(53.370,-1.471),'Sheffield Weds':(53.411,-1.501),'Southampton':(50.906,-1.391),'Stoke':(52.988,-2.176),'Sunderland':(54.915,-1.388),'Swansea':(51.643,-3.935),'Tottenham':(51.604,-0.066),'Watford':(51.650,-0.402),'West Brom':(52.509,-1.964),'West Ham':(51.539,-0.017),'Wigan':(53.548,-2.654),'Wolves':(52.590,-2.130),'Wrexham':(53.052,-3.004),'Wycombe':(51.631,-0.800),'Yeovil':(50.950,-2.674)}
def hav(a, b):
    la1, lo1, la2, lo2 = map(np.radians, [a[0], a[1], b[0], b[1]])
    h = np.sin((la2-la1)/2)**2 + np.cos(la1)*np.cos(la2)*np.sin((lo2-lo1)/2)**2
    return 6371 * 2 * np.arcsin(np.sqrt(h))
def add(m):
    m = m.copy()
    m['S_pc'] = (m.hw - m.aw) - (m.pc_h - m.pc_a); m['S_po'] = (m.hw - m.aw) - (m.po_h - m.po_a)
    m['gap'] = m.pc_h - m.pc_a
    m['dist'] = [hav(XY[h], XY[a]) if h in XY and a in XY else np.nan for h, a in zip(m.HomeTeam, m.AwayTeam)]
    m['ldist'] = np.log(m.dist.clip(lower=3))
    m['derby'] = (m.dist < 40).astype(float)
    m['far'] = (m.dist > 250).astype(float)
    dow = m.Date.dt.dayofweek
    m['midweek'] = dow.isin([1, 2, 3]).astype(float)
    m['far_midweek'] = m.far * m.midweek
    # attendance features. Capacity proxy = highest home gate that season (full-crowd games only).
    full = m[(m.crowd == 'full') & m.att.notna()]
    cs = full.groupby(['HomeTeam', 'season']).att.agg(cap='max', seas_mean='mean').reset_index()
    m = m.merge(cs, on=['HomeTeam', 'season'], how='left')
    # prior-season mean gate = what was knowable before the season
    prev = cs.rename(columns={'seas_mean': 'prev_mean', 'cap': 'prev_cap'}).assign(season=lambda d: d.season + 1)[['HomeTeam', 'season', 'prev_mean', 'prev_cap']]
    m = m.merge(prev, on=['HomeTeam', 'season'], how='left')
    m['occ'] = m.att / m.cap
    m['rel_att'] = m.att / m.seas_mean
    m['latt'] = np.log(m.att)
    # expanding mean of the club's earlier home gates this season (knowable before kick-off)
    m = m.sort_values('Date')
    m['run_mean'] = m[m.crowd == 'full'].groupby(['HomeTeam', 'season']).att.transform(lambda s: s.shift(1).expanding().mean())
    m['rel_run'] = m.att / m.run_mean
    return m
