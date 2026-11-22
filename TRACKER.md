# Tracker: what has been explored, what has not, and where each line ended

Question: what impact do fans in stadiums really have, and does the betting market price it?
Last updated 17 Nov 2026, evening. Full numbers are in `results/FINDINGS.md`. Code and outputs are in `pipeline/`.

Status key
- RESULT: holds up, worth writing about
- PRICED: effect exists and the market already has it
- DEAD END: tested properly, nothing there
- UNCONFIRMED: a hint that did not reach the bar
- OPEN: not tested, with the reason

## Where the project stands

1. Closing a stadium removes about half of home advantage (52, interval 36 to 67). Confirmed by an independent re-derivation from raw files (54).
2. It behaves like a switch: a few hundred fans restored about as much as several thousand, across 29 leagues. Gate size within the normal range does nothing.
3. Both channels moved: the home side's card advantage vanished, its shot advantage halved in step with goals.
4. The market priced the closure at about 60, held that view like a learner with a few thousand matches of prior weight, and could not be beaten.
5. Clubs do not differ in home advantage beyond a small spread the market already prices.
6. No live edge in match odds. Five apparent edges have now failed confirmation.

## A. Does the crowd change the match?

| # | Line of attack | Outcome | Status | Output file |
|---|---|---|---|---|
| A1 | Home advantage with and without crowds, 18 leagues | Removed about 48% (model), market priced 39% | RESULT | `model_out.txt` |
| A2 | Cards and fouls with and without crowds, England | Away-minus-home yellows 0.35 to -0.02, fouls 0.56 to -0.45 | RESULT | `mech_out.txt` |
| A3 | Referee-specific home bias | Real for fouls, persists with crowds, vanishes without (1.6 SE apart) | UNCONFIRMED | `mech_out.txt` |
| A4 | First half against second half, by half-time score | Loss concentrated when the home side is level or behind. Dose check did not back it | UNCONFIRMED | `extra_out.txt` |
| A5 | Crowd size within a club-season, results | Nothing with clean measures | DEAD END | `extra_out.txt` |
| A6 | Crowd size within a club-season, cards and fouls | Nothing (largest t = 1.25 over all games) | DEAD END | `cards_dose_out.txt` |
| A7 | Partial crowds of about 2,000 in 2020/21 | Home advantage looks restored (101, interval 57 to 145). Too wide to claim | UNCONFIRMED | `model_out.txt` |
| A9 | Dose curve, 29 leagues, 1,649 crowd matches (plan written first) | Step shape passes. Small crowds about 1.0 of normal, closed 0.48. Bands wide. Same-months check weaker | RESULT | `dose_out.txt` |
| A10 | Shots, corners, cards and fouls with and without crowds, all leagues | Shots and corners halve with goals. Cards vanish, fouls reverse | RESULT | `rederive_out.txt` |
| A11 | Club-specific true home advantage | Priced spread 8% of home advantage. Extra true spread not detectable (upper bound 32%) | DEAD END beyond what is priced | `clubs_expl.txt` |
| A12 | Stadium features | Not pursued: no club differences left to explain (A11). Moves too few to test truth | DEAD END by design | NEXT_PHASE_PLAN |
| A13 | VAR and true home advantage | Exploration -31%, confirmation no change | UNCONFIRMED | `var_confirm_out.txt` |
| A8 | Home advantage since fans returned | 86 against a 2015 to 2019 norm of 100 (76 to 97). Continues a decline that started before Covid | RESULT | `model_out.txt` |

## B. Is it priced in closing match odds?

| # | Line of attack | Outcome | Status | Output file |
|---|---|---|---|---|
| B1 | Referee identity (pre-registered, hold-out run once) | +0.004 (se 0.013). Rule lost 4.2% | PRICED | `edge_hold.txt` |
| B2 | Empty stadiums, England | Away backers +10.3%. Looked like an edge | Superseded by B3 | `ghost_out.txt` |
| B3 | Empty stadiums, 16 more leagues | -3.2% at Pinnacle, +0.9% at best price. Leagues differ no more than chance | DEAD END as an edge | `closures_out.txt` |
| B4 | Later closures 2021 to 2024 (pre-registered) | +6.4%, one-sided p = 0.0495, carried by one league | UNCONFIRMED | `closures_out.txt` |
| B5 | Hierarchical model of the market's error, 7,240 closed-door games | Market over-rated home sides with probability about 0.90. Size is inside ordinary season noise (2 of 12 normal seasons missed by more) | DEAD END as an edge, RESULT as a measurement | `model_out.txt`, `model_checks.txt` |
| B6 | Real-time learner against the price | Log loss no better (t = -0.1). 2,776 bets returned -0.4% | DEAD END | `model_out.txt` |
| B14 | "Mispriced, then corrected", three criteria fixed first | C1 mispricing: anytime-valid p = 0.095 (0.17 without England). C2 correction: raw priced path did not move between autumn and spring (-0.009, se 0.049). C3 fails with them | DEAD END as a claim | `learn_out.txt`, `market_path.txt` |
| B15 | Market as a learner: implied prior weight | Opening view about 0.67 of normal with the weight of about 5,300 matches (plausible range 2,600 to 16,000). A results-only learner does not fit the market's path | RESULT | `market_path.txt` |
| B16 | Could a different weight on results have predicted better? | No. Every learner is within 1 log unit of the market over 7,240 matches, intervals about plus or minus 4 | RESULT (cannot fault the market's weight) | `learn_out.txt` |
| B17 | Do the market's real-time revisions of home advantage carry the right weight? | Yes in ordinary seasons: 0.97 (se 0.33) where 1 is correct. An apparent -2.1 was a fixed-effects bias | PRICED | `kappa_clean.txt` |
| B18 | Club home-advantage mispricing, pre-registered hold-out | Slope +0.70 (se 0.81), p = 0.19 | DEAD END | `clubs_hold.txt` |
| B19 | Overall club mispricing (secondary in the same test) | Carried forward, slope 0.86, p = 0.039 | OPEN LEAD, outside the question | `clubs_hold.txt` |
| B20 | VAR: market under-reaction | Exploration t = -3.1. Confirmation on 5 new leagues p = 0.57 | DEAD END | `var_confirm_out.txt` |
| B21 | VAR: market's priced home advantage | Cut by 5 to 8% in both samples | RESULT | `var_confirm_out.txt` |
| B22 | Small crowds against price | Priced 0.78, achieved about 0.97. 1.4 SE | UNCONFIRMED | `dose_out.txt` |
| B23 | Independent re-derivation of the headline | Goals 0.54, prices 0.59 to 0.61 | RESULT | `rederive_out.txt` |
| B24 | Prior-weight figure, simulation check | Unbiased, accurate to a factor of 2 | RESULT | `prior_weight_sim.txt` |
| B13 | Model verification: recovery, power, peeking, de-vig, draw width | Unbiased, intervals honest. Can detect a gap of -0.06, not -0.03 | RESULT | `model_verify.txt` |
| B7 | Crowd size against club norm | Apparent t = -3.3 was a look-ahead artefact | DEAD END | `extra_out.txt` |
| B8 | Travel distance, derbies, midweek, away fan base | Nothing at the close | DEAD END | `ab_expl.txt` |
| B9 | Kick-off slot | Nothing | DEAD END | notes |
| B10 | Home slumps, relegation pressure, ghost placebo | Nothing | DEAD END | `pressure_out.txt` |
| B11 | First season in a new stadium, England | +0.059 (se 0.056), 181 games | DEAD END, small sample | `stadium_moves_england.txt` |
| B12 | Home sides in local games at the close | Championship only, not in the Premier League or the older sample | DEAD END | `local_home_england.txt` |

## C. Is it priced in the early price?

| # | Line of attack | Outcome | Status | Output file |
|---|---|---|---|---|
| C1 | Travel distance and line movement | t = 10 to 2020. Hold-out t = 3.4 but no longer beats the close | PRICED now. RESULT as history | `linemove_rule_hold.txt` |
| C2 | Attendance, away fan base, midweek and line movement | Nothing once distance is in | DEAD END | `linemove_expl.txt` |
| C3 | Empty stadiums, opening against closing | Opening price was further out. Same verdict as B3 | DEAD END | `ghost_out.txt` |

## D. Other prices

| # | Line of attack | Outcome | Status | Output file |
|---|---|---|---|---|
| D1 | Betfair Exchange against Pinnacle, 2024/25 on | Same information, book 100.6% against 103.3% | RESULT (sets the bar at 1 to 2 points) | `exchange_out.txt` |
| D2 | Crowd features against the exchange price | Nothing | DEAD END | `exchange_out.txt` |

## E. Not explored, and why

| Line | Why not | What it would need | My honest odds |
|---|---|---|---|
| Half-time and in-play prices by game state | No public in-play prices | Betfair historical data, free tier is last traded price each minute | Low. About 780 relevant games gives a t of 2 at best, and A4 has no dose support |
| Bookings and card markets | No historical card odds | A forward recorder for several weeks | Low for a crowd edge. A6 shows no live crowd variation in cards |
| Real stadium noise | No public dataset | Broadcast audio processed match by match | Unknown. The only route that tests noise itself instead of attendance. Heavy |
| Punishment closed-door games since 2012 | About 40 minutes of scraping, blanks need checking by hand | Transfermarkt full history | Low. Would double B4 and still leave an even chance of detecting the effect seen |
| Overall club mispricing (B19) | Outside the crowd question | Existing data | Moderate. Only result in the project to carry forward out of sample |
| VAR with more leagues | Dates for most other leagues could not be cross-checked | League-by-league sources | Low. Five-league confirmation was flat |
| Persistent season-level market error in home advantage | Worked out the power first: expected gain is under half the standard error on 80,000 games | Nothing more to pull | Not worth running |
| Away-fan bans (France, Italy, Argentina) | No clean list of affected matches | Hand-built list | Unknown, small samples |
| Stadium moves across Europe | England sample was null and tiny | List of about 25 moves | Low. Around 400 games cannot detect a 25% change |
| Safe standing rollout | Few clubs, staggered | Dates by club | Low |

## F. Corrections to my own earlier claims

Kept here so nothing gets quietly rewritten.

1. "Away sides were underpriced in empty stadiums" (afternoon). The Premier League figure was the top of a noisy spread across 18 leagues. Shrunk estimate is about a third of the raw one.
2. "The shortfall is t = -2.4 across 18 leagues" (Result 7). Overstated. That baseline ignored favourite-longshot bias. Properly calibrated it is 1.6 standard errors, and 1.3 once ordinary season noise is added.
3. "The market learned within six months." Not established. Early against late differ by about 1.6 standard errors on a split chosen after seeing the data.
4. "Big gates predict worse home results" (first pass, t = -3.3). Look-ahead artefact. Caught the same hour.
5. Sample B "passes the pre-set bar". True by the letter (p = 0.0495). Not trusted, for the reasons in Result 7.
6. In real time the learner hit 99% confidence that home sides were over-rated in February 2021 (sampling error only). It then faded, and betting on it lost 0.4%. A warning about acting on a running test.
7. "The closed-door miss was ordinary" (evening). Half right. The final figure is ordinary (2 of 12 normal seasons missed by more). The running peak of 0.99 in February 2021 is not: under an ordinary-season market that happens in about 3% of seasons. Evidence for a temporary gap is moderate, not nil. The base model holds delta constant, so it cannot tell.
8. The market line on the first learning chart was wrong in its month-to-month detail. It came from team strengths fitted on the whole season's prices, and prices after a match react to its result. Replaced by a Kalman filter that only ever uses earlier prices. The level (about 60) did not change.
9. "The market's revisions of home advantage carry no information" (briefly, -0.72 then -2.07, five standard errors from correct). Wrong twice over. First the same leak as item 8. Then a fixed-effects bias: demeaning within a season uses future values of a regressor that reacts to past results. Without fixed effects the answer is 0.97 (se 0.33). No anomaly.
10. "The market cut its estimate from 66 to 58" (filtered path). Half artefact. The filter lags a sudden move by about two months. The raw monthly reading shows a winter dip to 56 and a return to 62, with no net change between autumn and spring.
11. "VAR made the market under-price home advantage" (17 Nov, t = -3.1 on 7 leagues). Failed on 5 new leagues (p = 0.57). Half the exploration effect came from the EFL comparison group, which had a pre-trend.
12. "The mechanism runs through the referee" (16 Nov summary). Too strong. Cards and fouls collapse without crowds, but shots halve too. Both channels move.
13. Transfermarkt records some closed-door matches with token gates (5, 50, 100 for officials and guests). Code had counted any number as a crowd. Affected 5 of 583 partial-crowd matches in earlier results. Gates of 100 or fewer now count as closed.
14. Document and code disagreements found in the 16 Nov audit (two intervals for one number, an old chart overwriting the new one, stale method notes). All seven fixed.

## G. Data held

- Results, cards, fouls, half-time scores, Pinnacle open and close: 18 leagues, 2012/13 to January 2026 (`pipeline/fd`, `pipeline/fd2`)
- Attendance and referee: Premier League and Championship 2012 to 2026 (`pipeline/tm`). Other leagues 2020/21 and most of 2021/22, Greece 2023/24 (`pipeline/tm2`)
- Betfair Exchange closing prices: 2024/25 on only
- Market's real-time priced home advantage and team strengths for every match, from prices alone (`pipeline/work/kf.pkl`, built by `kf.py`)
- Gaps: no in-play prices, no card odds, no noise data, no attendance outside England before 2020, Turkey, Greece and Spain 2021/22 attendance not scraped

## H. Rules being followed

- Write the rule down before looking, where a hold-out is involved. Run each hold-out once.
- Separate "does it predict the residual against the fair price" from "does it make money at the odds offered".
- Any hint gets one confirmation on data it was not found on before it is believed.
- Work out the power before pulling more data.
- Anything built from prices that sit later in time than the match is treated as leaking results until shown otherwise.
- No fixed effects on a regressor that reacts to past results.

## I. Paper

Paper written 17 Nov 2026: "What are fans worth? Home advantage, crowds and how the betting market priced their absence" (`results/What_are_fans_worth_Joseph_Mace.pdf`). Eight sections plus a methods appendix, two charts drawn from the result rows.
