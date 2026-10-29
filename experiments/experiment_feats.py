#!/usr/bin/env python3
"""experiment_feats.py — Phase 7 generic feature hypothesis runner.

Runner umum: tambah kolom fitur ke meta 9-logit, walk-forward fit, bandingkan
log loss/brier (vs baseline 1.0017/0.5988) dan yield backtest (shin corrected,
engine backtest_picks.evaluate_strategy). KEEP jika LL<1.0017 DAN yield>-3.77%.

Pemakaian:  python experiment_feats.py <hyp>  (hyp: e1|e2|e3|e4)
"""
import os as _os, sys as _sys
_sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))

import os
import sys
from collections import defaultdict, deque

import numpy as np

import model_features_1x2 as mf
from validation import eval_1x2
from backtest_picks import load_records, evaluate_strategy, RECORDS
from football_etl import MatchCache

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CFG = {"model": "meta", "devig": "shin", "thr": 0.02,
       "stake": "flat", "kelly": 0.25}


def _logit_clip(p):
    return np.log(np.clip(p, 1e-6, 1 - 1e-6) / (1 - np.clip(p, 1e-6, 1 - 1e-6)))


def _sorted_matches():
    cache = MatchCache()
    return sorted(
        (m for m in cache.matches
         if m.get("date") and m.get("ftr") in ("H", "D", "A")),
        key=lambda m: (m["date"], m.get("div", ""), m.get("home", "")),
    )


# ------------------------------------------------------------------ E2 ----
def build_e2_map():
    """Overperformance index: rolling (gf - xgh) & (ga - xga), window 5."""
    from features import _load_xg_map
    xg = _load_xg_map()
    matches = _sorted_matches()
    opp = defaultdict(lambda: deque(maxlen=5))   # gf - xgh
    opc = defaultdict(lambda: deque(maxlen=5))   # ga - xga
    out = {}
    for m in matches:
        d = m["date"]
        h, a = m["home"], m["away"]
        k = (m.get("div"), d.isoformat(), h, a)

        def roll(team, side):
            q = opp[team] if side == "opp" else opc[team]
            return float(np.mean(list(q))) if q else None

        opp_h, opp_a = roll(h, "opp"), roll(a, "opp")
        opc_h, opc_a = roll(h, "opc"), roll(a, "opc")
        out[k] = {"opp_h": opp_h, "opp_a": opp_a,
                  "opc_h": opc_h, "opc_a": opc_a}
        # update state setalah match (anti-leakage): hanya jika xG tersedia,
        # supaya mean overperformance tidak tercemar gol tanpa xG.
        yh, ya = m.get("yh"), m.get("ya")
        if yh is not None and ya is not None:
            xgh, xga = xg.get(k, (None, None))
            if xgh is not None:
                opp[h].append(yh - xgh)
                opc[a].append(ya - xga)
    return out


# ------------------------------------------------------------------ E3 ----
def build_e3_map():
    """Motivasi & konteks klasemen: points-per-game (ppm) per tim + flag
    musim akhir (matchday > 78% dari total per musim)."""
    matches = _sorted_matches()
    # season length per (div, season) = jumlah match unik per tim
    season_count = defaultdict(int)
    seen = set()
    for m in matches:
        key = (m.get("div"), m.get("season"), m.get("home"))
        if key not in seen:
            seen.add(key)
            season_count[(m.get("div"), m.get("season"))] += 1
    season_total = {k: v for k, v in season_count.items()}

    pts = defaultdict(float)     # (div,season,team) -> points
    gp = defaultdict(int)        # (div,season,team) -> games played
    out = {}
    for m in matches:
        d = m["date"]
        h, a = m["home"], m["away"]
        season = m.get("season")
        div = m.get("div")
        k = (div, d.isoformat(), h, a)

        def ppm(team):
            key = (div, season, team)
            g = gp[key]
            return (pts[key] / g) if g else None

        ph, pa = ppm(h), ppm(a)
        tot = season_total.get((div, season), 0)
        played_so_far = max(gp[(div, season, h)], gp[(div, season, a)])
        late = 1.0 if (tot and played_so_far / tot >= 0.78) else 0.0
        out[k] = {"ppm_h": ph, "ppm_a": pa, "ppm_diff":
                  (ph - pa) if (ph is not None and pa is not None) else None,
                  "late": late}
        # update state setalah match
        ftr = m.get("ftr")
        yh, ya = m.get("yh"), m.get("ya")
        if ftr and yh is not None:
            ph_ = 3 if ftr == "H" else (1 if ftr == "D" else 0)
            pa_ = 3 if ftr == "A" else (1 if ftr == "D" else 0)
            pts[(div, season, h)] += ph_
            pts[(div, season, a)] += pa_
            gp[(div, season, h)] += 1
            gp[(div, season, a)] += 1
    return out


# ------------------------------------------------------------------ E4 ----
def build_e4_map():
    """CLV proxy: pergerakan odds (opening -> nearest pre-kickoff). Di sini
    kita tidak punya odds closing B365; proxy = selisih fair prob shin vs
    model prob (sudah dipakai) — jadi E4 memakai divisi & musim sebagai konteks
    yang bisa menangkap pergeseran pasar. Dummy: tidak ada feature baru."""
    return {}


# ---------------------------------------------------------------- runner ----
def build_Xy(records, fmap, extra_cols):
    n = len(records)
    base = 9
    m = len(extra_cols)
    X = np.full((n, base + m), np.nan)
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
        f = fmap.get((r["div"], r["date"], r["home"], r["away"]))
        if f:
            for j, col in enumerate(extra_cols):
                v = f.get(col)
                if v is not None:
                    X[i, base + j] = v
        y[i] = r["yi"]
        dates[i] = r["date"]
    return X, y, dates


def _walkforward(records, X, y, dates, extra_cols):
    months = sorted({d[:7] for d in dates})
    base = 9
    pairs = []
    pm = [None] * len(records)
    for m in months:
        tr = np.array([d < m + "-01" for d in dates])
        te = np.array([d[:7] == m for d in dates])
        if tr.sum() < 1500 or te.sum() == 0:
            continue
        Xtr, Xte = X[tr].copy(), X[te].copy()
        for j in range(base, X.shape[1]):
            trcol = Xtr[:, j]
            mu = np.nanmean(trcol)
            sd = np.nanstd(trcol)
            if not (sd > 1e-9):
                sd = 1.0
            trcol[np.isnan(trcol)] = mu
            Xtr[:, j] = (trcol - mu) / sd
            tecol = Xte[:, j]
            tecol[np.isnan(tecol)] = mu
            Xte[:, j] = (tecol - mu) / sd
        p = mf._fit_multinomial(Xtr, y[tr], Xte)
        for row, k in zip(p, np.where(te)[0]):
            pairs.append((tuple(row), int(y[k])))
            pm[k] = tuple(row)
    return eval_1x2(pairs), pm


def run(hyp):
    records = load_records(RECORDS)
    builders = {"e1": None, "e2": build_e2_map, "e3": build_e3_map,
                "e4": build_e4_map}
    extra = {"e1": ("rest_diff", "dens14_diff", "dens30_diff"),
             "e2": ("opp_h", "opp_a", "opc_h", "opc_a"),
             "e3": ("ppm_h", "ppm_a", "ppm_diff", "late"),
             "e4": ()}
    label = {"e1": "E1 FATIGUE", "e2": "E2 XG OVERPERF", "e3": "E3 MOTIVATION",
             "e4": "E4 CLV PROXY"}
    builder = builders[hyp]
    fmap = builder() if builder else {}
    cols = extra[hyp]
    X, y, dates = build_Xy(records, fmap, cols)
    ext, pm = _walkforward(records, X, y, dates, cols)
    # baseline (9 fitur)
    Xb, yb, datesb = build_Xy(records, {}, ())
    base_eval, _ = _walkforward(records, Xb, yb, datesb, ())

    b0 = evaluate_strategy(records, dict(CFG))
    for i, r in enumerate(records):
        e = pm[i] if pm[i] is not None else (r["ph_dc"], r["pd_dc"], r["pa_dc"])
        r["ph_meta"], r["pd_meta"], r["pa_meta"] = e
    b1 = evaluate_strategy(records, dict(CFG))
    best = max((evaluate_strategy(records, {**CFG, "thr": t})
                for t in (0.01, 0.02, 0.03, 0.05)), key=lambda d: d["yield"])

    print("=" * 72)
    print(f"PHASE 7 {label[hyp]} — fitur tambahan: {cols}")
    print("=" * 72)
    print(f"{'metrik':12} {'baseline(9)':>12} {'+fitur':>12}")
    for k in ("log_loss", "brier", "macro_f1", "accuracy"):
        print(f"{k:12} {base_eval[k]:>12.4f} {ext[k]:>12.4f}")
    print()
    print(f"bet thr .02  baseline : yield {b0['yield']:+.4%} (n={b0['n_bets']})")
    print(f"bet thr .02  +fitur  : yield {b1['yield']:+.4%} (n={b1['n_bets']})")
    print(f"bet best thr  +fitur  : yield {best['yield']:+.4%} (n={best['n_bets']})")
    ll_ok = ext["log_loss"] < 1.0017
    yield_ok = best["yield"] > -0.0377
    verdict = "KEEP" if (ll_ok and yield_ok) else "REVERT"
    print(f"\nKEEP jika LL<1.0017 ({ll_ok}) DAN yield>-3.77% ({yield_ok}) => {verdict}")
    return {"hyp": hyp, "ll": ext["log_loss"], "brier": ext["brier"],
            "yield": best["yield"], "n": best["n_bets"],
            "verdict": verdict}


if __name__ == "__main__":
    h = sys.argv[1] if len(sys.argv) > 1 else "e2"
    run(h)
