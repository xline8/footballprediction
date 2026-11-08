# Step 3 — EDA: Russia Second League (FotMob 9123)

All numbers are on **finished, non-awarded** matches unless stated
otherwise, from `eda_numbers.json` (re-derived from the CSV). Season
label 2025 is shown for inventory only and excluded from every
interpretation (harvest fragment).

## 1. Levels per season

| season | n | mean goals | H / D / A | O2.5 | BTTS | 0-0 |
|---|---:|---:|---:|---:|---:|---:|
| 2021/2022 | 1,126 | 2.874 | .453 / .211 / .336 | .544 | .467 | .067 |
| 2022/2023 | 1,115 | 2.696 | .419 / .238 / .343 | .492 | .477 | .082 |
| 2023 (B) | 512 | 2.652 | .398 / .229 / .373 | .467 | .484 | .070 |
| 2023/2024 (A) | 362 | 2.210 | .434 / .304 / .262 | .387 | .436 | .135 |
| 2024 (B) | 904 | 2.687 | .450 / .216 / .334 | .502 | .482 | .077 |
| 2024/2025 (A) | 235 | 2.515 | .362 / .311 / .328 | .455 | .545 | .085 |
| 2025/2026 (A) | 156 | 2.590 | .423 / .276 / .301 | .474 | .481 | .096 |
| 2026 (B) | 760 | 2.861 | .454 / .199 / .347 | .546 | .518 | .059 |
| 2026/2027 (A) | 128 | 2.648 | .359 / .320 / .320 | .492 | .492 | .109 |
| 2025 (B, fragment) | 29 | 2.000 | .310 / .379 / .310 | .345 | .483 | .172 |

Reference points: the B track sits at 2.65–2.87 goals/match with a
home win rate ~.40–.45 — an ordinary scoring league, close to the
J.League/J2 region. The A track is lower-scoring and draw-heavier:
2023/2024 is the clear outlier at **2.21 goals, 30.4% draws, 13.5%
0-0** (Gold/Silver groups, 25 teams, stronger defences and more
even matchups). 2024/2025 and 2025/2026 A sit between (2.52–2.59).
Home advantage is stable across tracks (~.40–.45 home wins) except
the small in-progress 2026/2027 sample (.359, n=128).

SOT / corners / cards / total shots: **no levels exist** — the targets
are absent from every payload (DATA_UNDERSTANDING.md §4). There is
nothing to tabulate, and no proxy is constructed.

## 2. Team trait reliability (the J1 checklist, goals only)

Split-half by season: each team's matches split chronologically into
halves; Pearson r of per-match rates across halves (teams ≥8 matches);
pooled via Fisher z.

| trait | 21/22 | 22/23 | 2023 | 23/24 | 2024 | pooled |
|---|---:|---:|---:|---:|---:|---:|
| goals for | .572 | .379 | .442 | −.108 | .517 | **.378** |
| goals against | .663 | .511 | .475 | .175 | .600 | **.500** |

Team goal traits are **real but modest** — weaker than the J1
career-pooled figures, as expected for ~30-match seasons split into
~15-match halves (attenuation). The 2023/2024 goals-for value (−.108,
n=25 teams) is noise around that modest true value, not evidence
against the trait: the pooled estimate and four of five seasons are
positive. The Dixon-Coles ratings (attack/defence fitted per team)
are the correct carrier of this signal; no separate trailing-means
covariate is added.

## 3. Home advantage

Home win rate .40–.45 in every complete season; the DC fit estimates
home advantage per fit (production pattern), so no separate
investigation is needed.

## 4. Half shares — the frozen-constant question

Goal events with times exist for 3,758 matches (events era
2021/2022–2024, goal-count-reconciled). First-half share of goals:

- Pooled **0.4393** (4,757 of 10,829 goals in the first half).
- By season: 0.4379 / 0.4461 / 0.4514 / 0.4062 / 0.4368. The 2023/2024
  dip (0.4062, n=320 matches) is ~2 SE from the pooled value — noise.
- Variance decomposition on 3,698 matches with ≥1 goal: observed
  variance of the per-match 1H share 0.11510 vs binomial-noise
  expectation 0.11787 → **true variance 0.00000, true SD 0.0000**.

The program's halves conclusion holds exactly here: per-match 1H
share variance is pure noise. **Frozen goals 1H share = 0.4393**,
presentation only (FT → 1H/2H). No other market has a halves constant:
no splits exist for SOT, corners, cards or total shots, and those
targets do not exist at all.

## 5. Movers between tiers (X2)

Teams entering 9123 whose previous completed season was in 1. Division
(338), by FotMob team id: **9 entrants** across the dev era
(2022/2023: Metallurg Lipetsk, Tekstilshchik, Rotor Volgograd;
2023/2024: Ufa, Krasnodar II, Veles Moscow; 2024/2025: Volgar, Kuban;
2025/2026: Alania Vladikavkaz). **Zero entrants from the Premier
League (63)** in any season. First-season gaps vs the pooled league
mean: GF **−0.079**, GA **−0.021** per match — essentially zero, with
wide heterogeneity (Rotor +0.410 GF; Alania −0.315 GF / +0.726 GA).
Caveat: entrants land in the Gold group, which is stronger than the
pooled league mean, so the pooled gap understates their group-relative
standing; even so, no systematic offset is estimable (n=9). No
hard-coded tier offset is used; the sanctioned SHRINK arm is the
treatment for thin-history teams (FEATURES.md, X2).

Entrants to 9123 from below (promoted from regional/amateur football)
have no FotMob history: 16 in 2022/2023, 11 in 2023, 9 in 2024, 9 in
2026 (B). In the virgin window, 2026 B has 9 such teams and 2026/2027
A has 0 new teams. These teams start at the league mean under Gate
Zero; SHRINK is identical for them at n=0 and bites only at 1–5 prior
matches.

## 6. What the EDA rules out

- SOT / corners / total shots: no target, no features, no levels.
- Cards: no yellow target (stats empty; events carry dismissals
  only, 959 Red/YellowRed events, 0 plain Yellows; events absent
  after 2024). Referee strictness is unmeasurable (referee field
  empty in 6,558/6,558).
- xG / set-play / shot quality / box touches: no stats, no shotmap.
- Lineup / absence: lineup shells only (25 payloads, id/name, no
  players); closed per R6 regardless.
