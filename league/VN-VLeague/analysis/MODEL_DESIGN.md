# Model design

## Candidate feasibility

G-VN is the only candidate. S is not buildable because no SOT target
exists in any payload; C is not buildable because no corners target
exists; T is not buildable because no total-shots target exists; K is
not buildable because there are **zero plain-Yellow events in
2021–2023/2024 (0/556 matches)** and yellows appear only from
2024/2025 — no dev season contains the target, so no valid virgin
window contains it either. See `prereg/PREREG_NOT_BUILDABLE_SCKT_VN.md`
(frozen in Phase A, before any fitting).

## G-VN

Reference is the production Dixon–Coles `model_v2.py` pattern:
goals-only observation, `hl=270`, rho grid, and fitted home
advantage. Arms are Gate Zero; and SHRINK, which multiplies attack
and defence ratings by `n/6` for teams with 1–5 prior in-league
matches and leaves unseen teams at the mean (the sanctioned G-J2
post-mortem arm). No X2 arm: no Vietnamese sibling league exists, so
no mover prior can be estimated (brief; EDA F4 records the entrant
pattern descriptively only). EDA F13 shows zero teams fall in the
1–5 prior-match band at any target-season start, so SHRINK is
expected to be identical to Gate Zero; the verdict verifies that
from the results file.

Training is season-blocked walk-forward: 2021 is the seed (84
finished), evaluation is 2022, 2023, 2023/2024, 2024/2025 (n = 654),
and 2025/2026 is the virgin (n = 182, complete season, 2025-08-15 –
2026-06-07). The dev gate requires pooled 1X2 log loss and RPS to
beat climatology and OU2.5 log loss to beat the base-rate baseline.
Virgin legs are the LL leg, pooled home-win and OU2.5 calibration
within 1.0 percentage point (within 1 SE is provisional), and a
per-season sign check for variants; both-pass rule applies. Gate Zero
failure makes variants moot and leaves virgin unread. Halves are FT
plus 1H/2H presentation using only the frozen goals constant 0.4468;
no other halves constants exist.

2026/2027 (in progress, 49 matches through 2026-11-08) is reserved
for a season-end confirmatory read after the season completes; it is
not a second virgin window and no gate depends on it.
