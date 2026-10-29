#!/usr/bin/env python3
"""slip_recommender.py — rekomendasi slip odds deterministik (±2.0).

Membaca market_compare.csv (join odds tipsterarea + prob implied) dan
menggabungkan dengan prob model (predictions_upcoming.csv /
predictions_cups_upcoming.csv) untuk skor kualitas kaki.

Aturan:
  - Pasar: 1X2 / DC / OU / BTS (tanpa corner).
  - Satu kaki per laga. Slip 2-4 kaki.
  - Kualitas kaki: p_model >= 0.50 DAN o_1xbet >= 1.20.
  - Total odds = produk o_1xbet; target di band 1.85-2.15 (target 2.0).
  - Pilih slip joint probability tertinggi (produk p_model); tie-break
    total EV (jumlah p_model*o - 1).
  - Jika tidak ada kombinasi dalam band: output kombinasi terdekat ke 2.0,
    diberi label in_band=false.

Output: recommended_slip.csv (baris per kaki + kolom agregat slip),
diarsipkan harian oleh market_orchestration.archive_snapshots.

Run: python slip_recommender.py
"""
import csv
import math
import os
import sys
from collections import defaultdict
from itertools import combinations

HERE = os.path.dirname(os.path.abspath(__file__))
MARKET_COMPARE = os.path.join(HERE, "market_compare.csv")
PRED_LEAGUE = os.path.join(HERE, "predictions_upcoming.csv")
PRED_CUP = os.path.join(HERE, "predictions_cups_upcoming.csv")
OUT = os.path.join(HERE, "recommended_slip.csv")

ODDS_LO, ODDS_HI = 1.85, 2.15
TARGET = 2.0
MIN_PMODEL = 0.50
MIN_ODDS = 1.20
MIN_LEGS, MAX_LEGS = 2, 4

MARKETS = ("1X2", "DC", "OU", "BTS")

SLIP_COLS = ["date", "home", "away", "competition", "market", "line",
             "selection", "o_1xbet", "p_model", "slip_total_odds",
             "slip_joint_prob", "slip_ev", "in_band"]


def _read(path):
    if not os.path.exists(path):
        return []
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _f(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def _load_preds():
    """(date, home_norm, away_norm) -> pred row (liga/cup)."""
    d = {}
    for fn in (PRED_LEAGUE, PRED_CUP):
        for r in _read(fn):
            key = ((r.get("date") or ""), (r.get("home") or "").lower(),
                   (r.get("away") or "").lower())
            d.setdefault(key, []).append(r)
    return d


def _pm_for(market, line, sel, pr):
    """p_model dari baris prediksi untuk (market, line, selection)."""
    if market == "1X2":
        col = {"1": "ph_dc", "X": "pd_dc", "2": "pa_dc"}.get(sel)
        return _f(pr.get(col)) if col else None
    if market == "DC":
        col = {"1X": "p_dc_1x", "12": "p_dc_12", "X2": "p_dc_x2"}.get(sel)
        return _f(pr.get(col)) if col else None
    if market == "OU":
        col = {"1.5": "p_over15_dc", "2.5": "p_over_dc",
               "3.5": "p_over35_dc"}.get(str(line))
        ov = _f(pr.get(col)) if col else None
        if ov is None:
            return None
        return ov if sel == "Over" else 1.0 - ov
    if market == "BTS":
        b = _f(pr.get("p_btts"))
        if b is None:
            return None
        return b if sel == "Yes" else 1.0 - b
    return None


def _candidates():
    preds = _load_preds()
    out = []
    for r in _read(MARKET_COMPARE):
        market = r.get("market")
        if market not in MARKETS:
            continue
        o = _f(r.get("o_1xbet"))
        if not o or o < MIN_ODDS:
            continue
        key = ((r.get("date") or ""), (r.get("home") or "").lower(),
               (r.get("away") or "").lower())
        prows = preds.get(key)
        if not prows:
            continue
        pm = _pm_for(market, r.get("line"), r.get("selection"), prows[0])
        if pm is None or pm < MIN_PMODEL:
            continue
        out.append({
            "match": r.get("game_id") or key,
            "date": r.get("date") or "", "home": r.get("home") or "",
            "away": r.get("away") or "", "comp": r.get("competition") or "",
            "market": market, "line": r.get("line") or "",
            "sel": r.get("selection") or "", "o": o, "pm": pm,
        })
    return out


def _slip_stats(legs):
    tot = math.prod(l["o"] for l in legs)
    jp = math.prod(l["pm"] for l in legs)
    ev = sum(l["pm"] * l["o"] for l in legs) - len(legs)
    return tot, jp, ev


def _better(a, b):
    """a,b = (tot, jp, ev, in_band, legs). Preferensi: in_band dulu,
    lalu joint prob, lalu total EV; kalau tak ada in_band, dekat ke target."""
    a_in, b_in = a[3], b[3]
    if a_in != b_in:
        return a_in
    jp_a, jp_b = a[1], b[1]
    if abs(jp_a - jp_b) > 1e-9:
        return jp_a > jp_b
    ev_a, ev_b = a[2], b[2]
    if abs(ev_a - ev_b) > 1e-9:
        return ev_a > ev_b
    if not a_in:  # keduanya out-of-band: dekat ke target menang
        return abs(a[0] - TARGET) < abs(b[0] - TARGET)
    return False


def recommend():
    cands = _candidates()
    by_match = defaultdict(list)
    for c in cands:
        by_match[c["match"]].append(c)
    keys = list(by_match)
    best = None  # (tot, jp, ev, in_band, legs)

    def consider(legs):
        nonlocal best
        tot, jp, ev = _slip_stats(legs)
        inb = ODDS_LO <= tot <= ODDS_HI
        # salin list: `legs` akan di-pop oleh rekursi setelah return
        cur = (tot, jp, ev, inb, list(legs))
        if best is None or _better(cur, best):
            best = cur

    for size in range(MIN_LEGS, MAX_LEGS + 1):
        for idxs in combinations(range(len(keys)), size):
            # delegasikan pemilihan kaki per laga: ambil semua kombinasi kaki
            pools = [by_match[keys[i]] for i in idxs]
            if any(not p for p in pools):
                continue
            # rekursif ringan: produk kartesian per kombinasi laga
            def rec(i, chosen):
                if i == len(pools):
                    consider(chosen)
                    return
                for leg in pools[i]:
                    chosen.append(leg)
                    rec(i + 1, chosen)
                    chosen.pop()
            rec(0, [])

    rows = []
    if best is not None:
        tot, jp, ev, inb, legs = best
        for l in legs:
            rows.append({"date": l["date"], "home": l["home"],
                         "away": l["away"], "competition": l["comp"],
                         "market": l["market"], "line": l["line"],
                         "selection": l["sel"], "o_1xbet": round(l["o"], 3),
                         "p_model": round(l["pm"], 4),
                         "slip_total_odds": round(tot, 3),
                         "slip_joint_prob": round(jp, 4),
                         "slip_ev": round(ev, 4),
                         "in_band": "true" if inb else "false"})

    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=SLIP_COLS)
        w.writeheader()
        w.writerows(rows)

    summary = {"n_legs": len(rows), "total_odds": round(best[0], 3) if best else None,
               "joint_prob": round(best[1], 4) if best else None,
               "in_band": bool(best[3]) if best else False}
    print(f"slip: {summary['n_legs']} kaki | total={summary['total_odds']} "
          f"joint={summary['joint_prob']} in_band={summary['in_band']} -> {OUT}")
    return summary


if __name__ == "__main__":
    sys.exit(0 if recommend().get("n_legs") else 1)
