#!/usr/bin/env python3
"""backtest_picks.py — backtest strategi value-bet 1X2: baseline DC vs T3 (fitur).

Mensimulasikan aturan yang SAMA dengan make_picks.py (signal = prob model murni,
harga = odds opening/day-of, edge > thr) tetapi pada riwayat, sehingga kita bisa
membandingkan profitabilitas model lama (Dixon-Coles) vs model baru (T3 fitur)
di rel yang sama, walk-forward, tanpa bocor.

Scope: pasar 1X2 (pasar utama make_picks). Corner/OU tidak disertakan di sini.

Jalankan:  python backtest_picks.py [--thr 0.02] [--seasons 2023/24,2024/25]
"""

import csv
import os
import sys
from datetime import datetime

import numpy as np

import model_features_1x2 as mf
from features import build_feature_rows
from football_etl import load_fd_odds, norm3, normalize_name, parse_date, TOP5
from model_v2 import DC
from validation import eval_1x2

BASE = os.path.dirname(os.path.abspath(__file__))

YIDX = {"H": 0, "D": 1, "A": 2}
SIDES = (("H", 0), ("D", 1), ("A", 2))


def _as_date(d):
    if isinstance(d, datetime):
        return d.date()
    if isinstance(d, str):
        return datetime.strptime(d[:10], "%Y-%m-%d").date()
    return d


def _load_hist_odds(path):
    """Odds historis dari all_matches_clean.csv (B365 opening) antar-musim."""
    odds = {}
    if not os.path.exists(path):
        return odds
    with open(path, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            d = parse_date(r.get("Date"))
            if not d:
                continue
            h = normalize_name(r.get("HomeTeam"))
            a = normalize_name(r.get("AwayTeam"))
            if not h or not a:
                continue
            bh, bd, ba = r.get("B365H"), r.get("B365D"), r.get("B365A")
            if bh and bd and ba:
                try:
                    odds[(r.get("Div"), d.isoformat(), h, a)] = (
                        float(bh), float(bd), float(ba))
                except ValueError:
                    continue
    return odds


def _open_dec(o):
    """Ambil harga desimal (h, d, a) dari opening (tuple atau dict)."""
    if isinstance(o, (tuple, list)) and len(o) >= 3:
        h, d, a = o[0], o[1], o[2]
    else:
        h, d, a = o.get("B365H"), o.get("B365D"), o.get("B365A")
        if not (h and d and a):
            h, d, a = o.get("AvgH"), o.get("AvgD"), o.get("AvgA")
    try:
        h, d, a = float(h), float(d), float(a)
    except (TypeError, ValueError):
        return None
    if min(h, d, a) <= 1.0:
        return None
    return (h, d, a)


def backtest(seasons=None, thr=0.02):
    rows = build_feature_rows(limit=None)
    if seasons:
        rows = [r for r in rows if r.get("season") in seasons]

    X, y, dates = mf._rows_to_arrays(rows)
    if len(rows) == 0:
        raise RuntimeError("tidak ada baris fitur")
    months = sorted({d[:7] for d in dates})

    # odds: historis (antar-musim) + live 2627 untuk match paling baru
    odds = _load_hist_odds(os.path.join(BASE, "all_matches_clean.csv"))
    for div in TOP5:
        for k, v in load_fd_odds(div, "2627").items():
            odds.setdefault(k, v.get("b365") or v.get("avg"))

    st_base = {"n": 0, "wins": 0, "profit": 0.0}
    st_t3 = {"n": 0, "wins": 0, "profit": 0.0}
    pairs_base, pairs_t3 = [], []

    for m in months:
        train = np.array([d < m + "-01" for d in dates])
        test = np.array([d[:7] == m for d in dates])
        if train.sum() < 1500 or test.sum() == 0:
            continue

        Xtr, ytr = X[train], y[train]
        Xte, yte = X[test], y[test]
        p3 = mf._fit_multinomial(Xtr, ytr, Xte)

        test_rows = [rows[i] for i in np.where(test)[0]]
        dc_cache = {}
        for idx, r in enumerate(test_rows):
            div, dstr = r["div"], r["date"]
            # baseline DC: fit sekali per (divisi, bulan)
            if div not in dc_cache:
                games = []
                for rr in rows:
                    if rr["div"] == div and rr["date"] < m + "-01" and rr["yh"] is not None:
                        games.append((rr["home"], rr["away"], rr["yh"], rr["ya"],
                                     _as_date(rr["date"])))
                mdl = DC()
                try:
                    mdl.fit(games[-4000:], _as_date(m + "-01"), 270.0)
                except Exception:
                    mdl = None
                dc_cache[div] = mdl
            mdl = dc_cache[div]
            if mdl is None:
                continue
            try:
                lh, la = mdl._lam(r["home"], r["away"])
                pr = mdl.probs(lh, la)
            except Exception:
                continue
            pbase = (pr["ph"], pr["pd"], pr["pa"])
            p3row = tuple(p3[idx])
            yi = int(yte[idx])
            pairs_base.append((pbase, yi))
            pairs_t3.append((p3row, yi))

            o = odds.get((div, dstr, r["home"], r["away"]))
            if o is None:
                continue
            odec = _open_dec(o)
            if odec is None:
                continue
            for side, im in SIDES:
                od = odec[im]
                imp = 1.0 / od
                for st, pm in ((st_base, pbase[im]), (st_t3, p3row[im])):
                    if pm - imp > thr:
                        st["n"] += 1
                        if im == yi:
                            st["wins"] += 1
                            st["profit"] += od - 1.0
                        else:
                            st["profit"] -= 1.0

    em = eval_1x2(pairs_t3)
    ep = eval_1x2(pairs_base)
    return em, ep, st_base, st_t3


def report(em, ep, st_base, st_t3):
    print("=" * 70)
    print("BACKTEST VALUE-BET 1X2 (walk-forward, model vs baseline)")
    print("=" * 70)
    print(f"n uji (semua match): {em['n']}")
    print()
    print(f"{'metrik':12} {'T3 fitur':>10} {'DC baseline':>10}")
    for k in ("brier", "log_loss", "macro_f1", "accuracy"):
        print(f"{k:12} {em[k]:>10.4f} {ep[k]:>10.4f}")
    print()
    print(f"{'pasar bet':6} {'n bet':>6} {'hit rate':>9} {'yield':>8} {'profit':>8}")
    for name, st in (("T3 fitur", st_t3), ("DC baseline", st_base)):
        n = st["n"]
        hit = st["wins"] / n if n else 0.0
        yield_ = st["profit"] / n if n else 0.0
        print(f"{name:6} {n:>6} {hit:>9.3f} {yield_:>8.3f} {st['profit']:>8.2f}")
    print()


def main():
    thr = 0.02
    seasons = None
    args = sys.argv[1:]
    if "--thr" in args:
        thr = float(args[args.index("--thr") + 1])
    if "--seasons" in args:
        seasons = set(args[args.index("--seasons") + 1].split(","))
    em, ep, st_base, st_t3 = backtest(seasons=seasons, thr=thr)
    report(em, ep, st_base, st_t3)


if __name__ == "__main__":
    main()
