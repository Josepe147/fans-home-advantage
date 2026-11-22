# Literature review: fans, noise, home advantage and betting markets

Compiled 16 Nov 2026. Grouped by what each paper answers. "Gap" notes are our angle.

## 1. Crowd noise and referees (the mechanism)
- **Nevill, Balmer & Williams (2002), Psychology of Sport & Exercise 3(4).** 40 qualified referees watched the same match (Liverpool v Leicester) with or without crowd noise. Noise made them favour the home team.
- **Unkelbach & Memmert (2010), Journal of Sport & Exercise Psychology 32(4).** Video of 56 games with recorded crowd reactions to fouls. Argue crowd noise is a genuine cue for how bad a foul is, so referees use it, and a partisan crowd produces home bias. Effect grows with crowd size and density.
- **Pettersson-Lidbom & Priks (2010), Economics Letters 108(2).** Natural experiment: after hooligan violence in Feb 2007 Italy forced 25 games behind closed doors. Referees punished away players more and home players less when fans were present.
- **Myers & Balmer (2012), Frontiers in Psychology.** Muay Thai judges with noise-cancelling headphones. Same idea outside football.

## 2. Covid ghost games and home advantage
- **Bryson, Dolton, Reade, Schreyer & Singleton (2021), Economics Letters 198.** 2019/20 ghost games across several countries. Large, significant drop in yellow cards without a crowd.
- **Reade, Schreyer & Singleton (2022), Economic Inquiry.** 160 pre-Covid closed-door matches (2002 to 2020) against 33,000+ others. Without a crowd referees booked visiting players over a third of a yellow card less per match. Overall home advantage fell but not significantly.
- **Wunderlich, Weigelt, Rein & Memmert (2021), PLoS ONE.** 40,000+ matches, 1,000+ ghost games. Referee bias fell and home shot dominance fell, but the home advantage itself fell only non-significantly. Conclude crowds are not the main driver.
- **Sors, Grassi, Agostini & Murgia (2022), PeerJ.** Whole 2020/21 season, first and second divisions of the big five. Points-based home advantage 54.95% vs 59.36% with fans. Referee bias disappeared. A slight home advantage remained (travel, familiarity).
- **Leitner & Richlan (2021), Frontiers in Sports and Active Living.** 1,286 matches, eight leagues. Home teams booked more for fouls in ghost games.
- **Schank (2024), arXiv 2411.12509.** Bundesliga during and after Covid. Home advantage in 2020/21 close to 2018/19, so teams adapted to empty stadiums.
- **Systematic review (2023), Management Review Quarterly 73(2).** 26 studies. Ghost games cut home advantage, mainly through reduced referee bias. Notes inconsistencies across studies.
- **NFL (Szabó & Pérez Ruiz 2021, arXiv 2104.11595).** No fans: home teams slightly worse than visitors. Limited fans: home performance no longer different from full stadiums. A small crowd restores most of the effect.

## 3. Betting markets and ghost games (closest to Starlizard)
- **Deutscher, Winkelmann & Ötting (2021), Applied Economics 53(26).** Bundesliga restart spring 2020. Bookmakers failed to adjust odds for the lost home advantage. Profitable strategies existed.
- **Meier, Flepp & Franck (2021), International Journal of Sport Finance 16(3).** Top European leagues. Bookmakers and exchanges overestimated home win probability early in the ghost games, so markets were not semi-strong efficient for a while. Driven by the Bundesliga. Profitable for over a month.
- **German professional football study (2021/22), "COVID-19, home advantage in professional soccer, and betting market efficiency".** Home advantage fell then recovered over time. Odds did not reflect either the drop or the recovery properly. Slow or no adaptation to new results.

## 4. Noise measurement
- **Osses, Ackermans, Nuijens & Scholte (2026), arXiv 2607.18922.** Loudest-stadium claims rest on single-point peak readings that are not comparable. Proposes a standard, spatially distributed method.
- Only public ground-level data: FanChants terrace averages (2011) and Press Association smartphone readings (Nov 2014). Crude.

## Starlizard people (LinkedIn, 16 Nov 2026)
Searched LinkedIn people and posts. Visible: Head of Football, CTO, Head of Integrity Services, recruiter, a former data science and football researcher, an ML specialist. No published papers found linked to Starlizard staff. The firm is secretive and publishes little. Its homepage questions are the best signal of what it values.

## Gaps we can fill (our angle)
1. **Most market studies stop at the spring 2020 restart, mainly in the Bundesliga.** Less is known about the full 2020/21 season in England, and almost nothing about **the return of fans in 2021/22**: did the market put home advantage back too fast or too slow?
2. **Partial crowds in England.** December 2020 (2,000 fans by local Covid tier, set by government not team quality) and May 2021 (up to 10,000). Small, but close to random. The NFL result suggests a small crowd restores most of the effect.
3. **Dose-response in normal seasons, controlling for team strength with the market price.** Does a fuller ground or bigger crowd add anything the closing odds do not already price? That is a "crowd edge" question in Starlizard's own language.
4. **Mechanism split.** How much of the crowd effect runs through the referee (fouls, cards) versus the scoreline itself.


## Added 16 Nov 2026 (after the pricing tests)

- Hegarty and Whelan, "The Wisdom of No Crowds". Reads the ghost period the other way from Fischer and Haucap (2022): on average the market adjusted well. Our Result 3 sits between the two. No shortfall at the June 2020 restart, a shortfall in 2020/21 concentrated in the Premier League.
- Fischer and Haucap (2021, Journal of Sports Economics). The drop in home advantage without crowds was bigger where normal occupancy was higher. Our H5 test of this against prices (did a bigger usual crowd mean a bigger pricing shortfall?) was null.
- Own finding to remember when reading any attendance paper: attendance measured against a season average leaks results, because gates follow results. See results/FINDINGS.md, Result 4.
