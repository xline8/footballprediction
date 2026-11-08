# Pre-registration — G-DE2 (DE-2Bundesliga goals model)

Frozen: 2026-11-09, before any fitting. Branch `build/de-2bundesliga`.
Design authority: `league/DE-2Bundesliga/analysis/MODEL_DESIGN.md`
(G-DE2); features per `analysis/FEATURES.md` (X1 blend pair, X2 mover,
X3 set-play); evidence per `analysis/EDA.md` (F1/F2/F5/F6/F12).
Reference: production Dixon-Coles in `model_v2.py` (class `DC`),
hl = 270; J1 analogue: `league/J1/prereg/PREREG_G_J1.md`; SHRINK/X3
form: `league/BE-FirstDivisionA/prereg/PREREG_G_BE.md`.
Format rule (frozen, MODEL_DESIGN): all matches are ordinary rows in
every fit; no phase feature anywhere (this corpus has no phases).

## Reference architecture (all arms share unless an arm says otherwise)

- Dixon-Coles fit, copied pattern from production `model_v2.py`:
  iterative multiplicative updates, 14 sweeps, damping 0.7, +0.25
  smoothing, home advantage fitted (init 0.28), attack/defence per
  team (init 0), score matrix MAXG = 10, production `tau` correction.
- Rho per fit from grid (0.0, −0.05, −0.10, −0.15) by weighted
  log-likelihood on goals only, as production.
- Observation (X1): blend 0.5·goals + 0.5·xG when both xG present,
  goals-only fallback otherwise. DE-2 has xG in every match, so the
  fallback never triggers.
- Half-life 270 days and blend weight 0.5 are the production values,
  frozen — no search.
- Fit scope for a target season S: all DE-2 matches with date strictly
  before the first match date of S (expanding window, season-blocked:
  one fit per target season, whole season predicted from that fit).
- Teams unseen in training start at the league mean (a = d = 0).

## Arms

1. **Gate Zero** — the unmodified reference above.
2. **Arm SHRINK** (sanctioned G-J2-lesson arm; EDA F5) — Gate Zero
   plus exactly one change at prediction time: for a team with
   fewer than 6 prior in-league matches in the training window, its
   fitted attack and defence ratings are shrunk toward the league
   mean: `a *= n/6`, `d *= n/6` where n = its prior in-league match
   count (n = 0 ⇒ a = d = 0, identical to Gate Zero's unseen rule;
   the arm bites exactly for teams with 1–5 prior matches — the
   season-opener failure mode). Nothing else changes.
3. **Arm X2** — Gate Zero plus direction-specific mover priors
   (feature X2, EDA F5). A club is a *mover* for target season S
   when its team id plays DE-2 in S, did not play DE-2 in S−1, and
   played S−1 in a neighbour tier — direction `down` if in the
   Bundesliga (FotMob id 54), `up` if in 3. Liga (id 208) —
   classified in the frozen table `analysis/movers.json` (`ids`
   block, built by `analysis/movers.py` from index membership;
   every entrant in the corpus resolves to exactly one neighbour).
   For a mover, at prediction time in season S only:
   - attack: `a += log(max(mu + ΔGF_dir, 0.10) / mu)`
   - defence: `d += log(max(mu + ΔGA_dir, 0.10) / mu)`
   where mu is the decay-weighted mean goals per team per match in
   the training window, and ΔGF_dir / ΔGA_dir are **estimated inside
   the fit**: pooled over all entrant first seasons strictly before
   S that are present in the training window (entrant GF per
   team-match minus the same seasons' league GF per team-match;
   likewise GA). If a direction has fewer than 2 clubs of such
   history, its offset is 0 (inactive). By construction there are
   NO prior transitions before 2022/2023 in this corpus (2021/2022
   is the first season), so X2 ≡ Gate Zero for the 2022/2023 dev
   season; the arm first bites in 2023/2024 (offsets from the
   2022/2023 transition: 5 clubs) and in the virgin (offsets from
   the three dev-era transitions: up ΔGF −0.360 / ΔGA +0.143 on
   9 clubs, down +0.097 / +0.078 on 6 clubs — the EDA F5 pooled
   values, which the virgin fit must reproduce). A club with no
   immediately-preceding-season record in DE-2, the Bundesliga or
   3. Liga starts at the league mean in every arm.
4. **Arm X3** — Arm SHRINK plus the set-play decomposition tilt of
   `PREREG_G_BE.md` arm X3, verbatim in form: decay-weighted
   open-play/set-play xG for/against per team over the training
   window; `att_mult = sqrt((op_for/L_op)·(sp_for/L_sp))`,
   `def_mult` mirrored, clamped [0.5, 2.0]; lambdas tilted by
   `sqrt(att_mult · def_mult_opp)`; teams with <8 xG matches in the
   window get multiplier 1.0. (X3 builds on SHRINK, not on X2 — the
   BE form — so the mover and set-play questions stay separable.)

## Dev protocol

- Training seed = 2021/2022; evaluation seasons 2022/2023, 2023/2024,
  2024/2025 (pooled n = 918) under the season-blocked walk-forward.
- Metrics per arm per season and pooled: mean 1X2 LL, mean RPS
  (H, D, A), mean OU2.5 LL. Baselines: climatology — for target
  season S, pooled outcome rates + OU2.5 over-rate of all seasons
  strictly before S.
- The dev harness must not read 2025/2026 or 2026/2027 rows at all.

## Virgin protocol

- Virgin = 2025/2026 (n = 306, complete), read ONCE, only for arms
  passing the dev gate, after dev results are frozen. Fit = all
  matches before the first 2025/2026 match date. Climatology =
  pooled 2021/2022–2024/2025 rates. Calibration: mean predicted −
  actual for home-win rate and OU2.5 over-rate, SE = sd(p_i − y_i)/√n.

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev 1X2 LL and RPS of an arm must beat climatology, and OU2.5 LL must beat the base-rate baseline, else the arm is dead. Virgin legs — (i) LL leg: arm's virgin 1X2 LL ≤ Gate Zero's AND ≤ climatology's; (ii) calibration leg: |mean predicted − actual| ≤ 1.0pp pooled for home-win rate and for OU2.5 over-rate, SEs reported; a breach within 1 SE of the boundary is recorded PROVISIONAL PASS, beyond it FAIL; (iii) per-season sign check on dev (arm LL ≤ Gate Zero LL in at least half the dev seasons) for the both-pass rule. Both-pass rule: if Gate Zero and a variant both pass all legs, the lower pooled virgin 1X2 LL ships; if only one passes, it ships; if none passes, G-DE2 verdict is FAIL and nothing ships.

Mechanical reading: an arm passes iff it survives the dev gate AND
passes virgin legs (i)–(ii) (PROVISIONAL counts, recorded as such)
AND, for variant arms, leg (iii); Gate Zero is exempt from (iii).
Ties go to the simpler arm (Gate Zero before SHRINK before X2 before
X3). If Gate Zero fails its own dev gate, variants are moot, verdict
FAIL, virgin NOT read.

## Outputs

Engine `league/DE-2Bundesliga/engine/goals/`; dev results
`results_dev.json` (+ CSV); virgin `results_virgin.json`; fitted
params `fitted_params_virgin.json`; on PASS, virgin predictions
`league/DE-2Bundesliga/predictions/g_de2_virgin_predictions.csv`
(shipped arm; 1H/2H presentation via frozen goals constant 0.450).
Verdict: `league/DE-2Bundesliga/reports/G_DE2_VERDICT.md`.
Production code untouched. No push. No merge.
