"""Unit tests for the project's core math.

These tests are data-free on purpose: they exercise pure functions with
fixed inputs, so they run in CI on a fresh checkout where the generated
data files (gitignored) do not exist. The data-dependent smoke tests stay
in test_core.py and run in the full local environment.

Run with pytest (`python -m pytest tests/ -q`) or directly
(`python tests/test_units.py`).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backtest_picks import _fair_probs
from model_v2 import DC
from predict_cups import p_adv
from slip_recommender import _search
from ta_model import fair_odds

TOL = 1e-6


# ------------------------------------------------------------ de-vig (Shin)

def test_fair_probs_mult_sums_to_one():
    p = _fair_probs((1.72, 4.37, 4.89), "mult")
    assert abs(sum(p) - 1.0) < 1e-9
    assert all(0.0 < x < 1.0 for x in p)


def test_fair_probs_shin_golden():
    # Book from a real market_compare row (Frosinone vs Lecce, 2026-10-29).
    p = _fair_probs((1.72, 4.37, 4.89), "shin")
    assert abs(sum(p) - 1.0) < 1e-9
    assert abs(p[0] - 0.57560) < 1e-4
    assert abs(p[1] - 0.22432) < 1e-4
    assert abs(p[2] - 0.20008) < 1e-4


def test_shin_moves_prob_from_longshot_to_favourite():
    # Shin's method, unlike proportional de-vigging, shifts probability
    # mass from longshots toward the favourite.
    o = (1.72, 4.37, 4.89)
    mult = _fair_probs(o, "mult")
    shin = _fair_probs(o, "shin")
    assert shin[0] > mult[0]
    assert shin[2] < mult[2]


# ------------------------------------------------------------ Dixon-Coles

def test_dc_probs_sum_to_one():
    pr = DC().probs(2.0, 1.0)
    assert abs(pr["ph"] + pr["pd"] + pr["pa"] - 1.0) < 1e-9
    for k in ("ph", "pd", "pa", "over", "over15", "over35", "btts"):
        assert 0.0 <= pr[k] <= 1.0


def test_dc_probs_golden_and_monotone():
    pr = DC().probs(2.0, 1.0)
    assert abs(pr["ph"] - 0.5987) < 1e-3
    assert abs(pr["over"] - 0.5768) < 1e-3
    stronger = DC().probs(2.6, 1.0)
    assert stronger["ph"] > pr["ph"]


# ------------------------------------------------------------ p_adv (cups)

def test_p_adv_golden_bayern_like():
    # Verified against the live system on 2026-10-29 (Bayern-like tie).
    pr = DC().probs(2.29, 0.747)
    adv_h, adv_a = p_adv(pr["ph"], pr["pd"], pr["pa"], 2.29, 0.747)
    assert abs(adv_h - 0.87044) < 1e-4
    assert abs(adv_h + adv_a - 1.0) < 1e-9


def test_p_adv_invariants():
    pr = DC().probs(1.4, 1.1)
    adv_h, adv_a = p_adv(pr["ph"], pr["pd"], pr["pa"], 1.4, 1.1)
    assert abs(adv_h + adv_a - 1.0) < 1e-9
    # Advancing can only be at least as likely as winning in 90 minutes,
    # and never more likely than not losing in 90 minutes.
    assert adv_h >= pr["ph"] - 1e-12
    assert adv_h <= 1.0 - pr["pa"] + 1e-9
    assert adv_a >= pr["pa"] - 1e-12


def test_p_adv_symmetric_tie_is_fifty_fifty():
    adv_h, adv_a = p_adv(0.4, 0.2, 0.4, 1.3, 1.3)
    assert abs(adv_h - 0.5) < 1e-9
    assert abs(adv_a - 0.5) < 1e-9


# ------------------------------------------------------------ slip search

def _leg(match, date, o, pm):
    return {"match": match, "date": date, "home": match, "away": "x",
            "comp": "", "market": "DC", "line": "", "sel": "1X",
            "o": o, "pm": pm}


def test_slip_search_picks_highest_joint_in_band():
    by_match = {
        "A": [_leg("A", "2026-10-29", 1.30, 0.80),
              _leg("A", "2026-10-29", 2.60, 0.45)],
        "B": [_leg("B", "2026-10-29", 1.50, 0.70),
              _leg("B", "2026-10-29", 1.45, 0.72)],
        "C": [_leg("C", "2026-10-29", 1.90, 0.55)],
    }
    best_in, _ = _search(by_match, 2, 4, 1.85, 2.15, 2.0)
    assert best_in is not None
    tot, jp, ev, legs = best_in
    # A@1.30 x B@1.45 = 1.885, joint 0.576 beats A@1.30 x B@1.50 (0.56).
    assert abs(tot - 1.885) < 1e-9
    assert abs(jp - 0.576) < 1e-9
    assert len({l["match"] for l in legs}) == len(legs)  # one leg per match


def test_slip_search_fallback_is_nearest_to_target():
    by_match = {
        "A": [_leg("A", "2026-10-29", 1.10, 0.90)],
        "B": [_leg("B", "2026-10-29", 1.10, 0.90)],
    }
    best_in, best_near = _search(by_match, 2, 4, 1.85, 2.15, 2.0)
    assert best_in is None  # 1.21 cannot reach the band
    assert best_near is not None
    assert abs(best_near[0] - 1.21) < 1e-9


# ------------------------------------------------------------ ta fair odds

def test_fair_odds_with_push():
    # (1 - p_push) / p_win; a push refunds the stake.
    assert abs(fair_odds(0.6, 0.1) - 1.5) < 1e-12
    assert fair_odds(0.0, 0.5) == 999.0


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items())
           if k.startswith("test_") and callable(v)]
    for fn in fns:
        fn()
        print(f"PASS {fn.__name__}")
    print(f"{len(fns)} unit tests passed")
