# Verdict — K-PE (Peru Liga 1 cards) — **FAIL** (dev gate; virgin NOT read)

Date: 2026-11-10. Branch `build/pe-liga1`. Prereg:
`league/PE-Liga1/prereg/PREREG_K_PE.md` (frozen in commit 2ca0c6f
before any fitting). Target: event-unified yellows including
second yellows, cards era 2023+ only (EDA F-feed-1: the event
feed carries no plain-yellow Card events in 2021–2022, and the
stats feed is absent from every dev Clausura block). Arms:
Gate Zero (production cards pattern), X8 (referee multiplier,
K_REF = 8, clamp [0.67, 1.50]). Primary line 4.5. Windows:
seed 2023 - Apertura (n = 165), dev evaluation 2023 - Clausura
… 2024 - Clausura (n = 475), online walk-forward.

## Dev results (pooled LL@4.5, n = 475)

| arm / baseline | LL@4.5 |
|---|---|
| Gate Zero | 0.712602 |
| X8 | **0.687450** |
| league base rate | 0.707846 |
| naive trailing-10 | 0.692826 |

Per-block LL@4.5 (Gate Zero / X8): 2023-Cl 0.738593 / 0.725063;
2024-Ap 0.685894 / 0.646464; 2024-Cl 0.710599 / 0.686887.

## Gate arithmetic (mechanical, prereg legs)

Dev gate — pooled dev LL@4.5 must beat BOTH baselines:

- **Gate Zero: 0.712602 > 0.707846 (league) ✗ and > 0.692826
  (naive) ✗ — fails against both baselines.**

Gate Zero failing its own dev gate makes the variant moot:
**verdict FAIL, virgin NOT read.** X8 beats both baselines on
dev (0.687450) and the referee trait behind it is the strongest
measured in the programme (split-half r = 0.769) — recorded
here as the obvious candidate for a future, separately
pre-registered design whose base arm is built differently. It
is NOT a rescue under this prereg, and no gate was moved.

Robustness: against the coordinator's constant block-prior-rate
baseline (0.747331 — weak, because the cards level shifted after
the seed block) Gate Zero would pass, but it still fails the
naive baseline under every reading, so the FAIL does not depend
on the baseline definition.

## Verification performed

- Coordinator re-ran `run_k_pe.py dev`: `results_dev.json`
  bit-identical to the Codex-produced file.
- Engine diffed against the CO-PrimeraA reference: `model.py`
  is identical except the docstring (HL = 270, K_PRIOR = 8,
  K_REF = 8, clamp [0.67, 1.50] as frozen). The harness applies
  the era filter, the corpus filter and the 4.5 gate line.
- Coordinator corrections to the virgin path (dormant — the
  short-circuit fires first): calibration line 5.5 → 4.5
  (a CO literal), leg (iii) count → at least half of the 3
  scored blocks, PE halves constant 0.3818 in the predictions
  writer. The virgin entry point short-circuits on the dev
  gate: `engine/cards/results_virgin.json` records
  `virgin_read: false`, verdict FAIL, and no 2025 row was read.

## Virgin

**Deliberately NOT read.** Calendar 2025 (n = 323) remains
untouched for this candidate.

## What ships

Nothing. No predictions CSV, no fitted params, no pipeline
join. K-PE verdict: **FAIL**.
