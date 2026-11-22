# Plan: the dose curve. Written 17 Nov 2026, 15:45, before any curve was fitted.

Already seen: closed doors 0.52 of normal home advantage, partial crowds (583 matches, median gate about 2,000) 1.01 with interval 0.57 to 1.45.

## Sample
First-wave window only (1 May 2020 to 30 June 2021), so the comparison is within the same period. 18 existing leagues plus Austria, Denmark, Romania, Switzerland, Japan and, if the scrape finishes, Poland, Russia, Sweden, Norway, Finland, Ireland. A recorded gate of 100 or fewer counts as closed doors (officials and guests, found in Swiss and Italian records).

## Model
Each match: true latent mean = price with the market's home advantage removed + league normal home advantage x f(crowd). Strength and priced home advantage come from the Kalman filter on prices only.

## Shapes compared (fixed now)
- S0. f constant: crowds of any size behind closed-doors-era rules make no difference.
- S1. Step: f = rho0 with no crowd, rho1 with any crowd.
- S2. Saturating: f = rho0 + (1 - rho0)(1 - exp(-gate / k)). Full crowds return to normal. k is the gate that restores 63% of the gap.
- S3. Linear in log gate: f = rho0 + beta log(1 + gate / 1000).

## Judging
Leave-one-league-out log score, summed over leagues, with a bootstrap over leagues for the differences. The headline is the attendance-band table (0, 101 to 1,000, 1,001 to 2,000, 2,001 to 5,000, over 5,000), each band estimated freely.

## Robustness, fixed now
(a) Closed-door comparison restricted to league-months that also had crowds. (b) England only. (c) Without Japan, the largest new contributor.

## What would count
"Threshold, not dose" is supported if S1 or S2 with k under 2,000 beats S0 by a bootstrap interval excluding zero and the 101 to 1,000 band is closer to 1 than to rho0. It is contradicted if S0 is not beaten, or if the bands rise steadily with gate.
