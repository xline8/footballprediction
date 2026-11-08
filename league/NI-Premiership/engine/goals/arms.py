"""The two preregistered G-NI arms."""
from dc import SHRINK_MIN_MATCHES, match_counts, shrink_factor

ARMS = ["GateZero", "SHRINK"]


def synthetic_unit_check():
    """The sanctioned scaling is active: three prior matches means factor 0.5."""
    assert shrink_factor({123: 3}, 123) == 0.5


synthetic_unit_check()
