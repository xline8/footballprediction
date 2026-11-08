# Pre-registration — G-PT (Liga Portugal goals model)

Frozen: 2026-11-09, before any fitting. Branch `build/pt-liga`.
Design authority: `league/PT-LigaPortugal/analysis/MODEL_DESIGN.md`
(G-PT) + FEATURES.md (X1 adopted; X2, X3 dropped with reasons).
Reference: production Dixon-Coles pattern as in the J1 goals engine
(`league/J1/engine/goals/dc.py`): iterative multiplicative fit, 14
sweeps, damping 0.7, +0.25 smoothing, home advantage fitted (init
0.28), rho chosen per fit from (0.0, -0.05, -0.10, -0.15) by
weighted goals LL, score matrix to MAXG=10 with tau correction.
Observation: blend 0.5*goals + 0.5*xG (xG present in every match of
this corpus, so the goals-only fallback never triggers). Decay:
w = 0.5**((cutoff - date).days/270), frozen. Fit scope for target
season S: all matches dated before the first match of S. Teams
unseen in training start at the league mean.

## Arms

1. **Gate Zero** — the unmodified reference above.
2. **Arm SHRINK** — Gate Zero, then any team with <15 matches in
   the training window has its fitted attack and defence ratings
   scaled by 0.5 (a[t] *= 0.5, d[t] *= 0.5) before predicting
   season S. This is the template-sanctioned response to the G-J2
   post-mortem (extreme lambdas for 1-2-match teams in season
   openers), pre-registered here before any fitting. No other
   difference.

## Protocols

Dev = expanding season-blocked walk-forward: for target season S,
fit on all matches of seasons strictly before S; evaluation seasons
2022/2023, 2023/2024, 2024/2025, 2025/2026 (pooled n=1,224). The dev
harness must not read 2026/2027 rows at all. Virgin = 2026/2027
(n=98, TRANSITIONAL — season in progress; confirmatory read at
season end reserved), read ONCE after dev results are frozen, and
only for arms that pass the dev gate. Calibration: mean predicted
P(over primary line) - actual over rate; SE = sd(pred_i - y_i)/sqrt(n).
Halves in outputs are presentation only via the frozen PT constants
(goals 0.443, SOT 0.449, corners 0.471, yellows 0.331, shots 0.456).
Metrics: per season and pooled — 1X2 LL, RPS (H/D/A), OU2.5 LL.
Baseline: climatology = pooled outcome rates and OU2.5 over-rate
of all seasons strictly before S.
Virgin calibration: home-win rate and OU2.5 over-rate, per arm.

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev 1X2 LL and RPS of an arm must beat
climatology, and OU2.5 LL must beat the base-rate baseline, else
the arm is dead and does NOT read the virgin. Virgin legs —
(i) LL leg: arm's virgin 1X2 LL <= Gate Zero's AND <= climatology's;
(ii) calibration leg: |mean predicted - actual| <= 1.0pp pooled for
home-win rate and for OU2.5 over-rate, SEs reported; a breach within
1 SE of the boundary is recorded PROVISIONAL PASS, beyond it FAIL;
(iii) per-season sign check on dev (arm LL <= Gate Zero LL in at
least half the dev seasons) for the both-pass rule. Both-pass rule:
if Gate Zero and a variant both pass all legs, the lower pooled
virgin 1X2 LL ships; if only one passes, it ships; if none passes,
verdict is FAIL and nothing ships. Gate Zero is exempt from (iii);
ties go to Gate Zero.

## Outputs

Engine `league/PT-LigaPortugal/engine/goals/`; results_dev.json
(+CSV), results_virgin.json, fitted_params_virgin.json; virgin
predictions `league/PT-LigaPortugal/predictions/g_pt_virgin_predictions.csv`
(shipped arm; Gate Zero's if none ships, labelled in the verdict)
with FT 1X2/OU/BTTS and 1H/2H OU lines via frozen goals constant
0.443; verdict `league/PT-LigaPortugal/reports/G_PT_VERDICT.md`.
Production code untouched. No push, no merge.
