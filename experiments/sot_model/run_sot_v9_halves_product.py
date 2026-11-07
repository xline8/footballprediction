#!/usr/bin/env python
"""SOT v9 — the HALVES SPLIT as a product in its own right.

Context: production model_sot.py (v5) predicts full-time SOT only. The
v6 experiment (run_sot_v6_halves.py, RESULTS_V6_HALVES.md) built per-half
ratings machinery but judged it ONLY as a full-time improver, and it
failed that gate. The halves as a prediction product were never gated
against half baselines. This script does exactly that.

PRODUCT (decided design): the FT total stays production v5's expectation
(exp per team = 0.5 * joint-regression + 0.5 * BB shots-implied, exactly
the model member production writes). The new product is the SPLIT: a
modelled share of each team's SOT expected in the 1H vs the 2H, from
the v6 halves machinery:

    E1H_team  from a per-half joint ridge-Poisson regression store
              fitted on first-half SOT (sot_1h_h / sot_1h_a);
    E2H_team  from the same kind of store on second-half SOT, then
              conditioned on the half-time state distribution:
                  E2H_cond = E2H * sum_s P(state s) * mult_s
              with the HT-state probabilities from a third regression
              store on HT goals and the FROZEN v6 multipliers
              (lead 0.964 / level 0.978 / trail 1.049, estimated on
              2019/20-2022/23 in the v6 round and frozen since);
    share_1H_team = E1H / (E1H + E2H_cond).

    exp_sot_1h_team = exp_v5_team * share_1H_team
    exp_sot_2h_team = exp_v5_team * (1 - share_1H_team)

so the split sums to the v5 total by construction. Half totals are
distributed negative-binomial with sizes r_1h / r_2h estimated by
method of moments from walk-forward warm-up residuals over
2019/20-2022/23 only (the same way v5's FT r=79.94 was estimated) and
frozen before the test seasons.

BASELINES (same v5 total, same NB sizes — only the split differs):
  (a) constant league share: every team split by the single frozen 1H
      share S = sum(1H SOT) / sum(FT SOT) over halves-labelled top-5
      matches in 2019/20-2022/23.
  (b) naive trailing team share: each team split by its own trailing-10
      matches' 1H share of its own SOT (walk-forward from the halves
      labels; falls back to S with <5 labelled matches).

EVALUATION: walk-forward, test seasons 2023/24-2025/26, top-5, actuals
from data_enrichment/sot_halves_combined.csv (matches without a halves
label are skipped for half scoring and counted). Natural half lines:
1H 3.5/4.5/5.5, 2H 4.5/5.5/6.5. Metrics per half: pooled log loss over
the three lines, calibration (mean |pred Over% - actual%| over lines),
MAE of the half total.

PRE-REGISTERED BAR: the product must beat baseline (a) on BOTH halves'
pooled log loss AND not be worse-calibrated than (a) by > 0.5pp on
either half. Per-division numbers are reported. Production is NOT
changed by this script either way.

Run:  .venv/bin/python experiments/sot_model/run_sot_v9_halves_product.py
Writes only RESULTS_V9_HALVES_PRODUCT.md next to itself.
"""

import csv
import math
import os
import sys
import time
from collections import defaultdict, deque

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ROOT = os.path.join(HERE, "..", "..")

from run_sot_v2 import (MAIN_LINE, TEST_SEASONS, TOP5,  # noqa: E402
                        NaiveTracker, Ratings, load_matches, nb_over)
from run_sot_v5 import (BASE_HL, BASE_K, RegressionStore, bb_ratio,  # noqa: E402
                        new_acc, add, stats, pass_warmup, slim_components,
                        update_all)
from run_sot_v6_halves import (load_halves, load_ht_goals,  # noqa: E402
                               poisson_state_probs, store_matches)

OUT = os.path.join(HERE, "RESULTS_V9_HALVES_PRODUCT.md")
FROZEN_LAM = 100.0
FROZEN_P = 200.0
MULTS = {"lead": 0.964, "level": 0.978, "trail": 1.049}  # frozen in v6
WARM_SEASONS = ["2019/20", "2020/21", "2021/22", "2022/23"]
LINES_1H = [3.5, 4.5, 5.5]
LINES_2H = [4.5, 5.5, 6.5]
HALF_LINES = {"1H": LINES_1H, "2H": LINES_2H}
VARIANTS = ("product", "base_share", "base_naive")
NAIVE_N = 10
NAIVE_MIN = 5


class ShareTracker:
    """Baseline (b): per (div, team) trailing-10 own-SOT 1H share."""

    def __init__(self):
        self.hist = defaultdict(lambda: deque(maxlen=NAIVE_N))

    def share(self, div, team, fallback):
        h = self.hist[(div, team)]
        if len(h) < NAIVE_MIN:
            return fallback
        s1 = sum(x[0] for x in h)
        s2 = sum(x[1] for x in h)
        if s1 + s2 <= 0:
            return fallback
        return s1 / (s1 + s2)

    def update(self, div, home, away, halves):
        self.hist[(div, home)].append((halves[0], halves[2]))
        self.hist[(div, away)].append((halves[1], halves[3]))


def build_stores(matches, halves, ht_goals):
    reg_1h = RegressionStore(
        store_matches(matches, lambda m: (
            (halves[(m["div"], m["date"], m["home"], m["away"])][0],
             halves[(m["div"], m["date"], m["home"], m["away"])][1])
            if (m["div"], m["date"], m["home"], m["away"]) in halves
            else None)), [FROZEN_LAM])
    reg_2h = RegressionStore(
        store_matches(matches, lambda m: (
            (halves[(m["div"], m["date"], m["home"], m["away"])][2],
             halves[(m["div"], m["date"], m["home"], m["away"])][3])
            if (m["div"], m["date"], m["home"], m["away"]) in halves
            else None)), [FROZEN_LAM])
    reg_ht = RegressionStore(
        store_matches(matches, lambda m: ht_goals.get(
            (m["div"], m["date"], m["home"], m["away"]))), [FROZEN_LAM])
    return reg_1h, reg_2h, reg_ht


def product_split(reg_1h, reg_2h, reg_ht, div, home, away, day,
                  league_share):
    """(share_1h_home, share_1h_away) from the halves machinery."""
    e1h, e1a = reg_1h.predict(div, home, away, day, FROZEN_LAM)
    e2h, e2a = reg_2h.predict(div, home, away, day, FROZEN_LAM)
    gh, ga = reg_ht.predict(div, home, away, day, FROZEN_LAM)
    p_lead, p_level, p_trail = poisson_state_probs(gh, ga)
    mix_h = (p_lead * MULTS["lead"] + p_level * MULTS["level"]
             + p_trail * MULTS["trail"])
    mix_a = (p_trail * MULTS["lead"] + p_level * MULTS["level"]
             + p_lead * MULTS["trail"])
    den_h = e1h + e2h * mix_h
    den_a = e1a + e2a * mix_a
    sh_h = e1h / den_h if den_h > 0 else league_share
    sh_a = e1a / den_a if den_a > 0 else league_share
    return sh_h, sh_a


def walk(matches, halves, ht_goals, best_lam, best_p, mode,
         r_half=None, league_share=None):
    """One chronological pass. mode='warm' collects warm-up residuals
    and league-share sums; mode='eval' scores the test seasons."""
    sot = Ratings(BASE_HL, BASE_K, "sot")
    shots = Ratings(BASE_HL, BASE_K, "shots", track_ratio=True)
    naive = NaiveTracker()
    tracker = ShareTracker()
    reg_ft = RegressionStore(matches, [best_lam])
    reg_1h, reg_2h, reg_ht = build_stores(matches, halves, ht_goals)

    resid = {"1H": [], "2H": []}          # (mu, y) warm-up pairs
    share_sums = [0, 0]                  # sum 1H SOT, sum FT SOT (warm)
    acc = {v: {h: new_acc(HALF_LINES[h]) for h in HALF_LINES}
           for v in VARIANTS}
    div_acc = {v: {h: {d: new_acc(HALF_LINES[h]) for d in TOP5}
                  for h in HALF_LINES} for v in ("product", "base_share")}
    mae = {v: {h: [0, 0.0] for h in HALF_LINES} for v in VARIANTS}
    ft_acc = new_acc([MAIN_LINE])
    n_scored = n_nolabel = 0

    for m in matches:
        day, div = m["day"], m["div"]
        home, away = m["home"], m["away"]
        key = (div, m["date"], home, away)
        in_warm = mode == "warm" and m["season"] in WARM_SEASONS
        in_test = mode == "eval" and m["season"] in TEST_SEASONS
        if (in_warm or in_test) and div in TOP5:
            if key not in halves:
                if in_test:
                    n_nolabel += 1
            else:
                hv = halves[key]
                y1 = hv[0] + hv[1]
                y2 = hv[2] + hv[3]
                (eh, ea, seh, sea, imp_h, imp_a, lam1,
                 lam_n) = slim_components(sot, shots, naive, div, home,
                                          away, day)
                ib_h = seh * bb_ratio(shots, div, home, "h", day, best_p)
                ib_a = sea * bb_ratio(shots, div, away, "a", day, best_p)
                reh, rea = reg_ft.predict(div, home, away, day, best_lam)
                exp_h = 0.5 * (reh + ib_h)
                exp_a = 0.5 * (rea + ib_a)
                total = exp_h + exp_a
                sh_h, sh_a = product_split(reg_1h, reg_2h, reg_ht, div,
                                           home, away, day,
                                           league_share or 0.46)
                mu1_prod = exp_h * sh_h + exp_a * sh_a
                if in_warm:
                    resid["1H"].append((mu1_prod, y1))
                    resid["2H"].append((total - mu1_prod, y2))
                    share_sums[0] += y1
                    share_sums[1] += y1 + y2
                else:
                    n_scored += 1
                    ls = league_share
                    mu = {
                        "product": (mu1_prod, total - mu1_prod),
                        "base_share": (total * ls, total * (1.0 - ls)),
                        "base_naive": (
                            exp_h * tracker.share(div, home, ls)
                            + exp_a * tracker.share(div, away, ls),
                            None),
                    }
                    mu["base_naive"] = (mu["base_naive"][0],
                                        total - mu["base_naive"][0])
                    ys = {"1H": y1, "2H": y2}
                    for v in VARIANTS:
                        for h, lines in HALF_LINES.items():
                            mu_h = mu[v][0] if h == "1H" else mu[v][1]
                            mae[v][h][0] += 1
                            mae[v][h][1] += abs(mu_h - ys[h])
                            for L in lines:
                                p = nb_over(mu_h, r_half[h], L)
                                add(acc[v][h], L, p,
                                    1.0 if ys[h] > L else 0.0)
                            if v in div_acc:
                                for L in lines:
                                    p = nb_over(mu_h, r_half[h], L)
                                    add(div_acc[v][h][div], L, p,
                                        1.0 if ys[h] > L else 0.0)
                    # FT continuity: v5 ensemble on the same match
                    rmu_h, rmu_a = reg_ft.league_mu(div, day, best_lam)
                    nh_r, na_r = naive.predict(div, home, away,
                                               rmu_h, rmu_a)
                    lam_ft = exp_h + exp_a
                    p95 = 0.5 * nb_over(lam_ft, 79.94, MAIN_LINE) \
                        + 0.5 * nb_over(nh_r + na_r, 79.94, MAIN_LINE)
                    add(ft_acc, MAIN_LINE, p95,
                        1.0 if m["hst"] + m["ast"] > MAIN_LINE else 0.0)
        update_all(sot, shots, naive, m)
        if key in halves:
            tracker.update(div, home, away, halves[key])

    return {"resid": resid, "share_sums": share_sums, "acc": acc,
            "div_acc": div_acc, "mae": mae, "ft_acc": ft_acc,
            "n_scored": n_scored, "n_nolabel": n_nolabel}


def pool(acc_h, lines):
    """Pooled (over lines) log loss and mean calibration error (pp)."""
    ll_sum = sum(acc_h[L][2] for L in lines)
    n_sum = sum(acc_h[L][0] for L in lines)
    calib = float(np.mean([stats(acc_h, L)["calib"] for L in lines]))
    return ll_sum / n_sum, calib


def mom_r(pairs):
    smu = sum(mu for mu, _ in pairs)
    smu2 = sum(mu * mu for mu, _ in pairs)
    sres = sum((y - mu) ** 2 for mu, y in pairs)
    den = sres - smu
    if den <= 0:
        return 1000.0
    return min(max(smu2 / den, 5.0), 1000.0)


def main():
    t0 = time.time()
    matches = load_matches()
    halves = load_halves()
    ht_goals = load_ht_goals()

    ll_r, ll_bb, nb_r_ft, _resid = pass_warmup(matches)
    tune_r = {lam: s / n for lam, (n, s) in ll_r.items()}
    tune_bb = {p: s / n for p, (n, s) in ll_bb.items()}
    best_lam = min(tune_r, key=lambda l: (tune_r[l], -l))
    best_p = min(tune_bb, key=lambda p: (tune_bb[p], -p))
    assert best_lam == FROZEN_LAM and best_p == FROZEN_P, (
        f"v5 warm-up choices changed: lam={best_lam} p={best_p}")

    warm = walk(matches, halves, ht_goals, best_lam, best_p, "warm")
    r_half = {h: mom_r(warm["resid"][h]) for h in HALF_LINES}
    league_share = warm["share_sums"][0] / warm["share_sums"][1]
    n_warm = len(warm["resid"]["1H"])

    ev = walk(matches, halves, ht_goals, best_lam, best_p, "eval",
              r_half=r_half, league_share=league_share)
    runtime = time.time() - t0

    res = {}
    for v in VARIANTS:
        res[v] = {}
        for h, lines in HALF_LINES.items():
            ll, cal = pool(ev["acc"][v][h], lines)
            res[v][h] = {"ll": ll, "calib": cal,
                         "mae": ev["mae"][v][h][1] / ev["mae"][v][h][0]}
    div_res = {}
    for v in ("product", "base_share"):
        div_res[v] = {}
        for h, lines in HALF_LINES.items():
            div_res[v][h] = {d: pool(ev["div_acc"][v][h][d], lines)[0]
                             for d in TOP5}
    ft = stats(ev["ft_acc"])

    gate_ll = all(res["product"][h]["ll"] < res["base_share"][h]["ll"]
                  for h in HALF_LINES)
    gate_calib = all(
        res["product"][h]["calib"] <= res["base_share"][h]["calib"] + 0.5
        for h in HALF_LINES)
    passed = gate_ll and gate_calib

    # ------------------------------------------------------------- report
    lbl = {"product": "PRODUCT (v5 total x modelled share)",
           "base_share": "baseline (a) constant league share",
           "base_naive": "baseline (b) naive trailing team share"}
    out = []
    out.append("# Model SOT v9 — Produk Pecahan Babak (1H / 2H / Total)")
    out.append("")
    out.append("## Ringkasan (Bahasa Indonesia)")
    out.append("")
    out.append(
        "Pertanyaan: v6 membangun mesin rating per babak tetapi hanya "
        "dinilai sebagai peningkat total full-time — dan gagal di "
        "gerbang itu. Di sini pecahan babak dinilai sebagai PRODUK "
        "tersendiri: total full-time tetap ekspektasi produksi v5, yang "
        "baru adalah PECAHANNYA — porsi SOT tiap tim yang dimodelkan "
        "jatuh di babak 1 vs babak 2 (rating per babak + pengali "
        "keadaan turun minum beku dari v6), dinilai melawan dua "
        "baseline pecahan pada total v5 yang sama.")
    out.append("")
    out.append(
        f"Jawaban: **{'LOLOS gerbang pra-registrasi' if passed else 'TIDAK LOLOS gerbang pra-registrasi'}**. "
        f"Pada {ev['n_scored']:,} laga uji lima liga top "
        f"(2023/24–2025/26; {ev['n_nolabel']} laga tanpa label babak "
        f"dilewati): log loss pooled babak 1 produk "
        f"{res['product']['1H']['ll']:.4f} vs baseline (a) "
        f"{res['base_share']['1H']['ll']:.4f}; babak 2 produk "
        f"{res['product']['2H']['ll']:.4f} vs baseline (a) "
        f"{res['base_share']['2H']['ll']:.4f}. Kalibrasi babak 1: "
        f"{res['product']['1H']['calib']:.2f}pp vs "
        f"{res['base_share']['1H']['calib']:.2f}pp; babak 2: "
        f"{res['product']['2H']['calib']:.2f}pp vs "
        f"{res['base_share']['2H']['calib']:.2f}pp. "
        + ("Pecahan yang dimodelkan mengalahkan pecahan konstan di "
           "kedua babak tanpa mengorbankan kalibrasi — produk layak "
           "dibangun (model_sot_halves.py), totalnya tetap v5."
           if passed else
           "Produk TIDAK dibangun; produksi tetap v5 total saja."))
    out.append("")
    out.append("## Frozen quantities (tuning era only, <=2022/23)")
    out.append("")
    out.append(f"- League 1H share S (baseline a), from "
               f"{n_warm:,} halves-labelled top-5 matches in "
               f"2019/20–2022/23: **{league_share:.4f}**")
    out.append(f"- NB sizes by method of moments on walk-forward "
               f"warm-up residuals (same {n_warm:,} matches): "
               f"r_1H = **{r_half['1H']:.2f}**, r_2H = "
               f"**{r_half['2H']:.2f}** (FT reference r = 79.94).")
    out.append(f"- HT-state multipliers (frozen in v6): lead "
               f"{MULTS['lead']}, level {MULTS['level']}, trail "
               f"{MULTS['trail']}. Ridge lambda = {best_lam:g}, "
               f"BB prior = {best_p:g} (v5 warm-up re-derived, asserted).")
    out.append(f"- FT continuity check on the scored set: v5 ensemble "
               f"line-9.5 log loss {ft['ll']:.4f} (v6 reported 0.6488 "
               f"on all top-5 test matches; the scored set here drops "
               f"the {ev['n_nolabel']} unlabelled match).")
    out.append("")
    out.append("## Headline — per half, pooled over the half's lines")
    out.append("")
    out.append("| Variant | 1H log loss | 1H calib (pp) | 1H MAE | "
               "2H log loss | 2H calib (pp) | 2H MAE |")
    out.append("|---|---|---|---|---|---|---|")
    for v in VARIANTS:
        out.append(
            f"| {lbl[v]} | {res[v]['1H']['ll']:.4f} | "
            f"{res[v]['1H']['calib']:.2f} | {res[v]['1H']['mae']:.2f} | "
            f"{res[v]['2H']['ll']:.4f} | {res[v]['2H']['calib']:.2f} | "
            f"{res[v]['2H']['mae']:.2f} |")
    out.append("")
    for h, lines in HALF_LINES.items():
        out.append(f"## Per line — {h} (lines {', '.join(str(x) for x in lines)})")
        out.append("")
        out.append("| Variant | Line | LogLoss | Pred Over% | Actual Over% |")
        out.append("|---|---|---|---|---|")
        for v in VARIANTS:
            for L in lines:
                s = stats(ev["acc"][v][h], L)
                out.append(f"| {lbl[v]} | {L} | {s['ll']:.4f} | "
                           f"{s['pred']:.1f} | {s['act']:.1f} |")
        out.append("")
    out.append("## By division — pooled log loss per half")
    out.append("")
    out.append("| Div | 1H product | 1H base (a) | Δ1H | 2H product | "
               "2H base (a) | Δ2H |")
    out.append("|---|---|---|---|---|---|---|")
    for d in TOP5:
        p1, b1 = div_res["product"]["1H"][d], div_res["base_share"]["1H"][d]
        p2, b2 = div_res["product"]["2H"][d], div_res["base_share"]["2H"][d]
        out.append(f"| {d} | {p1:.4f} | {b1:.4f} | {p1 - b1:+.4f} | "
                   f"{p2:.4f} | {b2:.4f} | {p2 - b2:+.4f} |")
    out.append("")
    out.append("## Gate verdict (pre-registered)")
    out.append("")
    out.append(f"- Product beats baseline (a) pooled log loss on BOTH "
               f"halves: **{'YES' if gate_ll else 'NO'}** "
               f"(1H {res['product']['1H']['ll']:.4f} vs "
               f"{res['base_share']['1H']['ll']:.4f}; 2H "
               f"{res['product']['2H']['ll']:.4f} vs "
               f"{res['base_share']['2H']['ll']:.4f}).")
    out.append(f"- Product not worse-calibrated than (a) by >0.5pp on "
               f"either half: **{'YES' if gate_calib else 'NO'}** "
               f"(1H {res['product']['1H']['calib']:.2f} vs "
               f"{res['base_share']['1H']['calib']:.2f}pp; 2H "
               f"{res['product']['2H']['calib']:.2f} vs "
               f"{res['base_share']['2H']['calib']:.2f}pp).")
    out.append(f"- **Verdict: {'PASS — build the halves product on top of production v5 totals' if passed else 'FAIL — do not build; production stays v5 total only'}.**")
    out.append("")
    out.append("## Method notes and caveats")
    out.append("")
    out.append("- The v5 total used here is the model MEMBER production "
               "writes as its expectation (0.5 * regression + 0.5 * BB "
               "shots-implied per team); the naive ensemble member "
               "enters only the FT continuity check, exactly as in "
               "production probabilities.")
    out.append("- The split is normalised per team, so product 1H + 2H "
               "expectations sum to the v5 total by construction; the "
               "halves are graded against halves actuals only — no "
               "claim is made here about improving the FT total (v6 "
               "already answered that: it does not).")
    out.append("- Halves are intrinsically noisier than full-time "
               "totals (roughly half the counts, plus HT-state "
               "variance); per-half log losses are not comparable to "
               "FT line log losses.")
    out.append("- Test-season halves-label coverage: all scored "
               "matches come from sot_halves_combined.csv; "
               f"{ev['n_nolabel']} top-5 test match(es) had no label "
               "and were skipped for half scoring.")
    out.append(f"- Script runtime: {runtime:.0f}s. No production code "
               "touched by this script; no odds anywhere.")

    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write("\n".join(out) + "\n")

    print(f"frozen: S={league_share:.4f} r_1H={r_half['1H']:.2f} "
          f"r_2H={r_half['2H']:.2f} (warm n={n_warm:,})")
    print(f"scored n={ev['n_scored']:,} (skipped {ev['n_nolabel']})")
    for v in VARIANTS:
        print(f"{v:11s} 1H ll={res[v]['1H']['ll']:.4f} "
              f"cal={res[v]['1H']['calib']:.2f}pp mae={res[v]['1H']['mae']:.2f} | "
              f"2H ll={res[v]['2H']['ll']:.4f} "
              f"cal={res[v]['2H']['calib']:.2f}pp mae={res[v]['2H']['mae']:.2f}")
    print(f"FT continuity LL@9.5: {ft['ll']:.4f}")
    print(f"verdict: {'PASS' if passed else 'FAIL'}")
    print(f"runtime: {runtime:.0f}s; wrote {OUT}")


if __name__ == "__main__":
    main()
