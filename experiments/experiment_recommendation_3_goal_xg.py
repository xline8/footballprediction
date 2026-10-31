#!/usr/bin/env python3
"""Recommendation #3: learn the goals/xG blend weight.

The validation seasons select a small grid of xG weights.  A single global
weight and a league-specific weight (shrunk back toward the global value) are
then frozen before evaluating the later test seasons.  This keeps the
experiment nested and prevents test-season tuning.
"""
from __future__ import annotations

import importlib
import math
import os
import sys
from collections import defaultdict

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE not in sys.path:
    sys.path.insert(0, BASE)

os.environ["FOOTBALL_XG_SOURCE"] = "native_priority"
os.environ["FOOTBALL_DC_FIT_MODE"] = "blend"

import features  # noqa: E402
import model_v2  # noqa: E402

features = importlib.reload(features)
model_v2 = importlib.reload(model_v2)

TOP5 = tuple(model_v2.TOP5)
VAL_SEASONS = {"2019/20", "2020/21"}
TEST_SEASONS = {"2021/22", "2022/23", "2023/24", "2024/25", "2025/26"}
WEIGHTS = (0.0, 0.25, 0.5, 0.75, 1.0)


def _reset():
    model_v2.matches = []
    model_v2.by_div = None


def metrics(rows):
    ll = brier = rps = 0.0
    by_div = defaultdict(lambda: [0, 0.0, 0.0])
    for r in rows:
        p = (r["pr"]["ph"], r["pr"]["pd"], r["pr"]["pa"])
        yi = model_v2.YIDX[r["ftr"]]
        ll_i = -math.log(max(p[yi], 1e-12))
        b_i = sum((p[k] - (1.0 if k == yi else 0.0)) ** 2
                  for k in range(3))
        cdf = target = 0.0
        r_i = 0.0
        for k in range(3):
            cdf += p[k]
            target += 1.0 if k == yi else 0.0
            r_i += (cdf - target) ** 2
        ll += ll_i
        brier += b_i
        rps += r_i / 2.0
        bucket = by_div[r["div"]]
        bucket[0] += 1
        bucket[1] += ll_i
        bucket[2] += b_i
    n = len(rows)
    return {
        "n": n,
        "log_loss": ll / max(n, 1),
        "brier": brier / max(n, 1),
        "rps": rps / max(n, 1),
        "per_div": {
            d: {"n": v[0], "log_loss": v[1] / v[0],
                "brier": v[2] / v[0]}
            for d, v in sorted(by_div.items())
        },
    }


def run(seasons, weights):
    _reset()
    rows = model_v2.run_wf(set(seasons), 270, "m", xg_weights=weights)
    return rows, metrics(rows)


def main():
    validation = {}
    for w in WEIGHTS:
        rows, m = run(VAL_SEASONS, {d: w for d in TOP5})
        validation[w] = m
        print(f"validation weight={w:.2f}: n={m['n']:,} "
              f"ll={m['log_loss']:.6f} brier={m['brier']:.6f}")

    global_weight = min(WEIGHTS, key=lambda w: validation[w]["log_loss"])
    per_div_weight = {}
    for div in TOP5:
        per_div_weight[div] = min(
            WEIGHTS,
            key=lambda w: validation[w]["per_div"].get(
                div, {"log_loss": float("inf")})["log_loss"])
    # Empirical-Bayes-style shrinkage: validation has roughly two seasons per
    # division, so do not let a small per-league winner move all the way.
    k = 1000.0
    shrunk = {}
    for div in TOP5:
        n = validation[per_div_weight[div]]["per_div"].get(div, {}).get("n", 0)
        shrunk[div] = (n * per_div_weight[div] + k * global_weight) / (n + k)

    print("selected global weight:", global_weight)
    print("selected per-division weights:", per_div_weight)
    print("shrunk weights:", {d: round(v, 4) for d, v in shrunk.items()})

    variants = {
        "goals": {d: 0.0 for d in TOP5},
        "fixed_50_50": {d: 0.5 for d in TOP5},
        "global_selected": {d: global_weight for d in TOP5},
        "league_shrunk": shrunk,
    }
    print("\nheld-out test seasons")
    for name, weights in variants.items():
        _, m = run(TEST_SEASONS, weights)
        print(name, {k: round(m[k], 6) for k in ("n", "log_loss", "brier", "rps")})


if __name__ == "__main__":
    main()
