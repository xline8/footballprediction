#!/usr/bin/env python3
"""Recommendation #6: hierarchical partial pooling challenger.

Each monthly fit starts with the existing weighted Dixon–Coles estimates, then
shrinks team attack/defence toward a division mean and a global mean.  The
shrinkage strength is tuned on validation seasons and frozen for the holdout.
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
K_GRID = (5.0, 15.0, 30.0)
K_DIV = 10.0
K_HOME = 500.0


def _metrics(pairs):
    ll = brier = rps = 0.0
    for p, yi in pairs:
        ll -= math.log(max(p[yi], 1e-12))
        brier += sum((p[k] - (1 if k == yi else 0)) ** 2 for k in range(3))
        cdf = target = 0.0
        for k in range(3):
            cdf += p[k]
            target += 1.0 if k == yi else 0.0
            rps += (cdf - target) ** 2 / 2.0
    n = len(pairs)
    return {"n": n, "log_loss": ll / max(n, 1), "brier": brier / max(n, 1),
            "rps": rps / max(n, 1)}


def _shrink(models, histories, k_team):
    fitted = [models[d] for d in TOP5 if models[d].n_trained]
    if not fitted:
        return
    all_a = [v for m in fitted for v in m.a.values()]
    all_d = [v for m in fitted for v in m.d.values()]
    global_a = sum(all_a) / len(all_a) if all_a else 0.0
    global_d = sum(all_d) / len(all_d) if all_d else 0.0
    global_h = sum(m.h for m in fitted) / len(fitted)
    for div in TOP5:
        m = models[div]
        if not m.n_trained:
            continue
        div_a = sum(m.a.values()) / len(m.a) if m.a else global_a
        div_d = sum(m.d.values()) / len(m.d) if m.d else global_d
        n_div = len(m.a)
        target_a = (n_div * div_a + K_DIV * global_a) / (n_div + K_DIV)
        target_d = (n_div * div_d + K_DIV * global_d) / (n_div + K_DIV)
        counts = defaultdict(int)
        for h, a, *_ in histories[div][-model_v2.MAX_TRAIN:]:
            counts[h] += 1
            counts[a] += 1
        for team in set(m.a) | set(m.d):
            n = counts[team]
            target_team_a = 0.5 * target_a + 0.5 * global_a
            target_team_d = 0.5 * target_d + 0.5 * global_d
            m.a[team] = (n * m.a[team] + k_team * target_team_a) / (n + k_team)
            m.d[team] = (n * m.d[team] + k_team * target_team_d) / (n + k_team)
        n_matches = m.n_trained
        m.h = (n_matches * m.h + K_HOME * global_h) / (n_matches + K_HOME)


def run_hier(seasons, k_team):
    model_v2._ensure_loaded()
    matches = model_v2.matches
    by_div = {d: [] for d in TOP5}
    for i, m in enumerate(matches):
        by_div[m["div"]].append(i)
    periods = defaultdict(list)
    for i, m in enumerate(matches):
        if m["season"] in seasons:
            periods[m["date"].strftime("%Y-%m")].append(i)
    ptr = {d: 0 for d in TOP5}
    histories = {d: [] for d in TOP5}
    models = {d: model_v2.DC() for d in TOP5}
    pairs = []
    for period in sorted(periods):
        start = min(matches[i]["date"] for i in periods[period])
        for div in TOP5:
            lst = by_div[div]
            while ptr[div] < len(lst) and matches[lst[ptr[div]]]["date"] < start:
                histories[div].append(tuple(
                    matches[lst[ptr[div]]][k] for k in ("home", "away", "yh", "ya",
                                                        "xgh", "xga", "date")))
                ptr[div] += 1
            if histories[div]:
                models[div].fit(histories[div], start, 270.0)
        _shrink(models, histories, k_team)
        for i in periods[period]:
            m = matches[i]
            mdl = models[m["div"]]
            lh, la = mdl._lam(m["home"], m["away"])
            p = mdl.probs(lh, la)
            pairs.append(((p["ph"], p["pd"], p["pa"]), model_v2.YIDX[m["ftr"]]))
    return pairs


def run_baseline(seasons):
    model_v2.matches = []
    model_v2.by_div = None
    rows = model_v2.run_wf(set(seasons), 270, "m")
    return _metrics([((r["pr"]["ph"], r["pr"]["pd"], r["pr"]["pa"]),
                      model_v2.YIDX[r["ftr"]]) for r in rows])


def main():
    validation = {}
    for k in K_GRID:
        m = _metrics(run_hier(VAL_SEASONS, k))
        validation[k] = m
        print(f"validation k_team={k:.1f}: n={m['n']:,} "
              f"ll={m['log_loss']:.6f} brier={m['brier']:.6f}")
    best = min(K_GRID, key=lambda k: validation[k]["log_loss"])
    baseline = run_baseline(TEST_SEASONS)
    hier = _metrics(run_hier(TEST_SEASONS, best))
    print("selected k_team:", best)
    print("held-out baseline_50_50", baseline)
    print("held-out hierarchical", hier)


if __name__ == "__main__":
    main()
