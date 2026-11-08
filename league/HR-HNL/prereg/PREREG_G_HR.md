# Pre-registration — G-HR (HR-HNL goals model)

Frozen: 2026-11-10, before any fitting. Branch `build/hr-hnl`.
Design authority: `analysis/MODEL_DESIGN.md` (G-HR); features X1 (goals-only
fallback — no xG exists in this feed), X2; evidence F1/F2/F4.
Reference: production Dixon-Coles in `model_v2.py`; programme analogue
`PREREG_G_FI.md` with the architecture carried over verbatim (14 sweeps,
damping 0.7, +0.25 smoothing, home init 0.28, MAXG = 10, production tau,
rho grid (0.0, −0.05, −0.10, −0.15) by goals log-likelihood, decay
HL = 270 days). The ONLY reference divergence: the observation is
goals-only in every match (the X1 blend's documented fallback), because
the HNL feed carries no xG in any season.

Phases: all rows are ordinary regular-season rows (HNL has no split or
play-off phase; Step 1). The in-progress 2026/2027 season is never loaded.

## Arms
1. **Gate Zero** — the unmodified reference above.
2. **SHRINK** — Gate Zero plus the sanctioned G-J2-lesson change: at prediction
   time a team with n < 6 prior in-league matches has a *= n/6, d *= n/6.
3. **X2** — SHRINK plus the entrant offset: a club whose previous completed
   season was NOT in HNL (entrant, identified in-corpus by absence from
   the previous season — HR is tier 1, entrants are promoted clubs; no
   tier-2 corpus is built in-system) enters with its lambdas tilted — its
   scoring lambda multiplied by exp(g), its conceded lambda by exp(c), where
   (g, c) are the mean (GF diff, GA diff) of all entrant transitions
   completed BEFORE the predicted season, measured in the HNL corpus
   itself (each entrant's first-season GF/GA per match minus that
   season's league team mean); if fewer than 3 completed transitions exist,
   the offset is 0. Multipliers clamped to [0.8, 1.25]. The tilt applies
   only in the entrant's first HNL season.

## Dev protocol
Training seed 2021/2022; evaluation seasons 2022/2023–2024/2025
(pooled n = 540), season-blocked (expanding fit strictly before each
season's first match). Metrics: 1X2 LL, RPS, OU2.5 LL per season and
pooled. Baseline: climatology (prior-seasons pooled outcome rates +
OU2.5 over-rate). The dev harness must not read 2025/2026 rows.

## Virgin protocol
Virgin = 2025/2026 (n = 180, complete season), read ONCE, only for
dev-passing arms. Calibration: mean predicted − actual for home-win rate
and OU2.5 over-rate, SE = sd(p_i − y_i)/√n.

## GATE LEGS (verbatim, frozen)
Dev gate — pooled dev 1X2 LL and RPS of an arm must beat climatology, and OU2.5 LL must beat the base-rate baseline, else the arm is dead. Virgin legs — (i) LL leg: arm's virgin 1X2 LL ≤ Gate Zero's AND ≤ climatology's; (ii) calibration leg: |mean predicted − actual| ≤ 1.0pp pooled for home-win rate and for OU2.5 over-rate, SEs reported; a breach within 1 SE of the boundary is recorded PROVISIONAL PASS, beyond it FAIL; (iii) per-season sign check on dev (arm LL ≤ Gate Zero LL in at least half the dev seasons) for the both-pass rule. Both-pass rule: if Gate Zero and a variant both pass all legs, the lower pooled virgin 1X2 LL ships; if only one passes, it ships; if none passes, G-HR verdict is FAIL and nothing ships.
Mechanical reading: an arm passes iff it survives the dev gate AND passes virgin legs (i)–(ii) (PROVISIONAL counts) AND, for variants, leg (iii); Gate Zero is exempt from (iii). Ties → simpler arm (Gate Zero, SHRINK, X2). If Gate Zero fails its dev gate, variants are moot, verdict FAIL, virgin NOT read.

## Outputs
Engine `engine/goals/`; `results_dev.json` (+ CSV); `results_virgin.json`;
`fitted_params_virgin.json`; on PASS, `predictions/g_hr_virgin_predictions.csv`
(1H/2H presentation via frozen goals constant 0.4320). Verdict `reports/G_HR_VERDICT.md`.
