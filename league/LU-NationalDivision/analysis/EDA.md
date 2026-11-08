# Step 3 — EDA: LU-NationalDivision

Source: `league/LU-NationalDivision/data/lu_matches.csv` (1,296 rows).
Windows: warm-up 2021/22 (n=240); dev scored 2022/23–2024/25
(n=720); virgin 2025/26 (n=240, complete — read only by the virgin
step); confirmatory reserve 2026/27 partial (n=96 — NOT read here
beyond the levels table below, which is inventory, not fitting).

## F1 — Levels per season (goals)

| Season | n | Goals/match | Home | Away | HW | D | AW | OU1.5 | OU2.5 | OU3.5 |
|---|---|---|---|---|---|---|---|---|---|---|
| 2021/2022 | 240 | 3.208 | 1.688 | 1.521 | .442 | .171 | .388 | .812 | .621 | .400 |
| 2022/2023 | 240 | 3.342 | 1.746 | 1.596 | .421 | .179 | .400 | .817 | .642 | .438 |
| 2023/2024 | 240 | 3.125 | 1.708 | 1.417 | .458 | .237 | .304 | .838 | .596 | .379 |
| 2024/2025 | 240 | 2.987 | 1.596 | 1.392 | .450 | .188 | .362 | .796 | .571 | .350 |
| 2025/2026 | 240 | 2.854 | 1.496 | 1.358 | .412 | .204 | .383 | .738 | .537 | .329 |
| 2026/2027* | 96 | 3.552 | 1.979 | 1.573 | .479 | .115 | .406 | .885 | .708 | .406 |

\* partial season (rounds 1–12), reserve — levels shown for inventory
only. Dev scored pooled (2022/23–2024/25, n=720): 3.151 goals/match
(H 1.683 / A 1.468), HW .443, D .201, AW .356, OU1.5 .817, OU2.5 .603,
OU3.5 .389.

LU is a high-scoring league by European standards (J1 ≈ 2.6–2.7
goals/match; top-5 ≈ 2.6–2.9): OU2.5 over-rate 0.60 in the dev window
is the highest of any score-only league built so far in the program.
The level drifts DOWN across the five complete seasons (3.21 → 3.34
→ 3.13 → 2.99 → 2.85) — a slow regime drift, not a step change; the
DC fit's 270-day half-life decay is the mechanism that absorbs it,
and no era split is imposed. Home advantage is modest and stable:
home goals exceed away by 0.17–0.33 per match in every complete
season; HW rate 0.41–0.46, AW rate 0.30–0.40.

## F2 — Team traits are reliable (goals)

Split-half by team-season (each team's matches in a season split
chronologically into first/second half; per-match GF and GA rates
correlated across halves):

| Window | Team-seasons | GF split-half r | GA split-half r |
|---|---|---|---|
| Dev era 2021/22–2024/25 | 64 | **0.730** | **0.673** |
| Scored window 2022/23–2024/25 | 48 | **0.742** | **0.627** |

Both traits are strongly reliable — stronger than SE-Ettan's
(GF 0.562/0.703, GA 0.742/0.604) and comfortably above the level at
which a Dixon-Coles rating fit is justified. Team attack/defence
ratings are real signal in this league, not noise. (Method note: the
split is within team-season, so promotion/relegation turnover does
not inflate the correlation; n is team-seasons, not teams.)

## F3 — Halves: the frozen-constant question (goals)

1H share of goals from event times (minute ≤ 45), dev scored window
2022/23–2024/25: **0.4294** (973 / 2,266 goals, 720 matches; match
4520839 contributes 0 goals to numerator and denominator — its
halves are missing). Per-season shares: 2021/22 0.4351 (n=770,
SE 0.018), 2022/23 0.4389 (802, 0.018), 2023/24 0.4253 (750, 0.018),
2024/25 0.4230 (714, 0.019), virgin 2025/26 0.4015 (685, 0.019).
Every complete season sits within ~1 SE of the pooled dev value;
there is no per-season pattern (no trend, no outlier season) and no
evidence of a per-team 1H-share trait to model (per-match 1H share
variance is consistent with binomial noise around the constant —
the same verdict as every league in the program so far). **Frozen
constant: goals_1h_share = 0.4294**, presentation only (FT → 1H/2H
splits of the fitted lambdas). The virgin season's 0.4015 is 1.5 SE
below the frozen value — noted, not acted on; the constant is frozen
from dev-era data by rule.

No halves constants exist for any other market: SOT, corners, cards
and total shots have no data at all (F5).

## F4 — Entrants (mover prior: no evidence base)

New teams per season vs the previous season: 2 (2022/23), 2
(2023/24), 3 (2024/25), 4 (2025/26), 4 (2026/27). Entrants arrive
from the Division of Honour, which is NOT in the warehouse, and
depart to it — so no entrant GF/GA tilt can be estimated from
in-warehouse prior-tier data at all (there is no second Luxembourg
league to measure against, and no cross-tier history for any LU
club). X2 is dropped on data absence, not on a failed reliability
check. The only pre-registered variant is therefore SHRINK (the
sanctioned G-J2-lesson arm), which bites only on teams with 1–5
prior in-league matches — with full 240-match seasons, no team in
any scored season's training data has 1–5 prior matches (entrants
have n=0 and sit at the league-mean fallback in both arms;
incumbents have n≥30), so SHRINK is expected to be numerically
identical to Gate Zero; the dev run will confirm or refute that
mechanically.

## F5 — SOT / corners / cards / total shots: no data, no candidate

- **SOT**: `content.stats` absent 1,296/1,296; shotmap shots empty
  1,296/1,296. No SOT target in any season. NOT BUILDABLE.
- **Corners**: same absence. NOT BUILDABLE.
- **Total shots**: same absence. NOT BUILDABLE.
- **Cards**: no yellow data anywhere (no stats feed; event cards
  are Red/YellowRed only, 385 events, 0.30/match). The cards market
  is a total-cards line (yellows + reds); the target does not exist.
  Red-card counts (0.30/match) are a rare-event descriptive series
  with no reliability evidence and no production analogue as a
  target. NOT BUILDABLE. Referee names are empty strings in all
  1,296 payloads, so referee strictness is unmeasurable even as a
  covariate — X8 dropped on absence.
- **xG**: absent in all seasons. The G candidate is goals-only
  throughout (the X1 blend's documented fallback).

## F6 — What the dev gate will have to beat

Dev scored baselines (pooled 2022/23–2024/25, n=720): climatology
(HW .443 / D .201 / AW .356; OU2.5 over-rate .603) and naive
trailing-10 (per-team trailing scoring means as independent-Poisson
lambdas). The league's high OU2.5 rate (0.603) and the downward
goals drift are the known headwinds: a DC fit that compresses
total-goals level toward the training mean while the actual level
falls will lose the OU2.5 leg to climatology — the exact failure
mode that killed G-SE. The 270-day decay is the only drift defence
in the frozen design; no post-hoc repair is permitted.
