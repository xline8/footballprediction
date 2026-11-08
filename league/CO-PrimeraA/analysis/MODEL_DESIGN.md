# Step 6 — Model Design: CO-PrimeraA

## Feasibility matrix

| candidate | target exists? | virgin window has target? | verdict |
|---|---|---|---|
| G-COA goals | YES (scores 2,582/2,582 finished) | YES (2026 - Apertura, n = 204) | **BUILD** |
| S-COA SOT | YES (stats feed ~100% from 2021) | YES | **BUILD** |
| C-COA corners | YES (stats feed ~100% from 2021) | YES | **BUILD** |
| K-COA cards | YES, era-restricted (event-unified from 2023 - Apertura; stats feed rejected — level break 2022) | YES (virgin is inside the era) | **BUILD (era-restricted)** |
| T-COA total shots | YES (stats feed ~100% from 2021) | YES | **BUILD** |

All five candidates are buildable — the opposite of the sibling
CO-PrimeraB (goals-only, stats feed absent there). The binding
constraints here are eras, not absence: xG/shotmap features are dead
(era starts at the virgin boundary), the cards target lives only in
its event era, and period splits (2023-Cl+) serve halves constants
only, never features.

## Windows (frozen here, repeated in each prereg)

- **Goals / SOT / corners / total shots** — seed: 2021 - Apertura +
  2021 - Clausura (n = 411, training only). Dev evaluation:
  tournament-blocked expanding walk-forward over 2022 - Apertura …
  2025 - Clausura (9 tournaments, n = 1,788; 1,787 scored for counts —
  one 2022 - Apertura match lacks stats). Virgin: **2026 - Apertura
  (n = 204, complete: 202 regular + 2 final, last match 2026-06-08)**,
  read ONCE. 2026 - Clausura is excluded everywhere (in progress).
- **Cards** — era 2023 - Apertura onward. Seed: 2023 - Apertura
  (n = 226, training only). Dev evaluation: 2023 - Clausura …
  2025 - Clausura (5 tournaments, n = 1,110). Virgin: 2026 - Apertura
  (n = 204), read ONCE.
- Season unit = the tournament (Apertura/Clausura), per the PY
  precedent for split calendars. Phase rule (frozen, DATA_UNDER-
  STANDING): all phases modelled, phase flagged, no phase feature.

## Candidates

- **G-COA (goals)** — production Dixon-Coles pattern (`model_v2.py`;
  the CO-PrimeraB / PY port), goals-only (X1 reduced). Arms:
  **Gate Zero** + **X2** (Primera B mover prior, FEATURES). No SHRINK
  arm (degenerate here — FEATURES). Primary metrics: 1X2 LL, RPS,
  OU2.5 LL vs climatology/base rate. Halves constant 0.4706.
- **S-COA (SOT)** — production v5 pattern (`model_sot.py`: joint
  Poisson ridge λ=100 + NB r=79.94 + Beta-Binomial on-target ratio),
  no xG input exists to consume. Arms: **Gate Zero** + **RS**
  (harder ratio shrinkage, prior 20,000). Primary line **7.5**
  (dev mean 8.10, dev over-rate 0.552). Halves constant 0.4862.
- **C-COA (corners)** — production `model_corners_v3` pattern. Arms:
  **Gate Zero** (X9 covariates inside) + **X7** (opp-box touches
  territorial multiplier). Primary line **8.5** (dev mean 9.16, dev
  over-rate 0.550). Halves constant 0.4956.
- **K-COA (cards)** — production `model_cards.py` pattern, target =
  **event-unified yellows**, era-restricted windows above. Arms:
  **Gate Zero** + **X8** (referee trailing-rate multiplier; dev-era
  coverage 0.94, strictness r = 0.487). Primary line **5.5** (dev-era
  mean 5.60, dev over-rate 0.524 on 2024–2025 blocks). Halves
  constant 0.3543.
- **T-COA (total shots)** — shots family (experiments/ + J1 engine).
  Arms: **A** (v1 pattern), **B** (v2 level layer), **C** (E9
  trailing-r). Primary line **24.5** (dev mean 25.06, dev over-rate
  0.526). Halves constant 0.4850.

## Gate frame (identical program-wide, per candidate prereg)

- Dev gate (counts): pooled dev LL at the primary line beats BOTH
  baselines (league base rate at the line; naive trailing-10).
  Goals: pooled dev 1X2 LL AND RPS beat climatology AND OU2.5 LL
  beats the base rate. An arm failing dev does not read the virgin.
  If Gate Zero fails its dev gate, the candidate is FAIL and the
  virgin is NOT read (variants moot).
- Virgin legs (dev-passers only, read ONCE): (i) LL leg — arm's
  virgin LL ≤ Gate Zero's AND ≤ the baselines'; (ii) calibration
  leg — |mean predicted − actual| at the primary line (goals: also
  home-win rate) ≤ 1.0pp clean PASS; a breach within 1 SE of the
  boundary = PROVISIONAL PASS; beyond = FAIL. Calibration is
  actual − predicted in reporting (sign stated in each verdict);
  the gate uses the absolute breach. (iii) per-block sign check on
  dev for variant arms (arm LL ≤ Gate Zero LL in at least half the
  dev blocks).
- Both-pass rule: if Gate Zero and a variant both pass, the lower
  pooled virgin LL ships; ties → the simpler arm. On PASS the
  winning arm's fitted params + virgin predictions ship; on FAIL
  nothing ships. No rescue arms; gates never move.
