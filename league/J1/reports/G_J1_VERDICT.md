# G-J1 Verdict — J1 goals model

Date: 2026-11-09. Branch `build/g-j1`. Prereg:
`league/J1/prereg/PREREG_G_J1.md` (commit b6d3fd4, frozen before any
fitting). Engine: `league/J1/engine/goals/`. Implementation by Codex
(gpt-5.6-luna) under the two-agent flow; all numbers below were
reproduced end-to-end by the coordinator's own rerun, and 5 virgin
predictions were recomputed by hand from the fitted parameters with
independent code (exact match, max diff 0.0).

## Verdict: FAIL — no arm passes all gate legs, nothing ships

Gate Zero passes the dev gate and the virgin LL leg, and its
home-win calibration breach is a provisional pass, but its OU2.5
calibration breach on the virgin window exceeds the boundary by more
than 1 SE, so the calibration leg fails. X2 and X3 are dead at the
dev gate already. Per the frozen both-pass rule, G-J1 does not ship.
The virgin predictions CSV on file is the Gate Zero fallback,
labelled `arm = gate_zero`, for the record only.

## Dev results (walk-forward expanding, season-blocked; n = 1,372)

Climatology per season uses pooled prior seasons only; the pooled
climatology row is the pooled score of those per-season predictions.

| Season | n | Arm | 1X2 LL | RPS | OU2.5 LL |
|---|---|---|---|---|---|
| 2022 | 306 | Gate Zero | 1.0810 | 0.2194 | 0.6681 |
| 2022 | 306 | X2 | 1.0894 | 0.2201 | 0.6737 |
| 2022 | 306 | X3 | 1.0894 | 0.2201 | 0.6737 |
| 2022 | 306 | Climatology | 1.1015 | 0.2230 | 0.6889 |
| 2023 | 306 | Gate Zero | 1.0517 | 0.2201 | 0.7033 |
| 2023 | 306 | X2 | 1.1025 | 0.2301 | 0.7062 |
| 2023 | 306 | X3 | 1.1108 | 0.2298 | 0.7180 |
| 2023 | 306 | Climatology | 1.0791 | 0.2315 | 0.6954 |
| 2024 | 380 | Gate Zero | 1.0817 | 0.2287 | 0.6976 |
| 2024 | 380 | X2 | 1.1564 | 0.2501 | 0.7011 |
| 2024 | 380 | X3 | 1.1741 | 0.2546 | 0.7096 |
| 2024 | 380 | Climatology | 1.0914 | 0.2317 | 0.6970 |
| 2025 | 380 | Gate Zero | 1.0554 | 0.2228 | 0.6873 |
| 2025 | 380 | X2 | 1.0930 | 0.2329 | 0.6890 |
| 2025 | 380 | X3 | 1.1141 | 0.2376 | 0.7018 |
| 2025 | 380 | Climatology | 1.0738 | 0.2297 | 0.6883 |
| Pooled | 1372 | Gate Zero | 1.0675 | 0.2231 | 0.6894 |
| Pooled | 1372 | X2 | 1.1119 | 0.2342 | 0.6928 |
| Pooled | 1372 | X3 | 1.1245 | 0.2367 | 0.7013 |
| Pooled | 1372 | Climatology | 1.0860 | 0.2291 | 0.6924 |

Dev gate (pooled LL and RPS must beat climatology, OU LL must beat
the base-rate baseline): Gate Zero **PASS** (1.0675 < 1.0860,
0.2231 < 0.2291, 0.6894 < 0.6924). X2 **FAIL** on all three. X3
**FAIL** on all three. X3 ≡ X2 in 2022 by construction (2021-only
training window has no xG).

Why X2 fails: the frozen F4 offset (−0.56 GF / +0.51 GA against the
league mean mu) is too strong as a constant. It is worst in 2024
(LL 1.1564 vs Gate Zero 1.0817), the season Machida Zelvia — a
promoted club the offset penalises — finished near the top of J1.
The offset as frozen does not survive contact with the dev window;
re-estimating it would be a new prereg, not a fix to this one.

## Virgin results (season "2026", n = 200, read once after dev froze)

| Arm | 1X2 LL | RPS | OU2.5 LL | HW calib diff | HW SE | OU calib diff | OU SE |
|---|---|---|---|---|---|---|---|
| Gate Zero | 1.0748 | 0.2232 | 0.7023 | +1.66pp | 3.42pp | −4.56pp | 3.56pp |
| X2 | 1.0552 | 0.2166 | 0.6996 | +1.92pp | 3.35pp | −4.89pp | 3.55pp |
| X3 | 1.0630 | 0.2186 | 0.7073 | +1.96pp | 3.36pp | −4.87pp | 3.57pp |
| Climatology | 1.0915 | 0.2289 | 0.6915 | — | — | — | — |

Actual virgin rates: home-win 39.0%, over-2.5 47.0%. All three arms
under-predict the over rate by ~4.6–4.9pp (mean predicted ~42.1–42.4%
against 47.0% actual): the 2026 transitional season ran hotter
(2.66 goals/match) than the decay-weighted training level
(mu = 1.247 goals per team per match, fitted h = 0.156, rho = 0.0).

## Per-leg verdicts

| Leg | Gate Zero | X2 | X3 |
|---|---|---|---|
| Dev gate | PASS | FAIL | FAIL |
| Virgin LL (≤ Gate Zero and ≤ climatology 1.0915) | PASS (1.0748) | PASS (1.0552) | PASS (1.0630) |
| Calibration — home-win (≤1.0pp, or breach ≤1 SE = provisional) | PROVISIONAL PASS (breach 0.66pp ≤ SE 3.42pp) | PROVISIONAL PASS (0.92 ≤ 3.35) | PROVISIONAL PASS (0.96 ≤ 3.36) |
| Calibration — OU2.5 | FAIL (breach 3.56pp > SE 3.56pp, by 0.005pp) | FAIL (3.89 > 3.55) | FAIL (3.87 > 3.57) |
| Per-season sign check (dev LL ≤ Gate Zero in ≥2 of 4 seasons) | n/a (comparator) | FAIL (0/4) | FAIL (0/4) |
| **Overall** | **FAIL** | **FAIL** | **FAIL** |

The Gate Zero OU2.5 failure is as narrow as a gate can be: breach
3.5636pp against 1 SE = 3.5589pp. The prereg's rule is mechanical —
beyond 1 SE is FAIL — and it is applied as written. No arm passes
all legs, so under the both-pass rule the verdict is FAIL and
nothing ships.

## Verification notes (coordinator, independent of Codex)

- Full harness rerun by the coordinator reproduces every model
  number above exactly.
- Dev isolation confirmed in code: the dev path loads only seasons
  2021–2025; season "2026" is touched only by the virgin step.
- Spot check: 5 virgin matches recomputed by hand from
  `fitted_params_virgin.json` (own score-matrix code) match the CSV
  exactly on lambdas, 1X2, OU and BTTS; 1H/2H lambdas equal the
  0.412/0.588 constant split of the same FT lambdas and the 1H OU
  lines equal the split-lambda matrix values.
- Effective movers per season, recomputed independently, are exactly
  the promoted clubs (2022: Jubilo Iwata, Kyoto Sanga; 2023: Albirex
  Niigata, Yokohama FC; 2024: Tokyo Verdy, Jubilo Iwata, Machida
  Zelvia; 2025: Shimizu S-Pulse, Yokohama FC, Fagiano Okayama;
  2026: JEF United Chiba, Mito Hollyhock, V-Varen Nagasaki).
- Two coordinator corrections during verification, neither touching
  a model or a gate: (1) the pooled dev climatology row in Codex's
  first run used full-period rates (including later seasons); fixed
  to pool the per-season expanding climatology predictions as the
  prereg specifies — Gate Zero passes the dev gate under either
  version, X2/X3 fail under either; (2) Codex's draft verdict read
  every calibration breach as a plain FAIL; the prereg's
  provisional-pass rule is applied in the table above.
