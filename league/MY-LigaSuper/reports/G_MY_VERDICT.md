# Verdict — G-MY (Malaysia Liga Super goals): **FAIL (dev gate)**

Frozen decision: `prereg/PREREG_G_MY.md` (prereg commit `c3d1a0cf`,
before any fitting). Engine: `league/MY-LigaSuper/engine/goals/`
(dev commit `f6924722`). Implementation by Codex (gpt-5.6-luna) under
the two-agent flow; all numbers below were reproduced by the
coordinator independently — pooled and per-season metrics recomputed
from the per-match `results_dev.csv` (max abs difference 2.2e-16),
predictions replayed from `fitted_params_dev.json` (max probability
error 3.3e-16), and all three target seasons re-fitted with
independently written code (different parameterisation and optimiser).
Every headline number matches; the independent re-fit also FAILS the
same gate (see below).

## Verdict: FAIL — no arm passes the dev gate, nothing ships

Gate Zero beats both baselines on pooled 1X2 log-loss, beats
climatology on RPS, and beats naive trailing-10 on OU2.5 log-loss —
but it **loses the OU2.5 log-loss leg against climatology** (0.7093 vs
0.6811, margin +0.0282) **and loses the RPS leg against naive
trailing-10** (0.2032 vs 0.1985, margin +0.0047), so the dev gate fails
on two of six legs. SHRINK is numerically identical to Gate Zero (see
below), so it fails on the same legs. Per the frozen rule — Gate Zero
fails dev ⇒ variants moot — **the virgin window (2025/2026) was NOT
read**, and the confirmatory reserve (2026/2027 partial) was not
touched. `engine/goals/results_virgin.json` records the not-read
state. No virgin predictions file exists. Nothing ships.

## Dev results (walk-forward expanding, season-blocked; n = 469)

Warm-up 2021 (n = 132 model matches); evaluation seasons 2022,
2023, 2024/2025. Climatology per season uses pooled prior seasons
only; the pooled climatology row is the pooled score of those
per-season predictions.

| Season | n | Arm | 1X2 LL | RPS | OU2.5 LL |
|---|---|---|---|---|---|
| 2022 | 132 | Gate Zero | 1.0740 | 0.2365 | 0.7642 |
| 2022 | 132 | SHRINK | 1.0740 | 0.2365 | 0.7642 |
| 2022 | 132 | Climatology | 1.0552 | 0.2362 | 0.6858 |
| 2022 | 132 | Naive trailing-10 | 1.0941 | 0.2402 | 0.7263 |
| 2023 | 182 | Gate Zero | 0.8954 | 0.1923 | 0.7034 |
| 2023 | 182 | SHRINK | 0.8954 | 0.1923 | 0.7034 |
| 2023 | 182 | Climatology | 1.0349 | 0.2388 | 0.6731 |
| 2023 | 182 | Naive trailing-10 | 0.9933 | 0.1774 | 0.8048 |
| 2024/2025 | 155 | Gate Zero | 0.9166 | 0.1877 | 0.6693 |
| 2024/2025 | 155 | SHRINK | 0.9166 | 0.1877 | 0.6693 |
| 2024/2025 | 155 | Climatology | 1.0777 | 0.2375 | 0.6864 |
| 2024/2025 | 155 | Naive trailing-10 | 0.9373 | 0.1878 | 0.7628 |
| Pooled | 469 | Gate Zero | 0.9527 | 0.2032 | 0.7093 |
| Pooled | 469 | SHRINK | 0.9527 | 0.2032 | 0.7093 |
| Pooled | 469 | Climatology | 1.0548 | 0.2376 | 0.6811 |
| Pooled | 469 | Naive trailing-10 | 1.0031 | 0.1985 | 0.7688 |

Dev gate (pooled 1X2 LL and RPS must beat climatology AND naive
trailing-10, and OU2.5 LL must beat both baselines):

| Leg (pooled) | Gate Zero | SHRINK |
|---|---|---|
| 1X2 LL vs climatology (0.9527 < 1.0548) | WIN | WIN |
| 1X2 LL vs naive (0.9527 < 1.0031) | WIN | WIN |
| RPS vs climatology (0.2032 < 0.2376) | WIN | WIN |
| RPS vs naive (0.2032 < 0.1985) | **LOSE** | **LOSE** |
| OU2.5 LL vs climatology (0.7093 < 0.6811) | **LOSE** | **LOSE** |
| OU2.5 LL vs naive (0.7093 < 0.7688) | WIN | WIN |
| **Dev gate** | **FAIL (4/6)** | **FAIL (4/6)** |

Fitted home intercept / rho per target season (both arms, identical):
2022: 0.2139 / −0.15; 2023: 0.3851 / 0.00; 2024/2025: 0.2630 / 0.00.

## Why the OU leg fails (measured facts, recorded not acted on)

Gate Zero loses the OU2.5 log-loss leg to climatology in two of the
three dev seasons individually (0.7642 vs 0.6858 in 2022; 0.7034 vs
0.6731 in 2023) and wins it narrowly in 2024/2025 (0.6693 vs 0.6864),
so the pooled loss is driven by the first two seasons.
Pooled, Gate Zero's mean P(over 2.5) is 0.5176 against an actual
over-rate of 0.5885 (−7.08pp) — the model systematically
under-predicts overs on the dev window — while climatology's mean
P(over) is 0.5558 (−3.27pp) and naive trailing-10's is 0.5665
(−2.20pp). The under-prediction is worst in 2022 (−12.22pp: 0.4536
vs 0.5758 actual) and 2023 (−9.30pp: 0.5279 vs 0.6209), and
essentially absent in 2024/2025 (−0.11pp: 0.5602 vs 0.5613). The
dev window is a high-scoring, rising-goals era (goals/match 2.94 in
2022, 3.43 in 2023, 3.05 in 2024/2025, dev pooled 3.17) and the
season-blocked expanding fit, trained mostly on the lower-scoring
2021 warm-up (2.70 goals/match) for its first scored season, lags
the level shift. No gate is moved: the verdict is FAIL and nothing
ships. A future revisit would need a pre-registered OU treatment
tested on a fresh virgin window — not a post-hoc rescue of this one.

The RPS loss to naive is driven by a single season: 2023
(0.1923 vs 0.1774); Gate Zero wins RPS against naive in 2022
(0.2365 vs 0.2402) and ties it in 2024/2025 (0.1877 vs 0.1878).
Pooled, the margin is +0.0047.

## SHRINK identity (expected, confirmed mechanically)

SHRINK is numerically identical to Gate Zero pooled and per season,
on all 469 rows. Verified cause: no team had 1–5 prior in-league
matches in any scored season's training data — every team entering a
scored season either had n = 0 prior matches (pure entrant, already
at the league-mean fallback in both arms: 2, 4, 0 entrants) or
n ≥ 6, so the n/6 scaling never bit on a fitted rating. The
bucket-count diagnostic initially counted training-window teams that
never play the target season (Perak, UiTM, etc.); it was fixed to
count target-season teams only, after which the actual counts match
the frozen prereg expectations exactly — 2022 (2, 0, 10, 0), 2023
(4, 0, 2, 8), 2024/2025 (0, 0, 3, 10) — with `results_dev.csv`
byte-identical before and after the fix. A synthetic test proved the
SHRINK scaling itself is active (n = 3 gives factor 0.5).

## Independent re-fit (coordinator, own code)

All three target seasons were re-fitted with independently written
code (free attack/defence with a centering penalty, BFGS optimiser,
different starting values). It finds the same rho choices (−0.15,
0.00, 0.00) with home intercepts 0.1336 / 0.3403 / 0.1885 (engine:
0.2139 / 0.3851 / 0.2630 — the 2022 gap reflects optimiser/
parameterisation differences, not a bug: the scored metrics are
close). Scored with the independent params, pooled dev is 1X2 LL
0.9503, RPS 0.2021, OU2.5 LL 0.7211 — the OU leg loses to
climatology (0.6811) by MORE (0.0400) and the RPS leg still loses
to naive (0.1985) by 0.0036. The FAIL verdict is therefore robust
to optimiser variation.

## Virgin: NOT read

No arm passed the dev gate, so under the frozen rule the virgin
window (2025/2026, n = 156 model rows) was not read, no virgin fit
was made, and no virgin leg was scored. The 2025/2026 level facts
(3.2949 goals/match, OU2.5 rate 0.6026, HW rate 0.3974, versus dev
pooled 3.1663 / 0.5885 / 0.4520) therefore play no part in this
verdict — they remain untested virgin facts. The 2026/2027 partial
reserve (n = 35) is untouched.
