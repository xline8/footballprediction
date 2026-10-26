#!/usr/bin/env python3
"""policy_overlay.py — Phase 9: Decoupled Betting Policy engine.

Probability Engine (locked): meta model probs (LL 1.0017), edge = shin fair.
Market Value Engine: edge = p - fair_shin > thr (0.05 default).
Contextual Policy Overlay: filter / stake modifier SETELAH prob dihitung.

Policies:
  9.1 Desperation filter : edge>thr AND despo(backed) > theta_D
  9.2 Rest-fatigue filter : edge>thr AND rest_adv(backed) >= 3 hari
  9.3 Composite score      : edge>thr AND (w1*despo + w2*fatigue_norm) >= theta
  9.4 Dynamic Kelly        : stake = base_kelly * composite_score

Evaluation: yield > -1.50% AND N >= 1000 AND yield > 0 di >=3 dari 2021-2025.
"""

import os
from collections import defaultdict

from backtest_picks import load_records, _fair_probs, RECORDS
from experiment_motiv import build_maps, _sorted_matches

BASE = os.path.dirname(os.path.abspath(__file__))
THR = 0.05
YLD_BAR = -0.0150
MIN_N = 1000
YEARS = ("2021", "2022", "2023", "2024", "2025")
BASELINE_KELLY = 0.25


def desperation(s, side):
    """Skor desperation [0,1] dari klasemen (leak-free, final 10 matchday)."""
    if not s or not s.get(f"late_{side}"):
        return 0.0
    rel = s[f"dist_releg_{side}"]
    eur = s[f"dist_euro_{side}"]
    if rel < 0.0:
        return min(1.0, 0.6 + (-rel) / 6.0)
    if eur < 0.0:
        return 0.8
    if eur <= 3.0:
        return 0.6
    if rel <= 3.0:
        return 0.5
    return 0.0


def desperation_exp(s, side):
    """Desperation ekspansi (Phase 10): + urgensi title/Eropa & points-gap."""
    if not s or not s.get(f"late_{side}"):
        return 0.0
    rel = s[f"dist_releg_{side}"]
    eur = s[f"dist_euro_{side}"]
    tit = s[f"dist_title_{side}"]
    if rel < 0.0:
        return min(1.0, 0.6 + (-rel) / 6.0)
    if rel <= 2.0:
        return 0.45
    if eur < 0.0:
        return 0.85
    if eur <= 2.0:
        return 0.75
    if eur <= 5.0:
        return 0.55
    if tit <= 2.0:
        return 0.70
    if tit <= 5.0:
        return 0.50
    return 0.0


def candidates(records, fmap, smap, thr=THR, cpmap=None, rmap=None):
    """Generator bet kandidat (sebelum overlay) dgn skor konteks per sisi."""
    for idx, r in enumerate(records):
        o = r.get("o")
        if not o:
            continue
        fair = _fair_probs(o, "shin")
        pm = (r["ph_meta"], r["pd_meta"], r["pa_meta"])
        key = (r["div"], r["date"], r["home"], r["away"])
        s = smap.get(key)
        f = fmap.get(key, {})
        dp_h, dp_a = desperation(s, "h"), desperation(s, "a")
        dx_h, dx_a = desperation_exp(s, "h"), desperation_exp(s, "a")
        fat_h = float(f.get("rest_diff", 0.0))   # rest_h - rest_a
        fat_a = -fat_h
        cont_h = float(cpmap.get(key, 0.0)) if cpmap else 0.0
        riv_h = float(rmap.get(key, 0.0)) if rmap else 0.0
        year = r["date"][:4]
        for im in (0, 1, 2):
            edge = pm[im] - fair[im]
            if edge <= thr:
                continue
            if im == 0:
                dp, dx, fat = dp_h, dx_h, fat_h
                cont, riv = cont_h, riv_h
            elif im == 2:
                dp, dx, fat = dp_a, dx_a, fat_a
                cont, riv = cont_h, riv_h
            else:
                dp, dx, fat = (dp_h + dp_a) / 2.0, (dx_h + dx_a) / 2.0, 0.0
                cont, riv = cont_h, riv_h
            od = o[im]
            win = im == r["yi"]
            yield {"idx": idx, "im": im, "od": od, "edge": edge,
                   "despo": dp, "despo_exp": dx, "fatigue": fat,
                   "cont": cont, "riv": riv, "year": year, "win": win,
                   "profit_flat": (od - 1.0) if win else -1.0}


def composite_score(c, w1=0.6, w2=0.4):
    """w1*despo + w2*fatigue_norm; keluaran [0,1]."""
    f_norm = max(0.0, min(1.0, c["fatigue"] / 7.0))
    return w1 * c["despo"] + w2 * f_norm


def evaluate(bets):
    """yield, n, dan yield per tahun."""
    n = 0
    staked = profit = 0.0
    yearly = defaultdict(lambda: [0, 0.0, 0.0])  # year -> [n, staked, profit]
    for b in bets:
        n += 1
        staked += 1.0
        profit += b["profit_flat"]
        y = yearly[b["year"]]
        y[0] += 1; y[1] += 1.0; y[2] += b["profit_flat"]
    yield_ = profit / staked if staked else 0.0
    yrs = {yr: (y[2] / y[1] if y[1] else 0.0) for yr, y in yearly.items()}
    stable = sum(1 for yr in YEARS if yrs.get(yr, 0.0) > 0.0)
    return {"n": n, "yield": yield_, "yearly": yrs, "stable_years": stable}


def sweep_p91(bets):
    print("\n--- Policy 9.1: Desperation Filter (theta_D sweep) ---")
    for th in (0.0, 0.3, 0.4, 0.5, 0.6, 0.8):
        e = evaluate([b for b in bets if b["despo"] > th])
        _show("9.1", th, e)


def sweep_p92(bets):
    print("\n--- Policy 9.2: Asymmetric Rest-Fatigue (gap>=3) ---")
    for gap in (0.0, 1.0, 3.0, 5.0):
        e = evaluate([b for b in bets if b["fatigue"] >= gap])
        _show("9.2", gap, e)


def sweep_p93(bets, w1=0.6, w2=0.4):
    print(f"\n--- Policy 9.3: Composite score (w1={w1},w2={w2}) ---")
    for th in (0.0, 0.15, 0.3, 0.45, 0.6, 0.75):
        e = evaluate([b for b in bets if composite_score(b, w1, w2) >= th])
        _show("9.3", th, e)


def sweep_p94(bets, w1=0.6, w2=0.4):
    print(f"\n--- Policy 9.4: Dynamic Kelly stake = base*composite ---")
    for th in (0.0, 0.15, 0.3, 0.45, 0.6):
        out = []
        for b in bets:
            sc = composite_score(b, w1, w2)
            stake = BASELINE_KELLY * sc
            if stake <= 0.0 or sc < th:
                continue
            od = b["od"]
            profit = (stake * (od - 1.0)) if b["win"] else -stake
            out.append((stake, profit, b["year"]))
        staked = sum(s for s, _, _ in out)
        profit = sum(p for _, p, _ in out)
        yield_ = profit / staked if staked else 0.0
        yr = defaultdict(lambda: [0.0, 0.0])
        for s, p, y in out:
            yr[y][0] += s
            yr[y][1] += p
        yrs = {y: (p / s if s else 0.0) for y, (s, p) in yr.items()}
        stable = sum(1 for y in YEARS if yrs.get(y, 0.0) > 0.0)
        e = {"n": len(out), "yield": yield_, "yearly": yrs, "stable_years": stable}
        _show("9.4", th, e)


def _show(tag, param, e):
    flag = ""
    ok = e["n"] >= MIN_N and e["yield"] > YLD_BAR and e["stable_years"] >= 3
    if ok:
        flag = "  <<< PASS"
    yrs = " ".join(f"{y}:{e['yearly'].get(y,0):+.2%}" for y in YEARS)
    print(f"{tag} param={param:<5} n={e['n']:>6} yield={e['yield']:+.4%} "
          f"stable(yly>{0})={e['stable_years']}/5 {flag}")
    print(f"    yearly: {yrs}")


def main():
    records = load_records(RECORDS)
    fmap, smap = build_maps()
    bets = list(candidates(records, fmap, smap))
    print(f"kandidat bet (edge>0.05, tanpa overlay): n={len(bets)}")
    sweep_p91(bets)
    sweep_p92(bets)
    sweep_p93(bets)
    sweep_p94(bets)


if __name__ == "__main__":
    main()
