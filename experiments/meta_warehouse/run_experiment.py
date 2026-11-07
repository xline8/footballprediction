#!/usr/bin/env python3
"""run_experiment.py — G-2: warehouse features as extra meta-stack columns.

Experiment ONLY (MODEL_AUDIT_2026-11-07.md section 1C, item G-2).
No production file is modified; production machinery is imported read-only
(backtest_picks._logit, model_features_1x2._fit_params/_softmax_scores,
matrix_pricer.price, validation.eval_1x2) and re-implemented/extended here.

PRE-REGISTERED DESIGN (written before any test result was computed)
-------------------------------------------------------------------
Baseline : monthly walk-forward meta stack exactly as
           backtest_picks._add_meta_walkforward -- 9 logit columns
           (logit DC probs, logit T3 probs, logit raw implied 1/odds from
           opening odds), multinomial logistic via mf._fit_params
           (defaults l2=1e-3, epochs=120), train = ALL records with
           date < first day of the test month, min_train=1500.
Variant  : baseline + exactly THREE extra columns (one set, no fishing):

  W1 shot-quality differential (trailing 10):
       per team-match net = (xg_for/shots_for) - (xg_against/shots_against)
       team value = mean net over its last 10 warehouse matches strictly
       before the match date (requires >=5 such matches, else NaN);
       match feature = home team value - away team value.
  W2 big-chance differential (trailing 10):
       per team-match net = big_chances_for - big_chances_against;
       team value / match feature constructed exactly as W1.
  W3 xGOT-per-SOT differential (trailing 10):
       per team-match net = (xgot_for/sot_for, 0 if sot_for==0)
                          - (xgot_against/sot_against, 0 if sot_against==0);
       team value / match feature constructed exactly as W1.

  The three W columns are raw standardised differentials, not probability
  logits (they can be negative); mf._fit_params median-imputes NaN and
  standardises every column from the training window only, exactly as it
  does for the 9 baseline logits. Lineup continuity is deliberately NOT
  included: the audit (section 1B.2 / 1C) already recorded it as a
  negative result.

Evaluation set (identical for baseline and variant):
  top-5 divisions (E0, D1, I1, SP1, F1), seasons 2024/25 and 2025/26,
  records with actual goals present and all three warehouse features
  non-NaN. Warehouse features exist only from 2022/23, which is why the
  test window starts in 2024/25: it leaves two full warehouse seasons
  (2022/23, 2023/24) plus the walk-forward history in every training set.

Derived markets: matrix_pricer.price(lam_h, lam_a, rho, meta_probs) for
each model -- the Phase-13 production derivation -- giving OU 2.5 and
BTTS probabilities from the same 1X2 probabilities; scored as binary
log loss against fthg/ftag.

GATE (pre-registered): pooled variant 1X2 log loss < same-set baseline
log loss AND variant log loss < 1.0017 (baseline-family standard) AND
Brier not worse AND RPS not worse AND OU 2.5 log loss not worse AND
BTTS log loss not worse. All on the identical evaluation set.

Outputs: results.json + predictions.csv in this directory.
"""
import csv
import json
import math
import os
import sys
from collections import defaultdict

BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, BASE)

import numpy as np  # noqa: E402

import model_features_1x2 as mf  # noqa: E402
from backtest_picks import _logit, load_records  # noqa: E402
from football_etl import normalize_name  # noqa: E402
from matrix_pricer import price as matrix_price  # noqa: E402
from validation import eval_1x2  # noqa: E402

TOP5 = {"E0", "D1", "I1", "SP1", "F1"}
TEST_SEASONS = {"2024/25", "2025/26"}
TRAIL_N = 10
TRAIL_MIN = 5
FAMILY_STANDARD_LL = 1.0017
OUT_DIR = os.path.dirname(os.path.abspath(__file__))


# ---------------------------------------------------------------- warehouse
def _f(row, col):
    v = row.get(col)
    if v in (None, ""):
        return None
    try:
        return float(v)
    except ValueError:
        return None


def build_trailing():
    """Return dict: record-key -> (W1, W2, W3) or None.

    Key = (div, date, normalize_name(home), normalize_name(away)), the
    same normalisation the audit script used for both sources.
    Team history is keyed (div, normalised team) and only warehouse
    matches with date strictly before the target match are used.
    """
    path = os.path.join(BASE, "data_enrichment", "shot_lineup_features.csv")
    team_hist = defaultdict(list)  # (div, team) -> [(date, w1_net, w2_net, w3_net)]
    match_rows = []
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            div, date = row["div"], row["date"]
            hn, an = normalize_name(row["home"]), normalize_name(row["away"])
            vals = {}
            ok = True
            for side in ("h", "a"):
                for stat in ("shots", "xg", "xgot", "sot", "big_chances"):
                    v = _f(row, f"{stat}_{side}")
                    if v is None:
                        ok = False
                    vals[f"{stat}_{side}"] = v
            if not ok:
                continue
            match_rows.append((div, date, hn, an, vals))
            for side, opp, team in (("h", "a", hn), ("a", "h", an)):
                shots_f, shots_a = vals[f"shots_{side}"], vals[f"shots_{opp}"]
                sot_f, sot_a = vals[f"sot_{side}"], vals[f"sot_{opp}"]
                sq_f = vals[f"xg_{side}"] / shots_f if shots_f > 0 else 0.0
                sq_a = vals[f"xg_{opp}"] / shots_a if shots_a > 0 else 0.0
                xg_f = vals[f"xgot_{side}"] / sot_f if sot_f > 0 else 0.0
                xg_a = vals[f"xgot_{opp}"] / sot_a if sot_a > 0 else 0.0
                team_hist[(div, team)].append((
                    date,
                    sq_f - sq_a,
                    vals[f"big_chances_{side}"] - vals[f"big_chances_{opp}"],
                    xg_f - xg_a,
                ))
    for v in team_hist.values():
        v.sort(key=lambda t: t[0])

    def team_value(div, team, date):
        hist = [t for t in team_hist.get((div, team), []) if t[0] < date]
        if len(hist) < TRAIL_MIN:
            return None
        hist = hist[-TRAIL_N:]
        return tuple(sum(t[j] for t in hist) / len(hist) for j in (1, 2, 3))

    out = {}
    for div, date, hn, an, _vals in match_rows:
        hv = team_value(div, hn, date)
        av = team_value(div, an, date)
        if hv is None or av is None:
            out[(div, date, hn, an)] = None
        else:
            out[(div, date, hn, an)] = tuple(hv[j] - av[j] for j in range(3))
    return out


# ---------------------------------------------------------------- metrics
def rps(p, yi):
    s = 0.0
    cum_p = cum_o = 0.0
    for k in range(2):  # order H, D, A; third term is identically 0
        cum_p += p[k]
        cum_o += 1.0 if k == yi else 0.0
        s += (cum_p - cum_o) ** 2
    return s / 2.0


def bin_ll(p, y):
    p = min(max(p, 1e-12), 1 - 1e-12)
    return -(y * math.log(p) + (1 - y) * math.log(1 - p))


def score(rows):
    """rows: list of dicts with p_base, p_var, yi, fthg, ftag."""
    if not rows:
        return {"n": 0}
    out = {"n": len(rows)}
    for tag, key in (("base", "p_base"), ("var", "p_var")):
        pairs = [(tuple(r[key]), r["yi"]) for r in rows]
        ev = eval_1x2(pairs)
        out[f"{tag}_ll"] = ev["log_loss"]
        out[f"{tag}_brier"] = ev["brier"]
        out[f"{tag}_rps"] = sum(rps(p, yi) for p, yi in pairs) / len(pairs)
        out[f"{tag}_acc"] = ev["accuracy"]
        # derived markets from the same probabilities (matrix pricer)
        ou_ll = btts_ll = 0.0
        n_deriv = 0
        for r in rows:
            d = matrix_price(r["lam_h"], r["lam_a"], r["rho"], tuple(r[key]))
            if d is None:
                continue
            p_over, _u, p_btts, _n = d
            ou_ll += bin_ll(p_over, 1.0 if (r["fthg"] + r["ftag"]) > 2.5 else 0.0)
            btts_ll += bin_ll(p_btts, 1.0 if (r["fthg"] > 0 and r["ftag"] > 0) else 0.0)
            n_deriv += 1
        out[f"{tag}_ou_ll"] = ou_ll / n_deriv
        out[f"{tag}_btts_ll"] = btts_ll / n_deriv
        out["n_deriv"] = n_deriv
    for m in ("ll", "brier", "rps", "ou_ll", "btts_ll"):
        out[f"delta_{m}"] = out[f"var_{m}"] - out[f"base_{m}"]
    return out


# ---------------------------------------------------------------- main
def main():
    records = load_records()
    trail = build_trailing()
    n = len(records)

    X9 = np.full((n, 9), np.nan)
    W = np.full((n, 3), np.nan)
    y = np.empty(n, dtype=int)
    dates = []
    for i, r in enumerate(records):
        X9[i, 0] = _logit(r["ph_dc"]); X9[i, 1] = _logit(r["pd_dc"])
        X9[i, 2] = _logit(r["pa_dc"])
        X9[i, 3] = _logit(r["ph_t3"]); X9[i, 4] = _logit(r["pd_t3"])
        X9[i, 5] = _logit(r["pa_t3"])
        o = r.get("o")
        if o:
            for j in range(3):
                X9[i, 6 + j] = _logit(1.0 / o[j])
        y[i] = r["yi"]
        dates.append(r["date"])
        if r["div"] in TOP5:
            w = trail.get((r["div"], r["date"],
                           normalize_name(r["home"]), normalize_name(r["away"])))
            if w is not None:
                W[i] = w
    X12 = np.hstack([X9, W])

    eval_idx = [i for i, r in enumerate(records)
                if r["div"] in TOP5 and r.get("season") in TEST_SEASONS
                and r.get("fthg") is not None and r.get("ftag") is not None
                and not np.isnan(W[i]).any()]
    print(f"records={n}  eval candidates={len(eval_idx)}")

    rows = []
    stored_pairs = []
    months = sorted({dates[i][:7] for i in eval_idx})
    for m in months:
        tr = np.array([d < m + "-01" for d in dates])
        te_idx = [i for i in eval_idx if dates[i][:7] == m]
        if tr.sum() < 1500 or not te_idx:
            continue
        te = np.array(te_idx)
        params_b = mf._fit_params(X9[tr], y[tr])
        pb = mf._softmax_scores(X9[te], *params_b)
        params_v = mf._fit_params(X12[tr], y[tr])
        pv = mf._softmax_scores(X12[te], *params_v)
        for j, i in enumerate(te_idx):
            r = records[i]
            rows.append({
                "div": r["div"], "date": r["date"], "season": r["season"],
                "home": r["home"], "away": r["away"], "yi": int(y[i]),
                "fthg": int(r["fthg"]), "ftag": int(r["ftag"]),
                "lam_h": r["lam_h"], "lam_a": r["lam_a"], "rho": r["rho"],
                "w1": float(W[i, 0]), "w2": float(W[i, 1]), "w3": float(W[i, 2]),
                "p_base": tuple(float(x) for x in pb[j]),
                "p_var": tuple(float(x) for x in pv[j]),
            })
            if r.get("ph_meta"):
                stored_pairs.append(((r["ph_meta"], r["pd_meta"], r["pa_meta"]),
                                     int(y[i])))
        print(f"  {m}: train={int(tr.sum())} test={len(te_idx)}")

    pooled = score(rows)
    per_season = {s: score([r for r in rows if r["season"] == s])
                  for s in sorted(TEST_SEASONS)}
    per_div = {d: score([r for r in rows if r["div"] == d])
               for d in sorted(TOP5)}

    stored = {}
    if stored_pairs:
        ev = eval_1x2(stored_pairs)
        stored = {"n": ev["n"], "ll": ev["log_loss"], "brier": ev["brier"],
                  "rps": sum(rps(p, yi) for p, yi in stored_pairs) / len(stored_pairs)}

    gate = {
        "ll_improves_vs_same_set_baseline": pooled["var_ll"] < pooled["base_ll"],
        "ll_below_family_standard_1.0017": pooled["var_ll"] < FAMILY_STANDARD_LL,
        "brier_not_worse": pooled["var_brier"] <= pooled["base_brier"],
        "rps_not_worse": pooled["var_rps"] <= pooled["base_rps"],
        "ou_ll_not_worse": pooled["var_ou_ll"] <= pooled["base_ou_ll"],
        "btts_ll_not_worse": pooled["var_btts_ll"] <= pooled["base_btts_ll"],
    }
    gate["PASS"] = all(gate.values())

    results = {
        "design": {
            "test_seasons": sorted(TEST_SEASONS),
            "divs": sorted(TOP5),
            "train": "all records, date < test month, monthly refit, min_train=1500",
            "baseline_features": "9 logits as backtest_picks._add_meta_walkforward",
            "variant_extra_features": [
                "W1 trailing-10 shot-quality differential (xg/shots net, home-away)",
                "W2 trailing-10 big-chance differential (net, home-away)",
                "W3 trailing-10 xGOT-per-SOT differential (net, home-away)",
            ],
            "trail_n": TRAIL_N, "trail_min": TRAIL_MIN,
            "family_standard_ll": FAMILY_STANDARD_LL,
        },
        "n_eval": pooled["n"],
        "eval_window": [min(r["date"] for r in rows), max(r["date"] for r in rows)],
        "pooled": pooled,
        "per_season": per_season,
        "per_div": per_div,
        "stored_meta_same_set_sanity": stored,
        "gate": gate,
        "verdict": "PASS" if gate["PASS"] else "FAIL",
    }
    with open(os.path.join(OUT_DIR, "results.json"), "w", encoding="utf-8") as f:
        json.dump(results, f, indent=1)
    with open(os.path.join(OUT_DIR, "predictions.csv"), "w", newline="",
              encoding="utf-8") as f:
        wcsv = csv.writer(f)
        wcsv.writerow(["div", "date", "season", "home", "away", "yi", "fthg", "ftag",
                       "w1", "w2", "w3",
                       "pb_h", "pb_d", "pb_a", "pv_h", "pv_d", "pv_a"])
        for r in rows:
            wcsv.writerow([r["div"], r["date"], r["season"], r["home"], r["away"],
                           r["yi"], r["fthg"], r["ftag"],
                           f"{r['w1']:.6f}", f"{r['w2']:.6f}", f"{r['w3']:.6f}"] +
                          [f"{x:.6f}" for x in r["p_base"]] +
                          [f"{x:.6f}" for x in r["p_var"]])
    print(json.dumps(results, indent=1))
    return results


if __name__ == "__main__":
    main()
