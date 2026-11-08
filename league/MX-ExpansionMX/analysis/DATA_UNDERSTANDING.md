# Liga de Expansión MX — data understanding

The FotMob index has 1,508 league-8976 rows, all finished. The
warehouse season is the football year and contains both tournaments:
1,208 regular-phase rows in ten complete tournament blocks
(2021/2022 - Apertura … 2025/2026 - Clausura), 172 liguilla play-off
rows excluded by the phase rule, and 128 rows of the in-progress
2026/2027 - Apertura (120 regular + 8 play-off) excluded wholesale.
The frozen phase rule is `general.matchRound` as a digit string
(1–17); every other label ("1/8", "1/4", "1/2", "final",
"Apertura - Quarter-finals") is a play-off. The frozen tournament
rule assigns blocks by date: Apertura = 15 Jun – 31 Dec of the
first calendar year, Clausura = 1 Jan – 14 Jun of the second
(Apertura 2022 began 25 Jun 2022 with a full round played 25–30 Jun;
a naive month≥7 rule misassigns that round).

## Findings

F1. **The stats era does not exist before 2026/2027.** The index
flags 128 rows `has_stats=True` — for once the flag is accurate:
`content.stats` is None in every one of the 1,380 earlier payloads
and carries real values (with FirstHalf/SecondHalf periods) in all
128 payloads of 2026/2027. `coverageLevel` is `lower` before and
`xG` in 2026/2027; shotmap is empty before and populated (with xG)
only in 2026/2027. Verified from payload content, not the flag.
Consequence: SOT / corners / total-shots targets exist **only** in
an in-progress season — there is no dev window and no complete
virgin window, so S-MXE / C-MXE / T-MXE are NOT BUILDABLE
(TH-ThaiLeague2 / CL-LigaDeAscenso precedent).

F2. **Cards era starts 2022/2023 Clausura, cleanly only from
2023/2024 Apertura.** Event `card='Yellow'` counts are zero before
2022/2023 Clausura — the feed recorded only Red/YellowRed events.
In 2022/2023 Clausura plain yellows appear (565 direct + YellowRed
in 153 regular matches, 3.86 unified/match) BUT capture is partial:
45 of 153 matches (29.4%) show zero yellows, versus 1–2 per 105 in
every later block, and the level (3.86) sits ~1.2 below the clean
era (4.89–5.84). That block is therefore excluded from the cards
corpus entirely — not even as warm-up, since its league-mean and
team states would be fitted on a ~25%-undercounted target. The
clean cards era is 2023/2024 Apertura → 2025/2026 Clausura
(630 regular matches, 98–99% of matches with ≥1 yellow).

F3. Goal events are essentially complete: event goal counts equal
the header score in 1,207 of 1,208 regular matches. The single
exception is match 4070356 (2022/2023 - Clausura), excluded from
halves computations only; its header score remains the FT target.

F4. Referee names: 0% in every block before 2025/2026 - Clausura
(12.4% there; 84.2% in 2026/2027). No referee feature can be fitted
on the dev window (X8 dropped).

F5. Team set churns by franchise movement, not by promotion or
relegation: 17 teams in 2021/2022, 18 in 2022/2023 (entrants
Alacranes de Durango, Atlético La Paz), 15 from 2023/2024 (three
departures, no entrants), plus Irapuato entering at 2025/2026 -
Apertura. There is **no promotion to Liga MX and no relegation
from it** in the window; the same-block team-id overlap with the
Liga MX corpus is 0 in all ten blocks. Reserve/affiliate sides
(Tapatío, Raya2 Expansion, Pumas Tabasco) are ordinary members.

F6. Levels (regular phase): goals 2.23–3.05 per match by block
(pooled 2.666), home advantage pooled +0.475 goals — a strong home
edge. First-half goal share 0.448 with measured true variance 0.0
(observed 0.11351 vs binomial noise floor 0.1173): the frozen-
constant question resolves to a constant, exactly as in J1.

F7. Altitude measured, no effect found: with the corrected home-
city map (Atlante's Expansion-era home is Zacatepec, ~1,160 m, per
the corpus's own stadium rows — not Mexico City), the two ≥2,000 m
clubs (Tlaxcala 2,400 m, Mineros de Zacatecas 2,440 m) show a home
edge of +0.207 (n=150) versus +0.513 for the rest (n=1,058); the
away<1,000 m contrast is +0.574 (n=68) vs +0.670 (n=448). No
altitude arm is pre-registered (see FEATURES.md R7).

## Coverage matrix (regular phase, % of matches with real content)

| Block | n | Stats FT | Per-half splits | Shotmap/xG | Events | Referee | Lineup |
|---|---|---|---|---|---|---|---|
| 2021/2022 - Apertura | 136 | 0 | 0 | 0 | 94.1 | 0 | 0 |
| 2021/2022 - Clausura | 136 | 0 | 0 | 0 | 93.4 | 0 | 15.4 |
| 2022/2023 - Apertura | 153 | 0 | 0 | 0 | 94.1 | 0 | 13.1 |
| 2022/2023 - Clausura | 153 | 0 | 0 | 0 | 99.3 | 0 | 76.5 |
| 2023/2024 - Apertura | 105 | 0 | 0 | 0 | 100 | 0 | 100 |
| 2023/2024 - Clausura | 105 | 0 | 0 | 0 | 100 | 0 | 100 |
| 2024/2025 - Apertura | 105 | 0 | 0 | 0 | 100 | 0 | 100 |
| 2024/2025 - Clausura | 105 | 0 | 0 | 0 | 100 | 0 | 100 |
| 2025/2026 - Apertura | 105 | 0 | 0 | 0 | 100 | 0 | 100 |
| 2025/2026 - Clausura (virgin) | 105 | 0 | 0 | 0 | 100 | 12.4 | 100 |
| 2026/2027 - Apertura (in progress, excluded) | 120 | 100 | 100 | 100 | 100 | 84.2 | 100 |

## Calendar and format

Two tournaments per football year — Apertura (late Jun/Jul–Oct/Nov)
and Clausura (Jan–Apr) — each a single round-robin (17 rounds with
17–18 teams in 2021–2023; 15 rounds with 15 teams from 2023/2024),
followed by a liguilla (reclassification, quarter-finals,
semi-finals, final) that is excluded everywhere by the phase rule.
The league is Mexico's second tier but has **no promotion** to
Liga MX in this window (suspended since 2020) — it is a closed
development league, which is why the X2-analogue question resolves
to "no mover flow exists" (FEATURES.md). The virgin block
(2025/2026 - Clausura, complete, n=105) is the most recent complete
tournament; 2026/2027 - Apertura is in progress and reserved as
confirmatory, never read in this build.
