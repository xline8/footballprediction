# K-AR Verdict — Liga Profesional cards model

Date: 2026-11-09. Branch `build/ar-liga`. Prereg:
`league/AR-LigaProfesional/prereg/PREREG_K_AR.md` (commit 7169cb5,
frozen before any fitting). Engine:
`league/AR-LigaProfesional/engine/cards/`. Implementation by Codex
(gpt-5.6-luna) under the two-agent flow; all numbers below were
reproduced by the coordinator's own reruns, and the virgin
calibration was recomputed independently from the predictions CSV
joined to the match table (see Verification notes).
Predictions-only product: no Liga Profesional cards odds source
exists in-system — expected, not a defect.

Target reminder: unified yellows from the **event feed** in this
league (the stats-feed `yellow_cards` key is not one consistent
quantity here — Phase 1 §3.3, PREPROCESSING rule 5).

## Verdict: FAIL — the referee arm is a genuine dev win that the virgin calibration leg kills

Both arms pass the dev gate. X8 (referee covariate) is the
strongest variant-arm dev result in this league: pooled dev
LL@4.5 0.6610 vs Gate Zero 0.6768, ahead in **all six** scored
blocks. On the virgin both arms pass the LL leg — and both fail
calibration: the virgin block's card level fell (event-yellows
mean 4.59 vs dev 4.92; actual over-4.5 rate 50.42%) while the
decayed ratings still priced the dev-era level (mean predicted
55.37% Gate Zero, ~56.0% X8), giving breaches of +4.95pp and
+5.95pp against SEs of 3.24pp/3.22pp — beyond the provisional
band. Nothing ships. The virgin predictions CSV on file is the
Gate Zero fallback product, labelled `arm = gate_zero`.

## Dev results (per-match walk-forward, scored blocks 2022 – 2026 - Apertura, n = 1,854)

LL@4.5, pooled:

| Gate Zero | X8 | Base rate | Naive t-10 |
|---|---|---|---|
| 0.6768 | **0.6610** | 0.6840 | 0.6771 |

Per-block LL@4.5: X8 beats Gate Zero in 6/6 blocks (2022: 0.6719
vs 0.6859; 2023: 0.6639 vs 0.6763; 2024: 0.6608 vs 0.6778;
2025 - Apertura: 0.6377 vs 0.6711; 2025 - Clausura: 0.6519 vs
0.6633; 2026 - Apertura: 0.6716 vs 0.6808).

Dev gate (pooled LL@4.5 beats BOTH baselines): Gate Zero **PASS**
(0.6768 < 0.6840 and < 0.6771 — the naive margin is 0.0003, the
tightest dev pass in this league). X8 **PASS** (0.6610 < both).
Both arms were therefore read on the virgin window.

Referee operational check (from the harness, coordinator-
verified against Phase 1): warehouse referee coverage by block —
2021: 0/325 (field empty; warm-up only), 2022: 378/378, 2023:
376/378, 2024: 378/378, 2025 - Apertura: 238/240,
2025 - Clausura: 240/240, 2026 - Apertura: 218/240, virgin block
2026 - Clausura: **240/240**. X8 was therefore honestly testable
on the window that decides (unlike K-J1, whose virgin referee
coverage was 0.5%). In the virgin run, 56/240 fixtures had a
referee with <8 prior in-league matches and took the preregistered
shrunk-mean fallback; none had an unknown identity. Warehouse
records are post-match snapshots with no publication timestamp,
so pre-match appointment availability cannot be proven from them;
the operating rule stands as registered (unknown/thin-history →
Gate Zero for that fixture, no imputation).

## Virgin results (block "2026 - Clausura", n = 240, read once after dev froze)

Actual over-4.5 rate 50.42%; mean total yellows (event) 4.59.

| Arm | LL@4.5 | Mean P(over 4.5) | Calib diff | Calib SE |
|---|---|---|---|---|
| Gate Zero | 0.7009 | 55.37% | +4.95pp | 3.24pp |
| X8 | **0.6956** | ≈56.0% | +5.95pp | 3.22pp |
| Base rate (baseline) | 0.7015 | 55.64% | — | — |
| Naive t-10 (baseline) | 0.7166 | 50.23% | — | — |

## Per-leg verdicts

| Leg | Gate Zero | X8 |
|---|---|---|
| Dev gate | PASS | PASS |
| Virgin (i) LL ≤ Gate Zero (0.7009) and ≤ best baseline (0.7015) | PASS (0.7009 ≤ 0.7015, by 0.0006) | PASS (0.6956) |
| Virgin (ii) calibration ≤1.0pp (breach ≤1 SE = provisional) | FAIL (breach 3.95pp > SE 3.24pp) | FAIL (breach 4.95pp > SE 3.22pp) |
| Virgin (iii) dev sign check vs Gate Zero (≥3 of 6 blocks) | n/a | PASS (6/6 blocks) |
| **Overall** | **FAIL** | **FAIL** |

Reading: the referee trait (F8, split-half r = 0.724 — the
program's strongest) does real work on dev and even wins the
virgin LL leg outright; what neither arm survives is a level
shift in the virgin block. The naive baseline's virgin mean
(50.23%) shows a trailing-10 window adapted to the lower level
within weeks, while the HL-270 decayed ratings carried the old
regime — the same failure shape as K-J2's dev diagnosis, here on
the virgin. That is a diagnosis for a possible future prereg
(shorter level memory for cards in this league), not a rescue:
the frozen legs are the legs.

## Verification notes (coordinator, independent of Codex)

- Full harness rerun (dev + virgin) reproduces every dev and
  virgin number exactly.
- Independent recompute: the predictions CSV (Gate Zero fallback)
  joined by match_id to the match table's event yellows gives
  LL@4.5 0.7009, calibration +4.95pp, SE 3.24pp, actual over-rate
  50.42% — identical to the harness. (The harness JSON stores
  this calibration under the inherited key name `diff_2_5`; the
  value is the 4.5-line figure, as the recompute proves. The
  results_dev.csv column headers likewise retain the port's
  ll_2_5/ll_3_5 names while carrying the 4.5/5.5 values; the JSON
  files govern.)
- NB size: as in the accepted J1/NL ports of this harness, the
  NB size is estimated by moments on the warm-up records only
  (never on scored data); Gate Zero's model r hit the port's 500
  cap because event-feed yellows in this league are near-Poisson
  (dispersion ≈0.95), so the NB is effectively Poisson. Recorded
  because the prereg text cites production's 112.39: the ported
  harness's frozen behaviour — identical in J1 and NL — is what
  ran, and with r ≥ 140 for every scorer the distinction is
  numerically minor here.
- The virgin protocol block in the harness JSON carries a stale
  `rows: 306` label (an NL leftover); the scored virgin n is 240
  in every metric row, as the recompute confirms.
