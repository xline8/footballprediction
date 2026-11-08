# Pre-registration — G-YK (FI-Ykkosliiga goals model)

Frozen: 2026-11-10, before any fitting. Branch `build/fi-ykkosliiga`.
Design authority: `analysis/MODEL_DESIGN.md`; features X1 goals-only fallback
and X2 entrant offset. No engine exists and no fitting is authorized by this
brief.

## Arms

1. **Gate Zero** — production Dixon-Coles pattern: 14 sweeps, damping 0.7,
   +0.25 smoothing, home init 0.28, MAXG=10, production tau, rho grid
   (0.0, -0.05, -0.10, -0.15) by goals log-likelihood, decay HL=270 days.
   The observation is goals-only because this feed has no xG.
2. **SHRINK** — Gate Zero plus the G-J2 lesson: at prediction time a team with
   n < 6 prior in-league matches has a*=n/6, d*=n/6.
3. **X2** — SHRINK plus one pooled entrant offset. Entrants are identified from
   team ids across league_id 51 + 251, pooling relegated Veikkausliiga clubs
   and clubs absent from both corpora the prior season. The offset uses all
   completed entrant transitions before the predicted season; it is inactive
   until at least 3 transitions exist, its multipliers are clamped to [0.8,
   1.25], and it applies in the entrant's first Ykkösliiga season only.

## Dev protocol

Training seed 2021; evaluation seasons 2022–2025 (pooled n = 598), expanding
season-blocked fits strictly before each season's first match. The dev harness
must not read 2026. Metrics are 1X2 LL, RPS, and OU2.5 LL. Baselines are
climatology (prior-seasons pooled outcome rates and OU2.5 rate) and the
specified base-rate OU baseline.

## Virgin protocol

Virgin = 2026 (n=135, complete; last match 2026-10-17), read ONCE and only for
dev-passing arms. Calibration uses mean predicted minus actual for home-win and
OU2.5-over rates, with SE = sd(p_i-y_i)/sqrt(n). Halves are presentation only,
using frozen goals_1h_share = 0.4462 (n=718 dev matches with goals).

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev 1X2 LL and RPS of an arm must beat climatology, and OU2.5 LL must beat the base-rate baseline, else the arm is dead. Virgin legs — (i) LL leg: arm's virgin 1X2 LL ≤ Gate Zero's AND ≤ climatology's; (ii) calibration leg: |mean predicted − actual| ≤ 1.0pp pooled for home-win rate and for OU2.5 over-rate, SEs reported; a breach within 1 SE of the boundary is recorded PROVISIONAL PASS, beyond it FAIL; (iii) per-season sign check on dev (arm LL ≤ Gate Zero LL in at least half the dev seasons) for the both-pass rule. Both-pass rule: if Gate Zero and a variant both pass all legs, the lower pooled virgin 1X2 LL ships; if only one passes, it ships; if none passes, G-YK verdict is FAIL and nothing ships.

Mechanical reading: an arm passes iff it survives the dev gate AND passes virgin legs (i)–(ii) (PROVISIONAL counts) AND, for variants, leg (iii); Gate Zero is exempt from (iii). Ties → simpler arm (Gate Zero, SHRINK, X2). If Gate Zero fails its dev gate, variants are moot, verdict FAIL, virgin NOT read.

## Outputs

`engine/goals/`; `results_dev.json` (+ CSV); `results_virgin.json`;
`fitted_params_virgin.json`; on PASS,
`predictions/g_yk_virgin_predictions.csv` with FT and 1H/2H presentation via
the frozen goals constant; and the final `reports/G_YK_VERDICT.md`.
