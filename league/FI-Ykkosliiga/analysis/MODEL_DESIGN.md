# Step 6 — Model Design: FI-Ykkosliiga

No model is fit in this brief.

## Feasibility

| Candidate | Feasibility | Evidence |
|---|---|---|
| G-YK | BUILDABLE | FT goals target exists in all 895 rows; virgin 2026 is complete, n=135. |
| S-YK | NOT BUILDABLE | Stats non-null 0/895; no target in dev or virgin. |
| C-YK | NOT BUILDABLE | Stats non-null 0/895; no target in dev or virgin. |
| T-YK | NOT BUILDABLE | Stats non-null 0/895 and shotmap empty 895/895; no target in dev or virgin. |
| K-YK | NOT BUILDABLE | Card target is near-complete only in virgin 2026 (134/135 matches); 2021–2025 coverage is 11.6%–19.3%, so no valid season-blocked dev window. |

The cards break is a feed-coverage break, not a model result. S/C/T/K are not
preregistered; this feasibility record is the only statement about them.

## Goals candidate

| Candidate | Reference | Variant arms | Warm-up | Dev scored | Primary line |
|---|---|---|---|---|---|
| G-YK | Production Dixon-Coles pattern: 14 sweeps, damping 0.7, +0.25 smoothing, home init 0.28, MAXG=10, production tau, rho grid (0.0,-0.05,-0.10,-0.15) by goals LL, decay HL=270 days | SHRINK; X2 = SHRINK + entrant offset | 2021 | 2022–2025 pooled n=598 | OU 2.5 plus 1X2 LL/RPS |

The observation is X1 goals-only. SHRINK uses the G-J2 lesson: at prediction
time a team with n<6 prior in-league matches has a*=n/6 and d*=n/6. X2 pools
all entrant origins and directions identified by team ids across league_ids 51
and 251. It requires at least 3 completed entrant transitions before the
predicted season, clamps multipliers to [0.8, 1.25], and applies them only in
the entrant's first Ykkösliiga season. The mixed-origin caveat is explicit:
the entrant arm combines relegated Veikkausliiga clubs with tier-3/unknown
promotees in one offset.

Dev is season-blocked, expanding, and uses no 2026 rows. Virgin 2026 is n=135
and is read once only for dev-passing arms. Gate Zero dev FAIL makes variants
moot and leaves virgin unread. Gate legs, calibration, sign check, tie rule,
and output names are frozen verbatim in `prereg/PREREG_G_YK.md`.
