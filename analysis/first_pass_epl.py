"""First pass: Premier League home advantage with and without fans (16 Nov 2026)."""
import pandas as pd

def show(d, label):
    inv = 1 / d[['PSCH', 'PSCD', 'PSCA']]
    p = inv.div(inv.sum(axis=1), axis=0)
    print(f"{label:28s} n={len(d):4d} home {100*(d.FTHG>d.FTAG).mean():5.1f}% "
          f"away {100*(d.FTHG<d.FTAG).mean():5.1f}% GD {(d.FTHG-d.FTAG).mean():+.2f} "
          f"market home {100*p.iloc[:,0].mean():5.1f}%")

def load(s):
    d = pd.read_csv(f'data/E0_{s}.csv', encoding='latin1').dropna(subset=['FTHG'])
    d['Date'] = pd.to_datetime(d.Date, dayfirst=True)
    return d

show(pd.concat([load(s) for s in ['1516', '1617', '1718', '1819']]), '2015-19 with fans')
e = load('1920')
show(e[e.Date < '2020-04-01'], '2019/20 with fans')
show(e[e.Date >= '2020-06-01'], '2019/20 restart, no fans')
d = load('2021')
show(d, '2020/21 empty stadiums')
show(d[d.Date < '2020-12-01'], '  first 3 months')
