# Research log

This is a retrospective summary of the main research decisions, checks and corrections. Original test plans are retained separately. Detailed estimates are in [`results/FINDINGS.md`](../results/FINDINGS.md).

Most of the work took place on 16 and 17 November 2026. Dates are given only where the original notes recorded them. The original plans in [`analysis/`](../analysis/README.md) are unchanged. Where this log says a plan was written before a test, that reflects the plan's own statement and the file history, not an independent check.

## 1. Framing the question

**Initial observation.** The literature already finds that crowds affect home advantage, largely through referees. A further question had received less attention: which parts of the crowd effect betting prices already include.

**Challenge.** Three distinctions shaped the design. Imposed absence (closures, capacity caps) is a cleaner test of the crowd than voluntary absence (protests, poor turnout), which is confounded with form. "How many" differs from "how full" and from "how loud". And predicting results beyond the price (information) differs from making money at the odds (returns).

**Outcome and decision.** Use the closures as the main source of variation, measure the market's error against the price rather than build a rival rating, and test information and returns separately throughout. Crowd noise was the original interest, but no public match-level noise data was found, so attendance became the only crowd measure.

**Evidence.** [FINDINGS section 2](../results/FINDINGS.md#2-questions-and-definitions).

## 2. Expanding beyond England

**Initial observation.** In England's 1,075 closed-door matches, backing every away side at Pinnacle's close returned +10.3%, and +28.7% in the Premier League in 2020/21 (t = -2.5 on the residual). It looked like a pricing edge.

**Challenge.** The idea came from one sample, so it could not confirm itself. A plan was written before other leagues were examined (`PLAN_closures.md`), covering the same period in 16 more leagues and later closures as a confirmation sample.

**Outcome.** Across 18 leagues the shortfall was real but about a third of the English size, and leagues differed no more than chance (p = 0.19). The Premier League and Ligue 1 were the lucky end of the spread. The later-closure sample passed its rule by the letter (p = 0.0495) but rested on one league (the Netherlands) and is not trusted.

**Decision.** Report the pooled estimate, shrink league estimates towards it, and treat "back the away side when stadiums close" as worth about 1 point of probability, not an edge. Pooling across leagues became standard for the rest of the project.

**Evidence.** Results 3 and 7.

## 3. The attendance look-ahead leak

**Initial observation.** Home sides playing before unusually large gates did worse than priced (-0.031 per sd, t = -3.3), stable across leagues.

**Challenge.** The gate was measured against the club's season average, which includes later gates, and gates respond to results (next home gate +1.5% after a win, -1.4% after a loss). Splitting the measure into earlier-only and later-only gates tests this directly.

**Outcome.** All of the signal sat in the part using later gates (t = -4.7). Against earlier gates only, t = -0.4. Caught within the hour.

**Decision.** Rule adopted for the rest of the project: nothing later than the match on the right-hand side. The leaky measure is kept in the code, labelled, as a diagnostic.

**Evidence.** Result 4. `pipeline/features_build.py`, `pipeline/extra.py`.

## 4. Replacing whole-season reconstruction of the market's view

**Initial observation.** The first month-by-month path of priced home advantage, and the first chart of it, came from team strengths fitted on a whole season's prices. On that path the market appeared to cut its estimate from 66 to 58 over the season, and the market's revisions of home advantage appeared to carry no information (-0.72, five standard errors from correct).

**Challenge.** Prices after a match react to its result. A strength fitted on the whole season therefore leaks later results into earlier months. `pipeline/traps/leak_check2.py` refit each month using only prices up to that month and showed the difference.

**Outcome.** Replaced by a Kalman filter that only ever uses earlier prices (`kf.py`). The overall level (about 60) did not change. The month-to-month detail did: the raw monthly reading shows a winter dip to about 56 and a return to about 62, with no net change between autumn and spring. The filtered path lags a sudden move by about two months, which explained the apparent 66 to 58 decline.

**Decision.** Use the filter for anything that varies within a season. Retire the original base-model time chart (`model_chart.py`, former `results/fig_base_model.png`) from the supported results. It ended at Market 68 and Model 58, against the later Market 59 and Learner 52. These differ in method, time window and quantity, so they do not contradict each other directly. The old chart was not wrong on purpose. It used a method later found to leak.

**Evidence.** Result 14. [`pipeline/traps/README.md`](../pipeline/traps/README.md).

## 5. The fixed-effects correction

**Initial observation.** After the leak was removed, the revision weight was still far from 1 (-2.07) when estimated with league-season fixed effects.

**Challenge.** Demeaning within a season uses the season's later values of the regressor. When that regressor reacts to past results, this biases the estimate. A simulation with no feedback from results to prices showed the method is unbiased only when there is no feedback.

**Outcome.** Without fixed effects, splitting priced home advantage into its season-start level and the change since, the weight on the change is 0.97 (se 0.33). Nothing to exploit.

**Decision.** Rule adopted: no fixed effects on a regressor that reacts to past results. Both biased versions are kept as diagnostics (`pipeline/traps/learn_checks.py`, the earlier sections of `kappa_clean.py`).

**Evidence.** Result 14. `pipeline/kappa_clean.py` section F.

## 6. "Mispriced, then corrected"

**Initial observation.** Phase estimates of the market's error were -0.058 in autumn 2020 and about zero in spring 2021. The weekly running probability of over-rating reached 0.99 in February 2021. That suggested the market learned within about six months.

**Challenge.** The split was chosen after seeing the data, and the running probability had been checked weekly. Three criteria were added to `PLAN_closures.md` before the learning model was run. The addendum states which estimates had already been seen, so it is not a clean pre-registration.

**Outcome.** All three criteria failed. The test valid under weekly looks peaked at 10.6 against a bar of 20. The raw priced path did not move between autumn and spring (-0.009, se 0.049). Without England, p = 0.17. The phase estimates moved because results drifted back towards the price, not because the price moved. Criterion C2 as written would have passed on the lagging filtered path under a constant truth. The plan records it as poorly specified and scores it a fail.

**Decision.** Withdraw "the market learned within about six months". Report the market's path as consistent with a learner whose prior was worth a few thousand matches, and checked that figure by simulation (Result 16).

**Evidence.** Results 11, 14 and 16. `analysis/PLAN_closures.md` addendum and outcome.

## 7. The mechanism: referees or teams

**Initial observation.** In England, cards and fouls swung strongly without crowds, and referee-specific foul bias appeared to persist with crowds and vanish without. An early summary said the mechanism runs mainly through the referee.

**Challenge.** If home advantage were mainly referee bias, shot dominance should have survived closures while results fell.

**Outcome.** Across all leagues with match statistics, card advantage vanished but shot and corner advantages halved, in step with goals. Both channels moved. The data cannot split home advantage into referee and team shares, because decisions also change play.

**Decision.** Replace "mostly through the referee" with "both channels moved". Record the identification limit alongside the result.

**Evidence.** Results 1 and 20.

## 8. VAR replication

**Initial observation.** In seven leagues, results fell well below the price after VAR arrived (t = -3.1), suggesting VAR cut true home advantage and the market took several seasons to price it.

**Challenge.** A confirmation plan was written (`PLAN_var.md`) and run once on five further leagues whose VAR start dates could be cross-checked.

**Outcome.** Confirmation was flat (p = 0.57). About half the exploration effect came from the EFL comparison group, which had its own downward pre-trend. The market's priced home advantage did fall by 5% to 8% in both samples. Norway's 2023 start lies outside the plan's stated adoption window but was included. That deviation is recorded in the findings, and the plan is unchanged.

**Decision.** Report the priced cut as detected and the under-reaction as not replicated.

**Evidence.** Result 18.

## 9. Club home advantage

**Initial observation.** Some clubs might have home advantage the market misses. A feasibility check showed the market's priced club home advantage barely varies.

**Challenge.** Rankings from one season of results are mostly noise. The plan (`PLAN_clubs.md`) estimated persistent variance from covariances between seasons first and tested shrunk effects once on a hold-out.

**Outcome.** The persistent unpriced spread was not significant (upper bound 32% of league home advantage) and the hold-out failed (p = 0.19). A secondary measure, overall club mispricing at all venues, did carry forward (p = 0.039). It sits outside the crowd question and is recorded as a lead.

**Decision.** No fortress table. The planned study of stadium features was dropped because there were no detectable club differences left to explain.

**Evidence.** Result 17.

## 10. Separate implementation and simulations

**Initial observation.** The headline came from a model with several layers. A simpler calculation and simulated checks were added to test it.

**Challenge.** `rederive.py` recomputes the share of home advantage left from the raw files with simple averages and no project code. `model_verify.py` and `prior_weight_sim.py` simulate results with known answers.

**Outcome.** The simple calculation agreed with the model. On 23 November 2026 a review found that identical files for four leagues (Germany, France, Italy and Spain top divisions) sat in both data folders and were read twice. The script was fixed to read each file once and rerun. The goal-difference share moved from 0.54 to 0.56, and the channel table changed by at most 0.04. The simulations show the methods recover known values under their own assumptions.

**Decision.** Describe the simple calculation as a separate implementation on shared data, not independent evidence. Describe the simulations as conditional checks.

**Evidence.** Results 15, 16 and 20. [FINDINGS section 9](../results/FINDINGS.md#9-validation).

## 11. Stopping decisions and unavailable data

Lines not pursued, and why:

| Line | Why not | What it would need |
|---|---|---|
| Half-time and in-play prices by game state | No public in-play prices | Exchange historical data. About 780 relevant matches give a t of about 2 at best, and Result 6 has no dose support |
| Card and bookings markets | No historical card odds | A forward price recorder. Result 12 shows no crowd-size effect on cards |
| Crowd noise | No public match-level dataset | Broadcast audio processed match by match |
| Punishment closed-door matches since 2012 | Scraping and manual checking of blanks | Full Transfermarkt history. Would roughly double the later-closure sample and still have low power |
| Overall club mispricing | Outside the crowd question | Existing data |
| VAR in more leagues | Start dates could not be cross-checked | League-by-league sources |
| Persistent season-level market error | Power worked out first: expected gain under half a standard error | Nothing more available |
| Away-fan bans | No clean list of affected matches | A hand-built list |
| Stadium moves outside England | England sample null and small | A list of about 25 moves. Around 400 matches cannot detect a 25% change |
| Safe-standing rollout | Few clubs, staggered dates | Dates by club |

Data gaps: no in-play prices, no card odds, no noise data, no attendance outside England before 2020, some 2021/22 attendance not scraped.

## 12. Smaller corrections

- **Token gates.** Transfermarkt records some closed matches with gates of 5, 50 or 100 (officials and guests). Code had counted any number as a crowd. Gates of 100 or fewer are now treated as closed in the dose analysis. The earlier notes put the effect at 5 of 583 partial matches in the base model, which still uses the older definition (FINDINGS section 2).
- **Calibration.** An early "t = -2.4 across 18 leagues" ignored favourite-longshot bias. Against the calibrated price it is 1.6 standard errors, and 1.3 with ordinary season noise.
- **The closed-door miss.** The final estimate is ordinary (2 of 12 normal seasons missed by more). The running peak of 0.99 in February 2021 is less ordinary (about 3% of seasons under an ordinary-season market), so the evidence for a temporary gap is moderate, not nil. The base model holds the error constant and cannot resolve this.
- **Document audit, 16 November.** Seven document and code disagreements were found and fixed, including two intervals quoted for one number, an old chart overwriting a new one, and stale method notes.
- **Review, 23 November.** Further disagreements were found and corrected in the documentation: the state-space model has four fitted settings, not three; the "-0.10%" line-movement figure is the odds-based measure, not closing-line value; the learning figures are evaluated at mid-month; and the duplicated input in `rederive.py` (section 10).

## 13. Working rules adopted

- Write the rule down before looking where a hold-out is involved. Run each hold-out once.
- Separate "does it predict the residual against the fair price" from "does it make money at the odds offered".
- Any hint gets one confirmation on data it was not found on before it is believed.
- Work out the power before pulling more data.
- Treat anything built from prices later than the match as leaking results until shown otherwise.
- No fixed effects on a regressor that reacts to past results.

## Investigation index

| Line | Status | Evidence |
|---|---|---|
| Home advantage with and without crowds, 18 leagues | Detected | Result 11 |
| Cards and fouls with and without crowds, England | Detected | Result 1 |
| Referee-specific home bias | Suggestive (1.6 se) | Result 1 |
| First half against second half | Exploratory, unconfirmed | Result 6 |
| Gate size within club-season, results | Not detected (leak caught) | Result 4 |
| Gate size within club-season, cards and fouls | Not detected | Result 12 |
| Partial crowds of about 2,000 | Inconclusive (wide) | Result 11 |
| Dose curve, 29 leagues | Step pattern favoured, gradient uncertain | Result 19 |
| Shots, corners, cards with and without crowds | Detected | Result 20 |
| Club home advantage beyond priced spread | Not detected | Result 17 |
| VAR and true home advantage | Inconclusive | Result 18 |
| Home advantage since crowds returned | Detected (about 86 of normal) | Result 11 |
| Referee identity in prices | No signal detected | Result 2 |
| Empty stadiums, England | Discovery, superseded | Result 3 |
| Empty stadiums, 16 more leagues | No edge | Result 7 |
| Later closures | Inconclusive | Result 7 |
| Real-time learner against the price | No improvement | Result 11 |
| Mispriced, then corrected | Failed criteria | Result 14 |
| Market's implied prior weight | A few thousand matches | Results 14, 16 |
| Revision weights | No signal detected | Result 14 |
| Overall club mispricing | Open lead | Result 17 |
| VAR, market under-reaction | Not replicated | Result 18 |
| VAR, priced home advantage | Detected | Result 18 |
| Small crowds against price | Inconclusive | Result 19 |
| Separate implementation | Agrees (shared data) | Result 15 |
| Travel distance and line movement | Detected, now mostly in early price | Result 8 |
| Travel, derbies, midweek, away fan base at the close | Not detected | Result 4 |
| Kick-off slot | Not detected (no saved output) | Result 4 |
| Home slumps, relegation pressure | Not detected | Result 9 |
| First season in a new stadium | Not detected, small sample | Result 10 |
| Home sides in local matches at the close | Not an edge | Result 8 |
| Exchange against Pinnacle | Very similar prices, lower margin | Result 5 |
| Crowd features against exchange prices | Not detected | Result 5 |
