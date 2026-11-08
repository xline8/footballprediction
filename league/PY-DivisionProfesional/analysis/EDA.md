# Step 3 — EDA: PY-DivisionProfesional

All numbers from `py_matches.csv` (1,480 matches, 2021–2026). Count
stats exist only in the stats era (2025+, n = 507) — every count level
below is stats-era only, by necessity, not by choice.

## F1 — Levels by tournament

| Season | n | goals | HW% | O2.5% | SOT | corners | cards* | shots |
|---|---|---|---|---|---|---|---|---|
| 2021 - Apertura | 90 | 2.60 | 35.6 | 50.0 | – | – | – | – |
| 2021 - Clausura | 90 | 2.47 | 30.0 | 46.7 | – | – | – | – |
| 2022 - Apertura | 132 | 2.55 | 38.6 | 51.5 | – | – | – | – |
| 2022 - Clausura | 132 | 2.45 | 50.8 | 45.5 | – | – | – | – |
| 2023 - Apertura | 132 | 2.40 | 37.9 | 40.2 | – | – | – | – |
| 2023 - Clausura | 132 | 2.64 | 37.9 | 49.2 | – | – | – | – |
| 2024 - Apertura | 132 | 2.57 | 34.8 | 47.0 | – | – | – | – |
| 2024 - Clausura | 132 | 2.10 | 38.6 | 38.6 | – | – | – | – |
| 2025 - Apertura | 132 | 2.18 | 32.6 | 37.9 | 7.80 | 8.14 | 4.64 | 25.14 |
| 2025 - Clausura | 132 | 2.58 | 39.4 | 41.7 | 8.17 | 9.05 | 4.87 | 25.10 |
| 2026 - Apertura | 132 | 2.44 | 44.7 | 43.2 | 8.01 | 8.44 | 4.21 | 24.56 |
| 2026 - Clausura† | 112 | 2.49 | 39.3 | 49.1 | 8.81 | 10.07 | 3.85 | 27.57 |

*cards = stats-feed column here (levels only); the modelling target is
event-unified (mean 4.92 dev era). †in progress.

- All-era goals level **2.45/match**, O2.5 44.8% — a low-scoring league
  (J1 ≈ 2.66; top-5 Europe ≈ 2.8–3.0). Home advantage is **small**:
  home − away goals = **+0.095/match**, HW 38.7% pooled. Apertura vs
  Clausura levels are near-identical for goals (2.448 vs 2.452) — the
  phase flag matters for block structure, not for level shifts.
- Count levels (stats era pooled): SOT **8.18**, corners **8.88**,
  total shots **25.52** — corners are low vs J1 (9.47) and far below
  SE-Allsvenskan (10.66); SOT is below J1's 9-ish as well, consistent
  with the low goals level.

## F2 — Team trait reliability (split-half, odd/even matches)

Career (goals, 20 teams ≥ 20 matches): goals-for **r = 0.79**,
goals-against **r = 0.70** — strong, DC has something real to fit.
Stats era (14 teams ≥ 10 matches, attenuated by the short era):

| trait | for | against |
|---|---|---|
| SOT | 0.83 | 0.66 |
| total shots | 0.81 | 0.78 |
| corners | 0.56 | 0.47 |
| yellows (stats col) | 0.37 | 0.51 |
| on-target rate (SOT/shots) | 0.48 | – |
| opp-box touches | 0.70 | – |
| big chances | 0.96 | – |

Traits are real for every count market. Yellows-for is the weakest
(0.37) — cards expectations stay modest. Opp-box touches correlate
0.389 per-match with corners (J1: 0.471) → X7 is adoptable here.

## F3 — Half shares: the frozen-constant question

| market | 1H share | obs var | noise var | true var |
|---|---|---|---|---|
| goals (events, n = 1,340) | 0.418 | 0.115 | 0.122 | ≈ 0 |
| SOT (splits) | 0.442 | 0.040 | 0.036 | 0.004 |
| corners (splits) | 0.492 | 0.037 | 0.034 | 0.003 |
| total shots (splits) | 0.465 | 0.010 | 0.010 | ≈ 0 |
| cards (events) | 0.327 | – | – | ≈ 0 (pooled share) |

Per-match 1H share variance is ≈ noise everywhere (the program's
usual result): **frozen league constants, presentation only** —
goals 0.418, SOT 0.442, corners 0.492, shots 0.465, cards 0.327.
Note corners' 1H share (0.492) is unusually high vs J1 (0.447).

## F4 — Referee

Split-half strictness r = 0.686 — but on only **7 referees** with ≥ 8
stats-era matches, and dev-era appointment coverage is 11.1%
(11.4 / 20.5 / 1.5 by tournament). The trait may be real; it is
**not measurable or usable on the dev window** → X8 DROPPED
(FEATURES), cards runs Gate Zero alone (K-J2 precedent: referee 0%
there; here it is merely ~11% and concentrated in the virgin era,
which must not be used to rescue an arm).

## F5 — Virgin-window behaviour (descriptive, read after the fact is not allowed pre-verdict; recorded in verdicts only)

The count virgin (2026 - Clausura, transitional) runs **hot** on
SOT/corners/shots (8.81 / 10.07 / 27.57 vs dev 8.09 / 8.75 / 24.83)
and **cold** on cards (event-unified ≈ 4.18 vs dev 4.89). Calibration
legs will feel this; the gates are not moved for it.
