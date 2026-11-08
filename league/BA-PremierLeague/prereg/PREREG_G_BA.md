# Pre-registration — G-BA (BA-PremierLeague goals model)

Frozen: 2026-11-10, before any fitting. Branch `build/ba-premier-league`.
Design authority: `league/BA-PremierLeague/analysis/MODEL_DESIGN.md` §1
(candidate G-BA) + shared validation frame; features per
`league/BA-PremierLeague/analysis/FEATURES.md` (X1 goals-only,
X5 naive baseline, X2-SHRINK); evidence per
`league/BA-PremierLeague/analysis/EDA.md` (F1/F2/F3/F4/F13).
Reference implementation: production Dixon-Coles in `model_v2.py`
(class `DC`, `probs`), production config `v2_config.json` (hl = 270).
Engine port pattern: `league/CY-1Division/engine/goals/` adapted to
this league's CSV (see also `league/J1/engine/goals/` for the
harness/results layout).

## Reference architecture (all arms share this unless an arm says otherwise)

- Dixon-Coles fit, copied pattern from production `model_v2.py`:
  iterative multiplicative updates, 14 sweeps, damping 0.7, +0.25
  smoothing, home advantage `h` fitted (init 0.28), attack `a` and
  defence `d` per team (init 0), score matrix to MAXG = 10 with the
  production `tau` low-score correction.
- Rho: chosen per fit from the grid (0.0, −0.05, −0.10, −0.15) by
  weighted log-likelihood on goals only, exactly as production.
- Observation (X1): goals-only — no xG exists anywhere in this league
  (stats null, shotmap empty, 1,036/1,036), so this is the reference
  blend's documented fallback, not a variant.
- Time decay: weight w = 0.5 ** ((cutoff − match_date).days / 270).
  Half-life 270 days is the production value, frozen — no search.
- Fit scope for a target season S: all BA matches with date strictly
  before the first match date of S (expanding window, season-blocked:
  one fit per target season, whole season predicted from that fit).
- **Awarded matches (4) are excluded from every fit and every
  evaluation** (their 3-0/0-3 scorelines do not reflect play).
- Teams unseen in training start at the league mean (a = d = 0).

## Arms

1. **Gate Zero** — the unmodified reference above.
2. **Arm SHRINK** — Gate Zero plus exactly one change at prediction
   time: for a team with fewer than 6 prior in-league matches in the
   training window, `a *= n/6`, `d *= n/6` (n = prior in-league
   matches; n=0 identical to Gate Zero's unseen rule). The sanctioned
   G-J2-lesson arm for thin-history season openers (feature
   X2-SHRINK, EDA F4: no mover offset is estimable — no Bosnian
   sibling exists — so shrinkage is the thin-data treatment).

## Dev protocol

- Dev period: seed season 2021/2022 (fit history, never scored);
  scored folds 2022/2023, 2023/2024, 2024/2025, 2025/2026
  (n = 772 after excluding the 4 awarded matches: 198 + 198 + 196
  + 180). Pooled dev = the four evaluation seasons combined.
- Metrics per arm per season and pooled: mean 1X2 log-loss (natural
  log), mean RPS (outcomes ordered H, D, A;
  RPS = 0.5 · Σ_k (Σ_{j≤k} p_j − Σ_{j≤k} y_j)²), mean OU2.5 log-loss
  (binary, on P(over 2.5)).
- Baselines: climatology — for target season S, the pooled outcome
  rates (home win / draw / away win) and OU2.5 over-rate of all BA
  seasons strictly before S (awarded excluded). The same climatology
  probabilities score LL, RPS and OU LL for that season. Also
  reported (not a gate leg): naive trailing-10 (X5) — Poisson with
  lambdas from each team's trailing-10 GF/GA means (min 6 of 10,
  else league mean), scored the same way.
- The dev harness must not read season "2026/2027" rows at all.
  Virgin data is touched only by the separate virgin step, once,
  after dev results are frozen in the results file.

## Virgin protocol

- Virgin window: season "2026/2027" (in progress, rounds 1–13,
  n = 64 as of 2026-11-08; round 10 has 4 matches — one fixture
  absent from the warehouse). Marked TRANSITIONAL: read ONCE, after
  dev freezes, only for arms passing the dev gate. Fit = all BA
  matches dated before the first 2026/2027 match (seasons
  2021/2022–2025/2026, awarded excluded). A confirmatory re-read
  at season end is reserved and is a separate, later read.
- Virgin climatology: pooled 2021/2022–2025/2026 outcome rates and
  OU2.5 over-rate (awarded excluded).
- Calibration per arm: (i) mean predicted home-win probability minus
  actual home-win rate; (ii) mean predicted P(over 2.5) minus actual
  over-rate. Standard error of each difference:
  SE = sd(pred_i − y_i) / √n over the 64 matches, reported with the
  difference.

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev 1X2 LL and RPS of an arm must beat climatology, and OU2.5 LL must beat the base-rate baseline, else the arm is dead. Virgin legs — (i) LL leg: arm's virgin 1X2 LL ≤ Gate Zero's AND ≤ climatology's; (ii) calibration leg: |mean predicted − actual| ≤ 1.0pp pooled for home-win rate and for OU2.5 over-rate, SEs reported; a breach within 1 SE of the boundary is recorded PROVISIONAL PASS, beyond it FAIL; (iii) per-season sign check on dev (arm LL ≤ Gate Zero LL in at least half the dev seasons) for the both-pass rule. Both-pass rule: if Gate Zero and a variant both pass all legs, the lower pooled virgin 1X2 LL ships; if only one passes, it ships; if none passes, G-BA verdict is FAIL and nothing ships.

Reading of the legs, fixed here so the verdict is mechanical:

- An arm *passes* iff it survives the dev gate AND passes virgin
  legs (i)–(ii) (a PROVISIONAL PASS counts as a pass, recorded as
  such) AND, for variant arms only, leg (iii). Gate Zero is exempt
  from (iii) (it is the comparator).
- If Gate Zero and SHRINK both pass, the both-pass rule's "lower
  pooled virgin 1X2 LL ships" applies; ties go to the simpler arm
  (Gate Zero before SHRINK).
- **Frozen rule: Gate Zero fails dev ⇒ variants moot.** If Gate Zero
  fails its own dev gate, SHRINK is not virgin-read, the verdict is
  FAIL, and the virgin is NOT read.

## Outputs

- Engine: `league/BA-PremierLeague/engine/goals/` (this league's own
  code: fit/predict/harness modules + a CLI runner).
- Dev results: `league/BA-PremierLeague/engine/goals/results_dev.json`
  (+ `results_dev.csv`, force-added).
- Fitted parameters for the virgin fit:
  `league/BA-PremierLeague/engine/goals/fitted_params_virgin.json`.
- Virgin predictions: `league/BA-PremierLeague/predictions/g_ba_virgin_predictions.csv`
  — the shipped arm's predictions (Gate Zero's if nothing ships,
  labelled in the verdict), one row per 2026/2027 match, with FT
  lambdas, FT 1X2 / OU (1.5, 2.5, 3.5) / BTTS probabilities, and
  1H/2H lines derived by splitting the same lambdas with the frozen
  BA goals constant 0.4493 (1H λ = 0.4493·FT λ, 2H λ = 0.5507·FT λ;
  1H OU lines 0.5/1.5/2.5, 2H OU lines 1.5/2.5/3.5, same rho and
  score-matrix machinery). Halves are presentation only, never
  fitted (design §1d / EDA F3).
- Verdict: `league/BA-PremierLeague/reports/G_BA_VERDICT.md`.

Production code and data are untouched. No push. No merge.
