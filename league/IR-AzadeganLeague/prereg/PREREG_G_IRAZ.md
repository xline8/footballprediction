# Pre-registration — G-IRAZ (Azadegan League goals model)

Frozen: 2026-11-10, before any fitting. Branch `build/ir-azadegan-league`.
Design authority: `league/IR-AzadeganLeague/analysis/MODEL_DESIGN.md`;
features per `FEATURES.md` (X1–X9 all dropped — no xG, stats, shotmap,
lineup, or referee text in this corpus; X2 dropped on scope and on
evidence); evidence per `EDA.md` (F1/F2/F3/F4/F6/F7).
Reference implementation: production Dixon-Coles in `model_v2.py`,
as ported in `league/NL-Eredivisie/engine/goals/` (dc.py), with the
documented goals-only fallback (the blend's xG half never exists
here), plus the SHRINK arm form from `league/DE-3Liga/engine/goals/`.

## Reference architecture (all arms share unless an arm says otherwise)

- Dixon-Coles fit, pattern copied from
  `league/NL-Eredivisie/engine/goals/dc.py`: iterative multiplicative
  updates, 14 sweeps, damping 0.7, +0.25 smoothing, home advantage
  fitted (init 0.28), attack `a` and defence `d` per team (init 0),
  score matrix to MAXG = 10 with the production `tau` low-score
  correction.
- Rho: per fit from the grid (0.0, −0.05, −0.10, −0.15) by weighted
  log-likelihood on goals only, exactly as the reference.
- Observation: **goals only** (no xG key exists in this corpus).
- Time decay: w = 0.5 ** ((cutoff − match_date).days / 270), frozen.
- Fit scope for target season S: all matches with date strictly
  before the first match date of S (expanding, season-blocked: one
  fit per target season, whole season predicted from that fit).
- Teams unseen in training start at the league mean (a = d = 0).
  There is no mover prior in any arm (EDA F4: entrants perform at
  the league mean; X2 dropped in FEATURES.md).

## Arms

1. **Gate Zero** — the unmodified reference above.
2. **Arm SHRINK** — Gate Zero plus the frozen <6 prior-match rating
   shrink (DE-3Liga form): at prediction time each team's attack
   and defence ratings are multiplied by min(1, n_prior/6), where
   n_prior = that team's match count in the training window.
   Pre-recorded: under season-blocked fitting, prior in-league
   counts at a season start are 0 or ≥34 in this league (every club
   plays a full season or is absent; 2022/2023 had 17 teams, all
   playing 32 matches), so this arm is expected to be bit-identical
   to Gate Zero (as in G-NLE, G-ESPF, and G-NLTD); it is run anyway
   so the fact is measured, not assumed.

No other arms exist. In particular there is no X2 arm: the brief
forbids inventing a parent-tier prior, and the within-league
entrant gaps (GF +0.002 / GA −0.034 over the three dev transitions)
give no magnitude to freeze. A future X2 amendment (see
MODEL_DESIGN.md §5) would require a fresh prereg.

## Dev protocol

- Dev period: seasons 2021/2022–2024/2025. 2021/2022 is the initial
  training window; evaluation seasons are 2022/2023, 2023/2024,
  2024/2025 under the expanding season-blocked walk-forward
  (pooled dev n = 884).
- Metrics per arm per season and pooled: mean 1X2 log-loss, mean
  RPS (H, D, A), mean OU2.5 log-loss.
- Baselines: climatology — for target season S, the pooled outcome
  rates and OU2.5 over-rate of all seasons strictly before S.
- The dev harness must not read season "2025/2026" or "2026/2027"
  rows at all.

## Virgin protocol

- Virgin window: season "2025/2026" (n = 305 played, complete).
  Fit = all matches dated before the first 2025/2026 match. Read
  ONCE, after dev results are frozen, only for arms that pass the
  dev gate.
- Virgin climatology: pooled 2021/2022–2024/2025 outcome rates and
  OU2.5 over-rate.
- Calibration per arm, **actual − predicted**: (i) actual home-win
  rate minus mean predicted home-win probability; (ii) actual
  over-2.5 rate minus mean predicted P(over 2.5).
  SE = sd(y_i − p_i)/√n, reported with the difference.

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev 1X2 LL and RPS of an arm must beat climatology, and OU2.5 LL must beat the base-rate baseline, else the arm is dead. Virgin legs — (i) LL leg: arm's virgin 1X2 LL ≤ Gate Zero's AND ≤ climatology's; (ii) calibration leg: |actual − predicted| ≤ 1.0pp pooled for home-win rate and for OU2.5 over-rate, SEs reported; a breach within 1 SE of the boundary is recorded PROVISIONAL PASS, beyond it FAIL; (iii) per-season sign check on dev (arm LL ≤ Gate Zero LL in at least half the dev seasons) for the both-pass rule. Both-pass rule: if Gate Zero and a variant both pass all legs, the lower pooled virgin 1X2 LL ships; if only one passes, it ships; if none passes, G-IRAZ verdict is FAIL and nothing ships.

Reading of the legs, fixed here so the verdict is mechanical:

- An arm *passes* iff it survives the dev gate AND passes virgin
  legs (i)–(ii) (a PROVISIONAL PASS counts as a pass, recorded as
  such) AND, for variant arms only, leg (iii). Gate Zero is exempt
  from (iii).
- If several variant arms pass together with Gate Zero, the lower
  pooled virgin 1X2 LL ships; ties go to the simpler arm (Gate Zero
  before SHRINK).
- If no arm passes dev, the virgin is NOT read and the verdict
  records that.

## Outputs

- Engine: `league/IR-AzadeganLeague/engine/goals/` (fit/predict/
  harness modules + CLI runner, README).
- Dev results: `engine/goals/results_dev.json` (+ CSV).
- Virgin results: `engine/goals/results_virgin.json`.
- Fitted parameters (virgin fit, shipped arm):
  `engine/goals/fitted_params_virgin.json`.
- Virgin predictions (shipped arm only, on PASS):
  `league/IR-AzadeganLeague/predictions/g_iraz_virgin_predictions.csv`,
  one row per 2025/2026 match, with FT lambdas, FT 1X2 / OU
  (1.5, 2.5, 3.5) / BTTS probabilities, and 1H/2H lines derived by
  splitting the same lambdas with the frozen goals constant 0.415
  (presentation only, never fitted).
- Verdict: `league/IR-AzadeganLeague/reports/G_IRAZ_VERDICT.md`.

Production code and data are untouched. No push. No merge.
