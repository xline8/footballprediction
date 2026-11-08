# Step 3 — EDA: NI-Premiership

Source: `league/NI-Premiership/data/ni_matches.csv` (1,242 rows;
regular n=1,227). Windows: warm-up 2021/22 (n=228); dev scored
2022/23–2024/25 (n=684); virgin 2025/26 (n=228, complete — levels
shown for inventory only, not fitted); confirmatory reserve 2026/27
partial (n=87 — inventory only). All levels below are REGULAR season
only (playoffs excluded, PREPROCESSING.md).

## F1 — Levels per season (goals)

| Season | n | Goals/match | Home | Away | HW | D | AW | OU1.5 | OU2.5 | OU3.5 | BTTS |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2021/2022 | 228 | 2.73 | 1.42 | 1.32 | .425 | .197 | .377 | .741 | .531 | .276 | .461 |
| 2022/2023 | 228 | 2.84 | 1.64 | 1.20 | .500 | .171 | .329 | .763 | .553 | .342 | .399 |
| 2023/2024 | 228 | 3.10 | 1.72 | 1.38 | .412 | .175 | .412 | .825 | .601 | .364 | .496 |
| 2024/2025 | 228 | 2.54 | 1.33 | 1.21 | .439 | .211 | .351 | .719 | .478 | .272 | .461 |
| 2025/2026 | 228 | 2.93 | 1.60 | 1.33 | .465 | .175 | .360 | .807 | .553 | .316 | .513 |
| 2026/2027* | 87 | 2.78 | 1.39 | 1.39 | .437 | .172 | .391 | .782 | .529 | .287 | .529 |

\* partial season (rounds 1–15), reserve — inventory only. Dev scored
pooled (2022/23–2024/25, n=684): 2.83 goals/match (H 1.56 / A 1.26),
HW .450, D .186, AW .364, OU1.5 .769, OU2.5 .544, OU3.5 .326,
BTTS .452.

NI is a mid-to-high-scoring league by European standards (J1 ≈ 2.6–2.7
goals/match; top-5 ≈ 2.6–2.9; LU-NationalDivision dev 3.15): OU2.5
over-rate 0.544 in the dev window. The level moves around without a
trend (2.73 → 2.84 → 3.10 → 2.54 → 2.93) — season-to-season swings of
±0.3 goals/match, no drift direction; the DC fit's 270-day half-life
decay is the mechanism that absorbs it, and no era split is imposed.
Home advantage is real but modest: home goals exceed away by
0.10–0.44 per match in every complete season (dev +0.30); HW rate
0.41–0.50, AW rate 0.33–0.41. The 2026/27 partial shows home = away
exactly (1.39/1.39) on 87 matches — noise at this n, noted not acted on.

## F2 — Team traits are reliable (goals)

Split-half by team-season (each team's matches in a season split
chronologically into first/second half; per-match GF and GA rates
correlated across halves):

| Window | Team-seasons | GF split-half r | GA split-half r |
|---|---|---|---|
| Dev era 2021/22–2024/25 | 48 | **0.591** | **0.735** |
| Scored window 2022/23–2024/25 | 36 | **0.615** | **0.754** |
| All complete 2021/22–2025/26 | 60 | 0.553 | 0.719 |

Both traits are clearly reliable — attack moderately (r ≈ 0.6),
defence strongly (r ≈ 0.73–0.75) — comfortably above the level at
which a Dixon-Coles rating fit is justified. (Method note: the split
is within team-season, so promotion/relegation turnover does not
inflate the correlation; n is team-seasons, not teams.) Defence is
the more stable trait here, the reverse of LU (GF 0.730 / GA 0.673).

## F3 — Halves: the frozen-constant question (goals)

1H share of goals from goal-event times (minute ≤ 45), dev scored
window 2022/23–2024/25: **0.4376** (845 / 1,931 goals, 683 matches
used; match 3907917 contributes 0 goals to numerator and denominator
— its halves are missing). Per-season shares: 2021/22 0.4671 (291/623),
2022/23 0.4363 (281/644), 2023/24 0.4470 (316/707), 2024/25 0.4276
(248/580), virgin 2025/26 0.4558 (304/667), reserve 2026/27 0.4215
(102/242). All complete seasons sit within ~1.5 SE of the frozen
value (per-season SE ≈ 0.02).

Per-match variance test (dev, scored matches with ≥1 goal, n=639):
observed variance of the per-match 1H share = 0.1094; binomial-noise
expectation E[var] = mean p(1−p)/goals = 0.1112; ratio 0.984;
implied true variance ≈ 0.0000, implied true SD ≈ 0.00pp. The
per-match 1H share variance is, within measurement error, EXACTLY
the binomial noise around a constant — there is no per-match signal
in the 1H share. The frozen-constant treatment is therefore the
correct one: **goals_1h_share = 0.4376**, applied at presentation
time only, never fitted per team or per match. (Same conclusion as
J1 and LU; the NI constant 0.4376 sits between LU's 0.4294 and J1's
0.412.)

## F4 — Format, turnover, and the mover question

- Format: 12 teams, 33 rounds + 5 split rounds (top-6/bottom-6),
  228 regular matches; 3 playoff matches excluded (see
  DATA_UNDERSTANDING.md). One team is relegated and one promoted
  every season: exactly ONE entrant per season (2022/23 Newry City
  AFC, 2023/24 Loughgall, 2024/25 Portadown, 2025/26 Bangor,
  2026/27 Limavady), each arriving from the Championship — a league
  that is NOT in the warehouse.
- **X2 mover offset: not estimable.** There is no sibling Northern
  Ireland league in the warehouse (only FotMob id 129), so no
  in-warehouse prior-tier history exists for any NI club and no mover
  tilt can be estimated from transitions. The single annual entrant
  starts at the league mean in both arms (as in LU). No ENTRANT arm.
- **SHRINK expectation:** the sanctioned G-J2-lesson variant is
  expected to be numerically identical to Gate Zero in this league:
  no team has 1–5 prior in-league matches in any scored season's
  training data (entrants have n=0; incumbents have n≥38 per prior
  season, i.e. n≥76 for a two-season fit) — the dev run states the
  fact mechanically either way.

## F5 — What does not exist (negative findings)

- SOT / corners / total shots: no stats feed and no shotmap in any
  of the 1,242 payloads, in any season. No candidate can be built;
  no virgin window contains these targets.
- Cards: no yellow-card data anywhere (events carry Red/YellowRed
  only, 261 events in 225 matches — fragmentary, not a target).
  Referee identity never present, so no referee strictness trait.
- xG: absent in every season — the goals model is goals-only
  throughout (the reference blend's documented fallback).
