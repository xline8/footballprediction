# Verdict — C-CA (CA-PremierLeague corners model)

**FAIL — Gate Zero passes dev, then fails BOTH virgin legs.**

Dev (pooled, stats-target n = 336, LL@9.5):

| | LL@9.5 |
|---|---|
| Gate Zero | **0.701972** |
| League base rate | 0.723780 |
| Naive trailing-10 | 0.723742 |

Dev gate: Gate Zero beats both baselines → virgin read.

Virgin (2025, n = 112):

| | LL@9.5 | Calibration (pp) |
|---|---|---|
| Gate Zero | 0.670307 | +6.99 (SE 4.59) |
| League base rate | 0.661984 | −1.40 |
| Naive trailing-10 | **0.656414** | −2.88 |

Gate arithmetic (PREREG_C_CA): leg (i) LL@9.5 ≤ best baseline's
— 0.670307 > 0.656414 ✗ FAIL. Leg (ii) calibration |breach| ≤
1.0pp — breach is +6.99pp; the excess over the boundary (5.99pp)
exceeds 1 SE (4.59pp), so this is an outright FAIL, not a
provisional pass. Both legs fail → verdict FAIL, nothing ships.

What happened: the league's corner level fell in 2025 (mean 8.77
per match, over-9.5 rate 0.375, vs 9.58 and a much higher rate in
2024). The season-blocked fit (gamma 0.0, betas −0.0025/0.0,
r = 1.021 at its clamp floor) carried the higher dev-era level
into 2025 and over-predicted all season (mean predicted 0.4449
vs actual 0.375); the trailing-10 naive adapted in-season and
won. The dev win was real but regime-dependent.

Verification: LL@9.5, calibration and SE recomputed independently
by the coordinator from the per-match virgin CSV — exact match.

Ships: nothing. Virgin read: YES (Gate Zero, once).
