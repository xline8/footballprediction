# Verdict — Lane 1 re-entry G-TZ-L1 (Tanzania Premier League goals)

**PROVISIONAL PASS — arm of record SHRINK ships provisionally.**

Lane 1 entry under `league/IMPROVEMENT_PROGRAM.md` (unread sealed
window) and `league/improvement_scratch/LANE1_WAVE1/cohort_report.md`
§1.5/§3 row 9. Fresh preregistration:
`league/TZ-PremierLeague/prereg/PREREG_L1_G_TZ.md`, commit
`2b5b21a41332954d7313db5f876c66001b6d4855` — the branch's first
commit, preceding any sealed access. Branch `build/lane1-gtz`.
Original candidate: `PREREG_G_TZ.md` / `G_TZ_VERDICT.md` (FAIL at the
dev gate; virgin deliberately NOT read — the defect this entry
corrects is Gate Zero's dev veto over a dev-passing variant, nothing
else). All runs via `league/gate_lib/` (dev-pass assertion before the
sealed load, mechanical prereg tokens, calibration sign convention
predicted − actual) with the P2 design seal (no new EDA; dev-era
seasons only before the read) and P6 worst-fold reporting below.
Sealed window read ONCE, through the gate_lib sealed loader, after
the dev-pass token was recorded. Verdict final.

## Dev evaluation (recomputed, dev data only, n = 720)

Recomputed with the league engine via
`engine/goals/run_lane1.py dev`; cross-checked through gate_lib's
`normalise_goals_dev` against the persisted original artefact
(`results_dev.json`): **max absolute difference 0.0** over every
per-season and pooled row — the documented dev numbers reproduce
exactly, so the STOP condition did not trigger.

Pooled dev legs (arm of record SHRINK vs climatology):

| Leg | SHRINK | Climatology / base rate | Margin | Result |
|---|---:|---:|---:|---|
| 1X2 LL vs climatology | 0.925501 | 1.069080 | −0.143579 | PASS |
| RPS vs climatology | 0.180158 | 0.223944 | −0.043786 | PASS |
| OU2.5 LL vs base rate | 0.689404 | 0.692720 | −0.003316 | PASS |

Gate Zero (baseline only, recomputed): pooled 1X2 LL 0.956279,
RPS 0.185632, OU2.5 LL 0.716160 — it again fails the OU leg, as
documented; under this entry that no longer vetoes the arm of
record. SHRINK differs from Gate Zero on 60 of 720 rows (0 in
2022/2023, 30 in 2023/2024 — Fountain Gate FC, n = 1 prior match
under its own name; 30 in 2024/2025 — Singida Black Stars, n = 2).

Sign check (sealed leg iii, on dev): SHRINK dev 1X2 LL ≤ Gate Zero
in **3 of 3** dev seasons (2022/2023 equal at 0.928407; 2023/2024
0.944276 vs 1.022600; 2024/2025 0.903820 vs 0.917829) — PASS
(≥ 2 of 3 required).

Dev-pass token for candidate `G-TZ-L1` recorded in
`engine/goals/dev_pass_registry_l1.json` before the sealed load.

## Sealed read (virgin 2025/2026, n = 239, one read)

Fit on all 959 eligible matches dated before the first 2025/2026
match. Calibration is predicted − actual (gate_lib convention).

| Quantity | SHRINK | Climatology |
|---|---:|---:|
| 1X2 LL | **0.882665** | 1.068084 |
| RPS | 0.164708 | 0.220913 |
| OU2.5 LL | 0.675088 | 0.670265 |

Sealed legs:

- **(i) LL leg — PASS.** SHRINK 1X2 LL 0.882665 ≤ climatology
  1.068084 (margin −0.185419). (Reference substitution per the
  fresh prereg §1: no Gate Zero sealed LL is produced as a gate
  reference.)
- **(ii) Calibration leg — PROVISIONAL PASS.**
  - Home-win: predicted − actual = **−0.509 pp**, SE 2.696 pp —
    |diff| ≤ 1.0 pp → clean PASS.
  - OU2.5 over-rate: predicted − actual = **+2.669 pp**,
    SE 3.162 pp — breach of 1.0 pp, within 1 SE of the boundary
    (2.669 ≤ 1.0 + 3.162 = 4.162) → PROVISIONAL.
  - The model over-predicts the over-2.5 rate on the sealed season;
    its sealed OU2.5 LL (0.675088) is likewise slightly worse than
    the base rate's (0.670265). That weakness is confined to the
    totals level — the 1X2/RPS legs beat climatology by wide
    margins — and it is exactly what the provisional label and
    live grading exist to watch.
- **(iii) Sign check — PASS** (3 of 3 dev seasons, above).

Both-pass semantics: Gate Zero is a baseline only and cannot ship
under this entry; the arm of record passes every leg, with one
calibration part provisional, so the verdict is **PROVISIONAL PASS**
and SHRINK ships provisionally.

Independent verification: every sealed number above was recomputed
from the shipped virgin predictions CSV alone (second code path,
gate_lib `calibration`) and matches the stored
`results_virgin_l1.json` exactly (1X2 LL 0.882665, RPS 0.164708,
OU LL 0.675088, home −0.509 pp / SE 2.696 pp, over +2.669 pp /
SE 3.162 pp; 239 rows, arm `shrink`).

## P6 worst-fold block (information only, no gate change)

### P6 worst-fold block — TZ-PremierLeague goals (primary metric: ll_1x2)

Source: `league/TZ-PremierLeague/engine/goals/results_dev.json` (persisted dev artefacts; information only — no gate change).
Worst dev season (highest ll_1x2 for the reference arm): **2023/2024**.

| Entity | Pooled ll_1x2 | Pooled source | Worst-season (2023/2024) ll_1x2 | n (worst) | Δ vs pooled |
|---|---|---|---|---|---|
| climatology | 1.0691 | n-weighted, computed | 1.0760 | 240 | +0.0069 |
| gate_zero | 0.9563 | n-weighted, computed | 1.0226 | 240 | +0.0663 |
| naive_trailing10 | 0.9771 | n-weighted, computed | 1.0010 | 240 | +0.0238 |
| shrink | 0.9255 | n-weighted, computed | 0.9443 | 240 | +0.0188 |

Worst-fold legs in full (2023/2024): SHRINK 1X2 LL 0.944276 vs
climatology 1.076021, RPS 0.175377 vs 0.216873, OU2.5 LL 0.652661
vs base rate 0.669352 — the arm of record passes all three legs
even in its worst dev fold; the pooled OU margin does not rest on
one easy season.

## What ships

SHRINK, provisionally: virgin predictions
`league/TZ-PremierLeague/predictions/g_tz_virgin_predictions.csv`
(239 rows; 1H/2H presentation via the frozen goals constant
0.4867818118), fitted params `engine/goals/fitted_params_virgin_l1.json`,
sealed results `engine/goals/results_virgin_l1.json`, dev
recomputation `engine/goals/results_dev_l1.json` +
`dev_check_l1.json`. A runner-join change for the goals market
(arm `shrink`) is prepared on this branch, following the existing
goals wiring in `league/runner/`; it is NOT merged by this verdict.
Live grading under the program's provisional semantics decides the
market's future; promotion to a clean PASS requires the user's
word. The confirmatory window 2026/2027 was not read.
