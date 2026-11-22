"""The market's priced home advantage behind closed doors, month by month, two ways:
(1) Kalman-filtered (smooth, but lags a sudden change by several weeks), (2) raw monthly: each match's price minus the
strength gap the filter expected from earlier prices, averaged over the month (noisier, no lag). Then the implied prior
is refitted on the raw path, and a figure is drawn."""
import pandas as pd, numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt, matplotlib.dates as mdates
from scipy.stats import norm
from scipy.optimize import minimize
d = pd.read_pickle('work/kf.pkl'); d = d[d.regime != 'drop'].copy()
def ll(eta, c, y):
    ph = norm.cdf(eta - c); pa = norm.cdf(-eta - c); pdw = np.clip(1 - ph - pa, 1e-12, None)
    return np.where(y == 1, np.log(np.clip(ph, 1e-12, None)), np.where(y == -1, np.log(np.clip(pa, 1e-12, None)), np.log(pdw)))
pre = d[(d.regime == 'full') & (d.Date < '2020-03-01')]
a, b = minimize(lambda p: -ll(p[0] + p[1] * pre.mu.values, pre.c.values, pre.y.values).sum(), [0, 1], method='Nelder-Mead', options={'xatol': 1e-7, 'fatol': 1e-9}).x
Hpre = d[(d.regime == 'full') & (d.season >= 2015) & (d.Date < '2020-03-01')].groupby('league').H_post.mean().rename('H_pre')
g = d[(d.regime == 'none') & (d.Date >= '2020-05-01') & (d.Date <= '2021-06-30')].join(Hpre, on='league').sort_values('Date').reset_index(drop=True)
g['ym'] = g.Date.dt.to_period('M'); g['base'] = a + b * g.H_pre; g['eta0'] = a + b * g.mu; g['r_kf'] = (a + b * g.H_post) / g.base; g['r_raw_i'] = (a + b * (g.H_prior + g.innov)) / g.base
M = g.groupby('ym').apply(lambda x: pd.Series({'n': len(x), 'leagues': x.league.nunique(), 'kf': x.r_kf.mean(), 'raw': x.r_raw_i.mean(), 'raw_se': x.groupby('league').r_raw_i.mean().std() / np.sqrt(x.league.nunique()) if x.league.nunique() > 2 else np.nan})); M = M[M.n >= 60]
# learner on a rho grid, exact
R = np.arange(0.0, 1.6001, 0.01); E = g.eta0.values[:, None] + g.base.values[:, None] * (R[None, :] - g.r_kf.values[:, None]); L = ll(E, g.c.values[:, None], g.y.values[:, None])
def post_before(date, rho0, s0):
    lp = L[(g.Date < date).values].sum(axis=0) + norm.logpdf(R, rho0, s0); p = np.exp(lp - lp.max()); p /= p.sum(); m = (p * R).sum(); return m, np.sqrt((p * (R - m) ** 2).sum())
mid = [p.start_time + pd.Timedelta(days=14) for p in M.index]
M['flat'], M['flat_sd'] = zip(*[post_before(t, 1.0, 5.0) for t in mid])
def sse(p): return np.average((np.array([post_before(t, p[0], np.exp(p[1]))[0] for t in mid]) - M.raw.values) ** 2, weights=M.n.values)
best = min((minimize(sse, [x0, np.log(s)], method='Nelder-Mead', options={'xatol': 1e-4, 'fatol': 1e-10}) for x0 in [0.6, 0.75] for s in [0.03, 0.1]), key=lambda f: f.fun)
rho0, s0 = best.x[0], float(np.exp(best.x[1])); M['implied'] = [post_before(t, rho0, s0)[0] for t in mid]
ph0 = norm.cdf(g.eta0 - g.c); pa0 = norm.cdf(-g.eta0 - g.c); f1 = norm.pdf(g.eta0 - g.c); f2 = norm.pdf(g.eta0 + g.c); info1 = ((f1 ** 2 / ph0 + f2 ** 2 / pa0 + (f2 - f1) ** 2 / (1 - ph0 - pa0)) * g.base ** 2).mean()
print(M.round(3).to_string())
print(f'\nmarket-implied prior fitted to the RAW monthly path: mean {rho0:.3f}, sd {s0:.4f} = weight of about {1/(s0**2*info1):,.0f} matches (rms gap {np.sqrt(best.fun):.3f}; flat line at the mean: {np.sqrt(np.average((np.average(M.raw,weights=M.n)-M.raw)**2,weights=M.n)):.3f})')
print('profile: rms gap at fixed prior sd (prior mean re-optimised):', {s: round(float(np.sqrt(minimize(lambda q: sse([q[0], np.log(s)]), [0.65], method='Nelder-Mead').fun)), 4) for s in [0.02, 0.04, 0.07, 0.10, 0.15, 0.30]})
e1 = M.loc['2020-09':'2020-11']; e2 = M.loc['2021-03':'2021-06']; w = lambda x, c: np.average(x[c], weights=x.n)
print(f'raw path: Sep-Nov 2020 {w(e1,"raw"):.3f}, Mar-Jun 2021 {w(e2,"raw"):.3f} | filtered path: {w(e1,"kf"):.3f} -> {w(e2,"kf"):.3f} | change on the raw path {w(e2,"raw")-w(e1,"raw"):+.3f} (se about {np.sqrt((e1.raw_se**2).mean()/len(e1)+(e2.raw_se**2).mean()/len(e2)):.3f})')
inside = ((M.raw >= M.flat - 1.96 * M.flat_sd) & (M.raw <= M.flat + 1.96 * M.flat_sd)); print('months where the raw market reading sits inside the learner 95% band:', int(inside.sum()), 'of', len(M), '| winter dip: Dec-Feb raw', round(w(M.loc['2020-12':'2021-02'],'raw'),3), 'v Sep-Nov', round(w(e1,'raw'),3), 'and Mar-May', round(w(M.loc['2021-03':'2021-05'],'raw'),3))
M.to_csv('work/market_path.csv')
# figure
INK, INK2, GRID, SURF, BLUE, ORANGE = '#0b0b0b', '#52514e', '#e4e3df', '#fcfcfb', '#2a78d6', '#eb6834'; x = [pd.Timestamp(t) for t in mid]
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10}); fig, ax = plt.subplots(figsize=(9.6, 5.4), dpi=160); fig.patch.set_facecolor(SURF); ax.set_facecolor(SURF)
ax.fill_between(x, 100 * (M.flat - 1.96 * M.flat_sd), 100 * (M.flat + 1.96 * M.flat_sd), color=ORANGE, alpha=0.14, linewidth=0, label='Learner, 95% interval')
ax.plot(x, 100 * M.flat, color=ORANGE, lw=2, label='Learner: results so far, no prior view', solid_capstyle='round')
ax.plot(x, 100 * M.kf, color=BLUE, lw=2, label='Market: priced home advantage (filtered)', solid_capstyle='round')
ax.scatter(x, 100 * M.raw, s=42, color=BLUE, edgecolor=SURF, linewidth=2, zorder=3, label='Market: raw monthly reading')
ax.axhline(100, color=INK2, lw=1, ls=(0, (4, 3))); ax.text(x[0], 102.5, 'Normal home advantage with crowds = 100', color=INK2, fontsize=9, va='bottom')
ax.text(x[-1] + pd.Timedelta(days=8), 100 * M.kf.iloc[-1] + 2, f'Market {100*M.kf.iloc[-1]:.0f}', color=INK, fontsize=9.5, va='center'); ax.text(x[-1] + pd.Timedelta(days=8), 100 * M.flat.iloc[-1] - 2, f'Learner {100*M.flat.iloc[-1]:.0f}', color=INK, fontsize=9.5, va='center')
ax.set_ylim(0, 125); ax.set_xlim(x[0] - pd.Timedelta(days=10), x[-1] + pd.Timedelta(days=50)); ax.yaxis.grid(True, color=GRID, lw=0.8); ax.set_axisbelow(True)
for s in ['top', 'right', 'left']: ax.spines[s].set_visible(False)
ax.spines['bottom'].set_color(GRID); ax.tick_params(colors=INK2, length=0); ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2)); ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
ax.set_ylabel('Home advantage behind closed doors (normal = 100)', color=INK2)
fig.suptitle('The market held near 60. Results pointed lower, but never decisively', x=0.065, y=0.97, ha='left', fontsize=14, fontweight='bold', color=INK)
ax.set_title('18 European leagues, 7,240 closed-door matches. Market line is read from prices alone. Learner sees only earlier results.', loc='left', fontsize=9.5, color=INK2, pad=10)
leg = ax.legend(loc='lower left', frameon=False, fontsize=9, ncol=2, handlelength=1.6, bbox_to_anchor=(0, -0.26)); [t.set_color(INK2) for t in leg.get_texts()]
fig.subplots_adjust(left=0.07, right=0.97, top=0.86, bottom=0.2); fig.savefig('work/fig_learning.png', facecolor=SURF)
