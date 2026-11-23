# What are fans worth?

Home advantage, crowd attendance and football betting prices.

This project investigates how football home advantage changed when stadiums closed and reopened, and whether closing betting prices reflected those changes. It compares results and prices across leagues using attendance records, statistical models and checks on apparent pricing signals.

## The question

Covid closed stadiums, then let crowds back in stages, so the same teams played at the same grounds with and without spectators. How much of home advantage depends on a crowd being there, does its size matter, and did closing prices adjust by the right amount?

## Three findings

**1. Without crowds, home advantage roughly halved.** In the 18-league base analysis (7,240 closed-door matches), estimated closed-door home advantage was 52% of its normal level. The 95% interval is 36% to 67% once ordinary season-to-season market error is included, or about 39% to 65% from sampling error alone. Prices implied about 61%. A separate, simpler calculation on the same raw files, with no model, gave 56% (43% to 68%).

**2. Presence seems to matter more than size.** Across 29 leagues, matches with a few hundred spectators recovered roughly as much home advantage as matches with several thousand. A step shape (no crowd against any crowd) was favoured over a steady gradient in a comparison written down before fitting. But each partial-crowd band rests on 218 to 600 matches and has a wide interval, and one pre-planned robustness check had an interval crossing zero. This does not show that crowd size or noise is irrelevant.

**3. No robust betting edge was found.** The tested historical strategies and learners showed no statistically clear improvement over their market benchmarks. Several promising signals (empty-stadium away bets, a VAR effect, club-specific home advantage) weakened or failed when checked on data they were not found on.

![Home advantage by crowd size](results/fig_dose.png)

*Estimated home advantage by recorded gate, 29 leagues, May 2020 to June 2021 (normal = 100). Orange: estimated from results, with 95% intervals. Blue: implied by prices (no interval drawn, but not free of estimation error). Bands above 100 fans are imprecise. The embedded title overstates the finding. The intended title, "Home advantage was lower without crowds. Differences between crowd sizes remain uncertain", awaits a regenerated chart.*

## Method in brief

- **Prices into probabilities.** Odds become fair win, draw and loss probabilities once the margin is removed, then two numbers per match: how strongly the market favours the home side, and how wide the draw band is (an ordered probit read backwards).
- **Calibration and pooling.** Prices are first checked against results in 51,437 normal matches, so a bias that is always present is not blamed on 2020. The market's closed-door error is estimated per league and pooled, so one lucky league cannot drive the answer.
- **What the market believed over time.** A state-space model (a Kalman filter) reads, from prices alone, the home advantage the market was pricing at each date. The market's path is then compared with a learner that updates on results.
- **Information against returns.** A factor can predict results beyond the price (information) without making money at the odds offered (returns). The two are tested separately.

Full detail: [MODEL_EXPLAINED.md](MODEL_EXPLAINED.md).

## Data and reproduction

Results and odds come from [football-data.co.uk](https://www.football-data.co.uk) season files. Attendance and referees come from Transfermarkt matchday pages. Coverage differs by analysis, so check the sample table in [results/FINDINGS.md](results/FINDINGS.md). Raw data and derived files are not included in the repository, and the licence below does not cover them.

`pip install -r requirements.txt` installs the libraries, but it does not reproduce the results by itself. Versions are not pinned, the input files must be obtained and arranged as described in [pipeline/README.md](pipeline/README.md), and the scripts must run in the order given there.

## Limitations

- **Closures came with other changes** (no away fans, travel limits, congested fixtures). Estimates cover the whole package, not the crowd alone.
- **Attendance is not noise.** Gate size is the only crowd measure.
- **Partial-crowd estimates are wide**, and the market comparison for small crowds is not established.
- **Reconstruction assumptions.** The price model's settings were fitted on four leagues using the full period, and prices are matched at date level, so the market path is not a strict pre-kick-off record.
- **Historical scope.** Strategy tests say nothing about live execution, liquidity or current prices.
- **Results only.** Using win, draw and loss, the models can detect a market error of about a quarter of home advantage, not an eighth.

## Further reading

- [results/FINDINGS.md](results/FINDINGS.md): every result, sample and robustness check
- [MODEL_EXPLAINED.md](MODEL_EXPLAINED.md): the models step by step
- [notes/RESEARCH_LOG.md](notes/RESEARCH_LOG.md): decisions, failed hypotheses and corrections
- [analysis/README.md](analysis/README.md): the original test plans, kept unchanged
- [notes/literature.md](notes/literature.md): related studies
- [pipeline/README.md](pipeline/README.md): inputs and run order

## Licence

Code is MIT licensed (see [LICENSE](LICENSE)). The licence covers this repository's code only. It does not grant any rights in football-data.co.uk or Transfermarkt data.
