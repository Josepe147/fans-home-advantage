# The models, explained

How the main estimates are produced, step by step, matched to the current code. Results are in [`results/FINDINGS.md`](results/FINDINGS.md). How the methods developed, including approaches that were replaced, is in [`notes/RESEARCH_LOG.md`](notes/RESEARCH_LOG.md).

## 1. Purpose

A closing price already contains the market's view of both teams and of home advantage. So the project does not build a team-strength model to compete with it. It takes the price as the strength estimate and asks a narrow question of the results: was the home edge, as priced, too big or too small when stadiums were empty?

There are two layers:

- **The base error model** (sections 2 to 6, `pipeline/model_data.py`, `model.py`): one number, delta, for how far true home supremacy sat from the calibrated price in closed-door matches, pooled across 18 leagues and held constant over the period.
- **Later extensions** (sections 7 to 9): a state-space model that reads the market's priced home advantage over time (`kf.py`), a learner that updates on results (`learn.py`, `market_path.py`), and the dose curve (`dose.py`), which reuses the same pieces.

## 2. Odds to fair probabilities

Pinnacle closing odds for home, draw and away are o_H, o_D, o_A. The implied probabilities 1/o sum to more than 1 (about 1.026). That excess is the bookmaker's margin. Dividing each by the sum gives fair probabilities p_H, p_D, p_A (proportional margin removal).

Valid inputs: all three closing odds present and above 1. Matches without a Pinnacle close are dropped from the model.

Check: removing the margin by the power method instead gives the same delta to three decimals (-0.022).

## 3. Fair probabilities to two numbers (ordered probit)

Picture each match as one hidden quantity X, the home side's performance margin on the day, normal with mean mu and standard deviation 1.

- Home win if X > c
- Away win if X < -c
- Draw in between

So p_H = Phi(mu - c) and p_A = Phi(-mu - c), where Phi is the standard normal distribution function. Writing z_H = Phi^-1(p_H) and z_A = Phi^-1(p_A):

    mu = (z_H - z_A) / 2
    c  = -(z_H + z_A) / 2

This inverts exactly for each match. Nothing is fitted. **mu** is the market's supremacy for the home side on a common scale and **c** is the half-width of the draw band. The standard deviation of X is fixed at 1, which sets the scale.

Worked match: Liverpool v Crystal Palace, 24 June 2020, closed doors. Odds 1.30 / 5.85 / 11.67. Book 102.6%. Fair probabilities 0.750 / 0.167 / 0.084. z_H = +0.674, z_A = -1.382, so mu = 1.028 and c = 0.354. For scale, an evenly matched game (0.44 / 0.29 / 0.27) has mu = 0.23 and c = 0.37. That 0.23 is home advantage.

## 4. Calibration and its uncertainty

Before judging the market in 2020, check it in 51,437 crowd matches from 2012 to February 2020. Fit

    true latent mean = a + b * mu

by maximum likelihood on results (win, draw, loss).

- a = 0.000 (se 0.003). The market's home advantage needs no correction in normal times.
- b = 1.056 (se 0.030). Strong favourites win slightly more often than priced (favourite-longshot bias). With power margin removal b falls to 1.02, so most of it comes from how the margin is removed.

Call a + b * mu the calibrated price, eta0. Later tests are against eta0. Several scripts refit a and b on their own sample (for example `learn.py` and `dose.py`), so values can differ slightly between results.

## 5. The market's error in closed-door matches (hierarchical delta)

**Priced home advantage by period** (`model.py`, layer 1). Within each league-season, mu for home team i against away team j is regressed on team dummies and a home-advantage term for each month and crowd regime: mu_ij = H + s_i - s_j + noise. In latent units the priced home advantage was 0.211 with crowds (2015/16 to 2019/20), 0.129 behind closed doors in the first wave, 0.156 with partial crowds and 0.190 with crowds from 2021/22. Season-level values are used in section 6. Month-by-month values from this method leak results (see section 7) and are no longer used.

**The error** (layer 2). For a closed-door match in league l:

    true latent mean = eta0 + delta_l

The likelihood of the result is Phi(eta0 + delta_l - c) for a home win, Phi(-eta0 - delta_l - c) for an away win, and the remainder for a draw.

**Pooling.** delta_l ~ Normal(delta_bar, tau^2). delta_bar is the overall market error and tau is how much leagues truly differ. A noisy league is pulled towards delta_bar by roughly tau^2 / (tau^2 + se_l^2). For the Premier League that is 0.021^2 / (0.021^2 + 0.039^2) = 0.22, which is why its raw -0.070 shrinks to about -0.03.

**Priors.** delta_bar ~ Normal(0, 0.05^2), centred on "the market is right". For tau the code uses a discrete prior on eight values (0.002, 0.01, 0.02, 0.03, 0.04, 0.06, 0.08, 0.10), weighted by the half-normal density with scale 0.05 at those points. Because the points are unevenly spaced and no interval widths are applied, this is not the same as a continuous half-normal prior. It puts relatively less weight on the larger values. Whether a continuous version would change the result has not been checked.

**Computation.** No sampling. The posterior is a numerical grid approximation: delta_bar on a grid from -0.16 to +0.16 in steps of 0.004, each league's delta_l on a grid from -0.30 to +0.30 in steps of 0.004 (integrated out numerically), and the eight tau values. Interval ends are read from the cumulative grid weights, so they are accurate to about one grid step.

Result: delta_bar = -0.020 (sd 0.014). Probability it is below zero: 0.92.

**Real time** (`model.py`). From 11 May 2020, the posterior is recomputed each week from matches before that date only and used to predict the following week. Matches before the first cut-off keep the prior (delta = 0). Scores against the calibrated price: log-loss difference t = -0.1, and 2,776 value bets, all on away sides, returned -0.4%.

## 6. Turning it into "normal = 100"

True home advantage in a regime is a + b * H_regime + delta_regime. Divide by the same quantity for crowd matches (a + b * 0.211 = 0.223):

- Closed doors, as priced: 1.056 * 0.129 / 0.223 = 61
- Closed doors, model: (1.056 * 0.129 - 0.020) / 0.223 = 52

Two intervals exist for the 52. Sampling error alone gives about 39 to 65. Adding ordinary season-to-season market error (sd 0.010, from section 10) gives 36 to 67, which is the interval quoted in the findings.

## 7. The state-space model (Kalman filter)

`pipeline/kf.py`. Needed because layer 1 fits team strengths on a whole season of prices, and prices after a match react to its result. A month's "priced home advantage" from layer 1 therefore partly contains that month's results.

**State, per league.** Home advantage under each regime (full, none, partial) and one strength per team. Initial means 0.22, 0.20 and 0.20 for the three regimes, initial sds 0.10, 0.15 and 0.15. Team strengths start at 0 with sd 0.5.

**Dynamics.** All states are random walks with variance proportional to the days elapsed. There are four settings:

| Setting | Meaning | Fitted value |
|---|---|---|
| qs | Team strength drift | sd 0.032 a week |
| qh | Home-advantage drift | sd 0.0027 a week |
| qbreak | Extra team-strength jump across a gap of more than 45 days (summer break) | sd 0.041 |
| R | Noise in one match's price | sd 0.079 |

A regime that has not yet been seen keeps its prior variance (no drift) until its first match. Matches in excluded weeks (March and April 2020) still update the full-crowd state.

**Observation.** Each match's mu = H_regime + s_home - s_away + noise. Results never enter.

**Timing.** Matches on the same date are processed one after another in no particular order (the data is sorted by date only). Two readings are kept: `H_prior`, from prices on strictly earlier dates, and `H_post`, after all prices on the match date. Most later scripts use `H_post`, so the market reading can include prices from later kick-offs on the same day. It is a date-level reconstruction, not a strict pre-kick-off record.

**Fitting scope.** The four settings were fitted by maximum likelihood (Nelder-Mead, capped at 160 iterations with loose tolerances) on four leagues (Premier League, Bundesliga, Segunda División, Eredivisie) using all their matches from 2012 to 2026. They were then applied to all 18 leagues and, through `newleagues.py`, the 11 extra leagues. Because the settings use later data, the filtered path is a retrospective reconstruction even though each step only uses earlier prices.

## 8. The market as a learner

`pipeline/learn.py` and `market_path.py`.

**The truth as a fraction.** Write the true closed-door home advantage in a league as rho times that league's normal level, and the market's priced fraction as r = (a + b * H_post) / (a + b * H_pre). For any rho the likelihood of every result can be computed, so the posterior for rho is computed on a grid from 0 to 1.6 in steps of 0.01. With a flat prior: rho = 0.52 (sd 0.06). The market's average r is 0.61.

**Fitted descriptive prior.** A learner with prior Normal(rho0, s0^2) has a posterior mean that moves from rho0 towards the data as matches arrive. rho0 and s0 are chosen so that this path matches the market's observed raw monthly path, evaluated at mid-month (the 15th). Result: rho0 = 0.67, s0 = 0.07. One match carries information of about 0.038 about rho, so s0 = 0.07 is worth 1 / (0.07^2 x 0.038), about 5,300 matches. `learn.py` fits the same thing to the weekly filtered path and gets 0.68 and about 5,400 matches.

This prior is fitted to what the market did. It describes the market's behaviour. It is not a prior anyone could have chosen in advance.

**Fixed alternatives for scoring.** The scored learners use fixed priors: flat, a sceptical prior at "no change" (1.0, sd 0.25), and a prior centred on the market's average early reading (the first three weekly readings, about 0.60) with sds from 0.03 to 0.50. Two learners allow the truth to drift weekly. The early reading uses observed prices, so these are not fully ex ante either.

**Timing.** `market_path.py` and the learning figure evaluate the learner at mid-month. `learn.py` prints start-of-month values. The numbers quoted in the findings come from the mid-month version.

## 9. Evaluation

- **Benchmark.** The calibrated price, eta0.
- **Log score.** Each week's matches are predicted with a posterior built from earlier matches only, and the log score is compared with the calibrated price's. Positive means better than the market.
- **Return.** Flat stakes at Pinnacle closing odds wherever a rule or learner sees value. Return is not the same as information: a factor can predict results without beating the margin.
- **Resampling.** Interval methods differ by result: individual bets (betting rules), weeks (`learn.py` log scores), league-seasons (`rederive.py`), leagues (`dose.py` shape comparison) and clubs (`clubs.py`). Each result states its own.
- **Sequential test (criterion C1).** The likelihood of the results under "home sides over-rated by some amount" (averaged over a half-normal prior with sd 0.05 on that amount, on a grid in steps of 0.002) is divided by the likelihood under "the calibrated price is right", and tracked week by week. If the calibrated price is the true outcome distribution and outcomes are conditionally independent given prices, the chance this ratio ever reaches 20 is at most 1 in 20, however often it is checked (Ville's inequality). Ours peaked at 10.6. The guarantee depends on those conditions, including that a and b, estimated on earlier data, are correct.
- **Revision weights.** `kappa_clean.py` section F (no fixed effects) gives the supported estimate: 0.97 (se 0.33) on the real-time change in priced home advantage. The earlier sections print fixed-effects versions, which are biased when the regressor reacts to past results.

## 10. Simulation checks and their limits

| Check | Script | Result | Limit |
|---|---|---|---|
| Recovery of delta | `model_verify.py`, 300 simulations per setting | Posterior mean close to the truth. 95% intervals cover it 94% to 98% of the time | Results simulated from the model itself |
| Power | Same | -0.06 found 99% of the time, -0.03 about 60% | Same |
| Repeated looks | Same | Running probability touches 0.95 in 11% and 0.99 in 1% of seasons if the market is exactly right. 15% and 3% if only as right as in an ordinary season | Same |
| Placebo seasons | `model_checks.py` | Errors from -0.028 to +0.038 over 12 seasons, season-level noise sd 0.010 | 12 seasons is a rough basis |
| Draw width | `model_verify.py` | k = 1.020 (p = 0.01), delta unchanged. Decile check off by up to 2.2 points for draws | |
| Prior weight | `prior_weight_sim.py`, 60 simulations per setting | Recovered to about a factor of 2. Cannot separate 20,000 matches from "never updates" | Simulated learner and independent monthly noise (sd 0.03) |

These checks show the methods behave well under their own assumptions. They do not show the assumptions hold for the real market.

## 11. Current limitations, extensions and script map

**Current limitations.**

1. The base model holds delta constant over the closure period. The learner in section 8 describes the market's path, but the results-side error is still estimated as one number (or a slowly drifting one).
2. Win, draw and loss only. Goals or handicap and totals prices would carry more information per match.
3. Draws are slightly miscalibrated (k = 1.02).
4. Season-level noise is estimated from 12 seasons.
5. Intervals ignore uncertainty in the priced level (layer 1 or the filter).
6. The tau prior is discrete (section 5), and filter settings are fitted retrospectively (section 7).
7. Crowd regimes in the base model are three categories. The dose analysis uses recorded gates, with a slightly different closed-door rule.

**Extensions in the repository.** Dose curve (`dose.py`, Result 19), club effects (`clubs.py`), VAR (`var_test.py`, `var_confirm.py`).

**Script map.**

| Step | Script | Writes |
|---|---|---|
| Margin removal, mu and c, regimes | `model_data.py` | `work/model.pkl`, `work/model_all.pkl` |
| Calibration, layer 1, delta, real time | `model.py` | `work/H.pkl`, `work/model_track.csv` |
| Placebo, season noise | `model_checks.py` | `work/season_noise_sd.txt` |
| Simulation checks | `model_verify.py` | console only |
| State-space model | `kf.py` | `work/kf_par.npy`, `work/kf.pkl` |
| Learner | `learn.py`, `market_path.py` | `work/learn_paths.npz`, `work/market_path.csv`, `work/fig_learning.png` |
| Revision weights | `kappa_clean.py` | console only |
| Historical base-model chart (superseded) | `model_chart.py` | `work/fig_base_model.png` |

## 12. Glossary

- **mu**: the market's latent supremacy for the home side. Typical even match 0.23.
- **c**: half-width of the draw band. Typical 0.37.
- **eta0**: calibrated price, a + b * mu.
- **H**: home advantage inside mu after team strengths are removed.
- **delta**: true latent mean minus eta0. Negative means home sides were over-rated.
- **delta_bar, tau**: mean and spread of delta across leagues.
- **rho**: true closed-door home advantage as a fraction of normal. **r**: the market's priced fraction.
- **Shrinkage**: pulling a noisy league estimate towards the average, more strongly the noisier it is.
- **Prequential**: predicting each match using only earlier data, then scoring.
- **State-space model / Kalman filter**: a model of quantities that drift over time, updated one observation at a time.
- **Closing-line value**: movement of the price in the bettor's favour between the bet and the close. Not the same as profit.
