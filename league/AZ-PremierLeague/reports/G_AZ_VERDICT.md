# Verdict — G-AZ (Azerbaijan Premier League goals, Dixon–Coles goals-only)

**FAIL — Gate Zero passes the dev gate on all three legs, passes the virgin
LL leg, but fails the virgin calibration leg on OU2.5. Virgin WAS read
(once, 2025/2026, n = 198). Nothing ships.**

## Dev (season-blocked walk-forward; seed 2021/2022, 112 finished matches; pooled n = 540)

| Arm | 1X2 LL | RPS | OU2.5 LL |
|---|---|---|---|
| Gate Zero | 1.0111 | 0.2066 | 0.6648 |
| SHRINK | 1.0111 | 0.2066 | 0.6648 |
| Climatology | 1.0810 | 0.2325 | 0.6933 |
| Naive trailing-10 | 1.0802 | 0.2239 | 0.7194 |

Per-season Gate Zero vs climatology (1X2 LL / RPS / OU2.5 LL):

| Season | n | Gate Zero | Climatology |
|---|---|---|---|
| 2022/2023 | 180 | 0.9215 / 0.1798 / 0.6799 | 1.0853 / 0.2332 / 0.6939 |
| 2023/2024 | 180 | 1.1059 / 0.2401 / 0.6624 | 1.0671 / 0.2350 / 0.6937 |
| 2024/2025 | 180 | 1.0058 / 0.2000 / 0.6519 | 1.0906 / 0.2292 / 0.6924 |

Gate arithmetic (PREREG_G_AZ): pooled 1X2 LL beats climatology ✓
(1.0111 < 1.0810); pooled RPS beats climatology ✓ (0.2066 < 0.2325);
pooled OU2.5 LL beats the base-rate baseline ✓ (0.6648 < 0.6933).
**Dev gate PASSES on all three legs for both arms.** The one weak season is
2023/2024, where Gate Zero loses the 1X2 LL and RPS legs to climatology
(1.1059 vs 1.0671; 0.2401 vs 0.2350) but still wins the OU2.5 leg
(0.6624 vs 0.6937); the pooled gate is what the prereg freezes, and it
passes. SHRINK is byte-identical to Gate Zero in every season
(0 changed rows, 0 thin-history teams), exactly as EDA F13 predicted:
no team falls in the 1–5 prior-match band at any target-season start.

## Virgin (2025/2026, complete season, n = 198; fit = all 652 matches before 2025-08-15)

| Arm | 1X2 LL | RPS | OU2.5 LL | Climatology 1X2 LL |
|---|---|---|---|---|
| Gate Zero | 1.0185 | 0.2116 | 0.7395 | 1.0841 |
| SHRINK | 1.0185 | 0.2116 | 0.7395 | 1.0841 |

Calibration (predicted − actual, pp; SE in pp):

| Arm | Home-win diff | OU2.5 diff |
|---|---|---|
| Gate Zero | +4.23 ± 3.28 | −6.29 ± 3.68 |
| SHRINK | +4.23 ± 3.28 | −6.29 ± 3.68 |

Virgin fit: rho 0.0, mu 1.2392, h 0.1640. Actual virgin rates: home-win
0.374, OU2.5 over-rate 0.485.

Gate arithmetic (PREREG_G_AZ):

- **LL leg (i) — PASS for both arms.** Virgin 1X2 LL 1.0185 ≤ Gate Zero's
  virgin 1X2 LL 1.0185 (equality, as the arms are identical) and ≤
  climatology's 1.0841. Note on reading: the leg compares virgin-window
  numbers with virgin-window numbers. An earlier draft of this verdict
  compared the virgin LL against Gate Zero's *dev* LL (1.0111) and called
  the leg a fail; that cross-window comparison is not what the prereg
  says and is corrected here — the outcome is unchanged because the
  calibration leg fails regardless.
- **Calibration leg (ii) — FAIL for both arms.** Home-win: |+4.23pp| breaches
  the 1.0pp boundary by 3.23pp, which is 3.23 / 3.28 = 0.98 SE — within
  1 SE, so PROVISIONAL PASS on this component. OU2.5: |−6.29pp| breaches
  the boundary by 5.29pp, which is 5.29 / 3.68 = 1.44 SE — beyond 1 SE,
  so FAIL on this component. The leg requires both components; it fails.
- **Per-season sign check (iii) — PASS for SHRINK, 3/3.** SHRINK dev LL
  equals Gate Zero dev LL in all three dev seasons (byte-identical arms).

**Both-pass rule: no arm passes all legs, so G-AZ verdict is FAIL and
nothing ships.** No virgin predictions file, no fitted-params file.

## Why it failed (diagnosis, not a rescue)

- The failure is a totals-level miss in the virgin season, not an entrant
  effect. The model under-predicted the over-2.5 rate (mean predicted
  0.422 vs actual 0.485) and its virgin OU2.5 LL (0.7395) is worse than
  climatology's (0.6930), even though its 1X2 LL beats climatology
  clearly (1.0185 vs 1.0841) and its RPS does too (0.2116 vs 0.2372).
- Split by entrant involvement (diagnostic replay): the 63 virgin matches
  involving a 2025/2026 entrant (Karvan, Imisli) are well calibrated on
  totals (predicted over 0.400 vs actual 0.413, OU LL 0.6823). The miss
  sits in the 135 established-team matches: predicted over 0.432 vs
  actual 0.519, OU LL 0.7662, at 2.70 goals/match — the established
  teams scored hotter in 2025/2026 than the decay-weighted training
  history implied (virgin fit mu 1.2392 per team-match vs virgin actual
  1.2955). The home-win over-prediction (+4.23pp) is the same level
  story from the other side: predicted home-win 0.416 vs actual 0.374.
- The dev gate passed, so this is not a case of a model that never worked:
  it worked in walk-forward and then the virgin season's level moved
  against it. With n = 198 the OU breach is 1.44 SE beyond the boundary —
  a real miss, not a borderline call. The 2026/2027 season-end
  confirmatory read will show whether the level reverts or persists.

## Verification (independent of Codex)

- Pooled dev metrics recomputed from `results_dev.csv` per-row columns
  reproduce `results_dev.json` exactly (LL 1.0111, RPS 0.2066, OU 0.6648;
  climatology 1.0810 / 0.2325 / 0.6933; naive 1.0802 / 0.2239).
  Probabilities sum to 1 on all 540 rows; SHRINK columns are identical
  to Gate Zero's on all 540 rows.
- A from-scratch re-implementation of the production DC pattern (written
  from the `model_v2.py` fit loop and `football_etl.py` pois/tau, not from
  the AZ engine) reproduces the harness fold numbers exactly to 4dp on
  two folds: 2022/2023 LL 0.9215 / RPS 0.1798 / OU 0.6799 and 2024/2025
  LL 1.0058 / RPS 0.2000 / OU 0.6519, with matching rho (−0.10 / 0.00)
  and mu (1.2906 / 1.3234); max per-match probability difference ~5e-11.
- The same independent implementation reproduces the virgin numbers
  exactly: LL 1.0185, RPS 0.2116, OU 0.7395, calibration +4.23pp ± 3.28
  and −6.29pp ± 3.68, rho 0.0, mu 1.2392; climatology 1.0841 / 0.2372 /
  0.6930. The virgin FAIL is genuine, not an engine bug.
- Fit bookkeeping checks out: cutoffs are each target season's first
  match date (2022-08-05, 2023-08-04, 2024-08-02, virgin 2025-08-15);
  training counts 112 / 292 / 472 / 652 are the exact expanding sums;
  no 2025/2026 row appears in any dev output and no 2026/2027 row
  appears in any output (asserted in the harness and re-checked from
  the files). Virgin was read exactly once (`virgin-metrics` only;
  `virgin-predict` was never run).
- `dc.py` / `arms.py` differ from the VN reference only in league naming;
  `harness.py` differs only by the intended AZ adaptations (seasons,
  virgin guard covering 2025/2026 and 2026/2027, halves constant 0.4344).

## Ships

Nothing. No fitted params, no virgin predictions, no daily-runner
artefact. S/C/K/T were already not buildable (separate prereg).
League completion state: all buildable candidates (G-AZ only) through
their gates — **league complete with 0 of 1 candidates passing
(0 markets live)**. 2026/2027 (in progress, 64 matches through
2026-11-08) is reserved for a season-end confirmatory read; no gate
depends on it.
