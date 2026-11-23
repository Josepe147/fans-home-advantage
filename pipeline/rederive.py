"""Independent re-derivation of the headline numbers from the raw season files. Imports nothing from the project,
uses no model: goals, handicap lines and simple averages. Closed doors is flagged by date alone (1 May 2020 to
30 June 2021), which lets in some partial-crowd games and so, if anything, understates the drop.
fd/ and fd2/ hold some identical league-season files, so each file name is read once (fd/ first)."""
import pandas as pd, numpy as np, glob, os
rows = []
fd1 = sorted(glob.glob('fd/*.csv')); seen = {os.path.basename(f) for f in fd1}
for f in fd1 + sorted(f for f in glob.glob('fd2/*.csv') if os.path.basename(f) not in seen):
    lg, code = os.path.basename(f)[:-9], os.path.basename(f)[-8:-4]; sea = 2000 + int(code[:2])
    if sea < 2015: continue
    try: d = pd.read_csv(f, encoding='latin1', on_bad_lines='skip')
    except Exception: continue
    if 'FTHG' not in d: continue
    d = d.dropna(subset=['FTHG', 'FTAG', 'Date']); d['lg'] = lg; d['sea'] = sea; d['Date'] = pd.to_datetime(d.Date, dayfirst=True, format='mixed')
    for c in ['PSCH', 'PSCD', 'PSCA', 'AHCh', 'AHh', 'BbAHh', 'HS', 'AS', 'HST', 'AST', 'HF', 'AF', 'HY', 'AY', 'HR', 'AR', 'HC', 'AC']:
        d[c] = pd.to_numeric(d[c], errors='coerce') if c in d else np.nan
    rows.append(d[['lg', 'sea', 'Date', 'FTHG', 'FTAG', 'PSCH', 'PSCD', 'PSCA', 'AHCh', 'AHh', 'BbAHh', 'HS', 'AS', 'HST', 'AST', 'HF', 'AF', 'HY', 'AY', 'HR', 'AR', 'HC', 'AC']])
d = pd.concat(rows, ignore_index=True); d['gd'] = d.FTHG - d.FTAG; d['w'] = np.sign(d.gd)
inv = 1 / d[['PSCH', 'PSCD', 'PSCA']]; p = inv.div(inv.sum(axis=1), axis=0); d['pdiff'] = p.PSCH - p.PSCA
d['line'] = -d.AHCh.fillna(d.AHh).fillna(d.BbAHh)                       # handicap the home side gives, in goals
d['per'] = np.where(d.Date < '2020-03-01', 'crowd before', np.where((d.Date >= '2020-05-01') & (d.Date <= '2021-06-30'), 'closed doors', np.where(d.Date >= '2021-08-01', 'crowd after', 'drop')))
d = d[d.per != 'drop']; print('matches:', d.per.value_counts().to_dict(), '| leagues', d.lg.nunique())
rng = np.random.default_rng(0)
def ratio(col, num='closed doors', den='crowd before', data=d):
    """ratio of means, bootstrap over league-seasons (vectorised)"""
    x = data.dropna(subset=[col]); x = x[x.per.isin([num, den])]
    g = x.groupby(['lg', 'sea', 'per'])[col].agg(['sum', 'count']).unstack('per').fillna(0)
    S = g['sum'].reindex(columns=[num, den], fill_value=0).values; N = g['count'].reindex(columns=[num, den], fill_value=0).values
    est = (S[:, 0].sum() / N[:, 0].sum()) / (S[:, 1].sum() / N[:, 1].sum())
    idx = rng.integers(0, len(S), (2000, len(S))); Sb = S[idx].sum(axis=1); Nb = N[idx].sum(axis=1); bs = (Sb[:, 0] / Nb[:, 0]) / (Sb[:, 1] / Nb[:, 1])
    a_ = x[x.per == num][col]; b_ = x[x.per == den][col]
    return f'{b_.mean():+.3f} -> {a_.mean():+.3f} | ratio {est:.2f} (95% {np.percentile(bs,2.5):.2f} to {np.percentile(bs,97.5):.2f}) | n {len(b_)} / {len(a_)}'
print('\nHOME ADVANTAGE, crowd seasons 2015/16 to Feb 2020 -> closed doors. Ratio = share of home advantage left.')
print('  RESULTS  goal difference per match      ', ratio('gd'))
print('  RESULTS  home win minus away win share  ', ratio('w'))
print('  MARKET   handicap line, goals           ', ratio('line'))
print('  MARKET   priced home minus away prob    ', ratio('pdiff'))
print('\nSAME, crowd seasons from August 2021 against before (did it come back?)')
print('  RESULTS  goal difference per match      ', ratio('gd', 'crowd after')); print('  MARKET   priced home minus away prob    ', ratio('pdiff', 'crowd after'))
print('\nREFEREE AND PERFORMANCE CHANNELS, away minus home per match (all leagues that record them)')
for a_, h_, lab in [('AS', 'HS', 'shots'), ('AST', 'HST', 'shots on target'), ('AC', 'HC', 'corners'), ('AF', 'HF', 'fouls given against'), ('AY', 'HY', 'yellow cards'), ('AR', 'HR', 'red cards')]:
    d['x'] = d[a_] - d[h_]; x = d.dropna(subset=['x']); b = x[x.per == 'crowd before'].x; c = x[x.per == 'closed doors'].x; a = x[x.per == 'crowd after'].x
    se = np.sqrt(b.var() / len(b) + c.var() / len(c)); print(f'  {lab:20s} before {b.mean():+.3f} | closed doors {c.mean():+.3f} | after {a.mean():+.3f} | change {c.mean()-b.mean():+.3f} (se {se:.3f}) | share left {c.mean()/b.mean():.2f} | n closed {len(c)}')
