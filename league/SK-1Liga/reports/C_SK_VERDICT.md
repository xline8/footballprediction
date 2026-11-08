# Verdict — C-SK (SK-1Liga corners, corners_v3 pattern, Gate Zero only)

**FAIL — virgin calibration leg (ii). Nothing ships.**

Dev (pooled, stats-target n = 568, LL@9.5):

| | LL@9.5 | Dev gate |
|---|---|---|
| Gate Zero | **0.688612** | PASS |
| League base rate | 0.747412 | |
| Naive trailing-10 | 0.747103 | |

Per-season Gate Zero LL@9.5: 0.676435 / 0.685553 / 0.704008 —
better than both baselines pooled and in every season.

Virgin (2025/2026, n = 192), Gate Zero:

| | LL@9.5 | Mean P(over 9.5) | Actual |
|---|---|---|---|
| Gate Zero | **0.700074** | 0.590250 | 0.541667 |
| League base rate | 0.745171 | 0.377168 | 0.541667 |
| Naive trailing-10 | 0.738842 | 0.379127 | 0.541667 |

Gate arithmetic (PREREG_C_SK): leg (i) LL@9.5 ≤ best baseline's
(0.738842) → PASS, by a wide margin. Leg (ii) calibration:
diff = +4.86pp (SE 3.63pp). The clean boundary is 1.0pp; a
provisional pass requires the breach to lie within 1 SE of the
boundary, i.e. |diff| ≤ 1.0pp + 3.63pp = 4.63pp. The observed
4.86pp exceeds that by 0.23pp → **FAIL**, stated plainly: the
model ranks virgin matches well (LL) but systematically
over-predicts the over-9.5 rate by nearly 5 points — the
possession multiplier fitted on dev-era levels overshoots in
the virgin season, whose actual corner level (9.89/match) sat
below the dev seasons the parameters came from.

Ships: nothing. No predictions file was written.
(`engine/corners/fitted_params_virgin.json` is the run artefact
recording the virgin fit — gamma 0.15, r 1.158, beta [0.0] — not
a shipment.)
