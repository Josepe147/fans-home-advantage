# Pipeline

All analysis code. Scripts were run on 16 and 17 November 2026, and `rederive.py` again on 23 November 2026 after a fix. This page describes what the code actually expects. It is not a one-command reproduction.

## Before running

1. **Environment.** Python 3 with pandas, numpy, scipy and matplotlib (`pip install -r ../requirements.txt`). Versions were not recorded or pinned, so results may differ slightly with other versions.
2. **Working folder.** Run every script from inside `pipeline/`. Scripts write to `work/` but do not create it, so first run `mkdir work`.
3. **Input data.** Not included in the repository. Expected layout:

| Folder | Contents | File names | Source |
|---|---|---|---|
| `fd/` | Season files for E0, E1, D1, SP1, I1, F1 | `<code>_<YYZZ>.csv`, for example `E0_1920.csv` for 2019/20 | football-data.co.uk |
| `fd2/` | Season files for B1, D1, D2, E2, E3, F1, F2, G1, I1, I2, N1, P1, SC0, SP1, SP2, T1 | Same pattern | football-data.co.uk |
| `fd3/` | One file per extra league: AUT, DNK, FIN, IRL, JPN, NOR, POL, ROU, RUS, SUI, SWE | `<code>.csv`, with columns `Season, Date, Home, Away, HG, AG, PSCH, PSCD, PSCA` | football-data.co.uk multi-season files. How these were downloaded is not documented |
| `tm/` | Transfermarkt matchdays, Premier League (GB1) and Championship (GB2) | `<GB1\|GB2>_<start year>.csv` | `analysis_tm_scrape.py` |
| `tm2/` | Transfermarkt matchdays, other leagues | `<Transfermarkt code>_<start year>.csv` | `tm_any.py` |

Season files use football-data.co.uk's standard columns (`Date`, `HomeTeam`, `AwayTeam`, `FTHG`, `FTAG`, `HTHG`, `HTAG`, match statistics, `PSH/PSD/PSA`, `PSCH/PSCD/PSCA` and others). Missing columns are filled as empty. Transfermarkt files have columns `season, matchday, home, away, score, date, referee, attendance`. A blank attendance means none was recorded.

Note that `fd/` and `fd2/` both contain D1, SP1, I1 and F1. Most scripts read only one of the two folders. `rederive.py` reads both and skips any file name already read from `fd/`.

## Run order

Each step lists what it reads from `work/` (other than raw data) and what it writes. The order below satisfies every dependency.

| Step | Command | Reads | Writes |
|---|---|---|---|
| 1 | `python build_master.py` | `fd/`, `tm/` | `master.pkl` |
| 2 | `python features_build.py` | `master.pkl` | `feat2.pkl` |
| 3 | `python mech.py` | `master.pkl` | `mech.pkl` |
| 4 | `python edge.py expl`, then `python edge.py hold` | `mech.pkl` | console |
| 5 | `python ghost.py` | `master.pkl` | console |
| 6 | `python explore_ab.py expl` | `master.pkl` | console |
| 7 | `python halves.py` | `master.pkl`, `fd/` | `halves.pkl` |
| 8 | `python extra.py` | `feat2.pkl`, `halves.pkl` | console |
| 9 | `python exchange.py` | `feat2.pkl`, `fd/` | console |
| 10 | `python cards_dose.py` | `feat2.pkl` | console |
| 11 | `python linemove.py expl`, then `python linemove_hold.py expl` and `python linemove_hold.py hold` | `feat2.pkl` | console |
| 12 | `python pressure.py` | `feat2.pkl` | `pressure.pkl` |
| 13 | `python closures.py` | `fd2/`, `tm2/` | `eu.pkl` |
| 14 | `python model_data.py` | `master.pkl`, `eu.pkl` | `model.pkl`, `model_all.pkl` |
| 15 | `python model.py` (optional argument: prior sd, default 0.05) | `model.pkl` | `H.pkl`, `model_track.csv`, `model_ghost.pkl` |
| 16 | `python model_checks.py` | `model.pkl` | `season_noise_sd.txt` |
| 17 | `python model_verify.py` (a few minutes) | `model.pkl`, `season_noise_sd.txt` | console |
| 18 | `python kf.py fit` (about 2 minutes) | `model_all.pkl` | `kf_par.npy`, `kf.pkl` |
| 19 | `python learn.py`, then `python learn.py noEngland` | `kf.pkl` | `learn_paths.npz` |
| 20 | `python market_path.py` | `kf.pkl` | `market_path.csv`, `fig_learning.png` |
| 21 | `python kappa_clean.py` | `kf.pkl`, `H.pkl` | console |
| 22 | `python prior_weight_sim.py` (about 10 minutes) | `kf.pkl` | console |
| 23 | `python clubs.py expl`, then `python clubs.py hold` | `kf.pkl` | `club_expl.pkl`, `club_var.pkl` |
| 24 | `python var_test.py` | `kf.pkl` | console |
| 25 | `python newleagues.py` | `fd3/`, `tm2/`, `kf.py`, `kf_par.npy` | `kf_extra.pkl` |
| 26 | `python var_confirm.py` | `kf.pkl`, `kf_extra.pkl` | console |
| 27 | `python dose.py samemonths`, `python dose.py noJPN`, `python dose.py england`, then `python dose.py` | `kf.pkl`, `kf_extra.pkl`, `eu.pkl`, `master.pkl` | `dose_bands.csv` |
| 28 | `python dose_chart.py` | `dose_bands.csv` | `fig_dose.png` |
| 29 | `python rederive.py` | `fd/`, `fd2/` only | console |

`python kf.py` with no argument reuses the saved settings in `kf_par.npy` instead of refitting.

Most results are printed to the console. The saved outputs cited in [`results/FINDINGS.md`](../results/FINDINGS.md) were captured by redirecting, for example `python mech.py > work/mech_out.txt`.

Published figures in `results/` were copied by hand from `work/fig_dose.png` and `work/fig_learning.png`. There is no export script.

## Arguments and hold-outs

- `edge.py`, `explore_ab.py`, `linemove.py`, `linemove_hold.py` and `clubs.py` need an argument. Without one they stop with an error.
- In `edge.py`, `explore_ab.py`, `linemove.py` and `linemove_hold.py`, any argument other than `expl` runs the hold-out. Type it carefully.
- Each hold-out was run once with its rule fixed in advance. Rerunning is fine for reproduction, but tuning and rerunning would invalidate it.
- `model.py`, `learn.py` and `dose.py` take optional arguments as shown above.

## Variants overwrite the baseline

- `learn.py noEngland` writes to the same `learn_paths.npz` as the baseline.
- Every `dose.py` variant writes to the same `dose_bands.csv`, which `dose_chart.py` draws. Run plain `python dose.py` last, immediately before `dose_chart.py`. The saved `dose_bands.csv` matches the baseline table in the findings.

## Historical and diagnostic scripts

- `model_chart.py` draws the original base-model time chart (`work/fig_base_model.png`). Its market line uses whole-season team strengths, which leak later results, and it hard-codes the calibration values. It is kept for the record and is not part of the supported results.
- `traps/leak_check2.py` and `traps/learn_checks.py` reproduce two biases found during development. See [`traps/README.md`](traps/README.md). Their numbers are not supported results.
- `../analysis/first_pass_epl.py` is the first exploratory look and uses a different data folder.

## Shared code and scrapers

- `reflib.py` (sample dates, regression with robust standard errors, referee-bias helpers) and `features.py` (distance, gate and occupancy features) are imported by other scripts.
- `analysis_tm_scrape.py COMP SEASONS` (for example `GB1 2019,2020`) and `tm_any.py COMP SEASONS` fetch Transfermarkt pages into `tm/` and `tm2/`. `tm_fill.py` re-fetches missing English matchdays. They need network access, are not part of the analysis run, and were not rerun for this version.
- `newleagues.py` and `tm_fill.py` load code from `kf.py` and `analysis_tm_scrape.py` by reading and executing part of those files. Changing those files can therefore change these scripts.

## Known limitations of the code

Documented, not fixed. Fixes are future work.

- **Crowd definitions differ** between the base route (`build_master.py`, `closures.py`, `model_data.py`) and the dose route (`newleagues.py`, `dose.py`), which also treats gates of 100 or fewer as closed.
- **Attendance joins** match on date and score, learn team-name mappings by vote, and in `closures.py` and `newleagues.py` try date offsets of up to two days. Unreadable lines are skipped. There are no match-rate checks.
- **Scraper coverage.** `analysis_tm_scrape.py` writes a file even if every page failed and skips files that already exist. `tm_any.py` stops after two empty matchdays and assumes a fixed number of matchdays. Gaps are possible.
- **`tm_fill.py`** fails if a 2026 season file has no rows.
- **Features** (`features.py`, `features_build.py`) include season-maximum and season-mean gates that use later matches (a labelled diagnostic), fixed club coordinates and full-sample standardisation.
- **Timing.** The filter's `H_post` reading includes all prices on the match date. Filter settings were fitted on four leagues using the whole period. Weekly cut-offs in `model.py` and `learn.py` start on 11 May 2020. In `learn.py` a closed-door match before that date would be added to the last week. Whether any such match exists has not been checked.
- **Statistics helpers.** `reflib.ols` uses a direct matrix inverse with no rank check. Optimisers are not checked for convergence. Permutation p-values in `mech.py` come from 2,000 shuffles and can print 0.
- **Labels.** `var_test.py` prints a win-minus-loss measure as "goals". `linemove_hold.py` display bands are right-closed and stop at 600 km, so they differ slightly from the rule's own boundaries. `pressure.py` ranks teams within a date without kick-off times.
- **`clubs.py hold`** does not skip the hold-out when the persistent variance is estimated at zero, as the plan says it should.
