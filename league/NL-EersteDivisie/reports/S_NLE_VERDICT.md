# S-NLE Verdict — Eerste Divisie shots-on-target model

Date: 2026-11-09. Branch `build/nl-eerste`. Prereg:
`league/NL-EersteDivisie/prereg/PREREG_S_NLE.md` (commit f267312,
frozen before any fitting). Engine:
`league/NL-EersteDivisie/engine/sot/`. Implementation by Codex
(gpt-5.6-luna) under the two-agent flow; dev and virgin headline
numbers were recomputed independently by the coordinator from the
per-match predictions CSVs (identical to the JSONs).
Calibration = actual − predicted. Predictions-only product: no
Eerste Divisie SOT odds source exists in-system — expected, not a
defect.

## Verdict: PASS (calibration PROVISIONAL) — Gate Zero ships

Gate Zero (the unmodified v5 pattern, goals-era inputs only — this
corpus has no xG) passes the dev gate and both virgin legs and
ships. RS (BB prior 200 → 20,000) also passes dev, then fails
virgin leg (i) by 0.00003 and the leg (iii) sign check 0/3, so it
cannot ship. The shipped file is
`predictions/s_nle_virgin_predictions.csv` (arm = GZ, force-added),
with fitted params in `engine/sot/fitted_params_virgin.json`.

## Dev results (per-match walk-forward, scored 2022/2023–2024/2025, n = 1140)

LL@9.5 (binary log-loss on P(over 9.5)):

| Season | n | Gate Zero | RS | Base rate | Naive t-10 |
|---|---|---|---|---|---|
| 2022/2023 | 380 | 0.6735 | 0.6746 | — | — |
| 2023/2024 | 380 | 0.6661 | 0.6675 | — | — |
| 2024/2025 | 380 | 0.6793 | 0.6805 | — | — |
| **Pooled** | 1140 | **0.6730** | **0.6742** | 0.6937 | 0.6793 |

Dev gate (pooled LL@9.5 beats BOTH baselines): Gate Zero **PASS**
(0.6730 < 0.6937, < 0.6793). RS **PASS** (0.6742 < both). Both arms
were read on the virgin window.

## Virgin results (season "2025/2026", n = 380, read once after dev froze)

Actual over-9.5 rate 57.11%; mean total SOT 10.24 (the virgin
season ran hot vs the dev mean of 9.64).

| Arm | LL@9.5 | Mean P(over 9.5) | Calib (actual − pred) | Calib SE |
|---|---|---|---|---|
| Gate Zero | **0.6809** | 54.17% | +2.94pp | 2.53pp |
| RS | 0.6809 (0.68090) | 54.16% | +2.95pp | 2.53pp |
| Base rate (constant) | 0.6970 | 48.75% | +8.36pp | — |
| Naive t-10 | 0.6841 | 55.86% | +1.15pp | — |

## Per-leg verdicts

| Leg | Gate Zero | RS |
|---|---|---|
| Dev gate | PASS | PASS |
| Virgin (i) LL ≤ Gate Zero's and ≤ best baseline's (0.6841) | PASS (0.6809) | **FAIL** (0.68090 > GZ 0.68087, by 0.00003) |
| Virgin (ii) calibration ≤1.0pp (breach ≤1 SE = provisional) | PROVISIONAL PASS (breach 1.94pp ≤ SE 2.53pp) | PROVISIONAL PASS (breach 1.95pp ≤ SE) |
| (iii) dev sign check vs Gate Zero | n/a | **FAIL (0/3 seasons)** |
| **Overall** | **PASS — ships** | FAIL |

Reading: the ratio-shrink question is settled negatively here —
shrinking the on-target ratio harder buys nothing at any point
(dev, virgin, calibration), and the unmodified v5 pattern is the
product. The virgin calibration breach is the hot-season pattern
seen across this league's count markets (2025/2026 ran hot on
SOT, corners and shots alike); it stays inside 1 SE, so the PASS
is provisional, not clean.

Coordinator correction applied to the shipped file: the ported
harness derived the 1H/2H presentation lines with the
NL-Eredivisie constant 0.446; the shipped CSV's halves columns
were regenerated with this league's frozen constant **0.451**
(FT probabilities — the gated quantities — are byte-identical).
The engine code was patched to 0.451 as well.
