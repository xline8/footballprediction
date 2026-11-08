# Pre-registration — G-IEFD (Ireland First Division goals model)

Frozen: 2026-11-10, before any fitting. Branch `build/ie-first-division`.
Design authority: `league/IE-FirstDivision/analysis/MODEL_DESIGN.md`
§1 (candidate G-IEFD) + shared validation frame; features per
`league/IE-FirstDivision/analysis/FEATURES.md` (X1 goals-only, X2
relegated-mover offset); evidence per
`league/IE-FirstDivision/analysis/EDA.md` (F1/F2/F4/F6).
Reference implementation: production Dixon-Coles in `model_v2.py`
(class `DC`, `probs`), production config `v2_config.json` (hl = 270);
nearest working analogue `league/IE-PremierDivision/engine/goals/`
(goals-only DC, same warehouse format, same season-blocked frame).

## Reference architecture (all arms share this unless an arm says otherwise)

- Dixon-Coles fit, copied pattern from production `model_v2.py`:
  iterative multiplicative updates, 14 sweeps, damping 0.7, +0.25
  smoothing, home advantage `h` fitted (init 0.28), attack `a` and
  defence `d` per team (init 0), score matrix to MAXG = 10 with the
  production `tau` low-score correction.
- Rho: chosen per fit from the grid (0.0, −0.05, −0.10, −0.15) by
  weighted log-likelihood on goals only, exactly as production.
- Observation (X1): **GOALS ONLY**. No xG exists anywhere in this
  corpus (no stats feed, no shotmap, any season), so the blend is
  goals-only throughout — the reference's documented fallback.
- Time decay: weight w = 0.5 ** ((cutoff − match_date).days / 270).
  Half-life 270 days is the production value, frozen — no search.
- Fit scope for a target season S: all IE-FirstDivision **regular**
  matches with date strictly before the first match date of S
  (expanding window, season-blocked: one fit per target season,
  whole season predicted from that fit). Playoff matches are never
  in a fit and never scored.
- Teams unseen in training start at the league mean (a = d = 0).

## Arms

1. **Gate Zero** — the unmodified reference above. Movers start at
   the league mean.
2. **Arm X2** — Gate Zero plus a relegated-mover prior offset
   (feature X2, EDA F4). A club is a *relegated mover* for target
   season S when it played the immediately preceding season in the
   Premier Division (team id present in
   `league/IE-PremierDivision/data/ie_matches.csv` for season S−1)
   and did not play the First Division in that season. For a
   relegated mover, at prediction time in season S only:
   - attack: `a += log(max(mu + 0.23, 0.10) / mu)`
   - defence: `d += log(max(mu − 0.27, 0.10) / mu)`
   where mu is the decay-weighted mean goals per team per match in
   the training window, and +0.23 / −0.27 are the F4 magnitudes
   (mean first-season deltas of the six relegated arrivals in dev,
   2022–2025: GF +0.23, GA −0.27 vs their seasons' league means).
   The offset is added to the fitted rating (league mean 0 for a
   first-time club). Brand-new clubs (no prior season in either tier)
   receive no offset and start at the league mean in every arm.
   A club entering from a lower tier would receive the mirrored
   offset; no tier exists below, so this case is definitional only.

## Dev protocol

- Dev period: seasons 2021–2025, regular season only. Season 2021
  is the initial training window; evaluation seasons are 2022, 2023,
  2024, 2025 under the expanding season-blocked walk-forward above.
  Pooled dev = the four evaluation seasons combined (n = 683).
- Metrics per arm per season and pooled: mean 1X2 log-loss (natural
  log), mean RPS (outcomes ordered H, D, A;
  RPS = 0.5 · Σ_k (Σ_{j≤k} p_j − Σ_{j≤k} y_j)²), mean OU2.5 log-loss
  (binary, on P(over 2.5)).
- Baselines: climatology — for target season S, the pooled outcome
  rates (home win / draw / away win) and OU2.5 over-rate of all
  regular-season matches strictly before S. The same climatology
  probabilities score LL, RPS and OU LL for that season.
- The dev harness must not read season "2026" rows at all. Virgin
  data is touched only by the separate virgin step, once, after dev
  results are frozen in the results file.

## Virgin protocol

- Virgin window: season "2026", **regular-season matches only**
  (n = 180, complete, 2026-02-13–2026-10-16). The 5 playoff matches
  are not predicted and not scored. Fit = all regular matches dated
  before the first 2026 match (seasons 2021–2025). Read ONCE, after
  dev freezes.
- Virgin climatology: pooled 2021–2025 regular outcome rates and
  OU2.5 over-rate.
- Calibration per arm: (i) mean predicted home-win probability minus
  actual home-win rate; (ii) mean predicted P(over 2.5) minus actual
  over-rate. Standard error of each difference:
  SE = sd(pred_i − y_i) / √n over the 180 matches, reported with the
  difference.

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev 1X2 LL and RPS of an arm must beat climatology, and OU2.5 LL must beat the base-rate baseline, else the arm is dead. Virgin legs — (i) LL leg: arm's virgin 1X2 LL ≤ Gate Zero's AND ≤ climatology's; (ii) calibration leg: |mean predicted − actual| ≤ 1.0pp pooled for home-win rate and for OU2.5 over-rate, SEs reported; a breach within 1 SE of the boundary is recorded PROVISIONAL PASS, beyond it FAIL; (iii) per-season sign check on dev (arm LL ≤ Gate Zero LL in at least half the dev seasons) for the both-pass rule. Both-pass rule: if Gate Zero and a variant both pass all legs, the lower pooled virgin 1X2 LL ships; if only one passes, it ships; if none passes, G-IEFD verdict is FAIL and nothing ships.

Reading of the legs, fixed here so the verdict is mechanical:

- An arm *passes* iff it survives the dev gate AND passes virgin
  legs (i)–(ii) (a PROVISIONAL PASS counts as a pass, recorded as
  such) AND, for variant arms only, leg (iii). Gate Zero is exempt
  from (iii) (it is the comparator).
- If several variant arms pass together with Gate Zero, the
  both-pass rule's "lower pooled virgin 1X2 LL ships" applies across
  all passing arms; ties go to the simpler arm (Gate Zero before X2).
- If Gate Zero fails its dev gate, the variant is moot, verdict FAIL,
  virgin NOT read.

## Outputs

- Engine: `league/IE-FirstDivision/engine/goals/` (this league's own
  code: fit/predict/harness modules + a CLI runner).
- Dev results: `league/IE-FirstDivision/engine/goals/results_dev.json`
  (+ CSV, force-added).
- Fitted parameters for the virgin fit:
  `league/IE-FirstDivision/engine/goals/fitted_params_virgin.json`.
- Virgin predictions: `league/IE-FirstDivision/predictions/g_iefd_virgin_predictions.csv`
  — the shipped arm's predictions (Gate Zero's if nothing ships,
  labelled in the verdict), one row per 2026 regular match, with FT
  lambdas, FT 1X2 / OU (1.5, 2.5, 3.5) / BTTS probabilities, and
  1H/2H lines derived by splitting the same lambdas with the frozen
  IE-FirstDivision goals constant 0.441 (1H λ = 0.441·FT λ,
  2H λ = 0.559·FT λ; 1H OU lines 0.5/1.5/2.5, 2H OU lines 1.5/2.5/3.5,
  same rho and score-matrix machinery). Halves are presentation only,
  never fitted (design §7b analogue).
- Verdict: `league/IE-FirstDivision/reports/G_IEFD_VERDICT.md`.

Production code and data are untouched. No push. No merge.
