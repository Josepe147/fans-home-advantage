# Pipeline

All analysis code, as run on 16 and 17 Nov 2026. Run from inside this folder with Python 3 (pandas, numpy, scipy, matplotlib).

The data folders below are not in the repo. See the main README for where to get them.

Data: `fd/` is football-data.co.uk season files. `tm/` is Transfermarkt attendance and referee per match (GB1 = Premier League, GB2 = Championship).

Run order:
1. `python build_master.py` builds `work/master.pkl` (one row per match)
2. `python mech.py` mechanism tests (cards, fouls, referee heterogeneity and persistence)
3. `python edge.py expl` then `python edge.py hold` the pre-registered referee test. The hold-out has been run once. Do not tune anything and re-run it.
4. `python ghost.py` ghost-period pricing
5. `python features_build.py` then `python explore_ab.py expl` and `python extra.py` crowd dose, away support, look-ahead check, halves
6. `python halves.py` must run before `extra.py` (it writes `work/halves.pkl`)
7. `python exchange.py` other price sources and Betfair Exchange

Round 2 (afternoon of 16 Nov):
8. `python closures.py` closed-door games across 16 more leagues. Data in `fd2/` (football-data) and `tm2/` (Transfermarkt, scraped with `tm_any.py`). Rules are in `../analysis/PLAN_closures.md`.
9. `python linemove.py expl`, then `python linemove_hold.py expl` and `python linemove_hold.py hold` line movement and travel distance. The hold-out has been run once.
10. `python pressure.py` home slumps and relegation pressure.

Model (evening of 16 Nov):
11. `python model_data.py`, then `python model.py` (optional argument: prior sd, default 0.05), `python model_checks.py`, `python model_verify.py` (simulation checks, about 3 minutes), `python model_chart.py`.
12. `python cards_dose.py` crowd size against cards and fouls.

Learning model (late evening of 16 Nov):
13. `python kf.py fit` Kalman filter on prices (about 2 minutes). Writes `work/kf.pkl`. Run `python kf.py` afterwards to reuse the fitted settings.
14. `python learn.py` and `python learn.py noEngland`, then `python market_path.py` (also redraws the figure) and `python kappa_clean.py`.
15. `traps/learn_checks.py` and `traps/leak_check2.py` are kept as the record of the two biases found. Their numbers are wrong on purpose. Do not quote them.

Round 4 (17 Nov):
16. `python rederive.py` independent check from raw files, no model.
17. `python prior_weight_sim.py` simulation check of the market's prior weight (about 10 minutes).
18. `python clubs.py expl` then `python clubs.py hold` club home advantage. The hold-out has been run once.
19. `python var_test.py` (exploration) and `python var_confirm.py` (confirmation, run once).
20. `python newleagues.py` (11 extra leagues from `fd3/`, attendance from `tm2/`), then `python dose.py` with optional `samemonths`, `england` or `noJPN`, then `python dose_chart.py`.

`reflib.py` and `features.py` are shared functions. `analysis_tm_scrape.py` and `tm_fill.py` rebuild `tm/` from Transfermarkt. Output text files are in `work/`. The write-up is `../results/FINDINGS.md`.
