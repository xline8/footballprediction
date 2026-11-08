# Verdict — C-PE (Peru Liga 1 corners) — **PASS (provisional)**, shipped arm **X7**

Date: 2026-11-10. Branch `build/pe-liga1`. Prereg:
`league/PE-Liga1/prereg/PREREG_C_PE.md` (frozen in commit 2ca0c6f
before any fitting). Arms: Gate Zero (production corners pattern,
X9 covariates), X7 (opp-box touches multiplier component).
Primary line 9.5. Dev: seed 2021 blocks, evaluation 2022 -
Apertura … 2024 - Clausura (890 scored of 982). Virgin: calendar
2025, read ONCE (280 scored of 323; the predictions file carries
all 323 rows, actuals blank on the 43 target-missing rows).

## Dev results (pooled LL@9.5, n = 890)

| arm / baseline | LL@9.5 |
|---|---|
| Gate Zero | 0.679867 |
| X7 | **0.679829** |
| league base rate (harness, NB) | 0.730644 |
| naive trailing-10 | 0.726109 |

Per-block LL@9.5 (Gate Zero / X7): 2022-Ap 0.672684 / 0.672684;
2022-Cl 0.651751 / 0.646887; 2023-Ap 0.680819 / 0.685040;
2023-Cl 0.703836 / 0.705695; 2024-Ap 0.687172 / 0.689661;
2024-Cl 0.677564 / 0.671312.

> **Erratum (builder verification, 2026-11-10):** the first
> version of this section carried dev figures from a superseded
> intermediate corners run (the port's initial 8.5-fit-line run,
> before the frozen 9.5 line was restored and dev re-run). The
> table above is taken from the committed
> `engine/corners/results_dev.json`, which the builder
> independently re-ran and reproduced bit-identically, and whose
> pooled values the coordinator's own re-run also matched. No
> gate outcome changes: both arms beat both baselines under
> either figure set, and the X7 sign check is 3 of 6 under the
> corrected figures as well (blocks: 2022-Ap tie, 2022-Cl,
> 2024-Cl).

**Dev gate: both arms beat BOTH baselines — PASS** (also against
the coordinator's constant block-prior-rate robustness baseline,
0.696372).

## Virgin results (n = 280 scored, read once)

| arm / baseline | LL@9.5 | calibration (actual − predicted) | SE |
|---|---|---|---|
| Gate Zero | 0.665982 | −3.72 pp | 2.90 pp |
| X7 | **0.659291** | −3.42 pp | 2.88 pp |
| league base rate | 0.666045 | — | — |
| naive trailing-10 | 0.666558 | — | — |

Gate legs: (i) LL — X7 ≤ Gate Zero and ≤ both baselines ✓;
Gate Zero itself passes leg (i) against the league baseline by
only 0.00006 — recorded plainly, it is a hair's breadth.
(ii) Calibration — both arms breach the 1.0 pp clean bound but
sit within 1 SE of it (bounds + SE: 3.90 / 3.88 pp) →
**PROVISIONAL PASS** for both. (iii) X7 dev sign check: X7 LL ≤
Gate Zero in 3 of 6 dev blocks (one exact tie) ✓.

Both arms pass all legs → the lower virgin LL ships: **X7**.

## The X7 caveat, stated plainly

In the reference implementation the X7 arm's multiplier slot
uses the box-touch component **instead of** the Gate Zero
possession/big-chance multiplier, with its own fitted beta. On
both virgin block fits the touches beta selected is **0.0** —
the touches component contributed nothing on the virgin, and
the shipped virgin product is effectively the base corners
model with **no** territorial multiplier. X7's virgin win is
the removal of Gate Zero's fitted poss/bc multiplier
(−0.0025 / −0.025), which hurt on 2025. The prereg's gloss
"β = 0 collapses X7 to Gate Zero numerically" is imprecise for
this implementation: β = 0 collapses X7 to the multiplier-free
base. The gate arithmetic is unaffected (the arm is the
reference arm, fitted exactly as the reference fits it), but
nobody should read this PASS as evidence that box touches
predict corners in Peru — on this evidence they were not used.

## Verification performed

- Coordinator re-ran `run_c_pe.py dev`: `results_dev.json`
  bit-identical to the Codex-produced file.
- Shipped arm recomputed from the shipped predictions CSV:
  LL@9.5 = 0.659291, calibration +0.0342 (pred − actual),
  SE 0.0288 over the 280 scored rows — exact match.
- Coordinator correction before the virgin run: the ported
  virgin path fitted parameters ONCE on pre-2025 data for both
  2025 blocks; per the frozen MODEL_DESIGN frame it now fits
  per block (fit_n 1,100 for Apertura, 1,228 for Clausura —
  visible in `results_virgin.json`), and the predictions field
  list was restored (the port would have crashed on the PASS
  path). Feature construction is date-grouped causal
  (whole-date feeding), diff-verified against the reference.

## What ships

Arm **X7** as fitted per virgin block (gamma 0.3, r ≈ 1.44,
touches beta 0.0 — i.e. the multiplier-free base; see the
caveat). Virgin predictions: `league/PE-Liga1/predictions/
c_pe_virgin_predictions.csv` (FT + halves via the frozen
corners constant 0.4817, presentation only). Fitted params:
`engine/corners/fitted_params_virgin.json`. C-PE verdict:
**PASS (provisional)**.
