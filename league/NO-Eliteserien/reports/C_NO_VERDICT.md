# C-NO Verdict — NO-Eliteserien corners model

Date: 2026-11-09. Branch `build/no-eliteserien`. Prereg:
`league/NO-Eliteserien/prereg/PREREG_C_NO.md` (commit 48330b5).
Engine: `league/NO-Eliteserien/engine/corners/` (J1 corners engine
seed via AT, primary line retargeted to 10.5 per the AU precedent).
Numbers from the coordinator's own runs. Predictions-only scope.

## Verdict: PASS (calibration PROVISIONAL) — Gate Zero SHIPS.

Both arms pass the dev gate, X7 with the better dev LL. On the virgin
window Gate Zero has the lower LL and X7's box-touch beta again fits
to **0.0** on the virgin training window — the F9 trait is real
(r=0.935) but worth zero inside this multiplier structure, as in J1,
DK, AT, BR and AR. X7 also fails virgin leg (i) against Gate Zero.
Gate Zero's calibration breach (−3.62pp) is within 1 SE (3.16pp), so
the pass is PROVISIONAL. The shipped predictions CSV is Gate Zero's.

## Dev results (season-blocked walk-forward; scored 2022–2024, n=720)

LL@10.5:

| Season | n | Gate Zero | X7 | Base rate | Naive t-10 |
|---|---|---|---|---|---|
| 2022 | 240 | 0.6968 | 0.6933 | 0.7578 | 0.7415 |
| 2023 | 240 | 0.6836 | 0.6693 | 0.7178 | 0.7036 |
| 2024 | 240 | 0.6705 | 0.6776 | 0.7144 | 0.7013 |
| **Pooled** | 720 | **0.6836** | **0.6801** | 0.7300 | 0.7155 |

Dev gate: GZ PASS, X7 PASS. Sign check: X7 ≤ GZ in 2/3 seasons — PASS.

## Virgin results (season 2025, n=240, read once after dev froze)

Actual over-10.5 rate 48.75%; mean total corners 10.68.

| Arm | LL@10.5 | Mean P(over 10.5) | Calib diff | Calib SE |
|---|---|---|---|---|
| Gate Zero | 0.6720 | 45.13% | −3.62pp | 3.16pp |
| X7 | 0.6733 | 45.15% | −3.60pp | 3.16pp |
| Base rate | 0.7289 | 35.62% | −13.13pp | — |
| Naive t-10 | 0.7228 | 35.93% | −12.82pp | — |

Fitted virgin-window params: GZ gamma 0.45, NB r 1.2892,
beta [0.0025, 0.0]; X7 gamma 0.45, r 1.2892, beta_bt [0.0].

## Per-leg verdicts

| Leg | Gate Zero | X7 |
|---|---|---|
| Dev gate | PASS | PASS |
| Virgin (i) LL ≤ GZ (0.6720) and ≤ best baseline (0.7228) | PASS | FAIL (0.6733 > 0.6720) |
| Virgin (ii) calibration ≤1.0pp (breach ≤1 SE = provisional) | PROVISIONAL PASS (breach 2.62pp ≤ SE 3.16pp) | PROVISIONAL PASS (breach 2.60pp ≤ SE 3.16pp) |
| Virgin (iii) dev sign check | n/a | PASS (2/3) |
| **Overall** | **PASS (PROVISIONAL) — SHIPS** | **FAIL** |

## Verification notes
- Coordinator reran dev; pooled LLs match the implementer's run to
  6 decimals. A coordinator fix is in this engine: the implementer's
  port had dedented the virgin baseline loop so only the last
  baseline would have been recorded — caught on diff audit against
  AT and fixed before the virgin run (both baselines are present in
  `results_virgin.json`).
- Predictions CSV halves recomputed through the engine's own
  `core.over_prob` for a sample row (1H P(over 4.5) matches to full
  precision; the core's pmf uses a mu-dependent size transform, so a
  plain NB(r) recompute does not apply — noted to save a future
  auditor the same detour).
