#!/usr/bin/env python
"""History-only diagnostic: why did early 2026/27 run so hot on total
shots? Reads ONLY past results data (spine HS/AS + FotMob features).
No candidate model is tuned or run; this script computes descriptive
statistics for DIAGNOSTIC_PHASE.md.

Scope note: the spine's top-5 coverage starts 2017/18 (all_matches_clean
holds no 2015/16 or 2016/17 rows at all), so history = 2017/18-2025/26
and the case under study = 2026/27.

Run: .venv/bin/python experiments/shots_model_v2/run_phase_diagnostic.py
"""

import csv
import math
import os
from collections import defaultdict
from datetime import date

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..", "..")
SPINE = os.path.join(ROOT, "all_matches_clean.csv")
FEATURES = os.path.join(ROOT, "data_enrichment", "shot_lineup_features.csv")
TOP5 = ["E0", "D1", "I1", "SP1", "F1"]
CASE = "2026/27"
LINE = 25.5


def load_spine():
    rows = []
    dropped = 0
    with open(SPINE, newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            if r["Div"] not in TOP5:
                continue
            if r["HS"] in (None, "") or r["AS"] in (None, ""):
                dropped += 1
                continue
            d = date.fromisoformat(r["Date"])
            rows.append({
                "div": r["Div"], "season": r["Season"], "date": d,
                "home": r["HomeTeam"], "away": r["AwayTeam"],
                "total": int(float(r["HS"])) + int(float(r["AS"])),
            })
    rows.sort(key=lambda m: (m["date"], m["div"], m["home"]))
    return rows, dropped


def pct(x):
    return f"{100.0 * x:.1f}%"


def over_rate(totals):
    return float(np.mean([1.0 if t > LINE else 0.0 for t in totals]))


def qstats(vals):
    a = np.asarray(vals, dtype=float)
    return (float(np.min(a)), float(np.percentile(a, 25)), float(np.median(a)),
            float(np.percentile(a, 75)), float(np.max(a)))


def main():
    rows, dropped = load_spine()
    seasons = sorted(set(r["season"] for r in rows))
    hist_seasons = [s for s in seasons if s != CASE]
    print(f"spine top-5 rows used: {len(rows)} (dropped missing HS/AS: {dropped})")
    print(f"seasons: {seasons}")

    # division-season structures
    ds_matches = defaultdict(list)          # (div, season) -> rows
    for r in rows:
        ds_matches[(r["div"], r["season"])].append(r)
    ds_start, ds_mean = {}, {}
    for k, ms in ds_matches.items():
        ds_start[k] = min(m["date"] for m in ms)
        ds_mean[k] = float(np.mean([m["total"] for m in ms]))
    for r in rows:
        k = (r["div"], r["season"])
        r["days"] = (r["date"] - ds_start[k]).days
        r["ratio"] = r["total"] / ds_mean[k]

    def season_rows(s):
        return [r for r in rows if r["season"] == s]

    # ---------------------------------------------------------------- Q1
    print("\n================ Q1: SEASON PHASE ================")
    blocks = [(0, 30), (31, 60), (61, 90), (91, 120), (121, 150),
              (151, 180), (181, 210), (211, 240), (241, 270), (271, 10**9)]
    hist = [r for r in rows if r["season"] != CASE]
    print("Pooled (2017/18-2025/26, ratios within division-season):")
    print(f"{'days':>10} {'n':>6} {'pooled ratio':>12} {'season med':>10} "
          f"{'IQR':>15} {'range':>15} {'seasons>1.0':>11}")
    phase_curve = {}
    for lo, hi in blocks:
        pooled = [r["ratio"] for r in hist if lo <= r["days"] <= hi]
        per_season = []
        for s in hist_seasons:
            v = [r["ratio"] for r in hist
                 if r["season"] == s and lo <= r["days"] <= hi]
            if len(v) >= 20:
                per_season.append(float(np.mean(v)))
        mn, q1, med, q3, mx = qstats(per_season)
        phase_curve[(lo, hi)] = float(np.mean(pooled))
        lab = f"{lo}-{hi if hi < 10**9 else '+'}"
        print(f"{lab:>10} {len(pooled):>6} {np.mean(pooled):>12.4f} "
              f"{med:>10.4f} [{q1:.3f},{q3:.3f}] [{mn:.3f},{mx:.3f}] "
              f"{sum(1 for v in per_season if v > 1.0)}/{len(per_season)}")

    print("\nCalendar month (ratios, months Aug-May only):")
    print(f"{'month':>5} {'n':>6} {'pooled ratio':>12} {'season med':>10} "
          f"{'IQR':>15} {'range':>15}")
    for mo in [8, 9, 10, 11, 12, 1, 2, 3, 4, 5]:
        pooled = [r["ratio"] for r in hist if r["date"].month == mo]
        per_season = []
        for s in hist_seasons:
            v = [r["ratio"] for r in hist
                 if r["season"] == s and r["date"].month == mo]
            if len(v) >= 20:
                per_season.append(float(np.mean(v)))
        mn, q1, med, q3, mx = qstats(per_season)
        print(f"{mo:>5} {len(pooled):>6} {np.mean(pooled):>12.4f} "
              f"{med:>10.4f} [{q1:.3f},{q3:.3f}] [{mn:.3f},{mx:.3f}]")

    print("\nFirst-60-days factor per season (div-season ratios averaged):")
    f60 = {}
    for s in seasons:
        v = [r["ratio"] for r in rows if r["season"] == s and r["days"] <= 60]
        f60[s] = float(np.mean(v))
        print(f"  {s}: {f60[s]:.4f}  (n={len(v)})")
    hist_f60 = [f60[s] for s in hist_seasons]
    print(f"  history: median {np.median(hist_f60):.4f}, "
          f"IQR [{np.percentile(hist_f60,25):.4f},{np.percentile(hist_f60,75):.4f}], "
          f"range [{min(hist_f60):.4f},{max(hist_f60):.4f}], "
          f"seasons > 1.0: {sum(1 for v in hist_f60 if v > 1.0)}/{len(hist_f60)}")

    # ---------------------------------------------------------------- Q2
    print("\n================ Q2: HOW UNUSUAL IS 2026/27's START? ================")

    def early_cal(s):
        y0 = int(s[:4])
        cut = date(y0, 11, 2)
        return [r for r in season_rows(s) if r["date"] <= cut]

    def early_cnt(s):
        out = []
        for d in TOP5:
            ms = [r for r in season_rows(s) if r["div"] == d]
            ms.sort(key=lambda m: (m["date"], m["home"]))
            out.extend(ms[:100])
        return out

    def window_table(fn, label):
        print(f"\n-- {label} --")
        print(f"{'season':>8} {'nE':>5} {'early mean':>10} {'early O%':>9} "
              f"{'full mean':>9} {'full O%':>8} {'elev(shots)':>11} {'elev(pp)':>9}")
        out = {}
        for s in seasons:
            e = fn(s)
            full = season_rows(s)
            em = float(np.mean([r["total"] for r in e]))
            eo = over_rate([r["total"] for r in e])
            fm = float(np.mean([r["total"] for r in full]))
            fo = over_rate([r["total"] for r in full])
            out[s] = dict(n=len(e), em=em, eo=eo, fm=fm, fo=fo,
                          elev=em - fm, elev_pp=100 * (eo - fo))
            note = "  <- partial season (early window = everything so far)" \
                if s == CASE else ""
            print(f"{s:>8} {len(e):>5} {em:>10.2f} {pct(eo):>9} {fm:>9.2f} "
                  f"{pct(fo):>8} {em-fm:>+11.2f} {100*(eo-fo):>+9.1f}{note}")
        hs = [out[s]["elev"] for s in hist_seasons]
        rank = 1 + sum(1 for v in hs if v > out[CASE]["elev"])
        hpp = [out[s]["elev_pp"] for s in hist_seasons]
        rank_pp = 1 + sum(1 for v in hpp if v > out[CASE]["elev_pp"])
        print(f"2026/27 elevation rank (shots): {rank} of {len(seasons)}; "
              f"history range [{min(hs):+.2f},{max(hs):+.2f}], "
              f"median {np.median(hs):+.2f}")
        print(f"2026/27 elevation rank (Over pp): {rank_pp} of {len(seasons)}; "
              f"history range [{min(hpp):+.1f},{max(hpp):+.1f}], "
              f"median {np.median(hpp):+.1f}")
        return out

    t_cal = window_table(early_cal, "E1: calendar window, date <= Nov 2")
    t_cnt = window_table(early_cnt, "E2: first 100 matches per division (~11 rounds)")

    print("\n2026/27 early window per division (E1):")
    for d in TOP5:
        e = [r for r in early_cal(CASE) if r["div"] == d]
        full = [r for r in season_rows(CASE) if r["div"] == d]
        print(f"  {d}: n={len(e)} early mean "
              f"{np.mean([r['total'] for r in e]):.2f}, Over {pct(over_rate([r['total'] for r in e]))}")

    # ---------------------------------------------------------------- Q3
    print("\n================ Q3: PERSISTENCE ================")
    hist_norm = float(np.mean([t_cal[s]["fm"] for s in hist_seasons]))
    phi_early = float(np.median([t_cal[s]["em"] / t_cal[s]["fm"]
                                 for s in hist_seasons]))
    print(f"historical norm (mean of full-season means 2017/18-2025/26): "
          f"{hist_norm:.2f}")
    print(f"typical early-window phase factor phi (median early/full ratio): "
          f"{phi_early:.4f}")

    xs, ys, xadj, labs = [], [], [], []
    print(f"{'season':>8} {'early_dev':>9} {'rest_dev':>9} {'early_dev_phaseadj':>18}")
    for s in hist_seasons:
        e = early_cal(s)
        y0 = int(s[:4])
        rest = [r for r in season_rows(s) if r["date"] > date(y0, 11, 2)]
        em = float(np.mean([r["total"] for r in e]))
        rm = float(np.mean([r["total"] for r in rest]))
        ed, rd = em - hist_norm, rm - hist_norm
        eda = em - hist_norm * phi_early
        xs.append(ed); ys.append(rd); xadj.append(eda); labs.append(s)
        print(f"{s:>8} {ed:>+9.2f} {rd:>+9.2f} {eda:>+18.2f}")

    def ols(x, y):
        x = np.asarray(x); y = np.asarray(y)
        b = float(np.cov(x, y, ddof=0)[0, 1] / np.var(x))
        a = float(np.mean(y) - b * np.mean(x))
        r = float(np.corrcoef(x, y)[0, 1])
        return a, b, r

    a, b, rr = ols(xs, ys)
    print(f"\nOLS rest_dev ~ early_dev:            slope {b:.3f}, "
          f"intercept {a:+.2f}, Pearson r {rr:.3f} (n={len(xs)})")
    a2, b2, rr2 = ols(xadj, ys)
    print(f"OLS rest_dev ~ early_dev(phase-adj): slope {b2:.3f}, "
          f"intercept {a2:+.2f}, Pearson r {rr2:.3f}")
    med = float(np.median(xs))
    hi = [y for x, y in zip(xs, ys) if x > med]
    lo = [y for x, y in zip(xs, ys) if x <= med]
    print(f"two-group: hot-start seasons (early_dev>median) mean rest_dev "
          f"{np.mean(hi):+.2f} (n={len(hi)}); cold-start mean rest_dev "
          f"{np.mean(lo):+.2f} (n={len(lo)})")
    hot = [(x, y) for x, y in zip(xs, ys) if x > 0]
    print(f"reversion among hot starts: mean rest_dev/early_dev = "
          f"{np.mean([y/x for x, y in hot]):.3f} over {len(hot)} seasons")
    case_em = t_cal[CASE]["em"]
    case_ed = case_em - hist_norm
    case_eda = case_em - hist_norm * phi_early
    print(f"\n2026/27: early mean {case_em:.2f}, early_dev {case_ed:+.2f}, "
          f"phase-adj early_dev {case_eda:+.2f}")
    print(f"  historical |early_dev| range: "
          f"[{min(xs):+.2f},{max(xs):+.2f}]; |phase-adj| range: "
          f"[{min(xadj):+.2f},{max(xadj):+.2f}]")
    print(f"  persistence-implied rest-of-2026/27 level (raw slope): "
          f"{hist_norm + a + b * case_ed:.2f}; (phase-adj slope): "
          f"{hist_norm + a2 + b2 * case_eda:.2f}")

    # ---------------------------------------------------------------- Q4
    print("\n================ Q4: ARTEFACT CHECK (spine vs FotMob) ================")
    spine_map = {(r["div"], r["season"], r["date"].isoformat(),
                  r["home"], r["away"]): r["total"] for r in rows}
    fm = defaultdict(list)
    with open(FEATURES, newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            if r["season"] not in ("2024/25", "2025/26", CASE):
                continue
            if r["shots_h"] in (None, "") or r["shots_a"] in (None, ""):
                continue
            fm[r["season"]].append(r)
    for s in ("2024/25", "2025/26", CASE):
        diffs, matched, unmatched = [], 0, 0
        fm_tot, sp_tot = [], []
        for r in fm[s]:
            key = (r["div"], r["season"], r["date"], r["home"], r["away"])
            if key in spine_map:
                d = (int(float(r["shots_h"])) + int(float(r["shots_a"]))) \
                    - spine_map[key]
                diffs.append(d)
                fm_tot.append(int(float(r["shots_h"])) + int(float(r["shots_a"])))
                sp_tot.append(spine_map[key])
                matched += 1
            else:
                unmatched += 1
        diffs = np.asarray(diffs, dtype=float)
        print(f"{s}: matched {matched}, unmatched {unmatched}; "
              f"exact {pct(np.mean(diffs == 0))}, |d|<=1 "
              f"{pct(np.mean(np.abs(diffs) <= 1))}, |d|<=2 "
              f"{pct(np.mean(np.abs(diffs) <= 2))}, mean diff (FM-spine) "
              f"{np.mean(diffs):+.3f}, mean |diff| {np.mean(np.abs(diffs)):.3f}")
        print(f"   window means: FotMob {np.mean(fm_tot):.2f} vs spine "
              f"{np.mean(sp_tot):.2f} (same matched matches)")
    # independent FotMob-only early elevation (FotMob seasons 2022/23+)
    fm_all = defaultdict(list)
    with open(FEATURES, newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            if r["shots_h"] in (None, "") or r["shots_a"] in (None, ""):
                continue
            fm_all[r["season"]].append(r)
    print("\nFotMob counts alone: early (<=Nov 2) mean vs full-season mean:")
    for s in sorted(fm_all):
        y0 = int(s[:4])
        cut = date(y0, 11, 2).isoformat()
        e = [int(float(r["shots_h"])) + int(float(r["shots_a"]))
             for r in fm_all[s] if r["date"] <= cut]
        f = [int(float(r["shots_h"])) + int(float(r["shots_a"]))
             for r in fm_all[s]]
        tag = " (partial)" if s == CASE else ""
        print(f"  {s}: early {np.mean(e):.2f} (n={len(e)}), full "
              f"{np.mean(f):.2f}, elev {np.mean(e)-np.mean(f):+.2f}{tag}")


if __name__ == "__main__":
    main()
