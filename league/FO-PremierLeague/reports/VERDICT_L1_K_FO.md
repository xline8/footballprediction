# Verdict — Lane 1 re-entry L1-K-FO (Faroe Islands Premier League cards)

**CLEAN PASS — arm of record SHRINK ships.**

Lane 1 entry under `league/IMPROVEMENT_PROGRAM.md` (unread sealed
window) and `league/improvement_scratch/LANE1_WAVE1/cohort_report.md`
§1.2/§1.5/§3 row 2. Fresh preregistration:
`league/FO-PremierLeague/prereg/PREREG_L1_K_FO.md`, commit
`49dc7666ff6d0a89849dc4fc03dbc2db44b2564d` — the branch's first
commit, preceding any sealed access. Branch `build/lane1-kfo`.
Original candidate: `PREREG_K_FO.md` / `K_FO_VERDICT.md` (FAIL at
the dev gate; virgin deliberately NOT read — the defect this entry
corrects is Gate Zero's dev veto over a dev-passing variant,
nothing else). All runs via `league/gate_lib/` (dev-pass assertion
before the sealed load, mechanical prereg tokens, calibration sign
convention predicted − actual) with the P2 design seal (no new
EDA; dev-era seasons only before the read) and P6 worst-fold
reporting below. Sealed window read ONCE, through the gate_lib
sealed loader, after the dev-pass token was recorded. Verdict
final.

## Dev evaluation (recomputed, dev data only, n = 539)

Recomputed with the frozen league engine via
`engine/cards/run_l1_k_fo.py dev` (Gate Zero `Online(8)`, SHRINK
`Online(16)`, r from the 2021 warm-up causal records only):
**every documented pooled number reproduces exactly** — absolute
difference 0.0 for all four methods against the full-precision
values persisted in the original `results_dev.json` — so the STOP
condition did not trigger.

Pooled dev LL@3.5 (scored seasons 2022–2025):

| Method | LL@3.5 | Result |
|---|---:|---|
| **SHRINK (arm of record)** | **0.681000** | beats BOTH baselines |
| Gate Zero (comparator) | 0.684736 | fails vs base rate, as documented |
| League base rate | 0.682420 | — |
| Naive trailing-10 | 0.693044 | — |

NB size r (dev, from 2021 warm-up): Gate Zero model 72.79,
SHRINK model 138.75, base 500 (clipped), naive 66.37 — identical
to the original build.

Sign check (sealed leg iii, on dev): SHRINK dev LL@3.5 ≤ Gate
Zero in **3 of 4** dev seasons (2022 0.6816 vs 0.6869; 2023
0.6760 vs 0.6829; 2024 0.6808 vs 0.6848; 2025 0.6856 vs 0.6843) —
PASS (≥2 of 4 required).

Dev-pass token for candidate `L1-K-FO` recorded in
`engine/cards/dev_pass_registry_l1.json` before the sealed load.

## Sealed read (virgin 2026, n = 135, one read)

One fresh online pass over 2021–2026; r per method re-estimated
from causal predictions over 2021–2025 only, then frozen
(SHRINK model r = 31.40, Gate Zero model r = 28.27, base 30.73,
naive 28.45). Calibration is predicted − actual (gate_lib
convention).

| Quantity @3.5 | SHRINK | Gate Zero | Base rate | Naive t-10 |
|---|---:|---:|---:|---:|
| LL | **0.686989** | 0.688355 | 0.693280 | 0.730895 |
| Mean P(over 3.5) | 0.5344 | 0.5338 | 0.5304 | 0.4947 |
| Actual over rate | 0.5407 | 0.5407 | 0.5407 | 0.5407 |
| Calibration (pred − actual) | **−0.63 pp** (SE 4.29 pp) | −0.69 pp (SE 4.30 pp) | — | — |

Context line @4.5: SHRINK LL 0.614426, Gate Zero 0.612304, base
0.628198, naive 0.632783 (context only; no leg consumes it).

Sealed legs:

- **(i) LL leg — PASS.** SHRINK 0.686989 ≤ Gate Zero 0.688355
  (margin −0.001365) and ≤ best baseline (base rate 0.693280,
  margin −0.006290; naive 0.730895).
- **(ii) Calibration leg — PASS (clean).** Predicted − actual =
  **−0.634 pp**, SE 4.293 pp; |−0.634| ≤ 1.0 pp.
- **(iii) Sign check — PASS** (3 of 4 dev seasons, above).

Both-pass semantics: Gate Zero is a comparator only and cannot
ship under this entry (its dev failure is a reproduced fact);
the arm of record passes every leg cleanly, so the verdict is
**CLEAN PASS** and SHRINK ships.

Independent verification: every sealed SHRINK number above was
recomputed from the shipped virgin predictions CSV alone
(second code path, gate_lib `virgin_csv_metrics`) and matches
`results_virgin_l1.json` exactly (LL 0.6869894205962768,
calibration −0.6344852736776498 pp, SE 4.292714092039349 pp;
135 rows, arm `shrink`).

## P6 worst-fold block (information only, no gate change)

### P6 worst-fold block — FO-PremierLeague cards (primary metric: ll_3.5)

Source: `league/FO-PremierLeague/engine/cards/results_dev.json` (persisted dev artefacts; information only — no gate change).
Worst dev season (highest ll_3.5 for the reference arm): **2022**.

| Entity | Pooled ll_3.5 | Pooled source | Worst-season (2022) ll_3.5 | n (worst) | Δ vs pooled |
|---|---|---|---|---|---|
| gate_zero | 0.6847 | n-weighted, computed | 0.6869 | 134 | +0.0022 |
| gate_zero [base] | 0.6824 | n-weighted, computed | 0.6804 | 134 | -0.0020 |
| gate_zero [naive] | 0.6930 | n-weighted, computed | 0.7034 | 134 | +0.0104 |
| shrink | 0.6810 | n-weighted, computed | 0.6816 | 134 | +0.0006 |

Reading: in the worst dev fold (2022) SHRINK (0.6816) still beats
Gate Zero (0.6869) and naive (0.7034) but loses to the base rate
(0.6804) by 0.0012 — the pooled dev edge over the base rate
(0.0014) is thin and does not hold in every fold, exactly the
thinness the cohort report flagged for this candidate. The sealed
read, not the pooled dev margin, is the verdict's evidence.

## Operational check (referee availability)

Referee identity coverage is **0/810** matches, as in the
original build. No referee arm exists and none is needed: SHRINK
uses no referee data, so there is no referee operational gate and
no fallback condition attached to this PASS.

## What ships

SHRINK (K_PRIOR = 16), clean: virgin predictions
`league/FO-PremierLeague/predictions/k_fo_virgin_predictions.csv`
(135 rows; 1H/2H presentation via the frozen cards constant
0.348), fitted params `engine/cards/fitted_params_virgin_l1.json`,
sealed results `engine/cards/results_virgin_l1.json`, dev
recomputation `engine/cards/results_dev_l1.json`. A runner-join
change for the cards market (arm `shrink`) is prepared on this
branch, following the existing cards wiring in `league/runner/`;
it is NOT merged by this verdict.
