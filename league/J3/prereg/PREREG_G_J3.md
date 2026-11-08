# Pre-registration — G-J3 (J3 goals model)

Frozen: 2026-11-09, before any fitting for this candidate. Branch
`build/g-j3`. This file is committed before the engine is written or
run; any change after the first fit must be recorded as an amendment
below with its date and reason, never edited silently into the frozen
text.

Governing design: `league/J1/analysis/MODEL_DESIGN.md` §2 (G-J3) and
its shared validation frame; features `FEATURES.md` X1 (goals-only)
and X2; EDA findings F2, F4, F13 in `league/J1/analysis/EDA.md`.

## 1. Scope and hard rules

- J3 is scores-only (F13): no xG, no SOT/shots/corners/cards targets.
  The model is a goals-only Dixon-Coles model.
- **FULL-TIME ONLY.** No halves product, split, or constant of any
  kind for J3 (design §2d: HT missing 6.8% and F3). Any halves output
  is a defect.
- Production (top-5) is untouched. All work is local on `build/g-j3`;
  nothing is pushed.
- Data: `league/J3/data/j3_matches.csv` (1,819 matches) regenerated
  by `league/build_league_data.py`, plus `league/J2/data/j2_matches.csv`
  used only to identify and rate movers in Arm X2.
- Team identity is the FotMob team id, never the name string.

## 2. Validation frame (frozen)

- Dev: walk-forward expanding, season-blocked, seasons 2021–2024.
  Season 2021 is the training origin (no prior corpus exists, so it
  cannot be an evaluated season). Evaluated dev seasons are 2022,
  2023, 2024: for target season S, one fit on all J3 matches with
  season < S, cutoff = the first kickoff date of season S, predictions
  for every match of season S.
- Virgin: season "2025" (n=383), read ONCE, after dev results are
  frozen. One fit on all J3 matches with season in 2021–2024, cutoff
  = first kickoff date of season 2025. No parameter, arm choice
  criterion, or gate may be tuned on the virgin window. Seasons
  2026/2027 are never read by this candidate's code.
- A fit for a match uses only matches strictly before that fit's
  cutoff (signed-age rule).

## 3. Reference architecture (both arms)

Seeded from production `model_v2.py` (`class DC`), goals-only mode:

- Ratings: log attack `a[t]`, log defence `d[t]` (higher `d` = concedes
  more), home advantage `h` (init 0.28), all other inits 0.
- Fit: 14 multiplicative sweeps, step 0.7, +0.25 smoothing, exactly as
  production; exponential time decay with half-life **270 days**
  (production `v2_config.json` `hl`), weight
  `0.5 ** ((cutoff - date).days / 270)`.
- Dixon-Coles rho chosen on the goals fit over the production grid
  `(0.0, -0.05, -0.10, -0.15)`.
- Score matrix 0..10 × 0..10, tau-corrected, normalised; outputs
  p_home, p_draw, p_away, p_over25 (full-time only).

## 4. Arms

### Gate Zero
Unmodified DC goals-only as in §3. Teams absent from the training
window (movers and new entrants alike) start at the league mean
(`a = d = 0`).

### Arm X2 — cross-tier priors (feature X2)
Identical to Gate Zero except for the *initial* ratings of one mover
class, set before the §3 sweeps:

- **Relegated from J2**: a club whose previous-season (S−1) membership
  was J2 (it appears in `j2_matches.csv` season S−1) and which plays
  in J3 in season S. Its prior is translated from its own season S−1
  J2 scoring rates (per match, ratio of sums; requires ≥10 J2 matches
  that season, else league mean):
  - `GF_J3 = GF_J2 + 0.496` and `GA_J3 = GA_J2 − 0.353`, the measured
    relegated-side deltas of `cross_tier["j3->j2"]` in
    `league/J1/analysis/eda_summary.json` (GF 0.861 → 1.357;
    GA 1.603 → 1.250; EDA F4). Floors: GF_J3, GA_J3 ≥ 0.30.
  - Initial ratings: `a_init = log(GF_J3 / M)`,
    `d_init = log(GA_J3 / M)`, where `M` is the training window's mean
    goals per team-match. A relegated club with no J3 training matches
    keeps this prior unchanged through the fit (no observations update
    it); a club that also has older J3 history is initialised here and
    then updated by its J3 observations like any other team.
- **Entrants with no J.League history** (e.g. promoted from JFL):
  league mean (`a = d = 0`), identical to Gate Zero. No J2 step can be
  computed for them and none is invented.
- Clubs promoted out of J3, and all non-movers: no treatment.
- Leakage guard (FEATURES X2): the prior for season S uses only
  season S−1 membership and S−1 J2 matches; a club's own season-S
  matches never inform its own entry prior.

## 5. Baselines

- **Climatology** (1X2): the home/draw/away frequencies of the same
  training window used for that target season's fit, applied to every
  match of the target season.
- **Base rate** (OU2.5): the over-2.5 rate of the same training
  window, applied to every match of the target season.
Baselines are computed from training data only, never from the target
season.

## 6. Metrics

- 1X2 log loss: mean `−log p(actual outcome)`.
- RPS (ordered home, draw, away):
  `0.5 * Σ_{k=1..2} (cum_pred_k − cum_actual_k)²`, averaged.
- OU2.5 log loss: mean binary log loss on `p_over25`.
- Calibration: mean predicted vs actual rate, pooled.
- Standard error of a calibration difference: match-level
  `SE = sd(p_i − y_i) / sqrt(n)`, reported alongside each difference.

## 7. Gate legs (verbatim, frozen)

Dev gate — pooled dev 1X2 LL and RPS beat climatology and OU2.5 LL beats base rate, else arm dead.

Virgin legs — (i) LL leg: virgin 1X2 LL ≤ Gate Zero's AND ≤ climatology's; (ii) calibration leg: |mean predicted − actual| ≤ 1.0pp pooled for home-win rate and OU2.5 over-rate, SEs reported; breach within 1 SE = PROVISIONAL PASS, beyond = FAIL; (iii) per-season sign check on dev for the both-pass rule.

Both-pass: both pass → lower pooled virgin LL ships; one passes → ships; none → FAIL, nothing ships.

Operational readings (also frozen):

- The dev gate is applied per arm, pooled over evaluated dev seasons
  2022–2024. An arm that fails it is dead: it cannot ship, whatever
  the virgin readout says.
- The LL leg's "≤ Gate Zero's" clause compares each arm to Gate Zero;
  for Gate Zero itself that clause is equality and the binding
  comparison is against climatology.
- The calibration leg must hold for *both* quantities (home-win and
  OU2.5). PROVISIONAL PASS counts as a pass for shipping, and is
  reported as provisional in the verdict.
- Per-season sign check: for an arm to take part in the both-pass
  comparison, its dev 1X2 LL must beat climatology in at least 2 of
  the 3 evaluated dev seasons (the sign of the improvement must not
  be carried by a single season). The per-season signs are reported
  either way.
- "Both pass" = both arms pass the dev gate and both virgin legs
  (subject to the sign check). If both pass, the arm with the lower
  pooled virgin 1X2 LL ships. If exactly one passes, it ships. If
  none pass, the verdict is FAIL and nothing ships.

## 8. Outputs (frozen)

- Engine: `league/J3/engine/goals/` (J3's own engine).
- Dev results + fitted parameters: JSON under
  `league/J3/engine/goals/results/`.
- Virgin predictions: `league/J3/predictions/g_j3_virgin_predictions.csv`,
  one row per 2025 match, full-time probabilities only, for the
  shipped arm; if no arm ships, the file still records both arms'
  virgin predictions and the verdict states that nothing shipped.
- Verdict: `league/J3/reports/G_J3_VERDICT.md` with the dev table per
  arm per season, the virgin table, per-leg PASS/FAIL per arm, the
  shipped arm and why.

## Amendments

(none at freeze)
