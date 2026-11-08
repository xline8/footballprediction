# Step 6 — Model Design: PY-DivisionProfesional

## Feasibility matrix

| Market | Target exists? | Virgin window contains target? | Candidate |
|---|---|---|---|
| Goals | yes, all 1,480 | yes (2026 - Apertura, complete, n = 132) | **G-PY** |
| SOT | stats era only (507) | yes (2026 - Clausura†, n = 112) | **S-PY** |
| Corners | stats era only | yes (2026 - Clausura†, n = 112) | **C-PY** |
| Cards | events, stats era (event-unified target) | yes (2026 - Clausura†, n = 112) | **K-PY** |
| Total shots | stats era only | yes (2026 - Clausura†, n = 112) | **T-PY** |

†TRANSITIONAL virgin: 2026 - Clausura is still in progress (112 of
132 played at pull, last played 2026-11-08). Like J1's 2026, the
verdict is recorded on the played part and a season-end confirmatory
read is noted as outstanding. This is the honest consequence of the
stats feed starting in 2025: the only complete stats-era tournaments
are the three dev blocks; no complete virgin with count targets
exists yet. A goals-only outcome was the alternative; the matrix
above is the fuller honest read the brief asks for.

## Windows (frozen here, repeated in each prereg)

- **Goals** — seed: 2021-Ap + 2021-Cl (n = 180, training only).
  Dev eval blocks: 2022-Ap … 2025-Cl (8 tournaments, n = 1,056),
  season-blocked (tournament-blocked) walk-forward.
  Virgin: **2026 - Apertura (n = 132, complete)**. Reserved
  confirmatory: 2026 - Clausura (unread for goals).
- **Counts (S/C/K/T)** — seed: 2025 - Apertura (n = 132, training
  only). Dev eval blocks: 2025 - Clausura + 2026 - Apertura
  (n = 264; 263 scored for S/C/T after the target-missing clásico).
  Virgin: **2026 - Clausura TRANSITIONAL (n = 112 played)**.

## Candidates

- **G-PY (goals)** — production Dixon-Coles pattern (model_v2.py),
  goals-only (X1 degraded). Arms: **Gate Zero** + **SHRINK**
  (sanctioned new-team shrinkage, FEATURES). Primary metrics: 1X2 LL,
  RPS, OU2.5 LL vs climatology. No xG arm exists.
- **S-PY (SOT)** — production v5 pattern (model_sot.py: joint Poisson
  ridge + NB + Beta-Binomial on-target ratio), **without any xG
  input** (none exists). Arms: **Gate Zero** + **RS** (harder ratio
  shrinkage prior 20,000, the AU/SA-winning configuration). X4/X6
  analogues dropped (no shotmap). Primary line **7.5** (dev mean 8.09).
- **C-PY (corners)** — production model_corners_v3 pattern. Arms:
  **Gate Zero** (X9 covariates inside) + **X7** (opp-box touches
  territorial multiplier). Primary line **8.5** (dev mean 8.75).
- **K-PY (cards)** — production model_cards.py pattern, target =
  **event-unified yellows**. Arms: **Gate Zero only** (X8 dropped on
  dev-era referee coverage 11.1% — FEATURES). Primary line **4.5**
  (dev event-unified mean 4.89).
- **T-PY (total shots)** — shots family (experiments/ + J1 engine).
  Arms: **A** (v1 pattern), **B** (v2 level layer), **C** (E9
  trailing-r). Primary line **24.5** (dev mean 24.83).

## Gate frame (identical program-wide, per candidate prereg)

Dev gate: pooled dev LL at the primary line beats **both** baselines
(league base rate at the line; naive trailing-10) — goals: 1X2 LL +
RPS beat climatology and OU2.5 LL beats base rate. Arms failing dev
do **not** read the virgin. Virgin legs: (i) LL ≤ Gate Zero's and ≤
both baselines'; (ii) calibration |mean predicted − actual| ≤ 1.0pp
clean PASS, breach within 1 SE = PROVISIONAL PASS, beyond = FAIL;
(iii) per-block sign check on dev for variant arms. Both-pass → lower
virgin LL ships; ties → simpler arm. If Gate Zero fails its dev gate,
the candidate is FAIL and the virgin is NOT read.
