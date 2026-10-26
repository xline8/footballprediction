#!/usr/bin/env python3
"""experiment_motiv.py — Phase 8: Dual-Gate evaluation of motivation hypotheses.

Dual-Gate (pre-fixed thr = 0.05, shin, flat):
  1. Log Loss Safety : LL_ext <= 1.00170 (tidak boleh degrade).
  2. Fixed-Threshold Yield: yield(thr .05) > -3.77% DAN n >= 2000.

Hipotesis 8.1–8.4 dibangun di atas papan klasemen incrementally (leak-free) +
fatigue (rest/density). Runner memakai ef._walkforward utk fitur tambahan.
"""

import os
import sys
from collections import defaultdict, deque

import numpy as np

import experiment_feats as ef
from backtest_picks import evaluate_strategy, load_records, RECORDS

CFG = {"model": "meta", "devig": "shin", "thr": 0.05,
       "stake": "flat", "kelly": 0.25}
LL_BAR = 1.00170
YLD_BAR = -0.0377
MIN_N = 2000


def _sorted_matches():
    return ef._sorted_matches()


def build_maps():
    """Tuple (fmap, smap):
    fmap[(div,date,home,away)] -> rest/14/30 per tim (fatigue, E1)
    smap[(div,date,home,away)] -> konteks klasemen per match.
    """
    matches = _sorted_matches()
    played = defaultdict(list)          # team -> recent dates
    table = defaultdict(lambda: defaultdict(lambda: [0, 0, 0]))  # (div,season)->team->[pts,gd,gp]
    teams = defaultdict(set)            # (div,season) -> teams
    fmap, smap = {}, {}

    for m in matches:
        d = m["date"]
        h, a = m["home"], m["away"]
        season, div = m.get("season"), m.get("div")
        key = (div, season)
        k = (div, d.isoformat(), h, a)

        # ---- fatigue (E1)
        def fstats(team):
            dl = [x for x in played[team] if x < d]
            rest = (d - dl[-1]).days if dl else None
            n14 = sum(1 for x in dl if (d - x).days <= 14)
            n30 = sum(1 for x in dl if (d - x).days <= 30)
            return rest, n14, n30
        rh, h14, h30 = fstats(h)
        ra, a14, a30 = fstats(a)
        if rh is not None and ra is not None:
            fmap[k] = {"rest_diff": float(np.clip(rh - ra, -15, 15)),
                       "dens14": float(h14 - a14), "dens30": float(h30 - a30)}

        # ---- standings (E3 deep)
        teams[key].update((h, a))
        t = table[key]
        n = len(teams[key])
        season_len = 2 * (n - 1) if n > 1 else 34

        def pos_and_cutoffs(team):
            pts, gd, gp = t[team]
            r = 1
            for x in t:
                if x == team:
                    continue
                px, gx, _ = t[x]
                if (px, gx) > (pts, gd):
                    r += 1
            arr = sorted(((t[x][0], t[x][1]) for x in t), reverse=True)
            topK = max(1, round(n * 0.25))
            pts_euro = arr[min(topK, n) - 1][0] if arr else 0
            pts_releg = arr[max(n - 3, 0)][0] if n >= 4 else 0
            pts_lead = arr[0][0] if arr else 0
            dist_euro = pts_euro - pts            # +: ketinggalan; -: sudah di zona
            dist_releg = pts - pts_releg          # +: aman; -: di zona degradasi
            dist_title = pts_lead - pts
            late = (season_len - gp) <= 10
            return r, pts, n, topK, dist_euro, dist_releg, dist_title, late

        ph, pts_h, _, _, eur_h, rel_h, tit_h, late_h = pos_and_cutoffs(h)
        pa, pts_a, _, _, eur_a, rel_a, tit_a, late_a = pos_and_cutoffs(a)
        smap[k] = {"pos_h": ph, "pos_a": pa, "n": n,
                   "dist_euro_h": eur_h, "dist_euro_a": eur_a,
                   "dist_releg_h": rel_h, "dist_releg_a": rel_a,
                   "dist_title_h": tit_h, "dist_title_a": tit_a,
                   "late_h": float(late_h), "late_a": float(late_a)}

        # update state
        ftr = m.get("ftr")
        yh, ya = m.get("yh"), m.get("ya")
        if ftr and yh is not None:
            ph_ = 3 if ftr == "H" else (1 if ftr == "D" else 0)
            pa_ = 3 if ftr == "A" else (1 if ftr == "D" else 0)
            t[h][0] += ph_; t[h][1] += yh - ya; t[h][2] += 1
            t[a][0] += pa_; t[a][1] += ya - yh; t[a][2] += 1
        played[h].append(d)
        played[a].append(d)

    return fmap, smap


def mot_index(s, team_pos):
    """Motivasi kontinu [0,1] dari konteks klasemen + flag late."""
    pos = s[f"pos_{team_pos}"]
    n = s["n"]
    late = s[f"late_{team_pos}"]
    if not late:
        return 0.5
    topK = max(1, round(n * 0.25))
    m = 0.5
    if pos <= topK:
        m += 0.35
    if pos >= n - 2:
        m += 0.35
    if topK + 3 < pos < n - 4:
        m -= 0.35
    return min(1.0, max(0.0, m))


def hyp_features(hyp, fmap, smap):
    """Return (rec_key -> dict kolom fitur) utk hipotesis tertentu."""
    import math
    rec = {}
    for k, s in smap.items():
        h = rec.setdefault(k, {})
        nh, na = s["n"], s["n"]
        mh, ma = mot_index(s, "h"), mot_index(s, "a")
        lateh, latea = s["late_h"], s["late_a"]
        despo_h = 1.0 if (lateh and s["dist_releg_h"] < 0) else 0.0
        despo_a = 1.0 if (latea and s["dist_releg_a"] < 0) else 0.0
        nothing_h = 1.0 if (lateh and s.get("dist_releg_h", 9) > 3
                            and abs(s["dist_euro_h"]) > 3) else 0.0
        nothing_a = 1.0 if (latea and s.get("dist_releg_a", 9) > 3
                            and abs(s["dist_euro_a"]) > 3) else 0.0

        if hyp == "e81":
            h["despo_h"] = despo_h; h["despo_a"] = despo_a
            h["nothing_h"] = nothing_h; h["nothing_a"] = nothing_a
            h["inter_h"] = despo_h * nothing_a
            h["inter_a"] = despo_a * nothing_h
            h["rel_h"] = s["dist_releg_h"]; h["rel_a"] = s["dist_releg_a"]
            h["eur_h"] = s["dist_euro_h"]; h["eur_a"] = s["dist_euro_a"]

        elif hyp == "e82":
            u_h = lateh / (1.0 + min(abs(s["dist_releg_h"]), abs(s["dist_euro_h"]),
                                     abs(s["dist_title_h"])))
            u_a = latea / (1.0 + min(abs(s["dist_releg_a"]), abs(s["dist_euro_a"]),
                                     abs(s["dist_title_a"])))
            h["u_h"] = u_h; h["u_a"] = u_a
            h["gd_h"] = float(s["pos_h"] < s["pos_a"] and lateh)   # urgency high
            h["gd_a"] = float(s["pos_a"] < s["pos_h"] and latea)
            h["rel_h"] = s["dist_releg_h"]; h["rel_a"] = s["dist_releg_a"]

        elif hyp == "e84":
            f = fmap.get(k, {})
            rd = f.get("rest_diff", 0.0)
            h["rest_diff"] = rd
            h["despo_h"] = despo_h; h["despo_a"] = despo_a
            h["stack_h"] = rd * despo_h
            h["stack_a"] = (-rd) * despo_a
            h["mot_diff"] = mh - ma
    return rec


def run(hyp):
    records = load_records(RECORDS)
    fmap, smap = build_maps()
    if hyp == "e83":
        # DC × motivasi: dlam = ph_dc - pa_dc (proxy Δλ), dikalikan motivasi
        rindex = {(r["div"], r["date"], r["home"], r["away"]): r for r in records}
        feat = {}
        for k, s in smap.items():
            r = rindex.get(k)
            if r is None:
                continue
            dlam = r["ph_dc"] - r["pa_dc"]
            mh, ma = mot_index(s, "h"), mot_index(s, "a")
            feat[k] = {"dmot_main": dlam * (mh - ma),
                       "dmot_h": dlam * mh, "dmot_a": dlam * ma,
                       "mot_diff": mh - ma}
        cols = ("dmot_main", "dmot_h", "dmot_a", "mot_diff")
    else:
        cols = {"e81": ("despo_h", "despo_a", "nothing_h", "nothing_a",
                        "inter_h", "inter_a", "rel_h", "rel_a", "eur_h", "eur_a"),
                "e82": ("u_h", "u_a", "gd_h", "gd_a", "rel_h", "rel_a"),
                "e84": ("rest_diff", "despo_h", "despo_a", "stack_h", "stack_a",
                        "mot_diff")}[hyp]
        feat = hyp_features(hyp, fmap, smap)

    # Suntik fitur ke records via fmap-style dict (join by key)
    X, y, dates = ef.build_Xy(records, feat, cols)
    ext, pm = ef._walkforward(records, X, y, dates, cols)
    Xb, yb, datesb = ef.build_Xy(records, {}, ())
    base_eval, _ = ef._walkforward(records, Xb, yb, datesb, ())

    b0 = evaluate_strategy(records, dict(CFG))          # baseline thr .05
    for i, r in enumerate(records):
        e = pm[i] if pm[i] is not None else (r["ph_dc"], r["pd_dc"], r["pa_dc"])
        r["ph_meta"], r["pd_meta"], r["pa_meta"] = e
    b1 = evaluate_strategy(records, dict(CFG))          # + fitur thr .05

    ll_ok = ext["log_loss"] <= LL_BAR
    yld_ok = b1["yield"] > YLD_BAR and b1["n_bets"] >= MIN_N
    verdict = "KEEP" if (ll_ok and yld_ok) else "REVERT"

    print("=" * 72)
    print(f"PHASE 8 {hyp.upper()} — dual gate, thr .05")
    print("=" * 72)
    print(f"{'metrik':12} {'baseline(9)':>12} {'+fitur':>12}")
    for kk in ("log_loss", "brier", "macro_f1", "accuracy"):
        print(f"{kk:12} {base_eval[kk]:>12.4f} {ext[kk]:>12.4f}")
    print()
    print(f"bet thr .05  baseline : yield {b0['yield']:+.4%} (n={b0['n_bets']})")
    print(f"bet thr .05  +fitur  : yield {b1['yield']:+.4%} (n={b1['n_bets']})")
    print(f"LL gate <= {LL_BAR} : {ext['log_loss']:.6f} -> {'OK' if ll_ok else 'FAIL'}")
    print(f"Yield gate > {YLD_BAR:.4%} & n>={MIN_N} : {b1['yield']:+.4%} "
          f"(n={b1['n_bets']}) -> {'OK' if yld_ok else 'FAIL'}")
    print(f"VERDICT: {verdict}")
    return {"hyp": hyp, "ll": ext["log_loss"], "brier": ext["brier"],
            "yield": b1["yield"], "n": b1["n_bets"], "verdict": verdict}


if __name__ == "__main__":
    h = sys.argv[1] if len(sys.argv) > 1 else "e81"
    run(h)
