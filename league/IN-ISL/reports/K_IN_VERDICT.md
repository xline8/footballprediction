# Verdict — K-IN (India Indian Super League cards)

**FAIL at the dev gate. Virgin 2025/2026 deliberately NOT read.
Nothing ships.**

Single-arm candidate by design (FEATURES dropped X8: referee
coverage 13.5% in dev, 0% in the virgin, no trait computable).
Target: **event-unified yellows** — the pre-fitting decision of
DATA_UNDERSTANDING §3 (stats feed undercounts the event feed in
every dev season; NO-Eliteserien precedent). Primary line 4.5.

## Dev (walk-forward, scored 2022/2023–2024/2025, n=419; pooled LL@4.5)

| Method | LL@4.5 |
|---|---|
| Gate Zero | 0.6738 |
| League base rate | 0.6921 |
| Naive trailing-10 | **0.6681** |

## Gate arithmetic (frozen legs, applied mechanically)

- Dev gate requires beating BOTH baselines. Gate Zero beats the
  league base rate (0.6738 < 0.6921) and loses to naive
  trailing-10 by 0.0057 (0.6738 > 0.6681) — the K-J2 failure
  shape (there by 0.0010). Arm dead; the virgin runner refused
  the non-passing arm and `engine/cards/results_virgin.json`
  records `virgin_read: false`.
- Context, not excuse: IN's team yellows trait is only moderate
  (F2, r=0.469) and the league's yellow level stepped up in
  2023/2024 (3.57 → 4.61 events/match) — a trailing-10 mean
  tracks a level step faster than decayed ratings do. The gate
  is the gate.

## What ships

Nothing. 2025/2026 remains the virgin for one future read under
a new prereg; 2026/2027 confirmatory untouched.
