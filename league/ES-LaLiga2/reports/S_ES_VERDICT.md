# Verdict — S-ES (ES-LaLiga2 SOT) — **PROVISIONAL PASS** (Gate Zero ships)

Prereg: `prereg/PREREG_S_ES.md`. Primary line 7.5. Dev n=1,404,
virgin 2025/2026 n=468. (X4/X6 not built — era-dead, FEATURES.)

## Dev (pooled LL@7.5; baselines: league 0.6981, naive 0.6830)

| Arm | Dev LL | Per-season sign vs GZ | Dev outcome |
|---|---|---|---|
| GZ | 0.6776 | — | PASS |
| RS | 0.6780 | 1/3 | beats baselines but sign leg (iii) fails → virgin NOT read |

## Virgin 2025/2026 (GZ only, per the frozen rule)

| Arm | LL@7.5 | Calibration (SE) |
|---|---|---|
| GZ | **0.6369** | −1.33pp (2.18pp) |
| Baselines | naive 0.6435 / league 0.6936 | |

Gate arithmetic: leg (i) GZ 0.6369 ≤ best baseline 0.6435 ✓;
leg (ii) breach 1.33pp exceeds the 1.0pp boundary by 0.33pp, within
1 SE (2.18pp) → PROVISIONAL; leg (iii) n/a for Gate Zero.
**Gate Zero ships, PROVISIONAL PASS.** The virgin season ran hot on
SOT (actual over-7.5 rate 0.605 vs dev 0.491) and the model
under-predicted it by 1.33pp — inside the provisional band, recorded
as such, not rounded into a clean pass. RS's harder ratio shrinkage
helped in 2022/2023 only and hurt in both later dev seasons; the
frozen sign rule kept it out of the virgin, as designed.

**Ships: Gate Zero** (`engine/sot/fitted_params_virgin.json`;
`predictions/s_es_virgin_predictions.csv`; halves via 0.4491).
Independent checks: coordinator re-ran the SOT dev harness
bit-identically (GZ 0.6776457194764814 to full precision); virgin
LL@7.5 (0.636912) and calibration (−1.334pp, SE 2.184pp) recomputed
by hand from the shipped predictions CSV; grep confirms GZ/RS read
no `sm_*` / `expected_goals` columns.
