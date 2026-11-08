# Pre-registration — G-IRPG (Persian Gulf Pro League goals model)

Frozen: 2026-11-10, before any fitting. Branch `build/ir-persian-gulf`.
Design authority: `league/IR-PersianGulf/analysis/MODEL_DESIGN.md`;
features per `FEATURES.md` (X1, X3–X9 dropped — no xG, stats,
shotmap, or referee text in this corpus; X2 adopted in frozen-offset
form only); evidence per `EDA.md` (F1/F2/F3/F4/F6/F7).
Reference implementation: production Dixon-Coles in `model_v2.py`,
as ported in `league/NL-Eredivisie/engine/goals/` (dc.py), with the
documented goals-only fallback (the blend's xG half never exists
here), plus the SHRINK arm form from `league/DE-3Liga/engine/goals/`
and the X2 entrant-offset arm defined below.

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
- Teams unseen in training start at the league mean (a = d = 0) in
  Gate Zero and SHRINK. There is no mover prior in those arms.

## Arms

1. **Gate Zero** — the unmodified reference above.
2. **Arm SHRINK** — Gate Zero plus the frozen <6 prior-match rating
   shrink (DE-3Liga form): at prediction time each team's attack
   and defence ratings are multiplied by min(1, n_prior/6), where
   n_prior = that team's match count in the training window.
   Pre-recorded: under season-blocked fitting, prior in-league
   counts at a season start are 0 or ≥30 in this league (every club
   plays a full 30-match season or is absent), so this arm is
   expected to be bit-identical to Gate Zero (as in G-NLE, G-ESPF,
   G-NLTD, and G-IRAZ); it is run anyway so the fact is measured,
   not assumed.
3. **Arm X2** — Gate Zero plus the frozen entrant offset: at
   prediction time, a team with **zero** matches in the training
   window starts at attack rating a0 = **−0.18** and defence
   rating d0 = **+0.15** instead of (0, 0). Derivation, frozen
   here: pooled dev entrant gaps GF −0.160 / GA +0.157 goals per
   team-match (EDA F4, transitions into 2022/2023, 2023/2024,
   2024/2025; n = 6 teams, 180 team-matches) at pooled dev
   team-mean μ = 0.996; a0 = ln((μ − 0.160)/μ) = ln(0.839) =
   −0.175 → −0.18, d0 = ln((μ + 0.157)/μ) = ln(1.158) = +0.146 →
   +0.15. Teams with any training-window match are fitted normally
   and X2 never touches them. X2 uses **no Azadegan League data**:
   the rating-based variant (per-entrant Azadegan ratings) is
   rejected in FEATURES.md R15 — the sibling goals model failed
   its dev gate and shipped no fitted ratings, so no cross-league
   scaling is estimable. The virgin transition's gaps (−0.038 /
   +0.136) are descriptive only and did not enter these values.

No other arms exist. In particular there is no per-entrant
Azadegan-rating arm, no referee arm, and no halves-fitted arm.

## Dev protocol

- Dev period: seasons 2021/2022–2024/2025. 2021/2022 is the initial
  training window; evaluation seasons are 2022/2023, 2023/2024,
  2024/2025 under the expanding season-blocked walk-forward
  (pooled dev n = 720).
- Metrics per arm per season and pooled: mean 1X2 log-loss, mean
  RPS (H, D, A), mean OU2.5 log-loss.
- Baselines: climatology — for target season S, the pooled outcome
  rates and OU2.5 over-rate of all seasons strictly before S.
- The dev harness must not read season "2025/2026" or "2026/2027"
  rows at all.

## Virgin protocol

- Virgin window: season "2025/2026" league-only (n = 178 played,
  rounds 1–23 — PARTIAL, the warehouse holds no rounds 24–30).
  Fit = all matches dated before the first 2025/2026 match. Read
  ONCE, after dev results are frozen, only for arms that pass the
  dev gate. The partial-season caveat is carried into the verdict:
  the virgin tests rounds 1–23, not the full season.
- Virgin climatology: pooled 2021/2022–2024/2025 outcome rates and
  OU2.5 over-rate.
- Calibration per arm, **actual − predicted**: (i) actual home-win
  rate minus mean predicted home-win probability; (ii) actual
  over-2.5 rate minus mean predicted P(over 2.5).
  SE = sd(y_i − p_i)/√n, reported with the difference.

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev 1X2 LL and RPS of an arm must beat climatology, and OU2.5 LL must beat the base-rate baseline, else the arm is dead. Virgin legs — (i) LL leg: arm's virgin 1X2 LL ≤ Gate Zero's AND ≤ climatology's; (ii) calibration leg: |actual − predicted| ≤ 1.0pp pooled for home-win rate and for OU2.5 over-rate, SEs reported; a breach within 1 SE of the boundary is recorded PROVISIONAL PASS, beyond it FAIL; (iii) per-season sign check on dev (arm LL ≤ Gate Zero LL in at least half the dev seasons) for the both-pass rule. Both-pass rule: if Gate Zero and a variant both pass all legs, the lower pooled virgin 1X2 LL ships; if only one passes, it ships; if none passes, G-IRPG verdict is FAIL and nothing ships.

Reading of the legs, fixed here so the verdict is mechanical:

- An arm *passes* iff it survives the dev gate AND passes virgin
  legs (i)–(ii) (a PROVISIONAL PASS counts as a pass, recorded as
  such) AND, for variant arms only, leg (iii). Gate Zero is exempt
  from (iii).
- If several variant arms pass together with Gate Zero, the lower
  pooled virgin 1X2 LL ships; ties go to the simpler arm (Gate Zero
  before SHRINK before X2).
- If no arm passes dev, the virgin is NOT read and the verdict
  records that.

## Outputs

- Engine: `league/IR-PersianGulf/engine/goals/` (fit/predict/
  harness modules + CLI runner, README).
- Dev results: `engine/goals/results_dev.json` (+ CSV).
- Virgin results: `engine/goals/results_virgin.json`.
- Fitted parameters (virgin fit, shipped arm):
  `engine/goals/fitted_params_virgin.json`.
- Virgin predictions (shipped arm only, on PASS):
  `league/IR-PersianGulf/predictions/g_irpg_virgin_predictions.csv`,
  one row per 2025/2026 league match, with FT lambdas, FT 1X2 / OU
  (1.5, 2.5, 3.5) / BTTS probabilities, and 1H/2H lines derived by
  splitting the same lambdas with the frozen goals constant 0.427
  (presentation only, never fitted).
- Verdict: `league/IR-PersianGulf/reports/G_IRPG_VERDICT.md`.

Production code and data are untouched. No push. No merge.
