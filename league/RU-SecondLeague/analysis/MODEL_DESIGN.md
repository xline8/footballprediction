# Step 6 — Model design: Russia Second League (FotMob 9123)

Design authority for the preregistrations. Features per
`analysis/FEATURES.md`; only G-RU2 reaches design — S/C/K/T are
not buildable (see §1).

## 1. Feasibility matrix

| candidate | target exists? | virgin window has target? | verdict |
|---|---|---|---|
| G-RU2 (goals) | yes — scores on 5,377 finished matches | yes — 888 finished non-awarded matches in 2026 + 2026/2027 | **BUILD** |
| S-RU2 (SOT) | no — `ShotsOnTarget` in 0/6,558 payloads | no | **NOT BUILDABLE** |
| C-RU2 (corners) | no — `corners` in 0/6,558 payloads | no | **NOT BUILDABLE** |
| K-RU2 (cards) | no — no stats yellows; events carry dismissals only (959 Red/YellowRed, 0 plain Yellows) and die after 2024 | no | **NOT BUILDABLE** |
| T-RU2 (total shots) | no — no stats, no shotmap in 0/6,558 payloads | no | **NOT BUILDABLE** |

The not-buildable verdicts are payload-level facts, not sample-size
judgements: the targets do not exist in the warehouse for this league
in any season. No virgin read follows for S/C/K/T.

## 2. G-RU2 — goals

### Reference pattern (Gate Zero)

Production Dixon-Coles from `model_v2.py` (class `DC`), copied as
`league/RU-SecondLeague/engine/goals/dc.py`, unmodified except the
goals-only observation (X1 fallback):

- Iterative multiplicative updates, 14 sweeps, damping 0.7, +0.25
  smoothing, home advantage fitted (init 0.28), attack/defence per
  team (init 0), score matrix MAXG = 10, production `tau`
  correction.
- Rho per fit from grid (0.0, −0.05, −0.10, −0.15) by weighted
  log-likelihood on goals only, as production.
- Observation: goals only (xG absent everywhere).
- Time decay w = 0.5 ** ((cutoff − match_date).days / 270) — frozen,
  no search.
- Fit scope: all eligible matches dated strictly before the test
  fold's first match date (expanding, date-cutoff — not label-cutoff,
  so the A/B calendar overlap cannot leak).
- Teams unseen in training start at the league mean (a = d = 0).

Sibling analogues: `league/RU-PremierLeague/prereg/PREREG_G_RU.md`
and `league/RU-1Division/prereg/PREREG_G_RU1.md` (the latter failed
its dev gate on RPS and OU2.5 legs — the same gate is applied here
without modification).

### Group / component rule (frozen)

The fit is **pooled over all groups, stages and both tracks**. Teams
are rated only against their own group/stage opponents; that is what
the data contains (2021/2022–2024: 4 disconnected components per
season label; A-track seasons: 1 component via stage re-sorting;
2026 B: 1 component via the Final Four). Cross-group levels rest on
the fit's zero-init anchor — the standard treatment for a pooled DC
on disconnected groups, and the only honest one (no cross-group
matches exist to estimate a group effect from). No group, stage or
track feature is used anywhere. Only 4 virgin matches (the 2026
Final Four) are cross-group predictions; they are scored like all
others and their count is reported in the verdict.

### Arms (pre-registered; see PREREG_G_RU2.md for the frozen gate text)

1. **Gate Zero** — the unmodified reference above.
2. **SHRINK** — the sanctioned G-J2-lesson arm, exactly as in
   G-RU1: at prediction time, for a team with fewer than 6 prior
   in-league matches in the training window, its fitted attack and
   defence ratings are shrunk toward the league mean
   (`a *= n/6`, `d *= n/6`, n = prior in-league match count; n = 0
   ⇒ a = d = 0, identical to Gate Zero). Nothing else changes.
   Motivation (X2): entrants are measurably off league mean in some
   seasons (e.g. Rotor +0.410 GF in its first season), and the
   season-opener failure mode (1–2-match teams with extreme lambdas)
   is the known G-J2 failure. Under date-cutoff fitting the arm may
   not bite — that is itself a recorded finding (as in G-RU1, where
   SHRINK was numerically identical to Gate Zero on all 918 dev
   rows). No hard-coded tier offset is used (X2 pooled gaps ≈ 0).

No other arms. No post-hoc arms if Gate Zero fails dev.

### Windows (frozen)

- **Training seed**: 2021/2022 (1,126 finished non-awarded matches).
- **Dev test folds** (season-blocked, expanding, date-cutoff):
  2022/2023 (n=1,115), 2023 (n=512), 2023/2024 (n=362), 2024
  (n=904), 2024/2025 (n=235), 2025/2026 (n=156). Pooled scored
  **n=3,284**. Partial A seasons (2024/2025, 2025/2026) are scored
  as they stand — their finished matches are real results; the
  missingness is a harvest gap, not result-dependent.
- **Virgin primary**: labels 2026 (B, n=760) + 2026/2027 (A
  to-date, n=128) = **888 finished non-awarded matches**, read ONCE,
  only for arms passing the dev gate. Fit = all eligible matches
  dated strictly before 2026-03-28 (first 2026 B match). The 95
  finished 2025/2026 A matches dated ≥2026-03-28 belong to the dev
  fold for that label, not to virgin training or virgin scoring.
  Virgin is **TRANSITIONAL**: 2026/2027 A is in progress (season ends
  Jun 2027) and 2026 B has 81 phantom rows; the season-end
  confirmatory read is reserved.
- **Excluded everywhere**: awarded matches (50) and season label
  2025 (42 finished rows, harvest fragment). Eligible = finished,
  non-awarded, season ≠ 2025.

### Primary line and metrics

Primary line **OU 2.5** (dev-period over-rate 0.50, closest to 0.5
among the ladder lines; ladder 1.5 / 2.5 / 3.5 reported). Metrics per
arm per season and pooled: mean 1X2 LL, mean RPS, mean OU2.5 LL.
Baselines: climatology — for target season S, pooled outcome rates +
OU2.5 over-rate of all eligible seasons strictly before S (date-
cutoff version: all eligible matches dated before S's first match).
Calibration: **actual − predicted** for home-win rate and OU2.5
over-rate, SE = sd(y_i − p_i)/√n. Gate legs verbatim in
PREREG_G_RU2.md (identical to G-RU1: dev gate = pooled 1X2 LL and
RPS beat climatology AND OU2.5 LL beats base rate; virgin legs =
LL leg, calibration leg |breach| ≤ 1pp clean PASS / ≤ 1 SE
PROVISIONAL, per-season sign check for variants; both-pass rule =
lower pooled virgin 1X2 LL ships; ties to Gate Zero; Gate Zero
fails dev ⇒ variants moot, virgin NOT read).

### Halves presentation (on PASS only)

FT + 1H/2H via the frozen goals constant **0.4393** (EDA §4),
presentation only. No other market has a halves constant.

## 3. Outputs

Engine `league/RU-SecondLeague/engine/goals/` (dc.py, arms.py,
harness.py, run_g_ru2.py, README.md); dev results
`results_dev.json` (+ CSV); virgin `results_virgin.json`; fitted
params `fitted_params_virgin.json`; on PASS, virgin predictions
`league/RU-SecondLeague/predictions/g_ru2_virgin_predictions.csv`
(shipped arm). Verdict: `league/RU-SecondLeague/reports/G_RU2_VERDICT.md`.
Not-buildable verdict: `league/RU-SecondLeague/reports/S_C_K_T_RU2_NOT_BUILDABLE.md`.
Production code untouched. No push. No merge.
