#!/usr/bin/env python
"""Total shots model v2 — level-tracking design (PREREG.md).

Candidate = v1's frozen winner (ridge Poisson ratings lam=100 on
total shots, NB r=79.82, 50/50 probability ensemble with the naive
trailing-10 member) PLUS a per-division level layer: decayed sums of
actual totals vs the base candidate's own pre-match ensemble totals,
a shrunk ratio R, and a clipped factor f = 1 + s*(R-1) multiplying
both member totals before their NB probabilities. The layer's
hyperparameters (HL, s, K) are the only tuned quantities, selected
on 2022/23 line-25.5 log loss only. Verdict window: the virgin
2026/27 season, evaluated once. 2023/24-2025/26 are secondary
(drift comparison only).

One chronological pass; every state updates only AFTER the match is
predicted. Predictions are computed for every match (the regression's
lazy 7-day refits therefore anchor at the first match, a superset
cadence vs v1's eval pass — see PREREG.md; the no-layer arm in this
same pass is reported against v1's published numbers as the harness
check).

Run:  .venv/bin/python experiments/shots_model_v2/run_shots_experiment_v2.py
Writes only RESULTS.md next to itself. No production code touched.
"""

import math
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "shots_model"))
sys.path.insert(0, os.path.join(HERE, "..", "sot_model"))

from run_sot_v2 import (BASE_HL, BASE_K, NaiveTracker, Ratings,  # noqa: E402
                        TEST_SEASONS, TOP5, load_matches, logloss,
                        nb_over, poisson_over)
from run_shots_experiment import ShotsRegressionStore  # noqa: E402

OUT = os.path.join(HERE, "RESULTS.md")

# --- frozen from v1 tuning (pre-2023/24); NOT re-tuned here
LAM = 100.0
NB_R = 79.82

# --- level layer design (PREREG.md)
M_BAR = 25.0
F_LO, F_HI = 0.90, 1.10
CELLS = [(hl, s, k) for hl in (30.0, 60.0, 120.0)
         for s in (0.5, 1.0) for k in (20.0, 50.0)]
SE_FULL_PASS = 0.5  # pp; calibration leg "statistically meaningful"

TUNE_SEASON = "2022/23"
VERDICT_SEASON = "2026/27"
MAIN_LINE = 25.5
LINES = [22.5, 23.5, 24.5, 25.5, 26.5, 27.5, 28.5]
EPS = 1e-6

# v1 published numbers (experiments/shots_model/RESULTS.md) — harness check
V1_POOLED = {"ll": 0.6263, "calib": -1.34}
V1_SEASON = {"2023/24": (0.6285, -2.13), "2024/25": (0.6187, +0.17),
             "2025/26": (0.6318, -2.06)}


class LevelLayer:
    """Per-cell per-division decayed (actual, predicted) sums."""

    def __init__(self, cells):
        self.cells = cells
        self.state = [dict() for _ in cells]  # ci -> div -> [A, P, last]

    def _decayed(self, ci, div, day):
        hl = self.cells[ci][0]
        st = self.state[ci].get(div)
        if st is None:
            return None
        if day > st[2]:
            f = 0.5 ** ((day - st[2]) / hl)
            st[0] *= f
            st[1] *= f
            st[2] = day
        return st

    def factor(self, ci, div, day):
        _, s, k = self.cells[ci]
        st = self._decayed(ci, div, day)
        if st is None:
            return 1.0
        r = (st[0] + k * M_BAR) / (st[1] + k * M_BAR)
        return min(F_HI, max(F_LO, 1.0 + s * (r - 1.0)))

    def update(self, ci, div, day, actual, pred):
        st = self._decayed(ci, div, day)
        if st is None:
            self.state[ci][div] = [float(actual), float(pred), day]
        else:
            st[0] += actual
            st[1] += pred


class Acc:
    """Accumulator at the main line (+ optional per-line LL)."""

    def __init__(self, lines=()):
        self.n = 0
        self.ll = 0.0
        self.brier = 0.0
        self.sp = 0.0
        self.sy = 0.0
        self.sd = 0.0
        self.sd2 = 0.0
        self.mae = 0.0
        self.ll_lines = {L: 0.0 for L in lines}

    def add(self, p, y, pt, total, lines_p=None):
        self.n += 1
        self.ll += logloss(p, y)
        self.brier += (p - y) ** 2
        self.sp += p
        self.sy += y
        d = p - y
        self.sd += d
        self.sd2 += d * d
        self.mae += abs(pt - total)
        if lines_p:
            for L, pl in lines_p.items():
                self.ll_lines[L] += logloss(pl, 1.0 if total > L else 0.0)

    def stats(self):
        n = self.n
        return {"n": n, "ll": self.ll / n, "brier": self.brier / n,
                "pred": 100 * self.sp / n, "act": 100 * self.sy / n,
                "calib": (self.sp - self.sy) / n * 100,
                "mae": self.mae / n,
                "se": 100 * math.sqrt(max(self.sd2 / n
                                          - (self.sd / n) ** 2, 0.0)
                                      / n)}


def ens_prob(lt, lt_n, f):
    return 0.5 * nb_over(lt * f, NB_R, MAIN_LINE) \
        + 0.5 * nb_over(lt_n * f, NB_R, MAIN_LINE)


def main():
    t0 = time.time()
    matches = load_matches()
    reg = ShotsRegressionStore(matches, [LAM])
    naive = NaiveTracker()
    shots_rt = Ratings(BASE_HL, BASE_K, "shots")
    layer = LevelLayer(CELLS)
    nc = len(CELLS)

    tune = [Acc() for _ in range(nc)]          # per cell, 2022/23 @25.5
    tune_nolayer = Acc()
    sec = {"cell": [Acc() for _ in range(nc)], "nolayer": Acc(),
           "base_league": Acc(), "base_naive": Acc()}
    sec_season = {s: {"cell": [Acc() for _ in range(nc)], "nolayer": Acc()}
                  for s in TEST_SEASONS}
    ver = {"cell": [Acc(LINES) for _ in range(nc)], "nolayer": Acc(LINES),
           "base_league": Acc(LINES), "base_naive": Acc(LINES)}
    ver_div = {d: {"cell": [Acc() for _ in range(nc)], "nolayer": Acc(),
                   "base_league": Acc(), "base_naive": Acc()}
               for d in TOP5}
    ver_top5 = [Acc() for _ in range(nc)]      # per cell, top-5 only

    for m in matches:
        day, div = m["day"], m["div"]
        home, away = m["home"], m["away"]
        season = m["season"]
        total = m["hs"] + m["as"]
        y = 1.0 if total > MAIN_LINE else 0.0

        eh, ea = reg.predict(div, home, away, day, LAM)
        lt = eh + ea
        rmu_h, rmu_a = reg.league_mu(div, day, LAM)
        nh_r, na_r = naive.predict(div, home, away, rmu_h, rmu_a)
        lt_nr = nh_r + na_r
        ens_total = 0.5 * (lt + lt_nr)

        scope = ("tune" if season == TUNE_SEASON
                 else "sec" if season in TEST_SEASONS
                 else "ver" if season == VERDICT_SEASON else None)

        if scope == "tune":
            tune_nolayer.add(ens_prob(lt, lt_nr, 1.0), y, ens_total, total)
            for ci in range(nc):
                f = layer.factor(ci, div, day)
                tune[ci].add(ens_prob(lt, lt_nr, f), y, f * ens_total,
                             total)
        elif scope in ("sec", "ver"):
            mu_h, mu_a, _, _ = shots_rt.league_mu(div, day)
            lt_base = mu_h + mu_a
            nh, na = naive.predict(div, home, away, mu_h, mu_a)
            lt_nb = nh + na
            tgt = sec if scope == "sec" else ver
            lines_p = None
            if scope == "ver":
                lines_p = {
                    "base_league": {L: poisson_over(lt_base, L)
                                    for L in LINES},
                    "base_naive": {L: poisson_over(lt_nb, L)
                                   for L in LINES},
                    "nolayer": {L: 0.5 * nb_over(lt, NB_R, L)
                                + 0.5 * nb_over(lt_nr, NB_R, L)
                                for L in LINES}}
            tgt["base_league"].add(poisson_over(lt_base, MAIN_LINE), y,
                                   lt_base, total,
                                   lines_p["base_league"] if lines_p
                                   else None)
            tgt["base_naive"].add(poisson_over(lt_nb, MAIN_LINE), y,
                                  lt_nb, total,
                                  lines_p["base_naive"] if lines_p
                                  else None)
            tgt["nolayer"].add(ens_prob(lt, lt_nr, 1.0), y, ens_total,
                               total,
                               lines_p["nolayer"] if lines_p else None)
            for ci in range(nc):
                f = layer.factor(ci, div, day)
                lp = None
                if scope == "ver":
                    lp = {L: 0.5 * nb_over(lt * f, NB_R, L)
                          + 0.5 * nb_over(lt_nr * f, NB_R, L)
                          for L in LINES}
                tgt["cell"][ci].add(ens_prob(lt, lt_nr, f), y,
                                    f * ens_total, total, lp)
            if scope == "sec":
                ss = sec_season[season]
                ss["nolayer"].add(ens_prob(lt, lt_nr, 1.0), y, ens_total,
                                  total)
                for ci in range(nc):
                    f = layer.factor(ci, div, day)
                    ss["cell"][ci].add(ens_prob(lt, lt_nr, f), y,
                                       f * ens_total, total)
            else:
                if div in TOP5:
                    dv = ver_div[div]
                    dv["base_league"].add(poisson_over(lt_base, MAIN_LINE),
                                          y, lt_base, total)
                    dv["base_naive"].add(poisson_over(lt_nb, MAIN_LINE),
                                         y, lt_nb, total)
                    dv["nolayer"].add(ens_prob(lt, lt_nr, 1.0), y,
                                      ens_total, total)
                    for ci in range(nc):
                        f = layer.factor(ci, div, day)
                        dv["cell"][ci].add(ens_prob(lt, lt_nr, f), y,
                                           f * ens_total, total)
                        ver_top5[ci].add(ens_prob(lt, lt_nr, f), y,
                                         f * ens_total, total)

        # ---- state updates (after prediction, every match)
        shots_rt.update(div, home, away, day, m["hs"], m["as"])
        naive.update(div, home, away, m["hs"], m["as"])
        for ci in range(nc):
            layer.update(ci, div, day, total, ens_total)

    # ---- selection on tuning ONLY (ties: larger HL, smaller s, larger K)
    def sel_key(ci):
        hl, s, k = CELLS[ci]
        return (tune[ci].stats()["ll"], -hl, s, -k)

    best_ci = min(range(nc), key=sel_key)
    bhl, bs, bk = CELLS[best_ci]
    runtime = time.time() - t0

    cand = ver["cell"][best_ci].stats()
    nol = ver["nolayer"].stats()
    bl = ver["base_league"].stats()
    bn = ver["base_naive"].stats()
    best_base_ll = min(bl["ll"], bn["ll"])
    margin = best_base_ll - cand["ll"]
    gate1 = margin >= 0.001
    gate2 = abs(cand["calib"]) <= 1.0
    div_rows = {}
    worst_div_excess = -1e9
    for d in TOP5:
        dc = ver_div[d]["cell"][best_ci].stats()
        db = min(ver_div[d]["base_league"].stats()["ll"],
                 ver_div[d]["base_naive"].stats()["ll"])
        div_rows[d] = (dc, db)
        worst_div_excess = max(worst_div_excess, dc["ll"] - db)
    gate3 = worst_div_excess <= 0.0003
    point_pass = gate1 and gate2 and gate3
    if not point_pass:
        verdict = "FAIL"
    elif cand["se"] <= SE_FULL_PASS:
        verdict = "PASS"
    else:
        verdict = "PROVISIONAL PASS"
    t5 = ver_top5[best_ci].stats()

    sec_nol = sec["nolayer"].stats()
    sec_cand = sec["cell"][best_ci].stats()

    out = []
    out.append("# Total Shots Model v2 — Experiment Results")
    out.append("")
    out.append("Script: `run_shots_experiment_v2.py`. Design and gate: "
               "`PREREG.md` (committed before this run). Candidate = "
               "v1's frozen winner (ridge lam=100, NB r=79.82, 50/50 "
               "naive ensemble) + a per-division level layer. Verdict "
               "window: the virgin 2026/27 season, evaluated once.")
    out.append("")
    out.append(f"Verdict window evaluated matches: {cand['n']:,} "
               f"(of which top-5: {t5['n']:,})")
    out.append("")
    out.append("## Level layer — tuning (2022/23 LL@25.5, selection "
               "reads this table only)")
    out.append("")
    out.append("| HL (days) | s | K | LL@25.5 |")
    out.append("|---|---|---|---|")
    order = sorted(range(nc), key=sel_key)
    for ci in order:
        hl, s, k = CELLS[ci]
        mark = " ← chosen" if ci == best_ci else ""
        out.append(f"| {hl:g} | {s:g} | {k:g} | "
                   f"{tune[ci].stats()['ll']:.4f}{mark} |")
    out.append("")
    out.append(f"No-layer arm (v1 candidate) on the same tuning pass: "
               f"{tune_nolayer.stats()['ll']:.4f}.")
    out.append("")
    out.append(f"**Frozen layer cell: HL = {bhl:g} days, s = {bs:g}, "
               f"K = {bk:g}** (factor clip [{F_LO}, {F_HI}], prior "
               f"mean M̄ = {M_BAR}).")
    out.append("")
    out.append("## Harness check — no-layer arm vs v1 published "
               "(secondary window 2023/24–2025/26, pooled)")
    out.append("")
    out.append(f"v1 published: LL {V1_POOLED['ll']:.4f}, calib "
               f"{V1_POOLED['calib']:+.2f}pp. This pass, no-layer arm: "
               f"LL {sec_nol['ll']:.4f}, calib {sec_nol['calib']:+.2f}pp. "
               "Any small deviation is the refit-anchoring difference "
               "documented in PREREG.md (predictions computed for every "
               "match here; v1's eval pass predicted test seasons only) "
               "— both cadences are strictly walk-forward honest, and "
               "the v1-vs-v2 comparison below uses arms from THIS pass, "
               "which share one trajectory.")
    out.append("")
    out.append("## Secondary window — per-season drift @25.5 "
               "(NOT the verdict)")
    out.append("")
    out.append("| Season | n | v1 published calib | v2 no-layer "
               "calib | v2 layered calib | v2 layered LL | v2 "
               "no-layer LL |")
    out.append("|---|---|---|---|---|---|---|")
    for sname in TEST_SEASONS:
        sn = sec_season[sname]["nolayer"].stats()
        sc = sec_season[sname]["cell"][best_ci].stats()
        v1ll, v1cal = V1_SEASON[sname]
        out.append(f"| {sname} | {sc['n']:,} | {v1cal:+.2f}pp | "
                   f"{sn['calib']:+.2f}pp | {sc['calib']:+.2f}pp | "
                   f"{sc['ll']:.4f} | {sn['ll']:.4f} |")
    out.append("")
    out.append(f"Pooled secondary: layered calib "
               f"{sec_cand['calib']:+.2f}pp (LL {sec_cand['ll']:.4f}) "
               f"vs no-layer {sec_nol['calib']:+.2f}pp "
               f"(LL {sec_nol['ll']:.4f}).")
    out.append("")
    out.append("## Verdict window (2026/27) — headline, line 25.5")
    out.append("")
    out.append("| Method | LogLoss | Brier | Pred Over% | Actual Over% | Calib (pp, signed) | MAE |")
    out.append("|---|---|---|---|---|---|---|")
    for name, s_ in (("Candidate v2 (layered)", cand),
                     ("No-layer arm (v1 candidate)", nol),
                     ("Baseline (a) division base rate", bl),
                     ("Baseline (b) naive trailing-10", bn)):
        out.append(f"| {name} | {s_['ll']:.4f} | {s_['brier']:.4f} | "
                   f"{s_['pred']:.1f} | {s_['act']:.1f} | "
                   f"{s_['calib']:+.2f} | {s_['mae']:.2f} |")
    out.append("")
    out.append(f"Calibration standard error (pooled, candidate): "
               f"**{cand['se']:.2f}pp** at n = {cand['n']:,}. "
               f"Top-5 only, for information: calib "
               f"{t5['calib']:+.2f}pp, SE {t5['se']:.2f}pp at "
               f"n = {t5['n']:,}; candidate top-5 LL {t5['ll']:.4f}.")
    out.append("")
    out.append("## Verdict window — all lines, pooled log loss")
    out.append("")
    out.append("| Method | " + " | ".join(f"{L}" for L in LINES) + " |")
    out.append("|---|" + "---|" * len(LINES))
    for name, acc in (("Candidate v2 (layered)", ver["cell"][best_ci]),
                      ("No-layer arm (v1 candidate)", ver["nolayer"]),
                      ("Baseline (a) division base rate",
                       ver["base_league"]),
                      ("Baseline (b) naive trailing-10",
                       ver["base_naive"])):
        cells = " | ".join(f"{acc.ll_lines[L] / acc.n:.4f}"
                           for L in LINES)
        out.append(f"| {name} | {cells} |")
    out.append("")
    out.append("## Verdict window — by division (top-5), line 25.5")
    out.append("")
    out.append("| Div | n | Candidate LL | Best baseline LL | Δ | Candidate calib (pp) |")
    out.append("|---|---|---|---|---|---|")
    for d in TOP5:
        dc, db = div_rows[d]
        out.append(f"| {d} | {dc['n']:,} | {dc['ll']:.4f} | {db:.4f} | "
                   f"{dc['ll'] - db:+.4f} | {dc['calib']:+.2f} |")
    out.append("")
    out.append("## Gate verdict (PREREG.md, fixed before the run; "
               "2026/27 window)")
    out.append("")
    out.append(f"1. Pooled LL@25.5 beats best baseline by ≥ 0.001: "
               f"margin {margin:+.4f} → **{'PASS' if gate1 else 'FAIL'}**.")
    out.append(f"2. Calibration @25.5 point estimate within ±1.0pp: "
               f"{cand['calib']:+.2f}pp → "
               f"**{'PASS' if gate2 else 'FAIL'}** (point estimate). "
               f"SE = {cand['se']:.2f}pp vs the ±1.0pp band: "
               + (f"statistically meaningful (SE ≤ {SE_FULL_PASS}pp)."
                  if cand["se"] <= SE_FULL_PASS else
                  f"NOT statistically meaningful (SE > "
                  f"{SE_FULL_PASS}pp) — the honesty clause applies."))
    out.append(f"3. Worst top-5 division excess over its best baseline "
               f"≤ 0.0003: {worst_div_excess:+.4f} → "
               f"**{'PASS' if gate3 else 'FAIL'}**.")
    out.append("")
    if verdict == "PASS":
        out.append("**VERDICT: PASS — proceed to production build "
                   "(Phase 2, as scoped in the v1 brief).**")
    elif verdict == "PROVISIONAL PASS":
        out.append("**VERDICT: PROVISIONAL PASS — all three legs pass "
                   "on point values, but the calibration leg is not "
                   "statistically meaningful at this sample size "
                   f"(SE {cand['se']:.2f}pp > {SE_FULL_PASS}pp). Per "
                   "the pre-registered honesty clause: NO production "
                   "wiring, no cron change. A single confirmation "
                   "re-run of this frozen design is pre-committed for "
                   "when the labelled top-5 2026/27 count reaches "
                   "≈ 1,500 (pooled n then ≈ 6,700, expected SE "
                   "≈ 0.60pp); all-legs point-PASS with SE ≤ 0.65pp "
                   "there converts to PASS, a point failure to "
                   "FAIL.**")
    else:
        out.append("**VERDICT: FAIL — production stays untouched; "
                   "this market remains unmodelled.**")
    out.append("")
    out.append("## Method notes and caveats")
    out.append("")
    out.append("- The level layer tracks the base candidate's OWN "
               "pre-match predictions (unadjusted), so it estimates "
               "the base model's trailing level bias per division; "
               "it cannot chase its own corrections.")
    out.append("- The baselines include no NB dispersion (house "
               "definition since the SOT base experiment); the "
               "candidate's edge partly reflects dispersion, as in "
               "v1 — the secondary-window drift table, not the LL "
               "margin, is the direct evidence on the layer itself.")
    out.append("- Provider disagreement on total shots is larger "
               "than for SOT (O/U flip 1.43–2.04% across the ladder, "
               "v1 PREREG.md): the model is trained and graded on "
               "the spine's count; bookmaker settlement on another "
               "count is a pricing-side risk, not a model error.")
    out.append("- No odds anywhere: predictive accuracy/calibration "
               "only, not betting value (no total-shots odds in our "
               "data).")
    out.append(f"- Script runtime (this run, incl. data load): "
               f"{runtime:.0f}s.")

    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write("\n".join(out) + "\n")

    print(f"frozen: lam={LAM:g} r={NB_R}  layer cell: HL={bhl:g} "
          f"s={bs:g} K={bk:g}")
    print("  tune LL by cell: " + ", ".join(
        f"({CELLS[ci][0]:g},{CELLS[ci][1]:g},{CELLS[ci][2]:g}):"
        f"{tune[ci].stats()['ll']:.4f}" for ci in range(nc)))
    print(f"  tune no-layer: {tune_nolayer.stats()['ll']:.4f}")
    print(f"harness check (secondary pooled, no-layer): "
          f"LL {sec_nol['ll']:.4f} (v1 pub 0.6263), calib "
          f"{sec_nol['calib']:+.2f}pp (v1 pub -1.34)")
    print(f"secondary layered pooled: LL {sec_cand['ll']:.4f}, "
          f"calib {sec_cand['calib']:+.2f}pp")
    for sname in TEST_SEASONS:
        sn = sec_season[sname]["nolayer"].stats()
        sc = sec_season[sname]["cell"][best_ci].stats()
        print(f"  {sname}: calib nolayer {sn['calib']:+.2f} -> "
              f"layered {sc['calib']:+.2f} (v1 pub "
              f"{V1_SEASON[sname][1]:+.2f})")
    print(f"verdict window n = {cand['n']:,} (top-5 {t5['n']:,})")
    print(f"{'method':34s} {'LL@25.5':>8s} {'calib':>8s} {'SE':>6s} "
          f"{'MAE':>5s}")
    for name, s_ in (("candidate v2", cand), ("no-layer", nol),
                     ("base_league", bl), ("base_naive", bn)):
        print(f"{name:34s} {s_['ll']:8.4f} {s_['calib']:+7.2f}p "
              f"{s_['se']:5.2f}p {s_['mae']:5.2f}")
    print(f"gate: margin {margin:+.4f} ({gate1}), calib "
          f"{cand['calib']:+.2f}pp ({gate2}), worst div "
          f"{worst_div_excess:+.4f} ({gate3}) -> {verdict}")
    print(f"runtime: {runtime:.0f}s")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
