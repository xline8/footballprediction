# PA-LPF features

X1 **ADOPTED**: goals-only blend fallback (688 usable rows). X2 mover offset
**DROPPED**: no sibling league; **X2-SHRINK ADOPTED**: G-J2 thin-history
treatment (shrink factor n/6 for teams with < 6 prior in-league matches).
EDA F4 measures exactly one such team per target season and all three are
n = 0 newcomers (Veraguas United, SD Atletico Nacional, Union Cocle), for
whom SHRINK ≡ Gate Zero — the arm is expected degenerate under this
season-blocked walk-forward (AM precedent); it stays pre-registered and
the degeneracy is verified from dev output, not assumed. X3 **DROPPED**:
set-play xG — no xG anywhere. X4 **DROPPED**: xG per shot — no shotmap.
X6 **DROPPED**: xGOT — no shotmap. X7 **DROPPED**: box touches — no
stats feed. X8 **DROPPED**: referee rate — referee text empty 735/735.
X9 **DROPPED**: possession / big chances — no stats feed.
X5 trailing target-rate means **ADOPTED as naive baseline only**: each
team's trailing-10 mean of the target (goals GF/GA here), min 6 of 10
matches carrying the stat else the league mean; Poisson lambdas from
those means; reported, not gated.

## 3. Rejected

R1 team 1H shares (per-season split-half r means .27/.07/.10/.07, pooled
team-season-block r −.03 — noise), R2 finishing (no xG denominator),
R4 on-target rate (no SOT), R6 lineup/absence, R8 formation/coach (data
absent), R9 standings/H2H (leakage), and R12 reds as target (rare-event
inventory, no production analogue).
