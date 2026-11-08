# C-MX Verdict — Liga MX corners model

Date: 2026-11-09. Branch `build/mx-ligamx`. Prereg:
`league/MX-LigaMX/prereg/PREREG_C_MX.md` (commit 8512c8d, frozen
before any fitting). Engine: `league/MX-LigaMX/engine/corners/`.
Implementation by Codex (gpt-5.6-luna) under the two-agent flow;
the coordinator fixed the sign-check rule to the MX prereg before
the virgin read and independently re-ran the dev harness (see
Verification notes). Predictions-only product: no Liga MX corner
odds source exists in-system — expected, not a defect.

## Verdict: PROVISIONAL PASS — Gate Zero ships

Both arms pass the dev gate and all three virgin legs. On the
virgin the two arms are **numerically identical** (the fitted
territorial coefficient is 0.0 on the virgin window — see below),
so the both-pass rule's tie clause ships the simpler arm, Gate
Zero. Calibration on the virgin is +4.17pp against a 1.0pp clean
boundary with SE 4.02pp — inside one SE of the boundary — so the
pass is **provisional**, not clean, for both arms.

## Dev results (expanding block-blocked walk-forward, scored blocks = tournaments 2–9, n = 1,224; LL@9.5)

Pooled:

| Arm | LL@9.5 | vs base 0.7367 | vs naive 0.7323 |
|---|---|---|---|
| Gate Zero (GZ pattern + X9 covariates) | **0.6969** | pass | pass |
| X7 (opponent box-touch multiplier) | **0.6988** | pass | pass |
| League base rate | 0.7367 | — | — |
| Naive trailing-10 | 0.7323 | — | — |

Per-block LL@9.5 (model arms; baselines identical across arms):

| Block | GZ | X7 | Base | Naive |
|---|---|---|---|---|
| 2021/2022 - Clausura | 0.7043 | 0.6956 | 0.7311 | 0.7207 |
| 2022/2023 - Apertura | 0.6983 | 0.6983 | 0.7291 | 0.7245 |
| 2022/2023 - Clausura | 0.7059 | 0.7301 | 0.7715 | 0.7560 |
| 2023/2024 - Apertura | 0.6913 | 0.6913 | 0.7528 | 0.7504 |
| 2023/2024 - Clausura | 0.6917 | 0.6917 | 0.7421 | 0.7429 |
| 2024/2025 - Apertura | 0.6975 | 0.6975 | 0.7436 | 0.7457 |
| 2024/2025 - Clausura | 0.6878 | 0.6878 | 0.7360 | 0.7287 |
| 2025/2026 - Apertura | 0.6983 | 0.6983 | 0.6877 | 0.6896 |

Sign check (X7 dev LL ≤ GZ, of 8): 7/8 (one strict win, six exact
ties, one loss) — passes leg (iii). Diagnostic honesty: X7's
multiplier is inactive on most of the dev window (both-teams
active share 0.824 but only 7.6% of matches carry a nonzero
coefficient; six of eight blocks are numerically identical to
GZ). The Gate Zero arm's own territorial coefficient is likewise
zero on most windows (25% nonzero share). The pattern's value in
this league is its calibrated ratings + NB core; the territorial
machinery contributes marginally.

## Virgin results (2025/2026 - Clausura, n = 153, read once)

| Arm | LL@9.5 | Mean P(over) | Actual over | Calibration diff | SE |
|---|---|---|---|---|---|
| Gate Zero | 0.6883 | 0.4992 | 0.4575 | +4.17pp | 4.02pp |
| X7 | 0.6883 | 0.4992 | 0.4575 | +4.17pp | 4.02pp |
| League base rate | 0.7025 | 0.3785 | 0.4575 | — | — |
| Naive trailing-10 | 0.7024 | 0.3525 | 0.4575 | — | — |

## Gate arithmetic

- Dev gate (pooled LL@9.5 strictly beats BOTH baselines): GZ
  **pass** (0.6969 < 0.7367, 0.7323), X7 **pass** (0.6988 < both).
- Virgin leg (i) (LL ≤ GZ's AND ≤ best baseline's): both arms
  0.6883 ≤ 0.6883 and ≤ 0.7024 → **pass**.
- Virgin leg (ii) (calibration): |diff| = 4.17pp > 1.0pp clean
  boundary, but ≤ 1.0pp + 1 SE (5.02pp) → **provisional pass**
  for both arms. The model over-forecast the over-rate on a
  virgin block that ran corner-light (actual total 9.14 vs dev
  9.79).
- Virgin leg (iii): X7 sign check 7/8 ≥ 4 → **pass**.
- Both-pass rule: pooled virgin LL ties exactly (0.6883 =
  0.6883) → tie goes to the simpler arm → **Gate Zero ships**,
  carrying the provisional status.

Why the arms tie: on the virgin fit window the frozen selection
procedure sets the territorial coefficient to exactly 0.0 in both
arms (fitted params: `gate_zero.beta = [0.0, 0.0]`, `x7.beta =
[0.0]`, same r = 1.0803, same fit_n = 1,365). X7 therefore ships
nothing extra — its dev record (pooled LL worse than GZ anyway)
gives no reason to prefer it.

## What ships

Gate Zero, fitted params in
`engine/corners/fitted_params_virgin.json`; virgin predictions in
`predictions/c_mx_virgin_predictions.csv` (153 rows, ladder
8.5/9.5/10.5). Halves presentation at the frozen MX constant
(1H share 0.465 / 2H 0.535) — presentation only.

## Verification notes (coordinator, independent of Codex)

- Coordinator review caught two AR-port leftovers in the virgin
  path before the read: an AR season label ("2026 - Clausura")
  that would have matched nothing, and the AR sign-check rule
  (AR tournament labels, ≥2 of a subset) in place of the MX rule
  (≥4 of the 8 scored blocks). Both fixed to the prereg; the
  runner applies the MX rule (recorded sign count 7/8 agrees with
  the coordinator's own count from the results file).
- Coordinator re-run of the dev harness reproduces the results
  file **exactly** (byte-identical JSON).
- The X7≡GZ identity on the virgin was verified from the fitted
  params (beta 0.0), not assumed: it is the reference procedure's
  fitted outcome on this window, and the verdict's ship decision
  follows the frozen tie clause rather than any preference.
