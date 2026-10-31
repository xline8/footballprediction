#!/usr/bin/env python3
"""Recommendation #4: opponent-adjusted shots/SOT and proxy xG.

The runner builds rolling pre-match shot and shot-on-target features.  State is
updated only after all matches on a date have been scored, so same-day fixtures
cannot leak into one another.  A small ridge model learns a proxy xG mapping
from historical Understat/native xG labels, fitting that mapping inside each
walk-forward training window.
"""
from __future__ import annotations

import csv
import math
import os
import sys
from collections import defaultdict, deque

import numpy as np

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE not in sys.path:
    sys.path.insert(0, BASE)

os.environ["FOOTBALL_XG_SOURCE"] = "native_priority"

from football_etl import normalize_name, parse_date  # noqa: E402
from features import build_feature_rows, _load_xg_map  # noqa: E402
import model_features_1x2 as mf  # noqa: E402

DATA = os.path.join(BASE, "all_matches_clean.csv")
TOP5 = {"E0", "D1", "I1", "SP1", "F1"}
BASE_NAMES = [
    "elo_diff", "form_pts_h", "form_pts_a", "goals_diff_h", "goals_diff_a",
    "xg_diff_h", "xg_diff_a", "rest_h", "rest_a", "n_played_h", "n_played_a",
]
SHOT_NAMES = [
    "shot_attack_h", "shot_defence_h", "shot_attack_a", "shot_defence_a",
    "sot_attack_h", "sot_defence_h", "sot_attack_a", "sot_defence_a",
    "shot_sot_rate_h", "shot_sot_rate_a", "shot_missing_h", "shot_missing_a",
]
VAL_SEASONS = {"2019/20", "2020/21"}
TEST_SEASONS = {"2021/22", "2022/23", "2023/24", "2024/25", "2025/26"}


def num(value):
    try:
        v = float(value)
        return v if math.isfinite(v) else None
    except (TypeError, ValueError):
        return None


def _shrink(value, n, prior, k=5.0):
    if value is None or n <= 0:
        return prior if prior is not None else np.nan
    if prior is None:
        return value
    return (n * value + k * prior) / (n + k)


def _team_avg(history, idx):
    vals = [x[idx] for x in history if x[idx] is not None]
    return (sum(vals) / len(vals), len(vals)) if vals else (None, 0)


def build_shot_rows():
    """Build one leak-free feature row per TOP5 match."""
    raw = []
    with open(DATA, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r.get("Div") not in TOP5 or not r.get("Date"):
                continue
            d = parse_date(r.get("Date"))
            if d is None or r.get("FTR") not in ("H", "D", "A"):
                continue
            raw.append({
                "div": r["Div"], "date": d.isoformat(), "season": r.get("Season"),
                "home": r.get("HomeTeam"), "away": r.get("AwayTeam"),
                "ftr": r["FTR"],
                "hs": num(r.get("HS")), "as": num(r.get("AS")),
                "hst": num(r.get("HST")), "ast": num(r.get("AST")),
                "yh": num(r.get("FTHG")), "ya": num(r.get("FTAG")),
            })
    raw.sort(key=lambda r: (r["date"], r["div"], r["home"] or ""))
    xg = _load_xg_map()
    history = defaultdict(lambda: deque(maxlen=5))
    league_sum = defaultdict(lambda: [0.0, 0.0, 0])
    out = []
    pos = 0
    while pos < len(raw):
        end = pos
        d = raw[pos]["date"]
        while end < len(raw) and raw[end]["date"] == d:
            end += 1
        # Score every same-day match from the state before this date.
        for r in raw[pos:end]:
            div = r["div"]
            h = (div, normalize_name(r["home"]))
            a = (div, normalize_name(r["away"]))
            hhist, ahist = history[h], history[a]
            ss = league_sum[div]
            league_shots = ss[0] / ss[2] if ss[2] else None
            league_sot = ss[1] / ss[2] if ss[2] else None
            hsf, nhsf = _team_avg(hhist, 0)
            hsa, nhsa = _team_avg(hhist, 1)
            htf, nhtf = _team_avg(hhist, 2)
            hta, nhta = _team_avg(hhist, 3)
            asf, nasf = _team_avg(ahist, 0)
            asa, nasa = _team_avg(ahist, 1)
            atf, natf = _team_avg(ahist, 2)
            ata, nata = _team_avg(ahist, 3)
            # Attack/defence ratios combine a team's rolling rate with the
            # opponent's allowed rate and shrink both toward the league mean.
            def ratio(for_v, for_n, opp_v, opp_n, prior):
                if prior is None or prior <= 0:
                    return np.nan
                af = _shrink(for_v, for_n, prior)
                od = _shrink(opp_v, opp_n, prior)
                if af is None or od is None:
                    return np.nan
                return ((af / prior) + (od / prior)) / 2.0

            vals = {
                "shot_attack_h": ratio(hsf, nhsf, asa, nasa, league_shots),
                "shot_defence_h": ratio(hsa, nhsa, asf, nasf, league_shots),
                "shot_attack_a": ratio(asf, nasf, hsa, nhsa, league_shots),
                "shot_defence_a": ratio(asa, nasa, hsf, nhsf, league_shots),
                "sot_attack_h": ratio(htf, nhtf, ata, nata, league_sot),
                "sot_defence_h": ratio(hta, nhta, atf, natf, league_sot),
                "sot_attack_a": ratio(atf, natf, hta, nhta, league_sot),
                "sot_defence_a": ratio(ata, nata, htf, nhtf, league_sot),
                "shot_sot_rate_h": (htf / hsf if htf is not None and hsf else np.nan),
                "shot_sot_rate_a": (atf / asf if atf is not None and asf else np.nan),
                "shot_missing_h": 0.0 if nhsf and nhtf else 1.0,
                "shot_missing_a": 0.0 if nasf and natf else 1.0,
            }
            key = (div, r["date"], normalize_name(r["home"]),
                   normalize_name(r["away"]))
            xgh, xga = xg.get(key, (None, None))
            out.append({"key": key, "season": r["season"], "date": r["date"],
                        "div": div, "ftr": r["ftr"], "xgh": xgh, "xga": xga,
                        **vals})
        # Only after all fixtures on this date have features, update state.
        for r in raw[pos:end]:
            div = r["div"]
            h = (div, normalize_name(r["home"]))
            a = (div, normalize_name(r["away"]))
            history[h].append((r["hs"], r["as"], r["hst"], r["ast"]))
            history[a].append((r["as"], r["hs"], r["ast"], r["hst"]))
            ss = league_sum[div]
            # A row contributes once if both sides' shot and SOT observations
            # exist; this avoids changing the denominator for partial rows.
            if all(r[k] is not None for k in ("hs", "as", "hst", "ast")):
                ss[0] += r["hs"] + r["as"]
                ss[1] += r["hst"] + r["ast"]
                ss[2] += 2
        pos = end
    return out


def _feature_rows():
    base_rows = [r for r in build_feature_rows()
                 if r.get("div") in TOP5 and r.get("ftr") in ("H", "D", "A")]
    shot = {r["key"]: r for r in build_shot_rows()}
    rows = []
    for r in base_rows:
        key = (r["div"], r["date"], normalize_name(r["home"]),
               normalize_name(r["away"]))
        s = shot.get(key)
        if not s:
            continue
        rows.append({"date": r["date"], "season": r.get("season"),
                     "div": r["div"], "ftr": r["ftr"],
                     "base": [r.get(k) for k in BASE_NAMES],
                     "shot": [s.get(k) for k in SHOT_NAMES],
                     "xgh": s.get("xgh"), "xga": s.get("xga")})
    rows.sort(key=lambda r: (r["date"], r["div"]))
    return rows


def _matrix(rows, field):
    return np.array([[np.nan if v is None else float(v) for v in r[field]]
                     for r in rows], dtype=float)


def _ridge_proxy(rows, Xraw, train_idx):
    idx = [int(i) for i in train_idx
           if rows[int(i)]["xgh"] is not None and rows[int(i)]["xga"] is not None]
    if len(idx) < 100:
        return None
    X = Xraw[idx]
    med = np.nanmedian(X, axis=0)
    med = np.where(np.isfinite(med), med, 0.0)
    X = np.where(np.isfinite(X), X, med)
    X = np.column_stack([np.ones(len(X)), X])
    y_h = np.array([rows[i]["xgh"] for i in idx], dtype=float)
    y_a = np.array([rows[i]["xga"] for i in idx], dtype=float)
    reg = np.eye(X.shape[1]) * 10.0
    reg[0, 0] = 0.01
    bh = np.linalg.solve(X.T @ X + reg, X.T @ y_h)
    ba = np.linalg.solve(X.T @ X + reg, X.T @ y_a)
    return med, bh, ba


def _metrics(pairs):
    ll = brier = acc = 0.0
    for p, yi in pairs:
        ll -= math.log(max(p[yi], 1e-12))
        brier += sum((p[k] - (1 if k == yi else 0)) ** 2 for k in range(3))
        acc += int(max(range(3), key=lambda k: p[k]) == yi)
    n = len(pairs)
    return {"n": n, "log_loss": ll / max(n, 1), "brier": brier / max(n, 1),
            "accuracy": acc / max(n, 1)}


def evaluate(seasons=None):
    """Return baseline/challenger metrics for the requested seasons."""
    seasons = set(seasons or (VAL_SEASONS | TEST_SEASONS))
    rows = _feature_rows()
    y = np.array([{ "H": 0, "D": 1, "A": 2}[r["ftr"]] for r in rows], dtype=int)
    Xb = _matrix(rows, "base")
    Xs = _matrix(rows, "shot")
    pairs = {"base": [], "shots_sot": []}
    for month in sorted({r["date"][:7] for r in rows}):
        train = np.array([r["date"] < month + "-01" for r in rows])
        test = np.array([r["date"][:7] == month for r in rows])
        if train.sum() < 1500 or not test.any():
            continue
        eval_mask = np.array([r["season"] in seasons for r in rows])
        test &= eval_mask
        if not test.any():
            continue
        pb = mf._fit_multinomial(Xb[train], y[train], Xb[test])
        for p, yi in zip(pb, y[test]):
            pairs["base"].append((tuple(p), int(yi)))
        proxy = _ridge_proxy(rows, Xs, np.where(train)[0])
        if proxy is None:
            Xext = np.column_stack([Xb, Xs, np.zeros(len(rows))])
        else:
            med, bh, ba = proxy
            filled = np.where(np.isfinite(Xs), Xs, med)
            design = np.column_stack([np.ones(len(rows)), filled])
            xgdiff = design @ bh - design @ ba
            Xext = np.column_stack([Xb, Xs, xgdiff])
        pe = mf._fit_multinomial(Xext[train], y[train], Xext[test])
        for p, yi in zip(pe, y[test]):
            pairs["shots_sot"].append((tuple(p), int(yi)))
    result = {name: _metrics(pair) for name, pair in pairs.items()}
    result["rows"] = len(rows)
    result["shot_labels"] = sum(r["xgh"] is not None for r in rows)
    return result


def main():
    result = evaluate()
    print(f"rows={result['rows']:,} shot_labels={result['shot_labels']:,}")
    for name in ("base", "shots_sot"):
        print(name, result[name])


if __name__ == "__main__":
    main()
