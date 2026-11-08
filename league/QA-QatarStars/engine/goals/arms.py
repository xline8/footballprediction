"""Arms for G-QA (see PREREG_G_QA and dc.py).

GateZero: Dixon-Coles goals-only, unmodified.
ENTRANT: Gate Zero plus frozen entrant-season shifts applied at
prediction time to a team absent from the immediately preceding
season: attack exponent -0.2391, defence exponent -0.1947
(EDA F4: dev entrant offsets GF -0.3561 / GA +0.3598 vs dev scored
mean team goals 1.6742/match; defence exponent is reduced because
a worse defence raises the opponent's expected goals).
"""
from dc import ATT_SHIFT, DEF_SHIFT  # noqa: F401

ARMS = ["GateZero", "ENTRANT"]
