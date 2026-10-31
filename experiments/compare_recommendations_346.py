#!/usr/bin/env python3
"""Compare recommendations #3, #4 and #6 against their baselines.

All DC rows use the same native-priority xG source and 2021/22–2025/26
holdout.  The shots/SOT challenger is a T3 model, so it is compared with its
own T3 baseline; it must not be interpreted as a direct replacement for the
DC probability engine.
"""
from __future__ import annotations

import json
import os
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE not in sys.path:
    sys.path.insert(0, BASE)

from experiments import experiment_recommendation_3_goal_xg as r3
from experiments import experiment_recommendation_4_shots_sot as r4
from experiments import experiment_recommendation_6_hierarchical as r6

TOP5 = tuple(r3.TOP5)
VAL_SEASONS = set(r3.VAL_SEASONS)
TEST_SEASONS = set(r3.TEST_SEASONS)


def select_goal_xg_weights():
    validation = {}
    for w in r3.WEIGHTS:
        _, m = r3.run(VAL_SEASONS, {d: w for d in TOP5})
        validation[w] = m
    global_weight = min(r3.WEIGHTS, key=lambda w: validation[w]["log_loss"])
    per_div = {
        d: min(r3.WEIGHTS, key=lambda w: validation[w]["per_div"][d]["log_loss"])
        for d in TOP5
    }
    shrunk = {}
    for d in TOP5:
        n = validation[per_div[d]]["per_div"][d]["n"]
        shrunk[d] = (n * per_div[d] + 1000.0 * global_weight) / (n + 1000.0)
    return global_weight, shrunk


def main():
    # #3: fixed production blend versus nested global/league weight selection.
    _, dc_baseline = r3.run(TEST_SEASONS, {d: 0.5 for d in TOP5})
    global_weight, shrunk_weights = select_goal_xg_weights()
    _, dc_goal_xg = r3.run(TEST_SEASONS,
                           {d: global_weight for d in TOP5})
    _, dc_goal_xg_shrunk = r3.run(TEST_SEASONS, shrunk_weights)

    # #6: the same weighted DC baseline and the pooled challenger.
    dc_hier_baseline = r6.run_baseline(TEST_SEASONS)
    # k_team=5 is selected by the validation run documented in recommendation #6.
    dc_hier = r6._metrics(r6.run_hier(TEST_SEASONS, 5.0))

    # #4: T3 baseline and the shots/SOT + proxy-xG challenger.
    t3 = r4.evaluate(TEST_SEASONS)

    result = {
        "holdout": sorted(TEST_SEASONS),
        "dc": {
            "baseline_fixed_50_50": dc_baseline,
            "goal_xg_global": dc_goal_xg,
            "goal_xg_league_shrunk": dc_goal_xg_shrunk,
            "hierarchical_baseline": dc_hier_baseline,
            "hierarchical": dc_hier,
            "selected_global_weight": global_weight,
            "selected_shrunk_weights": shrunk_weights,
        },
        "t3": {"baseline": t3["base"], "shots_sot_proxy_xg": t3["shots_sot"],
               "rows": t3["rows"], "shot_labels": t3["shot_labels"]},
    }
    print(json.dumps(result, indent=2, sort_keys=True, default=float))


if __name__ == "__main__":
    main()
