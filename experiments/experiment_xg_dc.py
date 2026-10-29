#!/usr/bin/env python3
"""experiment_xg_dc.py — DC fit pada xG vs gol: apakah xG meningkatkan 1X2 OOS?

Varian (fold identik, hl sama, MAX_TRAIN sama):
  G: gol (fit produksi sekarang — kontrol).
  X: murni xG — fit rating pada xG for/against. Rho TIDAK dipilih dari
     "scoreline" xG; dipakai ulang rho yang dipilih fit gol pada window latih
     yang sama.
  B: campuran — kuantitas observasi = 0.5*gol + 0.5*xG, alpha ditetapkan
     a priori (tidak di-tune pada fold test).

Evaluasi: walk-forward bulanan (sama dengan produksi, hl=270, freq='m') pada
musim test (2021/22-2025/26), hanya league-season dengan cakupan xG asli
(Understat). Metrik: log-loss (utama), Brier, n per liga & overall. Signifikansi:
bootstrap berpasangan 10k resample atas selisih per-match log-loss, CI 95%.

Adoption gate terhadap G:
  1) log-loss overall < G
  2) bootstrap CI 95% selisih mengecualikan 0
  3) tidak lebih buruk dari G > 0.005 log-loss di lebih dari satu liga

Model produksi (model_v2.py) TIDAK diubah. Hanya eksperimen.
"""
from __future__ import annotations
import os as _os, sys as _sys
_sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))

import csv
import math
import os
import sys
import time
from collections import defaultdict
from datetime import datetime

import numpy as np

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE)

from football_etl import normalize_name
from features import _load_xg_map
from model_v2 import DC, brier3, YIDX

DATA = os.path.join(BASE, "all_matches_clean.csv")
TOP5 = ["E0", "SP1", "D1", "I1", "F1"]
TEST_SEASONS = {"2021/22", "2022/23", "2023/24", "2024/25", "2025/26"}
HL = 270
MAX_TRAIN = 4000
N_BOOT = 10_000
ALPHA = 0.5
GATE_WORSE = 0.005  # ambang "lebih buruk" per liga

matches = []
by_div = None


def _ensure_loaded():
    """Muat matches TOP5 dgn gol + xG; hanya yang punya xG asli (universum sama)."""
    global matches, by_div
    if by_div is not None:
        return
    xg = _load_xg_map()
    loaded = []
    with open(DATA, encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            if r["Div"] not in TOP5 or not r["Date"] or r["FTR"] not in ("H", "D", "A"):
                continue
            d = datetime.strptime(r["Date"], "%Y-%m-%d").date()
            h, a = normalize_name(r["HomeTeam"]), normalize_name(r["AwayTeam"])
            x = xg.get((r["Div"], r["Date"][:10], h, a))
            if x is None:
                continue  # tanpa xG -> tidak masuk eksperimen (league-season tanpa cakupan)
            try:
                yh, ya = int(r["FTHG"]), int(r["FTAG"])
            except (TypeError, ValueError):
                continue
            loaded.append({
                "div": r["Div"], "date": d, "season": r["Season"],
                "home": h, "away": a, "yh": yh, "ya": ya,
                "ftr": r["FTR"], "xgh": x[0], "xga": x[1],
            })
    loaded.sort(key=lambda m: m["date"])
    bd = defaultdict(list)
    for i, m in enumerate(loaded):
        bd[m["div"]].append(i)
    matches = loaded
    by_div = bd


class DC_rho(DC):
    """DC dgn rho dikunci (dipakai varian X/B; rho diambil dari fit gol)."""

    def __init__(self, rho=None):
        super().__init__()
        self._fixed = rho

    def fit(self, games, cutoff, hl):
        super().fit(games, cutoff, hl)
        if self._fixed is not None:
            self.rho = self._fixed


def _wf_variants(seasons):
    """Walk-forward bulanan identik untuk G/X/B; kembalikan per-match {ll, br, div}."""
    _ensure_loaded()
    models = {d: {"G": DC(), "X": DC_rho(), "B": DC_rho()} for d in TOP5}
    ptr = {d: 0 for d in TOP5}
    games_hist = {d: [] for d in TOP5}
    groups = defaultdict(list)
    for i, m in enumerate(matches):
        if m["season"] in seasons:
            key = (m["div"], m["date"].year, m["date"].month)
            groups[key].append(i)
    out = {"G": [], "X": [], "B": []}
    nfits = 0
    for key in sorted(groups):
        idxs = groups[key]
        start = min(matches[i]["date"] for i in idxs)
        # Anti-leakage: seluruh match dlm grup test ini berada setelah training.
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
            G_games = [(h, a, yh, ya, dt) for h, a, yh, ya, xgh, xga, dt in gh]
            X_games = [(h, a, xgh, xga, dt) for h, a, yh, ya, xgh, xga, dt in gh]
            B_games = [(h, a, ALPHA * yh + (1 - ALPHA) * xgh,
                        ALPHA * ya + (1 - ALPHA) * xga, dt)
                       for h, a, yh, ya, xgh, xga, dt in gh]
            g = models[div]["G"]
            g.fit(G_games, start, HL)
            x = models[div]["X"]; x._fixed = g.rho
            x.fit(X_games, start, HL)
            b = models[div]["B"]; b._fixed = g.rho
            b.fit(B_games, start, HL)
            nfits += 1
        for i in idxs:
            mm = matches[i]
            yi = YIDX[mm["ftr"]]
            for variant, model in (("G", models[div]["G"]),
                                   ("X", models[div]["X"]),
                                   ("B", models[div]["B"])):
                lh, la = model._lam(mm["home"], mm["away"])
                pr = model.probs(lh, la)
                p = (pr["ph"], pr["pd"], pr["pa"])
                ll = -math.log(max(p[yi], 1e-12))
                out[variant].append({"div": mm["div"], "ll": ll, "br": brier3(p, yi)})
    print(f"  [wf {sorted(seasons)} hl={HL} freq=m] fits={nfits} "
          f"pred={len(out['G']):,}")
    return out


def _metrics(rows):
    n = len(rows)
    ll = sum(r["ll"] for r in rows) / n
    br = sum(r["br"] for r in rows) / n
    agg = defaultdict(lambda: [0, 0.0, 0.0])
    for r in rows:
        c = agg[r["div"]]; c[0] += 1; c[1] += r["ll"]; c[2] += r["br"]
    per = {d: (c[0], c[1] / c[0], c[2] / c[0]) for d, c in agg.items()}
    return (n, ll, br), per


def _boot_ci(diff):
    rng = np.random.default_rng(0)
    d = np.asarray(diff)
    n = len(d)
    means = np.empty(N_BOOT)
    for k in range(N_BOOT):
        means[k] = d[rng.integers(0, n, size=n)].mean()
    return float(means.mean()), (float(np.percentile(means, 2.5)),
                                 float(np.percentile(means, 97.5)))


def _verdict(overall, per, g_overall, g_per, ci):
    worse = sum(1 for d in TOP5
                if (per.get(d, (0, 0, 0))[1] - g_per.get(d, (0, 0, 0))[1]) > GATE_WORSE)
    c1 = overall[1] < g_overall[1]
    c2 = ci[1][0] > 0 or ci[1][1] < 0
    c3 = worse <= 1
    return c1, c2, c3, worse


def main():
    t0 = time.time()
    print("=== EXPERIMEN xG vs GOL (DC fit) ===")
    print("cakupan: hanya league-season dgn xG Understat asli (2017/18-2025/26); "
          "2026/27 (parsial) dikecualikan; tanpa imputasi.")
    rows = _wf_variants(TEST_SEASONS)

    overall = {}
    per = {}
    for v in ("G", "X", "B"):
        overall[v], per[v] = _metrics(rows[v])

    # selisih per-match log-loss
    by_i = {v: {r["div"]: [] for r in rows[v]} for v in rows}
    diff_XG = [x["ll"] - g["ll"] for g, x in zip(rows["G"], rows["X"])]
    diff_BG = [b["ll"] - g["ll"] for g, b in zip(rows["G"], rows["B"])]
    ci_XG = _boot_ci(diff_XG)
    ci_BG = _boot_ci(diff_BG)

    print("\n-- overall (test 2021/22-2025/26) --")
    print(f"n={overall['G'][0]:,}")
    print(f"{'variant':>3} {'logloss':>9} {'Brier':>9}")
    for v in ("G", "X", "B"):
        print(f"{v:>3} {overall[v][1]:9.5f} {overall[v][2]:9.5f}")

    print("\n-- per liga (logloss) --")
    print(f"{'league':>5} {'G':>9} {'X':>9} {'B':>9} {'n':>6}")
    for d in TOP5:
        print(f"{d:>5} "
              f"{per['G'].get(d,(0,0,0))[1]:9.5f} "
              f"{per['X'].get(d,(0,0,0))[1]:9.5f} "
              f"{per['B'].get(d,(0,0,0))[1]:9.5f} "
              f"{per['G'].get(d,(0,0,0))[0]:6d}")

    print("\n-- bootstrap berpasangan (selisih log-loss vs G, CI 95%) --")
    print(f"X-G: mean {ci_XG[0]:+.5f} CI [{ci_XG[1][0]:+.5f}, {ci_XG[1][1]:+.5f}]")
    print(f"B-G: mean {ci_BG[0]:+.5f} CI [{ci_BG[1][0]:+.5f}, {ci_BG[1][1]:+.5f}]")

    print("\n-- adoption gate (vs G) --")
    g_overall = overall["G"]; g_per = per["G"]
    for v in ("X", "B"):
        c1, c2, c3, worse = _verdict(overall[v], per[v], g_overall, g_per,
                                      ci_XG if v == "X" else ci_BG)
        print(f"{v}: LL{overall[v][1]:.5f}<G{g_overall[1]:.5f}? {c1} | "
              f"CI exclude 0? {c2} | worse>0.005 liga={worse} (<=1? {c3})")
        verdict = "PASS" if (c1 and c2 and c3) else "FAIL"
        if verdict == "PASS":
            print(f"  -> {v} LULUS gate. Rekomendasi: switch produksi ke {v} "
                  f"(tidak diimplementasikan di tugas ini).")
        else:
            print(f"  -> {v} tidak lulus. Verdict: keep goals.")

    runtime = time.time() - t0
    print(f"\nruntime: {runtime:.0f}s")
    return {"overall": overall, "per": per, "ci": {"XG": ci_XG, "BG": ci_BG},
            "runtime": runtime}


if __name__ == "__main__":
    main()
