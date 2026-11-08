# C-DE2 verdict — FAIL

Prereg: `prereg/PREREG_C_DE2.md` (frozen 4261ad8, before fitting).
Primary line **10.5** (dev over-rate 0.444). Dev pooled n = 918;
virgin 2025/2026 n = 306, read once, for both dev-passing arms.

## Dev results — pooled LL@10.5

| Arm / baseline | LL@10.5 |
|---|---|
| Gate Zero (X9) | 0.6969 |
| X7 (box touches) | 0.6888 |
| League base rate | 0.7130 |
| Naive trailing-10 | 0.7051 |

Both arms beat both baselines by a wide margin → both pass the
dev gate. X7's dev advantage is real (better in all three dev
seasons; sign check 3/3).

## Virgin results (2025/2026, n = 306)

| Arm / baseline | LL@10.5 | Calibration (mean P − actual) |
|---|---|---|
| Gate Zero | 0.6764 | +4.56pp (SE 2.80pp) |
| X7 | 0.6764 | +4.56pp (SE 2.80pp) |
| League base rate | 0.6769 | — |
| Naive trailing-10 | 0.6873 | — |

## Gate arithmetic

- Leg (i): both arms pass (0.6764 ≤ best baseline 0.6769 — by
  0.0005 over the league base rate).
- Leg (ii): **both arms FAIL.** |+4.56pp| breaches the 1.0pp
  boundary by 3.56pp, beyond 1 SE (2.80pp). The virgin season's
  corner volume at the 10.5 line ran far below prediction (actual
  over-rate 39.9% vs mean predicted 44.4%) while the season's
  corner *mean* (10.04) sat close to the dev level — the
  over-rate at this line, not the level, is what moved (the
  mirror image of C-BE's failure at 9.5).
- Leg (iii): X7's sign check is 3/3 — moot under leg (ii).

The two arms' virgin predictions are **identical** — on the
virgin fit both territorial betas fitted to exactly 0.0 (γ = 0.0,
r = 1.1121 for both), the same result C-J1, C-DK, C-CH and C-BE
recorded: the box-touch trait is real in DE-2 too (split-half
r = 0.842/0.619) but earns exactly zero inside this multiplier
structure. X7's genuine dev gain (0.6888 vs 0.6969) came from
seasons where the betas were non-zero; on the virgin fit the
structure switched itself off.

**Verdict: FAIL. Nothing ships.** (The harness's per-arm
`fitted_params_virgin.json` was removed on FAIL; the fitted
values remain recorded in `results_virgin.json`.)
