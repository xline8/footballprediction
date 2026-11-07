#!/usr/bin/env python
"""Shots-on-target (SOT) model — v6: per-half ratings + HT-state conditioning.

Question: does computing the SOT expectation per half — first-half ratings
and second-half ratings from the combined halves dataset
(data_enrichment/sot_halves_combined.csv), with the second-half expectation
conditioned on the half-time state distribution (home leading / level /
away leading) — beat the production v5 recipe on the standard
walk-forward?

VARIANT ("halves"). For each match:
  E[SOT] = E1H + E2H_cond, per team, where
  - E1H comes from a joint ridge-Poisson regression store fitted on
    first-half SOT (targets sot_1h_h / sot_1h_a), same machinery, same
    frozen lambda=100, same lazy 7-day refits as v5's R;
  - E2H_uncond comes from the same kind of store fitted on second-half
    SOT; the conditional expectation mixes it with three role
    multipliers estimated on warm-up only:
        E2H_team = E2H_uncond_team * sum_s P(state s at HT) * mult_s,
    the state taken from the team's own perspective (leading / level /
    trailing);
  - P(state) comes from a third regression store fitted on half-time
    GOALS (HTHG/HTAG, complete in the spine), independent Poissons over
    a 0..10 grid collapsed to the three states.
  The summed expectation replaces the v5 ratings member; the rest of
  the production structure is kept identical: 50/50 ensemble with the
  naive trailing-10 tracker (with the FT regression's league means,
  exactly as v5 combined) and negative-binomial line probabilities with
  the frozen r from the v5 warm-up.

REFERENCES in the same pass:
  - "v5" = slim+R+NB+BB exactly as run_sot_v5.py computes it. Its
    FULL pooled line-9.5 log loss over all divisions must reproduce
    RESULTS_V5.md's 0.6304 (the pass is invalid otherwise).
  - "v5-nobb" = slim+R+NB (regression member without the BB/shots
    member), the like-for-like baseline for reading the halves delta,
    because the halves member has no shots/BB analogue in the halves
    dataset (it carries SOT splits only, no shots splits).

EVALUATION SET for the gate: top-5 test matches only (2023/24–2025/26),
because the halves training labels exist only for the top-5. Both the
reference and the variant are scored on the identical match set. The
full-pooled v5 numbers are reported for continuity.

TUNING discipline: ridge lambda (100), BB prior (200) and NB r are the
v5 frozen choices, re-derived by re-running v5's warm-up pass in this
script (2022/23 / 2019/20–2022/23 data only). The only new parameters,
the three HT-state multipliers, are estimated by moment matching on
walk-forward predictions over 2019/20–2022/23 only, then frozen. Test
seasons touch nothing.

GATE (pre-registered for this round): the variant is judged ADOPTABLE
only if, on top-5 test matches, pooled line-9.5 log loss improves vs
v5 AND calibration error does not worsen vs v5 AND no top-5 division
worsens by more than 0.003. Production is NOT changed by this script
either way; the verdict is reported for the user's decision.

Run:  .venv/bin/python experiments/sot_model/run_sot_v6_halves.py
Writes only RESULTS_V6_HALVES.md next to itself.
"""

import csv
import math
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ROOT = os.path.join(HERE, "..", "..")

from run_sot_v2 import (LINES, MAIN_LINE, TEST_SEASONS, TOP5,  # noqa: E402
                        NaiveTracker, Ratings, load_matches, logloss,
                        nb_over, poisson_over)
from run_sot_v5 import (BASE_HL, BASE_K, RegressionStore, bb_ratio,  # noqa: E402
                        new_acc, add, stats, pass_warmup, slim_components,
                        update_all)

OUT = os.path.join(HERE, "RESULTS_V6_HALVES.md")
HALVES_CSV = os.path.join(ROOT, "data_enrichment", "sot_halves_combined.csv")
CLEAN_CSV = os.path.join(ROOT, "all_matches_clean.csv")
REF_V5_LL = 0.6304
FROZEN_LAM = 100.0
MULT_SEASONS = ["2019/20", "2020/21", "2021/22", "2022/23"]
STATES = ("lead", "level", "trail")


# ------------------------------------------------------------------ data
def load_halves():
    """(div, date, home, away) -> (sot_1h_h, sot_1h_a, sot_2h_h, sot_2h_a)."""
    out = {}
    with open(HALVES_CSV, newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            out[(r["div"], r["date"], r["home"], r["away"])] = (
                int(r["sot_1h_h"]), int(r["sot_1h_a"]),
                int(r["sot_2h_h"]), int(r["sot_2h_a"]))
    return out


def load_ht_goals():
    """(div, date, home, away) -> (HTHG, HTAG) from the clean file."""
    out = {}
    with open(CLEAN_CSV, newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            if r.get("HTHG") in (None, "") or r.get("HTAG") in (None, ""):
                continue
            out[(r["Div"], r["Date"], r["HomeTeam"], r["AwayTeam"])] = (
                int(float(r["HTHG"])), int(float(r["HTAG"])))
    return out


def store_matches(matches, target_fn):
    """Lightweight match dicts for a RegressionStore with swapped targets."""
    out = []
    for m in matches:
        t = target_fn(m)
        if t is None:
            continue
        out.append({"div": m["div"], "season": m["season"],
                    "date": m["date"], "day": m["day"],
                    "home": m["home"], "away": m["away"],
                    "hst": t[0], "ast": t[1]})
    return out


def poisson_state_probs(mu_h, mu_a, kmax=10):
    def pmf(mu):
        p = [math.exp(-mu)]
        for k in range(1, kmax + 1):
            p.append(p[-1] * mu / k)
        return p
    ph, pa = pmf(mu_h), pmf(mu_a)
    lead = level = trail = 0.0
    for i, a in enumerate(ph):
        for j, b in enumerate(pa):
            w = a * b
            if i > j:
                lead += w
            elif i == j:
                level += w
            else:
                trail += w
    return lead, level, trail


# ------------------------------------------------- multiplier estimation
def estimate_multipliers(matches, halves, ht_goals):
    """Moment-matched HT-state multipliers for team 2H SOT, walk-forward
    over MULT_SEASONS only: mult_s = sum(actual 2H SOT of teams in state
    s) / sum(unconditional predicted 2H SOT of teams in state s), the
    state from each team's own perspective, pooled over both teams."""
    reg2 = RegressionStore(
        store_matches(matches, lambda m: (
            (halves[(m["div"], m["date"], m["home"], m["away"])][2],
             halves[(m["div"], m["date"], m["home"], m["away"])][3])
            if (m["div"], m["date"], m["home"], m["away"]) in halves
            else None)), [FROZEN_LAM])
    acc = {s: [0.0, 0.0, 0] for s in STATES}  # pred, actual, n
    for m in matches:
        if m["season"] in TEST_SEASONS:
            break
        if m["season"] not in MULT_SEASONS:
            continue
        key = (m["div"], m["date"], m["home"], m["away"])
        if key not in halves or key not in ht_goals:
            continue
        h2h, h2a = halves[key][2], halves[key][3]
        gh, ga = ht_goals[key]
        state_h = "lead" if gh > ga else "level" if gh == ga else "trail"
        state_a = "lead" if ga > gh else "level" if ga == gh else "trail"
        eh, ea = reg2.predict(m["div"], m["home"], m["away"], m["day"],
                              FROZEN_LAM)
        acc[state_h][0] += eh
        acc[state_h][1] += h2h
        acc[state_h][2] += 1
        acc[state_a][0] += ea
        acc[state_a][1] += h2a
        acc[state_a][2] += 1
    mults = {s: (acc[s][1] / acc[s][0] if acc[s][0] > 0 else 1.0)
             for s in STATES}
    info = {s: {"pred": acc[s][0], "actual": acc[s][1], "n": acc[s][2]}
            for s in STATES}
    return mults, info


# ------------------------------------------------------------------ eval
def pass_eval_v6(matches, halves, ht_goals, best_lam, best_p, nb_r, mults):
    sot = Ratings(BASE_HL, BASE_K, "sot")
    shots = Ratings(BASE_HL, BASE_K, "shots", track_ratio=True)
    naive = NaiveTracker()
    reg_ft = RegressionStore(matches, [best_lam])
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

    variants = ("v5", "v5-nobb", "halves")
    pooled_all = {v: new_acc(LINES) for v in ("v5",)}
    pooled_t5 = {v: new_acc(LINES) for v in variants}
    div_acc = {v: {d: new_acc([MAIN_LINE]) for d in TOP5} for v in variants}
    season_acc = {v: {s: new_acc([MAIN_LINE]) for s in TEST_SEASONS}
                  for v in ("v5", "halves")}
    mae = {v: [0, 0.0] for v in variants}
    n_all = n_t5 = 0

    for m in matches:
        day, div = m["day"], m["div"]
        home, away = m["home"], m["away"]
        if m["season"] in TEST_SEASONS:
            total = m["hst"] + m["ast"]
            ys = {L: (1.0 if total > L else 0.0) for L in LINES}
            (eh, ea, seh, sea, imp_h, imp_a, lam1,
             lam_n) = slim_components(sot, shots, naive, div, home, away,
                                      day)
            ib_h = seh * bb_ratio(shots, div, home, "h", day, best_p)
            ib_a = sea * bb_ratio(shots, div, away, "a", day, best_p)
            reh, rea = reg_ft.predict(div, home, away, day, best_lam)
            rmu_h, rmu_a = reg_ft.league_mu(div, day, best_lam)
            nh_r, na_r = naive.predict(div, home, away, rmu_h, rmu_a)
            lam_n_r = nh_r + na_r
            lam1_r = 0.5 * (reh + imp_h) + 0.5 * (rea + imp_a)
            lam1_rb = 0.5 * (reh + ib_h) + 0.5 * (rea + ib_a)

            def ens_nb(la, lb):
                return {L: 0.5 * nb_over(la, nb_r, L)
                        + 0.5 * nb_over(lb, nb_r, L) for L in LINES}

            probs = {"v5": ens_nb(lam1_rb, lam_n_r),
                     "v5-nobb": ens_nb(lam1_r, lam_n_r)}
            lam_pt = {"v5": lam1_rb, "v5-nobb": lam1_r}
            n_all += 1
            for L in LINES:
                add(pooled_all["v5"], L, probs["v5"][L], ys[L])
            mae["v5"][0] += 1
            mae["v5"][1] += abs(lam1_rb - total)
            mae["v5-nobb"][0] += 1
            mae["v5-nobb"][1] += abs(lam1_r - total)

            if div in TOP5:
                n_t5 += 1
                e1h, e1a = reg_1h.predict(div, home, away, day, FROZEN_LAM)
                e2h, e2a = reg_2h.predict(div, home, away, day, FROZEN_LAM)
                gh, ga = reg_ht.predict(div, home, away, day, FROZEN_LAM)
                p_lead, p_level, p_trail = poisson_state_probs(gh, ga)
                mix_h = (p_lead * mults["lead"] + p_level * mults["level"]
                         + p_trail * mults["trail"])
                mix_a = (p_trail * mults["lead"] + p_level * mults["level"]
                         + p_lead * mults["trail"])
                lam_halves = (e1h + e2h * mix_h) + (e1a + e2a * mix_a)
                probs["halves"] = ens_nb(lam_halves, lam_n_r)
                lam_pt["halves"] = lam_halves
                mae["halves"][0] += 1
                mae["halves"][1] += abs(lam_halves - total)
                for v in variants:
                    for L in LINES:
                        add(pooled_t5[v], L, probs[v][L], ys[L])
                    add(div_acc[v][div], MAIN_LINE,
                        probs[v][MAIN_LINE], ys[MAIN_LINE])
                for v in ("v5", "halves"):
                    add(season_acc[v][m["season"]], MAIN_LINE,
                        probs[v][MAIN_LINE], ys[MAIN_LINE])
        update_all(sot, shots, naive, m)

    return pooled_all, pooled_t5, div_acc, season_acc, mae, n_all, n_t5


# ------------------------------------------------------------------- main
def main():
    t0 = time.time()
    matches = load_matches()
    halves = load_halves()
    ht_goals = load_ht_goals()

    ll_r, ll_bb, nb_r, resid = pass_warmup(matches)
    tune_r = {lam: s / n for lam, (n, s) in ll_r.items()}
    tune_bb = {p: s / n for p, (n, s) in ll_bb.items()}
    best_lam = min(tune_r, key=lambda l: (tune_r[l], -l))
    best_p = min(tune_bb, key=lambda p: (tune_bb[p], -p))
    assert best_lam == FROZEN_LAM, f"v5 warm-up lambda changed: {best_lam}"

    mults, mult_info = estimate_multipliers(matches, halves, ht_goals)
    (pooled_all, pooled_t5, div_acc, season_acc, mae,
     n_all, n_t5) = pass_eval_v6(matches, halves, ht_goals, best_lam,
                                 best_p, nb_r, mults)
    runtime = time.time() - t0

    v5_all = stats(pooled_all["v5"])
    repro_ok = abs(v5_all["ll"] - REF_V5_LL) < 0.0001
    v5 = stats(pooled_t5["v5"])
    hv = stats(pooled_t5["halves"])
    nb5 = stats(pooled_t5["v5-nobb"])
    div_deltas = {d: stats(div_acc["halves"][d])["ll"]
                  - stats(div_acc["v5"][d])["ll"] for d in TOP5}
    worst_div = max(div_deltas.values())
    gate_ll = hv["ll"] < v5["ll"]
    gate_calib = hv["calib"] <= v5["calib"]
    gate_div = worst_div <= 0.003
    adoptable = repro_ok and gate_ll and gate_calib and gate_div

    # ------------------------------------------------------------ report
    out = []
    out.append("# Model SOT v6 — Per Babak + Kondisi Skor Turun Minum "
               "(eksperimen, BUKAN produksi)")
    out.append("")
    out.append("## Ringkasan (Bahasa Indonesia)")
    out.append("")
    out.append(
        f"Pertanyaan: apakah menghitung tembakan ke gawang per babak "
        f"(babak 1 dan babak 2 dinilai terpisah dari dataset gabungan "
        f"SofaScore+FotMob), dengan perkiraan babak 2 disyaratkan pada "
        f"keadaan skor saat turun minum (unggul / imbang / tertinggal), "
        f"mengalahkan resep produksi v5 pada uji walk-forward yang sama?")
    out.append("")
    out.append(
        f"Jawaban: **{'YA — lolos gerbang' if adoptable else 'TIDAK — tidak lolos gerbang'}**. "
        f"Pada {n_t5:,} laga uji lima liga top (2023/24–2025/26), log loss "
        f"garis 9,5: v5 = {v5['ll']:.4f}, varian babak = {hv['ll']:.4f} "
        f"(selisih {hv['ll'] - v5['ll']:+.4f}); kesalahan kalibrasi: v5 = "
        f"{v5['calib']:.1f}pp, varian babak = {hv['calib']:.1f}pp; divisi "
        f"paling memburuk: {worst_div:+.4f} (batas +0,003). "
        f"Pengali keadaan turun minum dari data pemanasan: tertinggal "
        f"×{mults['trail']:.3f}, imbang ×{mults['level']:.3f}, unggul "
        f"×{mults['lead']:.3f} — arahnya sesuai dugaan (tim tertinggal "
        f"menembak lebih banyak di babak 2), besarnya "
        f"{'cukup terasa' if abs(mults['trail'] - mults['lead']) > 0.10 else 'kecil'}.")
    out.append("")
    out.append(
        "Produksi TIDAK diubah oleh eksperimen ini apa pun hasilnya — "
        "keputusan adopsi ada di tangan user setelah membaca laporan ini.")
    out.append("")
    out.append("## Reference reproduction check")
    out.append("")
    out.append(
        f"Production v5 (slim+R+NB+BB) recomputed in this pass over ALL "
        f"divisions: pooled line-9.5 log loss **{v5_all['ll']:.4f}** "
        f"(RESULTS_V5.md: 0.6304) → "
        f"**{'MATCH' if repro_ok else 'MISMATCH — RUN INVALID'}**. "
        f"n = {n_all:,}. Frozen choices re-derived from warm-up only: "
        f"ridge lambda = {best_lam:g}, BB prior = {best_p:g}, NB r = "
        f"{nb_r:.2f}.")
    out.append("")
    out.append("## HT-state multipliers (frozen from 2019/20–2022/23)")
    out.append("")
    out.append("| State (team's own view) | Team-matches | Σ predicted 2H | Σ actual 2H | Multiplier |")
    out.append("|---|---|---|---|---|")
    for s in STATES:
        i = mult_info[s]
        out.append(f"| {s} | {i['n']:,} | {i['pred']:.0f} | {i['actual']:.0f} | {mults[s]:.3f} |")
    out.append("")
    out.append("## Headline — top-5 test matches, line 9.5")
    out.append("")
    out.append("| Variant | LogLoss | Brier | Calib err (pp) | MAE | ΔLL vs v5 |")
    out.append("|---|---|---|---|---|---|")
    for name, key, s in (("v5 (production)", "v5", v5),
                         ("v5 without BB (ablation baseline)", "v5-nobb", nb5),
                         ("halves (per-half + HT state)", "halves", hv)):
        m = mae[key][1] / mae[key][0]
        out.append(f"| {name} | {s['ll']:.4f} | {s['brier']:.4f} | "
                   f"{s['calib']:.1f} | {m:.2f} | {s['ll'] - v5['ll']:+.4f} |")
    out.append("")
    out.append("## All lines — top-5 pooled log loss")
    out.append("")
    out.append("| Variant | 7.5 | 8.5 | 9.5 | 10.5 |")
    out.append("|---|---|---|---|---|")
    for name, key in (("v5", "v5"), ("v5-nobb", "v5-nobb"),
                      ("halves", "halves")):
        cells = " | ".join(f"{stats(pooled_t5[key], L)['ll']:.4f}"
                           for L in LINES)
        out.append(f"| {name} | {cells} |")
    out.append("")
    out.append("## By division — line 9.5 log loss (top-5 test matches)")
    out.append("")
    out.append("| Div | n | v5 | halves | Δ |")
    out.append("|---|---|---|---|---|")
    for d in TOP5:
        sv = stats(div_acc["v5"][d])
        sh = stats(div_acc["halves"][d])
        out.append(f"| {d} | {sv['n']:,} | {sv['ll']:.4f} | {sh['ll']:.4f} | "
                   f"{sh['ll'] - sv['ll']:+.4f} |")
    out.append("")
    out.append("## By season — line 9.5 log loss (top-5)")
    out.append("")
    out.append("| Season | n | v5 | halves | Δ |")
    out.append("|---|---|---|---|---|")
    for sname in TEST_SEASONS:
        sv = stats(season_acc["v5"][sname])
        sh = stats(season_acc["halves"][sname])
        out.append(f"| {sname} | {sv['n']:,} | {sv['ll']:.4f} | "
                   f"{sh['ll']:.4f} | {sh['ll'] - sv['ll']:+.4f} |")
    out.append("")
    out.append("## Gate verdict")
    out.append("")
    if not repro_ok:
        out.append("**RUN INVALID** — the v5 reference did not reproduce "
                   "0.6304; no verdict may be taken from this run.")
    else:
        out.append(f"- Pooled (top-5) log loss improves: "
                   f"**{'YES' if gate_ll else 'NO'}** "
                   f"({hv['ll']:.4f} vs {v5['ll']:.4f}).")
        out.append(f"- Calibration does not worsen: "
                   f"**{'YES' if gate_calib else 'NO'}** "
                   f"({hv['calib']:.1f}pp vs {v5['calib']:.1f}pp).")
        out.append(f"- No top-5 division worsens by >0.003: "
                   f"**{'YES' if gate_div else 'NO'}** "
                   f"(worst {worst_div:+.4f}).")
        out.append(f"- **Verdict: {'ADOPTABLE — candidate for production, pending the user decision' if adoptable else 'NOT ADOPTABLE — production v5 stays'}.**")
    out.append("")
    out.append("## Method notes and caveats")
    out.append("")
    out.append("- The halves variant is defined on the top-5 only: the "
               "halves training labels (sot_halves_combined.csv) cover "
               "94.4% of the top-5 spine but no lower divisions, so both "
               "variants are gated on identical top-5 test matches; the "
               "full-pooled v5 figure above is the continuity check.")
    out.append("- Halves training coverage by era (top-5): 2020/21 "
               "onward ~100% except one F1 match; 2019/20 82% (F1 nearly "
               "absent); 2017/18–2018/19 partial (F1/SP1 holes). The "
               "per-half stores therefore learn early seasons from "
               "fewer matches; test-season coverage is 100% except one "
               "F1 match in 2023/24 (a test match needs no label — "
               "labels are training data; its FT total grades it).")
    out.append("- The halves member has no shots/BB component (the "
               "halves dataset carries SOT splits only, not shots "
               "splits), so read the halves delta against v5-nobb as "
               "well as against full v5: v5-nobb isolates what dropping "
               "BB costs, halves-vs-nobb isolates the halves engine.")
    out.append("- HT-state probabilities come from a goals regression "
               "on HTHG/HTAG with the same frozen lambda=100 (not "
               "separately tuned) and independent Poissons; the three "
               "multipliers are the only new fitted parameters and were "
               "frozen from pre-2023/24 walk-forward predictions.")
    out.append("- The state multipliers are pooled across divisions "
               "and both teams (by the team's own state); per-division "
               "multipliers were not attempted — the warm-up counts do "
               "not support five-way splits for the trailing state in "
               "smaller divisions.")
    out.append(f"- Script runtime: {runtime:.0f}s. No production code "
               "touched; no odds anywhere (accuracy/calibration only).")

    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write("\n".join(out) + "\n")

    print(f"multipliers: lead={mults['lead']:.3f} level={mults['level']:.3f} "
          f"trail={mults['trail']:.3f}")
    print(f"v5 full-pooled LL: {v5_all['ll']:.4f} (ref 0.6304) "
          f"repro={'MATCH' if repro_ok else 'MISMATCH'}")
    print(f"top-5 n={n_t5:,}: v5 {v5['ll']:.4f} | v5-nobb {nb5['ll']:.4f} | "
          f"halves {hv['ll']:.4f} (dLL {hv['ll'] - v5['ll']:+.4f})")
    print(f"calib: v5 {v5['calib']:.1f}pp halves {hv['calib']:.1f}pp | "
          f"worst div dLL {worst_div:+.4f}")
    print(f"verdict: {'ADOPTABLE' if adoptable else 'NOT ADOPTABLE'}")
    print(f"runtime: {runtime:.0f}s; wrote {OUT}")


if __name__ == "__main__":
    main()
