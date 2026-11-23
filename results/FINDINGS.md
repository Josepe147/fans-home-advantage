# Findings

Current reference for every result in the project. Numbers come from scripts in `pipeline/` and their saved console output in `pipeline/work/` (not included in the repository, see [Code and output map](#code-and-output-map)). How each result was reached, including superseded readings, is in [`../notes/RESEARCH_LOG.md`](../notes/RESEARCH_LOG.md). The original test plans are in [`../analysis/`](../analysis/README.md).

Result numbers (Result 1 to Result 20) are kept from earlier versions of this file so that older references still resolve. A [crosswalk](#result-crosswalk) at the end lists where each one now sits.

## Contents

1. [Scope and status](#1-scope-and-status)
2. [Questions and definitions](#2-questions-and-definitions)
3. [Data and samples](#3-data-and-samples)
4. [Crowd absence](#4-crowd-absence)
5. [Crowd size](#5-crowd-size)
6. [Performance and discipline](#6-performance-and-discipline)
7. [Market pricing and learning](#7-market-pricing-and-learning)
8. [Additional investigations](#8-additional-investigations)
9. [Validation](#9-validation)
10. [Limitations, deviations and next steps](#10-limitations-deviations-and-next-steps)
11. [Code and output map](#code-and-output-map)

## 1. Scope and status

Current summary, qualified:

- **Size.** In the 18-league base analysis, estimated closed-door home advantage was 52% of its normal level (95% interval 36% to 67% including ordinary season-to-season market error, about 39% to 65% from sampling error alone). Prices implied about 61%. A separate implementation on the same raw files gave 56% (43% to 68%). See Results 11 and 15.
- **Shape.** Across 29 leagues the attendance analysis favours a presence-against-absence pattern over a gradient across crowd sizes. Partial-crowd bands are imprecise, and a same-month robustness check had an interval crossing zero. See Result 19.
- **Channels.** Without crowds the home side's card advantage disappeared and its shot advantage roughly halved, in step with goals. This rules out "home advantage is mainly referee bias with team performance unchanged". It does not split home advantage into a referee share and a team share. See Result 20.
- **Market.** The market's priced closed-door home advantage stayed near 60% of normal for the first wave. Its path resembles a Bayesian learner with a prior worth a few thousand matches. Tested learners showed no statistically clear improvement on the closing price, and a "mispriced, then corrected" hypothesis failed all three criteria set in advance. See Results 14 and 16.
- **Edges.** No robust edge was found in the tested historical strategies. Apparent signals for empty stadiums, VAR and club home advantage weakened or failed confirmation. See the [scorecard](#scorecard).

All results are historical and based on win, draw and loss. Nothing here is a live trading claim.

## 2. Questions and definitions

**Questions.** How much of home advantage depends on spectators being present? Does crowd size matter? Did closing prices reflect these changes, and how did the market's view move as evidence arrived?

**Information test.** Remove the bookmaker margin to get fair probabilities. The residual is S = (home win minus away win) minus (priced home probability minus priced away probability). If a factor predicts S, the price is missing that information, even if the margin is too large to profit from it. Some later results use a model-based residual against the calibrated price instead (see [MODEL_EXPLAINED.md](../MODEL_EXPLAINED.md)).

**Profit test.** Return on a simple rule at the odds actually offered. A factor can pass the information test and fail the profit test.

**Closing-line value.** How far the price moved in the bettor's favour between an early price and the close. It is not profit.

**Crowd regimes.** Definitions differ by analysis:

| Route | Closed doors means | Partial crowd means |
|---|---|---|
| England (`build_master.py`) | Transfermarkt page found with no attendance, 12 Mar 2020 to 28 Feb 2022. Matches with no page, June 2020 to June 2021, are treated as closed by date | Recorded attendance in 2020/21 |
| 16 other base leagues (`model_data.py`, `closures.py`) | Restart 1 May to 31 Aug 2020 by date. 2020/21 with no attendance recorded. From July 2021, runs of 5 or more blank gates within 30 days | Recorded attendance in 2020/21. From July 2021, gates under 25% of the club's median that season |
| Dose analysis (`newleagues.py`, `dose.py`) | As above, and also any recorded gate of 100 or fewer (officials and guests) | Recorded gate over 100 |
| Separate implementation (`rederive.py`) | Every match from 1 May 2020 to 30 June 2021, by date only | Not separated |

The 100-or-fewer rule is applied only in the dose route. The base model counts such matches as partial. The research log records that this affected 5 of 583 partial matches; that count has not been re-verified. Harmonising the definitions and rerunning is deferred.

**Normal = 100.** Home advantage in a regime is expressed as a percentage of the same league's home advantage in crowd matches from 2015/16 to February 2020, after calibration.

## 3. Data and samples

Sources: football-data.co.uk season files (results, match statistics, Pinnacle opening and closing odds, other bookmakers, Betfair Exchange from 2024/25) and Transfermarkt matchday pages (attendance and referee). Attendance outside England covers mainly the closure seasons. Pinnacle prices in the files end on 8 January 2026.

| Analysis | Question | Leagues | Dates | Odds needed | Crowd definition | N | Script | Status |
|---|---|---|---|---|---|---|---|---|
| Results 1, 2, 12 | Referee channel and pricing | E0, E1 | 2002 to Jan 2026 (bias history from 2000/01) | Pinnacle open and close | England route | Hold-out 4,197 | `mech.py`, `edge.py`, `cards_dose.py` | Saved output |
| Results 3, 5 | English empty-stadium pricing, exchange | E0, E1 | 2012/13 to Nov 2026 | Pinnacle, average, best, Betfair | England route | 1,075 closed (EPL 437, Championship 638) | `ghost.py`, `exchange.py` | Saved output |
| Result 4 | Gate size within club | E0, E1 | 2012/13 to Mar 2020 | Pinnacle open and close | Crowd matches | Exploration 7,255 (fewer where gate measures are missing) | `features_build.py`, `explore_ab.py`, `extra.py` | Saved output |
| Result 6 | Half-by-half | E0, E1, D1, SP1, I1, F1 | 2017/18 to 2022/23 | Pinnacle or Bet365 close | England route, date window elsewhere | 14,108 (2,837 no crowd) | `halves.py`, `extra.py` | Saved output |
| Result 7 | Closures outside England | 16 leagues in `fd2/` | 2015 to Jan 2026 | Pinnacle close | Base route | A 6,273, B 208, baseline 31,404 | `closures.py` | Saved output |
| Result 8 | Line movement | E0, E1 | Expl. to Mar 2020, hold-out from 2021/22 | Pinnacle open and close | Crowd matches | 7,255 and 4,197 | `linemove.py`, `linemove_hold.py` | Saved output |
| Results 11, 14, 16 | Base model and learning | 18 (E0, E1 and 16 in `fd2/`) | 2012/13 to Jan 2026 | Pinnacle close | Base route | 7,240 first-wave closed, 51,437 calibration | `model_data.py`, `model.py`, `kf.py`, `learn.py`, `market_path.py` | Saved output |
| Result 15 | Separate implementation | Same 18 | 2015/16 to 2026/27 | Pinnacle close, handicap line | Date only | 7,856 closed-window, 31,500 before | `rederive.py` | Rerun 23 Nov 2026 after de-duplication |
| Result 17 | Club home advantage | 18 | Expl. to Feb 2020, hold-out Aug 2021 to Jan 2026 | Pinnacle close | Crowd matches | 51,437 (2,791 club-seasons, 471 clubs), hold-out 29,001 | `clubs.py` | Saved output |
| Result 18 | VAR | 7 exploration, 5 confirmation, 4 controls | 2012 to 2025, 2020/21 skipped | Pinnacle close | Crowd matches | Season-level | `var_test.py`, `var_confirm.py` | Saved output |
| Result 19 | Dose curve | 29 (18 plus 11 in `fd3/`) | 1 May 2020 to 30 Jun 2021 | Pinnacle close | Dose route | 9,993 = 8,344 closed + 1,649 partial | `newleagues.py`, `dose.py` | Saved output |
| Result 20 | Channels | Same 18, leagues that record statistics | As Result 15 | None | Date only | 7,854 closed-window | `rederive.py` | Rerun 23 Nov 2026 |

Gaps: no in-play prices, no card odds, no noise measurements, no attendance outside England before 2020, and some 2021/22 attendance not scraped (Turkey, Greece, Spain). Calendar-year leagues (Scandinavia, Japan) are aligned with split-season leagues by start year, which is approximate.

**Exploration and hold-out.** For pre-registered tests, exploration ran to 11 March 2020 (or February 2020) and hold-outs from 2021/22 to 8 January 2026. Each hold-out was run once.

## 4. Crowd absence

### Result 11. Base model: how much home advantage was lost

`pipeline/model.py`, checks in `model_checks.py` and `model_verify.py`, method in [MODEL_EXPLAINED.md](../MODEL_EXPLAINED.md).

| Home advantage, normal with crowds = 100 | As priced | Model estimate | 95% interval |
|---|---|---|---|
| Closed doors, first wave (7,240 matches) | 61 | 52 | 36 to 67 |
| Partial crowds (583 matches) | 74 | 101 | 57 to 145 |
| Crowds, 2021/22 on | 90 | 86 | 76 to 97 |

- **Which interval.** The closed-door interval of 36 to 67 adds ordinary season-to-season market error (sd 0.010 on the latent scale) to sampling error. Sampling error alone gives about 39 to 65 (the script prints "48% removed, 35% to 61%"). Intervals do not include uncertainty in the market's priced level, which is small next to the error term.
- **Calibration.** In 51,437 crowd matches to February 2020 the market's home advantage needs no correction (a = 0.000, se 0.003). There is a mild favourite-longshot tilt (b = 1.056).
- **The market's error behind closed doors.** delta_bar = -0.020 (sd 0.014). Probability that home sides were over-rated: 0.92 from sampling error, about 0.90 once ordinary season noise is added.
- **Placebo.** The same calculation on 12 ordinary seasons gives errors from -0.028 to +0.038. Two of the twelve are larger than the closed-door error.
- **Prior.** Halving or doubling the prior width moves delta_bar between -0.016 and -0.022.
- **Real time.** Updated weekly from earlier matches only, the learner's probability that home sides were over-rated peaked at 0.99 in February 2021 and then faded. Scored out of sample it did not beat the calibrated price (log-loss difference t = -0.1). Betting every outcome where it saw value: 2,776 bets, all on away sides, return -0.4% (interval -4.8% to +4.4%).
- **Trend.** Priced home advantage fell from 0.232 in 2012/13 to 0.206 in 2019/20 and 0.180 in 2025/26, in line with a decline that started before Covid.

The base model holds the market's error constant across the closure period. Its month-by-month market line (the former `fig_base_model.png`) used team strengths fitted on whole seasons of prices, which leak later results, and is no longer part of the supported results. The time path now comes from the state-space model in Result 14.

### Result 15. Separate implementation from the raw files

`pipeline/rederive.py` imports nothing from the project and fits no model. It uses the same raw files and flags closed doors by date alone (1 May 2020 to 30 June 2021), which lets in some partial-crowd matches. Share of home advantage left, closed doors against 2015/16 to February 2020, bootstrap over league-seasons:

| Measure | Share left | 95% interval |
|---|---|---|
| Results: goal difference | 0.56 | 0.43 to 0.68 |
| Results: home win minus away win | 0.52 | 0.38 to 0.66 |
| Market: handicap line | 0.60 | 0.55 to 0.65 |
| Market: priced home minus away probability | 0.62 | 0.58 to 0.67 |

Since crowds returned (August 2021 on), results show 0.87 of the old level (0.79 to 0.94) and prices 0.90 (0.85 to 0.95).

This is a separate implementation, not independent evidence. It shares the data sources and a simpler closure definition with the main analysis. **Correction, 23 Nov 2026:** earlier versions read four leagues (Germany, France, Italy and Spain top divisions) twice, because identical files sit in both `fd/` and `fd2/`. The script now reads each file once. The figures above come from the corrected run. The earlier figures were 0.54 (0.41 to 0.67), 0.50, 0.59 and 0.61.

### Result 3. English empty-stadium pricing (discovery sample)

The first look, on England only. Backing every away team in the 1,075 closed-door matches:

| Price | Return | 95% interval | Same bet with crowds |
|---|---|---|---|
| Pinnacle close | +10.3% | -0.1% to +20.7% | -6.7% (2015 to Mar 2020) |
| Pinnacle open | +12.7% | +2.1% to +23.7% | |
| Market average close | +7.3% | -2.0% to +17.5% | -6.4% (2021/22 on) |
| Best price at close | +14.5% | +4.0% to +25.3% | -0.6% (2021/22 on) |

Information test: S = -0.040 (se 0.025) across both leagues. EPL only -0.070 (t = -1.8), EPL 2020/21 -0.112 (t = -2.5), Championship -0.020 (t = -0.6). There was no shortfall in the June to July 2020 restart (S = -0.009) or when crowds returned in 2021/22 (S = +0.001, se 0.026).

This was a discovery sample and cannot confirm itself. Result 7 placed it in a wider sample, where the Premier League figure sits at the noisy end of the spread.

### Result 7. Closures outside England

Rules in [`analysis/PLAN_closures.md`](../analysis/PLAN_closures.md), written before data outside England was examined. 16 leagues with Pinnacle odds.

| Sample | Matches | S against Pinnacle close | Back every away side, Pinnacle close | Best price |
|---|---|---|---|---|
| Crowd matches, 2015 to Feb 2020 | 31,404 | +0.012 (se 0.004) | -7.1% | -2.4% |
| England, first wave (discovery) | 1,073 | -0.040 (se 0.025) | +10.3% | +14.5% |
| A. Other 16 leagues, first wave | 6,273 | -0.008 (se 0.010) | -3.2% [-7.3, +1.0] | +0.9% |
| B. Later closures, July 2021 on | 208 | -0.087 (se 0.053) | +6.4% [-16.8, +32.2] | +12.9% |
| All closed-door matches found | 7,554 | -0.015 (se 0.009) | -1.0% [-4.9, +2.7] | +3.2% [-0.8, +7.4] |

- **Size of any shortfall.** Against the raw price, first-wave closed-door matches across 18 leagues sat about 2.5 points of supremacy below the normal baseline. Against the calibrated price in Result 11 this falls to 1.6 standard errors, and 1.3 once ordinary season noise is added. It is inside Pinnacle's margin.
- **Leagues differ no more than chance.** Q = 21.9 on 17 degrees of freedom, p = 0.19. Shrunk towards the pooled mean, the Premier League estimate is -0.025.
- **Sample B meets the pre-set rule by the letter** (one-sided p = 0.0495, positive return) **but is not treated as confirmed.** The Netherlands in winter 2021/22 carries it (76 matches, S = -0.201). Without the Netherlands S = -0.021 (se 0.068). Greece 2023/24 went the other way (+0.050, 64 matches).
- **Partial crowds in 2020/21** (506 matches, median gate about 2,000) lean the other way (S = +0.059, t = +1.7). Exploratory.

Verdict: "stadium closed, back the away side" is worth roughly 1 point of probability at most. No edge at Pinnacle. At the best available price it is about break-even, with an interval including zero.

## 5. Crowd size

### Result 19. Dose curve

`pipeline/dose.py`, plan in [`analysis/PLAN_dose.md`](../analysis/PLAN_dose.md). First-wave window, 29 leagues, 9,993 matches: 8,344 closed doors and 1,649 with a recorded crowd. Each band is estimated separately with a flat prior on a grid.

| Gate | Matches | Home advantage achieved (normal = 1) | 95% interval | Market priced |
|---|---|---|---|---|
| Closed doors | 8,344 | 0.48 | 0.37 to 0.59 | 0.62 |
| 101 to 1,000 | 383 | 1.08 | 0.54 to 1.62 | 0.74 |
| 1,001 to 2,000 | 218 | 1.02 | 0.29 to 1.75 | 0.80 |
| 2,001 to 5,000 | 600 | 0.69 | 0.20 to 1.19 | 0.79 |
| Over 5,000 | 448 | 1.20 | 0.62 to 1.78 | 0.78 |

The closed-door figure here (0.48) differs from Result 11 (0.52) because the sample, crowd definition and model differ. They are not two estimates of one quantity.

Shapes compared by leave-one-league-out log score against "crowd size makes no difference":

| Shape | Log-score gain | Bootstrap 95% over leagues |
|---|---|---|
| Step (none against any) | +3.97 | -0.40 to +8.81 |
| Saturating, full crowd = normal | +4.76 | +0.15 to +10.24 |
| Rising with log gate | +1.66 | -3.71 to +6.00 |

- **Against the criteria written first:** passes. The saturating shape beats "no difference" with an interval excluding zero, and the smallest crowd band is closer to 1 than to closed doors. The fitted half-saturation point is about 5 fans, so in practice it is a step.
- **Robustness fixed in advance:** without Japan, passes (+0.22 to +9.97). Same league-months only, same direction but the interval includes zero (-1.18 to +5.98). England alone has 106 crowd matches and cannot test it.
- **Market:** crowd matches were priced at about 0.78 of normal against an estimated 0.97, about 1.4 standard errors. Not established.
- **What it does not show:** that crowd size or noise is irrelevant. Small 2020/21 crowds were home supporters only. The result is about presence and recorded gate, not loudness.

The chart `results/fig_dose.png` shows this table. Its embedded title ("Any crowd brought home advantage back") is stronger than the intervals support. Regenerating it with a more cautious title is deferred.

### Result 4. Gate size within a club in normal seasons

A first pass found home sides doing worse than priced in front of unusually large gates (-0.031 per standard deviation, t = -3.3). It was a look-ahead artefact. The gate was measured against the club's season average, which includes later gates, and gates follow results (next home gate +1.5% after a win, -1.4% after a loss).

| Gate measured against | Slope | t |
|---|---|---|
| Club's season mean (uses later gates) | -0.031 | -3.3 |
| Club's earlier home gates only | -0.004 | -0.4 |
| Club's later home gates only | -0.048 | -4.7 |

With measures using only earlier information, no additional signal was detected: predicted uplift from away fan base, travel distance and midweek, t = -0.3. Travel distance t = -0.9, derbies t = -0.1, midweek t = +1.0. Kick-off slot was also null against Pinnacle (no saved output or script for this check is in the repository). No rule earned a hold-out run. Exploratory.

### Result 12. Gate size and referee decisions

Within a club-season, a gate one standard deviation above the club's earlier gates (about 11% larger) changes away-minus-home yellows by -0.022 (se 0.018) and fouls by -0.040 (se 0.048). The one subsample that stands out (fouls, 2021/22 on, t = -2.5) has the opposite sign to the earlier period. No marginal effect was detected. Effects smaller than about twice these standard errors cannot be ruled out.

## 6. Performance and discipline

### Result 20. Teams or referees

From `pipeline/rederive.py` (corrected run, see Result 15), all leagues that record match statistics, away minus home per match:

| Channel | Before | Closed doors | Share left | Since crowds returned |
|---|---|---|---|---|
| Shots | -2.38 | -1.19 | 0.50 | -2.38 |
| Shots on target | -0.87 | -0.48 | 0.55 | -0.82 |
| Corners | -1.03 | -0.44 | 0.43 | -0.94 |
| Fouls given against | +0.48 | -0.20 | reversed | +0.36 |
| Yellow cards | +0.31 | +0.00 | 0.01 | +0.28 |
| Red cards | +0.032 | +0.010 | 0.33 | +0.019 |
| Goal difference (for comparison) | | | 0.56 | |

- The home side's advantage in cards disappeared and the foul count reversed.
- Shot and corner advantages fell by about half, in proportion to goals.
- **Identification:** this does not split home advantage into a referee share and a team share. Decisions also change play. What it argues against is the strong claim that home advantage is mainly referee bias with team performance unchanged. If that were so, shot dominance would have stayed while results fell.
- Since crowds returned, shots are back to normal but goal difference is at 0.87 of its old level. This fits the pre-Covid decline in home advantage. It is not tested.

Earlier figures from the double-counted run were within 0.04 of these (for example shots -2.42 to -1.23, share 0.51).

### Result 1. Referee decisions in England

Away-minus-home differentials, crowd matches against closed-door matches, Premier League and Championship:

| Measure | With crowd | Closed doors |
|---|---|---|
| Yellow cards, away minus home | +0.35 | -0.02 |
| Fouls given, away minus home | +0.56 | -0.45 |
| Total yellows per match | 3.29 | 2.82 |

Referees differ in how far they favour the home side on fouls: the spread is 1.3 times what chance alone gives (permutation p = 0.002 from 2,000 shuffles). That tendency carries over from earlier seasons to later ones with crowds (slope 0.80 in exploration, 0.63 in the hold-out) and disappears in closed-door matches (-0.09). The gap is about 1.6 standard errors, so suggestive only. Referee-specific bias in yellow cards is small in modern data.

Read together with Result 20: referees changed, and so did the teams.

### Result 6. Where in the match the effect sits (exploratory)

Six leagues, 2017/18 to 2022/23, 14,108 matches, 2,837 without crowds. Change in home goal supremacy without a crowd: full match -0.167 (se 0.061), first half -0.069 (se 0.032), second half -0.097 (se 0.037).

| Home side at half-time | Change in second-half supremacy | Change in away win probability |
|---|---|---|
| Leading | -0.044 (se 0.058) | +0.8 pts |
| Level | -0.104 (se 0.049) | +2.9 pts |
| Trailing | -0.137 (se 0.057) | +6.1 pts (se 1.9) |

The leading and trailing rows differ by only about 1.1 standard errors. Controlling for the pre-match price halves the trailing figure (+3.1 pts, se 1.6). A dose check in normal crowd matches did not back it up. Outside England "no crowd" is a date window, so some of these matches had limited crowds. Treat it as a hypothesis for in-play prices, which were not available.

## 7. Market pricing and learning

### Result 2. Referee identity: no signal detected in the hold-out (pre-registered)

Plan: [`analysis/PLAN_referee_x_crowd.md`](../analysis/PLAN_referee_x_crowd.md). Hold-out, 4,197 matches, run once. Effect of one standard deviation of a referee's prior home bias on the residual against Pinnacle's close: +0.004 (se 0.013). Against the opening price +0.005. Closing line movement: zero. Bias times crowd size: no effect detected. Betting rule: 1,122 bets, -4.2% (95% interval -12.8% to +4.5%, bootstrap over individual bets).

The plan's power statement put the smallest detectable slope at about 2.6 points of home-minus-away probability per standard deviation of referee bias, and the upper end of the observed interval is about 3 points. Smaller effects would look like a null. No additional signal was detected, which is not proof that referee assignment is fully priced.

### Result 14. What the market believed, and whether it should have moved

Criteria were added to [`analysis/PLAN_closures.md`](../analysis/PLAN_closures.md) before this was run, after some related estimates had been seen (the plan says which). Code: `kf.py`, `learn.py`, `market_path.py`, `kappa_clean.py`. Figure: `results/fig_learning.png`.

**Estimating price-implied home advantage.** Each league has a hidden state: home advantage under each crowd regime and one strength per team, all random walks. Each closing price is one noisy observation. Results never enter. Four settings were fitted by maximum likelihood on four leagues using all their available matches (2012 to 2026), then applied to every league: team strength drifts by sd 0.032 a week, home advantage by 0.0027 a week, team strengths get an extra jump of sd 0.041 across breaks of more than 45 days, and one match's price has noise sd 0.079. Because the settings use the whole period, this is a retrospective reconstruction, not a strict real-time one. The reading used below includes all prices on the match date, so it can include prices from later kick-offs that day.

**What the market priced.** Raw monthly readings, as a fraction of normal home advantage: 0.59 to 0.66 from June to October 2020, 0.54 to 0.57 from December to February, 0.59 to 0.68 from March to May 2021. Average about 0.61. Most months have a standard error of 0.02 to 0.04, but August and September 2020 (few matches) are much less precise.

**What the results said.** With one fixed fraction over the period: 0.52 (sd 0.06, interval 0.40 to 0.63). A learner with no prior view, evaluated at mid-month, was at 0.28 in June 2020 and between 0.44 and 0.53 from September. The market's raw reading sat inside that learner's 95% band in 12 of 13 months. Overlapping bands are a description, not a significance test.

**The market's path as a learner.** The raw monthly path is best matched by a Bayesian learner with an opening view of 0.67 and prior sd 0.07, equivalent to about 5,300 matches of evidence (the whole first wave was 7,240). Prior sds from 0.04 to 0.10 fit nearly as well, about 2,600 to 16,000 matches. This prior is fitted to the observed path, so it describes the market. It is not a forecast the market could have used in advance. A learner driven by results alone does not fit the path.

**Could a different learner have done better?** Starting from the market's average early reading (the first three weekly readings) with any prior width from 0.03 to 0.50, the total log-score difference against the market over 7,240 matches is between -0.5 and +0.6, with weekly-bootstrap intervals of about ±4. Tested learners showed no statistically clear improvement. This covers a finite family of learners.

**"Mispriced, then corrected": the three criteria.**

| Criterion | Result | Verdict |
|---|---|---|
| C1. Mispricing, with a test valid under weekly looks | Running likelihood ratio peaks at 10.6 on 8 Feb 2021. Needs 20. Anytime-valid p = 0.095 | Fail |
| C2. Correction: market error smaller in spring 2021 than autumn 2020 | Raw priced path 0.629 then 0.620, change -0.009 (se 0.049) | Fail (see note) |
| C3. Both hold without England | C1 p = 0.174 | Fail |

C2 as first written would have passed on the filtered path under a constant truth (0.966). The plan records that the filtered path lags and the criterion was poorly specified, and scores it a fail. The C1 guarantee holds if the calibrated price is the true outcome distribution and outcomes are conditionally independent given prices.

The earlier phase estimates (-0.058 in autumn 2020, about zero in spring 2021) moved because results drifted back towards the price, not because the price moved towards the results.

**Does the market weight its own revisions correctly?** In 73,935 ordinary matches, with no fixed effects, the real-time change in priced home advantage since the start of the season carries a weight of 0.97 (se 0.33), where 1 is correct. Match-level news carries 1.03 (se 0.03). No additional signal detected. (`kappa_clean.py` section F is the supported estimate. Its earlier sections print fixed-effects versions that are biased, see the research log.)

### Result 16. The prior-weight figure, checked by simulation

`pipeline/prior_weight_sim.py`. A market that is a Bayesian learner with a known prior weight was simulated on the real fixture list (true fraction 0.52, opening view 0.67), with independent monthly reading noise (sd 0.03). The weight was then refitted by the same method. 60 simulations per setting.

| True weight | Recovered (median) | Middle 80% | Within a factor of 2 |
|---|---|---|---|
| 1,000 matches | 959 | 497 to 1,668 | 83% |
| 5,000 matches | 5,598 | 3,243 to 10,660 | 83% |
| 20,000 matches | 23,251 | 10,719 to over 5 million | 62% |

Under these assumptions the method recovers the weight without obvious bias but only to about a factor of 2, and it cannot tell 20,000 from "never updates". The conclusion is "a few thousand matches, roughly 2,500 to 15,000". This checks recovery under the simulated learner and noise model, not identification of the real market's behaviour.

### Result 5. Exchange prices

Betfair Exchange closing prices against Pinnacle, 1,413 crowd matches from 2024/25:

- Prices are very similar: correlation 0.998, mean gap 0.7 points, log loss 1.0096 against 1.0095. No difference in information was detected, which does not show they hold identical information.
- The exchange book is 100.6% against Pinnacle's 103.3%. With 2% commission deducted from each winning bet, blanket bets lose about 2 points less on the exchange (homes -0.3% against -1.8%, aways -7.6% against -9.7%). This simplifies real commission, which is charged on net market winnings, and ignores liquidity and whether the quoted price could be traded.
- Crowd features against the exchange residual (about 1,700 to 2,090 matches to November 2026) showed no signal, and their signs flipped against exploration. This period overlaps the hold-out, so it was a check on already-dead factors.

So a factor needs to be worth about 1 to 2 points to clear exchange costs. None of the tested crowd factors reached that. No exchange prices are available for the closure period.

### Result 8. Travel distance and line movement

Line movement (closing minus opening price gap) is much less noisy than results (sd 0.046 against 0.79). Rule fixed in the [closures plan addendum](../analysis/PLAN_closures.md) before the hold-out.

- **Exploration (7,255 matches to March 2020).** The line moved towards the away side in local matches and towards the home side on long trips: slope +0.0060 per sd of log distance, t = 10, in every season and both leagues, surviving team-season fixed effects. The pattern persisted at two thirds of the size in closed-door matches (t = 2.4), so it reflects travel rather than crowds.
- **Hold-out (4,197 matches, 2021/22 on, run once).** Slope +0.0028, t = 3.4. Same direction, half the size.
- **Three separate measures for the rule** (back the away side at the early price in matches under 60 km, the home side over 200 km):

| Measure | Exploration (4,179 bets) | Hold-out (2,294 bets) |
|---|---|---|
| Closing-line value, probability points | +0.31 [+0.24, +0.38] | +0.15 [+0.05, +0.26] |
| Price beaten (early odds / closing odds - 1) | +0.79% [+0.57, +1.02] | -0.10% [-0.41, +0.22] |
| Return at early odds | -2.57% [-6.80, +1.83] | -2.91% [-8.38, +2.62] |

  In exploration the away-in-local-matches leg beat the closing odds by 2.2%. On the hold-out the line still moved slightly towards the side backed, but the early odds no longer beat the closing odds, and returns were negative in both periods. The early price now carries most of the effect. Intervals are bootstraps over individual bets.
- Attendance, away fan base and midweek do not move the line once distance is included.
- A follow-up (home sides in local matches underpriced at the close, S = +0.036, se 0.020) appeared in the Championship only, not the Premier League or a 2002 to 2012 Bet365 sample. Return +0.8% (-5.7% to +7.5%). Not an edge. The script that produced this output is not in the repository.

Line movement is price movement. It is not a direct observation of who bet or why.

### Result 17. Club home advantage, priced against true

`pipeline/clubs.py`, plan in [`analysis/PLAN_clubs.md`](../analysis/PLAN_clubs.md). 51,437 crowd matches to February 2020, 2,791 club-seasons, 471 clubs. Persistent variation is read from covariances between seasons of the same club.

| Quantity | Persistent spread across clubs | Share of league home advantage |
|---|---|---|
| Home advantage the market prices | sd 0.018 | 8% |
| Home advantage the market misses | sd 0.046 (variance t = 1.2) | 20%, upper 95% bound 32% |
| Overall club mispricing (all venues) | sd 0.030 (variance t = 1.6) | |

- One club-season of results pins down its home advantage only to about ±0.39, nearly twice league home advantage, so no club ranking is produced.
- **Pre-registered hold-out, run once (29,001 matches, August 2021 to January 2026):** slope +0.70 (se 0.81, one-sided p = 0.19). Fail. The betting rule was not run.
- Secondary: overall club mispricing carried forward (slope 0.86, se 0.49, p = 0.039). Recorded as a lead outside the crowd question, not a confirmed strategy.
- The standard errors treat covariances at lags 1 to 3 as independent, though they share clubs and seasons. A joint bootstrap is future work. The plan says to skip the hold-out if the persistent variance were zero. The code does not do that, but the variance was positive, so the reported run is unaffected.

No additional persistent club signal was confirmed, so the planned study of stadium features had nothing to explain and was not pursued.

### Result 18. VAR

`pipeline/var_test.py` (exploration) and `var_confirm.py` (confirmation, run once), plan in [`analysis/PLAN_var.md`](../analysis/PLAN_var.md). Each adopting league: three seasons before against the first three with VAR, 2020/21 skipped, minus the same change in leagues that had not adopted.

| | Exploration: D1, I1, P1, SP1, F1, E0, D2 | Confirmation: N1, SUI, DNK, JPN, NOR |
|---|---|---|
| Results against the price | -0.050 (t -3.1) | +0.007 (p = 0.57) |
| Priced home advantage | -0.017 (t -2.3) | -0.012 (t -2.5) |
| Home win minus away win share, no price model | -31% | -0.004 (p = 0.43) |

- **Detected:** the market's priced home advantage fell by about 5% to 8% after VAR in both samples, gradually.
- **Not established:** that VAR cut true home advantage, or that the market under-reacted. The exploration result had a downward pre-trend against the EFL comparison group and did not replicate.
- Inference: five confirmation leagues, standard error across leagues (t on 4 degrees of freedom), shared control leagues (EFL Championship, League One, League Two, Allsvenskan). Scotland was excluded because its VAR started mid-season.
- Deviation: Norway's first VAR season (2023) falls outside the plan's adoption window of 2017/18 to 2022/23. It was included in the confirmation run. The plan is unchanged.
- Published studies reach different conclusions on whether VAR reduced home advantage (see [literature.md](../notes/literature.md)). Whether betting markets priced VAR was not found in the sources checked, but no systematic search was made.

## 8. Additional investigations

### Result 9. Home slumps and relegation pressure

Home sides that had underperformed the market in their last three home games, sides on a home losing run, and bottom-four sides in the final third of the season. No home-side measure beyond t = 1.5 against the closing price, and nothing different in closed-door matches. League position is approximated from points per game within each date, without kick-off times. Exploratory. A null here is not proof of no effect.

### Result 10. Stadium moves

Nine first seasons in a new ground in the Premier League and Championship since 2002 (181 home matches): S = +0.059 (se 0.056). Too small to say much. The script that produced this output is not in the repository.

### Result 13. Related literature

Three published studies tested how betting markets priced closed-door matches. They cover at most four leagues and mostly the first months after the 2020 restart. This project pools 18 leagues, uses a test valid under repeated looks, includes closures after June 2021 and estimates how much weight the market put on results. Its size estimate agrees with Hegarty and Whelan's, so that part is a replication on more leagues. Details and verification status: [`notes/literature.md`](../notes/literature.md).

## 9. Validation

| Check | Result | Scope |
|---|---|---|
| Recovery (`model_verify.py`, 300 simulations per setting) | Posterior mean close to the truth, 95% intervals cover it 94% to 98% of the time | Results simulated from the model on the real fixture list |
| Power | A true error of -0.06 found 99% of the time, -0.03 about 60% | Same |
| Repeated weekly looks | If the market were exactly right, the running probability touches 0.95 in 11% of seasons and 0.99 in 1%. If only as right as in an ordinary season, 15% and 3% | Same |
| Placebo seasons | Errors from -0.028 to +0.038 across 12 seasons, season-level noise sd 0.010 | Ordinary seasons |
| De-vig method | Power method gives the same delta to three decimals | |
| Draw width | Letting it scale gives k = 1.020 (p = 0.01), delta unchanged | |
| Separate implementation (Result 15) | 0.56 against the model's 0.52 | Shared data |
| Prior-weight simulation (Result 16) | Recovery to a factor of 2 | Simulated learner and noise |

These checks show the methods behave well under their own assumptions. They do not validate those assumptions against the real market.

### Scorecard

| Factor | Affects the match? | Priced? |
|---|---|---|
| Crowd present or absent | Detected: about half of home advantage | Priced at about 60 against an estimate of 52. Difference inconclusive, no edge detected |
| Crowd size, closed against a few hundred | Detected: step pattern favoured. Gradient uncertain | Small crowds priced about 0.78 against 0.97. Inconclusive |
| Club-specific home advantage | Not detected beyond a small priced spread | Hold-out failed |
| VAR | Inconclusive | Priced home advantage cut 5% to 8% (detected). Under-reaction not replicated |
| Referee identity (home bias) | Detected on fouls | No signal detected in the hold-out |
| Travel distance | Detected in line movement | Priced late until about 2020, now mostly in the early price |
| Gate size against club norm | Not detected | No signal detected |
| Away support proxies, kick-off slot | Not detected | No signal detected |
| Home slumps, relegation pressure | Not detected | No signal detected |
| Stadium moves | Not detected, small sample | No signal detected |
| Game state and crowd | Exploratory | Untested, needs in-play prices |

**Multiplicity.** Roughly 120 specifications were examined across the project. This is an informal count with no complete inventory, and most were exploratory. Only the tests with written plans were pre-specified. The results beyond t = 2.5 were the look-ahead artefact (Result 4), travel distance in line movement (confirmed on the hold-out), EPL and Ligue 1 closed-door matches (explained as the noisy end of a spread) and the trailing-at-half-time split (unconfirmed).

## 10. Limitations, deviations and next steps

### Limitations

- **Concurrent changes.** Closures came with no away fans, distancing, travel limits and congested fixtures. Estimates describe the whole package.
- **Attendance is not crowd noise.** Recorded gate is the only crowd measure.
- **Precision.** All results-based estimates use win, draw and loss. The base model can detect a market error of about a quarter of home advantage but not an eighth. Partial-crowd bands are wide.
- **Retrospective reconstruction.** State-space settings were fitted using the whole period, and the market reading includes all prices on the match date.
- **Crowd definitions differ** between the base and dose routes (section 2).
- **Data checks not done.** Attendance joins (date, score and team-name matching with ±2 day offsets) have no match-rate diagnostics. Some filters check only some outcome or odds fields. Scraped attendance may be incomplete where pages failed.
- **Features and distance.** Club coordinates are fixed (no stadium moves) and some standardisations use the full sample.
- **Historical scope.** Returns use quoted closing or opening odds, with no allowance for liquidity, limits or execution.

### Deviations from the written plans

Recorded here as later commentary. The plans themselves are unchanged.

- Referee plan: the shrinkage constant is estimated by one-way ANOVA (the first method gave a negative variance). Standard errors are the larger of cluster-robust and HC1. Foul share and total yellows were added as robustness measures after the plan was written.
- Results 4 to 6, 9 and 10 are exploration and were not pre-registered.
- Closures plan: restart matches outside England in May to August 2020 are flagged by date, not attendance, because that season was not scraped.
- Line-movement addendum: returns for each leg of the rule were added to the output after the rule was fixed. The rule was not changed.
- Learning criteria: written after some related estimates had been seen, as the plan states. C2 was poorly specified (Result 14).
- VAR plan: Norway 2023 included outside the stated adoption window.
- Clubs plan: the zero-variance skip is not implemented in code (not triggered).

### Next steps

1. Harmonise crowd definitions across routes and rerun the affected results.
2. A model using goals with handicap and totals prices could tighten intervals, most usefully for the crowd bands. The size of any gain has not been estimated.
3. The overall club mispricing lead (Result 17 secondary), outside the crowd question.
4. Real crowd-noise data, the only route that tests loudness itself. A separate study.
5. Reproducibility work: pinned environment, explicit export of figures and tables with sample counts, separate output files for variants, and checks on joins and inputs. See the research log.

## Code and output map

Saved outputs are console captures in `pipeline/work/` (git-ignored, not in the repository). Where no generating script is in the repository, it is noted.

| Result | Script | Saved output |
|---|---|---|
| 1 | `mech.py` | `mech_out.txt` |
| 2 | `edge.py expl`, `edge.py hold` | `edge_expl.txt`, `edge_hold.txt` |
| 3 | `ghost.py`, `exchange.py` | `ghost_out.txt`, `exchange_out.txt` |
| 4 | `features_build.py`, `explore_ab.py`, `extra.py` | `ab_expl.txt`, `extra_out.txt`. Kick-off slot: no script or output in repository |
| 5 | `exchange.py` | `exchange_out.txt` |
| 6 | `halves.py`, `extra.py` | `halves_out.txt`, `extra_out.txt` |
| 7 | `closures.py` | `closures_out.txt` |
| 8 | `linemove.py`, `linemove_hold.py` | `linemove_expl.txt`, `linemove_rule_hold.txt`. Local-home follow-up `local_home_england.txt`: no script in repository |
| 9 | `pressure.py` | `pressure_out.txt` |
| 10 | No script in repository | `stadium_moves_england.txt` |
| 11 | `model_data.py`, `model.py`, `model_checks.py`, `model_verify.py` | `model_out.txt`, `model_checks.txt`, `model_verify.txt` |
| 12 | `cards_dose.py` | `cards_dose_out.txt` |
| 14 | `kf.py`, `learn.py`, `market_path.py`, `kappa_clean.py` | `learn_out.txt`, `market_path.txt`, `kappa_clean.txt`. Figure `results/fig_learning.png` |
| 15, 20 | `rederive.py` | `rederive_out.txt` (rerun 23 Nov 2026) |
| 16 | `prior_weight_sim.py` | `prior_weight_sim.txt` |
| 17 | `clubs.py expl`, `clubs.py hold` | `clubs_expl.txt`, `clubs_hold.txt` |
| 18 | `var_test.py`, `var_confirm.py` | `var_confirm_out.txt` |
| 19 | `newleagues.py`, `dose.py`, `dose_chart.py` | `dose_out.txt`, `dose_bands.csv`. Figure `results/fig_dose.png` |

### Result crosswalk

| Result | Section |
|---|---|
| 1 | 6 Performance and discipline |
| 2 | 7 Market pricing |
| 3 | 4 Crowd absence |
| 4 | 5 Crowd size |
| 5 | 7 Market pricing |
| 6 | 6 Performance and discipline |
| 7 | 4 Crowd absence |
| 8 | 7 Market pricing |
| 9, 10 | 8 Additional investigations |
| 11 | 4 Crowd absence |
| 12 | 5 Crowd size |
| 13 | 8 Additional investigations |
| 14, 16, 17, 18 | 7 Market pricing |
| 15 | 4 Crowd absence |
| 19 | 5 Crowd size |
| 20 | 6 Performance and discipline |
