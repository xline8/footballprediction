# Pre-registration — G-NG (Nigeria Professional Football League goals model)

Frozen: 2026-11-10, before any fitting. Branch `build/ng-professional-league`.
Design authority: `league/NG-ProfessionalLeague/analysis/MODEL_DESIGN.md`
(G-NG); features per `analysis/FEATURES.md` (X1 ADOPTED as goals-only
— no xG exists in this league at all, so the observation is goals-only;
X2 DROPPED — no built Nigerian sibling exists, so no cross-league mover
prior is available; SHRINK is the thin-data arm, no hard-coded tier
offset). Reference: production Dixon-Coles in `model_v2.py` (class
`DC`), hl = 270; sibling analogues:
`league/RU-SecondLeague/prereg/PREREG_G_RU2.md` (same scores-only
shape; failed its dev gate on 1X2 LL and OU2.5 LL) and
`league/RU-1Division/prereg/PREREG_G_RU1.md` (which failed its dev
gate on the RPS and OU2.5 legs — the same gate is applied here
unmodified).
Format rule (frozen, MODEL_DESIGN): FotMob 533 is a parent id. The fit
is pooled over the single table and the 2023 two-group stage; no group,
stage or sub-tournament feature anywhere. The 15 Championship Group
matches (2023, neutral venue — home-win rate 20.0%, home goals 0.93 <
away 1.13) are EXCLUDED from every fit and score, as are the 1 awarded
match and the 1 phantom fixture. Cross-group levels rest on the fit's
zero-init anchor; only the 2023 group stage is cross-group by
construction and it is scored like all other dev rows.
Eligibility rule (frozen): eligible = finished AND not awarded AND
stage ≠ championship_group (the `eligible` column of
`data/ng_matches.csv`; n = 1,813).
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
  is absent from every one of the 1,830 payloads.)
- Time decay w = 0.5 ** ((cutoff − match_date).days / 270) — frozen,
  no search.
- Fit scope for target season S: all eligible matches dated strictly
  before the first match date of S (expanding, season-blocked:
  one fit per target season, whole season predicted from that fit).
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
   Nothing else changes. Motivation: 3–4 promoted clubs enter every
   season (EDA §5) and no cross-league mover prior exists
   (FEATURES X2) — no hard-coded tier offset is used.

## Dev protocol

- Training seed = 2021/2022 (n = 379 eligible); evaluation seasons
  2023 group stage (n = 180), 2023/2024 (n = 379), 2024/2025
  (n = 380); pooled scored **n = 939** under the season-blocked
  expanding walk-forward.
- Metrics per arm per season and pooled: mean 1X2 LL, mean RPS
  (H, D, A), mean OU2.5 LL. Baselines: climatology — for target
  season S, pooled outcome rates + OU2.5 over-rate of all eligible
  matches dated strictly before S's first match date; plus the
  naive trailing-10 baseline reported alongside.
- Primary line OU 2.5 (ladder 1.5 / 2.5 / 3.5 reported).
- The dev harness must not read season "2025/2026" or "2026/2027"
  rows at all. Virgin data is touched only by the separate virgin
  step, once, after dev results are frozen in the results file.

## Virgin protocol

- Virgin window: season "2025/2026" (**n = 379, complete**). Fit =
  all eligible matches dated before the first 2025/2026 match
  (seasons 2021/2022–2024/2025). Read ONCE, after dev freezes.
- Virgin climatology: pooled 2021/2022–2024/2025 outcome rates and
  OU2.5 over-rate.
- Calibration per arm: (i) mean predicted home-win probability minus
  actual home-win rate; (ii) mean predicted P(over 2.5) minus actual
  over-rate. Standard error of each difference:
  SE = sd(pred_i − y_i) / √n over the 379 matches, reported with the
  difference. (Sign convention: actual − predicted, as frozen above.)
- Confirmatory window "2026/2027" (in progress, 116 matches to
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
(arm LL ≤ Gate Zero LL in at least half the dev seasons) for the
both-pass rule. Both-pass rule: if Gate Zero and a variant both pass
all legs, the lower pooled virgin 1X2 LL ships; if only one passes,
it ships; if none passes, G-NG verdict is FAIL and nothing ships.

Mechanical reading: an arm passes iff it survives the dev gate AND
passes virgin legs (i)–(ii) (PROVISIONAL counts, recorded as such)
AND, for variant arms, leg (iii); Gate Zero is exempt from (iii).
Ties go to the simpler arm (Gate Zero before SHRINK). If Gate Zero
fails its own dev gate, variants are moot, verdict FAIL, virgin
NOT read.

## Outputs

Engine `league/NG-ProfessionalLeague/engine/goals/`; dev results
`results_dev.json` (+ CSV); virgin `results_virgin.json`; fitted
params `fitted_params_virgin.json`; on PASS, virgin predictions
`league/NG-ProfessionalLeague/predictions/g_ng_virgin_predictions.csv`
(shipped arm; 1H/2H presentation via frozen goals constant 0.4796).
Verdict: `league/NG-ProfessionalLeague/reports/G_NG_VERDICT.md`.
Production code untouched. No push. No merge.
