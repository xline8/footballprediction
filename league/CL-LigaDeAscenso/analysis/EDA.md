# Step 3 — EDA — CL-LigaDeAscenso

Numbers: `analysis/eda_numbers.json` (script `eda_compute.py`),
population = finished + regular (1,403 matches) unless stated.

## Levels by season

| season | n | teams | goals/match | home | away | HW rate | OU2.5 rate |
|---|---|---|---|---|---|---|---|
| 2021 | 178 | 16 | 2.393 | 1.326 | 1.067 | 0.371 | 0.433 |
| 2022 | 272 | 17 | 2.342 | 1.368 | 0.974 | 0.460 | 0.426 |
| 2023 | 240 | 16 | 2.592 | 1.450 | 1.142 | 0.463 | 0.504 |
| 2024 | 240 | 16 | 2.529 | 1.346 | 1.183 | 0.383 | 0.496 |
| 2025 (virgin) | 240 | 16 | 2.342 | 1.379 | 0.963 | 0.425 | 0.458 |
| 2026 (unread) | 233 | 16 | 2.644 | 1.541 | 1.103 | 0.442 | 0.476 |

Goals level ~2.34–2.59 — a touch below the parent Primera and the
J1 reference (~2.6–2.7), in line with a second tier. Home advantage
is real but variable (home/away goal ratio 1.14–1.43 by season).
SOT / corners / cards / total-shots levels **do not exist** — there
is no stats content in any season (DATA_UNDERSTANDING); the EDA
table for those markets is empty by fact, not by omission.

Dev pooled OU2.5 over-rate (2022–2024) = 356/752 = **0.473**, so the
primary goals line is OU 2.5.

## Trait reliability (split-half by team-season, chronological)

- Goals for: r = **0.198** (n = 97 team-seasons); goals against:
  r = **0.241**. Weak-to-modest — normal for a goals trait at this
  sample size; the DC reference does not consume split-half traits
  directly, and X5's stats consumers are not buildable here.
- SOT / corners / total shots / box touches: **not computable —
  zero rows carry the trait** (n = 0). Recorded as absent, never
  imputed.
- Event yellows: the naive split-half computation returns r = 0.959,
  which is an **era artefact, not a trait**: both halves of every
  2022–2024 team-season are ≈ 0 (the feed carries no plain yellows)
  and both halves of 2025 team-seasons are ≈ 6, so the correlation
  measures the feed-era level shift. It is not evidence for any
  cards feature and is not used anywhere.

## Halves (frozen-constant question)

Goal-event times exist from 2022 (2021 feed is empty). On
goal-events-complete finished regular matches of the **dev era
2022–2024** (n = 687 of 752; completeness is judged on goal events
vs score — 2022 is 272/272 on that test; the 65 exclusions are the
5 truncated-feed matches, 1 in 2023 and 4 in 2024, each missing all
its goal events, plus 60 goalless matches, which carry no share
information):

- pooled 1H share of goals = **0.4273**; mean-of-ratios 0.4231.
- Observed per-match share variance 0.1116 vs binomial sampling
  variance 0.1226 → **true variance estimate = 0.0**: per-match 1H
  share is pure noise around the constant, so a frozen constant is
  the honest presentation (same conclusion as the program-wide
  halves audits).
- Frozen constant: **goals_1h_share = 0.4273** (dev era only; the
  2022–2025 reference including the virgin reads 0.4264 and is
  recorded for comparison in `eda_numbers.json` but is **not**
  used — the constant was frozen without the virgin).
- Stats markets have **no halves source at all** (no period splits,
  no stats): they are FT-only by construction — moot, since they
  are not buildable.

## Referee

Coverage 0% in 2021–2024, 21.7% (54/252) in 2025, 0.9% in 2026.
No strictness reliability can be computed on the dev era (no
referee identities at all). X8 dropped (FEATURES).

## Format facts carried into design

Play-offs exist every season and are excluded (phase rule);
2022 is a 17-team season (272 regular matches); exactly 2
Primera-relegated teams arrive each season (X2 measurable against
the real parent corpus); 2026 is incomplete and unread.
