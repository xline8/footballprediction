# Verdict — S-ENGCH (England Championship SOT) — **PROVISIONAL PASS** (RS ships)

Prereg: `prereg/PREREG_S_ENGCH.md`. Primary line 7.5. Dev n=1,671,
virgin 2025/2026 n=555.

## Dev (pooled LL@7.5; baselines: league 0.6964, naive 0.6950)

| Arm | Dev LL | Per-season sign vs GZ | Dev outcome |
|---|---|---|---|
| GZ | 0.6855 | — | PASS |
| RS | 0.6855 (0.68545) | 2/3 | PASS |
| X4 | 0.6876 | 0/3 | beats baselines but sign leg (iii) fails → virgin NOT read |

## Virgin 2025/2026 (GZ + RS only, per the frozen rule)

| Arm | LL@7.5 | Calibration (SE) |
|---|---|---|
| GZ | 0.6807 | −2.71pp (2.09pp) |
| RS | **0.6798** | −2.64pp (2.09pp) |
| Baselines | naive 0.6860 / league 0.6902 | |

Gate arithmetic: leg (i) RS 0.6798 ≤ GZ 0.6807 and ≤ best baseline
0.6860 ✓; leg (ii) both arms breach 1pp but the excess (1.64–1.71pp)
is within 1 SE (2.09pp) → PROVISIONAL; leg (iii) RS 2/3 ✓.
Both-pass rule: lower pooled virgin LL ships → **RS (BB prior
20,000) ships, PROVISIONAL PASS**. The virgin season ran hot on SOT
(actual over-7.5 rate 0.564, recomputed from the raw CSV) and both
arms under-predicted it by ~2.7pp — inside the provisional band,
recorded as such, not rounded into a clean pass.

**Ships: RS** (`engine/sot/fitted_params_virgin.json`;
`predictions/s_engch_virgin_predictions.csv`; halves via 0.4548).
Independent checks: coordinator re-ran the goals/corners dev
harnesses bit-identically; the virgin over-7.5 actual rate (0.564)
and the predictions CSV's 555 RS rows were recomputed by hand.
