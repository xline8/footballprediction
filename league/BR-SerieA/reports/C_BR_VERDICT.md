# C-BR verdict — FAIL (virgin leg (i)); nothing ships

Prereg: `prereg/PREREG_C_BR.md` (frozen 7056902, before fitting).
Primary line 10.5. Dev pooled n = 1,140; virgin 2025 n = 380, read
once for both dev-passing arms.

## Dev results — pooled LL@10.5

| Arm / baseline | LL@10.5 |
|---|---|
| Gate Zero (X9) | 0.688535 |
| X7 (box touches) | 0.688535 |
| League base rate | 0.720910 |
| Naive trailing-10 | 0.717438 |

Both arms beat both baselines → both pass the dev gate. The two
arms are **numerically identical**: β_bt fitted to 0 in every
season — the third straight league (J1, DK, BR) where the F9 box
-touch trait is real (BR r = 0.803) but worth zero inside this
multiplier structure.

## Virgin results (2025, n = 380)

| Arm / baseline | LL@10.5 | Calibration (pp) |
|---|---|---|
| Gate Zero = X7 | 0.674000 | +3.38 (SE 2.58) |
| League base rate | **0.672548** | — |
| Naive trailing-10 | 0.677117 | — |

## Gate arithmetic

- Leg (i): arm LL 0.674000 must be ≤ Gate Zero's (trivially,
  identical) **and ≤ the best baseline's** 0.672548. It is not —
  **leg (i) FAILS** for both arms: on the virgin, a decay-weighted
  league base rate out-predicts the full corners model. 2025 ran
  cold on corners (9.93/match vs dev-era 10.2–11.0) and the base
  rate's faster level adaptation won, the K-J2 lesson in reverse.
- Leg (ii): calibration breach +3.38pp exceeds 1.0pp but lies
  within 1 SE (2.58pp) of the boundary → would be PROVISIONAL;
  moot under the leg (i) failure.
- Leg (iii): arms identical, sign check trivially satisfied; moot.

**Ships: nothing.** C-BR is FAIL. (The `fitted_params_virgin.json`
in the engine dir is the virgin-run artefact of the harness, as in
the DK engine; on a FAIL verdict it ships nothing and authorises
nothing.)
