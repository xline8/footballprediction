# Pre-registration — G-BG (Bulgaria First Professional League goals model)

Frozen: 2026-11-10, before any fitting. Branch `build/bg-first`.
Design authority: `league/BG-FirstLeague/analysis/MODEL_DESIGN.md` (G-BG);
features per `analysis/FEATURES.md` (X1 DROPPED — no xG or shotmap
anywhere in this league, so the observation is goals-only; X2's tier
offset is not hard-coded — the mover gaps were measured against the
real tier-2 corpus (id 9096): 7 pre-virgin entrants, GF −0.205,
GA +0.399 — and SHRINK is the thin-data arm). Reference: production
Dixon-Coles in `model_v2.py` (class `DC`), hl = 270; sibling analogue:
`league/ZA-PSL/prereg/PREREG_G_ZA.md`.
Phase rule (frozen): every modelled row keeps its `phase` flag
(regular / championship_playoff / ecl_group / relegation_group /
ecl_playoff); all phases are in every window; no phase feature.
Team identity is the FotMob team id.
Calibration is defined as **actual − predicted** everywhere in this build.

## Reference architecture (all arms share unless an arm says otherwise)

- Dixon-Coles fit, copied pattern from production `model_v2.py`:
  iterative multiplicative updates, 14 sweeps, damping 0.7, +0.25
  smoothing, home advantage fitted (init 0.28), attack/defence per
  team (init 0), score matrix MAXG = 10, production `tau` correction.
- Rho per fit from grid (0.0, −0.05, −0.10, −0.15) by weighted
  log-likelihood on goals only, as production.
- Observation: goals only.
- Time decay w = 0.5 ** ((cutoff − match_date).days / 270) — frozen,
  no search.
- Fit scope for target season S: all BG matches dated strictly before
  the first match date of S (expanding, season-blocked).
- Teams unseen in training start at the league mean (a = d = 0).

## Arms

1. **Gate Zero** — the unmodified reference above.
2. **Arm SHRINK** (programme-sanctioned G-J2-lesson arm) — Gate Zero plus
   exactly one change at prediction time: for a team with fewer than 6
   prior in-league matches in the training window, its fitted attack and
   defence ratings are shrunk toward the league mean: `a *= n/6`,
   `d *= n/6` where n = its prior in-league match count (n = 0 ⇒
   a = d = 0, identical to Gate Zero's unseen rule). Nothing else
   changes. X2 evidence: entrants measured against the real tier-2
   corpus (n = 7 pre-virgin), first-season GF gap −0.205, GA gap
   +0.399. No hard-coded tier offset is used. (Note, recorded in
   advance from the TH/ZA sibling runs: under season-blocked fitting a
   team's prior count is 0 or ≥ a full season, so SHRINK may turn out
   row-identical to Gate Zero; if so, that is reported, not patched.)

## Dev protocol

- Training seed = 2021/2022; evaluation seasons 2022/2023, 2023/2024,
  2024/2025 (pooled scored n = 859) under the season-blocked
  walk-forward.
- Metrics per arm per season and pooled: mean 1X2 LL, mean RPS
  (H, D, A), mean OU2.5 LL. Baselines: climatology — for target
  season S, pooled outcome rates + OU2.5 over-rate of all seasons
  strictly before S.
- The dev harness must not read 2025/2026 or 2026/2027 rows at all.

## Virgin protocol

- Virgin = 2025/2026 (n = 293, last complete season), read ONCE, only
  for arms passing the dev gate, after dev results are frozen.
  Fit = all matches before the first 2025/2026 match date.
  Climatology = pooled 2021/2022–2024/2025 rates. Calibration:
  actual − mean predicted for home-win rate and OU2.5 over-rate,
  SE = sd(y_i − p_i)/√n.
- 2026/2027 (97 matches, in progress) is the reserved confirmatory
  window — never read in this build.

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev 1X2 LL and RPS must beat climatology, and OU2.5 LL must beat the base-rate baseline, else the arm is dead. Virgin legs — (i) LL leg: arm's virgin 1X2 LL ≤ Gate Zero's AND ≤ climatology's; (ii) calibration leg: |actual − mean predicted| ≤ 1.0pp pooled for home-win rate and for OU2.5 over-rate, SEs reported; a breach within 1 SE of the boundary is recorded PROVISIONAL PASS, beyond it FAIL; (iii) per-season sign check on dev (arm LL ≤ Gate Zero LL in at least half the dev seasons) for the both-pass rule. Both-pass rule: if Gate Zero and a variant both pass all legs, the lower pooled virgin 1X2 LL ships; if only one passes, it ships; if none passes, G-BG verdict is FAIL and nothing ships.

Mechanical reading: an arm passes iff it survives the dev gate AND
passes virgin legs (i)–(ii) (PROVISIONAL counts, recorded as such)
AND, for variant arms, leg (iii); Gate Zero is exempt from (iii).
Ties go to the simpler arm (Gate Zero before SHRINK). If Gate Zero
fails its own dev gate, variants are moot, verdict FAIL, virgin
NOT read.

## Outputs

Engine `league/BG-FirstLeague/engine/goals/`; dev results
`results_dev.json` (+ CSV); virgin `results_virgin.json`; fitted
params `fitted_params_virgin.json`; on PASS, virgin predictions
`league/BG-FirstLeague/predictions/g_bg_virgin_predictions.csv`
(shipped arm; 1H/2H presentation via frozen goals constant 0.4542).
Verdict: `league/BG-FirstLeague/reports/G_BG_VERDICT.md`.
Production code untouched. No push. No merge.
