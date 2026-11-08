# Verdict — C-LV (Latvia Virsliga corners model)

**FAIL — dev gate.** Nothing ships. The virgin 2026 was NOT read.

## Dev results (walk-forward over the stats era; warm-up 2025-03-05–04-30, scored 2025-05-01–11-09, n=133)

| arm | LL@9.5 | league base rate | naive trailing-10 |
|---|---|---:|---:|
| Gate Zero | **0.723840** | 0.699255 | 0.682656 |

Gate Zero's mean predicted total (9.95) is close to the actual
(10.11) and its mean P(over 9.5) is 0.519 vs actual 0.571, yet its
log loss is worse than both baselines — the corners distribution
the model implies (NB r = 1.15 fitted on the 37 warm-up rows with
prior_n ≥ 10, possession beta +0.005) fits this window worse than
a constant base rate and worse than a plain trailing-10. The
territorial possession multiplier does not rescue it: the naive
tracker, which uses no possession term at all, wins by 0.041.

## Gate arithmetic (frozen in PREREG_C_LV.md)

Dev gate requires pooled dev LL@9.5 to beat BOTH baselines:

- vs league base rate: 0.723840 > 0.699255 — **FAIL**.
- vs naive trailing-10: 0.723840 > 0.682656 — **FAIL**.

Gate Zero fails its dev gate ⇒ candidate FAILS, virgin NOT read.
No rescue arm was invented; the gate was not moved.

## Verification

Model LL@9.5 recomputed independently from
`predictions_dev.csv` (0.723840, exact); both baseline LLs
recomputed independently from the raw CSV + frozen model code
(league 0.699255, naive 0.682656, exact); targets match the raw
CSV on all 133 scored matches; scored window 2025-05-01–11-09
(74 dates). Dev harness loads 2025 rows only (asserted in code);
no 2026 row was read. The virgin function in the engine is a
completed port of MA's virgin, marked UNTESTED — it must not be
run, since the dev gate failed.
