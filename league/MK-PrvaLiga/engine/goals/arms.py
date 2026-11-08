"""The preregistered G-MK arms."""
from dc import shrink_factor, SHRINK_MIN_MATCHES

ARMS = ["GateZero", "SHRINK"]


def synthetic_unit_check():
    assert shrink_factor({123: 3}, 123) == 0.5


synthetic_unit_check()
