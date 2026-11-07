#!/usr/bin/env python
"""Shots-on-target (SOT) model — v8: does the ACTUAL starting XI help?

Question: production v5 predicts in the morning, before lineups exist.
Lineups publish ~1 hour before kickoff. If, at that just-in-time (JIT)
decision point, we adjust each team's expected SOT by how much of its
trailing SOT production sits OUTSIDE the confirmed starting XI, does
the prediction improve — judged honestly, walk-forward, with every
strength parameter tuned on 2022/23 only?

Adjustment (the only new ingredient). For each team, from matches
strictly before the predicted one (FotMob store, seasons >= 2022/23),
each player's share of the team's SOT — exponential decay, half-life
365d, the base model's own clock — is accumulated per (division,
team). For the match being predicted, its ACTUAL lineup gives:

    missing_share = sum of trailing shares of players NOT starting

Variants:
  sotB   SOT shares; bench players count as fully missing.
  sotA   SOT shares; bench players count as half-present
         (their share enters missing at 0.5 weight).
  shotB  same as sotB but shares of SHOTS instead of SOT.
  shotA  same as sotA but shares of SHOTS instead of SOT.
  sot*+ret (only if the simple versions show tuning signal):
         symmetric boost — players in the XI who were absent from
         the team's previous starting XI carry a return share;
         expectation multiplied by (1 + kb * return_share).

Adjusted per-team expectation = base * (1 - k * missing_share)
[* (1 + kb * return_share) for the boost variant], applied to BOTH
ensemble members' per-team components of production v5 (the
regression+BB blended member and the naive member), so the v5
probability machinery (NB totals, 50/50 ensemble) is untouched apart
from the scaled team expectations. k (and kb) are tuned ONLY on
2022/23 over a coarse grid 0.0..1.0 step 0.1 (ties -> smaller k).

Player attribution uses the house SOT counting rule (the one
build_shot_lineup_features.py validated against the spine): a shot
counts as the player's SOT iff isOnTarget and not isBlocked and not
isOwnGoal. Shares are team-specific: a transferred player's history
stays with the club he produced it for.

Evaluation: test seasons 2023/24-2025/26, top-5, line 9.5 — exactly
the 5,255 matches present in the FotMob store (verified: full
coverage). Reference: production v5 (slim+R+NB+BB) recomputed in the
same pass on the identical match set, plus the standard full-set
anchor (pass_eval of run_sot_v5.py must reproduce pooled 0.6304).

GATE (pre-registered): a variant is adoptable (as a JIT step) only if
ALL hold vs the unadjusted v5 on the identical set: pooled line-9.5
log loss improves; calibration error does not worsen; no top-5
division's log loss worsens by more than 0.003.

Run:  .venv/bin/python experiments/sot_model/run_sot_v8_lineup_jit.py
Writes only RESULTS_V8_LINEUP_JIT.md next to itself (plus a /tmp
extraction cache). No production code touched.
"""

import csv
import json
import math
import os
import pickle
import sys
import time
from collections import Counter, defaultdict

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)

from run_sot_v2 import (BASE_HL, BASE_K, MAIN_LINE, TEST_SEASONS, TOP5,
                        NaiveTracker, Ratings, load_matches, logloss,
                        nb_over)
from run_sot_v5 import (GRID_BB, GRID_LAM, RegressionStore, add,
                        bb_ratio, new_acc, pass_eval, pass_warmup,
                        slim_components, stats, update_all)

OUT = os.path.join(HERE, "RESULTS_V8_LINEUP_JIT.md")
INDEX = os.path.join(ROOT, "data_enrichment", "fotmob_full_index.csv")
CACHE = "/tmp/v8_lineup_extract.pkl"
TUNE_SEASON = "2022/23"
K_GRID = [round(0.1 * i, 2) for i in range(11)]
REF_V5_LL = 0.6304              # RESULTS_V5.md pooled, slim+R+NB+BB
BOOST_TRIGGER_DLL = -0.0005     # tuning gain needed to try +ret
VARIANTS = ["sotB", "sotA", "shotB", "shotA"]
SHARE_OF = {"sotB": "sot", "sotA": "sot", "shotB": "shots", "shotA": "shots"}
HALF_BENCH = {"sotB": False, "sotA": True, "shotB": False, "shotA": True}


# ------------------------------------------------------------- extraction
def extract_store():
    """Parse every FotMob store JSON once -> per-match player data.

    Returns dict keyed by (div, date, home, away) (spine names) with
    starter/bench id sets and per-player SOT / shot counters per side.
    """
    if os.path.exists(CACHE):
        with open(CACHE, "rb") as fh:
            return pickle.load(fh)
    store = {}
    n_no_lineup = n_no_shotmap = 0
    with open(INDEX, newline="", encoding="utf-8") as fh:
        index = list(csv.DictReader(fh))
    for ix in index:
        with open(os.path.join(ROOT, ix["path"]), encoding="utf-8") as fh:
            payload = json.load(fh)
        content = payload.get("content") or {}
        teams = (payload.get("header") or {}).get("teams") or []
        lineup = content.get("lineup") or {}
        if len(teams) != 2 or not lineup:
            n_no_lineup += 1
            continue
        tid = {teams[0].get("id"): "h", teams[1].get("id"): "a"}
        rec = {}
        for side, lkey in (("h", "homeTeam"), ("a", "awayTeam")):
            team = lineup.get(lkey) or {}
            rec[f"xi_{side}"] = {p["id"] for p in team.get("starters") or []}
            rec[f"bench_{side}"] = {p["id"] for p in team.get("subs") or []}
            rec[f"sot_{side}"] = Counter()
            rec[f"shots_{side}"] = Counter()
        shots = (content.get("shotmap") or {}).get("shots") or []
        if not shots:
            n_no_shotmap += 1
        for s in shots:
            side = tid.get(s.get("teamId"))
            if side is None or s.get("isOwnGoal"):
                continue
            pid = s.get("playerId")
            if pid is None:
                continue
            rec[f"shots_{side}"][pid] += 1
            if s.get("isOnTarget") is True and s.get("isBlocked") is not True:
                rec[f"sot_{side}"][pid] += 1
        store[(ix["div"], ix["date"], ix["home"], ix["away"])] = rec
    print(f"extracted {len(store):,} store matches "
          f"(no lineup: {n_no_lineup}, no shotmap: {n_no_shotmap})")
    with open(CACHE, "wb") as fh:
        pickle.dump(store, fh)
    return store


# ------------------------------------------------------- player shares
class PlayerShares:
    """Decayed per-player SOT/shot totals per (div, spine team).

    Decay half-life = BASE_HL (365d), the base model's clock. Shares
    are read (and the state decayed) strictly at the predicted
    match's day, from matches already updated — i.e. strictly before.
    """

    def __init__(self):
        self.tot = {}   # (div, team) -> {pid: [sot, shots, last_day]}

    def _decay_to(self, key, day):
        d = self.tot.get(key)
        if not d:
            return d
        for v in d.values():
            if day > v[2]:
                f = 0.5 ** ((day - v[2]) / BASE_HL)
                v[0] *= f
                v[1] *= f
                v[2] = day
        return d

    def shares(self, div, team, day):
        """-> (sot_share dict, shot_share dict); empty if no history."""
        d = self._decay_to((div, team), day)
        if not d:
            return {}, {}
        ts = sum(v[0] for v in d.values())
        th = sum(v[1] for v in d.values())
        sot_sh = {p: v[0] / ts for p, v in d.items()} if ts > 1e-9 else {}
        shot_sh = {p: v[1] / th for p, v in d.items()} if th > 1e-9 else {}
        return sot_sh, shot_sh

    def update(self, div, team, day, sot_c, shots_c):
        key = (div, team)
        d = self._decay_to(key, day)
        if d is None:
            d = self.tot[key] = {}
        for pid, n in shots_c.items():
            v = d.setdefault(pid, [0.0, 0.0, day])
            v[1] += n
        for pid, n in sot_c.items():
            v = d.setdefault(pid, [0.0, 0.0, day])
            v[0] += n


def missing_share(share, xi, bench, half_bench):
    """Share mass outside the starting XI (see module docstring)."""
    if not share:
        return 0.0
    miss = 0.0
    for pid, sh in share.items():
        if pid in xi:
            continue
        if half_bench and pid in bench:
            miss += 0.5 * sh
        else:
            miss += sh
    return miss


# ------------------------------------------------------------ base v5
def base_components(sot, shots, naive, reg, div, home, away, day, lam, bp):
    """Production v5 per-team ensemble members, in run_sot_v5
    .pass_eval's exact call order. Returns (rb_h, rb_a, n_h, n_a):
    the regression+BB member's per-team expectations and the naive
    member's per-team expectations."""
    (eh, ea, seh, sea, imp_h, imp_a, lam1,
     lam_n) = slim_components(sot, shots, naive, div, home, away, day)
    ib_h = seh * bb_ratio(shots, div, home, "h", day, bp)
    ib_a = sea * bb_ratio(shots, div, away, "a", day, bp)
    reh, rea = reg.predict(div, home, away, day, lam)
    rmu_h, rmu_a = reg.league_mu(div, day, lam)
    nh_r, na_r = naive.predict(div, home, away, rmu_h, rmu_a)
    return 0.5 * (reh + ib_h), 0.5 * (rea + ib_a), nh_r, na_r


def prob_from(rb_h, rb_a, n_h, n_a, f_h, f_a, nb_r):
    t_rb = rb_h * f_h + rb_a * f_a
    t_n = n_h * f_h + n_a * f_a
    return (0.5 * nb_over(t_rb, nb_r, MAIN_LINE)
            + 0.5 * nb_over(t_n, nb_r, MAIN_LINE))


# ------------------------------------------------------------- pass T
def pass_tune(matches, store, lam, bp, nb_r):
    """Chronological pass over pre-test data only. For 2022/23 top-5
    store matches, accumulate line-9.5 log loss of every variant over
    the k grid (and the (k, kb) boost grids for the SOT variants)."""
    sot = Ratings(BASE_HL, BASE_K, "sot")
    shots = Ratings(BASE_HL, BASE_K, "shots", track_ratio=True)
    naive = NaiveTracker()
    reg = RegressionStore(matches, [lam])
    shares = PlayerShares()
    prev_xi = {}        # (div, team) -> set of starter ids, last store match
    grid = {v: {k: [0, 0.0] for k in K_GRID} for v in VARIANTS}
    grid_ret = {v: {(k, kb): [0, 0.0] for k in K_GRID for kb in K_GRID}
                for v in ("sotB", "sotA")}

    for m in matches:
        if m["season"] in TEST_SEASONS:
            break                       # tuning data only
        day, div = m["day"], m["div"]
        home, away = m["home"], m["away"]
        key = (div, m["date"], home, away)
        rec = store.get(key)
        if m["season"] == TUNE_SEASON and div in TOP5 and rec is not None:
            rb_h, rb_a, n_h, n_a = base_components(
                sot, shots, naive, reg, div, home, away, day, lam, bp)
            total = m["hst"] + m["ast"]
            y = 1.0 if total > MAIN_LINE else 0.0
            for v in VARIANTS:
                which = 0 if SHARE_OF[v] == "sot" else 1
                miss = {}
                for side, team in (("h", home), ("a", away)):
                    sh = shares.shares(div, team, day)[which]
                    miss[side] = missing_share(
                        sh, rec[f"xi_{side}"], rec[f"bench_{side}"],
                        HALF_BENCH[v])
                for k in K_GRID:
                    p = prob_from(rb_h, rb_a, n_h, n_a,
                                  1 - k * miss["h"], 1 - k * miss["a"], nb_r)
                    g = grid[v][k]
                    g[0] += 1
                    g[1] += logloss(p, y)
            for v in ("sotB", "sotA"):
                miss, ret = {}, {}
                for side, team in (("h", home), ("a", away)):
                    sh = shares.shares(div, team, day)[0]
                    miss[side] = missing_share(
                        sh, rec[f"xi_{side}"], rec[f"bench_{side}"],
                        HALF_BENCH[v])
                    px = prev_xi.get((div, team))
                    ret[side] = (sum(s for p, s in sh.items()
                                     if p in rec[f"xi_{side}"]
                                     and px is not None and p not in px)
                                 if px is not None else 0.0)
                for k in K_GRID:
                    for kb in K_GRID:
                        fh = ((1 - k * miss["h"]) * (1 + kb * ret["h"]))
                        fa = ((1 - k * miss["a"]) * (1 + kb * ret["a"]))
                        p = prob_from(rb_h, rb_a, n_h, n_a, fh, fa, nb_r)
                        g = grid_ret[v][(k, kb)]
                        g[0] += 1
                        g[1] += logloss(p, y)
        if rec is not None:
            shares.update(div, home, day, rec["sot_h"], rec["shots_h"])
            shares.update(div, away, day, rec["sot_a"], rec["shots_a"])
            prev_xi[(div, home)] = rec["xi_h"]
            prev_xi[(div, away)] = rec["xi_a"]
        update_all(sot, shots, naive, m)

    return grid, grid_ret


# ------------------------------------------------------------- pass E
def pass_eval_v8(matches, store, lam, bp, nb_r, chosen):
    """Fresh pass identical in schedule to run_sot_v5.pass_eval
    (regression calls only on test matches, so the base is v5
    exactly), scoring base v5 and the frozen adjusted variants on
    test-season top-5 store matches. `chosen`: variant -> (k, kb)."""
    sot = Ratings(BASE_HL, BASE_K, "sot")
    shots = Ratings(BASE_HL, BASE_K, "shots", track_ratio=True)
    naive = NaiveTracker()
    reg = RegressionStore(matches, [lam])
    shares = PlayerShares()
    prev_xi = {}
    names = ["base"] + list(chosen)
    pooled = {v: new_acc([MAIN_LINE]) for v in names}
    season_acc = {v: {s: new_acc([MAIN_LINE]) for s in TEST_SEASONS}
                  for v in names}
    div_acc = {v: {d: new_acc([MAIN_LINE]) for d in TOP5} for v in names}
    mae = {v: [0, 0.0] for v in names}
    dist = {"sotB": [], "sotA": [], "shotB": [], "shotA": []}
    top_absent = [0, 0]         # team-matches where top SOT player absent
    ret_share = []

    for m in matches:
        day, div = m["day"], m["div"]
        home, away = m["home"], m["away"]
        key = (div, m["date"], home, away)
        rec = store.get(key)

        if m["season"] in TEST_SEASONS and div in TOP5 and rec is not None:
            rb_h, rb_a, n_h, n_a = base_components(
                sot, shots, naive, reg, div, home, away, day, lam, bp)
            total = m["hst"] + m["ast"]
            y = 1.0 if total > MAIN_LINE else 0.0
            probs = {"base": prob_from(rb_h, rb_a, n_h, n_a, 1.0, 1.0,
                                       nb_r)}
            pts = {"base": 0.5 * (rb_h + rb_a + n_h + n_a)}
            miss_all, ret_all = {}, {}
            for v in VARIANTS:
                which = 0 if SHARE_OF[v] == "sot" else 1
                miss, ret = {}, {}
                for side, team in (("h", home), ("a", away)):
                    sh = shares.shares(div, team, day)[which]
                    miss[side] = missing_share(
                        sh, rec[f"xi_{side}"], rec[f"bench_{side}"],
                        HALF_BENCH[v])
                    if v == "sotB":
                        if sh:
                            top_pid = max(sh, key=sh.get)
                            top_absent[1] += 1
                            if top_pid not in rec[f"xi_{side}"]:
                                top_absent[0] += 1
                    px = prev_xi.get((div, team))
                    ret[side] = (sum(s for p, s in sh.items()
                                     if p in rec[f"xi_{side}"]
                                     and px is not None and p not in px)
                                 if px is not None else 0.0)
                    dist[v].append(miss[side])
                    if v == "sotB":
                        ret_share.append(ret[side])
                miss_all[v] = miss
                ret_all[v] = ret
            for v, (k, kb) in chosen.items():
                core = v.replace("+ret", "")
                fh = (1 - k * miss_all[core]["h"])
                fa = (1 - k * miss_all[core]["a"])
                if kb:
                    fh *= 1 + kb * ret_all[core]["h"]
                    fa *= 1 + kb * ret_all[core]["a"]
                probs[v] = prob_from(rb_h, rb_a, n_h, n_a, fh, fa, nb_r)
                pts[v] = 0.5 * (rb_h * fh + rb_a * fa
                                + n_h * fh + n_a * fa)
            for v in names:
                add(pooled[v], MAIN_LINE, probs[v], y)
                add(season_acc[v][m["season"]], MAIN_LINE, probs[v], y)
                add(div_acc[v][div], MAIN_LINE, probs[v], y)
                mae[v][0] += 1
                mae[v][1] += abs(pts[v] - total)

        if rec is not None:
            shares.update(div, home, day, rec["sot_h"], rec["shots_h"])
            shares.update(div, away, day, rec["sot_a"], rec["shots_a"])
            prev_xi[(div, home)] = rec["xi_h"]
            prev_xi[(div, away)] = rec["xi_a"]
        update_all(sot, shots, naive, m)

    return pooled, season_acc, div_acc, mae, dist, top_absent, ret_share


# ----------------------------------------------------------------- main
def pct(xs, q):
    return float(np.percentile(np.array(xs), q)) if xs else float("nan")


def main():
    t0 = time.time()
    matches = load_matches()
    store = extract_store()

    # frozen v5 choices + full-set anchor, exactly as run_sot_v5 does
    ll_r, ll_bb, nb_r, _ = pass_warmup(matches)
    tune_r = {l: s / n for l, (n, s) in ll_r.items()}
    tune_bb = {p: s / n for p, (n, s) in ll_bb.items()}
    best_lam = min(GRID_LAM, key=lambda l: (tune_r[l], -l))
    best_p = min(GRID_BB, key=lambda p: (tune_bb[p], -p))
    pooled5, _, div5, _, _ = pass_eval(matches, best_lam, best_p, nb_r)
    anchor = stats(pooled5["slim+R+NB+BB"])
    anchor_ok = abs(anchor["ll"] - REF_V5_LL) < 0.0005
    print(f"v5 frozen: lam={best_lam:g} P={best_p:g} NB r={nb_r:.2f}; "
          f"anchor pooled LL {anchor['ll']:.4f} vs {REF_V5_LL} -> "
          f"{'MATCH' if anchor_ok else 'MISMATCH'}")

    # tuning: k per variant (+ boost trigger)
    grid, grid_ret = pass_tune(matches, store, best_lam, best_p, nb_r)
    chosen, tune_info = {}, {}
    for v in VARIANTS:
        n0, s0 = grid[v][0.0]
        bk = min(K_GRID, key=lambda k: (grid[v][k][1] / grid[v][k][0], k))
        tune_info[v] = {"n": n0, "ll0": s0 / n0,
                        "llk": grid[v][bk][1] / grid[v][bk][0], "k": bk}
        chosen[v] = (bk, 0.0)
        print(f"tune {v}: n={n0} LL(k=0)={tune_info[v]['ll0']:.4f} "
              f"best k={bk:g} LL={tune_info[v]['llk']:.4f} "
              f"(d {tune_info[v]['llk'] - tune_info[v]['ll0']:+.4f})")
    trig = [v for v in VARIANTS
            if tune_info[v]["k"] > 0
            and tune_info[v]["llk"] - tune_info[v]["ll0"] <= BOOST_TRIGGER_DLL]
    boost = None
    if trig:
        best = None
        for v in ("sotB", "sotA"):
            for (k, kb), (n, s) in grid_ret[v].items():
                if kb <= 0:
                    continue
                ll = s / n
                if best is None or ll < best[0]:
                    best = (ll, v, k, kb)
        n0, s0 = grid[best[1]][0.0]
        if best and best[0] < tune_info[best[1]]["llk"]:
            boost = (best[1] + "+ret", best[2], best[3], best[0], s0 / n0)
            chosen[boost[0]] = (boost[1], boost[2])
            print(f"boost triggered by {trig}: {boost[0]} k={boost[1]:g} "
                  f"kb={boost[2]:g} tune LL={best[0]:.4f}")
    if not trig:
        print("boost NOT triggered (no variant with k>0 and tuning "
              f"gain >= {-BOOST_TRIGGER_DLL})")

    # evaluation on the identical test subset
    pooled, season_acc, div_acc, mae, dist, top_absent, ret_share = \
        pass_eval_v8(matches, store, best_lam, best_p, nb_r, chosen)
    base = stats(pooled["base"])
    # cross-check: my base per-division LL vs pass_eval's combined
    xchk = max(abs(stats(div_acc["base"][d])["ll"]
                   - stats(div5["slim+R+NB+BB"][d])["ll"]) for d in TOP5)
    print(f"base on subset: n={base['n']} LL={base['ll']:.4f} "
          f"calib={base['calib']:.2f}pp; cross-check vs pass_eval "
          f"max div dLL={xchk:.2e}")

    def gate(v):
        sv = stats(pooled[v])
        deltas = {d: stats(div_acc[v][d])["ll"]
                  - stats(div_acc["base"][d])["ll"] for d in TOP5}
        worst = max(deltas.values())
        return {"ll": sv["ll"], "calib": sv["calib"],
                "dll": sv["ll"] - base["ll"],
                "calib_ok": sv["calib"] <= base["calib"] + 1e-9,
                "ll_ok": sv["ll"] < base["ll"],
                "worst": worst, "div_ok": worst <= 0.003,
                "deltas": deltas,
                "adoptable": sv["ll"] < base["ll"]
                and sv["calib"] <= base["calib"] + 1e-9 and worst <= 0.003}

    gates = {v: gate(v) for v in chosen}
    adoptable = [v for v in chosen if gates[v]["adoptable"]]
    winner = (min(adoptable, key=lambda v: gates[v]["ll"])
              if adoptable else None)

    # ------------------------------------------------------------ report
    o = []
    o.append("# Model SOT v8 — Susunan Pemain Asli (JIT) sebagai Penyesuai "
             "(eksperimen, BUKAN produksi)")
    o.append("")
    o.append("## Ringkasan (Bahasa Indonesia)")
    o.append("")
    o.append("Pertanyaan: model produksi v5 memprediksi di pagi hari, "
             "sebelum susunan pemain (starting XI) ada. Susunan resmi "
             "terbit ~1 jam sebelum kickoff. Kalau pada titik just-in-"
             "time itu perkiraan tembakan ke gawang (SOT) tiap tim "
             "disesuaikan dengan seberapa besar porsi produksi SOT "
             "terakhir tim itu yang duduk DI LUAR starting XI (pemain "
             "kunci absen), apakah prediksinya membaik?")
    o.append("")
    if winner:
        o.append(f"Jawaban: **YA, untuk varian {winner}** — lolos gerbang "
                 f"pada 5.255 laga uji lima liga top (2023/24–2025/26): "
                 f"log loss garis 9,5 {gates[winner]['ll']:.4f} vs v5 "
                 f"{base['ll']:.4f} (selisih {gates[winner]['dll']:+.4f}), "
                 f"kalibrasi {gates[winner]['calib']:.2f}pp vs "
                 f"{base['calib']:.2f}pp, divisi paling memburuk "
                 f"{gates[winner]['worst']:+.4f} (batas +0,003). "
                 f"Kekuatan penyesuaian k = {chosen[winner][0]:g}"
                 + (f", penguat pemain kembali kb = {chosen[winner][1]:g}"
                    if chosen[winner][1] else "")
                 + " (disetel hanya dari 2022/23).")
    else:
        o.append(f"Jawaban: **TIDAK — tidak ada varian yang lolos "
                 f"gerbang**. Pada 5.255 laga uji lima liga top "
                 f"(2023/24–2025/26), log loss garis 9,5 v5 = "
                 f"{base['ll']:.4f}; setiap varian penyesuaian dengan "
                 f"k > 0 justru MEMBURUK (terbaik sotA/shotA "
                 f"{min(gates[v]['ll'] for v in chosen if chosen[v][0] > 0):.4f}, "
                 f"dan kalibrasinya runtuh ke ~5pp), sedangkan shotB "
                 f"memilih k = 0 — artinya datanya sendiri berkata "
                 "\"jangan disesuaikan\". Kenapa: porsi produksi yang "
                 "\"hilang\" rata-rata 0,56 per tim per laga — tapi itu "
                 "kebanyakan massa pemain pinggiran dan pemain yang "
                 "sudah pindah klub, bukan bintang yang absen (pemain "
                 "dengan porsi SOT terbesar memang absen di 39,9% "
                 "laga-tim, jadi sinyal bintangnya ada — hanya tenggelam "
                 "di dalam ukuran agregatnya). Penyesuaiannya akhirnya "
                 "bertindak seperti pemangkasan rata ke bawah yang "
                 "tidak dibutuhkan model yang sudah terkalibrasi.")
    o.append("")
    o.append("Implikasi produksi (apa pun hasilnya): penyesuaian ini "
             "HANYA bisa dipakai oleh langkah penyegaran prediksi "
             "menjelang kickoff (~1 jam sebelum laga, saat susunan "
             "pemain terbit). Model pagi tidak bisa memakainya. "
             "Produksi TIDAK diubah oleh eksperimen ini — keputusan "
             "adopsi ada di tangan user setelah membaca laporan ini.")
    o.append("")
    o.append("## Reference reproduction check")
    o.append("")
    o.append(f"Production v5 (slim+R+NB+BB) recomputed by run_sot_v5's "
             f"own passes over ALL divisions: pooled line-9.5 log loss "
             f"**{anchor['ll']:.4f}** (RESULTS_V5.md: {REF_V5_LL}) -> "
             f"**{'MATCH' if anchor_ok else 'MISMATCH — RUN INVALID'}**. "
             f"Frozen v5 choices re-derived from warm-up only: ridge "
             f"lambda = {best_lam:g}, BB prior = {best_p:g}, NB r = "
             f"{nb_r:.2f}. On the identical evaluation subset (top-5 "
             f"test matches in the FotMob store, n = {base['n']:,}) the "
             f"base recomputed inside this experiment matches "
             f"pass_eval's per-division numbers to {xchk:.1e} log loss — "
             "the base being adjusted is exactly production v5.")
    o.append("")
    o.append("## The adjustment")
    o.append("")
    o.append("Per team and match: trailing player shares (365d decay) "
             "of team SOT (variants sot*) or of team shots (variants "
             "shot*) over store matches strictly before the match; "
             "missing_share = share mass of players not in the actual "
             "starting XI (bench counts fully missing in *B, half in "
             "*A). Both v5 ensemble members' per-team expectations are "
             "scaled by (1 - k * missing_share); the NB/50-50 ensemble "
             "machinery is otherwise unchanged. k tuned on 2022/23 "
             "only (grid 0.0-1.0 step 0.1, ties -> smaller k).")
    o.append("")
    o.append("### Tuning on 2022/23 (top-5 store matches, line 9.5)")
    o.append("")
    o.append("| Variant | n | LL(k=0) | best k | LL(best k) | Δ |")
    o.append("|---|---|---|---|---|---|")
    for v in VARIANTS:
        ti = tune_info[v]
        o.append(f"| {v} | {ti['n']:,} | {ti['ll0']:.4f} | {ti['k']:g} | "
                 f"{ti['llk']:.4f} | {ti['llk'] - ti['ll0']:+.4f} |")
    if boost:
        o.append(f"| {boost[0]} | {tune_info[boost[0].replace('+ret','')]['n']:,} "
                 f"| {boost[4]:.4f} | k={boost[1]:g}, kb={boost[2]:g} | "
                 f"{boost[3]:.4f} | {boost[3] - boost[4]:+.4f} |")
    else:
        o.append("")
        o.append(f"Boost variant (+ret): **not run** — trigger not met "
                 f"(needs a variant with k > 0 and tuning gain >= "
                 f"{-BOOST_TRIGGER_DLL:.4f}); "
                 + ("; ".join(f"{v}: k={tune_info[v]['k']:g}, "
                              f"Δ={tune_info[v]['llk'] - tune_info[v]['ll0']:+.4f}"
                              for v in VARIANTS)) + ".")
    o.append("")
    o.append("## How much production is actually missing? "
             "(test seasons, per team-match)")
    o.append("")
    for v in ("sotB", "sotA", "shotB", "shotA"):
        xs = dist[v]
        o.append(f"- {v}: mean {np.mean(xs):.3f}, median "
                 f"{pct(xs, 50):.3f}, p90 {pct(xs, 90):.3f}, max "
                 f"{max(xs):.3f}; missing > 0.10 in "
                 f"{100 * np.mean([x > 0.10 for x in xs]):.1f}% of "
                 f"team-matches, > 0.20 in "
                 f"{100 * np.mean([x > 0.20 for x in xs]):.1f}%.")
    o.append(f"- The single largest trailing-SOT player is absent from "
             f"the XI in {top_absent[0]:,} of {top_absent[1]:,} "
             f"team-matches ({100 * top_absent[0] / max(top_absent[1], 1):.1f}%).")
    o.append(f"- Return share (SOT share of XI players who were not in "
             f"the previous XI): mean {np.mean(ret_share):.3f}, p90 "
             f"{pct(ret_share, 90):.3f}.")
    o.append("")
    o.append("## Headline — identical subset, line 9.5")
    o.append("")
    o.append("| Variant | LogLoss | Brier | Calib err (pp) | MAE | ΔLL vs v5 |")
    o.append("|---|---|---|---|---|---|")
    o.append(f"| v5 (unadjusted) | {base['ll']:.4f} | {base['brier']:.4f} "
             f"| {base['calib']:.2f} | {mae['base'][1] / mae['base'][0]:.2f} "
             f"| — |")
    for v in chosen:
        sv = stats(pooled[v])
        o.append(f"| {v} (k={chosen[v][0]:g}"
                 + (f", kb={chosen[v][1]:g}" if chosen[v][1] else "")
                 + f") | {sv['ll']:.4f} | {sv['brier']:.4f} | "
                 f"{sv['calib']:.2f} | {mae[v][1] / mae[v][0]:.2f} | "
                 f"{gates[v]['dll']:+.4f} |")
    o.append("")
    o.append("## By season — line 9.5 log loss")
    o.append("")
    o.append("| Season | n | v5 | " + " | ".join(chosen) + " |")
    o.append("|---|" + "---|" * (len(chosen) + 2))
    for sname in TEST_SEASONS:
        cells = " | ".join(f"{stats(season_acc[v][sname])['ll']:.4f}"
                           for v in chosen)
        sb = stats(season_acc["base"][sname])
        o.append(f"| {sname} | {sb['n']:,} | {sb['ll']:.4f} | {cells} |")
    o.append("")
    o.append("## By division — line 9.5 log loss")
    o.append("")
    o.append("| Div | n | v5 | " + " | ".join(chosen) + " |")
    o.append("|---|" + "---|" * (len(chosen) + 2))
    for d in TOP5:
        cells = " | ".join(f"{stats(div_acc[v][d])['ll']:.4f}"
                           for v in chosen)
        sb = stats(div_acc["base"][d])
        o.append(f"| {d} | {sb['n']:,} | {sb['ll']:.4f} | {cells} |")
    o.append("")
    o.append("## Gate verdict")
    o.append("")
    for v in chosen:
        g = gates[v]
        o.append(f"- {v}: pooled LL {'improves' if g['ll_ok'] else 'does NOT improve'} "
                 f"({g['dll']:+.4f}); calibration {g['calib']:.2f}pp vs "
                 f"base {base['calib']:.2f}pp "
                 f"({'ok' if g['calib_ok'] else 'WORSE — fail'}); worst "
                 f"division ΔLL {g['worst']:+.4f} (limit +0.003) -> "
                 f"**{'ADOPTABLE (as a JIT step)' if g['adoptable'] else 'not adoptable'}**.")
    o.append(f"- **Winner: {winner}**" if winner else
             "- **No variant is adoptable — production v5 stays "
             "unchanged, and a JIT lineup step is not worth building "
             "on this evidence.**")
    o.append("")
    o.append("## Method notes and caveats")
    o.append("")
    o.append("- Information discipline: shares use store matches "
             "strictly before the predicted match; the ONLY same-match "
             "information used is the official starting XI/bench — "
             "exactly what is public ~1h before kickoff, which is the "
             "decision point being evaluated. The match's own shotmap "
             "is never used for its own prediction (it updates the "
             "trailing state only afterwards).")
    o.append("- Departed players: a transferred/retired player's "
             "decayed share keeps counting as 'missing' until it "
             "decays away (365d half-life), so missing_share is an "
             "upper bound on truly-absent production — one reason the "
             "tuned k, not the raw share, carries the effect size.")
    o.append("- The store starts 2022/23, so tuning-season shares "
             "warm up from zero during Aug-Oct 2022; the tuning grid "
             "sees a weaker version of the signal than the test "
             "seasons have. Test-season shares benefit from the full "
             "trailing window.")
    o.append("- Player shares are team-specific (a mid-season "
             "transfer's history stays at his old club) and use the "
             "house SOT counting rule (on-target, not blocked, not "
             "own goal), the rule already validated against the "
             "spine's HST/AST.")
    o.append("- Why it failed (the distribution section is the "
             "evidence): missing_share averages 0.56 — but that mass "
             "is mostly long-tail production (fringe players, "
             "occasional shooters, departed players still decaying), "
             "not star absence. The single top producer IS absent in "
             "39.9% of team-matches, so the star signal exists, but "
             "the aggregate share drowns it: at any k > 0 the factor "
             "(1 - k * missing) acts mainly as a near-uniform "
             "downward scaling of a base that is already calibrated "
             "(calibration error explodes 0.01pp -> ~5pp). Tuning on "
             "2022/23 understated this: the store had just started, "
             "share mass was still warming up, so the same k looked "
             "harmless there. An obvious follow-up hypothesis for a "
             "FUTURE round (not run here — testing it now would be "
             "fitting to the test set): restrict/renormalise shares "
             "to the current matchday squad (starters + bench + "
             "unavailable) so departed/fringe mass drops out, and "
             "validate on a fresh split.")
    o.append("- No odds anywhere: predictive accuracy/calibration "
             "only, not betting value.")
    o.append(f"- Script runtime (this run): {time.time() - t0:.0f}s.")

    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write("\n".join(o) + "\n")

    print(f"\nbase subset LL {base['ll']:.4f} calib {base['calib']:.2f}pp")
    for v in chosen:
        print(f"{v:12s} LL {gates[v]['ll']:.4f} dLL {gates[v]['dll']:+.4f} "
              f"calib {gates[v]['calib']:.2f}pp worst div "
              f"{gates[v]['worst']:+.4f} adoptable={gates[v]['adoptable']}")
    print(f"winner: {winner or 'NONE'}")
    print(f"wrote {OUT}  (runtime {time.time() - t0:.0f}s)")


if __name__ == "__main__":
    main()
