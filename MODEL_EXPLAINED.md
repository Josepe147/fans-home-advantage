# The base model, explained

Written 16 Nov 2026 so that every step can be defended out loud. Code: `pipeline/model_data.py`, `pipeline/model.py`. Checks: `pipeline/model_checks.py`, `pipeline/model_verify.py`.

## The idea in one paragraph

A closing price already contains the market's view of both teams and of home advantage. So do not build a team-strength model to compete with it. Take the price as the strength estimate, and ask one narrow question of the results: was the home side's edge, as priced, too big or too small when the stadium was empty? That one number is called delta. Everything else is bookkeeping to measure delta fairly and to say how sure we can be.

## Step 1. Odds to fair probabilities

Pinnacle closing odds for home, draw, away are o_H, o_D, o_A. The implied probabilities 1/o sum to more than 1 (about 1.026). That excess is the bookmaker's margin. Divide each by the sum to get fair probabilities p_H, p_D, p_A.

Checked: using the power method instead of dividing by the sum gives the same delta to three decimals (-0.022).

## Step 2. Fair probabilities to two numbers

Picture each match as one hidden quantity X, the home side's performance margin on the day, drawn from a normal distribution with mean mu and standard deviation 1.

- Home win if X > c
- Away win if X < -c
- Draw in between

So p_H = Phi(mu - c) and p_A = Phi(-mu - c), where Phi is the standard normal distribution function. Two equations, two unknowns. Write z_H = Phi^-1(p_H) and z_A = Phi^-1(p_A). Then

    z_H = mu - c
    z_A = -mu - c
    mu = (z_H - z_A) / 2
    c  = -(z_H + z_A) / 2

This is exact. Nothing is fitted. **mu** is the market's supremacy for the home side on a common scale. **c** is how wide the draw band is. This is an ordered probit model read backwards.

Worked match: Liverpool v Crystal Palace, 24 June 2020, closed doors. Odds 1.30 / 5.85 / 11.67. Book 102.6%. Fair probabilities 0.750 / 0.167 / 0.084. z_H = +0.674, z_A = -1.382. So mu = 1.028 and c = 0.354.
For scale, a typical evenly matched game (0.44 / 0.29 / 0.27) has mu = 0.23 and c = 0.37. That 0.23 is home advantage.

## Step 3. Calibration: is the price right in normal times?

Before blaming the market for anything in 2020, check it in 51,437 ordinary games (2012 to February 2020). Fit

    true latent mean = a + b * mu

by maximum likelihood on results.

- a = 0.000 (se 0.003). The market's home advantage needs no correction in normal times.
- b = 1.056 (se 0.030). Strong favourites win slightly more than priced. This is the favourite-longshot bias. With the power de-vig it shrinks to 1.02, so most of it comes from how the margin is removed.

Call a + b * mu the calibrated price, eta0. All later tests are against eta0, so nothing in 2020 gets blamed for a bias that is always there.

## Step 4. Layer 1: what home advantage was the market pricing?

*Note added 17 Nov: the season-level numbers in this step stand. Anything that varies within a season (the month-by-month path) now comes from the Kalman filter in Step 8, because whole-season team strengths leak results.*

Within one league season, write the market's supremacy for home team i against away team j as

    mu_ij = H + s_i - s_j + noise

H is home advantage. s_i is team i's strength that season. Every team plays home and away, so the strengths can be separated from H by ordinary least squares with one dummy per team. H is allowed to differ by month and by crowd status.

Result, in latent units:

| | Priced home advantage H |
|---|---|
| Crowds, 2015/16 to 2019/20 | 0.211 |
| Closed doors, first wave | 0.129 |
| Partial crowds | 0.156 |
| Crowds, 2021/22 on | 0.190 |

So the market cut home advantage by 39% when stadiums closed.

## Step 5. Layer 2: was that cut right?

For a closed-door match in league l, suppose the truth was

    true latent mean = eta0 + delta_l

delta_l < 0 means home sides in that league did worse than even the calibrated price implied. The likelihood of the actual result is Phi(eta0 + delta_l - c) for a home win, Phi(-eta0 - delta_l - c) for an away win, and the remainder for a draw.

**Pooling across leagues.** Eighteen separate estimates are noisy, and picking the biggest is how the Premier League result fooled us. So assume the leagues are draws from a common distribution:

    delta_l ~ Normal(delta_bar, tau^2)

delta_bar is the Europe-wide market error. tau is how much leagues truly differ. The data decide both. The effect is shrinkage: a league's estimate is pulled towards delta_bar by a factor of roughly tau^2 / (tau^2 + se_l^2). For the Premier League that is 0.021^2 / (0.021^2 + 0.039^2) = 0.22, which is why its raw -0.070 shrinks to about -0.03.

**Prior.** delta_bar ~ Normal(0, 0.05^2). Centred on "the market is right", wide enough to allow an error of a quarter of home advantage either way. tau has a half-normal prior with scale 0.05.

**Computation.** No sampling. The posterior is computed exactly on a grid of delta_bar and tau values, integrating each league's delta_l out numerically.

Result: delta_bar = -0.020 (sd 0.014). Probability it is below zero: 0.92.

## Step 6. Turning it into "normal = 100"

True home advantage in a regime = a + b * H_regime + delta_regime. Divide by the same thing for normal crowd games (a + b * 0.211 = 0.223).

- Closed doors, as priced: 1.056 * 0.129 / 0.223 = 61
- Closed doors, model: (1.056 * 0.129 - 0.020) / 0.223 = 52

## Step 7. Real time, and scoring

Each week from May 2020 the posterior is recomputed from matches played before that date only. The following week's matches are then predicted with it. Two scores:

- Log loss against the calibrated price. Difference t = -0.1. The learner did not predict better.
- Bets wherever the learner's probability times the Pinnacle odds exceeded 1. 2,776 bets, all on away sides, return -0.4%.

## Step 8. The extension: the market as a learner (added late on 16 Nov)

**Why Step 4 was not good enough for anything that moves within a season.** Step 4 fits team strengths on the whole season's prices. Prices after a match react to its result. So a month's "priced home advantage" quietly contains that month's results. The season-level numbers in Step 4 are fine. The month-by-month path was not.

**The fix: a Kalman filter on prices** (`pipeline/kf.py`). Hidden state for each league: home advantage H under each crowd regime, and a strength s for each team. All drift as random walks. Each closing price is an observation

    mu = H_regime + s_home - s_away + noise

The filter runs forwards through the fixtures. Before each match date it holds an estimate of H built only from earlier prices. Results never enter. Three variances are fitted by maximum likelihood: how fast strength drifts, how fast H drifts, and how noisy one match's price is. They were fitted on four leagues (Premier League, Bundesliga, Segunda, Eredivisie) to save time and applied to all 18.

**The truth as a fraction.** Write the true closed-door home advantage in a league as rho times that league's normal level. The market's priced fraction is r. For any value of rho, the likelihood of every result can be computed exactly, so the posterior for rho is computed on a grid. Result: rho = 0.52 (sd 0.06). Market average r = 0.61.

**The market as a Bayesian learner.** A learner with prior Normal(rho0, s0^2) has a posterior mean that moves from rho0 towards the data as matches arrive. Fit rho0 and s0 so that this moving mean matches the market's observed path. Result: rho0 = 0.67, s0 = 0.07. Converting s0 into matches: one match carries information 0.038 about rho, so a prior variance of 0.07^2 equals 1 / (0.07^2 x 0.038) = about 5,300 matches.

**A test that survives weekly checking.** Take the ratio of the likelihood under "home sides over-rated by some amount" (averaged over a half-normal prior on that amount) to the likelihood under "the calibrated price is right". If the price is right, this running ratio is a fair-game process, and the chance it ever reaches 20 is at most 1 in 20, however often it is checked (Ville's inequality). Ours peaked at 10.6.

**Did the market weight its own revisions correctly?** Split the price into two parts known before kick-off: priced home advantage at the season start, and its real-time change since. If the price is efficient each part has weight 1. Estimated weight on the change: 0.97 (se 0.33). An earlier version with league-season fixed effects gave -2.07. That was bias, because demeaning within a season uses future values of a variable that responds to past results.

## What has been verified

| Check | Result |
|---|---|
| Recovery. Simulate results on the real fixture list with a known delta, 300 times | Posterior mean is unbiased at zero and within 0.005 of the truth elsewhere. 95% intervals cover the truth 94 to 98% of the time |
| Power | A true gap of -0.06 would be detected 99% of the time. A true gap of -0.03 only about 60%. The data cannot separate -0.03 from zero |
| Peeking | If the market were exactly right, the weekly running probability would still touch 0.95 at some point in 11% of seasons and 0.99 in 1%. If the market were as right as in an ordinary season, 15% and 3% |
| Placebo | Same calculation on 12 ordinary seasons: misses from -0.028 to +0.038. Season-level noise sd 0.010 |
| Prior | Halving or doubling the prior width moves delta_bar between -0.016 and -0.022 |
| De-vig method | No change |
| Draw width | Letting c scale by k gives k = 1.020 (p = 0.01). Delta unchanged |

## What is weak in the base model

1. **Delta is one constant for the whole closed-door period.** Addressed in Step 8. The phase estimates moved because results drifted, not because the price did.
2. **The real-time peak was a rare event that the constant-delta model shrugs off.** The running probability reached 0.99 in February 2021. Under an ordinary-season market that happens in about 3% of seasons. So the evidence for a temporary gap is moderate, not nil.
3. **It uses win, draw, loss only.** Goals carry more information per match. A goals model would tighten every interval. This is now the main weakness.
4. **Draws are slightly miscalibrated** (k = 1.02, and the decile check fails for draws by up to 2.2 points).
5. **Season noise is estimated from 12 seasons.** That is a rough number.
6. **Intervals ignore the uncertainty in Step 4.** Small, but not zero.
7. **Crowd status is three boxes** (none, partial, full). No dose curve.

## Glossary

- **mu**: market's latent supremacy for the home side. Typical even match 0.23.
- **c**: half-width of the draw band. Typical 0.37.
- **eta0**: calibrated price, a + b * mu.
- **H**: home advantage inside mu after team strengths are removed.
- **delta**: true latent mean minus eta0. Negative means home sides were over-rated.
- **delta_bar, tau**: mean and spread of delta across leagues.
- **Shrinkage**: pulling a noisy league estimate towards the average, more strongly the noisier it is.
- **Prequential**: predicting each match using only earlier data, then scoring.
