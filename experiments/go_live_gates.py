#!/usr/bin/env python3
"""go_live_gates.py — gerbang go-live untuk switch produksi DC ke blend ("B").

Menjalankan 3 gate (SEMUA harus lulus sebelum default flip di model_v2.py):

  Gate A (meta stack): bangun ulang records cache mode goals vs blend
      (cache_records produksi), refit meta 9-logit walk-forward bulanan pada
      fold identik, bandingkan stacked 1X2 log loss. Blend <= goals.

  Gate B (derivatif): walk-forward O/U 2.5 dan BTTS (log loss + Brier)
      G vs B pada fold eksperimen (top5 dgn xG asli); harga dari matriks
      scoreline varian masing-masing; tak boleh degradasi > +0.002 log loss
      overall di kedua market.

  Gate C (held-out seasons): ulangi perbandingan eksperimen pada fold
      2017/18-2020/21 (bukan musim test 1255bcd); B overall log loss <= G.

Jika ada gate gagal: biarkan default "goals", laporkan angka. Hanya flip saat
semua lulus.
"""
from __future__ import annotations
import os as _os, sys as _sys
_sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))

import json
import math
import os
import sys
import time
from collections import defaultdict
from datetime import datetime

import numpy as np

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE)

import model_features_1x2 as mf
import model_v2
from model_v2 import DC, MAXG
from football_etl import pois, tau
from backtest_picks import cache_records, load_records
from validation import eval_1x2
from experiment_xg_dc import _wf_variants, _metrics

# Gate B / C
HELD_OUT_SEASONS = {"2017/18", "2018/19", "2019/20", "2020/21"}
TOP5 = ["E0", "SP1", "D1", "I1", "F1"]
GATE_B_DEGRADE = 0.002  # ambang degradasi log loss overall per market

# file records sementara untuk Gate A (dibersihkan di akhir)
REC_GOALS = os.path.join(BASE, "gates_records_goals.jsonl")
REC_BLEND = os.path.join(BASE, "gates_records_blend.jsonl")


def _logit(p):
    p = np.clip(np.asarray(p, dtype=float), 1e-6, 1 - 1e-6)
    return np.log(p / (1 - p))


# ------------------------------------------------------------------ Gate A ----
def _records_meta_stack(records):
    """Stack meta walk-forward bulanan (9-logit) pada records; -> pairs."""
    n = len(records)
    X = np.full((n, 9), np.nan)
    y = np.empty(n, dtype=int)
    dates = []
    for i, r in enumerate(records):
        X[i, 0] = _logit(r["ph_dc"]); X[i, 1] = _logit(r["pd_dc"])
        X[i, 2] = _logit(r["pa_dc"])
        X[i, 3] = _logit(r["ph_t3"]); X[i, 4] = _logit(r["pd_t3"])
        X[i, 5] = _logit(r["pa_t3"])
        o = r.get("o")
        if o:
            for j in range(3):
                X[i, 6 + j] = _logit(1.0 / o[j])
        y[i] = r["yi"]
        dates.append(r["date"])
    months = sorted({d[:7] for d in dates})
    pairs = []
    for m in months:
        tr = np.array([d < m + "-01" for d in dates])
        te = np.array([d[:7] == m for d in dates])
        if tr.sum() < 1500 or te.sum() == 0:
            continue
        params = mf._fit_params(X[tr], y[tr])
        preds = mf._softmax_scores(X[te], *params)
        for row, k in zip(preds, np.where(te)[0]):
            pairs.append((tuple(row), int(y[k])))
    return pairs


def _build_records(mode, path):
    model_v2.DC_FIT_MODE = mode
    try:
        n = cache_records(path)
    finally:
        model_v2.DC_FIT_MODE = "goals"
    return n


def gate_a():
    print("\n=== Gate A: meta stack (blend vs goals) ===")
    n_g = _build_records("goals", REC_GOALS)
    n_b = _build_records("blend", REC_BLEND)
    assert n_g == n_b, f"universe beda: goals={n_g} blend={n_b}"
    rg, rb = load_records(REC_GOALS), load_records(REC_BLEND)
    lg = eval_1x2(_records_meta_stack(rg))
    lb = eval_1x2(_records_meta_stack(rb))
    print(f"n={n_g:,}")
    print(f"stacked 1X2 log loss: goals={lg['log_loss']:.5f} "
          f"blend={lb['log_loss']:.5f}")
    ok = lb["log_loss"] <= lg["log_loss"]
    print(f"PASS? blend<=goals: {ok}")
    return ok, {"n": n_g, "goals": lg["log_loss"], "blend": lb["log_loss"]}


# ------------------------------------------------------------------ Gate B ----
def _deriv_price(lh, la, rho):
    m = [[pois(x, lh) * pois(y, la) * tau(x, y, lh, la, rho)
          for y in range(MAXG + 1)] for x in range(MAXG + 1)]
    s = sum(sum(row) for row in m)
    p_over25 = sum(m[x][y] for x in range(MAXG + 1) for y in range(MAXG + 1)
                   if x + y > 2) / s
    p0h = sum(m[0][y] for y in range(MAXG + 1)) / s
    p0a = sum(m[x][0] for x in range(MAXG + 1)) / s
    p_btts = 1.0 - p0h - p0a + m[0][0] / s
    return p_over25, p_btts


def _gateB_wf(seasons):
    """Walk-forward G & B; kembalikan per-match {ll_ov, br_ov, ll_bt, br_bt}."""
    import experiment_xg_dc as X
    X._ensure_loaded()
    matches, by_div = X.matches, X.by_div
    models = {d: {"G": DC(), "B": DC()} for d in TOP5}
    ptr = {d: 0 for d in TOP5}
    games_hist = {d: [] for d in TOP5}
    groups = defaultdict(list)
    for i, m in enumerate(matches):
        if m["season"] in seasons:
            groups[(m["div"], m["date"].year, m["date"].month)].append(i)
    out = {"G": [], "B": []}
    for key in sorted(groups):
        idxs = groups[key]
        start = min(matches[i]["date"] for i in idxs)
        assert all(matches[i]["date"] >= start for i in idxs), "leakage grup test"
        div = key[0]
        lst = by_div[div]
        while ptr[div] < len(lst) and matches[lst[ptr[div]]]["date"] < start:
            j = lst[ptr[div]]
            mm = matches[j]
            games_hist[div].append((mm["home"], mm["away"], mm["yh"], mm["ya"],
                                    mm["xgh"], mm["xga"], mm["date"]))
            ptr[div] += 1
        gh = games_hist[div]
        if gh:
            model_v2.DC_FIT_MODE = "goals"
            models[div]["G"].fit(gh, start, 270)
            model_v2.DC_FIT_MODE = "blend"
            models[div]["B"].fit(gh, start, 270)
            model_v2.DC_FIT_MODE = "goals"
        for i in idxs:
            mm = matches[i]
            for v in ("G", "B"):
                model = models[div][v]
                lh, la = model._lam(mm["home"], mm["away"])
                p_ov, p_bt = _deriv_price(lh, la, model.rho)
                y_ov = (mm["yh"] + mm["ya"] > 2)
                y_bt = (mm["yh"] > 0 and mm["ya"] > 0)
                eps = 1e-12
                ll_ov = -math.log(max(p_ov if y_ov else 1 - p_ov, eps))
                ll_bt = -math.log(max(p_bt if y_bt else 1 - p_bt, eps))
                br_ov = (p_ov - (1.0 if y_ov else 0.0)) ** 2
                br_bt = (p_bt - (1.0 if y_bt else 0.0)) ** 2
                out[v].append({"ll_ov": ll_ov, "br_ov": br_ov,
                               "ll_bt": ll_bt, "br_bt": br_bt})
    return out


def gate_b():
    print("\n=== Gate B: derivatif O/U 2.5 & BTTS (G vs B) ===")
    rows = _gateB_wf({"2021/22", "2022/23", "2023/24", "2024/25", "2025/26"})
    n = len(rows["G"])
    res = {}
    allok = True
    for market, llk, brk in (("over25", "ll_ov", "br_ov"),
                              ("btts", "ll_bt", "br_bt")):
        g_ll = sum(r[llk] for r in rows["G"]) / n
        b_ll = sum(r[llk] for r in rows["B"]) / n
        g_br = sum(r[brk] for r in rows["G"]) / n
        b_br = sum(r[brk] for r in rows["B"]) / n
        deg = b_ll - g_ll
        ok = deg <= GATE_B_DEGRADE
        allok = allok and ok
        print(f"{market}: n={n:,} | LL goals={g_ll:.5f} blend={b_ll:.5f} "
              f"(delta={deg:+.5f}) | Brier {g_br:.5f}->{b_br:.5f} | PASS? {ok}")
        res[market] = {"n": n, "ll_goals": g_ll, "ll_blend": b_ll,
                       "br_goals": g_br, "br_blend": b_br, "delta": deg}
    print(f"ALL PASS? {allok}")
    return allok, res


# ------------------------------------------------------------------ Gate C ----
def gate_c():
    print("\n=== Gate C: held-out 2017/18-2020/21 (G vs B) ===")
    rows = _wf_variants(HELD_OUT_SEASONS)
    overall = {}
    for v in ("G", "B"):
        overall[v], _ = _metrics(rows[v])
    g_ll = overall["G"][1]
    b_ll = overall["B"][1]
    ok = b_ll <= g_ll
    print(f"n={overall['G'][0]:,}")
    print(f"1X2 log loss: goals={g_ll:.5f} blend={b_ll:.5f} "
          f"(delta={b_ll - g_ll:+.5f}) | PASS? {ok}")
    return ok, {"n": overall["G"][0], "goals": g_ll, "blend": b_ll,
                "delta": b_ll - g_ll}


def main():
    t0 = time.time()
    results = {}
    try:
        results["A"], results["A_data"] = gate_a()
        results["B"], results["B_data"] = gate_b()
        results["C"], results["C_data"] = gate_c()
    finally:
        for p in (REC_GOALS, REC_BLEND):
            if os.path.exists(p):
                os.remove(p)
        for p in (REC_GOALS, REC_BLEND):
            mp = os.path.splitext(p)[0] + ".meta.json"
            if os.path.exists(mp):
                os.remove(mp)

    print("\n=== RINGKASAN GATE ===")
    allok = True
    for g in ("A", "B", "C"):
        print(f"Gate {g}: {'PASS' if results[g] else 'FAIL'}")
        allok = allok and results[g]
    print("\nVERDICT:", "SEMUA PASS -> siap flip default ke blend"
          if allok else "ADA GAGAL -> pertahankan default goals")
    print(f"runtime: {time.time() - t0:.0f}s")
    return results


if __name__ == "__main__":
    main()
