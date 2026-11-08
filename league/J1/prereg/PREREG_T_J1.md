# Pre-registration — T-J1 (J1 total shots model)

**Provenance, stated plainly.** This candidate's design family
(total shots) is under a frozen prospective trial on the top-5:
the v2 design (`experiments/shots_model_v2/PREREG_PROSPECTIVE.md`)
and the E9 challenger (`experiments/shots_model_v2/
PREREG_V3_PROSPECTIVE_V2.md`, commit 0251116) are frozen there,
with the verdict due at n ≥ 1,200 scored top-5 matches or the end
of the 2026/27 season, whichever comes first. That verdict has
NOT been reached. The user explicitly ordered T-J1 built NOW,
ahead of that verdict (2026-11-09 14:17, reaffirmed in the 14:38
build mandate; `league/J1/analysis/MODEL_DESIGN.md` §6 as
amended), on the J.League corpus only. The top-5 prospective
trial is not touched by this build, and nothing produced here
feeds it: different corpus, different virgin window, no shared
fitting. Neither result contaminates the other.

Frozen: 2026-11-09, before any fitting. Branch `build/t-j1`.
Design authority: `league/J1/analysis/MODEL_DESIGN.md` §6 +
shared validation frame + §7b; levels per `league/J1/analysis/
EDA.md` (J1 total shots mean ≈ 24.8, dispersion 1.32–1.35).
Family record read before writing this document:
`experiments/shots_model/PREREG.md` + `RESULTS.md` (v1),
`experiments/shots_model_v2/PREREG.md` + `RESULTS.md` (v2),
`experiments/shots_model_v2/PREREG_V3_PROSPECTIVE_V2.md` (E9
freeze; the E9 dispersion formula below is taken from that
document verbatim in structure). `WINNER_SPEC_R2.md` was not
present in the loop worktree at build time; the freeze document
above carries the full E9 dispersion specification and governs.

## Target and data

- Target: total shots per match = `total_shots_home +
  total_shots_away` (stats feed) from
  `league/J1/data/j1_matches.csv`. Team identity = team id.
- Scope: every J1 row with both total-shots fields present,
  sorted by date (match_id as tiebreak). Coverage measured
  pre-freeze (design-level aggregates only): 2021 n=380,
  2022 n=306, 2023 n=306, 2024 n=380, 2025 n=380, 2026 n=200.
- One chronological walk-forward pass; every state (regression,
  naive tracker, base-rate tracker, level layer, trailing-r
  window) updates only AFTER the match is predicted.

## Frozen line and ladder

Dev distribution (seasons 2022–2025, n = 1,372, measured
pre-freeze from the data file): mean 24.898, median 24.0.
Over-rates: 23.5 → 56.27%, 24.5 → 48.69%, 25.5 → 41.84%.

- **Primary line: 24.5** — the ladder line whose dev over-rate
  is closest to 50% (the line nearest the dev median).
- Ladder (reported, all arms and baselines): 23.5 / 24.5 / 25.5.
- All gate legs are judged at the primary line 24.5 only.

## Shared machinery (all arms unless an arm says otherwise)

Seeded from `experiments/shots_model/run_shots_experiment.py`
(the v1 pattern), adapted to a single league (the "division" is
J1 as a whole):

- Regression core: jointly fitted log-linear Poisson ratings on
  team shots for/against — log(mu_home) = beta_home + A[home] +
  D[away], log(mu_away) = beta_away + A[away] + D[home] — ridge
  penalty (lam/2)·Σ(A² + D²), sample weights
  0.5 ** ((refit_day − match_day) / 365), lazy refits every 7
  days of match dates on matches strictly before the refit day,
  warm-started Newton/Fisher IRLS, eta clipped to [−6, 4] —
  exactly the v1 `ShotsRegressionStore` mechanics with one
  division.
- Naive trailing-10 member: each team's plain mean shots
  for/against over its last 10 matches, combined
  (for + opponent-against)/2 per side, league-mean fallback
  (the house `NaiveTracker` definition).
- NB line probabilities: P(over L) from a negative binomial
  with mean = predicted total and size r (arm-specific r
  below); the 50/50 ensemble averages the two members'
  probabilities (regression member and naive member, each
  through the same NB).

## Tuning (frozen procedure; tuning season never judged)

Mirrors v1: v1 tuned on 2022/23 and judged on later seasons.
Here the tuning season is **2022** (the first dev season); it is
reported for transparency but is NOT part of the dev gate pool.

- Ridge lambda: grid {3, 10, 30, 100, 300} (the v1 grid),
  chosen by line-24.5 log loss of regression+Poisson on season
  2022 only; ties toward larger lambda.
- NB size r_A (arm A's r): method of moments from the tuned
  regression's walk-forward residuals over seasons 2021–2022:
  r = Σλ² / (Σ(t − λ)² − Σλ), clipped to [1, 1e6] (the v1
  formula and clip).
- Arm B's level-layer cell: selected on season 2022 only
  (grid and rule under Arm B below).
- No other quantity is tuned anywhere. Nothing may be added
  after dev results are seen: three arms, frozen below, no
  fourth arm, no post-hoc variant.

## Arms (THREE, frozen)

**Arm A — v1 pattern.** Regression core at the tuned lambda +
NB total with size r_A, ensembled 50/50 (probability average)
with the naive trailing-10 member (both members' totals through
the same NB with r_A). This is v1's chosen candidate (b),
single-league. Arm A is the reference arm (the Gate Zero
analogue for this candidate).

**Arm B — v2 pattern.** Arm A plus the per-unit level layer of
`experiments/shots_model_v2/PREREG.md`, single-league adapted:
the "division" is the whole league; nothing else about the
mechanics changes.

- Two exponentially decayed sums over matches ALREADY PLAYED:
  A_s = decayed sum of actual total shots, P_s = decayed sum of
  arm A's ensemble total (0.5·(lt_reg + lt_naive)) as predicted
  BEFORE the match. Decay in days, half-life HL_L. The tracked
  prediction is the UNADJUSTED arm-A total; state updates only
  after a match is predicted, carries across season boundaries,
  starts empty.
- Shrunk ratio: R = (A_s + K_L·M̄) / (P_s + K_L·M̄), with
  M̄ = 24.9 frozen (≈ the J1 dev mean 24.898, a design-level
  aggregate known pre-freeze; v2 used its global mean 25.0 the
  same way).
- Factor: f = clip(1 + s·(R − 1), 0.90, 1.10) (v2's clip). Both
  ensemble member totals are multiplied by f before their NB
  probabilities are computed; the 50/50 probability ensemble is
  unchanged.
- Grid (the ONLY tuned quantities in arm B): HL_L ∈ {30, 60,
  120} days × s ∈ {0.5, 1.0} × K_L ∈ {20, 50} = 12 cells.
  Selection metric: line-24.5 log loss of the layered candidate
  on the tuning season 2022 ONLY. Ties break toward larger
  HL_L, then smaller s, then larger K_L (the v2 rule).

**Arm C — E9 mechanism.** Arm A with the NB size r re-estimated
from a trailing window of matches, the single-league analogue
of E9's per-division trailing-200 r
(`PREREG_V3_PROSPECTIVE_V2.md`, "Dispersion (NB r)"):

- Window: the last **k = 200** league match totals v from
  matches with date strictly before the predicted match's date
  (strictly-prior release; no same-day totals).
- M = (Σv + 200·24.9) / (n + 200);
  S2 = (Σv² + 200·(24.9 + 24.9²/r_A + 24.9²)) / (n + 200);
  V = max(0, S2 − M²);
  r = clip(M² / max(V − M, 1e-9), [20, 400]).
  (E9's formula with E9's prior mean 25.0 → J1's frozen 24.9 and
  E9's prior r 79.82 → this build's r_A; E9's window k = 200 and
  clip [20, 400] unchanged.) With n = 0, r = r_A within floating
  precision.
- Everything else is arm A exactly: same totals, same 50/50
  ensemble; only the NB size used for BOTH members' line
  probabilities is the trailing r above (per prediction).

## Baselines (house definitions, as in v1; no layer, no tuning)

- (a) League base rate: decayed (half-life 365 days) league
  mean home/away shot rates; expectation = mu_h + mu_a;
  Poisson probabilities.
- (b) Naive trailing-10: the shared naive tracker above,
  Poisson probabilities.

## Dev protocol

- Dev period: walk-forward expanding on the stats era, seasons
  2022–2025, with season 2021 as warm-up (predictions in 2021
  feed residuals and state; 2021 is not scored).
- Tuning season 2022 (see Tuning): scored and reported, NOT in
  the dev gate pool (v1 precedent: the tuning season never
  judges).
- **Dev gate pool: seasons 2023–2025** (n = 1,066). Metrics per
  arm and baseline, per season and pooled: log loss at every
  ladder line, calibration at 24.5 (mean predicted P(over) −
  actual over rate, pp), MAE of the predicted total.
- The dev harness must not read season "2026" or "2026/2027"
  rows at all. Virgin data is touched only by the separate
  virgin step, once, after dev results are frozen in the
  results file, and only for arms that pass the dev gate.

## Virgin protocol

- Virgin window: season "2026" (n = 200, complete), read ONCE,
  only for arms passing the dev gate (baselines are also scored
  on the virgin window — leg (i) requires them; v2 did the
  same). State carries continuously from the dev pass (fits use
  all matches before each predicted match, exactly as in dev).
- Reported per virgin-scored arm and baseline: log loss at
  every ladder line, calibration at 24.5 with its standard
  error SE = sd(p_i − y_i)/√n, MAE.

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev LL@primary beats BOTH baselines (league base rate; naive trailing-10), else arm dead, no virgin read. Virgin legs — (i) LL@primary ≤ best other passing arm's reference (arm A if it passes) and ≤ best baseline; (ii) calibration |mean P(over primary) − actual| ≤ 1.0pp, SE reported, breach within 1 SE = PROVISIONAL PASS; (iii) dev per-season sign check for the both-pass rule. Both-pass: among passing arms, lower pooled virgin LL ships; one → ships; none → FAIL.

Reading of the legs, fixed here so the verdict is mechanical:

- "Pooled dev" = the dev gate pool (seasons 2023–2025) at the
  primary line 24.5. "Beats" = strictly lower log loss.
- Leg (i) reference: R = arm A if arm A passes the dev gate;
  otherwise R = the dev-passing arm with the lowest pooled dev
  LL@24.5. An arm passes leg (i) iff its virgin LL@24.5 ≤ R's
  virgin LL@24.5 (the reference arm passes this clause
  trivially) AND its virgin LL@24.5 ≤ the best (lowest) virgin
  LL@24.5 of the two baselines.
- Leg (ii): |calibration| ≤ 1.0pp = PASS. If |calibration| >
  1.0pp but the breach beyond 1.0pp is within 1 SE (i.e.
  |calibration| − 1.0pp ≤ SE), the leg is a PROVISIONAL PASS
  and counts as a pass, recorded as such. Beyond that, FAIL.
- Leg (iii): for arms B and C, the arm's dev LL@24.5 ≤ arm A's
  dev LL@24.5 in at least half of the dev gate seasons (2023,
  2024, 2025 → at least 2 of 3). Arm A is exempt (it is the
  comparator).
- An arm *passes* iff it survives the dev gate AND passes
  virgin legs (i)–(ii) AND (for B and C) leg (iii).
- Both-pass rule: if two or more arms pass, the one with the
  lower pooled virgin LL@24.5 ships; a tie goes to the simpler
  arm (A before B before C). If exactly one passes, it ships.
  If none passes, T-J1 verdict is FAIL and nothing ships.

## Outputs

- Engine: `league/J1/engine/total_shots/` (this league's own
  code: model/harness modules + a CLI runner with `dev` and
  `virgin` steps; the virgin step refuses to run for an arm
  that did not pass the dev gate recorded in the dev results
  file).
- Dev results: `league/J1/engine/total_shots/results_dev.json`
  (+ CSV), including the frozen tuning outcomes (lambda, r_A,
  arm B's layer cell) and per-season/per-arm/per-baseline
  metrics.
- Fitted parameters: `league/J1/engine/total_shots/
  fitted_params.json` (lambda, r_A, layer cell, M̄, window k,
  primary line, frozen constants).
- Virgin predictions: `league/J1/predictions/
  t_j1_virgin_predictions.csv` — the shipped arm's predictions
  (arm A's if nothing ships but arm A was virgin-read, labelled
  in the verdict; no CSV if no arm passes the dev gate), one row
  per 2026 match: predicted FT total, FT ladder probabilities
  (23.5/24.5/25.5), and 1H/2H ladders derived by splitting the
  FT total with the frozen J1 total-shots constant 0.455
  (1H mean = 0.455·FT, 2H mean = 0.545·FT, same NB size r as the
  arm's FT probabilities for that match; 1H ladder
  10.5/11.5/12.5, 2H ladder 12.5/13.5/14.5). Halves are
  presentation only, never fitted (design §7b).
- Verdict: `league/J1/reports/T_J1_VERDICT.md`, including one
  context paragraph comparing (as readings, not verdicts) with
  the family's top-5 history (v1 calibration −1.34pp; v2 virgin
  −6.04pp).

Production code and data are untouched. The top-5 prospective
trial (v2 + E9) is untouched. No push. No merge.
