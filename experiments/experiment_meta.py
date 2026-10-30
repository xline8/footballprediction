#!/usr/bin/env python3
"""experiment_meta.py — fase 4 E1: meta-logistic di atas DC/T3 + market implied.

STATUS (audit round 12): recipe adopted. This prototype's design —
a multinomial logistic stack over DC, T3, and market-implied
logits — is the production meta recipe (nine logits, walk-forward,
in backtest_picks.py / make_picks_live.py). Kept as the design
record; production changes belong to the live modules, not here.

Fitur per match (leak-free, semuanya diketahui sebelum kickoff):
  - prob DC (ph_dc, pd_dc, pa_dc)
  - prob T3 fitur (ph_t3, pd_t3, pa_t3)
  - prob implied market (1/o(h), 1/o(d), 1/o(a)) dari B365 opening

Model: multinomial logistic regression (numpy), walk-forward bulanan, sama dgn
engine backtest. Target: log loss < 1.020 & Brier < 0.600.
"""
import os as _os, sys as _sys
_sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))

import json
import os
import sys

import numpy as np

import model_features_1x2 as mf
from backtest_picks import _fair_probs
from validation import eval_1x2

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RECORDS = os.path.join(BASE, "records_cache.jsonl")


def _load():
    from experiment_enriched import load_enriched_records
    return load_enriched_records()


def _logit_clip(p):
    return np.log(np.clip(p, 1e-6, 1 - 1e-6) / (1 - np.clip(p, 1e-6, 1 - 1e-6)))


def build_Xy(records):
    """17 fitur (Phase 12 Pathway A): 9 logit asal + dev_H/D/A + ps_fair + midweek_h/a."""
    n = len(records)
    X = np.full((n, 17), np.nan)
    y = np.empty(n, dtype=np.int64)
    dates = [None] * n
    for i, r in enumerate(records):
        X[i, 0] = _logit_clip(r["ph_dc"]); X[i, 1] = _logit_clip(r["pd_dc"])
        X[i, 2] = _logit_clip(r["pa_dc"])
        X[i, 3] = _logit_clip(r["ph_t3"]); X[i, 4] = _logit_clip(r["pd_t3"])
        X[i, 5] = _logit_clip(r["pa_t3"])
        o = r["o"]
        if o:
            for j in range(3):
                X[i, 6 + j] = _logit_clip(1.0 / o[j])
        ps = r.get("ps")
        if o and ps and all(p is not None for p in ps):
            dev = [o[j] / ps[j] for j in range(3)]
            f = _fair_probs(tuple(ps), "shin")
            for j in range(3):
                X[i, 9 + j] = _logit_clip(dev[j])
                X[i, 12 + j] = _logit_clip(f[j])
        X[i, 15] = float(r.get("mw_h", 0))
        X[i, 16] = float(r.get("mw_a", 0))
        y[i] = r["yi"]
        dates[i] = r["date"]
    return X, y, dates


def run():
    records = _load()
    X, y, dates = build_Xy(records)
    months = sorted({d[:7] for d in dates})
    pairs_meta, pairs_dc, pairs_t3 = [], [], []
    for m in months:
        train = np.array([d < m + "-01" for d in dates])
        test = np.array([d[:7] == m for d in dates])
        if train.sum() < 1500 or test.sum() == 0:
            continue
        p = mf._fit_multinomial(X[train], y[train], X[test])
        for row, k in zip(p, np.where(test)[0]):
            pairs_meta.append((tuple(row), int(y[k])))
            pairs_dc.append(((records[k]["ph_dc"], records[k]["pd_dc"],
                             records[k]["pa_dc"]), int(y[k])))
            pairs_t3.append(((records[k]["ph_t3"], records[k]["pd_t3"],
                             records[k]["pa_t3"]), int(y[k])))
    em = eval_1x2(pairs_meta)
    ed = eval_1x2(pairs_dc)
    et = eval_1x2(pairs_t3)
    print("=" * 66)
    print("META-LOGISTIC (DC+T3+market implied) — walk-forward")
    print("=" * 66)
    print(f"n eval: {em['n']}")
    print(f"{'metrik':10} {'meta':>9} {'DC':>9} {'T3':>9}")
    for k in ("log_loss", "brier", "macro_f1", "accuracy"):
        print(f"{k:10} {em[k]:>9.4f} {ed[k]:>9.4f} {et[k]:>9.4f}")
    return em, ed, et


def augment_records(path=RECORDS):
    """Tambahkan kolom ph_meta/pd_meta/pa_meta ke records_cache (walk-forward)."""
    records = _load()
    X, y, dates = build_Xy(records)
    months = sorted({d[:7] for d in dates})
    pm = [None] * len(records)
    for m in months:
        train = np.array([d < m + "-01" for d in dates])
        test = np.array([d[:7] == m for d in dates])
        if train.sum() < 1500 or test.sum() == 0:
            continue
        p = mf._fit_multinomial(X[train], y[train], X[test])
        for row, k in zip(p, np.where(test)[0]):
            pm[k] = tuple(row)
    with open(path, "w", encoding="utf-8") as f:
        for k, r in enumerate(records):
            if pm[k] is not None:
                r["ph_meta"], r["pd_meta"], r["pa_meta"] = pm[k]
            else:
                r["ph_meta"], r["pd_meta"], r["pa_meta"] = (r["ph_dc"], r["pd_dc"], r["pa_dc"])
            f.write(json.dumps(r) + "\n")
    n = sum(1 for k in range(len(records)) if pm[k] is not None)
    print(f"augment meta probs: {n}/{len(records)}")


if __name__ == "__main__":
    if "--augment" in sys.argv:
        augment_records()
    else:
        run()
