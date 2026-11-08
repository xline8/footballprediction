# Pre-registration — C-J1 (J1 corners model)

Frozen: 2026-11-09, before any fitting. Branch `build/c-j1`.
Design authority: `league/J1/analysis/MODEL_DESIGN.md` §4 (candidate
C-J1) + shared validation frame + §7b; features per
`league/J1/analysis/FEATURES.md` (X5 corners naive, X7 opp-box
touches, X9 production territorial covariates); evidence per
`league/J1/analysis/EDA.md` (F2/F9/F13). Reference implementation:
production `model_corners_v3.py` (decay-weighted base rates +
rolling-5 shots relative factors + Negative Binomial total +
territorial multiplier `exp(beta·z)` clamped to [0.70, 1.43], betas
and gamma fitted on a fit window only, never on the test window).

## Data and coverage (measured on the built CSV before freezing)

Source: `league/J1/data/j1_matches.csv` (built by
`league/build_league_data.py` from the FotMob J.League warehouse).
Target: `y = corners_home + corners_away` (stats feed). J1 mean over
all seasons = 9.47; primary line 9.5.

Coverage (matches with both sides present / season n):

| Season | n | corners | possession + big_chance (X9) | touches_opp_box (X7) |
|---|---|---|---|---|
| 2021 | 380 | 380 | 380 | 230 |
| 2022 | 306 | 306 | 306 | 144 |
| 2023 | 306 | 306 | 306 | 128 |
| 2024 | 380 | 380 | 380 | 380 |
| 2025 | 380 | 380 | 380 | 380 |
| 2026 (virgin) | 200 | 200 | 200 | 200 |

The target and the X9 covariates are complete in every season. X7 is
complete only from 2024; in 2021–2023 it exists in blocks. The
FEATURES min-8 trailing rule (below) therefore makes the X7
multiplier inactive for many early matches — that is the documented
contract, not a defect, and the harness reports the active share per
season. Dev folds are frozen accordingly: training seed season 2021,
evaluation seasons **2022, 2023, 2024, 2025** (pooled n = 1,372).

## Shared engine (both arms identical unless an arm says otherwise)

Matches are processed in chronological order (date, then match_id).
For a match M, every state quantity uses only matches with date
strictly before M's date (same-date matches never see each other).

- **Base rates** (production `stats_window`, HL = 270 days frozen):
  with w_i = 0.5 ** ((date_M − date_i).days / 270) over prior matches,
  `bh` = decay-weighted mean home corners, `ba` = decay-weighted
  mean away corners, `L` = decay-weighted mean total shots per team
  per match. Production moment ratio for the base-rate baseline:
  `r_base = Σ w·y² / Σ w·y`.
- **Relative factors** (production `rel_factors`): per team, the
  last 5 prior matches (team perspective: shots for, shots against);
  factor = clamp(mean / L, 0.6, 1.7); a team with no prior match
  gets factor 1.0. `fhp, fhc` = home team's (for, against) factors;
  `fap, fac` = away team's.
- **Core mean**: `mu_cs = bh·(fhp·fac)^gamma + ba·(fap·fhc)^gamma`.
- **Distribution**: Negative Binomial pmf on k = 0..50, normalised
  (production `pmf_k`, GRID = 50), size `k_nb = mu / (r − 1)` for
  r > 1.02, else the Poisson limit (k_nb = 1e9). P(over L) =
  Σ_{k > L} pmf(k).
- **Walk-forward rows**: a match becomes a scored row once at least
  10 prior league matches exist (before that it only feeds state).
- **Per-season hyperparameter fitting.** For target season S,
  gamma_S, the arm's beta(s), and r_S are fitted ONLY on walk-forward
  rows from seasons strictly before S (for S = 2022: season 2021
  rows), then frozen for every match of S:
  1. gamma: grid (0.0, 0.15, 0.3, 0.45, 0.6, 0.8); for each gamma,
     r(gamma) = clamp(Σ(y − mu_cs)² / Σ mu_cs, 1.02, 5.0) over the
     training rows; gamma_S minimises mean full-count NB NLL
     (−log pmf(y)) over the training rows (production selects gamma
     by NLL); ties go to the smaller gamma. r_S = r(gamma_S).
  2. betas: grid search minimising mean binary LL@9.5 over the same
     training rows, with mu = mu_cs(gamma_S) · mult(beta) and NB
     size from r_S. Ties go to the beta combination with the
     smallest Σ|beta| (then the lexicographically smallest).
- **Territorial multiplier** (production structure): per team, over
  its last 10 matches strictly before M (window entries are prior
  matches regardless of stat presence; a match is *valid* for a
  covariate when that covariate is present for both teams in it):
  if fewer than 8 of the 10 are valid, the covariate is inactive
  for that team (FEATURES.md min-8 rule for X7 and X9). Where
  active, `z_team = mean over valid matches of (stat_for −
  stat_against)` (ratio-of-sums contract is equivalent here up to
  the per-match differencing production itself uses). The match
  multiplier is 1.0 unless the covariate is active for BOTH teams.

## Arms

1. **Gate Zero (X9)** — the production pattern carried unchanged:
   covariates = `BallPossesion` (percentage points) and `big_chance`
   (counts). `mult = clamp(exp(beta_poss·(z_poss_home − z_poss_away)
   + beta_bc·(z_bc_home − z_bc_away)), 0.70, 1.43)`. Beta grids:
   beta_poss ∈ {−0.010, −0.0075, −0.005, −0.0025, 0, 0.0025, 0.005,
   0.0075, 0.010}; beta_bc ∈ {−0.10, −0.075, −0.05, −0.025, 0,
   0.025, 0.05, 0.075, 0.10}; joint 9×9 grid.
2. **Arm X7** — identical engine; the territorial covariates are
   replaced by opp-box touches (feature X7, EDA F9):
   `mult = clamp(exp(beta_bt·(z_bt_home − z_bt_away)), 0.70, 1.43)`
   with z from `touches_opp_box` for/against. Beta grid: beta_bt ∈
   {−0.04, −0.03, −0.02, −0.01, 0, 0.01, 0.02, 0.03, 0.04}.

No other difference between arms. No half-share modelling anywhere
(F3); halves appear only in the predictions CSV via the frozen
constant (below).

## Baselines (scored on the same dev / virgin matches)

1. **League base rate**: one NB per target season S — mu = the
   decay-weighted mean total corners over matches dated before the
   first date of S (HL 270 to that date), r = `r_base` over the same
   window. Same P(over 9.5) for every match of S.
2. **Naive trailing-10** (feature X5): per match M,
   `mu_naive = (CF_home + CA_away)/2 + (CF_away + CA_home)/2`, where
   CF/CA are a team's mean corners for/against over its last 10
   matches strictly before M. A team with fewer than 6 prior matches
   contributes the league per-team mean (bh + ba)/2 (M's own
   decay-weighted base rates) for both CF and CA. NB size from the
   same per-season `r_base` as baseline 1.

## Dev protocol

- Dev harness loads ONLY seasons 2021–2025; it must not read
  season "2026" or "2026/2027" rows at all. Virgin data is touched
  only by the separate virgin step, once, after dev results are
  frozen in the results files, and only for arms that pass the
  dev gate.
- Metrics per arm / baseline, per season and pooled: n, mean binary
  LL at lines 8.5 / **9.5 (primary)** / 10.5 (natural log), mean
  P(over 9.5), actual over-9.5 rate. For Arm X7 additionally: the
  share of matches whose multiplier was active (both teams active
  and beta_bt ≠ 0 is reported separately from both-teams-active).

## Virgin protocol

- Virgin window: season "2026" (n = 200, complete). Treated exactly
  as another target season: gamma, betas and r fitted on
  walk-forward rows from seasons 2021–2025 only; base state and
  trailing windows chronological, strictly pre-match. Read ONCE,
  after dev freezes, and only for arms passing the dev gate.
- Virgin baselines: as defined above with S = "2026".
- Calibration per arm: mean P(over 9.5) − actual over-9.5 rate;
  SE = sd(pred_i − y_i) / √n over the 200 matches (y_i = 1 if the
  match went over 9.5), reported with the difference.

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev LL@9.5 beats BOTH baselines (league base rate; naive trailing-10 team means), else the arm is dead and does NOT read the virgin. Virgin legs — (i) LL@9.5 ≤ Gate Zero's and ≤ best baseline's; (ii) calibration |mean P(over 9.5) − actual over rate| ≤ 1.0pp, SE reported, breach within 1 SE = PROVISIONAL PASS, beyond = FAIL; (iii) dev per-season sign check (arm LL ≤ Gate Zero in ≥ half the dev seasons) for the both-pass rule. Both-pass: both pass → lower pooled virgin LL ships; one → ships; none → FAIL.

Reading of the legs, fixed here so the verdict is mechanical:

- An arm *passes* iff it survives the dev gate AND passes virgin
  legs (i)–(ii) (a PROVISIONAL PASS counts as a pass, recorded as
  such) AND, for the variant arm (X7) only, leg (iii). Gate Zero is
  exempt from (iii) (it is the comparator). Leg (i) for Gate Zero
  itself reads: its virgin LL@9.5 ≤ the best baseline's.
- If both arms pass, the lower pooled virgin LL@9.5 ships; a tie
  goes to Gate Zero (the simpler, production-proven arm). If only
  one passes, it ships. If none passes, C-J1 verdict is FAIL and
  nothing ships.

## Outputs

- Engine: `league/J1/engine/corners/` (this league's own code:
  core + harness modules + a CLI runner with `dev` and `virgin`
  subcommands; the virgin subcommand takes the arm(s) to evaluate
  explicitly).
- Dev results: `league/J1/engine/corners/results_dev.json` (+ CSV).
- Virgin results: `league/J1/engine/corners/results_virgin.json`;
  fitted parameters per evaluated arm:
  `league/J1/engine/corners/fitted_params_virgin.json`.
- Virgin predictions: `league/J1/predictions/c_j1_virgin_predictions.csv`
  — the shipped arm's predictions (Gate Zero's if nothing ships,
  labelled in the verdict), one row per 2026 match: match_id, date,
  home/away teams, actual corners home/away/total, arm, mu, r,
  gamma, beta(s), FT P(over) for lines 6.5/7.5/8.5/9.5/10.5/11.5,
  and 1H/2H ladders derived ONLY via the frozen J1 corners constant
  0.447 (presentation only, design §7b): mu_1h = 0.447·mu,
  mu_2h = 0.553·mu, same r (size from the half's own mu), 1H lines
  3.5/4.5/5.5, 2H lines 4.5/5.5/6.5.
- Verdict: `league/J1/reports/C_J1_VERDICT.md`.

Production code and data are untouched. No push. No merge.
