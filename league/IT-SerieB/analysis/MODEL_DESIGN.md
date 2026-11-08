# Step 6 — Model Design: IT-SerieB Candidates

Rules inherited from `league/J1/analysis/MODEL_DESIGN.md`: every
candidate names its production reference, Gate Zero is the
unmodified reference fitted per league, variants come only from
FEATURES.md adopted arms (max 2–3 per candidate), gates are the
program's frozen legs, a FAIL is a complete outcome. Worked
analogues: ES-LaLiga2 (same shape — rich stats feed, xG era inside
the virgin, heavy churn) and IT-SerieC (same country; opposite
coverage verdict).

Shared frame: dev = walk-forward over 2021/2022–2024/2025 (train
seed 2021/2022; evaluation 2022/2023–2024/2025, pooled n=1,169,
season-blocked for goals / per-match for counts); virgin =
2025/2026 (n=390, complete), read ONCE and only for arms passing
the dev gate; 2026/2027 (partial, n=110) reserved un-read as the
confirmatory window. Baselines: league base rate (prior-seasons
over-rate at the primary line) and naive trailing-10 (count
markets) / climatology (goals). **Calibration = actual −
predicted** throughout this league (the reverse sign of some
earlier leagues; every prereg and verdict states it). Calibration
rule: |breach| ≤ 1pp clean PASS; ≤ 1 SE beyond the boundary =
PROVISIONAL PASS; else FAIL. Primary line per candidate = the .5
line whose dev-eval (2022/2023–2024/2025 pooled) over-rate is
closest to 0.5. All model state is keyed on FotMob team_id (with
the documented Reggiana alias).

## Feasibility matrix

| Candidate | Target exists? | Virgin contains target? | Buildable |
|---|---|---|---|
| **G-ITB goals** | Yes — FT score 2,059/2,059 | Yes — 2025/2026 n=390 | **YES** |
| **S-ITB SOT** | Yes — stats feed 100% every season | Yes | **YES** |
| **C-ITB corners** | Yes — stats feed 100% every season | Yes | **YES** |
| **K-ITB cards** | Yes — event feed 100% every season (unified target) | Yes | **YES** |
| **T-ITB total shots** | Yes — stats feed 100% every season | Yes | **YES** |

| Candidate | Reference | Primary line (dev-eval over-rate) | Arms |
|---|---|---|---|
| G-ITB goals | production DC (model_v2 pattern), **goals-only** (X1 era-dead — documented fallback, J2/ES precedent) | OU 2.5 (0.450) + 1X2 LL/RPS | Gate Zero; SHRINK (thin-data prior — sanctioned G-J2-lesson arm); X2 mover tier offset (F4 magnitudes, Serie A/Serie C) |
| S-ITB SOT | model_sot.py v5 | 7.5 (0.549) | Gate Zero; RS ratio-shrink (X4/X6 era-dead — not built) |
| C-ITB corners | model_corners_v3 | 9.5 (0.478) | Gate Zero (X9) only (X7 dropped in FEATURES: for r=0.320 n=16, against r=−0.129) |
| K-ITB cards | model_cards.py | 4.5 (0.584, events) | Gate Zero only (X8 dropped in FEATURES, dev r=0.061; target = event-feed yellows) |
| T-ITB total shots | shots family (v1/v2/E9, as T-J1) | 25.5 (0.475) | A v1 pattern; B v2 level layer; C E9 trailing-r. Tuning season 2022/2023 (reported, not in gate pool); gate pool 2023/2024–2024/2025 (n=779) per the J1 tuning discipline |

Notes:
- G-ITB is goals-only **by design**: `expected_goals` exists in
  13 of 1,559 dev matches and the xG era starts inside the
  virgin — building an xG arm on one era is explicitly not done
  (ES precedent). Gate Zero is the reference architecture with
  its documented goals-only observation.
- SHRINK and X2 are both pre-registered before any fitting:
  SHRINK per the template's explicit G-J2-lesson sanction, X2 as
  this league's F4-measured feature. With 7 new clubs every
  season (35% churn), season openers are where an unmodified DC
  is most exposed.
- X2 membership is carried as a **frozen mover table** (team_id ×
  entry season → source tier) derived in EDA from team_id churn
  plus tier name matching — not re-derived by name at engine
  runtime (the Reggiana spelling split showed why).
- K-ITB's target is the event-feed yellow count (Phase 1): the
  stats feed is not one consistent quantity in this league.
- C-ITB runs one arm because its only variant failed the
  reliability standard in FEATURES; the arm cap is a ceiling,
  not a quota (ES S-ES precedent).
- T-ITB follows the J1 tuning discipline explicitly: 2022/2023
  is the tuning season (lambda, r_A, layer cell chosen there
  only) and is reported but never judges; the dev gate pool is
  2023/2024–2024/2025.
- The virgin season ran hot on goals/SOT/shots and cold on cards
  (EDA F1) — recorded here so calibration outcomes are read
  against the regime, not re-litigated after the fact.
- Halves presentation (all markets): FT + 1H/2H via the frozen
  ITB constants, presentation only, exactly as J1.
- Play-off / play-out rows are ordinary rows in every fit
  (PREPROCESSING rule 3); no phase feature anywhere.
- Predictions-only: no IT-SerieB odds/settlement source in-system.
