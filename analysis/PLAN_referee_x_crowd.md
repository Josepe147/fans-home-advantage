# Test plan: referee x crowd (written before any edge test was run)

Written 16 Nov 2026, 14:50. Committed to the project folder before the hold-out was touched.

## Question
Some referees favour the home side more than others (Boyko et al. 2007), and the lab and ghost-game evidence says the crowd causes it. The referee is announced before kick-off. Does Pinnacle's price fully reflect who the referee is?

## Data
- Premier League and Championship, football-data.co.uk: result, cards, fouls, referee, Pinnacle opening and closing 1X2 odds (2012/13 to 8 Jan 2026).
- Transfermarkt: attendance per match. No attendance listed inside the Covid window = ghost game.
- Referee history back to 2000/01 is used only to estimate each referee's bias.

## Referee bias measure (fixed now)
For every match, the referee's bias is computed **only from seasons before that match's season**, and only from games with a full crowd.
- **Primary: yellow-card bias.** Card differential = away yellows minus home yellows. Residualised on the market's strength gap (home prob minus away prob) with league-season fixed effects. Referee bias = mean residual over his past matches, shrunk towards zero by n / (n + k), with k estimated from the data. Referees with fewer than 30 past matches get bias 0.
- Secondary A: foul bias (away fouls minus home fouls, same construction).
- Secondary B: result bias (past mean of the result residual S, defined below).
Bias is standardised (z-score) across matches within the sample being tested.

## Outcome
S = (home win minus away win) minus (market home prob minus market away prob). Zero on average if the price is right.

## Hypotheses
- **H1 (edge).** In games with a crowd, S rises with the referee's bias z-score. One-sided. Tested against Pinnacle **closing** probabilities (primary) and opening (secondary).
- **H2 (market learning).** Closing minus opening home probability moves in the direction of the referee's bias.
- **H3 (crowd dose).** The H1 slope is larger when the crowd is larger (bias x attendance, attendance standardised within league).
- **H4 (mechanism placebo).** Past card bias predicts card differential in crowd games, and the slope shrinks towards zero in ghost games.

## Sample split
- **Exploration:** 2012/13 to 11 Mar 2020 (crowd games). Used to estimate k, check persistence and look at H1 to H3 freely.
- **Ghost period:** restart 2020 and 2020/21. Used only for H4.
- **Hold-out:** 2021/22 to 8 Jan 2026 (last Pinnacle price). Run once, with the specification above unchanged.

## Betting rule on the hold-out (fixed now)
Flat one-unit stakes at Pinnacle closing odds. Back the home team when primary bias z >= +1. Back the away team when z <= -1. Report return on stake with a bootstrap 95% interval. Repeat at opening odds.

## Power, stated in advance
S has a standard deviation of about 0.85. With roughly 4,000 hold-out matches the standard error on the H1 slope is about 0.013 per z. So only a slope above roughly 0.026 (2.6 percentage points of home-minus-away probability per standard deviation of referee bias) would be detectable. A true effect smaller than that will look like a null. A null therefore means "no edge big enough to see at this sample size", not "no effect".

## What would count as a finding
- H4 holding is a finding on its own (referee bias is real, persistent and crowd-dependent).
- H1 on the hold-out with the betting rule profitable and the interval excluding zero would be an edge. Anything else is reported as not an edge.
