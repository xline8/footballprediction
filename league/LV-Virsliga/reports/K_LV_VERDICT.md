# Verdict — K-LV (Latvia Virsliga cards model)

**FAIL — dev gate.** Nothing ships. The virgin 2026 was NOT read.

## Dev results (walk-forward over the stats era; warm-up 2025-03-05–04-30, scored 2025-05-01–11-09, n=133)

| arm | LL@4.5 | league base rate | naive trailing-10 |
|---|---|---:|---:|
| Gate Zero | **0.678231** | 0.692909 | 0.671066 |

Target: event-unified yellows (Yellow + YellowRed). Gate Zero's
mean predicted total (4.74) is close to the actual (4.77) and its
mean P(over 4.5) is 0.495 vs actual 0.511 — the level is right —
but its log loss loses to the naive trailing-10 by 0.007. The
decayed team-rating machinery adds nothing over a plain
trailing-10 average in this 133-match window, despite the
respectable yellows trait reliability (split-half r ≈ 0.6).

## Gate arithmetic (frozen in PREREG_K_LV.md)

Dev gate requires pooled dev LL@4.5 to beat BOTH baselines:

- vs league base rate: 0.678231 < 0.692909 — **PASS**.
- vs naive trailing-10: 0.678231 > 0.671066 — **FAIL**.

Gate Zero fails its dev gate ⇒ candidate FAILS, virgin NOT read.
No rescue arm was invented; the gate was not moved.

## Robustness note (verified, not assumed)

The LV harness scores all three series with the model's single
dispersion r (21.69, estimated on warm-up predictions), while the
MA reference estimated a separate r per series (model 21.69,
base 30.16, naive 16.92). Recomputing with per-kind r: naive
0.6715, league base 0.6979 — the verdict is unchanged (Gate Zero
still loses to naive). The failure is in the model, not in the
r convention.

## Verification

Model LL@4.5 recomputed independently from
`predictions_dev.csv` (0.678231, exact); both baseline LLs
recomputed independently from the raw CSV + frozen model code
(league 0.692909, naive 0.671066, exact); targets match the raw
CSV on all 133 scored matches; scored window 2025-05-01–11-09
(74 dates). Dev harness loads 2025 rows only (asserted in code);
no 2026 row was read. The virgin function in the engine is a
completed mirror of the dev construction, marked UNTESTED — it
must not be run, since the dev gate failed.
