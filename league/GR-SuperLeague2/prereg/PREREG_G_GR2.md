# Pre-registration — G-GR2 (GR-SuperLeague2 goals model)

Frozen: 2026-11-10, before any fitting. Branch `build/gr-superleague2`.
Design authority: `league/GR-SuperLeague2/analysis/MODEL_DESIGN.md`
(G-GR2); features per `analysis/FEATURES.md` (X1 blend pair, goals-only
throughout — xG exists in zero payloads; X2 measured but not consumed,
SHRINK is the thin-data arm); evidence per `analysis/EDA.md`.
Reference: production Dixon-Coles in `model_v2.py` (class `DC`),
hl = 270; PL analogue:
`league/PL-Ekstraklasa/prereg/PREREG_G_PL.md`; closest sibling
`league/GR-SuperLeague/prereg/PREREG_G_GR.md` (whose goals candidate
failed its dev gate on OU2.5 LL — the same leg applies here).
Phase rule (frozen, MODEL_DESIGN): phase is flagged from
`general.leagueName` (regular / playoff_promotion /
playoff_relegation / playoff / supercup); all phases are ordinary
rows in every fit; no phase feature anywhere. B-team rule (frozen):
B teams are ordinary teams; no B-team feature anywhere.
Calibration is defined as **actual − predicted** everywhere in this
build.

## Reference architecture (all arms share unless an arm says otherwise)

- Dixon-Coles fit, copied pattern from production `model_v2.py`:
  iterative multiplicative updates, 14 sweeps, damping 0.7, +0.25
  smoothing, home advantage fitted (init 0.28), attack/defence per
  team (init 0), score matrix MAXG = 10, production `tau` correction.
- Rho per fit from grid (0.0, −0.05, −0.10, −0.15) by weighted
  log-likelihood on goals only, as production.
- Observation (X1): blend 0.5·goals + 0.5·xG when both xG present,
  goals-only fallback otherwise. GR2 stats xG exists in zero of the
  1,935 payloads, so the fallback fires on every match in dev and
  in the virgin fit; Gate Zero is therefore the goals-only DC in
  this corpus, with the production blend pattern intact.
- Time decay w = 0.5 ** ((cutoff − match_date).days / 270); blend
  weight 0.5 — both frozen, no search.
- Fit scope for target season S: all GR2 matches dated strictly
  before the first match date of S (expanding, season-blocked).
- Teams unseen in training start at the league mean (a = d = 0).
  Team identity is the FotMob team id.

## Arms

1. **Gate Zero** — the unmodified reference above.
2. **Arm SHRINK** (sanctioned G-J2-lesson arm) — Gate Zero plus
   exactly one change at prediction time: for a team with fewer
   than 6 prior in-league matches in the training window, its
   fitted attack and defence ratings are shrunk toward the league
   mean: `a *= n/6`, `d *= n/6` where n = its prior in-league match
   count (n = 0 ⇒ a = d = 0, identical to Gate Zero's unseen rule;
   the arm bites exactly for teams with 1–5 prior matches; under
   season-blocked fitting that band may not occur, which is itself
   a recorded finding if so). Nothing else changes.
3. **No X2 arm.** The mover gaps are measured in EDA F4
   (SL1-relegated +0.314/−0.288, n=8 with 5 in dev; Gamma/other
   −0.198/+0.108, n=25) but no offset is estimated or consumed:
   5 dev movers cannot carry a parameter, and a single pooled
   newcomer offset would be wrong-signed for both origin groups.
   Recorded in FEATURES; not built.

## Dev protocol

- Training seed = 2021/2022; evaluation seasons 2022/2023, 2023/2024,
  2024/2025 (pooled scored n = 1,045) under the season-blocked
  walk-forward.
- Metrics per arm per season and pooled: mean 1X2 LL, mean RPS
  (H, D, A), mean OU2.5 LL. Baselines: climatology — for target
  season S, pooled outcome rates + OU2.5 over-rate of all seasons
  strictly before S.
- The dev harness must not read 2025/2026 or 2026/2027 rows at all.

## Virgin protocol

- Virgin = 2025/2026 (n = 265, complete), read ONCE, only for arms
  passing the dev gate, after dev results are frozen. Fit = all
  matches before the first 2025/2026 match date. Climatology =
  pooled 2021/2022–2024/2025 rates. Calibration: actual − mean
  predicted for home-win rate and OU2.5 over-rate, SE = sd(y_i − p_i)/√n.
- 2026/2027 (n = 79, in progress, single-group format) is
  confirmatory only and is not read in this build.

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev 1X2 LL and RPS of an arm must beat climatology, and OU2.5 LL must beat the base-rate baseline, else the arm is dead. Virgin legs — (i) LL leg: arm's virgin 1X2 LL ≤ Gate Zero's AND ≤ climatology's; (ii) calibration leg: |actual − mean predicted| ≤ 1.0pp pooled for home-win rate and for OU2.5 over-rate, SEs reported; a breach within 1 SE of the boundary is recorded PROVISIONAL PASS, beyond it FAIL; (iii) per-season sign check on dev (arm LL ≤ Gate Zero LL in at least half the dev seasons) for the both-pass rule. Both-pass rule: if Gate Zero and a variant both pass all legs, the lower pooled virgin 1X2 LL ships; if only one passes, it ships; if none passes, G-GR2 verdict is FAIL and nothing ships.

Mechanical reading: an arm passes iff it survives the dev gate AND
passes virgin legs (i)–(ii) (PROVISIONAL counts, recorded as such)
AND, for variant arms, leg (iii); Gate Zero is exempt from (iii).
Ties go to the simpler arm (Gate Zero before SHRINK). If Gate Zero
fails its own dev gate, variants are moot, verdict FAIL, virgin
NOT read.

## Outputs

Engine `league/GR-SuperLeague2/engine/goals/`; dev results
`results_dev.json` (+ CSV); virgin `results_virgin.json`; fitted
params `fitted_params_virgin.json`; on PASS, virgin predictions
`league/GR-SuperLeague2/predictions/g_gr2_virgin_predictions.csv`
(shipped arm; 1H/2H presentation via frozen goals constant 0.4596).
Verdict: `league/GR-SuperLeague2/reports/G_GR2_VERDICT.md`.
Production code untouched. No push. No merge.
