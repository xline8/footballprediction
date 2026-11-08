# Verdict — T-SCOCH (Scotland Championship total shots)

**FAIL at the virgin LL leg (all arms). Nothing ships.**

Prereg: `prereg/PREREG_T_SCOCH.md`. Primary line 15.5 (this
feed's total_shots sums to ≈15/match — a feed-definition
property, taken as-is). Dev n=427 stats rows, virgin 2025/2026
n=177. All numbers recomputed by the coordinator from the
per-match prediction CSVs (see the export defect note below).
Calibration = predicted − actual.

## Dev (pooled LL@15.5; baselines: league 0.6921, naive 0.7044)

| Arm | Dev LL | Sign vs A | Dev outcome |
|---|---|---|---|
| A (v1) | 0.6846 | — | PASS |
| B (v2) | 0.6853 | 0/3 | PASS (gate), sign leg fails |
| C (E9) | 0.6843 | 2/3 | PASS |

## Virgin (all three arms read, per the frozen rule)

| Arm | Virgin LL@15.5 | Calibration | Legs |
|---|---|---|---|
| A | 0.64582 | +0.78pp → clean PASS | (i) FAIL |
| B | 0.64656 | +0.26pp → clean PASS | (i) FAIL, (iii) FAIL |
| C | 0.64471 | +1.00pp → clean PASS | (i) FAIL |
| league base rate | **0.64208** | — | — |
| naive trailing-10 | 0.66656 | — | — |

Leg (i) requires the arm's virgin LL ≤ the reference arm's and
≤ the best baseline's (0.64208). Every arm is worse than the
flat league base rate on the virgin, whose shots level fell to
13.35/match from the dev-era ≈15.1 — a level shift the
prior-seasons base rate absorbed better than the fitted ratings.
Calibration is clean for all arms; it does not rescue leg (i).

**T-SCOCH is FAIL. Nothing ships.**

## Defect (stated plainly)

The first Phase C export wrote `engine/total_shots/
predictions_virgin.csv` containing the DEV predictions (1,281
rows, 2022/2023–2024/2025) instead of the virgin rows — a writer
bug in the copied RU-1Division run script. The coordinator's
independent recomputation caught it (CSV LLs equalled the dev
numbers, not the JSON's). The writer was fixed, the virgin pass
re-run, and the regenerated CSV (531 rows, 2025/2026 only) now
reproduces the virgin metrics exactly (A 0.64582 / B 0.64656 /
C 0.64471; baselines 0.64208 / 0.66656 — unchanged from the first
run, so the metrics pass itself was sound; only the export was
wrong).
