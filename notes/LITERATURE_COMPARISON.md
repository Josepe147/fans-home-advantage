# The three pricing papers against this project

Read in full on 16 Nov 2026 (working-paper versions). This table is why the hypothesis "mispriced, then corrected" is not new, and what is.

| | Fischer and Haucap (2020 working paper, later Kyklos 2022) | Meier, Flepp and Franck (2021) | Hegarty and Whelan (2022, J. Prediction Markets 2023) | This project |
|---|---|---|---|---|
| Leagues | Germany, top two divisions | England, Germany, Italy, Spain, top division | Same four | 18 leagues in 11 countries |
| Closed-door games | 164 in the working paper | About 400, to 2 Aug 2020 | 1,783 | 7,240 first wave, 209 later |
| Price | Closing 1X2, one firm | Average of six bookmakers, and two exchanges | Asian handicap line | Pinnacle close and open, best price, exchange from 2024 |
| Team strength control | Covariates | The implied probability | SPI ratings | The closing price itself, read as an ordered probit |
| Test | Probit of win on implied probability, ghost dummy, ghost x matchday | Logit of win on implied probability, home x ghost, over cumulative weekly windows | OLS of goal difference and of the handicap line on a lockdown dummy, recursive samples | One parameter for the market's error, pooled across leagues, updated in real time |
| Verdict | Odds missed it. Kyklos version: short run only | Home sides over-rated for about five weeks, Bundesliga only. Other three leagues priced correctly | Market cut home advantage by about half at once and was right. Early results were noise | Small over-rating with probability about 0.90, inside ordinary season noise, not exploitable |
| Returns | Reported without intervals | Away bets positive for about five weeks in the Bundesliga | No strategy tested | Bootstrap intervals, real-time learner lost 0.4% |
| Pooling across leagues | Each division separately | League fixed effects, by-league table | League intercepts | Hierarchical, with a test that leagues differ no more than chance |
| Repeated looks at growing data | Not addressed | Not addressed, and the window cut-off looks chosen after the fact | Recursive estimates, not addressed | Simulated false-alarm rate, and an anytime-valid test |
| Closures after June 2021 | No | No | No | Netherlands, Germany, Belgium 2021/22, Greece 2023/24 |
| Placebo on normal seasons | No | No | No | 12 seasons |

## What this means for the paper

- The disagreement in the literature is mostly about the first five weeks in one league. Hegarty and Whelan's reply is that the market was right to discount those early results. Nobody has put a number on how much the market discounted them, or on how much it should have.
- That is the gap this project can fill: treat the market's priced home advantage as the belief of a learner, measure the weight it put on results, and compare that with the weight that would have predicted best.
- Our "about half" for the size of the effect agrees with Hegarty and Whelan. It is a replication on more leagues, not a new number.
- Our Premier League 2020/21 result is not in any of the three. It also did not survive pooling.
