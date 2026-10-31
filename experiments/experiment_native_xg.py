"""Compare native football-data xG with the existing Understat map.

This is deliberately an experiment-only entry point.  It does not rewrite
model state, prediction CSVs, or the production config.  Run it with:

    python experiments/experiment_native_xg.py

The current-season sample is small, so the output is evidence for a follow-up
decision, not an automatic production promotion.
"""
from __future__ import annotations

import importlib
import math
import os
import sys
from collections import defaultdict

import numpy as np

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE not in sys.path:
    sys.path.insert(0, BASE)


SEASON = "2026/27"
SOURCE_VARIANTS = ("understat", "native_priority")


def _reload_for(source: str, feature_mode: str = "base"):
    os.environ["FOOTBALL_XG_SOURCE"] = source
    os.environ["FOOTBALL_T3_FEATURES"] = feature_mode

    import features
    import model_features_1x2 as mf
    import model_v2

    importlib.reload(features)
    importlib.reload(mf)
    importlib.reload(model_v2)
    return features, mf, model_v2


def _dc_metrics(rows, model_v2):
    n = len(rows)
    ll = brier = rps = 0.0
    per_div = defaultdict(lambda: [0, 0.0])
    for r in rows:
        p = (r["pr"]["ph"], r["pr"]["pd"], r["pr"]["pa"])
        yi = model_v2.YIDX[r["ftr"]]
        ll_i = -math.log(max(p[yi], 1e-12))
        ll += ll_i
        brier += sum((p[k] - (1.0 if k == yi else 0.0)) ** 2
                      for k in range(3))
        cdf = 0.0
        target = 0.0
        for k in range(3):
            cdf += p[k]
            target += 1.0 if k == yi else 0.0
            rps += (cdf - target) ** 2
        per_div[r["div"]][0] += 1
        per_div[r["div"]][1] += ll_i
    return {
        "n": n,
        "log_loss": ll / max(n, 1),
        "brier": brier / max(n, 1),
        "rps": rps / max(2 * n, 1),
        "per_div_log_loss": {
            div: total / n_div for div, (n_div, total) in sorted(per_div.items())
        },
    }


def run_dc(source: str):
    features, _, model_v2 = _reload_for(source)
    model_v2.matches = []
    model_v2.by_div = None
    rows = model_v2.run_wf({SEASON}, 270, "m")
    return _dc_metrics(rows, model_v2), len(features._load_xg_map())


def run_t3(source: str, feature_mode: str):
    features, mf, _ = _reload_for(source, feature_mode)
    # Evaluate only the current-season tail, but train each month on the full
    # history before it.  This preserves the expanding-window protocol while
    # avoiding a full 70k-row rerun for every source/feature combination.
    from validation import eval_1x2
    rows = features.build_feature_rows()
    X, y, dates = mf._rows_to_arrays(rows)
    pairs_model = []
    pairs_prior = []
    months = sorted({d[:7] for d, r in zip(dates, rows)
                     if r.get("season") == SEASON})
    for month in months:
        train = np.array([d < month + "-01" for d in dates])
        test = np.array([d[:7] == month for d in dates])
        if train.sum() < 1500 or not test.any():
            continue
        p = mf._fit_multinomial(X[train], y[train], X[test])
        prior = np.bincount(y[train], minlength=3).astype(float)
        prior /= prior.sum()
        for row, yi in zip(p, y[test]):
            pairs_model.append((tuple(row), int(yi)))
            pairs_prior.append((tuple(prior), int(yi)))
    model = eval_1x2(pairs_model)
    prior = eval_1x2(pairs_prior)
    return {
        "n": model["n"],
        "log_loss": model["log_loss"],
        "brier": model["brier"],
        "accuracy": model["accuracy"],
        "prior_log_loss": prior["log_loss"],
    }


def main():
    result = {"season": SEASON, "dc": {}, "t3": {}}
    for source in SOURCE_VARIANTS:
        dc, coverage = run_dc(source)
        result["dc"][source] = {"xg_map_rows": coverage, **dc}
        result["t3"][source] = {}
        for feature_mode in ("base", "xg_aware"):
            result["t3"][source][feature_mode] = run_t3(source, feature_mode)

    print("Native xG experiment (walk-forward, no production writes)")
    for source in SOURCE_VARIANTS:
        print(f"\n[{source}]")
        print(" DC:", result["dc"][source])
        for mode, metrics in result["t3"][source].items():
            print(f" T3/{mode}:", metrics)
    return result


if __name__ == "__main__":
    main()
