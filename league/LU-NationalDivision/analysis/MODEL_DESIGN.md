# Step 6 — Model Design: LU-NationalDivision

Design authority: EDA.md (F1–F6) + FEATURES.md (X1 goals-only, X5
baseline-only; X2–X9 dropped). Reference pattern: production
Dixon-Coles (`model_v2.py`, `v2_config.json` hl = 270) as carried by
the program analogues `PREREG_G_SE.md` / `PREREG_G_QA.md`.

## Feasibility matrix

| Candidate | Target exists? | Virgin window has target? | Verdict |
|---|---|---|---|
| G-LU (goals) | Yes — FT scores, all seasons | Yes — 2025/26 complete (n=240) | **BUILD** |
| S-LU (SOT) | No — stats absent, shotmap empty, all seasons | — | NOT BUILDABLE |
| C-LU (corners) | No — same absence | — | NOT BUILDABLE |
| K-LU (cards) | No — no yellows anywhere; reds only (0.30/match), referee names empty | — | NOT BUILDABLE |
| T-LU (total shots) | No — same absence | — | NOT BUILDABLE |

One candidate is built: **G-LU**. The other four get short
not-buildable verdicts (`reports/{S,C,K,T}_LU_VERDICT.md`) recording
the data absence; no prereg, no engine, no virgin read for them.

## G-LU — candidate definition

- **Reference architecture (all arms):** Dixon-Coles fit on goals
  only (X1 fallback), copied from production `model_v2.py`:
  ratings fitted by direct Poisson log-likelihood maximisation
  (scipy L-BFGS, sum-to-zero identification, ridge 1e-3); rho chosen
  per fit from the grid (0.0, −0.05, −0.10, −0.15) by training
  log-likelihood; MAXG = 10; tau = standard Dixon-Coles low-score
  correction; home intercept fitted (init 0.25). Time decay weight
  w = 0.5 ** ((cutoff − match_date).days / 270), half-life 270 days
  (production value, frozen — no search). Fit scope for target
  season S: all LU matches dated strictly before the first match
  date of S (expanding window, season-blocked: one fit per target
  season, whole season predicted from that fit). Teams unseen in
  training start at the league mean (attack/defence exponents 0.0).
- **Arm 1 — Gate Zero:** the reference above, unmodified.
- **Arm 2 — SHRINK:** Gate Zero plus the sanctioned G-J2-lesson
  change, defined verbatim from `PREREG_G_FI.md` (via
  `PREREG_G_SE.md`): at prediction time a team with n < 6 prior
  in-league matches has a *= n/6, d *= n/6, where n is the number of
  matches the team played in the training data strictly before the
  predicted season; n ≥ 6 → no change; n = 0 → exponents 0.0
  (identical to the league-mean fallback). Applies to both attack
  and defence exponents, home and away alike. EDA F4: expected to
  be numerically identical to Gate Zero in this league (no team
  with 1–5 prior matches in any scored season's training data);
  the dev run states the fact mechanically either way.
- **NO ENTRANT arm:** X2 dropped (FEATURES.md) — no sibling league,
  no mover tilt estimable. No other variant arms: X3/X4/X6/X7/X8/X9
  are all data-absent, and no further arm is justified by the EDA.

## Windows (frozen)

- Warm-up: 2021/22 (n=240, complete).
- Dev scored: 2022/23, 2023/24, 2024/25 (pooled n=720).
- Virgin: 2025/26 (n=240, complete). Read ONCE, only for arms that
  pass the dev gate. Fit expands to all matches ≤ 2024/25.
- Confirmatory reserve: 2026/27 partial (n=96) — untouched by every
  step in this league; the season-end confirmatory read is a future
  decision, not part of this build.
- Primary line: Over/Under 2.5 goals (dev OU2.5 over-rate 0.603;
  the line the gate's OU leg is scored on).

## Metrics and baselines (frozen, see PREREG_G_LU.md)

Per arm per season and pooled: mean 1X2 log-loss, mean RPS
(outcomes ordered H, D, A), mean OU2.5 log-loss. Baselines:
climatology (pooled outcome rates and OU2.5 over-rate over training
seasons only) and naive trailing-10 (independent Poissons from each
team's trailing-10 mean goals scored). Calibration: mean predicted
− actual for home-win rate and OU2.5 over-rate, SE =
sd(pred_i − y_i)/√n.

## Gates (frozen, see PREREG_G_LU.md)

Dev gate: pooled dev 1X2 LL and RPS must beat climatology AND naive
trailing-10, and OU2.5 LL must beat both baselines, else the arm is
dead. Virgin legs: (i) LL leg — arm's virgin 1X2 LL ≤ Gate Zero's
AND ≤ climatology's; (ii) calibration leg — |mean predicted −
actual| ≤ 1.0pp pooled for home-win rate and OU2.5 over-rate (breach
within 1 SE of the boundary = PROVISIONAL PASS, beyond it FAIL);
(iii) per-season sign check on dev (variant LL ≤ Gate Zero LL in at
least half the dev seasons). Both-pass rule: if Gate Zero and a
variant both pass all legs, the lower pooled virgin 1X2 LL ships;
if only one passes, it ships; if none passes, G-LU verdict is FAIL
and nothing ships. Gates are never moved after results are seen.

## Halves presentation

On PASS only: FT predictions plus 1H/2H lines derived by splitting
the same lambdas with the frozen LU goals constant 0.4294
(1H λ = 0.4294·FT λ, 2H λ = 0.5706·FT λ; 1H OU lines 0.5/1.5/2.5,
2H OU lines 1.5/2.5/3.5, same rho and score-matrix machinery).
Halves are presentation only, never fitted.

## Outputs

- Engine: `league/LU-NationalDivision/engine/goals/` (fit/predict/
  harness + CLI runner + README).
- `results_dev.json` (+ CSV), `results_virgin.json`,
  `fitted_params_virgin.json`.
- On PASS: `predictions/g_lu_virgin_predictions.csv` (force-added).
- Verdict: `reports/G_LU_VERDICT.md`.
