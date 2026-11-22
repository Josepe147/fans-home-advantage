# Plan: did the market price VAR's effect on home advantage? Written 17 Nov 2026, 16:40.

## What has been seen (exploration, 7 leagues)
Germany, Italy, Portugal (2017/18), Spain, France (2018/19), Premier League, 2. Bundesliga (2019/20), against EFL Championship, League One, League Two (no VAR). Three seasons before against the first three with VAR, 2020/21 skipped.
- Results against the calibrated price fell by 0.050 (t = -3.1) relative to the EFL. Without a control group: -0.026 (t = -2.0). There is a downward pre-trend against the EFL.
- Priced home advantage fell by 0.017 (t = -2.3), gradually, over about three seasons.
- Win-minus-loss share fell 31% relative to the EFL, with no price model.
Reading to be tested: VAR cut true home advantage, and the market took several seasons to price it.

## Confirmation, run once
- Sample: every other league in the data (the 11 other football-data leagues and the 11 extra leagues) whose top-flight VAR start can be dated to the start of a season from 2017/18 to 2022/23, from the Wikipedia VAR article cross-checked against one other source. Dates are recorded in var_confirm.py before any result is computed. Leagues with mid-season starts or dates that cannot be cross-checked are left out.
- Controls: leagues in the data that did not adopt VAR within three seasons either side of the treated league's start (never-adopters plus late adopters).
- Primary: change in results against the calibrated price, first three VAR seasons against three before, minus the same change in controls, averaged across confirmation leagues. Pass if the mean is below zero with one-sided p < 0.05 (standard error across leagues).
- Secondary: the same without a control group, and for priced home advantage.
- Exploration and confirmation are reported separately. They are pooled only if the confirmation passes.
