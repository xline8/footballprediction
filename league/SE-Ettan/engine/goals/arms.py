"""Arms for G-SE (see PREREG_G_SE.md and dc.py).

GateZero: Dixon-Coles goals-only, unmodified.
SHRINK: Gate Zero plus the sanctioned G-J2-lesson change, defined
verbatim from PREREG_G_FI.md: at prediction time a team with n < 6
prior in-league matches has a *= n/6, d *= n/6, where n is the number
of matches the team played in the training data strictly before the
predicted season (all matches in that season's expanding fit); n >= 6
-> no change; n = 0 -> exponents 0.0 (identical to the league-mean
fallback). The scaling applies to both the attack and the defence
exponent, for home and away teams alike.
NO ENTRANT arm: X2 rejected (EDA F4).
"""
from dc import SHRINK_MIN_MATCHES, match_counts, shrink_factor  # noqa: F401

ARMS = ["GateZero", "SHRINK"]
