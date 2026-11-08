# Verdict — G-MK (North Macedonia Prva Liga goals): **FAIL (dev gate)**

Frozen decision: `prereg/PREREG_G_MK.md` (prereg commit `ecfd67f7`,
before any fitting). Engine: `league/MK-PrvaLiga/engine/goals/`.
Implementation by Codex (gpt-5.6-luna) under the two-agent flow; all
numbers below were reproduced end-to-end by the coordinator's own
independent DC fit (own code, same math spec) and by recomputing the
metrics from `results_dev.csv` — every headline number matches to 4
decimal places.

## Verdict: FAIL — no arm passes the dev gate, nothing ships

Gate Zero beats both baselines on pooled 1X2 log-loss and RPS, and
beats naive trailing-10 on OU2.5 log-loss — but it **loses the OU2.5
log-loss leg against climatology** (0.6899 vs 0.6804), so the dev gate
fails. SHRINK is numerically identical to Gate Zero (see below), so
it fails on the same leg. Per the frozen rule — Gate Zero fails dev
⇒ variants moot — **the virgin window (2025/2026) was NOT read**,
and the confirmatory reserve (2026/2027 partial) was not touched.
`engine/goals/results_virgin.json` records the not-read state.
No virgin predictions file exists. Nothing ships.

## Dev results (walk-forward expanding, season-blocked; n = 549)

Warm-up 2021/2022 (n = 198 model matches); evaluation seasons
2022/2023, 2023/2024, 2024/2025. Climatology per season uses pooled
prior seasons only; the pooled climatology row is the pooled score
of those per-season predictions.

| Season | n | Arm | 1X2 LL | RPS | OU2.5 LL |
|---|---|---|---|---|---|
| 2022/2023 | 165 | Gate Zero | 1.0627 | 0.2208 | 0.6973 |
| 2022/2023 | 165 | SHRINK | 1.0627 | 0.2208 | 0.6973 |
| 2022/2023 | 165 | Climatology | 1.0861 | 0.2313 | 0.6920 |
| 2022/2023 | 165 | Naive trailing-10 | 1.0632 | 0.2200 | 0.7650 |
| 2023/2024 | 198 | Gate Zero | 0.9929 | 0.1976 | 0.6890 |
| 2023/2024 | 198 | SHRINK | 0.9929 | 0.1976 | 0.6890 |
| 2023/2024 | 198 | Climatology | 1.0318 | 0.2089 | 0.6767 |
| 2023/2024 | 198 | Naive trailing-10 | 1.2027 | 0.2210 | 0.8620 |
| 2024/2025 | 186 | Gate Zero | 1.0996 | 0.2250 | 0.6844 |
| 2024/2025 | 186 | SHRINK | 1.0996 | 0.2250 | 0.6844 |
| 2024/2025 | 186 | Climatology | 1.0802 | 0.2200 | 0.6740 |
| 2024/2025 | 186 | Naive trailing-10 | 1.1013 | 0.2206 | 0.7346 |
| Pooled | 549 | Gate Zero | 1.0500 | 0.2139 | 0.6899 |
| Pooled | 549 | SHRINK | 1.0500 | 0.2139 | 0.6899 |
| Pooled | 549 | Climatology | 1.0645 | 0.2194 | 0.6804 |
| Pooled | 549 | Naive trailing-10 | 1.1264 | 0.2206 | 0.7897 |

Dev gate (pooled 1X2 LL and RPS must beat climatology AND naive
trailing-10, and OU2.5 LL must beat both baselines):

| Leg (pooled) | Gate Zero | SHRINK |
|---|---|---|
| 1X2 LL vs climatology (1.0500 < 1.0645) | WIN | WIN |
| 1X2 LL vs naive (1.0500 < 1.1264) | WIN | WIN |
| RPS vs climatology (0.2139 < 0.2194) | WIN | WIN |
| RPS vs naive (0.2139 < 0.2206) | WIN | WIN |
| OU2.5 LL vs climatology (0.6899 < 0.6804) | **LOSE** | **LOSE** |
| OU2.5 LL vs naive (0.6899 < 0.7897) | WIN | WIN |
| **Dev gate** | **FAIL (5/6)** | **FAIL (5/6)** |

Fitted home intercept / rho per target season (both arms, identical):
2022/2023: 0.2576 / −0.10; 2023/2024: 0.2303 / −0.15;
2024/2025: 0.3112 / −0.10.

## Why the OU leg fails (measured facts, recorded not acted on)

Gate Zero loses the OU2.5 log-loss leg to climatology in **all three**
dev seasons individually (0.6973 vs 0.6920; 0.6890 vs 0.6767;
0.6844 vs 0.6740), so the pooled loss is not a one-season accident.
It is also not a level miss: pooled, Gate Zero's mean P(over 2.5) is
0.4323 against an actual over-rate of 0.4171 (+1.51pp), and
climatology's is 0.4339 (+1.68pp) — the two are level-equivalent, yet
climatology scores the better OU log-loss. The model's per-match OU
spread does not pay on this window: its match-level over
probabilities are worse than a constant. The worst season is
2023/2024, where the model also badly under-predicts home wins
(mean P(HW) 0.4169 vs actual 0.5253, −10.83pp) — that season's home
win rate (0.5253) is the highest in the corpus and the ratings
fitted on earlier seasons cannot see it. In 2024/2025 the model
loses all three metrics to climatology. No gate is moved: the
verdict is FAIL and nothing ships. A future revisit would need a
pre-registered OU treatment tested on a fresh virgin window — not a
post-hoc rescue of this one.

## SHRINK identity (expected, confirmed mechanically)

SHRINK is numerically identical to Gate Zero pooled and per season.
Verified cause: no team had 1–5 prior in-league matches in any
scored season's training data — every team entering a scored season
either had n = 0 prior matches (pure entrant, already at the
league-mean fallback in both arms: 2, 3, 1 entrants) or n ≥ 30, so
the n/6 scaling never bit on a fitted rating. A synthetic test
proved the SHRINK scaling itself is active (n = 3 gives factor 0.5).

## Virgin: NOT read

No arm passed the dev gate, so under the frozen rule the virgin
window (2025/2026, n = 197 model rows) was not read, no virgin fit
was made, and no virgin leg was scored. The 2025/2026 goals-level
jump (3.09 goals/match) therefore plays no part in this verdict —
it remains an untested virgin fact. The 2026/2027 partial reserve
(n = 65) is untouched.

## Verification notes (coordinator, independent of Codex)

- Full DC fit re-implemented from scratch by the coordinator (own
  code, same prereg spec): fitted home intercepts, rhos, and every
  pooled/per-season metric for both arms and both baselines
  reproduce Codex's numbers to 4 decimal places.
- Metrics recomputed from `results_dev.csv` reproduce
  `results_dev.json` exactly (pooled and per arm/baseline).
- Dev isolation confirmed: `results_dev.csv` has 549 rows, seasons
  2022/2023–2024/2025 only; no 2025/2026 or 2026/2027 match id
  appears in any dev output; the dev loader asserts the four-season
  set and the frozen counts (198/165/198/186).
- Probability sums: max |sum − 1| = 4.44e-16; no NaN probabilities.
- Determinism: two dev runs produce byte-identical
  `results_dev.json`.
- One coordinator correction during Phase A verification (before any
  fitting): the halves variance in `eda.py` was computed as squared
  deviations from the pooled share rather than from the mean of the
  per-match shares (the TN/J1 standard); fixed to the standard
  estimator — observed variance 0.119824 → 0.119702, ratio
  0.9582 → 0.9572 — with the three quoting docs updated. The frozen
  constant (0.4323) is unaffected and the conclusion (NOISE) is
  unchanged.
- One coordinator correction during Phase A verification: two event
  counts in the DATA_UNDERSTANDING coverage table (2025/2026: 178,
  2026/2027: 57) disagreed with `inventory_summary.json` and the CSV
  (184, 61); corrected to the file values.

## Outcome

G-MK verdict is **FAIL**. No arm ships; no predictions file; the
league completes with 0 of 5 candidates live (G-MK failed at dev;
S/C/K/T not buildable). The engine and dev results remain in the
tree as the auditable record.
