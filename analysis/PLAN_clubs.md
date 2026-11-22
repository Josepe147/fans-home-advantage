# Plan: club-specific home advantage, priced against true. Written 17 Nov 2026, 15:20, before any club-level result was computed.

Already seen: a feasibility check (16 Nov) that the market's priced club home advantage barely varies between clubs (spread within one season no bigger than reading noise, season-to-season correlation 0.15).

## Quantities
For each match, z = the result's departure from the calibrated closing price, in latent units (one-step score divided by Fisher information, weight = information). z is from the home side's point of view.
- Club overall mispricing m_i, club home-advantage mispricing g_i. A home match of i against j has expected z = m_i + g_i/2 - m_j + g_j/2.
- Per club-season: g_hat = mean z over its home games + mean z over its away games, minus the league-season mean of the same. m_hat = (mean z home - mean z away) / 2.
- Priced club home advantage per club-season: from a round-robin fit of mu = a_i - b_j within the league-season, h = a_i - b_i minus the league mean.

## Exploration (2012/13 to 29 Feb 2020, crowd games)
Variance of the persistent part of g, m and h from covariances between seasons of the same club at lags 1, 2 and 3 (noise in different seasons is independent). Standard errors by bootstrap over clubs.

## Hold-out test, run once (crowd games, 1 Aug 2021 to 8 Jan 2026)
- Shrunk club effects from exploration: g_i* = w_i * mean(g_hat_i), w_i = V_g / (V_g + noise_i / k_i), V_g from the exploration covariances (floored at 0), k_i = seasons. Same for m.
- Prediction for each hold-out match: zp_g = (g_i* + g_j*) / 2 and zp_m = m_i* - m_j*. Clubs absent from exploration get 0.
- Primary: information-weighted regression of hold-out z on zp_g. Pass if slope > 0, one-sided p < 0.05, standard errors clustered by league-month.
- Secondary: same for zp_m. Then, only if the primary passes, returns at Pinnacle close for a rule fixed now: back the home side when zp_g is in the top 10% of hold-out matches, the away side when it is in the bottom 10%.
- If V_g is estimated as zero, the hold-out test is skipped and the result is "no detectable persistent club home-advantage mispricing", with the detection limit stated.
