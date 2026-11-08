# Liga MX data understanding

The FotMob index has 1,829 league-230 rows: 1,530 regular rows from ten complete tournaments, 156 completed-tournament playoff rows excluded, and 143 rows from the in-progress 2026/2027 Apertura excluded wholesale. Each complete tournament has 18 teams and 153 regular matches. The frozen phase rule is `general.matchRound` as a digit 1–17; every other non-empty label is playoff/play-in/reclassification and unclassified labels raise.

## Findings

F1. Goal scores and event goals are retained with an explicit mismatch flag; measured mismatches: **2 of 1,530** regular matches (header score is the target by rule). `coverageLevel` is `xG` for all 1,530; HT goals are event-derived for all 1,530; there are zero shootout shots in the regular corpus (shootouts occur only in the excluded Liguilla).

## Coverage matrix (regular phase, % of 153 matches per tournament with real content)

| Tournament | Stats FT | Per-half splits | Shotmap / xG | Events | Referee named | touches_opp_box present |
|---|---|---|---|---|---|---|
| 2021/2022 - Apertura | 100 | 4.6 | 100 | 100 | **0** | 65/153 |
| 2021/2022 - Clausura | 100 | 11.8 | 100 | 100 | 96.7 | 147/153 |
| 2022/2023 - Apertura | 100 | 10.5 | 100 | 100 | 95.4 | 60/153 |
| 2022/2023 - Clausura | 100 | 40.5 | 100 | 100 | 95.4 | 146/153 |
| 2023/2024 - Apertura | 100 | 100 | 100 | 100 | 100 | 153/153 |
| 2023/2024 - Clausura | 100 | 100 | 100 | 100 | 96.1 | 153/153 |
| 2024/2025 - Apertura | 100 | 100 | 100 | 100 | 97.4 | 152/153 |
| 2024/2025 - Clausura | 100 | 100 | 100 | 100 | 97.4 | 153/153 |
| 2025/2026 - Apertura | 100 | 100 | 100 | 100 | **24.8** | 153/153 |
| 2025/2026 - Clausura (virgin) | 100 | 100 | 100 | 100 | **58.2** | 153/153 |

## Calendar and format

Two tournaments per football year — Apertura (roughly Jul–Nov) and
Clausura (Jan–Apr/May) — each a 17-round single round-robin of the
same 18 clubs (153 matches), followed by the Liguilla (reclassification /
play-in, quarter-finals, semi-finals, final; 18 playoff matches per
tournament in 2021/2022–2022/2023, 14 per tournament from 2023/2024
under the play-in format), excluded everywhere by the phase rule.
No promotion/relegation in the window (suspended since 2020): the
18-club set is identical in all 10 tournaments. The regular season
is the modelled object; the Liguilla is a knockout competition with
aggregate and shootout settlement and is a different object, as in
AR/NL. The virgin tournament (2025/2026 - Clausura, 2026-01-10 →
2026-04-27) is complete; 2026/2027 - Apertura is in progress at
pull time and excluded wholesale.

F2. Stats, xG and shotmap coverage are 100% in every tournament; production fallback code remains.

F3. Period splits are sparse early and complete from 2023/2024 Apertura.

F4. Goals/xG calibration ranges 0.952–1.144 by tournament.

F5. xGOT population is 0.302–0.350 through 2023/2024 Clausura, 0.855 in 2024/2025 Apertura and 0.997+ thereafter; X6 guard is 2025-01-01+.

F6. Set-play xG share reliability is 0.558 ratio-of-sums split-half.

F7. Reliability is strong for xG (0.811/0.881), SOT (0.848/0.797), shots (0.845/0.890), corners (0.670/0.718), and box touches (0.863/0.890), for/against.

F8. First-half shares are goals 0.456, SOT 0.455, corners 0.465, shots 0.458 and event yellows 0.385.

F9. Referee coverage is 0.0% warm-up, 96.7%, 95.4%, 95.4%, 100.0%, 96.1%, 97.4%, 97.4%, 24.8%, and 58.2%; the caveat is operational.

F10. Event yellows are the target. Dev regular stats/event totals are 608/622, 708/729, 708/728, 658/679, 750/772, 671/684, 614/636, 660/664, 713/721; exact-match agreement is 135, 133, 135, 133, 120, 135, 130, 131, 122 of 153.

F11. Primary dev lines nearest the medians are goals 2.5 (mean 2.744, over 52.5%), SOT 8.5 (8.916, 51.2%), corners 9.5 (9.793, 50.8%), cards 4.5 (4.528, 47.5%), shots 26.5 (26.646, 47.9%).

F12. The same 18 teams occur in all ten tournaments; every transition has zero entrants and departures, so X2 is dropped.

Altitude finding: static mapping in `eda.py` gives high-altitude homes (>=2000m) edge 0.586 and win rate 50.6% across 510 matches, versus 0.221 and 41.5% across 1,020 rest matches. With away altitude <1000m, the comparison is 0.875/56.7% (n=120) versus 0.077/40.5% (n=220). Descriptive/not adopted: altitude is collinear with stable team identity.
