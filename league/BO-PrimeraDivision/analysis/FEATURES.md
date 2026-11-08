# Step 5 — Features: BO-PrimeraDivision

Decisions use only the measured EDA and the stated window discipline.

| feature | decision | evidence / reason |
|---|---|---|
| X1 goals-only | ADOPTED | No xG exists; score-derived goals are complete in all 1,603 rows. |
| X2 parent-tier mover prior | DROPPED | No Bolivian second-tier corpus exists. |
| X3 xG | DROPPED | 0 matches with an xG key. |
| X4 shotmap/xGOT | DROPPED | 0 non-empty shotmaps. |
| X5 trailing stats | ADOPTED | SOT/corners/shots/cards exist in all 439 stats-era rows; trailing-10 with min-6 is valid for count markets. |
| X6 shot quality | DROPPED | No shotmap or xGOT field. |
| X7 box touches | ADOPTED (C-BO variant arm) | 2025 split-half r=.703 for, .408 against (n=16 teams); trailing means with the min-6 rule. The against-trait is weak, so this is a variant arm gated against Gate Zero, never the base. |
| X8 referee | DROPPED | 0 named in 2021–2024; only 16.7% (40/240) in 2025 and 39.7% (79/199) in 2026, with no dev-era signal. |
| X9 territory/chance | ADOPTED for C-BO Gate Zero | Possession and big chances are present throughout the in-era feed; the possession split-half r=.775 supports the Gate Zero input. |
| SHRINK | ADOPTED for G-BO variant | Sanctioned G-J2 lesson: shrink unseen/new-team ratings to a prior to limit opener extremes. |

Rejected R1–R13 are the J1/PY rejected alternatives: xG/xGOT/shotmap and shot-quality blends (R1–R3), parent-tier mover priors (R4), referee effects (R5), per-match half-share features (R6), raw stats-era card feed as target (R7), post-cutoff 2026 feature selection (R8), league-name identity instead of IDs (R9), playoff pooling (R10), fabricated pre-2025 stats (R11), same-match leakage (R12), and post-hoc rescue arms (R13). The measured values above explain the Bolivia-specific entries.

Frozen constants are recorded in EDA and are presentation-only. Bolivia-specific note: the on-target rate is a real team trait here (split-half r=0.613, 2025, n=16), unlike J1 (r=0.06, NOISE) — so S-BO's RS arm is a robustness arm expected to lose to Gate Zero, and it ships only if it beats Gate Zero on dev and virgin. Trailing finishing (goals/shot, r=0.261) stays rejected.
