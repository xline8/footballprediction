# Pre-registration — G-RS (RS-SuperLiga goals model)

Frozen: 2026-11-10, before any fitting. Branch `wip-rs-superliga`.
Design authority: `analysis/MODEL_DESIGN.md` (G-RS); features X1 (goals-only
fallback — no xG exists in this feed in any season), X2, X5 (goals only);
evidence F1/F2/F4 (EDA.md). Reference: production Dixon-Coles;
programme analogue `PREREG_G_FI.md` with the architecture carried over
verbatim (14 sweeps, damping 0.7, +0.25 smoothing, home init 0.28, MAXG = 10,
production tau, rho grid (0.0, −0.05, −0.10, −0.15) by goals
log-likelihood, decay HL = 270 days). The ONLY reference divergence in the
observation: goals-only in every match (the X1 blend's documented
fallback), because the Super Liga feed carries no xG in any season.

Phases: all league-member rows are ordinary rows (regular / championship /
relegation flags carried, never filtered). The 8 **qualification** rows
(2021/2022 + 2022/2023, 2-legged relegation play-off ties vs Prva Liga
tier-2 clubs) are EXCLUDED from fitting and from dev scoring — they pit
Super Liga clubs against clubs with no in-corpus history; the exclusion is
documented in `analysis/DATA_UNDERSTANDING.md` and
`eda_summary.json: qualification_matches`, never silent. Awarded match
4271663 (2023/2024, awarded 0–3 but 7 Goal events): FT score is
authoritative and the row IS fitted/scored; it is excluded from the halves
measurement only (EDA.md).

## Arms
1. **Gate Zero** — the unmodified reference above, fitted on league-member
   rows only (phase != qualification).
2. **SHRINK** — Gate Zero plus the sanctioned G-J2-lesson change: at
   prediction time a team with n < 6 prior in-league matches has
   a *= n/6, d *= n/6 (applied to the log-ratings, as in the FI reference
   implementation).
3. **X2** — SHRINK plus the entrant offset: a club whose previous completed
   season was NOT in the Super Liga regular phase (entrant, identified
   in-corpus by absence from the previous season's REGULAR-phase teams —
   the RS divergence from FI, forced by EDA: the plain-absence rule here
   catches tier-2 qualification opponents) enters with its lambdas tilted
   — its scoring lambda multiplied by exp(g), its conceded lambda by
   exp(c), where (g, c) are the mean (GF diff, GA diff) of all entrant
   transitions completed BEFORE the predicted season, measured in the RS
   corpus itself (each entrant's first-season GF/GA per match minus that
   season's league team mean, league-member rows only); if fewer than 3
   completed transitions exist, the offset is 0. Multipliers clamped to
   [0.8, 1.25]. The tilt applies only in the entrant's first Super Liga
   season. Dev measurement (for the record, not a frozen constant — the
   harness recomputes it from completed transitions before each season):
   7 dev transitions, GF −0.326, GA +0.242
   (`eda_summary.json: x2_entrant_gf_ga_diff_vs_league_team_mean_dev`).
   The offset first fires in dev 2024/2025 (4 completed transitions; before
   2022/2023 there are 0, before 2023/2024 there are 2 — below the minimum
   of 3). For the virgin it fires for Javor and FK Radnik Surdulica on the
   7 dev transitions (clamped multipliers 0.8 scoring / 1.25 conceded).

## Dev protocol
Training seed 2021/2022 (300 matches; 296 league-member); evaluation
seasons 2022/2023–2024/2025 (pooled n = 888 league-member rows; 892
including the 4 excluded qualification rows), season-blocked (expanding
fit strictly before each season's first match). Metrics: 1X2 LL, RPS,
OU2.5 LL per season and pooled. Baseline: climatology (expanding
prior-seasons pooled outcome rates + OU2.5 over-rate; pooled climatology
is the pooled score of the per-season expanding climatology predictions).
The dev harness must not read 2025/2026 rows. Note: MODEL_DESIGN.md
mentions a "naive trailing-10" baseline in passing; it was never defined
anywhere in the step 1–6 documents, so it is NOT a frozen baseline — the
frozen baselines are climatology (1X2 LL / RPS) and the base-rate OU2.5
baseline, exactly as in the FI reference prereg.

## Virgin protocol
Virgin = 2025/2026 (n = 296, complete season, last match 2026-05-24),
read ONCE, only for dev-passing arms. Calibration: mean predicted −
actual for home-win rate and OU2.5 over-rate, SE = sd(p_i − y_i)/√n.

## GATE LEGS (verbatim, frozen)
Dev gate — pooled dev 1X2 LL and RPS of an arm must beat climatology, and
OU2.5 LL must beat the base-rate baseline, else the arm is dead. Virgin
legs — (i) LL leg: arm's virgin 1X2 LL ≤ Gate Zero's AND ≤ climatology's;
(ii) calibration leg: |mean predicted − actual| ≤ 1.0pp pooled for
home-win rate and for OU2.5 over-rate, SEs reported; a breach within 1 SE
of the boundary is recorded PROVISIONAL PASS, beyond it FAIL; (iii)
per-season sign check on dev (arm LL ≤ Gate Zero LL in at least half the
dev seasons) for the both-pass rule. Both-pass rule: if Gate Zero and a
variant both pass all legs, the lower pooled virgin 1X2 LL ships; if only
one passes, it ships; if none passes, G-RS verdict is FAIL and nothing
ships. Mechanical reading: an arm passes iff it survives the dev gate AND
passes virgin legs (i)–(ii) (PROVISIONAL counts) AND, for variants, leg
(iii); Gate Zero is exempt from (iii). Ties → simpler arm (Gate Zero,
SHRINK, X2). If Gate Zero fails its dev gate, variants are moot, verdict
FAIL, virgin NOT read.

## Outputs
Engine `engine/goals/`; `results_dev.json` (+ CSV); `results_virgin.json`;
`fitted_params_virgin.json`; on PASS, `predictions/g_rs_virgin_predictions.csv`
(1H/2H presentation via frozen goals constant 0.4606). Verdict
`reports/G_RS_VERDICT.md`.
