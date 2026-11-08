# Verdict — T-LV (Latvia Virsliga total shots model)

**FAIL — virgin leg (i).** All three arms pass dev but lose to the
naive baseline on the virgin. Nothing ships.

## Dev results (walk-forward over the stats era; warm-up 2025-03-05–04-30, scored 2025-05-01–11-09, n=133)

| arm | LL@26.5 | league base rate | naive trailing-10 |
|---|---|---:|---:|
| A (v1) | 0.689508 | 0.696231 | 0.699169 |
| B (v2 level layer) | 0.688321 | 0.696231 | 0.699169 |
| C (E9 trailing-r) | **0.685859** | 0.696231 | 0.699169 |

All three arms beat both baselines on dev → all three reach the
virgin.

## Virgin results (2026, n=179, read once for the dev-passing arms)

| arm | LL@26.5 | league base rate | naive trailing-10 | calibration (actual − predicted) | SE |
|---|---|---:|---:|---:|---:|---:|
| A | 0.667470 | 0.695736 | **0.650779** | +0.0030 (+0.30pp) | 0.03648 |
| B | 0.666705 | 0.695736 | **0.650779** | +0.0065 (+0.65pp) | 0.03644 |
| C | 0.665752 | 0.695736 | **0.650779** | −0.0020 (−0.20pp) | 0.03642 |

Mean P(over 26.5): A 0.4774 / B 0.4739 / C 0.4825 vs actual
over-rate 0.4804. Virgin mean total shots 26.79 (dev 27.66).

## Gate arithmetic (frozen in PREREG_T_LV.md)

- Leg (i) LL: each arm must be ≤ the reference arm's (A, 0.667470)
  AND ≤ best baseline's. A ≤ A ✓, B ≤ A ✓, C ≤ A ✓ — but best
  baseline is the naive trailing-10 at 0.650779, and A 0.667470,
  B 0.666705, C 0.665752 are ALL above it — **FAIL for all three**.
- Leg (ii) calibration: all |cal| ≤ 0.65pp ≤ 1.0pp — **PASS**.
- Leg (iii) dev sign check: B and C pooled dev LL ≤ A's — ✓,
  moot since leg (i) fails.

The naive trailing-10 — weak on dev (0.699169, worst of all) —
is the best predictor on the virgin (0.650779). The shots
family's regression ratings do not beat a plain trailing
average out-of-sample in this league. The both-pass rule has no
passing arm → **T-LV verdict is FAIL and nothing ships**.

## Verification

Dev LLs recomputed independently from `predictions_dev.csv`
(A 0.689508, B 0.688321, C 0.685859, exact); both dev baseline
LLs recomputed independently (league 0.696231, naive 0.699169,
exact). Virgin LLs + calibrations recomputed independently with
a separate date-grouped walk through the frozen model code,
including the lambda/r refit on pre-virgin rows (lambda 3.0,
r_A 24.5363): A 0.667470, B 0.666705, C 0.665752, league
0.695736, naive 0.650779 — exact. Targets match the raw CSV on
all scored matches in both windows. The virgin walk is
date-grouped (same-date matches never see each other) and the
regression store refits on strictly prior days only.
