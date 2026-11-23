# Test plans and first-pass scripts

The plans in this folder were written during the project to fix test rules before the relevant hold-out or confirmation data was used. **They are kept exactly as written.** Later commentary, including deviations, lives in [`results/FINDINGS.md`](../results/FINDINGS.md#deviations-from-the-written-plans) and [`notes/RESEARCH_LOG.md`](../notes/RESEARCH_LOG.md).

The times written inside each plan are the author's own record. File dates and Git history are not independent proof that a plan came before a result. Several plans state what had already been seen when they were written, and those statements should be read as part of the plan.

| Plan | Question | Already seen when written | Confirmation sample | Scripts | Deviations recorded later | Provenance |
|---|---|---|---|---|---|---|
| [`PLAN_referee_x_crowd.md`](PLAN_referee_x_crowd.md) | Does the closing price reflect the assigned referee's home bias? Primary yellow-card bias, secondary foul and result bias. Power statement included | Stated as written before any edge test. Literature on referee bias | Hold-out 2021/22 to 8 Jan 2026, run once | `pipeline/mech.py`, `pipeline/edge.py` | Shrinkage by one-way ANOVA. SEs the larger of cluster-robust and HC1. Foul share and total yellows added later | Self-dated 16 Nov 2026, 14:50 |
| [`PLAN_closures.md`](PLAN_closures.md) | Are closed stadiums underpriced outside England? Samples A (same period), B (later closures), C (capped crowds) | England discovery sample, stated in the plan | Sample B, July 2021 on | `pipeline/closures.py` | Restart matches outside England flagged by date | Self-dated 16 Nov 2026, 15:45 |
| `PLAN_closures.md`, addendum 16:05 | Line movement and travel distance: slope and a fixed betting rule | Exploration slope (t = 10), stated | Hold-out 2021/22 to 8 Jan 2026, run once | `pipeline/linemove.py`, `pipeline/linemove_hold.py` | Per-leg returns added to output after the rule was fixed | Self-dated |
| `PLAN_closures.md`, addendum 16:55 | Criteria C1 to C3 for "mispriced, then corrected" | Pooled error, phase estimates, running probability and the market chart, stated. The plan says it is not a clean pre-registration | Same first-wave data, scored once | `pipeline/learn.py`, `pipeline/market_path.py` | Outcome section records that C2 was poorly specified | Self-dated, outcome 17:40 |
| [`PLAN_clubs.md`](PLAN_clubs.md) | Club home advantage, priced against true | A feasibility check of priced club variation | Hold-out 1 Aug 2021 to 8 Jan 2026, run once | `pipeline/clubs.py` | The zero-variance skip is not implemented in code (not triggered in the reported run) | Self-dated 17 Nov 2026, 15:20 |
| [`PLAN_dose.md`](PLAN_dose.md) | Is the crowd effect a step or a gradient? Shapes S0 to S3, five gate bands, three robustness checks | Closed 0.52, partial 1.01 (583 matches) from the base model, stated | Leave-one-league-out, 29 leagues | `pipeline/newleagues.py`, `pipeline/dose.py`, `pipeline/dose_chart.py` | England-only check had too few crowd matches (106) to test | Self-dated 17 Nov 2026, 15:45 |
| [`PLAN_var.md`](PLAN_var.md) | Did VAR cut home advantage, and did the market price it? | Seven-league exploration, stated | Five further leagues, run once | `pipeline/var_test.py`, `pipeline/var_confirm.py` | Norway (first VAR season 2023) is outside the stated window of 2017/18 to 2022/23 but was included | Self-dated 17 Nov 2026, 16:40 |

## First-pass scripts (historical)

| File | Status |
|---|---|
| `first_pass_epl.py` | The first Premier League look, 16 Nov 2026. Reads `data/E0_<season>.csv` from a root-level `data/` folder that the main pipeline does not use, and splits crowd periods by date only. Kept as a record. Not part of the supported run |
| `scrape_transfermarkt_attendance.py` | Byte-identical to `pipeline/analysis_tm_scrape.py`, which is the copy the pipeline uses. Removing this duplicate is a possible future clean-up |
