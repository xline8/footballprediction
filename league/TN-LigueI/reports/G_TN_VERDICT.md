# Verdict — G-TN (Tunisia Ligue I goals): **FAIL (virgin calibration leg)**

Frozen decision: PREREG_G_TN.md (prereg commit d6bdacb9, before any
fitting). Virgin 2025/26 WAS read, once, for both dev-passing arms —
Gate Zero passed the dev gate 6/6, so the virgin read was legitimate.
2026/27 was not touched (confirmatory reserve).

Dev (pooled 2022/23–2024/25, n = 602 model matches, season-blocked
expanding fit, warm-up 2021/22 complete, n = 156):

| Arm | 1X2 LL | RPS | OU2.5 LL | Dev gate |
|---|---|---|---|---|
| Gate Zero | 1.0043 | 0.2000 | 0.6338 | PASS (6/6) |
| SHRINK | 1.0043 | 0.2000 | 0.6338 | PASS (6/6, identical) |
| Climatology | 1.0637 | 0.2194 | 0.6425 | — |
| Naive trailing-10 | 1.1212 | 0.2209 | 0.7309 | — |

Per season, Gate Zero 1X2 LL / RPS / OU2.5 LL: 2022/23 1.0494 /
0.2146 / 0.6258; 2023/24 0.9905 / 0.1963 / 0.6291; 2024/25 0.9770 /
0.1906 / 0.6438. Climatology per season: 2022/23 1.0664 / 0.2217 /
0.6320; 2023/24 1.0498 / 0.2150 / 0.6492; 2024/25 1.0713 / 0.2207 /
0.6464. Naive trailing-10 per season: 2022/23 1.2441 / 0.2335 /
0.7026; 2023/24 1.0532 / 0.2126 / 0.7761; 2024/25 1.0688 / 0.2164 /
0.7217. SHRINK is identical to Gate Zero in every season. Fitted
home intercept / rho per season: 2022/23 0.0031 / 0.00; 2023/24
0.1536 / 0.00; 2024/25 0.2382 / 0.00. (The near-zero 2022/23 home
intercept was independently re-fitted from scratch and reproduced
exactly — the raw 1.50 home/away goal ratio is absorbed by the
rating dispersion in that single-season window, not a fit bug.)

SHRINK is numerically identical to Gate Zero pooled and per season
(1.0043 / 0.2000 / 0.6338 in every window). Verified cause: no team
had 1–5 prior in-league matches in any scored season's training
data — every team entering a scored season either had n = 0 prior
matches (pure entrant, already at the league-mean fallback in both
arms) or n ≥ 26, so the n/6 scaling never bit on a fitted rating;
a synthetic test proved the SHRINK scaling itself is active (n=3
gives factor 0.5).

Virgin (2025/26, n = 237 model matches, fit on all 758 matches ≤
2024/25; home intercept 0.2695, rho 0.00):

| Arm | 1X2 LL | RPS | OU2.5 LL | Leg (i) | Leg (ii) | Leg (iii) | Verdict |
|---|---|---|---|---|---|---|---|
| Gate Zero | 0.9785 | 0.1950 | 0.5876 | PASS | FAIL | EXEMPT | **FAIL** |
| SHRINK | 0.9785 | 0.1950 | 0.5876 | PASS | FAIL | PASS (3/3) | **FAIL** |
| Climatology | 1.0639 | 0.2198 | 0.5913 | — | — | — | — |
| Naive trailing-10 | 1.0937 | 0.2204 | 0.6570 | — | — | — | — |

Virgin legs, leg by leg:

- (i) LL leg: PASS for both arms — virgin 1X2 LL 0.9785 ≤ Gate
  Zero's 0.9785 (equality) and ≤ climatology's 1.0639.
- (ii) Calibration leg: FAIL. Home-win rate: mean predicted
  0.4225 vs actual 0.4599, diff −3.74pp (SE 2.96pp) — a breach of
  the 1.0pp boundary, but within 1 SE of it (3.74 ≤ 1.0 + 2.96 =
  3.96, by a 0.22pp margin) → PROVISIONAL PASS. OU2.5 over-rate:
  mean predicted 0.3502 vs actual 0.2700, diff +8.02pp (SE
  2.87pp) — the breach exceeds the boundary by 7.02pp, i.e. 2.45
  SEs beyond it (8.02 > 1.0 + 2.87 = 3.87) → FAIL. One quantity
  fails outright, so leg (ii) fails.
- (iii) Per-season sign check (SHRINK only): PASS — SHRINK 1X2 LL
  ≤ Gate Zero 1X2 LL in 3 of 3 dev seasons (by equality).

Both-pass rule: no arm passes all legs, so there is no winner and
nothing ships. No virgin predictions file exists (correctly — the
runner writes one only for a winner).

Diagnosis (measured facts, recorded not acted on): the virgin
season is a goals-level regime shift the expanding fit could not
absorb — 2025/26 scored 1.72 goals/match (OU2.5 over-rate 0.270)
against 2.00 (0.339) in the dev window and 2.03 (0.346) in the
2024/25 training season, the lowest of any complete season in the
corpus. The model, fitted on the higher-scoring history with a
270-day half-life, predicted an over-rate of 0.350 — essentially
its training level — against an actual 0.270. The LL legs still
passed because the per-match total-goals distribution stayed close
enough on log-likelihood (OU2.5 LL 0.5876 vs climatology 0.5913),
but the calibration leg is a level test and the level moved by
8 points. The home-win calibration miss (−3.74pp) points the same
way: the model under-predicted home wins while over-predicting
goals. No gate is moved: the verdict is FAIL and nothing ships.
A future revisit would need a pre-registered level-shift treatment
(e.g. a shorter decay or a level layer) tested on a fresh virgin
window — not a post-hoc rescue of this one.

Verification: every headline number above was independently
recomputed from the CSVs through a second code path (own DC fit
and prediction code): dev pooled/per-season metrics, virgin
1X2 LL / RPS / OU2.5 LL, both calibration diffs and SEs, and the
climatology virgin numbers all reproduce to 4 decimal places; the
virgin fit's ratings match `fitted_params_virgin.json` exactly
(max |diff| 0.00e+00); probability sums are 1.000000; no
virgin/reserve match id appears in `results_dev.csv`.
