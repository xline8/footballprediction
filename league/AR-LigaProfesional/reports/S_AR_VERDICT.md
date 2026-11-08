# S-AR Verdict — Liga Profesional shots-on-target model

Date: 2026-11-09. Branch `build/ar-liga`. Prereg:
`league/AR-LigaProfesional/prereg/PREREG_S_AR.md` (commit 7169cb5,
frozen before any fitting). Engine:
`league/AR-LigaProfesional/engine/sot/`. Implementation by Codex
(gpt-5.6-luna) under the two-agent flow; all numbers below were
reproduced by the coordinator's own reruns, and the virgin
calibration was recomputed independently from the predictions CSV
(see Verification notes). Predictions-only product: no Liga
Profesional SOT odds source exists in-system — expected, not a
defect.

## Verdict: FAIL — every arm passes dev, every arm fails the virgin calibration leg

All four arms pass the dev gate (X6 on its era folds) and are read
on the virgin window. On the virgin, Gate Zero passes the LL leg
but its calibration breach (−4.24pp) exceeds 1 SE (3.17pp); the
three variants fail the LL leg as well (RS by 0.00003) and fail
calibration by the same margin. The virgin block ran hot on SOT
(actual over-7.5 rate 58.75% vs dev-era level ~51%) and the
walk-forward levels lagged it. Nothing ships. The virgin
predictions CSV on file is the Gate Zero fallback product,
labelled `arm = GZ`.

## Dev results (per-match walk-forward, scored 2022 – 2026 - Apertura, n = 1,854)

LL@7.5 (binary log-loss on P(over 7.5); lower is better), pooled:

| Gate Zero | RS | X4 | X6 (pooled) | Base rate | Naive t-10 |
|---|---|---|---|---|---|
| 0.6896 | 0.6892 | 0.6907 | 0.6927 | 0.6940 | 0.6991 |

X6 dev judging (frozen era exception — era folds = scored dev
matches dated ≥ 2025-01-01, n = 720): X6 **0.6902** vs base rate
0.6934 and naive 0.6909 on the same subset → passes its dev gate.
Gate Zero on the same era subset: 0.6830 (used for X6's sign
check below).

Dev gate (pooled LL@7.5 beats BOTH baselines; X6 on era folds):
Gate Zero **PASS**, RS **PASS**, X4 **PASS**, X6 **PASS** (era).
All four arms were therefore read on the virgin window. X4 was
active on 75.6% of scored dev matches (shotmap era only, as
designed); X6's trait was active on 32.5%.

## Virgin results (block "2026 - Clausura", n = 240, read once after dev froze)

Actual over-7.5 rate 58.75%; mean total SOT 8.52.

| Arm | LL@7.5 | Mean P(over 7.5) | Calib diff | Calib SE |
|---|---|---|---|---|
| Gate Zero | **0.6782** | 54.51% | −4.24pp | 3.17pp |
| RS | 0.6783 | 54.53% | −4.23pp | 3.17pp |
| X4 | 0.6802 | 54.49% | −4.25pp | 3.18pp |
| X6 | 0.6850 | 54.21% | −4.63pp | 3.19pp |
| Base rate (baseline) | 0.6897 | 51.20% | −7.72pp | — |
| Naive t-10 (baseline) | 0.6856 | 57.56% | −1.18pp | — |

## Per-leg verdicts

| Leg | Gate Zero | RS | X4 | X6 |
|---|---|---|---|---|
| Dev gate | PASS | PASS | PASS | PASS (era folds) |
| Virgin (i) LL ≤ Gate Zero (0.6782) and ≤ best baseline (0.6856) | PASS | FAIL (0.6783) | FAIL (0.6802) | FAIL (0.6850) |
| Virgin (ii) calibration ≤1.0pp (breach ≤1 SE = provisional) | FAIL (breach 3.24pp > SE 3.17pp) | FAIL (3.23 > 3.17) | FAIL (3.25 > 3.18) | FAIL (3.63 > 3.19) |
| Virgin (iii) dev sign check vs Gate Zero | n/a | PASS (4/6 blocks) | PASS (3/6 blocks) | FAIL (era 0.6902 > GZ era 0.6830) |
| **Overall** | **FAIL** | FAIL | FAIL | FAIL |

Gate Zero's calibration miss is narrow in SE terms (breach
3.24pp vs 1 SE 3.17pp) but the rule is mechanical and was applied
as written — this is the same leg that caught AT-Bundesliga's
count markets when their virgin season ran cold; here the virgin
block ran hot and the level lagged the other way. The variants
add nothing on the virgin: harder ratio shrinkage (RS) is a wash
(it fails leg (i) by three hundred-thousandths of a nat), the
xG/shot quality input (X4) is neutral, and the era-guarded xGOT
arm (X6) is worst — the quality traits price in no extra SOT on
a block whose SOT rise was a level shift, not a quality shift.

## Verification notes (coordinator, independent of Codex)

- Full harness rerun (dev + virgin) reproduces every dev and
  virgin number exactly.
- Independent recompute from the shipped predictions CSV
  (`s_ar_virgin_predictions.csv`, Gate Zero fallback): LL@7.5
  0.6782, calibration −4.24pp, SE 3.17pp, actual over-rate
  58.75% — identical to the harness's virgin table.
- Virgin isolation confirmed in code: the dev loader asserts no
  "2026 - Clausura" rows among scored matches (n = 1,854).
- Arm-activity diagnostics (Codex run, coordinator-checked):
  RS differs from Gate Zero on 2,394/2,419 matches (by
  construction); X4 differs on 1,642, of which 682 are pre-2025 —
  all in 2023–2024, where the shotmap exists (X4 is inactive in
  2021–2022, whose 703 matches carry no shotmap base); X6 differs
  from X4 on 842 era matches and is identical to X4 on every
  pre-2025 match — the era guard works as frozen.
