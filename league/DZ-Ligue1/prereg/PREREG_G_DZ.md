# Pre-registration — G-DZ (Algeria Ligue 1 goals model)

Frozen: 2026-11-10, before any fitting. Branch `build/dz-ligue1`
(worktree `~/workspace/wt-dz-ligue1`; NOTE — 2026-11-10 15:42 WIB
the coordinator froze all git work repo-wide after a cleanup
command damaged git history, so this prereg is filed on disk
uncommitted; the coordinator will rebuild history and commit the
branch afterwards. Commit order is preserved in substance: this
file was written BEFORE any engine fitting began.)
Design authority: `league/DZ-Ligue1/analysis/MODEL_DESIGN.md`
(G-DZ); features per `analysis/FEATURES.md` (X1 ADOPTED as goals-only
— no xG exists in this league at all, so the observation is goals-only;
X2 DROPPED — no other Algerian league exists in the warehouse, so no
cross-league mover prior is available; SHRINK is the thin-data arm,
no hard-coded tier offset). Reference: production Dixon-Coles in
`model_v2.py` (class `DC`), hl = 270; sibling analogues:
`league/GH-PremierLeague/prereg/PREREG_G_GH.md` (same scores-only
shape; failed its dev gate on 1X2 LL, RPS and OU2.5 LL),
`league/NG-ProfessionalLeague/prereg/PREREG_G_NG.md` (same scores-only
shape; failed its dev gate on 1X2 LL, RPS and OU2.5 LL),
`league/RU-SecondLeague/prereg/PREREG_G_RU2.md` (same scores-only
shape; failed its dev gate on 1X2 LL and OU2.5 LL) and
`league/SV-PrimeraDivision/prereg/PREREG_G_SV.md` (same scores-only
shape; failed its dev gate on the OU2.5 leg only).
Format rule (frozen, MODEL_DESIGN): single round-robin league; every
match is regular phase. Eligible = `eligible` column in
`data/dz_matches.csv` (n = 1,331; the one awarded match 4366461 is
excluded). Teams are keyed by FotMob team id.
Calibration is defined as **actual − predicted** everywhere in this
build.

## Reference architecture (all arms share unless an arm says otherwise)

- Dixon-Coles fit, copied pattern from production `model_v2.py`:
  iterative multiplicative updates, 14 sweeps, damping 0.7, +0.25
  smoothing, home advantage fitted (init 0.28), attack/defence per
  team (init 0), score matrix MAXG = 10, production `tau` correction.
- Rho per fit from grid (0.0, −0.05, −0.10, −0.15) by weighted
  log-likelihood on goals only, as production.
- Observation: goals only. (Divergence from PREREG_G_J1, justified
  in FEATURES: the X1 blend pair cannot exist here — expected_goals
  is absent from every one of the 1,332 payloads.)
- Time decay w = 0.5 ** ((cutoff − match_date).days / 270) — frozen,
  no search.
- Fit scope for target season S: all eligible matches dated strictly
  before the first match date of S (expanding, season-blocked: one
  fit per target season, whole season predicted from that fit).
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
   Nothing else changes. Motivation: 2 promoted clubs enter every
   season (EDA §5) and no cross-league mover prior exists
   (FEATURES X2) — no hard-coded tier offset is used.

## Dev protocol

- Training seed = 2021/2022 (n = 306 eligible); evaluation seasons
  2022/2023 (n = 240), 2023/2024 (n = 239), 2024/2025 (n = 240);
  pooled scored **n = 719** under the season-blocked expanding
  walk-forward.
- Metrics per arm per season and pooled: mean 1X2 LL, mean RPS
  (H, D, A), mean OU2.5 LL. Baselines: climatology — for target
  season S, pooled outcome rates + OU2.5 over-rate of all eligible
  matches dated strictly before S's first match date; plus the naive
  trailing-10 baseline reported alongside.
- Primary line OU 2.5 (ladder 1.5 / 2.5 / 3.5 reported).
- The dev harness must not read season "2025/2026" or "2026/2027"
  rows at all. Virgin data is touched only by the separate virgin
  step, once, after dev results are frozen in the results file.

## Virgin protocol

- Virgin window: season "2025/2026" (**n = 240, complete**). Fit =
  all eligible matches dated before the first 2025/2026 match
  (seasons 2021/2022 through 2024/2025). Read ONCE, after dev freezes.
- Virgin climatology: pooled 2021/2022 through 2024/2025 outcome
  rates and OU2.5 over-rate.
- Calibration per arm: (i) mean predicted home-win probability minus
  actual home-win rate; (ii) mean predicted P(over 2.5) minus actual
  over-rate. Standard error of each difference:
  SE = sd(pred_i − y_i) / √n over the 240 matches, reported with the
  difference. (Sign convention: actual − predicted, as frozen above.)
- Confirmatory window "2026/2027" (in progress, 66 matches to
  2026-11-08) is **reserved**; evaluated once when the season
  completes, not part of this build.

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev 1X2 LL and RPS must beat climatology, and
OU2.5 LL must beat the base-rate baseline, else the arm is dead.
Virgin legs — (i) LL leg: arm's virgin 1X2 LL ≤ Gate Zero's AND ≤
climatology's; (ii) calibration leg: |actual − mean predicted| ≤
1.0pp pooled for home-win rate and for OU2.5 over-rate, SEs
reported; a breach within 1 SE of the boundary is recorded
PROVISIONAL PASS, beyond it FAIL; (iii) per-season sign check on dev
(arm LL ≤ Gate Zero LL in at least half the dev seasons — i.e. 2 of
3) for the both-pass rule. Both-pass rule: if Gate Zero and a variant
both pass all legs, the lower pooled virgin 1X2 LL ships; if only one
passes, it ships; if none passes, G-DZ verdict is FAIL and nothing
ships.

Mechanical reading: an arm passes iff it survives the dev gate AND
passes virgin legs (i)–(ii) (PROVISIONAL counts, recorded as such)
AND, for variant arms, leg (iii); Gate Zero is exempt from (iii).
Ties go to the simpler arm (Gate Zero before SHRINK). If Gate Zero
fails its own dev gate, variants are moot, verdict FAIL, virgin
NOT read.

## Outputs

Engine `league/DZ-Ligue1/engine/goals/`; dev results
`results_dev.json` (+ CSV); virgin `results_virgin.json`; fitted
params `fitted_params_virgin.json`; on PASS, virgin predictions
`league/DZ-Ligue1/predictions/g_dz_virgin_predictions.csv`
(shipped arm; 1H/2H presentation via frozen goals constant 0.4421).
Verdict: `league/DZ-Ligue1/reports/G_DZ_VERDICT.md`.
Production code untouched. No push. No merge.
