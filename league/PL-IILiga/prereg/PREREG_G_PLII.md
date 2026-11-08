# Pre-registration — G-PL-II (Poland II Liga goals model)

Frozen: 2026-11-10, before any fitting. Branch `build/pl-ii-liga`.
Design authority: `analysis/MODEL_DESIGN.md`; evidence:
`analysis/EDA.md`. Reference architecture: production `model_v2.py`,
`hl=270`, with the parent G-PL and sibling G-GR2 precedents. FotMob
league_id is 8935. Calibration is actual − predicted everywhere.

## Reference architecture

Dixon–Coles copied from production: iterative multiplicative updates,
14 sweeps, damping 0.7, +0.25 smoothing, fitted home advantage (init
0.28), attack/defence per FotMob team ID (init 0), MAXG=10, production
tau correction, and rho selected from (0, −0.05, −0.10, −0.15) by weighted
goals log-likelihood. Time decay is `0.5 ** (age_days / 270)` and the
blend weight is 0.5. xG fallback fires on every payload because xG exists
in zero of 1,679 rows. Fit scope for target season S: all PL-II matches
dated strictly before the first match date of S (expanding,
season-blocked). Teams unseen in training start at the league mean
(a = d = 0). Team identity is the FotMob team id. All phases and B teams are ordinary rows.

## Arms

1. Gate Zero — the reference goals-only DC.
2. SHRINK — the sanctioned G-J2 lesson. At prediction time only, for a
team with fewer than six prior in-league training matches, multiply fitted
attack and defence by n/6; n=0 gives zero ratings. Nothing else changes.

There is no X2 arm. Movers are measured in EDA but the dev gaps are small
and the from-below sign is opposite to a promotion penalty. No other arm
survives the Phase A feature gate.

## Dev protocol

Season-blocked walk-forward, seed 2021/2022; evaluate 2022/2023,
2023/2024, and 2024/2025, pooled scored n=927. Report per-arm and pooled
1X2 log loss, RPS, and OU2.5 log loss. Baselines: climatology — for
target season S, the pooled outcome rates + OU2.5 over-rate of all
seasons strictly before S. The Phase B harness must not read
2025/2026 or 2026/2027 rows at all. Primary line: OU2.5.

## Virgin protocol

Virgin primary is 2025/2026, n=309 complete, read once only after dev
results are frozen. Fit uses matches strictly before that season’s first
match date. 2026/2027, n=134 through 2026-11-08, is confirmatory only and
is not read in this build.

## GATE LEGS

Dev gate — pooled dev 1X2 LL and RPS of an arm must beat climatology, and OU2.5 LL must beat the base-rate baseline, else the arm is dead. Virgin legs — (i) LL leg: arm's virgin 1X2 LL ≤ Gate Zero's AND ≤ climatology's; (ii) calibration leg: |actual − mean predicted| ≤ 1.0pp pooled for home-win rate and for OU2.5 over-rate, SEs reported; a breach within 1 SE of the boundary is recorded PROVISIONAL PASS, beyond it FAIL; (iii) per-season sign check on dev (arm LL ≤ Gate Zero LL in at least half the dev seasons) for the both-pass rule. Both-pass rule: if Gate Zero and a variant both pass all legs, the lower pooled virgin 1X2 LL ships; if only one passes, it ships; if none passes, G-PL-II verdict is FAIL and nothing ships.

Mechanical reading: an arm passes iff it survives the dev gate AND
passes virgin legs (i)–(ii) (PROVISIONAL counts, recorded as such) AND,
for variant arms, leg (iii); Gate Zero is exempt from (iii). Ties go to
the simpler arm. If Gate Zero fails its own dev gate, variants are moot,
verdict FAIL, virgin NOT read.

## Outputs

Phase B owns the engine, dev/virgin results, fitted parameters, and any
predictions under `league/PL-IILiga/`. This prereg is committed before any
fitting. No production code, cron, reports, or `league/PROGRAM_STATUS.md`
is changed in Phase A.
