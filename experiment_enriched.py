#!/usr/bin/env python3
"""experiment_enriched.py — Phase 12: Sharp vs Soft book integration.

Sumber: `all_matches_enriched.csv` (Pinnacle PS, midweek_flags, rolling_xg_diff)
di-join ke records_cache. Imputasi: PS hilang -> fallback ke B365 (dev=1.0);
rolling_xg_diff hilang -> Fallback rolling_goal_diff / 0.

Pathway A (ML injection): meta 9-logit + fitur dev & ps_fair & midweek
   -> walk-forward LL/Brier; gate LL < 1.00170.
Pathway B (Policy overlay, meta dikunci): filter dev_side > threshold (dan/atau
   midweek) pada bet ber-edge; evaluasi yield/N + bootstrap p-value (H0 ROI<=0).
"""

from __future__ import annotations

import os
from collections import defaultdict

import numpy as np

from backtest_picks import _fair_probs, load_records, RECORDS
from data_enrichment.utils import norm_team, to_float
from experiment_feats import _walkforward

BASE = os.path.dirname(os.path.abspath(__file__))
ENRICHED = os.path.join(BASE, "all_matches_enriched.csv")
LL_BAR = 1.00170
N_BOOT = 10_000


def _logit_clip(p):
    return np.log(np.clip(p, 1e-6, 1 - 1e-6) / (1 - np.clip(p, 1e-6, 1 - 1e-6)))


def _enriched_index():
    import csv
    idx = {}
    with open(ENRICHED, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            d = str(r.get("Date") or "")[:10]
            div = r.get("Div")
            h = norm_team(r.get("HomeTeam"))
            a = norm_team(r.get("AwayTeam"))
            if not (d and div and h and a):
                continue
            ps = (to_float(r.get("ps_home")), to_float(r.get("ps_draw")),
                  to_float(r.get("ps_away")))
            idx[(div, d, h, a)] = {
                "ps": ps,
                "mw_h": int(r.get("midweek_home_flag") or 0),
                "mw_a": int(r.get("midweek_away_flag") or 0),
                "rollxg": to_float(r.get("rolling_xg_diff")),
            }
    return idx


def load_enriched_records():
    records = load_records(RECORDS)
    idx = _enriched_index()
    missing_ps = 0
    for r in records:
        v = idx.get((r["div"], r["date"], norm_team(r["home"]),
                     norm_team(r["away"])))
        if v:
            ps = v["ps"]
            # imputasi: PS hilang -> fallback ke B365 (dev=1.0)
            o = r.get("o")
            if o and any(p is None for p in ps):
                missing_ps += 1
                ps = tuple(p if p is not None else o[i] for i, p in enumerate(ps))
            r["ps"] = ps
            r["mw_h"] = v["mw_h"]
            r["mw_a"] = v["mw_a"]
            r["rollxg"] = v["rollxg"]
        else:
            missing_ps += 1
            r["ps"] = r.get("o")
            r["mw_h"] = r["mw_a"] = 0
            r["rollxg"] = None
    print(f"join enriched: {len(records)-missing_ps}/{len(records)} imputasi ps tengat",
          missing_ps)
    return records


def build_Xy_a(records):
    """17 fitur: 9 logit asal + dev_H/D/A, ps_fair, midweek_h/a."""
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


def pathway_a(records):
    X, y, dates = build_Xy_a(records)
    ext, pm = _walkforward(records, X, y, dates, list(range(9, 17)))
    # baseline (9 fitur)
    Xb, yb, datesb = build_Xy_a(records)
    Xb, yb, datesb = Xb[:, :9], yb, datesb
    base, _ = _walkforward(records, Xb, yb, datesb, [])
    print("=" * 70)
    print("PATHWAY A — META + SHARP/SOFT FEATURES")
    print("=" * 70)
    print(f"{'metrik':12} {'baseline(9)':>12} {'+sharp':>12}")
    for k in ("log_loss", "brier", "macro_f1", "accuracy"):
        print(f"{k:12} {base[k]:>12.4f} {ext[k]:>12.4f}")
    ok = ext["log_loss"] < LL_BAR
    print(f"LL gate < {LL_BAR}: {ext['log_loss']:.6f} -> {'OK' if ok else 'FAIL'}")
    return {"ll": ext["log_loss"], "brier": ext["brier"], "ok": ok}


def candidate_bets(records):
    """semua sisi dgn edge>0.05 (shin fair), + info dev/mw per sisi."""
    bets = []
    for idx, r in enumerate(records):
        o = r.get("o")
        if not o:
            continue
        fair = _fair_probs(o, "shin")
        pm = (r["ph_meta"], r["pd_meta"], r["pa_meta"])
        ps = r.get("ps")
        for im in (0, 1, 2):
            edge = pm[im] - fair[im]
            if edge <= 0.05:
                continue
            dev = (o[im] / ps[im]) if (ps and ps[im]) else 1.0
            mw = r.get("mw_h") if im == 0 else (r.get("mw_a") if im == 2 else 0)
            win = im == r["yi"]
            years = r["date"][:4]
            bets.append({"im": im, "od": o[im], "edge": edge, "dev": dev,
                         "mw": mw, "year": years, "win": win,
                         "profit": (o[im] - 1.0) if win else -1.0})
    return bets


def sweep_b(bets):
    print("\nPATHWAY B — POLICY OVERLAY (meta dikunci)")
    print(f"{'dev>':>5} {'mw':>3} {'N':>6} {'yield':>9} {'pos(21-25)':>10}")
    best = None
    for dev in (1.0, 1.02, 1.05, 1.08):
        for mw in (0, 1):
            sel = [b for b in bets if b["dev"] > dev and (b["mw"] >= mw)]
            n = len(sel)
            if n == 0:
                continue
            profit = sum(b["profit"] for b in sel)
            yld = profit / n
            yrs = defaultdict(int)
            for b in sel:
                if b["year"] in ("2021", "2022", "2023", "2024", "2025"):
                    yrs[b["year"]] += 1 if b["profit"] > 0 else 0
            pos = sum(1 for y in ("2021", "2022", "2023", "2024", "2025")
                      if (sum(1 for b in sel if b["year"] == y and b["profit"] > 0)) > 0)
            print(f"{dev:>5.2f} {mw:>3} {n:>6} {yld:>+9.4%} {pos:>9}/5")
            if n >= 800 and best is None:
                best = (dev, mw, sel)
    return best


def bootstrap_b(sel):
    rng = np.random.default_rng(0)
    m = len(sel)
    profits = np.array([b["profit"] for b in sel])
    obs = profits.mean()
    le0 = 0
    for _ in range(N_BOOT):
        rs = profits[rng.integers(0, m, size=m)]
        if rs.mean() <= 0.0:
            le0 += 1
    p = le0 / N_BOOT
    lo, hi = np.percentile(profits[rng.integers(0, m, size=(N_BOOT, m))].mean(axis=1),
                           [2.5, 97.5])
    print(f"\nbootstrap N={m} yield={obs:+.4%} p={p:.4f} CI95=[{lo:+.4%},{hi:+.4%}]")
    return {"n": m, "yield": obs, "p": p}


def main():
    records = load_enriched_records()
    print("--- Pathway A ---")
    a = pathway_a(records)
    print("\n--- Pathway B ---")
    bets = candidate_bets(records)
    best = sweep_b(bets)
    if best:
        dev, mw, sel = best
        b = bootstrap_b(sel)
        print("B verdict:", "SIGNIFIKAN" if b["p"] < 0.05 else "TIDAK")
    else:
        print("tidak ada konfigurasi dengan N>=800")
    return a


if __name__ == "__main__":
    main()
