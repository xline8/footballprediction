# Verdict — S-SCO (Scotland Premiership SOT) — **PROVISIONAL PASS** (Gate Zero ships)

Prereg: `prereg/PREREG_S_SCO.md`. Primary line 8.5. Dev n=684,
virgin 2025/2026 n=228.

## Dev (pooled LL@8.5; baselines: league 0.6895, naive 0.6883)
| Arm | Dev LL | Per-season sign vs GZ | Dev outcome |
|---|---|---|---|
| GZ | 0.6696 | — | PASS |
| RS | 0.6709 | 0/3 | beats baselines but sign leg (iii) fails → virgin NOT read |
| X4 | 0.6699 | 1/3 | sign leg (iii) fails → virgin NOT read |

## Virgin (GZ only, per the frozen rule)
LL@8.5 **0.6775** ≤ GZ (self) and ≤ best baseline (naive 0.6839,
league 0.6916) — leg (i) ✓. Calibration: mean P(over 8.5) − actual
= **+2.98pp**, SE 3.26pp → breach beyond 1pp but within 1 SE →
leg (ii) PROVISIONAL.

**Ships: Gate Zero** (`engine/sot/fitted_params_virgin.json`;
`predictions/s_sco_virgin_predictions.csv`; halves via 0.4492).
Independent check: virgin actual over-8.5 rate recomputed from the
raw CSV = 0.4693, matching the harness inputs exactly.
