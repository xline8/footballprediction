# Model design

## Candidate feasibility

G-KZ is the only candidate. S is not buildable because no SOT target
exists in any payload; C is not buildable because no corners target
exists; T is not buildable because no total-shots target exists; K is
not buildable because there are zero plain Yellow events and only
rare Red/YellowRed events (127 + 68 in dev, about 0.22 card events per
finished match in dev), which the production cards design excludes.

## G-KZ

Reference is the production Dixon–Coles `model_v2.py` pattern:
goals-only observation, `hl=270`, rho grid, and fitted home
advantage. Arms are Gate Zero; and SHRINK, which multiplies attack
and defence ratings by `n/6` for teams with 1–5 prior in-league
matches and leaves unseen teams at the mean (the sanctioned G-J2
post-mortem arm). No X2 arm: no Kazakh sibling league exists, so no
mover prior can be estimated (brief; EDA F4 records the entrant
pattern descriptively only). EDA F13 shows zero teams fall in the
1–5 prior-match band at any target-season start, so SHRINK is
expected to be identical to Gate Zero; the verdict verifies that
from the results file.

Training is season-blocked walk-forward: 2021 is the seed (182
finished), evaluation is 2022–2025 (`n=702`), and 2026 is the virgin
(`n=240`, complete season, Mar 7 – Oct 31). The dev gate requires
pooled 1X2 log loss and RPS to beat climatology and OU2.5 log loss
to beat the base-rate baseline. Virgin legs are the LL leg, pooled
home-win and OU2.5 calibration within 1.0 percentage point (within
1 SE is provisional), and a per-season sign check for variants;
both-pass rule applies. Gate Zero failure makes variants moot and
leaves virgin unread. Halves are FT plus 1H/2H presentation using
only the frozen goals 1H constant 0.4539; no other halves constants
exist.
