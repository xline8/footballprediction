# K-NO-OBOS Lane 1 verdict — cards (event-unified yellows)

**FAIL at sealed leg (i). The single Lane 1 sealed read has been
made and this verdict is final. Nothing ships; no runner join.**

Lane 1 re-entry of the original K-NO-OBOS candidate, which failed
at the dev gate in the original run (`reports/K_NO_OBOS_VERDICT.md`)
with its sealed window deliberately unread. Fresh preregistration:
`prereg/PREREG_L1_K_NO_OBOS.md`, commit `bde0aefb` — the first
commit on branch `build/lane1-knoobos`, committed before any
sealed access. Arm of record: **X8 (referee covariate)**. Gate
Zero is retained as a baseline/comparator only; its dev veto —
the gate-architecture defect this entry corrects — no longer
preconditions the arm of record's sealed read. All other gate
legs are identical to the original prereg. Primary line 3.5.
Target: event-unified yellows. Calibration sign convention
(gate_lib): predicted − actual.

Execution: `league/NO-OBOSLigaen/engine/cards/run_k_obos_l1.py`,
through `league/gate_lib/`. The dev load asserted no sealed rows
(`assert_no_sealed_rows`); the dev pass was recorded as a
gate_lib token (`engine/cards/dev_pass_registry_l1.json`); the
2026 rows were then loaded ONCE through the fail-closed sealed
loader (`load_sealed_rows`), in a separate process from the dev
evaluation.

## Dev (walk-forward, warm-up 2021, scored 2022–2025, n=960)

Recomputed via gate_lib before the sealed read. The L1 dev
artefact (`engine/cards/results_dev_l1.json`) is identical to
the frozen `results_dev.json` on every cell of every arm,
season, method and line — the documented dev pass reproduces
exactly, within artefact rounding (in fact bit-for-bit).

| Arm / baseline | Pooled LL@3.5 |
|---|---|
| **X8 (arm of record)** | **0.655345** |
| Gate Zero | 0.669336 |
| League base rate | 0.668295 |
| Naive trailing-10 | 0.672943 |

Dev gate (arm of record beats BOTH baselines): **PASS** —
0.655345 < 0.668295 and < 0.672943 (documented: 0.6553 vs
0.6683 / 0.6729).

Per-season LL@3.5 (sign check, leg iii):

| Season | X8 | Gate Zero | X8 ≤ GZ |
|---|---|---|---|
| 2022 | 0.638483 | 0.647133 | yes |
| 2023 | 0.663150 | 0.670967 | yes |
| 2024 | 0.662828 | 0.670642 | yes |
| 2025 | 0.656921 | 0.688599 | yes |

Sign check: **4/4 seasons** (needed ≥ half) — leg (iii) PASS.

### P6 worst-fold block — NO-OBOSLigaen cards (primary metric: ll_3.5)

Source: `league/NO-OBOSLigaen/engine/cards/results_dev_l1.json` (persisted dev artefacts; information only — no gate change).
Worst dev season (highest ll_3.5 for the reference arm): **2025**.

| Entity | Pooled ll_3.5 | Pooled source | Worst-season (2025) ll_3.5 | n (worst) | Δ vs pooled |
|---|---|---|---|---|---|
| gate_zero | 0.6693 | n-weighted, computed | 0.6886 | 240 | +0.0193 |
| gate_zero [base] | 0.6683 | n-weighted, computed | 0.6774 | 240 | +0.0091 |
| gate_zero [naive] | 0.6729 | n-weighted, computed | 0.7031 | 240 | +0.0302 |
| x8 | 0.6553 | n-weighted, computed | 0.6569 | 240 | +0.0016 |

Reading: even in its worst dev fold (2025) X8 (0.6569) still
beat both baselines on that fold (base 0.6774, naive 0.7031);
the pooled dev margin did not rest on one easy season.

## Sealed (virgin) — season 2026, n=240, read once

Online walk-forward continuing from the dev end state; both
arms and both baselines computed, Gate Zero as comparator
only. Artefact: `engine/cards/results_virgin_l1.json`.
Actual over-3.5 rate 0.4458 (107/240). Referee identity
coverage 229/240 = 95.4% (as the original prereg stated);
X8 fallbacks on the window: 11 unknown identity + 68 thin
history, so the referee multiplier was active on 161/240
matches and the remaining 79 took the Gate Zero prediction.

| Arm / baseline | Sealed LL@3.5 | Mean P(over 3.5) |
|---|---|---|
| X8 (arm of record) | 0.712425 | 0.4366 |
| Gate Zero | 0.696439 | 0.4302 |
| League base rate | 0.690062 | 0.4256 |
| Naive trailing-10 | 0.697490 | 0.4304 |

## Gate arithmetic

- **Leg (i) — LL ≤ Gate Zero's and ≤ best baseline's: FAIL.**
  X8 0.712425 is above Gate Zero's 0.696439 (by 0.0160) and
  above the best baseline, the league base rate's 0.690062
  (by 0.0224). It is also above naive trailing-10 (0.697490).
  On the sealed season the referee covariate did not merely
  fail to help — the arm finished last of the four.
- **Leg (ii) — calibration: PASS (inside tolerance).**
  X8 calibration (predicted − actual) = **−0.92pp**, SE
  3.29pp; |−0.92pp| ≤ 1.0pp, so the leg passes outright —
  no provisional question arises. (Gate Zero as comparator:
  −1.56pp, SE 3.24pp, which would have been a within-1-SE
  provisional breach; it is not a shipping candidate under
  this preregistration and is reported for context only.)
- **Leg (iii) — dev per-season sign check: PASS**, 4/4 (above).

One leg fails, and it is the decisive LL leg: **FAIL**.

## What ships

Nothing. No virgin predictions were written (the L1 harness
writes predictions only on PASS), no fitted params were
exported, and no runner-join change was prepared. The
referee operational gate for upcoming fixtures (k/N) is
therefore not applicable — it is run only for a PASS, per
the Lane 1 protocol. NO-OBOSLigaen's runner membership is
unchanged (corners only).

The 2026 window is now read for this candidate: it cannot be
re-used for a clean verdict for K-NO-OBOS under any later
preregistration. The honest summary of the Lane 1 test is
that correcting the gate architecture let the question be
asked properly — X8's dev signal (the program's strongest
referee reading, F8 r=0.715, a clean 4/4 sign check, and a
worst fold that still beat both baselines) did not survive
contact with the sealed season, where the arm's LL finished
behind Gate Zero, behind naive, and behind the base rate.
