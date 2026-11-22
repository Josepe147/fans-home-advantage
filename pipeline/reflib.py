"""Shared functions for the referee x crowd analysis."""
import pandas as pd, numpy as np

EXPL_END = pd.Timestamp('2020-03-11')      # last crowd games before Covid
HOLD_START_SEASON = 2021                   # 2021/22 onwards
PIN_END = pd.Timestamp('2026-01-08')       # last Pinnacle price in the data

def load():
    m = pd.read_pickle('work/master.pkl')
    m = m[m.ref.notna()].copy()
    m['gap'] = m.mk_h - m.mk_a
    m['yd'] = m.AY - m.HY                  # away yellows minus home yellows
    m['fdiff'] = m.AF - m.HF               # away fouls minus home fouls
    m['S_mk'] = (m.hw - m.aw) - (m.mk_h - m.mk_a)
    m['S_pc'] = (m.hw - m.aw) - (m.pc_h - m.pc_a)
    m['S_po'] = (m.hw - m.aw) - (m.po_h - m.po_a)
    return m

def residualise(m, col):
    """Residual of col on market strength gap, within league-season, with separate intercepts by crowd status."""
    out = pd.Series(np.nan, index=m.index)
    for _, g in m.groupby(['league', 'season']):
        g = g.dropna(subset=[col, 'gap'])
        if len(g) < 50: continue
        X = np.column_stack([np.ones(len(g)), g.gap.values] + [(g.crowd == c).values.astype(float) for c in ['ghost', 'partial'] if (g.crowd == c).sum() >= 5 and (g.crowd != c).sum() >= 5])
        beta, *_ = np.linalg.lstsq(X, g[col].values, rcond=None)
        out.loc[g.index] = g[col].values - X @ beta
    return out

def shrink_k(m, rcol, mask):
    """One-way ANOVA estimate of k = within variance / between-referee variance."""
    d = m[mask].dropna(subset=[rcol])
    g = d.groupby('ref')[rcol].agg(['mean', 'count'])
    N, R = g['count'].sum(), len(g)
    grand = d[rcol].mean()
    ssb = (g['count'] * (g['mean'] - grand) ** 2).sum()
    sw = ((d[rcol] - d.ref.map(g['mean'])) ** 2).sum() / (N - R)
    n0 = (N - (g['count'] ** 2).sum() / N) / (R - 1)
    tau2 = max((ssb / (R - 1) - sw) / n0, 1e-9)
    return sw / tau2, sw, tau2

def lagged_bias(m, rcol, k, min_n=30):
    """For each match: referee's shrunk mean of rcol over full-crowd matches in earlier seasons only."""
    d = m[(m.crowd == 'full')].dropna(subset=[rcol])
    per = d.groupby(['ref', 'season'])[rcol].agg(['sum', 'count']).reset_index().sort_values(['ref', 'season'])
    per['csum'] = per.groupby('ref')['sum'].cumsum(); per['ccnt'] = per.groupby('ref')['count'].cumsum()
    seasons = sorted(m.season.unique())
    rows = []
    for ref, g in per.groupby('ref'):
        g = g.set_index('season')
        cs = g['csum'].reindex(seasons).ffill(); cc = g['ccnt'].reindex(seasons).ffill()
        # value available for season s = cumulative up to season s-1
        cs = cs.shift(1); cc = cc.shift(1)
        rows.append(pd.DataFrame({'ref': ref, 'season': seasons, 'psum': cs.values, 'pn': cc.values}))
    lag = pd.concat(rows).dropna()
    x = m[['ref', 'season']].merge(lag, on=['ref', 'season'], how='left')
    pn = x.pn.fillna(0).values; psum = x.psum.fillna(0).values
    mean = np.where(pn > 0, psum / np.maximum(pn, 1), 0.0)
    b = np.where(pn >= min_n, mean * pn / (pn + k), 0.0)
    return pd.Series(b, index=m.index), pd.Series(pn, index=m.index)

def ols(y, X, cluster=None):
    """OLS with cluster-robust (or HC1) standard errors. X includes intercept."""
    y = np.asarray(y, float); X = np.asarray(X, float)
    XtX_inv = np.linalg.inv(X.T @ X); beta = XtX_inv @ X.T @ y; e = y - X @ beta
    n, p = X.shape
    if cluster is None:
        meat = (X * e[:, None]).T @ (X * e[:, None]) * n / (n - p)
    else:
        cl = pd.factorize(cluster)[0]; G = cl.max() + 1
        Xe = X * e[:, None]; S = np.zeros((G, p)); np.add.at(S, cl, Xe)
        meat = S.T @ S * G / (G - 1) * (n - 1) / (n - p)
    V = XtX_inv @ meat @ XtX_inv
    return beta, np.sqrt(np.diag(V))
