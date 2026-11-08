# Pre-registration — G-RU2 (Russia Second League goals model)

Frozen: 2026-11-10, before any fitting. Branch `build/ru-second-league`.
Design authority: `league/RU-SecondLeague/analysis/MODEL_DESIGN.md`
(G-RU2); features per `analysis/FEATURES.md` (X1 ADOPTED as goals-only
— no xG exists in this league at all, so the observation is goals-only;
X2 measured against the 1. Division (338) / Premier League (63) corpora,
SHRINK is the thin-data arm, no hard-coded tier offset). Reference:
production Dixon-Coles in `model_v2.py` (class `DC`), hl = 270; sibling
analogues: `league/RU-PremierLeague/prereg/PREREG_G_RU.md`,
`league/RU-1Division/prereg/PREREG_G_RU1.md` (which failed its dev gate
on the RPS and OU2.5 legs — the same gate is applied here unmodified).
Format rule (frozen, MODEL_DESIGN): FotMob 9123 is a parent id over 44
sub-tournaments in two parallel tracks (Division A autumn–spring,
Gold/Silver, first/second stage; Division B calendar year, 4 groups)
plus the pre-2023 FNL 2 / Second League groups. The fit is pooled over
all groups, stages and both tracks; no group, stage or track feature
anywhere. Cross-group levels rest on the fit's zero-init anchor; only
the 4 virgin Final Four matches are cross-group predictions.
Eligibility rule (frozen): eligible = finished AND not awarded AND
season label ≠ 2025 (50 awarded matches and the 42 finished rows of
the 2025 harvest fragment are excluded from every fit and score).
Calibration is defined as **actual − predicted** everywhere in this
build.

## Reference architecture (all arms share unless an arm says otherwise)

- Dixon-Coles fit, copied pattern from production `model_v2.py`:
  iterative multiplicative updates, 14 sweeps, damping 0.7, +0.25
  smoothing, home advantage fitted (init 0.28), attack/defence per
  team (init 0), score matrix MAXG = 10, production `tau` correction.
- Rho per fit from grid (0.0, −0.05, −0.10, −0.15) by weighted
  log-likelihood on goals only, as production.
- Observation: goals only. (Divergence from PREREG_G_RU, justified
  in FEATURES: the X1 blend pair cannot exist here — expected_goals
  is absent from every one of the 6,558 payloads.)
- Time decay w = 0.5 ** ((cutoff − match_date).days / 270) — frozen,
  no search.
- Fit scope for target fold F: all eligible matches dated strictly
  before the first match date of F (expanding, date-cutoff).
- Teams unseen in training start at the league mean (a = d = 0).

## Arms

1. **Gate Zero** — the unmodified reference above.
2. **Arm SHRINK** (sanctioned G-J2-lesson arm) — Gate Zero plus
   exactly one change at prediction time: for a team with fewer
   than 6 prior in-league matches in the training window, its
   fitted attack and defence ratings are shrunk toward the league
   mean: `a *= n/6`, `d *= n/6` where n = its prior in-league match
   count (n = 0 ⇒ a = d = 0, identical to Gate Zero's unseen rule;
   the arm bites exactly for teams with 1–5 prior matches — the
   season-opener failure mode; under date-cutoff fitting that band
   may not occur, which is itself a recorded finding if so).
   Nothing else changes. X2 evidence motivating it: 9 relegated
   entrants from 1. Division (338), 0 from the Premier League (63);
   pooled first-season gaps GF −0.079 / GA −0.021 (heterogeneous:
   Rotor +0.410 GF, Alania +0.726 GA) — no hard-coded tier offset
   is used.

## Dev protocol

- Training seed = 2021/2022 (n = 1,126 eligible); evaluation folds
  2022/2023 (n = 1,115), 2023 (n = 512), 2023/2024 (n = 362),
  2024 (n = 904), 2024/2025 (n = 235), 2025/2026 (n = 156);
  pooled scored **n = 3,284** under the date-cutoff walk-forward.
- Metrics per arm per fold and pooled: mean 1X2 LL, mean RPS
  (H, D, A), mean OU2.5 LL. Baselines: climatology — for target
  fold F, pooled outcome rates + OU2.5 over-rate of all eligible
  matches dated strictly before F's first match date.
- Primary line OU 2.5 (ladder 1.5 / 2.5 / 3.5 reported).
- The dev harness must not read virgin labels 2026 or 2026/2027
  at all. It must not read season label 2025 at all.

## Virgin protocol

- Virgin = labels 2026 (B, n = 760) + 2026/2027 (A to-date,
  n = 128) = **888 eligible matches**, read ONCE, only for arms
  passing the dev gate, after dev results are frozen.
  Fit = all eligible matches dated strictly before 2026-03-28
  (first 2026 B match date). Climatology = pooled rates of the
  same training set. Calibration: actual − mean predicted for
  home-win rate and OU2.5 over-rate, SE = sd(y_i − p_i)/√n.
- Virgin is **TRANSITIONAL**: 2026/2027 A is in progress (season
  ends Jun 2027) and 2026 B carries 81 phantom rows. The season-end
  confirmatory read is reserved and is not part of this build.
- The 95 finished 2025/2026 A matches dated ≥ 2026-03-28 belong to
  the dev fold for that label; they are in neither virgin training
  nor virgin scoring.

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev 1X2 LL and RPS must beat climatology, and
OU2.5 LL must beat the base-rate baseline, else the arm is dead.
Virgin legs — (i) LL leg: arm's virgin 1X2 LL ≤ Gate Zero's AND ≤
climatology's; (ii) calibration leg: |actual − mean predicted| ≤
1.0pp pooled for home-win rate and for OU2.5 over-rate, SEs
reported; a breach within 1 SE of the boundary is recorded
PROVISIONAL PASS, beyond it FAIL; (iii) per-season sign check on dev
(arm LL ≤ Gate Zero LL in at least half the dev folds) for the
both-pass rule. Both-pass rule: if Gate Zero and a variant both pass
all legs, the lower pooled virgin 1X2 LL ships; if only one passes,
it ships; if none passes, G-RU2 verdict is FAIL and nothing ships.

Mechanical reading: an arm passes iff it survives the dev gate AND
passes virgin legs (i)–(ii) (PROVISIONAL counts, recorded as such)
AND, for variant arms, leg (iii); Gate Zero is exempt from (iii).
Ties go to the simpler arm (Gate Zero before SHRINK). If Gate Zero
fails its own dev gate, variants are moot, verdict FAIL, virgin
NOT read.

## Outputs

Engine `league/RU-SecondLeague/engine/goals/`; dev results
`results_dev.json` (+ CSV); virgin `results_virgin.json`; fitted
params `fitted_params_virgin.json`; on PASS, virgin predictions
`league/RU-SecondLeague/predictions/g_ru2_virgin_predictions.csv`
(shipped arm; 1H/2H presentation via frozen goals constant 0.4393).
Verdict: `league/RU-SecondLeague/reports/G_RU2_VERDICT.md`.
Production code untouched. No push. No merge.
