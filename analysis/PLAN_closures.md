# Plan: are closed stadiums still underpriced? Written 16 Nov 2026, 15:45, before any result or price outside England was looked at

## What has been seen already (discovery sample)
England, 1,075 ghost games, June 2020 to May 2021. Away sides underpriced at Pinnacle close (S = -0.040, away backers +10.3%). Found in exploration, so it cannot confirm itself.

## The rule being tested
R1: when a league match is played with no spectators, back the away side at Pinnacle's closing price.
Information test: mean S < 0, where S = (home win - away win) - (priced home prob - priced away prob), prices de-vigged.
Profit test: return on R1 at Pinnacle close. Also reported at opening price and best available price.

## Samples, in order of evidential weight
A. Replication across leagues, same time period. Every non-English league with Pinnacle odds, matches from 1 May 2020 to 30 June 2021 with no attendance recorded. Same shock, different markets. Not independent in time.
B. Confirmation, later closures. Any league match from 1 July 2021 onwards with no attendance recorded inside a run of at least 5 such matches in the same league within 30 days (blanket closures: Netherlands winter 2021/22 is already identified from attendance alone, others to be found the same way), plus isolated no-attendance matches listed separately as punishment games. This is the test that matters. The market had a full season of evidence by then.
C. Dose. Matches from 1 July 2021 with attendance recorded but below 25% of the home club's median gate that season (capped crowds). Secondary.

## Decision rule
R1 is confirmed only if sample B shows S < 0 with one-sided p < 0.05 AND a positive return at Pinnacle close. Sample A alone does not confirm it. If B is null, the finding is "the market was slow once and then learned", which is still a result.

## Fixed choices
- No-attendance flag comes from Transfermarkt. Isolated blanks outside known closures may be missing data, so B's headline uses blanket closures only.
- Pinnacle closing odds, de-vig by normalising. Matches without Pinnacle close dropped.
- Standard error of mean S is the plain standard error. Returns get a bootstrap interval.
- No subgroup is promoted to a headline after the fact.

# Addendum, 16:05: line-movement rule fixed before the hold-out is touched
Exploration (2012/13 to Mar 2020, 7,255 crowd games) shows Pinnacle's line moves towards the away side in local games and towards the home side on long trips between the early price and the close (slope per SD of log distance +0.0060 on the home-minus-away gap, t = 10, every season, both leagues, survives team-season fixed effects).
Hold-out test, run once on 2021/22 to 8 Jan 2026 crowd games:
- H-L1 (primary): slope of the move on z(log distance), controlling for the early gap, is positive. z uses the exploration mean and SD.
- H-L2 (rule): at the early Pinnacle price, back the away side when distance < 60 km and the home side when distance > 200 km. Report closing-line value (de-vigged closing probability minus de-vigged early probability of the side backed), the return at the early odds, the return of the same bets at closing odds, and the information test on outcomes against the early price.
- Bands (60 km, 200 km) come from the exploration table and are not to be changed.
What cannot be settled by this test: whether the close or the early price is right about distance. That needs outcomes, and England alone has no power for it.

# Addendum, 16:55: criteria for "mispriced, then corrected", fixed before the learning model is run

What I have already seen, so this is not a clean pre-registration: the pooled constant-error estimate (-0.020), the four phase estimates (-0.024, -0.058, -0.020, +0.006), the weekly running probability (peak 0.99 in February 2021), and the market's priced path on the chart.

The hypothesis is confirmed only if all three hold.
- C1. Mispricing. A test that stays valid under weekly looks rejects "the calibrated market is right" in favour of "home sides over-rated" at the 5% level at some point between 1 May 2020 and 30 June 2021. Test: mixture likelihood ratio with a half-normal prior (sd 0.05) on negative errors, pooled over 18 leagues. Reject if the running ratio ever reaches 20.
- C2. Correction. The market's error in March to June 2021 is smaller in size than in September to November 2020 with probability at least 0.95, under a truth that is constant AND under a truth that is allowed to drift.
- C3. Both C1 and C2 hold with the Premier League and Championship removed, because the idea came from England.

Separately, and not part of the hypothesis: measure the weight the market put on results as they arrived (its implied prior), and compare with the weight that predicted best.

## Outcome, 17:40
C1 fail (anytime-valid p = 0.095, peak ratio 10.6 on 8 Feb 2021). C2 fail (raw priced path 0.629 in Sep-Nov, 0.620 in Mar-Jun, change -0.009 with se 0.049. Under a drifting truth the probability is about 0.81 on the filtered path). C3 fail (C1 p = 0.174 without England). Note: C2 as first written would have passed on the filtered path under a constant truth (0.966). The filtered path lags, and the raw path shows the price did not move, so I am scoring it as a fail and recording that the criterion was poorly specified.
