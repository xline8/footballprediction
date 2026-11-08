# S-BR verdict — PASS — arm RS (ratio-shrink) SHIPS

Prereg: `prereg/PREREG_S_BR.md` (frozen 7056902, before fitting).
Primary line 8.5. Dev pooled n = 1,140; virgin 2025 n = 380, read
once for the dev-passing, leg-(iii)-eligible arms (GZ, RS).

## Dev results — pooled LL@8.5

| Arm / baseline | LL@8.5 | Per-season (2022, 2023, 2024) |
|---|---|---|
| Gate Zero | 0.688842 | 0.697219 / 0.679925 / 0.689383 |
| RS | 0.688339 | 0.696579 / 0.679864 / 0.688576 |
| X4 | 0.690269 | 0.698051 / 0.679984 / 0.692774 |
| League base rate | 0.695199 | — |
| Naive trailing-10 | 0.699372 | — |

All three arms beat both baselines → all pass the dev gate.

## Virgin results (2025, n = 380)

| Arm / baseline | LL@8.5 | Calibration (pp) |
|---|---|---|
| Gate Zero | 0.687941 | +0.34 (SE 2.56) |
| RS | **0.686872** | +0.27 (SE 2.55) |
| League base rate | 0.693724 | +1.78 |
| Naive trailing-10 | 0.689958 | −0.65 |

## Gate arithmetic

- Leg (i): GZ 0.687941 ≤ best baseline 0.689958 ✓. RS 0.686872 ≤
  GZ's and ≤ best baseline ✓.
- Leg (ii): both calibrations inside 1.0pp → **clean PASS** for
  both arms (no provisional needed — the first clean calibration
  pass among the conveyor's count markets at this sample size).
- Leg (iii) sign check vs Gate Zero on dev: RS ≤ GZ in 3/3
  seasons ✓. **X4 ≤ GZ in 0/3 seasons → X4 fails leg (iii)** and
  cannot pass; its virgin was therefore not read (the outcome is
  determined by the frozen legs, and the 2025 window remains
  unburned for X4). Recorded plainly: X4 — the strongest X4
  reliability reading in the program (F6, r=0.571) — still loses
  to Gate Zero per-season on dev here, because its shotmap window
  only fills from 2023 and the 2024 season reverses hard
  (0.692774 vs 0.689383).
- Passing arms: Gate Zero and RS. Both-pass rule: lower pooled
  virgin LL ships → **RS (0.686872 < 0.687941)**.

**Ships:** arm RS — the v5 pattern with the Beta-Binomial prior
raised P = 200 → 20,000, i.e. in BR the on-target ratio component
earns its place only under much harder shrinkage toward the
league ratio. Fitted parameters in `engine/sot/
fitted_params_virgin.json` (NB r = 79.94 frozen; league means
home 5.098 / away 3.811); virgin predictions in
`predictions/s_br_virgin_predictions.csv` (380 rows, arm "RS";
FT ladder 7.5/8.5/9.5; 1H/2H presentation via frozen SOT constant
0.462). **BR joins the daily runner with SOT (arm RS).**
Coordinator verification: dev rerun reproduced pooled LLs
exactly; virgin LL@8.5 recomputed from the shipped predictions
CSV = 0.686872, matching the results JSON to 6dp. Corpus note:
the v5 engine keys teams by name and FotMob spells some clubs
two ways (e.g. "America MG" / "América-MG", one team_id) — the
split history affects all arms equally as part of the faithful
reference pattern; it is recorded here for the runner phase.
