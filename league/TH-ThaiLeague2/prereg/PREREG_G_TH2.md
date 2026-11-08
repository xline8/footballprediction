# Pre-registration — G-TH2 (Thailand Thai League 2 goals model)

Frozen: 2026-11-10, before any fitting. Branch `build/th-thaileague2`.
Design authority: `analysis/MODEL_DESIGN.md` (G-TH2); features per
`analysis/FEATURES.md` (X1 DROPPED — no xG exists in any payload, so the
observation is goals-only; X2 measured against the parent Thai League 1
corpus, SHRINK is the thin-data arm). Reference: production Dixon-Coles
in `model_v2.py` (class `DC`), hl = 270; sibling analogue:
`league/TH-ThaiLeague/prereg/PREREG_G_TH.md`.
Phase rule (frozen): promotion play-off ties (phase = "playoffs",
6 matches per complete season) are **excluded from every fit and every
scored window**; only regular-phase rows are used.
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
- Fit scope for a target date D: all TH2 regular matches dated strictly
  before D (expanding, date-grouped). Teams unseen in training start at
  the league mean (a = d = 0).

## Arms

1. **Gate Zero** — the unmodified reference above.
2. **Arm SHRINK** (sanctioned G-J2-lesson arm) — Gate Zero plus exactly
   one change at prediction time: for a team with fewer than 6 prior
   in-league matches in the training window, its fitted attack and
   defence ratings are shrunk toward the league mean: `a *= n/6`,
   `d *= n/6` where n = its prior in-league match count (n = 0 ⇒
   a = d = 0, identical to Gate Zero's unseen rule). Nothing else
   changes. X2 evidence: relegated movers into the dev season (n = 3)
   first-season GF/GA gaps +0.397/−0.416, −0.135/+0.147, −0.172/+0.131.
   No hard-coded tier offset is used.

## Dev protocol

- Only one pre-virgin season exists, so dev is a **within-season
  walk-forward** over 2024/2025 regular (n = 273): warm-up = first 90
  matches in (date, match_id) order (never scored); scored = the
  remaining **183 matches** (2024-11-09 – 2025-04-26), predicted
  date-grouped with an expanding fit on all regular matches strictly
  before each scored date.
- Metrics per arm, pooled over the scored block: mean 1X2 LL, mean RPS
  (H, D, A), mean OU2.5 LL. Baselines: climatology — for each scored
  date, pooled outcome rates + OU2.5 over-rate of all regular matches
  strictly before that date (expanding).
- The dev harness must not read 2025/2026 or 2026/2027 rows at all.

## Virgin protocol

- Virgin = 2025/2026 regular (n = 306, last complete season), read
  ONCE, only for arms passing the dev gate, after dev results are
  frozen. Fit = all 2024/2025 regular matches (273). Climatology =
  pooled 2024/2025 regular rates. Calibration: actual − mean predicted
  for home-win rate and OU2.5 over-rate, SE = sd(y_i − p_i)/√n.
- 2026/2027 (90 matches, in progress) is the reserved confirmatory
  window — never read in this build.

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev 1X2 LL and RPS must beat climatology, and OU2.5 LL must beat the base-rate baseline, else the arm is dead. Virgin legs — (i) LL leg: arm's virgin 1X2 LL ≤ Gate Zero's AND ≤ climatology's; (ii) calibration leg: |actual − mean predicted| ≤ 1.0pp pooled for home-win rate and for OU2.5 over-rate, SEs reported; a breach within 1 SE of the boundary is recorded PROVISIONAL PASS, beyond it FAIL; (iii) sign check: a variant arm's pooled dev 1X2 LL ≤ Gate Zero's pooled dev 1X2 LL (single dev season, so the pooled comparison is the check). Both-pass rule: if Gate Zero and a variant both pass all legs, the lower pooled virgin 1X2 LL ships; if only one passes, it ships; if none passes, G-TH2 verdict is FAIL and nothing ships.

Mechanical reading: an arm passes iff it survives the dev gate AND
passes virgin legs (i)–(ii) (PROVISIONAL counts, recorded as such)
AND, for variant arms, leg (iii); Gate Zero is exempt from (iii).
Ties go to the simpler arm (Gate Zero before SHRINK). If Gate Zero
fails its own dev gate, variants are moot, verdict FAIL, virgin
NOT read.

## Outputs

Engine `league/TH-ThaiLeague2/engine/goals/`; dev results
`results_dev.json` (+ CSV); virgin `results_virgin.json`; fitted
params `fitted_params_virgin.json`; on PASS, virgin predictions
`league/TH-ThaiLeague2/predictions/g_th2_virgin_predictions.csv`
(shipped arm; 1H/2H presentation via frozen goals constant 0.4249).
Verdict: `league/TH-ThaiLeague2/reports/G_TH2_VERDICT.md`.
Production code untouched. No push. No merge.
