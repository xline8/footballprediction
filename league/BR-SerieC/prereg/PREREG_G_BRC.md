# Pre-registration — G-BRC (BR-SerieC goals model)

Frozen: 2026-11-10, before any fitting. Branch `build/br-seriec`.
Design authority: `league/BR-SerieC/analysis/MODEL_DESIGN.md` (G-BRC);
features per `analysis/FEATURES.md` (X1 blend pair, X2 mover offset,
SHRINK prior); evidence per `analysis/EDA.md`. Reference: production
Dixon-Coles in `model_v2.py` (class `DC`), hl = 270; BR analogue:
`league/BR-SerieB/prereg/PREREG_G_BRB.md` — its reference architecture
is carried over, changing only league, data file, windows (virgin
2026 is complete, so there is no confirmatory window), the phase
rule, and the X2 two-sided parameterisation below.

## Reference architecture (all arms share unless an arm says otherwise)

- Dixon-Coles fit, copied pattern from production `model_v2.py`:
  iterative multiplicative updates, 14 sweeps, damping 0.7, +0.25
  smoothing, home advantage fitted (init 0.28), attack/defence per
  team (init 0), score matrix MAXG = 10, production `tau` correction.
- Rho per fit from grid (0.0, −0.05, −0.10, −0.15) by weighted
  log-likelihood on goals only, as production.
- Observation (X1): blend 0.5·goals + 0.5·xG when both xG present,
  goals-only fallback otherwise. Série C xG coverage is ZERO in every
  season (no stat value exists in any of the 1,286 payloads), so the
  blend is goals-only in effect for every fit in this build — the
  reference's own fallback, not a design change.
- Time decay w = 0.5 ** ((cutoff − match_date).days / 270); blend
  weight 0.5 — both frozen, no search.
- Fit scope for target season S: all BR-SerieC **fit-set** matches
  (`in_fit_set = 1`, i.e. first phase + second-stage / Promotion
  Round groups; the two Final legs per season are excluded by the
  frozen phase rule) dated strictly before the first match date of
  S (expanding, season-blocked).
- Teams unseen in training start at the league mean (a = d = 0).

## Arms

1. **Gate Zero** — the unmodified reference above.
2. **Arm SHRINK** (sanctioned G-J2-lesson arm) — Gate Zero plus
   exactly one change at prediction time: for a team with fewer
   than 6 prior in-league matches in the training window, its
   fitted attack and defence ratings are shrunk toward the league
   mean: `a *= n/6`, `d *= n/6`, n = prior in-league match count
   (n = 0 ⇒ identical to Gate Zero's unseen rule). Nothing else.
3. **Arm X2** — Gate Zero plus cross-tier priors (feature X2, EDA
   mover finding). A club is a *mover* for target season S when it
   plays in Série C in S, did NOT play Série C in S−1, and either
   played S−1 in Série B (id 8814, *ex-B / down-mover*) or played
   S−1 in NEITHER Série B nor Série C (*newcomer / up-mover*,
   promoted from Série D — Série D is not in the warehouse, so
   absence from both tiers is the presence-based definition),
   identified by FotMob team id in the warehouse index. For a
   mover, at prediction time in season S only:
   - The offsets are defined in LAMBDA space (unambiguous under
     any rating sign convention; the engine implements them as the
     equivalent rating shifts and must say so in its README):
     ex-B: lambda_for × (mu − 0.0405)/mu and lambda_against ×
     (mu − 0.0868)/mu. newcomer: lambda_for × (mu − 0.0627)/mu
     and lambda_against × (mu + 0.0667)/mu. (lambda_for = the
     mover's own expected goals; lambda_against = its opponent's.)
   where mu is the decay-weighted mean goals per team per match in
   the training window, and the four deltas are the pooled
   match-weighted first-C-season deviations from the C league mean
   over the DEV-ERA transitions into 2022, 2023, 2024, 2025 ONLY
   (ex-B: dGF −0.178/+0.080/−0.103/+0.038, dGA
   −0.081/−0.204/−0.054/+0.006; newcomer: dGF
   −0.155/−0.159/+0.185/−0.149, dGA +0.061/−0.011/+0.094/+0.114;
   coordinator-verified from brc_team_matches.csv, fit-set basis,
   pooled league mean 1.1157). The transition into the virgin 2026
   is deliberately NOT used (its first-season performance is virgin
   data). Deltas are floored so mu + delta stays ≥ 0.10. Recorded
   honestly: the per-season signs flip for ex-B goals-for (2/4
   negative) — the arm is a gated hypothesis, not an asserted
   effect. X2 does NOT stack on SHRINK.

## Dev protocol

- Training seed = 2021 (fit-set n = 147 usable; the 57 unfinished
  2021 payloads are excluded with placeholder scores — a data fact,
  not a design choice); evaluation seasons 2022, 2023, 2024, 2025
  (pooled fit-set n = 856) under the season-blocked walk-forward.
- Metrics per arm per season and pooled: mean 1X2 LL, mean RPS
  (H, D, A), mean OU2.5 LL. Baselines: climatology — for target
  season S, pooled outcome rates + OU2.5 over-rate of all fit-set
  seasons strictly before S. Primary line OU2.5 (dev pooled
  over-rate 0.396 — the .5 line closest to 0.5; OU1.5 0.646,
  OU3.5 0.188).
- The dev harness must not read 2026 rows at all (enforce by an
  explicit season allow-list / date assertion in the loader, and
  state the check in the engine README).

## Virgin protocol

- Virgin = 2026 (n = 214 fit-set matches, complete — final legs
  2026-10-17 and 2026-10-24), read ONCE, only for arms passing
  the dev gate, after dev results are frozen. Fit = all fit-set
  matches before the first 2026 match date. Climatology = pooled
  2021–2025 fit-set rates (H/D/A 0.475/0.300/0.225, OU2.5 over
  0.389). Calibration = ACTUAL − PREDICTED (this build's stated
  convention) for home-win rate and OU2.5 over-rate,
  SE = sd(y_i − p_i)/√n.
- There is NO confirmatory window: 2026 is the most recent
  complete season.

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev 1X2 LL and RPS of an arm must beat climatology, and OU2.5 LL must beat the base-rate baseline, else the arm is dead. Virgin legs — (i) LL leg: arm's virgin 1X2 LL ≤ Gate Zero's AND ≤ climatology's; (ii) calibration leg: |actual − predicted| ≤ 1.0pp pooled for home-win rate and for OU2.5 over-rate, SEs reported; a breach within 1 SE of the boundary is recorded PROVISIONAL PASS, beyond it FAIL; (iii) per-season sign check on dev (arm LL ≤ Gate Zero LL in at least half the dev seasons) for the both-pass rule. Both-pass rule: if Gate Zero and a variant both pass all legs, the lower pooled virgin 1X2 LL ships; if only one passes, it ships; if none passes, G-BRC verdict is FAIL and nothing ships.

Mechanical reading: an arm passes iff it survives the dev gate AND
passes virgin legs (i)–(ii) (PROVISIONAL counts, recorded as such)
AND, for variant arms, leg (iii); Gate Zero is exempt from (iii).
Ties go to the simpler arm (Gate Zero before SHRINK before X2).
If Gate Zero fails its own dev gate, variants are moot, verdict
FAIL, virgin NOT read.

## Outputs

Engine `league/BR-SerieC/engine/goals/`; dev results
`results_dev.json` (+ CSV); virgin `results_virgin.json`; fitted
params `fitted_params_virgin.json`; on PASS, virgin predictions
`league/BR-SerieC/predictions/g_brc_virgin_predictions.csv`
(shipped arm; 1H/2H presentation via frozen goals constant 0.443).
Verdict: `league/BR-SerieC/reports/G_BRC_VERDICT.md`.
Production code untouched. No push. No merge.

## Commit-order note (environment)

This prereg was written and frozen BEFORE any fitting (file created
2026-11-10, prior to the engine/dev brief). The builder's sandbox
blocks git object writes (EPERM on `.git/objects` writes; verified
by strace: `write()` to a loose-object tmp file returns EPERM, while
ordinary workspace writes succeed), so the builder could not commit
it in-session. The coordinator MUST commit in this exact order to
preserve the gate audit: (1) steps 1–6 + not-buildable verdicts,
(2) this prereg alone, (3) engine + dev results, (4) virgin results
+ G-BRC verdict. Do NOT squash (1)+(2) into one commit.
