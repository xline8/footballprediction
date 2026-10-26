#!/usr/bin/env python3
"""experiment_deriv.py — Phase 13: derivative market backtest (O/U 2.5).

Dari matriks DC terkalibrasi-meta (matrix_pricer) kita dapatkan prob over 2.5
per match, lalu dibandingkan dgn odds B365 (de-vigged shin 2-way). Edge =
p_model - p_fair. Bet pada Over bila edge>thr, Under bila (1-p)>thr. Flat 1u.
Validasi: yield + bootstrap p (H0 ROI<=0).

BTTS: odds historis tidak tersedia di dataset -> dicatat sbg blocker, tidak
di-backtest (lihat TODO_AI.md). Logika pricing BTTS tetap ada di matrix_pricer.
"""

from __future__ import annotations

import csv
import os
from collections import defaultdict

import numpy as np

from backtest_picks import load_records, RECORDS, _fair_probs
from data_enrichment.utils import norm_team, to_float
from matrix_pricer import price

BASE = os.path.dirname(os.path.abspath(__file__))
CLEAN = os.path.join(BASE, "all_matches_clean.csv")
ENRICHED = os.path.join(BASE, "all_matches_enriched.csv")
N_BOOT = 10_000


def _idx_map():
    """(div,date,normhome,normaway) -> dict odds O/U (B365 & PS) + goals."""
    idx = {}
    with open(ENRICHED, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            d = str(r.get("Date") or "")[:10]
            div = r.get("Div")
            h = norm_team(r.get("HomeTeam"))
            a = norm_team(r.get("AwayTeam"))
            if not (d and div and h and a):
                continue
            idx[(div, d, h, a)] = {
                "b365": (to_float(r.get("B365>2.5")), to_float(r.get("B365<2.5"))),
                "pn": (to_float(r.get("P>2.5")), to_float(r.get("P<2.5"))),
            }
    with open(CLEAN, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            d = str(r.get("Date") or "")[:10]
            div = r.get("Div")
            h = norm_team(r.get("HomeTeam"))
            a = norm_team(r.get("AwayTeam"))
            k = (div, d, h, a)
            if k in idx:
                idx[k]["goals"] = (to_float(r.get("FTHG")), to_float(r.get("FTAG")))
    return idx


def build_bets(records, idx, thr=0.05, use="b365"):
    bets = []
    no_odds = no_goals = 0
    for r in records:
        meta = (r.get("ph_meta"), r.get("pd_meta"), r.get("pa_meta"))
        lh, la, rho = r.get("lam_h"), r.get("lam_a"), r.get("rho")
        if not (meta[0] is not None and lh is not None):
            continue
        v = idx.get((r["div"], r["date"], norm_team(r["home"]),
                     norm_team(r["away"])))
        if not v:
            continue
        odds = v.get(use)
        if not (odds and odds[0] and odds[1]):
            no_odds += 1
            continue
        g = v.get("goals")
        if not (g and g[0] is not None and g[1] is not None):
            no_goals += 1
            continue
        p = price(lh, la, rho, meta)
        if p is None:
            continue
        over = p[0]
        fair = _fair_probs(odds, "shin")
        f_over, f_under = fair
        # dua sisi: Over & Under
        eo = over - f_over
        eu = (1.0 - over) - f_under
        tot = g[0] + g[1]
        ov = 1 if tot > 2.5 else 0
        if eo > thr:
            bets.append({"mkt": "over", "od": odds[0], "edge": eo,
                         "year": r["date"][:4], "win": ov == 1,
                         "profit": (odds[0] - 1.0) if ov == 1 else -1.0})
        elif eu > thr:
            bets.append({"mkt": "under", "od": odds[1], "edge": eu,
                         "year": r["date"][:4], "win": ov == 0,
                         "profit": (odds[1] - 1.0) if ov == 0 else -1.0})
    print(f"no odds {no_odds} / no goals {no_goals}")
    return bets


def evaluate(bets):
    if not bets:
        print("no bets")
        return None
    profit = sum(b["profit"] for b in bets)
    yield_ = profit / len(bets)
    hit = sum(1 for b in bets if b["win"]) / len(bets)
    mkt = defaultdict(int)
    for b in bets:
        mkt[b["mkt"]] += 1
    with open(os.path.join(BASE, "deriv_bets.csv"), "w", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["market", "odds", "edge", "year", "win", "profit"])
        for b in bets:
            w.writerow([b["mkt"], b["od"], round(b["edge"], 4), b["year"],
                        int(b["win"]), b["profit"]])
    obs = np.mean([b["profit"] for b in bets])
    m = len(bets)
    rng = np.random.default_rng(0)
    profits = np.array([b["profit"] for b in bets])
    le0 = sum(1 for _ in range(N_BOOT)
              if profits[rng.integers(0, m, size=m)].mean() <= 0.0)
    p = le0 / N_BOOT
    print(f"N={m} yield={obs:+.4%} hit={hit:.1%} "
          f"p_bootstrap={p:.4f} over/under={mkt['over']}/{mkt['under']}")
    return {"n": m, "yield": obs, "p": p, "hit": hit}


def main():
    records = load_records(RECORDS)
    idx = _idx_map()
    for thr in (0.02, 0.05, 0.08):
        print(f"\n--- thr={thr:.2f} (B365, shin) ---")
        bets = build_bets(records, idx, thr=thr, use="b365")
        evaluate(bets)


if __name__ == "__main__":
    main()
