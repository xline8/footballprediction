#!/usr/bin/env python3
"""Recommendation #5: dynamic state-space attack/defence challenger.

This is an experiment-only online filter.  Team attack and defence states are
updated after each completed match with a Poisson residual; no future match is
used for a prediction.  The learning rate is selected on validation seasons
and frozen for the later holdout.
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
LR_GRID = (0.01, 0.02, 0.04, 0.08)


class DynamicState:
    def __init__(self, lr):
        self.lr = float(lr)
        self.attack = defaultdict(float)
        self.defence = defaultdict(float)
        self.count = defaultdict(int)
        self.home = 0.28
        self.rho = -0.07

    def lambdas(self, home, away):
        lh = math.exp(max(-3.0, min(2.0, self.attack[home] +
                                    self.defence[away] + self.home)))
        la = math.exp(max(-3.0, min(2.0, self.attack[away] +
                                    self.defence[home])))
        return lh, la

    def update(self, m):
        home, away = m["home"], m["away"]
        lh, la = self.lambdas(home, away)
        w = 0.5
        oh = (1.0 - w) * m["yh"] + w * (m["xgh"] if m["xgh"] is not None else m["yh"])
        oa = (1.0 - w) * m["ya"] + w * (m["xga"] if m["xga"] is not None else m["ya"])
        gh, ga = oh - lh, oa - la
        # A process-noise floor keeps newly promoted/changed teams adaptable;
        # experienced teams receive a smaller update.
        eta_h = self.lr * (0.25 + 0.75 / math.sqrt(1.0 + self.count[home]))
        eta_a = self.lr * (0.25 + 0.75 / math.sqrt(1.0 + self.count[away]))
        self.attack[home] += eta_h * gh
        self.defence[away] -= eta_h * gh
        self.attack[away] += eta_a * ga
        self.defence[home] -= eta_a * ga
        self.home += self.lr * 0.08 * (gh + ga)
        self.home = max(-0.1, min(0.8, self.home))
        for team in (home, away):
            self.attack[team] = max(-2.0, min(2.0, self.attack[team]))
            self.defence[team] = max(-2.0, min(2.0, self.defence[team]))
            self.count[team] += 1


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


def run_dynamic(seasons, lr):
    model_v2._ensure_loaded()
    states = {d: DynamicState(lr) for d in TOP5}
    prob = model_v2.DC()
    pairs = []
    i = 0
    matches = model_v2.matches
    while i < len(matches):
        j = i + 1
        day = matches[i]["date"]
        while j < len(matches) and matches[j]["date"] == day:
            j += 1
        # Predict every fixture from the state before this day.
        for m in matches[i:j]:
            if m["season"] not in seasons:
                continue
            state = states[m["div"]]
            lh, la = state.lambdas(m["home"], m["away"])
            pr = prob.probs(lh, la)
            pairs.append(((pr["ph"], pr["pd"], pr["pa"]),
                          model_v2.YIDX[m["ftr"]]))
        # Update only after all predictions on this date.
        for m in matches[i:j]:
            states[m["div"]].update(m)
        i = j
    return pairs


def run_baseline(seasons):
    model_v2.matches = []
    model_v2.by_div = None
    rows = model_v2.run_wf(set(seasons), 270, "m")
    pairs = [((r["pr"]["ph"], r["pr"]["pd"], r["pr"]["pa"]),
              model_v2.YIDX[r["ftr"]]) for r in rows]
    return _metrics(pairs)


def main():
    validation = {}
    for lr in LR_GRID:
        m = _metrics(run_dynamic(VAL_SEASONS, lr))
        validation[lr] = m
        print(f"validation lr={lr:.3f}: n={m['n']:,} "
              f"ll={m['log_loss']:.6f} brier={m['brier']:.6f}")
    best = min(LR_GRID, key=lambda lr: validation[lr]["log_loss"])
    print("selected learning rate:", best)
    baseline = run_baseline(TEST_SEASONS)
    dynamic = _metrics(run_dynamic(TEST_SEASONS, best))
    print("held-out baseline_50_50", baseline)
    print("held-out dynamic_state_space", dynamic)


if __name__ == "__main__":
    main()
