#!/usr/bin/env python3
"""experiment_edge_band.py — re-validasi live-pick edge band (Phase 5 S1).

Eksperimen-and-verdict, pola experiment_xg_dc.py. PRODUKSI TIDAK DIUBAH
(make_picks_live.py). Menjawab: apakah band produksi
  edge = p_meta(home) - p_fair_shin(home) in [0.20, 0.22)
  dan odds home B365 opening in [1.20, 1.50]
memiliki edge nyata? Walk-forward meta bulanan (leak-free), home-win only,
flat 1u, settle di odds_open.

Splits:
  diagnostics  = 2017/18-2022/23  (grid exploration)
  confirmation = 2023/24-2025/26  (evaluasi final, hanya 2 rule)

Grid diagnostics (landscape): edge thresholds 0.05..0.30 (step 0.025),
dengan & tanpa odds window. Best simple threshold = yield tertinggi di antara
threshold dengan >=100 pick diagnostic (tanpa odds window — murni edge).

Confirmation mengevaluasi tepat dua rule:
  R1  band produksi (edge [0.20,0.22) & odds [1.20,1.50])
  T*  best simple threshold dari diagnostics

Per-rule: n, seasons covered, hit rate, yield/ROI, paired bootstrap 95% CI
per-pick profit (10k), mean CLV (Shin de-vig pada close odds).
Verdict: VALIDATED / REPLACE / UNVALIDATED.
"""
import os as _os, sys as _sys
_sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))

import csv
import os
import time

import numpy as np

import model_features_1x2 as mf
from backtest_picks import _fair_probs, load_records
from football_etl import TOP5, normalize_name
import paths

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RECORDS = os.path.join(BASE, "records_cache.jsonl")

# parameter produksi (MIRROR make_picks_live.py — jangan diubah)
EDGE_LO, EDGE_HI = 0.20, 0.22
ODDS_LO, ODDS_HI = 1.20, 1.50

N_BOOT = 10000
GATE_MIN_PICKS = 100
GRID_EDGES = np.round(np.arange(0.05, 0.301, 0.025), 3)

DIAG_SEASONS = {f"{y}/{str(y+1)[-2:]}" for y in range(2017, 2023)}
CONF_SEASONS = {f"{y}/{str(y+1)[-2:]}" for y in range(2023, 2026)}

CLOSE_1X2 = (("PSCH", "PSCD", "PSCA"),
              ("AvgCH", "AvgCD", "AvgCA"),
              ("B365CH", "B365CD", "B365CA"))


def _logit_clip(p):
    return np.log(np.clip(p, 1e-6, 1 - 1e-6) / (1 - np.clip(p, 1e-6, 1 - 1e-6)))


def _num(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def _load_close_map():
    """{(div, date_iso, home_norm, away_norm) -> (o_1x2, None)}."""
    m = {}
    if not os.path.exists(paths.DATA_CLEAN):
        return m
    with open(paths.DATA_CLEAN, encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            div, dt = r.get("Div"), r.get("Date")
            if not div or not dt:
                continue
            h = normalize_name(r.get("HomeTeam") or "")
            a = normalize_name(r.get("AwayTeam") or "")
            if not h or not a:
                continue
            o = None
            for ch, cd, ca in CLOSE_1X2:
                vh, vd, va = _num(r.get(ch)), _num(r.get(cd)), _num(r.get(ca))
                if vh and vd and va:
                    o = (vh, vd, va)
                    break
            if o is not None:
                m[(div, dt[:10], h, a)] = o
    return m


def _wf_meta(records):
    """Walk-forward meta bulanan, 9-logit set (sama dgn _fit_meta produksi).

    Kembalikan array meta probs (n,3); None utk bulan tanpa train cukup.
    """
    n = len(records)
    X = np.full((n, 9), np.nan)
    y = np.zeros(n, dtype=np.int64)
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
        y[i] = r["yi"]
        dates[i] = r["date"]
    months = sorted({d[:7] for d in dates})
    pm = np.full((n, 3), np.nan)
    for m in months:
        train = np.array([d < m + "-01" for d in dates])
        test = np.array([d[:7] == m for d in dates])
        if train.sum() < 1500 or test.sum() == 0:
            continue
        p = mf._fit_multinomial(X[train], y[train], X[test])
        pm[test] = np.asarray(p)
    return pm


def _fair_home(o):
    f = _fair_probs(o, "shin")
    return f[0]


def _candidate_rows(records):
    """Baris kandidat home-win: TOP5, odds valid, meta prob ada."""
    pm = _wf_meta(records)
    rows = []
    for k, r in enumerate(records):
        if r["div"] not in TOP5:
            continue
        o = r["o"]
        if not o or min(o) <= 1.0:
            continue
        if np.isnan(pm[k, 0]):
            continue
        fair_h = _fair_home(o)
        edge = pm[k, 0] - fair_h
        rows.append({
            "div": r["div"], "season": r["season"], "date": r["date"],
            "home": r["home"], "away": r["away"],
            "yi": r["yi"], "o": o, "edge": edge,
            "pm_h": pm[k, 0],
        })
    return rows


def _profit(row):
    return (row["o"][0] - 1.0) if row["yi"] == 0 else -1.0


def _yield_only(rows):
    if not rows:
        return 0.0
    return float(np.mean([_profit(r) for r in rows]))


def _eval(rows):
    if not rows:
        return {"n": 0, "seasons": [], "wins": 0, "yield": 0.0,
                "ci": (0.0, (0.0, 0.0))}
    profits = np.array([_profit(r) for r in rows])
    n = len(profits)
    wins = int((profits > 0).sum())
    yield_ = float(profits.mean())
    mean_ci = _boot_ci(profits)
    return {"n": n, "seasons": sorted({r["season"] for r in rows}),
            "wins": wins, "yield": yield_, "ci": mean_ci}


def _boot_ci(profits):
    rng = np.random.default_rng(0)
    d = np.asarray(profits)
    n = len(d)
    means = np.empty(N_BOOT)
    for k in range(N_BOOT):
        means[k] = d[rng.integers(0, n, size=n)].mean()
    return float(means.mean()), (float(np.percentile(means, 2.5)),
                                 float(np.percentile(means, 97.5)))


def _mean_clv(rows, close_map):
    """Mean CLV home-win: p_fair_close(home)*odds_open - 1 (definisi ledger CLV)."""
    vals = []
    for r in rows:
        key = (r["div"], r["date"], normalize_name(r["home"]),
               normalize_name(r["away"]))
        oc = close_map.get(key)
        if oc is None:
            continue
        fair = _fair_probs(oc, "shin")
        clv_ev = fair[0] * r["o"][0] - 1.0
        vals.append(clv_ev)
    return float(np.mean(vals)) if vals else None


def _grid(rows):
    """Landscape diagnostics: (threshold, odds_window) -> {"n","yield"}."""
    res = {}
    for t in GRID_EDGES:
        for win in (True, False):
            sel = []
            for r in rows:
                if r["edge"] < t:
                    continue
                if win and not (ODDS_LO <= r["o"][0] <= ODDS_HI):
                    continue
                sel.append(r)
            res[(float(t), win)] = {"n": len(sel), "yield": _yield_only(sel)}
    return res


def _best_simple(grid):
    """Best simple threshold: yield tertinggi >=GATE_MIN_PICKS, tanpa odds window."""
    best = (None, -1e9)
    for (t, win), v in grid.items():
        if win:
            continue
        if v["n"] >= GATE_MIN_PICKS and v["yield"] > best[1]:
            best = (t, v["yield"])
    return best[0]


def _rule_rows(rows, t_lo, t_hi, use_window):
    sel = []
    for r in rows:
        if t_hi is not None and not (t_lo <= r["edge"] < t_hi):
            continue
        if t_hi is None and r["edge"] < t_lo:
            continue
        if use_window and not (ODDS_LO <= r["o"][0] <= ODDS_HI):
            continue
        sel.append(r)
    return sel


def _fmt_rule(name, res, clv):
    print(f"\n-- {name} --")
    if res["n"] == 0:
        print("  n=0 (tidak ada pick)")
        return
    print(f"  n        : {res['n']}")
    print(f"  seasons  : {', '.join(res['seasons'])}")
    print(f"  hit rate : {res['wins']/res['n']:.3f} ({res['wins']}/{res['n']})")
    print(f"  yield    : {res['yield']:+.3f} (per-pick profit, 1u flat)")
    print(f"  boot 95%: [{res['ci'][1][0]:+.3f}, {res['ci'][1][1]:+.3f}]")
    print(f"  mean CLV : {clv:+.4f}" if clv is not None
          else "  mean CLV : n/a (close odds tidak lengkap)")


def _freq_per_season(rows):
    d = {}
    for r in rows:
        d[r["season"]] = d.get(r["season"], 0) + 1
    return d


def main():
    t0 = time.time()
    print("=== EXPERIMEN EDGE BAND (live pick) — re-validasi ===")
    print("produksi TIDAK diubah; mirror make_picks_live.main (meta probs vs "
          "shin fair opening, home-win, flat 1u, settle odds_open)")
    records = load_records(RECORDS)
    cand = _candidate_rows(records)
    print(f"\nrecords: {len(records):,} | kandidat home-win TOP5: {len(cand):,}")

    diag = [r for r in cand if r["season"] in DIAG_SEASONS]
    conf = [r for r in cand if r["season"] in CONF_SEASONS]
    print(f"diagnostics {min(DIAG_SEASONS)}-{max(DIAG_SEASONS)}: {len(diag):,}")
    print(f"confirmation {min(CONF_SEASONS)}-{max(CONF_SEASONS)}: {len(conf):,}")

    # grid diagnostics
    grid = _grid(diag)
    print("\n-- landscape diagnostics (yield per-pick, 1u flat) --")
    header = "threshold | n>=100 odds-off | n>=100 odds-on  | odds-off yield | odds-on yield"
    print(header)
    for t in GRID_EDGES:
        off = grid[(float(t), False)]
        on = grid[(float(t), True)]
        print(f"  {t:.3f}  | {off['n']:>6} {off['n']>=GATE_MIN_PICKS!s:>5} | "
              f"{on['n']:>6} {on['n']>=GATE_MIN_PICKS!s:>5} | "
              f"{off['yield']:+8.4f} | {on['yield']:+8.4f}")

    # distribusi edge kandidat (untuk laporan)
    edges = np.array([r["edge"] for r in cand])
    print("\n-- distribusi edge kandidat (semua musim) --")
    print(f"  mean={edges.mean():+.4f} std={edges.std():.4f} "
          f"min={edges.min():+.4f} max={edges.max():+.4f}")
    print(f"  percentil: 50%={np.percentile(edges,50):+.4f} "
          f"90%={np.percentile(edges,90):+.4f} "
          f"95%={np.percentile(edges,95):+.4f} "
          f"99%={np.percentile(edges,99):+.4f}")
    print(f"  fraction edge>=0.05: {(edges>=0.05).mean():.4f} "
          f"edge>=0.10: {(edges>=0.10).mean():.4f} "
          f"edge>=0.20: {(edges>=0.20).mean():.4f}")

    tstar = _best_simple(grid)
    if tstar is None:
        print("\nbest simple threshold: TIDAK ADA threshold mencapai >=100 pick diagnostic "
              "(kriteria gagal) -> T* tidak dievaluasi")
    else:
        print(f"\nbest simple threshold (diag, >=100 pick, tanpa odds window): "
              f"edge >= {tstar:.3f}")

    # frekuensi R1 per season
    r1_all = _rule_rows(cand, EDGE_LO, EDGE_HI, True)
    freq = _freq_per_season(r1_all)
    total_r1 = sum(freq.values())
    print(f"\nR1 (band produksi) frekuensi historis: {total_r1} pick total")
    for s in sorted(freq):
        print(f"    {s}: {freq[s]}")
    if freq and total_r1 / len(freq) < 20:
        print("  -> rata-rata <20 pick/musim: jalur live bersifat dekoratif "
              "(jarang memicu).")

    # confirmation: R1 vs T*
    close_map = _load_close_map()
    print(f"\nclose map size: {len(close_map)}")
    print("\n=== CONFIRMATION (2023/24-2025/26) ===")
    r1_rows = _rule_rows(conf, EDGE_LO, EDGE_HI, True)
    r1 = _eval(r1_rows)
    _fmt_rule("R1 band produksi edge[0.20,0.22) & odds[1.20,1.50]",
               r1, _mean_clv(r1_rows, close_map))

    if tstar is None:
        ts = {"n": 0, "seasons": [], "wins": 0, "yield": 0.0,
              "ci": (0.0, (0.0, 0.0))}
        print("\n-- T* --\n  tidak dievaluasi (tidak ada threshold >=100 pick diagnostic)")
    else:
        ts_rows = _rule_rows(conf, tstar, None, False)
        ts = _eval(ts_rows)
        _fmt_rule(f"T* edge >= {tstar:.3f} (tanpa odds window)",
                   ts, _mean_clv(ts_rows, close_map))

    # verdict
    c1 = r1["n"] >= GATE_MIN_PICKS and r1["ci"][1][0] > 0.0
    c2 = ts["n"] >= GATE_MIN_PICKS and ts["ci"][1][0] > 0.0
    if c1:
        verdict = "VALIDATED"
    elif c2:
        verdict = "REPLACE"
    else:
        verdict = "UNVALIDATED"
    print("\n=== VERDICT ===")
    print(f"R1 n={r1['n']} yield={r1['yield']:+.3f} "
          f"CI95%=[{r1['ci'][1][0]:+.3f},{r1['ci'][1][1]:+.3f}]")
    print(f"T* n={ts['n']} yield={ts['yield']:+.3f} "
          f"CI95%=[{ts['ci'][1][0]:+.3f},{ts['ci'][1][1]:+.3f}] (eval hanya jika T* ada)")
    print(f"verdict: {verdict}")
    print(f"\nruntime: {time.time()-t0:.0f}s")


if __name__ == "__main__":
    main()
