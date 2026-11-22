# What impact do fans in stadiums really have? Findings so far

Working note, 16 Nov 2026. Every number here comes from a script in `pipeline/` and an output file in `pipeline/work/`. Nothing is quoted from memory.

## The answer (updated 17 Nov 2026)

1. **Presence against absence is large.** Closing a stadium removes about half of home advantage: 52 on a scale where normal is 100 (95% interval 36 to 67), 18 leagues, 7,240 closed-door matches. An independent re-derivation from raw files with no model gives 54 (41 to 67).
2. **It behaves like a switch, not a dial.** Across 29 leagues, crowds of a few hundred restored about as much home advantage as crowds of several thousand (Result 19). Within a club in normal times, a gate 10% above or below its norm changes nothing (Results 4 and 12). The step shape passed the test set in advance. The intervals on each crowd band are wide.
3. **Both teams and referees changed.** Without crowds, home sides' card and foul advantage vanished completely, but their shot advantage halved, in step with goals (Result 20). Shots are the measure least touched by referees, so a large share of the effect runs through how the teams play, not only through decisions.
4. **The market priced it, and held its view.** Prices put closed-door home advantage at about 60 for 13 months. The market behaved like a learner whose opening view carried the weight of a few thousand matches (verified by simulation, Result 16). Results pointed to 52, never decisively, and no learner could beat the closing price. "Mispriced, then corrected" failed all three criteria fixed in advance.
5. **Clubs do not differ in home advantage beyond what is priced** (Result 17). The market prices a small spread between clubs (about 8% of home advantage). Any extra true spread is too small to detect, and a pre-registered out-of-sample test failed.
6. **No live edge in match odds.** Two more apparent edges failed confirmation today: VAR (Result 18) and club home advantage. `TRACKER.md` lists every line tried.

## The question, asked the way a betting syndicate would ask it

The academic literature already answers "do crowds matter?" (yes, mostly through the referee). So this project asks the next question:

**Which parts of the crowd effect does the betting market already price, and which parts does it not?**

Two separate tests are used throughout, because they answer different things.

1. **Information test.** Take the fair price (bookmaker margin removed). Compute the residual S = (home win minus away win) minus (priced home probability minus priced away probability). If a factor predicts S, the price is missing that information, even if the margin is too big to profit from it.
2. **Profit test.** Return on a simple rule at the odds actually offered.

A factor can pass the first and fail the second. That still matters to a firm with its own model, because it is an input the market is not using fully.

## Data

- England, Premier League and Championship, 2000/01 to Nov 2026. 24,230 matches, 327 referees. Results, cards, fouls, half-time scores, Pinnacle opening and closing odds (2012/13 to 8 Jan 2026), Bet365, market average and best closing odds (2019/20 on), Betfair Exchange closing odds (2024/25 on). Source: football-data.co.uk.
- Attendance and referee for every match from Transfermarkt. A ghost game is a match with no attendance inside the Covid window. 1,075 ghost games (EPL 437, Championship 638).
- Germany, Spain, Italy, France top divisions 2015/16 on, results and half-time scores only, used for the half-by-half split.

Discipline: the referee test was written down before any edge test was run (`analysis/PLAN_referee_x_crowd.md`). Exploration set is 2012/13 to 11 Mar 2020. Hold-out is 2021/22 to 8 Jan 2026 and was run once.

## Result 1. The referee channel is real (Result 20 shows the teams change too)

Away-minus-home differentials, crowd games against ghost games:

| Measure | With crowd | Ghost |
|---|---|---|
| Yellow cards, away minus home | +0.35 | -0.02 |
| Fouls given, away minus home | +0.56 | -0.45 |
| Total yellows per match | 3.29 | 2.82 |

Referees differ from each other in how far they favour the home side on fouls. The spread between referees is 1.3 times what chance alone would give (permutation p = 0.002). That foul bias carries over from a referee's earlier seasons to later ones when crowds are present (slope 0.80 in exploration, 0.63 in the hold-out) and disappears in ghost games (slope -0.09). The gap between those is about 1.6 standard errors, so it is suggestive and not proven. Referee-specific bias in yellow cards barely exists in modern data.

## Result 2. Referee identity is fully priced in match odds (pre-registered, clean null)

Hold-out, 4,197 matches. Effect of one standard deviation of a referee's home bias on the residual against Pinnacle's closing price: **+0.004 (se 0.013)**. Against the opening price: +0.005. Closing line movement: zero. Bias times crowd size: nothing. Betting rule: 1,122 bets, -4.2% (95% interval -12.8% to +4.5%).

Power statement: the upper end of the interval is about 3 points of supremacy per standard deviation of referee bias. Any real effect is smaller than the bookmaker's margin. Referee assignment is not an unpriced factor in the 1X2 market.

## Result 3. When crowds vanished, English prices under-adjusted (first look, revised by Result 7)

Backing every away team in the 1,075 ghost games:

| Price | Return | 95% interval | Same bet with crowds |
|---|---|---|---|
| Pinnacle close | +10.3% | -0.1% to +20.7% | -6.7% (2015 to Mar 2020) |
| Pinnacle open | +12.7% | +2.1% to +23.7% | |
| Market average close | +7.3% | -2.0% to +17.5% | -6.4% (2021/22 on) |
| Best price at close | +14.5% | +4.0% to +25.3% | -0.6% (2021/22 on) |

Information test: S = -0.040 (se 0.025, t = -1.6) across both leagues. EPL only: -0.070 (t = -1.8). EPL 2020/21 alone: -0.112 (t = -2.5), away backers +28.7% at the close. Championship: -0.020 (t = -0.6). There was no shortfall in the June to July 2020 restart (S = -0.009). It appeared in 2020/21 and did not shrink (March to May 2021 away backers still +21.5%). When fans came back in 2021/22 there was no mispricing (S = +0.001, se 0.026).

How to read it, corrected after Result 7:
- Taken alone this looked like a 17-point swing at every price source. Result 7 shows it was the top end of a noisy spread. Across 18 leagues the shortfall was real but about a third of this size.
- The opening price was further out than the close. The market was correcting during each week.

## Result 4. Crowd size as a dose: nothing unpriced, and one trap caught

First pass looked like a find. Home teams playing in front of an unusually big gate (relative to the club's season average) did worse than priced: -0.031 per standard deviation, t = -3.3, stable across leagues.

It is a look-ahead artefact. The season average includes later games, and gates follow results (next home gate is +1.5% after a win, -1.4% after a loss). Splitting the measure settles it:

| Gate measured against | Slope | t |
|---|---|---|
| Club's season mean (uses later gates) | -0.031 | -3.3 |
| Club's earlier home gates only | -0.004 | -0.4 |
| Club's later home gates only | -0.048 | -4.7 |

All of the signal sits in the part that uses the future. With clean measures there is nothing: predicted uplift from away fan base, travel distance and midweek, t = -0.3. Travel distance t = -0.9, derbies t = -0.1, midweek t = +1.0. Kick-off slot (the "night owl" effect) was also null against Pinnacle. No rule earned a hold-out run.

## Result 5. Exchange prices

Betfair Exchange closing prices against Pinnacle, 1,413 crowd games from 2024/25:

- The two prices carry the same information. Correlation 0.998, mean gap 0.7 points, log loss 1.0096 against 1.0095.
- The exchange book is 100.6%. Pinnacle is 103.3%. After 2% commission every blanket bet loses about 2 points less on the exchange (homes -0.3% against -1.8%, aways -7.6% against -9.7%).
- Crowd features against the exchange residual (about 1,700 to 2,090 games to Nov 2026) are null and their signs flip against the exploration set. Note this period overlaps the hold-out, so it was a check on dead factors, not a search.

So "beat Pinnacle" is the wrong bar. A factor worth about 1 to 2 points clears the exchange. None of the crowd factors tested reaches that in 1X2. The football-data source has no exchange prices for the ghost period. Betfair's historical data would show whether the ghost shortfall was also there on the exchange.

## Result 6. Where in the match the crowd effect sits (new, suggestive)

Six leagues, 2017/18 to 2022/23, 14,108 matches, 2,837 without crowds. Change in home goal supremacy without a crowd:

| | Change | se |
|---|---|---|
| Full match | -0.167 | 0.061 |
| First half | -0.069 | 0.032 |
| Second half | -0.097 | 0.037 |

Second half, split by the half-time score:

| Home side at half-time | Change in second-half supremacy | Change in away win probability |
|---|---|---|
| Leading | -0.044 (se 0.058) | +0.8 pts |
| Level | -0.104 (se 0.049) | +2.9 pts |
| Trailing | -0.137 (se 0.057) | +6.1 pts (se 1.9) |

The crowd looks like it matters most when the home side needs a goal. Caveats: the difference between the leading and trailing rows is only about 1.1 standard errors. Controlling for the pre-match price halves the trailing figure (+3.1 pts, se 1.6), because the price already holds some of the adjustment. A dose check in normal crowd games (does a bigger gate help more when trailing?) did not back it up. Outside England the no-crowd flag is a date window, and some of those games had limited crowds, which weakens the contrast. Treat this as a hypothesis for in-play prices, not a result.

## Round 2, same day: four more avenues

Rules for Results 7 and 8 were written in `analysis/PLAN_closures.md` before the data was looked at.

## Result 7. Closed stadiums across Europe: a small real shortfall, and the Premier League number was luck

16 more leagues with Pinnacle odds (Germany, Spain, Italy, France top two tiers, Netherlands, Belgium, Portugal, Turkey, Greece, Scotland, League One, League Two). Closed-door games flagged from Transfermarkt attendance.

| Sample | Games | S against Pinnacle close | Back every away side, Pinnacle close | Best price |
|---|---|---|---|---|
| Normal crowd games, 2015 to Feb 2020 | 31,404 | +0.012 (se 0.004) | -7.1% (16 leagues outside England) | -2.4% |
| England, first wave (discovery) | 1,073 | -0.040 (se 0.025) | +10.3% | +14.5% |
| A. Other 16 leagues, first wave | 6,273 | -0.008 (se 0.010) | -3.2% [-7.3, +1.0] | +0.9% |
| B. Later closures, July 2021 on | 208 | -0.087 (se 0.053) | +6.4% [-16.8, +32.2] | +12.9% |
| Every closed-door game found | 7,554 | -0.015 (se 0.009) | -1.0% [-4.9, +2.7] | +3.2% [-0.8, +7.4] |

- **The shortfall is real but small.** *(Superseded by Result 11: this baseline ignored favourite-longshot bias. Against the calibrated price the shortfall is 1.6 standard errors, and 1.3 once ordinary season noise is added.)* First-wave closed-door games across all 18 leagues sit 2.5 points of supremacy below the normal baseline (t = -2.4). That is about 1.2 points of home win probability. It is inside Pinnacle's margin.
- **Leagues do not differ more than chance.** Heterogeneity test Q = 21.9 on 17 degrees of freedom, p = 0.19. The Premier League (-0.070) and Ligue 1 (-0.122) are the lucky end. Ligue 2 (+0.074) is the unlucky end. Shrunk towards the pooled mean, the Premier League estimate is -0.025.
- **Outside England the market learned within about six months.** Restart -0.025, September to November 2020 -0.034, December to February -0.009, March to June 2021 +0.021.
- **Later closures (sample B) pass the pre-set bar by a hair and I do not trust it.** One-sided p = 0.0495 and the return is positive, which is what the plan asked for. But the Netherlands in winter 2021/22 carries it (76 games, S = -0.201). Without the Netherlands S = -0.021 (se 0.068). Greece 2023/24, the closure most like a future one, went the other way (+0.050, 64 games).
- Partial crowds in 2020/21 (506 games, median gate about 2,000) lean the other way: home sides did better than priced (S = +0.059, t = +1.7). The market may have applied one blanket haircut to the whole season. Suggestive only.

Verdict: "stadium closed, back the away side" is worth roughly 1 point of probability. It does not beat Pinnacle. At the best available price it is about break-even to slightly positive, and the interval includes zero.

## Result 8. Opening to closing line: travel distance used to be priced late, and now is not

Line movement is far less noisy than results (SD 0.046 against 0.79), so this test has real power.

- Exploration (7,255 games to March 2020): the line moved towards the away side in local games and towards the home side on long trips. Slope +0.0060 per SD of log distance, **t = 10**, in every season and both leagues, and it survives team-season fixed effects. Local games under 60 km moved 0.8 points of home probability towards the away side.
- Backing the away side early in local games beat the closing price by 2.2% on average in that period. That is closing-line value, not profit: the return at early odds was still negative.
- The pattern persisted in ghost games at two thirds of the size (t = 2.4), so the market treats it as travel, not as a crowd effect.
- **Hold-out (4,197 games, 2021/22 on, run once): slope +0.0028, t = 3.4. Same direction, half the size, and the rule no longer beats the close (-0.10%, interval -0.41 to +0.22).** The early price now carries most of it.
- Nothing else moves the line: attendance, away fan base and midweek are all flat once distance is in.
- Follow-up idea killed: home sides in local games looked underpriced at the close in both samples (S = +0.036, se 0.020). It is Championship only, absent in the Premier League and absent in the 2002 to 2012 Bet365 sample. Return +0.8% with an interval of -5.7 to +7.5. Not an edge.

## Result 9. When the crowd turns: null

Home sides that had underperformed the market in their last three home games, home sides on a losing run at home, and bottom-four sides in the final third of the season. No residual against the closing price with crowds (no home-side measure beyond t = 1.5) and nothing different in ghost games.

## Result 10. Stadium moves: null, and too small to say much

Nine first seasons in a new ground in the Premier League and Championship since 2002 (181 home games). S = +0.059 (se 0.056). No sign that home sides are overpriced after a move.

## Result 11. The model: how big is the fan effect, and did prices keep up?

`pipeline/model.py`, checks in `pipeline/model_checks.py`, figure `pipeline/work/fig_base_model.png` (its market line uses the old whole-season method and is superseded by the figure in Result 14).

How it works, in three steps:
1. Every closing price is read as an ordered probit: a latent supremacy mu and a draw width c. Given de-vigged prices this inverts exactly, so each match has the market's own supremacy number.
2. Regressing mu on team-season effects leaves the home advantage the market was pricing, by league and month.
3. Results are then scored against the calibrated price with one extra parameter, delta: how far the true home supremacy sat from the priced one. Delta is pooled across leagues (each league drawn from a common mean) and updated week by week from past matches only.

What it shows:

| Home advantage, normal with crowds = 100 | As priced | Model estimate | 95% interval |
|---|---|---|---|
| Closed doors, first wave | 61 | 52 | 36 to 67 |
| Partial crowds (median about 2,000) | 74 | 101 | 57 to 145 |
| Crowds, 2021/22 on | 90 | 86 | 76 to 97 |

- **Calibration.** In 51,437 normal games the market's home advantage needs no correction (a = 0.000, se 0.003). It has a mild favourite-longshot tilt (b = 1.056).
- **The market's error behind closed doors.** Delta = -0.020 (sd 0.014). Probability that home sides were over-rated: 0.92 on sampling error alone, about 0.90 once ordinary season noise is added.
- **Placebo.** The same calculation on each of 12 ordinary seasons gives misses from -0.028 to +0.038. Two of the twelve are bigger than the closed-door miss. The market is off on home advantage by about this much in a normal year.
- **Real time.** The learner's confidence peaked at 0.99 in February 2021 and then faded. Scored out of sample it did not beat the calibrated price (log-loss difference t = -0.1). Betting every outcome where it saw value: 2,776 bets, all on away sides, return -0.4% (interval -4.8% to +4.4%).
- **Prior.** Halving or doubling the prior width moves the estimate between -0.016 and -0.022. The conclusion does not depend on it.
- **Trend.** Priced home advantage fell from 0.232 in 2012/13 to 0.206 in 2019/20 and 0.180 in 2025/26. It did not bounce back to the old level when fans returned, and the fall since 2021 is in line with the earlier trend.

Reading: the earlier "18 leagues, t = -2.4" overstated the gap, because that baseline ignored favourite-longshot bias. Properly calibrated, the closed-door period looks like an ordinary season's worth of market error. The intervals above do not include uncertainty in step 2, which is small next to delta.

Verification (`pipeline/model_verify.py`, plain-English walkthrough in `MODEL_EXPLAINED.md`):
- Simulating results on the real fixture list with a known delta, the posterior is unbiased and its 95% intervals cover the truth 94 to 98% of the time.
- Power: a true gap of -0.06 would be found 99% of the time, a gap of -0.03 only about 60%. The data cannot separate -0.03 from zero.
- Peeking: under an ordinary-season market the weekly running probability reaches 0.99 at some point in about 3% of seasons. Ours did, in February 2021. So the evidence for a temporary gap in autumn and winter 2020/21 is moderate, not nil. The base model holds delta constant and cannot resolve this. A time-varying version is the natural next model.
- De-vig method and draw-width calibration leave delta unchanged.

## Result 12. Crowd size does not move referee decisions at the margin

Within a club-season, a gate one standard deviation above the club's earlier gates (about 11% bigger) changes away-minus-home yellows by -0.022 (se 0.018) and fouls by -0.040 (se 0.048). Nothing in either league. The one subsample that looks like something (fouls, 2021/22 on, t = -2.5) has the opposite sign to the earlier period. Combined with Result 4, the referee effect is about a crowd being there at all, not about how big it is.

## Result 13. Where this sits in the literature

Full table in `notes/LITERATURE_COMPARISON.md`. Three papers have tested the pricing of closed-door games. Fischer and Haucap (Germany) and Meier, Flepp and Franck (four leagues, first weeks) find home sides over-rated early on. Hegarty and Whelan (four leagues, Asian handicap) find the market cut home advantage by about half at once and was right to discount the wild early results. None pools more than four leagues, none corrects for looking at growing data repeatedly, none covers closures after June 2021, and none measures how much weight the market put on results. Our "about half" agrees with Hegarty and Whelan. It is a replication on more leagues, not a new number.

## Result 14. The learning model: what the market believed, week by week, and whether it should have moved

Criteria were written into `analysis/PLAN_closures.md` before this was run. Code: `pipeline/kf.py`, `learn.py`, `market_path.py`, `kappa_clean.py`. Figure: `results/fig_learning.png`.

**Reading the market's mind from prices (Kalman filter).** Each league has a hidden state: home advantage under each crowd regime, and one strength per team, all random walks. Each closing price is one noisy observation, mu = H + strength_home - strength_away. The filter uses prices only, never results, and never a price later than the match. Fitted by maximum likelihood: team strength moves by 0.032 a week, home advantage by 0.003, match-specific news has sd 0.079. This replaces the fixed-effects Layer 1 for anything that varies within a season.

**What the market believed.** As a fraction of normal home advantage, raw monthly readings: 0.59 to 0.66 from June to October 2020, a dip to 0.54 to 0.57 from December to February, back to 0.59 to 0.68 from March to May 2021. Average 0.61. Each monthly reading is good to about 0.02 to 0.04.

**What the results said.** One fixed fraction over the whole period: 0.52 (sd 0.06, interval 0.40 to 0.63). A learner with no prior view swung to 0.28 after the first month and settled between 0.44 and 0.53 from September. The market's reading sat inside that learner's 95% band in 12 of 13 months.

**The market as a learner.** The market's path is best matched by a Bayesian learner whose opening view was 0.67 with a prior sd of 0.07. That is the weight of about 5,300 matches, when the whole first wave was 7,240. Prior sds between 0.04 and 0.10 fit nearly as well, so the honest range is about 2,600 to 16,000 matches. A learner driven by results alone does not fit the market's path at all. This puts a number on Hegarty and Whelan's verbal point that the market discounted the early results.

**Was that weight wrong?** Out of sample, no learner beats the market. Starting from the market's first price with any prior width from 0.03 to 0.50, the total log-score difference over 7,240 matches is between -0.5 and +0.6, with intervals of about plus or minus 4. The data cannot fault the weight the market chose.

**The three criteria for "mispriced, then corrected".**

| Criterion | Result | Verdict |
|---|---|---|
| C1. Mispricing, with a test valid under weekly looks | Running likelihood ratio peaks at 10.6 on 8 Feb 2021. Needs 20. Anytime-valid p = 0.095 | Fail |
| C2. Correction: market error smaller in spring 2021 than autumn 2020 | Raw priced path: 0.629 then 0.620, change -0.009 (se 0.049). The price did not move between the two windows | Fail |
| C3. Both hold without England | C1 p = 0.174 | Fail |

The earlier phase estimates (-0.058 in autumn, about zero in spring) came from results drifting back towards the price, not from the price moving towards the results.

**Does the market weight its own revisions correctly?** In 73,935 ordinary games, the real-time change in priced home advantage since the start of the season carries a weight of 0.97 (se 0.33), where 1 is correct. Match-level news carries 1.03 (se 0.03). Nothing to exploit.

**Two traps caught while building this.** Both produced a five-standard-error "anomaly" before being killed.
1. Team strengths fitted on a whole season's prices leak results, because prices after a match respond to it.
2. Fixed effects on a regressor that reacts to past results bias the estimate downwards.

## Round 4, 17 Nov 2026

Plans for Results 17 to 19 were written before the results: `analysis/PLAN_clubs.md`, `analysis/PLAN_var.md`, `analysis/PLAN_dose.md`.

## Result 15. Independent re-derivation of the headline

`pipeline/rederive.py` imports nothing from the project and fits no model. Closed doors is flagged by date alone (1 May 2020 to 30 June 2021), which lets in some partial-crowd matches and so, if anything, understates the drop. Share of home advantage left, closed doors against 2015/16 to Feb 2020, bootstrap over league-seasons:

| Measure | Share left | 95% interval |
|---|---|---|
| Results: goal difference | 0.54 | 0.41 to 0.67 |
| Results: home win minus away win | 0.50 | 0.35 to 0.64 |
| Market: handicap line | 0.59 | 0.54 to 0.63 |
| Market: priced home minus away probability | 0.61 | 0.57 to 0.66 |

This matches the model (52 achieved, 61 priced). Since fans returned (August 2021 on), results show 0.85 of the old level and prices 0.90.

## Result 16. The "few thousand matches" figure, verified

`pipeline/prior_weight_sim.py`. A market that really is a Bayesian learner was simulated on the real fixture list with a known prior weight, monthly reading noise of the size observed was added, and the weight was refitted by the same method.

| True weight | Recovered (median) | Middle 80% | Within a factor of 2 |
|---|---|---|---|
| 1,000 matches | 959 | 497 to 1,668 | 83% |
| 5,000 matches | 5,598 | 3,243 to 10,660 | 83% |
| 20,000 matches | 23,251 | 10,719 to over 5 million | 62% |

The method is unbiased but only accurate to about a factor of 2, and it cannot tell 20,000 from "never updates". The honest statement is: the market's opening view carried the weight of a few thousand matches, roughly 2,500 to 15,000, best guess about 5,000.

## Result 17. Club home advantage: priced against true

`pipeline/clubs.py`. 51,437 crowd matches to Feb 2020, 2,791 club-seasons, 471 clubs. For each club-season, the home-advantage surprise is the sum of its home and away residuals against the calibrated price (the opponents' strengths cancel). Persistent variation is read from covariances between seasons of the same club, because noise in different seasons is independent.

| Quantity | Persistent spread across clubs | As a share of league home advantage |
|---|---|---|
| Home advantage the market prices | sd 0.018 (se of variance small) | 8% |
| Home advantage the market misses | sd 0.046 (variance t = 1.2) | 20%, upper 95% bound 32% |
| Overall club mispricing (all venues) | sd 0.030 (variance t = 1.6) | |

- One club-season of results pins down its home advantage to about 0.39, nearly twice league home advantage. A table of "fortresses" is not supportable from results, and none is produced.
- The market raises a club's priced home advantage after a season of over-performing at home, and its priced number does not predict future surprises.
- **Pre-registered hold-out, run once (29,001 crowd matches, Aug 2021 to Jan 2026):** shrunk club effects from the exploration predicted home-advantage surprises with slope +0.70 (se 0.81, one-sided p = 0.19). Fail. The betting rule was not run.
- Secondary: overall club mispricing did carry forward (slope 0.86, se 0.49, p = 0.039). Some clubs look persistently over- or under-rated at all venues. This is outside the crowd question and is recorded as a lead, not a finding.
- Consequence: with no detectable club differences beyond the small priced spread, a cross-section of stadium features has nothing to explain. The stadium line was not pursued.

## Result 18. VAR: the market cut home advantage, but the "underpriced" result did not replicate

`pipeline/var_test.py` (exploration), `pipeline/var_confirm.py` (confirmation). VAR removes discretion on goals, penalties, straight reds and mistaken identity, and leaves everything else alone, so it is the one natural experiment in the data aimed at the referee channel. Each adopting league: three seasons before against the first three with VAR, 2020/21 skipped, minus the same change in leagues that never adopted or had not yet adopted.

| | Exploration: Germany, Italy, Portugal, Spain, France, Premier League, 2. Bundesliga | Confirmation, run once: Eredivisie, Switzerland, Denmark, J1, Eliteserien |
|---|---|---|
| Results against the price | -0.050 (t -3.1) | +0.007 (p = 0.57) |
| Priced home advantage | -0.017 (t -2.3) | -0.012 (t -2.5) |
| Win-minus-loss share, no price model | -31% | -0.004 (p = 0.43) |

- **Established:** the market cuts priced home advantage by about 5 to 8% when VAR arrives, in both samples, gradually over two to three seasons.
- **Not established:** that VAR cut true home advantage, or that the market under-reacted. The exploration result was large, but it had a downward pre-trend against the EFL and failed on new leagues. This mirrors the published disagreement: a 2025 staggered difference-in-differences study across 41 leagues finds VAR reduced home advantage, and a 2024 meta-analysis finds no reduction. As far as I can find, no published work asks whether the betting market priced it.
- Controls: EFL Championship, League One, League Two and the Allsvenskan, which never adopted VAR. Scotland was excluded because its VAR started mid-season.

## Result 19. The dose curve: a switch, not a dial

`pipeline/dose.py`, figure `results/fig_dose.png`. First-wave window only, 29 leagues (the original 18 plus Austria, Denmark, Romania, Switzerland, Japan, Poland, Russia, Sweden, Norway, Finland, Ireland), 9,993 matches, 1,649 with a crowd. Transfermarkt records some closed-door matches with token gates for officials and guests (5, 50, 100), so a gate of 100 or fewer counts as closed.

| Gate | Home advantage achieved (normal = 1) | 95% interval | Market priced |
|---|---|---|---|
| Closed doors (8,344) | 0.48 | 0.37 to 0.59 | 0.62 |
| 101 to 1,000 (383) | 1.08 | 0.54 to 1.62 | 0.74 |
| 1,001 to 2,000 (218) | 1.02 | 0.29 to 1.75 | 0.80 |
| 2,001 to 5,000 (600) | 0.69 | 0.20 to 1.19 | 0.79 |
| Over 5,000 (448) | 1.20 | 0.62 to 1.78 | 0.78 |

Shapes compared on leagues left out of the fit, against "crowd size makes no difference":

| Shape | Log score gain | Bootstrap 95% over leagues |
|---|---|---|
| Step (none against any) | +3.97 | -0.40 to +8.81 |
| Saturating, full crowd = normal | +4.76 | +0.15 to +10.24. Fitted half-saturation is 5 fans, so it is a step |
| Rising with log gate | +1.66 | -3.71 to +6.00 |

- **Against the criteria written first:** passes. The saturating step beats "no difference" with an interval excluding zero, and the smallest crowd band is near 1, not near closed doors.
- **Robustness, fixed in advance:** without Japan, passes (+0.22 to +9.97). Same league-months only, same direction but the interval includes zero (-1.18 to +5.98). England alone has 106 crowd matches and cannot test it.
- **Market:** priced crowd matches at about 0.78 of normal against an estimated 0.97. About 1.4 standard errors. Not established.
- **What it does not show:** that noise is irrelevant. Small crowds in 2020/21 were home supporters only, and often the most committed. The finding is about presence and gate size, not loudness.

## Result 20. Teams or referees? Shots halved with goals, cards vanished

From `pipeline/rederive.py`, all leagues that record match statistics, away minus home per match:

| Channel | Before | Closed doors | Share left | Since fans returned |
|---|---|---|---|---|
| Shots | -2.42 | -1.23 | 0.51 | -2.40 |
| Shots on target | -0.89 | -0.49 | 0.56 | -0.84 |
| Corners | -1.05 | -0.44 | 0.42 | -0.96 |
| Fouls given against | +0.45 | -0.19 | reversed | +0.35 |
| Yellow cards | +0.31 | +0.00 | 0.01 | +0.28 |
| Red cards | +0.032 | +0.011 | 0.36 | +0.017 |
| Goal difference (for comparison) | | | 0.54 | |

- The referee channel moved completely. The home side's advantage in cards disappeared and the foul count reversed.
- The performance channel moved by about half, the same proportion as goals. Shots are the measure least determined by referees.
- **Identification, stated plainly:** this does not decompose home advantage into a referee share and a team share. Decisions also change play: a team protected by the referee may play more aggressively. What it rules out is the strong claim that home advantage is mainly referee bias with team performance unchanged. If that were true, shot dominance would have stayed while results fell.
- Since fans returned, shots are back to normal (-2.40) but goal difference is at 0.85 of its old level. This fits the slow pre-Covid decline in home advantage. It is not tested.

## Scorecard

| Factor | Affects the match? | Priced? |
|---|---|---|
| Crowd present or absent | Yes, about half of home advantage | Priced at about 60 against a best estimate of 52. Not distinguishable, and not exploitable |
| Crowd size, closed against a few hundred | Yes, a step | Market priced small crowds at about 0.78 against 0.97. Not established |
| Club-specific home advantage | Not beyond a small priced spread | Priced. Hold-out failed |
| VAR | Unresolved | Market cut home advantage 5 to 8%. Under-reaction did not replicate |
| Referee identity (home bias) | Yes, on fouls | Fully priced in 1X2 |
| Travel distance and local games | Market thinks so | Priced late until about 2020. Now mostly in the early price |
| Crowd size against club norm | No, for results, cards and fouls | Nothing unpriced |
| Away support proxies, kick-off slot | No clean evidence | Nothing unpriced |
| Home slumps and relegation pressure | No | Nothing unpriced |
| Stadium moves | No evidence | Nothing unpriced, small sample |
| Game state times crowd | Possibly | Untested, needs in-play prices |

**No live edge in match odds.** The one gap that is firmly established was temporary: travel distance sat in the closing price but not the early price until about 2020.

About 120 tests have been run. The ones beyond t = 2.5 are the look-ahead artefact, the travel-distance line movement (confirmed on the hold-out), EPL 2020/21 ghost games (now explained as the top of a noisy spread), Ligue 1 ghost games (same) and the trailing-at-half-time split (unconfirmed).

## Deviations from the written plan

- The shrinkage constant k is estimated by one-way ANOVA. The first method gave a negative between-referee variance.
- Standard errors are the larger of cluster-robust and HC1.
- Foul share and total yellows were added as robustness measures after the plan was written.
- Results 4 to 6, 9 and 10 are exploration and were not pre-registered.
- Result 7: the May to August 2020 restart games outside England are flagged by date window, not attendance, because that season was not scraped.
- Result 8: component returns for each leg of the rule were added to the output after the rule was fixed. The rule itself was not changed.

## What I would do next

1. **Write the paper.** The argument is complete: size of the effect, its shape, its channels, the market's response and its learning, and what failed. Results 1 to 3, 11 and 14 to 20 carry it.
2. **Goals model with handicap and totals prices.** Tightens every interval by roughly a quarter. Most useful for the crowd bands in Result 19, where the intervals are widest.
3. **The overall club mispricing lead** (Result 17 secondary). Outside the crowd question, but it is the only thing in the project that carried forward out of sample.
4. **Real noise data.** Still the only route that tests loudness itself. Parked as a separate study.
