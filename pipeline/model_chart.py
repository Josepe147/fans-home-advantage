"""Figure: home advantage in closed-door games as priced by the market and as estimated in real time by the model."""
import pandas as pd, numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt, matplotlib.dates as mdates
A, B = 0.00001, 1.05632; NOISE = float(open('work/season_noise_sd.txt').read())
T = pd.read_csv('work/model_track.csv', parse_dates=['week']); T = T[(T.week >= '2020-05-18') & (T.week <= '2021-05-31')].dropna(subset=['H_mkt'])
base = A + B * T.H_pre; mkt = 100 * (A + B * T.H_mkt) / base; mod = 100 * (A + B * T.H_mkt + T['mean']) / base
half = 1.96 * np.sqrt(T.sd ** 2 + NOISE ** 2); lo = 100 * (A + B * T.H_mkt + T['mean'] - half) / base; hi = 100 * (A + B * T.H_mkt + T['mean'] + half) / base
INK, INK2, GRID, SURF, BLUE, ORANGE = '#0b0b0b', '#52514e', '#e4e3df', '#fcfcfb', '#2a78d6', '#eb6834'
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10})
fig, ax = plt.subplots(figsize=(9.6, 5.4), dpi=160); fig.patch.set_facecolor(SURF); ax.set_facecolor(SURF)
ax.fill_between(T.week, lo, hi, color=ORANGE, alpha=0.14, linewidth=0, label='Model, 95% interval')
ax.plot(T.week, mkt, color=BLUE, lw=2, drawstyle='steps-post', label='Priced by the market', solid_capstyle='round')
ax.plot(T.week, mod, color=ORANGE, lw=2, label='Model, updated each week from results', solid_capstyle='round')
ax.axhline(100, color=INK2, lw=1, ls=(0, (4, 3))); ax.text(T.week.iloc[0], 102.5, 'Normal home advantage with crowds = 100', color=INK2, fontsize=9, va='bottom')
ax.text(T.week.iloc[-1] + pd.Timedelta(days=5), mkt.iloc[-1], f'Market {mkt.iloc[-1]:.0f}', color=INK, fontsize=9.5, va='center')
ax.text(T.week.iloc[-1] + pd.Timedelta(days=5), mod.iloc[-1], f'Model {mod.iloc[-1]:.0f}', color=INK, fontsize=9.5, va='center')
ax.set_ylim(0, 125); ax.set_xlim(T.week.iloc[0] - pd.Timedelta(days=5), T.week.iloc[-1] + pd.Timedelta(days=42))
ax.yaxis.grid(True, color=GRID, lw=0.8); ax.set_axisbelow(True)
for s in ['top', 'right', 'left']: ax.spines[s].set_visible(False)
ax.spines['bottom'].set_color(GRID); ax.tick_params(colors=INK2, length=0)
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2)); ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
ax.set_ylabel('Home advantage, closed-door games (normal = 100)', color=INK2)
fig.suptitle('Prices sat above the model all season, but inside its range in 52 of 53 weeks', x=0.065, y=0.97, ha='left', fontsize=14, fontweight='bold', color=INK)
ax.set_title('Home advantage behind closed doors, 18 European leagues, 7,240 matches. Model sees only results before each date.', loc='left', fontsize=9.5, color=INK2, pad=10)
leg = ax.legend(loc='lower left', frameon=False, fontsize=9, ncol=3, handlelength=1.6, bbox_to_anchor=(0, -0.2)); [t.set_color(INK2) for t in leg.get_texts()]
fig.subplots_adjust(left=0.07, right=0.97, top=0.86, bottom=0.16)
fig.savefig('work/fig_base_model.png', facecolor=SURF)
print(pd.DataFrame({'week': T.week.dt.date, 'mkt': mkt.round(0), 'model': mod.round(0), 'lo': lo.round(0), 'hi': hi.round(0)}).iloc[::6].to_string(index=False))
