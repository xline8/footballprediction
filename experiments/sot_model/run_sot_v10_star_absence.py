#!/usr/bin/env python
"""SOT model — v10: the star-absence test (user's claim, isolated).

Question (user's intuition): if a team's STAR player is absent, the
team's shots on target (SOT) drop. v8 adjusted for AGGREGATE missing
production (mean missing share 0.56, dominated by fringe/departed
players) and failed its gate outright. This experiment isolates only
team-matches whose TRAILING TOP shooter holds a truly dominant share
of the team's SOT and does not appear in the match at all.

Design was pre-registered in RESULTS_V10_STAR_ABSENCE.md (committed
before this script was run). Summary of the locked design:

- Frame: top-5 league matches in the FotMob store with lineup +
  shotmap, seasons 2022/23-2025/26 (the v5/V8 validation frame).
- Trailing shares: per (div, team), each player's share of team SOT
  over store matches STRICTLY BEFORE the current one — EXPANDING
  window, no decay (deliberate difference from v8, pre-registered),
  house SOT rule (isOnTarget, not blocked, not own goal), team-
  specific. Team-match eligible only with >= 5 prior store matches.
- Dominant shooter: the team's top trailing-share player when that
  share >= threshold. Primary threshold 25%; sensitivity 20%, 30%.
- Appeared: in the starting XI, or a substitute with a subIn event
  (lineup performance.substitutionEvents), or recorded a shot in the
  match shotmap. Absent = dominant player did not appear at all.
- Expectations: production v5 walk-forward per-team expectations via
  v8's verified machinery (base_components / prob_from), with the
  two anchors (pooled 0.6304; subset base 0.6488) required to match.
  Pass schedules mirror v8 (separate tune-schedule pass for 2022/23,
  eval-schedule pass for 2023/24-2025/26) because RegressionStore's
  lazy refits depend on per-division call order.
- Actuals: spine HST/AST.
- Primary verdict rule (locked): the effect is REAL only if, at the
  25% threshold, the dominant-absent mean residual (actual - expected)
  is < 0 AND its 95% CI (normal approx) lies entirely below 0.
- Secondary (only if real): one multiplicative factor f on the
  absent team's expectation, grid 0.80-1.00 step 0.01, minimising
  subset line-9.5 log loss on tuning seasons 2022/23+2023/24
  (ties -> f closest to 1.00). Mini-gate on validation 2024/25+
  2025/26: subset LL improves AND pooled LL worsens by <= 0.0005.

Run:  .venv/bin/python experiments/sot_model/run_sot_v10_star_absence.py
Writes: appends the results section to RESULTS_V10_STAR_ABSENCE.md
(refuses if already appended). No production code touched.
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
                        Ratings, NaiveTracker, load_matches, logloss)
from run_sot_v5 import (GRID_BB, GRID_LAM, RegressionStore, pass_eval,
                        pass_warmup, stats, update_all)
from run_sot_v8_lineup_jit import base_components, prob_from

OUT = os.path.join(HERE, "RESULTS_V10_STAR_ABSENCE.md")
INDEX = os.path.join(ROOT, "data_enrichment", "fotmob_full_index.csv")
CACHE = "/tmp/v10_lineup_extract.pkl"
REF_V5_LL = 0.6304              # RESULTS_V5.md pooled, slim+R+NB+BB
REF_V8_SUBSET_LL = 0.6488       # RESULTS_V8 base on the test subset
FRAME_SEASONS = ["2022/23", "2023/24", "2024/25", "2025/26"]
TUNE_SEASON = "2022/23"
MIN_PRIOR = 5
THRESHOLDS = [0.20, 0.25, 0.30]
PRIMARY_THR = 0.25
F_GRID = [round(0.80 + 0.01 * i, 2) for i in range(21)]
VAL_SEASONS = ["2024/25", "2025/26"]
SEC_TUNE_SEASONS = ["2022/23", "2023/24"]


# ------------------------------------------------------------- extraction
def extract_store():
    """Parse every FotMob store JSON once -> per-match player data.

    Per side: starter ids, entered-sub ids (subIn event), all bench
    ids, unavailable ids, appeared ids (starters | entered | shotmap
    shooters), per-player SOT counters (house rule), team SOT total
    from the shotmap. Plus a global player-id -> name map.
    """
    if os.path.exists(CACHE):
        with open(CACHE, "rb") as fh:
            return pickle.load(fh)
    store = {}
    names = {}
    n_no_lineup = n_no_shotmap = n_corrections = 0
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
        shots = (content.get("shotmap") or {}).get("shots") or []
        if not shots:
            n_no_shotmap += 1
        shot_pids = {"h": set(), "a": set()}
        sot_c = {"h": Counter(), "a": Counter()}
        for s in shots:
            side = tid.get(s.get("teamId"))
            if side is None or s.get("isOwnGoal"):
                continue
            pid = s.get("playerId")
            if pid is None:
                continue
            shot_pids[side].add(pid)
            if s.get("playerName"):
                names.setdefault(pid, s["playerName"])
            if s.get("isOnTarget") is True and s.get("isBlocked") is not True:
                sot_c[side][pid] += 1
        rec = {}
        for side, lkey in (("h", "homeTeam"), ("a", "awayTeam")):
            team = lineup.get(lkey) or {}
            xi, entered, bench, unav = set(), set(), set(), set()
            for p in team.get("starters") or []:
                xi.add(p["id"])
                if p.get("name"):
                    names.setdefault(p["id"], p["name"])
            for p in team.get("subs") or []:
                bench.add(p["id"])
                if p.get("name"):
                    names.setdefault(p["id"], p["name"])
                evs = ((p.get("performance") or {})
                       .get("substitutionEvents") or [])
                if any(e.get("type") == "subIn" for e in evs):
                    entered.add(p["id"])
            for p in team.get("unavailable") or []:
                if p.get("id") is not None:
                    unav.add(p["id"])
                    if p.get("name"):
                        names.setdefault(p["id"], p["name"])
            appeared = xi | entered | shot_pids[side]
            n_corrections += len(shot_pids[side] - xi - entered)
            rec[f"xi_{side}"] = xi
            rec[f"bench_{side}"] = bench
            rec[f"unav_{side}"] = unav
            rec[f"appeared_{side}"] = appeared
            rec[f"sot_{side}"] = sot_c[side]
            rec[f"sot_tot_{side}"] = sum(sot_c[side].values())
        store[(ix["div"], ix["date"], ix["home"], ix["away"])] = rec
    print(f"extracted {len(store):,} store matches (no lineup: "
          f"{n_no_lineup}, no shotmap: {n_no_shotmap}, shooter-not-in-"
          f"lineup corrections: {n_corrections})")
    out = {"store": store, "names": names}
    with open(CACHE, "wb") as fh:
        pickle.dump(out, fh)
    return out


# ------------------------------------------------- expanding trailing shares
class ExpShares:
    """Cumulative (expanding-window, no decay) per-player SOT totals
    per (div, spine team), from store matches strictly before."""

    def __init__(self):
        self.tot = {}   # (div, team) -> {"sot": Counter, "team": float,
                        #                    "n": int}

    def read(self, div, team):
        """-> (share dict pid->share, n_prior_matches)."""
        d = self.tot.get((div, team))
        if not d or d["team"] <= 0:
            return {}, 0 if d is None else d["n"]
        return {p: v / d["team"] for p, v in d["sot"].items()}, d["n"]

    def update(self, div, team, sot_c):
        d = self.tot.setdefault((div, team),
                                {"sot": Counter(), "team": 0.0, "n": 0})
        for pid, n in sot_c.items():
            d["sot"][pid] += n
        d["team"] += sum(sot_c.values())
        d["n"] += 1


# ------------------------------------------------------------- record pass
def collect(matches, store, lam, bp, nb_r, mode):
    """One chronological pass mirroring v8's schedule.

    mode == "tune": v8 pass_tune schedule — base components only for
        TUNE_SEASON top-5 store matches; stop at TEST_SEASONS.
    mode == "eval": v8 pass_eval schedule — base components only for
        TEST_SEASONS top-5 store matches.
    Returns (records, base_ll_sum, base_n): per-team-match records for
    frame matches, plus base line-9.5 LL accumulation (eval mode).
    """
    sot = Ratings(BASE_HL, BASE_K, "sot")
    shots = Ratings(BASE_HL, BASE_K, "shots", track_ratio=True)
    naive = NaiveTracker()
    reg = RegressionStore(matches, [lam])
    shares = ExpShares()
    records = []
    ll_sum, ll_n = 0.0, 0

    for m in matches:
        if mode == "tune" and m["season"] in TEST_SEASONS:
            break
        day, div = m["day"], m["div"]
        home, away = m["home"], m["away"]
        key = (div, m["date"], home, away)
        rec = store.get(key)
        in_frame = (rec is not None and div in TOP5 and
                    ((mode == "tune" and m["season"] == TUNE_SEASON) or
                     (mode == "eval" and m["season"] in TEST_SEASONS)))
        if in_frame:
            rb_h, rb_a, n_h, n_a = base_components(
                sot, shots, naive, reg, div, home, away, day, lam, bp)
            total = m["hst"] + m["ast"]
            if mode == "eval":
                p0 = prob_from(rb_h, rb_a, n_h, n_a, 1.0, 1.0, nb_r)
                ll_sum += logloss(p0, 1.0 if total > MAIN_LINE else 0.0)
                ll_n += 1
            sides = {}
            for side, team, rb, nv, act in (
                    ("h", home, rb_h, n_h, m["hst"]),
                    ("a", away, rb_a, n_a, m["ast"])):
                sh, n_prior = shares.read(div, team)
                top_pid, top_share = None, 0.0
                if sh:
                    top_pid = max(sh, key=lambda p: (sh[p], p))
                    top_share = sh[top_pid]
                appeared = rec[f"appeared_{side}"]
                if top_pid is None:
                    state = "nodef"
                elif top_pid in appeared:
                    state = "present"
                elif top_pid in rec[f"unav_{side}"]:
                    state = "unavailable"
                elif top_pid in rec[f"bench_{side}"]:
                    state = "bench_unused"
                else:
                    state = "not_listed"
                sides[side] = {
                    "team": team, "exp": 0.5 * rb + 0.5 * nv,
                    "actual": act, "top_pid": top_pid,
                    "top_share": top_share, "n_prior": n_prior,
                    "state": state,
                    "n_ge25": sum(1 for v in sh.values() if v >= 0.25),
                    "store_sot": rec[f"sot_tot_{side}"],
                }
            records.append({
                "div": div, "season": m["season"], "date": m["date"],
                "home": home, "away": away, "total": total,
                "rb_h": rb_h, "rb_a": rb_a, "n_h": n_h, "n_a": n_a,
                "h": sides["h"], "a": sides["a"],
            })
        if rec is not None:
            shares.update(div, home, rec["sot_h"])
            shares.update(div, away, rec["sot_a"])
        update_all(sot, shots, naive, m)

    return records, ll_sum, ll_n


# ------------------------------------------------------------------ stats
def resid_stats(pairs):
    """pairs: list of (actual, expected) -> summary dict."""
    if not pairs:
        return {"n": 0}
    act = np.array([a for a, _ in pairs], dtype=float)
    exp = np.array([e for _, e in pairs], dtype=float)
    res = act - exp
    n = len(pairs)
    mean = float(res.mean())
    sd = float(res.std(ddof=1)) if n > 1 else 0.0
    half = 1.96 * sd / math.sqrt(n)
    return {"n": n, "mean_exp": float(exp.mean()),
            "mean_act": float(act.mean()), "mean_resid": mean,
            "lo": mean - half, "hi": mean + half,
            "agg_pct": float((act.sum() - exp.sum()) / exp.sum() * 100),
            "case_pct": float(np.mean(res / exp) * 100)}


def side_cases(records, thr, want_absent):
    out = []
    for r in records:
        for side in ("h", "a"):
            s = r[side]
            if s["n_prior"] < MIN_PRIOR or s["top_share"] < thr:
                continue
            absent = s["state"] != "present" and s["state"] != "nodef"
            if absent == want_absent:
                out.append((s["actual"], s["exp"]))
    return out


def match_subset_ll(records, f, nb_r):
    """Mean line-9.5 log loss over match records, scaling the
    expectation of any dominant-absent (25%, eligible) side by f."""
    tot, n = 0.0, 0
    for r in records:
        f_h = f_a = 1.0
        for side, attr in (("h", "f_h"), ("a", "f_a")):
            s = r[side]
            if (s["n_prior"] >= MIN_PRIOR
                    and s["top_share"] >= PRIMARY_THR
                    and s["state"] not in ("present", "nodef")):
                if attr == "f_h":
                    f_h = f
                else:
                    f_a = f
        p = prob_from(r["rb_h"], r["rb_a"], r["n_h"], r["n_a"],
                      f_h, f_a, nb_r)
        tot += logloss(p, 1.0 if r["total"] > MAIN_LINE else 0.0)
        n += 1
    return tot / n if n else float("nan")


def has_absent_side(r):
    return any(r[side]["n_prior"] >= MIN_PRIOR
               and r[side]["top_share"] >= PRIMARY_THR
               and r[side]["state"] not in ("present", "nodef")
               for side in ("h", "a"))


# -------------------------------------------------------------------- main
def fmt(x, nd=3):
    return f"{x:+.{nd}f}" if isinstance(x, float) else str(x)


def main():
    t0 = time.time()
    if os.path.exists(OUT):
        with open(OUT, encoding="utf-8") as fh:
            if "\n## Hasil\n" in fh.read():
                print("ABORT: results section already appended to "
                      f"{OUT}; refusing to double-append.")
                return
    matches = load_matches()
    ext = extract_store()
    store, names = ext["store"], ext["names"]

    # frozen v5 choices + full-set anchor, exactly as run_sot_v5/v8 do
    ll_r, ll_bb, nb_r, _ = pass_warmup(matches)
    tune_r = {l: s / n for l, (n, s) in ll_r.items()}
    tune_bb = {p: s / n for p, (n, s) in ll_bb.items()}
    best_lam = min(GRID_LAM, key=lambda l: (tune_r[l], -l))
    best_p = min(GRID_BB, key=lambda p: (tune_bb[p], -p))
    pooled5, _, _, _, _ = pass_eval(matches, best_lam, best_p, nb_r)
    anchor = stats(pooled5["slim+R+NB+BB"])
    anchor_ok = abs(anchor["ll"] - REF_V5_LL) < 0.0005
    print(f"v5 frozen: lam={best_lam:g} P={best_p:g} NB r={nb_r:.2f}; "
          f"anchor pooled LL {anchor['ll']:.4f} vs {REF_V5_LL} -> "
          f"{'MATCH' if anchor_ok else 'MISMATCH'}")

    rec_tune, _, _ = collect(matches, store, best_lam, best_p, nb_r,
                             "tune")
    rec_eval, base_ll_sum, base_n = collect(matches, store, best_lam,
                                            best_p, nb_r, "eval")
    base_ll = base_ll_sum / base_n if base_n else float("nan")
    subset_ok = abs(base_ll - REF_V8_SUBSET_LL) < 0.0005
    print(f"eval pass: {len(rec_eval):,} test matches, base LL "
          f"{base_ll:.4f} vs {REF_V8_SUBSET_LL} -> "
          f"{'MATCH' if subset_ok else 'MISMATCH'}; tune pass: "
          f"{len(rec_tune):,} matches")
    valid = anchor_ok and subset_ok

    records = rec_tune + rec_eval
    records.sort(key=lambda r: (r["date"], r["div"], r["home"]))

    # cross-check: shotmap team totals vs spine HST/AST
    agree = tot_pairs = 0
    for r in records:
        for side, act in (("h", r["h"]["actual"]),
                          ("a", r["a"]["actual"])):
            tot_pairs += 1
            if r[side]["store_sot"] == act:
                agree += 1
    agree_pct = 100 * agree / max(tot_pairs, 1)

    # ------------------------------------------------------------ primary
    prim = {}
    for thr in THRESHOLDS:
        prim[thr] = {
            "absent": resid_stats(side_cases(records, thr, True)),
            "present": resid_stats(side_cases(records, thr, False)),
        }
    pa = prim[PRIMARY_THR]["absent"]
    effect_real = (valid and pa.get("n", 0) > 0
                   and pa["mean_resid"] < 0 and pa["hi"] < 0)

    # absent-case characterisation at the primary threshold
    state_counts = Counter()
    pid_counts = Counter()
    season_resid = defaultdict(list)
    div_resid = defaultdict(list)
    for r in records:
        for side in ("h", "a"):
            s = r[side]
            if (s["n_prior"] >= MIN_PRIOR
                    and s["top_share"] >= PRIMARY_THR
                    and s["state"] not in ("present", "nodef")):
                state_counts[s["state"]] += 1
                pid_counts[s["top_pid"]] += 1
                season_resid[r["season"]].append(
                    (s["actual"], s["exp"]))
                div_resid[r["div"]].append((s["actual"], s["exp"]))
    top_names = [(names.get(pid, str(pid)), c)
                 for pid, c in pid_counts.most_common(10)]

    # ---------------------------------------------------------- secondary
    sec = None
    if effect_real:
        tune_matches = [r for r in records
                        if r["season"] in SEC_TUNE_SEASONS
                        and has_absent_side(r)]
        val_matches = [r for r in records
                       if r["season"] in VAL_SEASONS]
        val_subset = [r for r in val_matches if has_absent_side(r)]
        curve = {f: match_subset_ll(tune_matches, f, nb_r)
                 for f in F_GRID}
        f_star = min(F_GRID, key=lambda f: (curve[f], abs(f - 1.0)))
        tune_pairs = []
        for r in records:
            if r["season"] not in SEC_TUNE_SEASONS:
                continue
            for side in ("h", "a"):
                s = r[side]
                if (s["n_prior"] >= MIN_PRIOR
                        and s["top_share"] >= PRIMARY_THR
                        and s["state"] not in ("present", "nodef")):
                    tune_pairs.append((s["actual"], s["exp"]))
        mm = resid_stats(tune_pairs)
        sec = {
            "n_tune_matches": len(tune_matches), "curve": curve,
            "f_star": f_star, "ll_tune_f1": curve[1.0],
            "ll_tune_star": curve[f_star],
            "mean_match_f": (mm["mean_act"] / mm["mean_exp"]
                             if mm.get("n") else float("nan")),
            "val_subset_f1": match_subset_ll(val_subset, 1.0, nb_r),
            "val_subset_star": match_subset_ll(val_subset, f_star, nb_r),
            "val_pool_f1": match_subset_ll(val_matches, 1.0, nb_r),
            "val_pool_star": match_subset_ll(val_matches, f_star, nb_r),
            "n_val_subset": len(val_subset),
            "n_val_pool": len(val_matches),
        }
        sec["subset_ok"] = sec["val_subset_star"] < sec["val_subset_f1"]
        sec["pool_ok"] = (sec["val_pool_star"] - sec["val_pool_f1"]
                          <= 0.0005)
        sec["gate_pass"] = sec["subset_ok"] and sec["pool_ok"]

    # -------------------------------------------------------------- report
    o = []
    o.append("")
    o.append("## Hasil")
    o.append("")
    o.append(f"Validitas run: jangkar pooled v5 = {anchor['ll']:.4f} "
             f"(target {REF_V5_LL}) -> "
             f"{'COCOK' if anchor_ok else 'TIDAK COCOK'}; log loss "
             f"basis subset uji = {base_ll:.4f} (target "
             f"{REF_V8_SUBSET_LL}, n = {base_n:,}) -> "
             f"{'COCOK' if subset_ok else 'TIDAK COCOK'}. "
             + ("Kedua jangkar cocok — angka di bawah sah."
                if valid else
                "**JANGKAR TIDAK COCOK — RUN TIDAK SAH, angka di "
                "bawah tidak boleh dipakai.**"))
    o.append("")
    o.append(f"Kerangka terkumpul: {len(rec_tune):,} laga 2022/23 + "
             f"{len(rec_eval):,} laga 2023/24–2025/26 = "
             f"{len(records):,} laga. Pemeriksaan silang aktual: "
             f"total SOT shotmap per tim sama persis dengan HST/AST "
             f"pada {agree:,} dari {tot_pairs:,} laga-tim "
             f"({agree_pct:.1f}%).")
    o.append("")
    o.append("### Pengukuran primer — residual (aktual − ekspektasi v5) per laga-tim")
    o.append("")
    o.append("| Ambang | Kelompok | n | Rata-rata eksp. | Rata-rata aktual | Rata-rata residual [IK 95%] | Kekurangan agregat | Rata-rata per kasus |")
    o.append("|---|---|---|---|---|---|---|---|")
    for thr in THRESHOLDS:
        for grp, lab in (("absent", "dominan ABSEN"),
                         ("present", "dominan tampil (kontrol)")):
            s = prim[thr][grp]
            if not s.get("n"):
                continue
            o.append(f"| {thr:.0%} | {lab} | {s['n']:,} | "
                     f"{s['mean_exp']:.2f} | {s['mean_act']:.2f} | "
                     f"{s['mean_resid']:+.3f} [{s['lo']:+.3f}, "
                     f"{s['hi']:+.3f}] | {s['agg_pct']:+.1f}% | "
                     f"{s['case_pct']:+.1f}% |")
    o.append("")
    pp = prim[PRIMARY_THR]["present"]
    o.append(f"Putusan efek (aturan terkunci, ambang 25%): rata-rata "
             f"residual dominan-absen = {pa['mean_resid']:+.3f} dengan "
             f"IK 95% [{pa['lo']:+.3f}, {pa['hi']:+.3f}] -> efek "
             f"**{'NYATA' if effect_real else 'TIDAK TERBUKTI'}**. "
             f"Kontrol dominan-tampil pada ambang yang sama: "
             f"{pp['mean_resid']:+.3f} [{pp['lo']:+.3f}, "
             f"{pp['hi']:+.3f}] (n = {pp['n']:,}). Pola dosis antar "
             f"ambang terlihat pada tabel: kekurangan agregat absen "
             + ", ".join(f"{t:.0%}: {prim[t]['absent']['agg_pct']:+.1f}%"
                         for t in THRESHOLDS) + ".")
    o.append("")
    o.append("### Karakterisasi kasus dominan-absen (ambang 25%, deskriptif)")
    o.append("")
    lab_state = {"unavailable": "terdaftar unavailable (cedera/skorsing)",
                 "bench_unused": "di bangku cadangan, tidak dimainkan",
                 "not_listed": "tidak ada di daftar skuad hari laga"}
    for st, c in state_counts.most_common():
        o.append(f"- {lab_state.get(st, st)}: {c:,} laga-tim")
    o.append("- Paling sering absen sebagai penembak dominan: "
             + "; ".join(f"{nm} ({c}×)" for nm, c in top_names) + ".")
    o.append("")
    o.append("Residual dominan-absen per musim (deskriptif, tanpa gerbang):")
    o.append("")
    o.append("| Musim | n | Rata-rata residual [IK 95%] | Kekurangan agregat |")
    o.append("|---|---|---|---|")
    for sname in FRAME_SEASONS:
        s = resid_stats(season_resid.get(sname, []))
        if s.get("n"):
            o.append(f"| {sname} | {s['n']:,} | {s['mean_resid']:+.3f} "
                     f"[{s['lo']:+.3f}, {s['hi']:+.3f}] | "
                     f"{s['agg_pct']:+.1f}% |")
    o.append("")
    o.append("Residual dominan-absen per divisi (deskriptif, tanpa gerbang):")
    o.append("")
    o.append("| Divisi | n | Rata-rata residual [IK 95%] | Kekurangan agregat |")
    o.append("|---|---|---|---|")
    for d in TOP5:
        s = resid_stats(div_resid.get(d, []))
        if s.get("n"):
            o.append(f"| {d} | {s['n']:,} | {s['mean_resid']:+.3f} "
                     f"[{s['lo']:+.3f}, {s['hi']:+.3f}] | "
                     f"{s['agg_pct']:+.1f}% |")
    o.append("")
    if sec is None:
        o.append("### Pengukuran sekunder")
        o.append("")
        o.append("Tidak dijalankan — syaratnya (efek primer nyata "
                 "pada ambang 25% menurut aturan terkunci) tidak "
                 "terpenuhi" + (" atau run tidak sah" if not valid
                                else "") + ".")
        o.append("")
    else:
        o.append("### Pengukuran sekunder — satu faktor penyesuaian")
        o.append("")
        o.append(f"Efek primer nyata, jadi penyesuaian satu parameter "
                 f"di-fit pada musim tuning "
                 f"({' + '.join(SEC_TUNE_SEASONS)}; "
                 f"{sec['n_tune_matches']:,} laga bersisi dominan-"
                 f"absen): faktor terpilih **f = {sec['f_star']:.2f}** "
                 f"(log loss subset tuning {sec['ll_tune_star']:.4f} "
                 f"vs f = 1: {sec['ll_tune_f1']:.4f}). Faktor pencocok-"
                 f"rata-rata pada laga-tim dominan-absen tuning = "
                 f"{sec['mean_match_f']:.3f} (referensi deskriptif).")
        o.append("")
        o.append(f"Validasi ({' + '.join(VAL_SEASONS)}): log loss "
                 f"subset ({sec['n_val_subset']:,} laga) "
                 f"{sec['val_subset_star']:.4f} dengan penyesuaian vs "
                 f"{sec['val_subset_f1']:.4f} tanpa -> subset "
                 f"{'MEMBAIK' if sec['subset_ok'] else 'TIDAK MEMBAIK'}"
                 f"; log loss pooled ({sec['n_val_pool']:,} laga) "
                 f"{sec['val_pool_star']:.4f} vs "
                 f"{sec['val_pool_f1']:.4f} (selisih "
                 f"{sec['val_pool_star'] - sec['val_pool_f1']:+.4f}, "
                 f"batas +0,0005) -> pooled "
                 f"{'AMAN' if sec['pool_ok'] else 'MELANGGAR BATAS'}.")
        o.append("")
        o.append(f"**Mini-gate: {'LOLOS' if sec['gate_pass'] else 'GAGAL'}**"
                 + (" — penyesuaian faktor "
                    f"{sec['f_star']:.2f} untuk tim yang penembak "
                    "dominannya absen adalah REKOMENDASI BANGUN "
                    "sebagai langkah penyegaran JIT terpisah (bukan "
                    "perubahan produksi di eksperimen ini)."
                    if sec['gate_pass'] else
                    " — penyesuaian tidak direkomendasikan."))
        o.append("")
    o.append("## Catatan metode")
    o.append("")
    o.append("- Porsi trailing memakai jendela expanding tanpa decay "
             "(praregistrasi) — berbeda dari V8 yang memakai decay "
             "365 hari. Definisi absen juga lebih ketat dari V8: V8 "
             "menghitung 'tidak menjadi starter'; di sini pemain "
             "pengganti yang masuk dihitung TAMPIL, jadi 'absen' "
             "berarti benar-benar tidak bermain semenit pun.")
    o.append("- Ekspektasi v5 untuk 2022/23 berasal dari pass "
             "berjadwal tuning dan untuk 2023/24–2025/26 dari pass "
             "berjadwal eval, meniru V8 persis; kedua jangkar "
             "reproduksi v5 cocok (lihat Validitas run).")
    o.append("- Satu-satunya informasi hari-laga yang dipakai adalah "
             "daftar tampil/tidak tampilnya pemain — persis yang "
             "publik ~1 jam sebelum kickoff, titik keputusan JIT "
             "yang dinilai. Shotmap laga itu sendiri hanya memperbarui "
             "keadaan trailing SESUDAH laganya dinilai.")
    o.append("- Tidak ada odds: akurasi prediksi saja, bukan nilai "
             "taruhan.")
    o.append(f"- Waktu jalan skrip: {time.time() - t0:.0f} detik.")

    with open(OUT, "a", encoding="utf-8") as fh:
        fh.write("\n".join(o) + "\n")

    print(f"\nPRIMARY 25% absent: n={pa.get('n')} resid "
          f"{pa.get('mean_resid', float('nan')):+.3f} "
          f"[{pa.get('lo', float('nan')):+.3f}, "
          f"{pa.get('hi', float('nan')):+.3f}] agg "
          f"{pa.get('agg_pct', float('nan')):+.1f}% | present: n="
          f"{pp.get('n')} resid {pp.get('mean_resid', float('nan')):+.3f}")
    print(f"effect_real={effect_real} valid={valid}")
    if sec:
        print(f"SECONDARY f*={sec['f_star']:.2f} gate_pass="
              f"{sec['gate_pass']} (subset {sec['val_subset_f1']:.4f}"
              f"->{sec['val_subset_star']:.4f}; pooled "
              f"{sec['val_pool_f1']:.4f}->{sec['val_pool_star']:.4f})")
    print(f"wrote results section to {OUT} "
          f"(runtime {time.time() - t0:.0f}s)")


if __name__ == "__main__":
    main()
