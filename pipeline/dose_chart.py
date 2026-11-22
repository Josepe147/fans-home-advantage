import pandas as pd, numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
B = pd.read_csv('work/dose_bands.csv')
INK, INK2, GRID, SURF, BLUE, ORANGE = '#0b0b0b', '#52514e', '#e4e3df', '#fcfcfb', '#2a78d6', '#eb6834'
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10})
fig, ax = plt.subplots(figsize=(9.6, 5.4), dpi=160); fig.patch.set_facecolor(SURF); ax.set_facecolor(SURF)
x = np.arange(len(B)); lab = ['Closed\ndoors', '101 to\n1,000', '1,001 to\n2,000', '2,001 to\n5,000', 'Over\n5,000']
ax.vlines(x - 0.08, 100 * B.lo, 100 * B.hi, color=ORANGE, lw=2, alpha=0.45, label='Results, 95% interval')
ax.scatter(x - 0.08, 100 * B['mean'], s=70, color=ORANGE, edgecolor=SURF, linewidth=2, zorder=3, label='Results: home advantage achieved')
ax.scatter(x + 0.08, 100 * B.priced, s=70, marker='D', color=BLUE, edgecolor=SURF, linewidth=2, zorder=3, label='Market: home advantage priced')
ax.axhline(100, color=INK2, lw=1, ls=(0, (4, 3))); ax.text(4.45, 102, 'Normal with\nfull crowds', color=INK2, fontsize=9, va='bottom', ha='right')
for i, r in B.iterrows(): ax.text(i - 0.16, 100 * r['mean'], f'{100*r["mean"]:.0f}', color=INK, fontsize=9.5, va='center', ha='right')
for i, r in B.iterrows(): ax.text(i, -6, f'n = {int(r.n):,}', color=INK2, fontsize=8.5, ha='center')
ax.set_xticks(x); ax.set_xticklabels(lab, color=INK2); ax.set_ylim(-12, 185); ax.set_xlim(-0.6, 4.6)
ax.yaxis.grid(True, color=GRID, lw=0.8); ax.set_axisbelow(True)
for s in ['top', 'right', 'left']: ax.spines[s].set_visible(False)
ax.spines['bottom'].set_color(GRID); ax.tick_params(colors=INK2, length=0)
ax.set_ylabel('Home advantage (normal = 100)', color=INK2)
fig.suptitle('Any crowd brought home advantage back. Size made no clear difference', x=0.065, y=0.97, ha='left', fontsize=14, fontweight='bold', color=INK)
ax.set_title('29 leagues, May 2020 to June 2021, 9,993 matches. Gate size from recorded attendance.', loc='left', fontsize=9.5, color=INK2, pad=10)
leg = ax.legend(loc='upper left', frameon=False, fontsize=9, ncol=1); [t.set_color(INK2) for t in leg.get_texts()]
fig.subplots_adjust(left=0.08, right=0.97, top=0.86, bottom=0.14); fig.savefig('work/fig_dose.png', facecolor=SURF)
