#!/usr/bin/env python3
"""Recommendation #2: reproduce the 17-feature meta model safely.

The old experiment treated a missing Pinnacle price as if it were identical to
B365.  This runner compares that legacy recipe with a missingness-aware
variant.  Both variants use the same records, monthly expanding walk-forward,
and the same numpy multinomial logistic implementation used by production.

No production cache or prediction file is written.
"""
from __future__ import annotations

import math
import os
import sys

import numpy as np

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE not in sys.path:
    sys.path.insert(0, BASE)

from backtest_picks import _fair_probs, load_records  # noqa: E402
from data_enrichment.utils import norm_team, to_float  # noqa: E402
import model_features_1x2 as mf  # noqa: E402

RECORDS = os.path.join(BASE, "records_cache.jsonl")
ENRICHED = os.path.join(BASE, "all_matches_enriched.csv")
MIN_TRAIN = 1500


def _logit(p):
    p = np.clip(float(p), 1e-6, 1.0 - 1e-6)
    return math.log(p / (1.0 - p))


def _enriched_index():
    import csv

    out = {}
    with open(ENRICHED, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            key = (r.get("Div"), str(r.get("Date") or "")[:10],
                   norm_team(r.get("HomeTeam")), norm_team(r.get("AwayTeam")))
            if not all(key):
                continue
            out[key] = {
                "ps": (to_float(r.get("ps_home")),
                       to_float(r.get("ps_draw")),
                       to_float(r.get("ps_away"))),
                "mw_h": int(r.get("midweek_home_flag") or 0),
                "mw_a": int(r.get("midweek_away_flag") or 0),
            }
    return out


def _base9(r):
    out = [_logit(r["ph_dc"]), _logit(r["pd_dc"]), _logit(r["pa_dc"]),
           _logit(r["ph_t3"]), _logit(r["pd_t3"]), _logit(r["pa_t3"])]
    odds = r.get("o") or (None, None, None)
    for odd in list(odds)[:3]:
        out.append(_logit(1.0 / odd) if odd else np.nan)
    while len(out) < 9:
        out.append(np.nan)
    return out


def build_features(records, mode):
    """Return X, y, dates and coverage for ``legacy17`` or ``aware19``."""
    idx = _enriched_index()
    n = len(records)
    width = 17 if mode == "legacy17" else 19
    X = np.full((n, width), np.nan, dtype=float)
    y = np.empty(n, dtype=int)
    dates = []
    matched = complete = 0
    for i, r in enumerate(records):
        X[i, :9] = _base9(r)
        key = (r["div"], r["date"], norm_team(r["home"]),
               norm_team(r["away"]))
        ext = idx.get(key)
        ps = ext["ps"] if ext else (None, None, None)
        o = r.get("o")
        present = bool(o and all(v is not None for v in ps))
        if ext:
            matched += 1
        if present:
            complete += 1
        if mode == "legacy17" and o:
            # Historical recipe: missing sharp prices fall back to B365.
            ps_use = tuple(ps[j] if ps[j] is not None else o[j]
                           for j in range(3))
            dev = [o[j] / ps_use[j] for j in range(3)]
            fair = _fair_probs(tuple(ps_use), "shin")
            for j in range(3):
                X[i, 9 + j] = _logit(dev[j])
                X[i, 12 + j] = _logit(fair[j])
            X[i, 15] = float(ext["mw_h"] if ext else 0)
            X[i, 16] = float(ext["mw_a"] if ext else 0)
        elif mode == "aware19":
            if present:
                dev = [o[j] / ps[j] for j in range(3)]
                fair = _fair_probs(tuple(ps), "shin")
                for j in range(3):
                    X[i, 9 + j] = _logit(dev[j])
                    X[i, 12 + j] = _logit(fair[j])
            X[i, 15] = float(ext["mw_h"] if ext else 0)
            X[i, 16] = float(ext["mw_a"] if ext else 0)
            # Explicit availability indicators: 1 means no complete PS quote.
            X[i, 17] = 0.0 if present else 1.0
            X[i, 18] = 0.0 if present else 1.0
        y[i] = int(r["yi"])
        dates.append(r["date"])
    return X, y, dates, {"matched": matched, "complete_ps": complete}


def evaluate(records, X, y, dates):
    pairs = []
    for month in sorted({d[:7] for d in dates}):
        train = np.array([d < month + "-01" for d in dates])
        test = np.array([d[:7] == month for d in dates])
        if train.sum() < MIN_TRAIN or not test.any():
            continue
        p = mf._fit_multinomial(X[train], y[train], X[test])
        for row, yi in zip(p, y[test]):
            pairs.append((tuple(row), int(yi)))
    from validation import eval_1x2
    return eval_1x2(pairs)


def main():
    records = load_records(RECORDS)
    print(f"records={len(records):,} enriched={os.path.basename(ENRICHED)}")
    for mode in ("legacy17", "aware19"):
        X, y, dates, coverage = build_features(records, mode)
        metrics = evaluate(records, X, y, dates)
        print(mode, coverage, {k: metrics[k] for k in
                               ("n", "log_loss", "brier", "accuracy", "macro_f1")})


if __name__ == "__main__":
    main()
