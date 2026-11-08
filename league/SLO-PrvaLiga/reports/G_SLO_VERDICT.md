# Verdict — G-SLO (Slovenia Prva Liga goals): **FAIL (dev gate)**

Frozen decision: `prereg/PREREG_G_SLO.md` (prereg commit `d973cfe6`,
before any fitting). Engine: `league/SLO-PrvaLiga/engine/goals/`
(dev commit `e8d4bdfa`). Implementation by Codex (gpt-5.6-luna) under the
two-agent flow; all numbers below were reproduced by the coordinator
independently — pooled and per-season metrics recomputed from the
per-match `results_dev.csv`, predictions replayed from
`fitted_params_dev.json` (max probability error 2e-16), and all three
target seasons re-fitted with independently written code (different
parameterisation and optimiser). Every headline number matches; the
independent re-fit also FAILS the same gate (see below).

## Verdict: FAIL — no arm passes the dev gate, nothing ships

Gate Zero beats both baselines on pooled 1X2 log-loss and RPS, and beats
naive trailing-10 on OU2.5 log-loss — but it **loses the OU2.5 log-loss
leg against climatology** (0.6971 vs 0.6957), so the dev gate fails.
SHRINK is numerically identical to Gate Zero (see below), so it fails on
the same leg. Per the frozen rule — Gate Zero fails dev ⇒ variants moot
— **the virgin window (2025/2026) was NOT read**, and the confirmatory
reserve (2026/2027 partial) was not touched.
`engine/goals/results_virgin.json` records the not-read state.
No virgin predictions file exists. Nothing ships.

## Dev results (walk-forward expanding, season-blocked; n = 538)

Warm-up 2021/2022 (n = 180 model matches); evaluation seasons 2022/2023,
2023/2024, 2024/2025. Climatology per season uses pooled prior seasons
only; the pooled climatology row is the pooled score of those per-season
predictions.

| Season | n | Arm | 1X2 LL | RPS | OU2.5 LL |
|---|---|---|---|---|---|
| 2022/2023 | 180 | Gate Zero | 1.0586 | 0.2156 | 0.6931 |
| 2022/2023 | 180 | SHRINK | 1.0586 | 0.2156 | 0.6931 |
| 2022/2023 | 180 | Climatology | 1.0933 | 0.2272 | 0.6857 |
| 2022/2023 | 180 | Naive trailing-10 | 1.0572 | 0.2149 | 0.7653 |
| 2023/2024 | 178 | Gate Zero | 1.0300 | 0.2129 | 0.6972 |
| 2023/2024 | 178 | SHRINK | 1.0300 | 0.2129 | 0.6972 |
| 2023/2024 | 178 | Climatology | 1.0876 | 0.2337 | 0.7062 |
| 2023/2024 | 178 | Naive trailing-10 | 1.0242 | 0.2115 | 0.7521 |
| 2024/2025 | 180 | Gate Zero | 1.0045 | 0.2042 | 0.7011 |
| 2024/2025 | 180 | SHRINK | 1.0045 | 0.2042 | 0.7011 |
| 2024/2025 | 180 | Climatology | 1.0797 | 0.2304 | 0.6954 |
| 2024/2025 | 180 | Naive trailing-10 | 1.3859 | 0.2327 | 0.7935 |
| Pooled | 538 | Gate Zero | 1.0310 | 0.2109 | 0.6971 |
| Pooled | 538 | SHRINK | 1.0310 | 0.2109 | 0.6971 |
| Pooled | 538 | Climatology | 1.0869 | 0.2304 | 0.6957 |
| Pooled | 538 | Naive trailing-10 | 1.1562 | 0.2197 | 0.7704 |

Dev gate (pooled 1X2 LL and RPS must beat climatology AND naive
trailing-10, and OU2.5 LL must beat both baselines):

| Leg (pooled) | Gate Zero | SHRINK |
|---|---|---|
| 1X2 LL vs climatology (1.0310 < 1.0869) | WIN | WIN |
| 1X2 LL vs naive (1.0310 < 1.1562) | WIN | WIN |
| RPS vs climatology (0.2109 < 0.2304) | WIN | WIN |
| RPS vs naive (0.2109 < 0.2197) | WIN | WIN |
| OU2.5 LL vs climatology (0.6971 < 0.6957) | **LOSE** | **LOSE** |
| OU2.5 LL vs naive (0.6971 < 0.7704) | WIN | WIN |
| **Dev gate** | **FAIL (5/6)** | **FAIL (5/6)** |

Fitted home intercept / rho per target season (both arms, identical):
2022/2023: 0.2152 / −0.05; 2023/2024: 0.2000 / −0.05;
2024/2025: 0.2044 / −0.10.

## Why the OU leg fails (measured facts, recorded not acted on)

Gate Zero loses the OU2.5 log-loss leg to climatology in two of the three
dev seasons individually (0.6931 vs 0.6857 in 2022/2023; 0.7011 vs 0.6954
in 2024/2025) and wins it only in 2023/2024 (0.6972 vs 0.7062). The
pooled loss is narrow (0.0014) but it is not a level miss in the
climatology direction: pooled, Gate Zero's mean P(over 2.5) is 0.4235
against an actual over-rate of 0.4870 (−6.34pp) — the model
systematically under-predicts overs on the dev window — while
climatology's mean P(over) is 0.4481 (−3.88pp). The model's per-match
OU spread does not pay on this window: its match-level over
probabilities are worse than a constant. No gate is moved: the verdict
is FAIL and nothing ships. A future revisit would need a pre-registered
OU treatment tested on a fresh virgin window — not a post-hoc rescue of
this one.

## SHRINK identity (expected, confirmed mechanically)

SHRINK is numerically identical to Gate Zero pooled and per season.
Verified cause: no team had 1–5 prior in-league matches in any scored
season's training data — every team entering a scored season either had
n = 0 prior matches (pure entrant, already at the league-mean fallback
in both arms: 1, 1, 2 entrants) or n ≥ 30, so the n/6 scaling never bit
on a fitted rating. A synthetic test proved the SHRINK scaling itself
is active (n = 3 gives factor 0.5).

## Independent re-fit (coordinator, own code)

All three target seasons were re-fitted with independently written code
(free attack/defence with a centering penalty, BFGS optimiser, different
starting values). It finds slightly higher training log-likelihoods
(−195.33 vs −195.69; −272.58 vs −273.13; −293.07 vs −293.71) with the
same rho choices (−0.05, −0.05, −0.10) and home intercepts within 0.02
of the engine's — the engine's L-BFGS-B fit stops marginally short of
the optimum, which is optimiser tolerance, not a bug. Scored with the
independent params, pooled dev is 1X2 LL 1.0306, RPS 0.2108, OU2.5 LL
0.6999 — the OU leg loses to climatology (0.6957) by MORE (0.0042).
The FAIL verdict is therefore robust to optimiser variation.

## Naive baseline diagnostic (recorded, not acted on)

Naive trailing-10's 2024/2025 1X2 LL of 1.3859 is driven by two matches
worth 27.63 each (the epsilon floor): Nafta 2–1 Radomlje (2024-07-26)
and Nafta 0–3 Primorje (2024-08-10). Nafta is a 2024/2025 entrant; after
a scoreless debut its trailing-10 mean is exactly 0.0 (one prior match,
zero goals), so the baseline assigns probability 0.0 to Nafta scoring
and is maximally wrong when Nafta scores. This is the preregistered
spec ("fewer when necessary, training league mean if none exist" —
one prior match exists, so the mean is 0), not an engine bug, and it
does not touch the failing leg: removing both matches, naive pooled
1X2 LL would still be ≈1.0534, above Gate Zero's 1.0310.

## Virgin: NOT read

No arm passed the dev gate, so under the frozen rule the virgin window
(2025/2026, n = 161 model rows) was not read, no virgin fit was made,
and no virgin leg was scored. The 2025/2026 goals-level jump (3.0870
goals/match, OU2.5 rate 0.6522, HW rate 0.4969, versus dev pooled
2.7026 / 0.4870 / 0.4033) therefore plays no part in this verdict — it
remains an untested virgin fact. The 2026/2027 partial reserve (n = 74)
is untouched.
