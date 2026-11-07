#!/usr/bin/env python
"""Shots-on-target (SOT) model — v7: FotMob shot/lineup features on v5.

Tests whether the features materialised from the FotMob full-response
store (data_enrichment/shot_lineup_features.csv, 7,532 top-5 matches,
seasons >= 2022/23) improve on the production v5 recipe
(slim + R + NB + BB; ridge lam = 100, BB prior P = 200, NB r estimated
in-pass exactly as run_sot_v5.py does — production model_sot.py froze
RIDGE_LAM = 100, BB_PRIOR = 200, NB_R = 79.94).

REFERENCE DISCIPLINE
--------------------
The v5 variant in this script is computed with the exact formulas of
run_sot_v5.pass_eval's combined variant. Sanity anchor: v5 recomputed
on the FULL standard test set (all divisions, 2023/24-2025/26, the
21,461 matches of every earlier round) must reproduce RESULTS_V5.md's
pooled line-9.5 log loss 0.6304; if it does not, the run is invalid.
All feature variants are compared against v5 recomputed on the SAME
match set (top-5 test matches present in the features file).

NO-LEAKAGE DISCIPLINE (strict)
------------------------------
- Every feature for a match is a TRAILING aggregate over the team's
  earlier matches in the features file only (last 10 at the same
  venue; if fewer than 5 same-venue matches, last 10 at any venue; if
  fewer than 5 matches in total, the feature layer is unavailable for
  that match and every feature variant falls back to plain v5 for it —
  fallbacks are counted). The match's own shotmap, stats and lineup
  are NEVER used for its own prediction; feature state updates only
  after the match has been predicted, in the same sequential order
  the ratings machinery uses.
- Feature coverage starts 2022/23. All tuning (standardisation
  constants, per-group coefficients) uses 2022/23 ONLY. Test seasons
  2023/24-2025/26 are untouched by every choice.
- The location splits (G2) and shooter/lineup identities (G3) are not
  in the flat features CSV (it carries starter COUNTS only), so they
  are extracted here from the same FotMob store JSONs the CSV was
  materialised from, with the extractor's exact counting rules
  (house SOT rule; inside-box = isFromInsideBox is True), cached to
  v7_extra_features.csv next to this script. team_rating and the
  same-match unavailable counts are post-match fields and are not
  used anywhere.

FEATURE GROUPS (each tested separately on top of v5, then survivors
combined; a group survives iff its tuned parameter is non-trivial AND
it beats v5 on the 2022/23 tuning set)
--------------------------------------------------------------------------
Let th/ta be v5's per-team blended expectations (0.5*(regression exp
+ BB shots-implied exp)); the naive ensemble member is never touched.
Adjustments multiply th/ta before the NB stage:
    lam1 = exp(b1*z1h + b3*z3h + b4*z4h) * th
         + exp(b1*z1a + b3*z3a + b4*z4a) * ta     (groups present only)
z's are means of per-component z-scores; component standardisation
(mu, sd) is frozen from the trailing observations recorded at
2022/23 matches. Components, per team (attack perspective):

G1 shot quality (own trailing): xG per shot, xGOT per shot,
   inside-box share, deep-shot share (x >= 80), blocked-on-target
   share. One coefficient b1 (symmetric grid, tuned on 2022/23).
G2 on-target craft by location (structural, replaces the ratio stage
   inside th/ta): the BB single ratio is blended with a location-aware
   ratio built from trailing inside/outside shot and SOT sums:
       share_in = (S_in + 200*lg_share_in) / (S + 200)
       ratio_l  = (N_l + 200*rho_l) / (S_l + 200)   l in {in, out}
       ib_loc   = exp_shots * (share_in*ratio_in
                               + (1-share_in)*ratio_out)
   league shares/ratios are walk-forward cumulative division sums
   over earlier features matches; prior 200 mirrors the BB prior
   (frozen, not tuned). Blend weight w in {0, .25, .5, .75, 1}
   tuned on 2022/23; w = 0 reproduces v5 exactly.
G3 shooter concentration & continuity (own trailing): mean share of
   team shots taken by its top-3 shooters, mean share of team SOT by
   its top-3 shooters, lineup continuity (mean over the last up-to-5
   starter-overlap transitions |S_t n S_{t-1}| / |S_t|). One
   coefficient b3.
G4 match stats: own trailing big chances created per match,
   OPPONENT's trailing big chances conceded per match, own trailing
   possession. One coefficient b4.

GATE (pre-registered, same spirit as V5/V6, calibration leg as
specified for this round): a variant is adopt-worthy only if ALL
hold vs the same-set v5 reference: pooled line-9.5 log loss improves;
pooled calibration error does not worsen (delta <= 0.0pp); no top-5
division's log loss worsens by more than 0.003.

Run:  .venv/bin/python experiments/sot_model/run_sot_v7.py
Writes RESULTS_V7_FEATURES.md (+ v7_extra_features.csv cache) next to
itself. No production code touched.
"""

import csv
import json
import math
import os
import sys
import time
from collections import defaultdict, deque

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ROOT = os.path.join(HERE, "..", "..")

from run_sot_v2 import (BASE_HL, BASE_K, LINES, MAIN_LINE, TEST_SEASONS,
                        TOP5, NaiveTracker, Ratings, load_matches, logloss,
                        nb_over, poisson_over)
from run_sot_v5 import (RegressionStore, bb_ratio, pass_warmup,
                        slim_components)

OUT = os.path.join(HERE, "RESULTS_V7_FEATURES.md")
EXTRA_CACHE = os.path.join(HERE, "v7_extra_features.csv")
FEATURES_CSV = os.path.join(ROOT, "data_enrichment",
                            "shot_lineup_features.csv")
INDEX_CSV = os.path.join(ROOT, "data_enrichment", "fotmob_full_index.csv")

TUNE_SEASON = "2022/23"
FROZEN_LAM = 100.0        # production RIDGE_LAM (v5 tuning chose 100)
FROZEN_P = 200.0          # production BB_PRIOR (v5 tuning chose 200)
REF_V5_LL = 0.6304        # RESULTS_V5.md combined, pooled line 9.5
MIN_HIST = 5              # minimum trailing matches for the feature layer
WINDOW = 10               # trailing window (matches)
BETA_GRID = [0.0, 0.01, -0.01, 0.02, -0.02, 0.04, -0.04, 0.07, -0.07,
             0.1, -0.1, 0.15, -0.15, 0.2, -0.2, 0.3, -0.3]
W_GRID = [0.0, 0.25, 0.5, 0.75, 1.0]
G2_PRIOR = 200.0          # mirrors BB prior; frozen, not tuned

GROUPS = ["G1", "G2", "G3", "G4"]
LABELS = {"v5": "v5 (production reference)",
          "G1": "v5 + G1 shot quality",
          "G2": "v5 + G2 location-aware ratio",
          "G3": "v5 + G3 concentration & continuity",
          "G4": "v5 + G4 match stats",
          "ALL": "v5 + surviving groups combined"}
COMPONENTS = ["xg_shot", "xgot_shot", "in_share", "deep_share",
              "blk_share", "top3_shot", "top3_sot", "cont",
              "big_pm", "poss", "opp_big_ag_pm"]
GROUP_COMPONENTS = {"G1": ["xg_shot", "xgot_shot", "in_share",
                           "deep_share", "blk_share"],
                    "G3": ["top3_shot", "top3_sot", "cont"],
                    "G4": ["big_pm", "opp_big_ag_pm", "poss"]}


# ------------------------------------------------------- data: features CSV
def _f(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def load_features():
    """(div, date, home, away) -> per-match feature row (spine names)."""
    out = {}
    with open(FEATURES_CSV, newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            row = {}
            for s in ("h", "a"):
                row[s] = {
                    "shots": _f(r[f"shots_{s}"]), "sot": _f(r[f"sot_{s}"]),
                    "xg": _f(r[f"xg_{s}"]), "xgot": _f(r[f"xgot_{s}"]),
                    "blocked_ot": _f(r[f"blocked_ot_{s}"]),
                    "inside_box": _f(r[f"inside_box_{s}"]),
                    "deep_share": _f(r[f"deep_share_{s}"]),
                    "possession": _f(r[f"possession_{s}"]),
                    "big_chances": _f(r[f"big_chances_{s}"]),
                }
            out[(r["div"], r["date"], r["home"], r["away"])] = row
    return out


# ------------------------------------------- data: store extraction (G2/G3)
def build_extra():
    """Per features match and side: location splits, deep counts,
    top-3 shooter shares, starter id sets. Mirrors the counting rules
    of data_enrichment/build_shot_lineup_features.py exactly. Cached.
    """
    if os.path.exists(EXTRA_CACHE):
        out = {}
        with open(EXTRA_CACHE, newline="", encoding="utf-8") as fh:
            for r in csv.DictReader(fh):
                side = {}
                for s in ("h", "a"):
                    side[s] = {
                        "shots_in": int(r[f"shots_in_{s}"]),
                        "sot_in": int(r[f"sot_in_{s}"]),
                        "sot": int(r[f"sot_{s}"]),
                        "deep": int(r[f"deep_{s}"]),
                        "xcount": int(r[f"xcount_{s}"]),
                        "top3_shot": _f(r[f"top3_shot_{s}"]),
                        "top3_sot": _f(r[f"top3_sot_{s}"]),
                        "starters": [int(x) for x in
                                     r[f"starters_{s}"].split(";") if x],
                    }
                out[(r["div"], r["date"], r["home"], r["away"])] = side
        return out, True

    feats = load_features()
    out = {}
    with open(INDEX_CSV, newline="", encoding="utf-8") as fh:
        index = list(csv.DictReader(fh))
    for ix in index:
        key = (ix["div"], ix["date"], ix["home"], ix["away"])
        payload = json.loads(open(os.path.join(ROOT, ix["path"]),
                                  encoding="utf-8").read())
        content = payload.get("content") or {}
        teams = (payload.get("header") or {}).get("teams") or []
        shots = (content.get("shotmap") or {}).get("shots") or []
        lineup = content.get("lineup") or {}
        side = {}
        for s, t in (("h", 0), ("a", 1)):
            tid = teams[t].get("id") if len(teams) == 2 else None
            mine = [x for x in shots if x.get("teamId") == tid]
            shots_in = sot_in = sot_tot = deep = xcount = 0
            per_shooter = defaultdict(int)
            per_shooter_sot = defaultdict(int)
            for x in mine:
                per_shooter[x.get("playerId")] += 1
                inside = x.get("isFromInsideBox") is True
                if inside:
                    shots_in += 1
                if x.get("x") is not None:
                    xcount += 1
                    if float(x["x"]) >= 80:
                        deep += 1
                if x.get("isOwnGoal") or x.get("isOnTarget") is not True:
                    continue
                if x.get("isBlocked") is True:
                    continue
                per_shooter_sot[x.get("playerId")] += 1
                sot_tot += 1
                if inside:
                    sot_in += 1

            def top3(d):
                if not d:
                    return None
                tot = sum(d.values())
                if tot <= 0:
                    return None
                return sum(sorted(d.values(), reverse=True)[:3]) / tot

            team_lu = lineup.get("homeTeam" if s == "h" else "awayTeam") \
                or {}
            starters = [p.get("id") for p in team_lu.get("starters") or []
                        if p.get("id") is not None]
            side[s] = {"shots_in": shots_in, "sot_in": sot_in,
                       "sot": sot_tot,
                       "deep": deep, "xcount": xcount,
                       "top3_shot": top3(per_shooter),
                       "top3_sot": top3(per_shooter_sot),
                       "starters": starters}
        out[key] = side

    with open(EXTRA_CACHE, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["div", "date", "home", "away"] +
                   [f"{c}_{s}" for s in ("h", "a") for c in
                    ("shots_in", "sot_in", "sot", "deep", "xcount",
                     "top3_shot", "top3_sot", "starters")])
        for (div, dt, home, away), side in sorted(out.items()):
            row = [div, dt, home, away]
            for s in ("h", "a"):
                d = side[s]
                row += [d["shots_in"], d["sot_in"], d["sot"], d["deep"],
                        d["xcount"],
                        "" if d["top3_shot"] is None else
                        f"{d['top3_shot']:.4f}",
                        "" if d["top3_sot"] is None else
                        f"{d['top3_sot']:.4f}",
                        ";".join(str(x) for x in d["starters"])]
            w.writerow(row)
    assert set(out) == set(feats), "extra/feature key mismatch"
    return out, False


# ------------------------------------------------------------ feature state
class FeatureState:
    """Trailing feature histories over features-file matches only.

    Update order mirrors the model pass: a match's features become
    visible only to LATER matches. Venue rule: last WINDOW matches at
    the same venue if at least MIN_HIST exist, else last WINDOW at
    any venue if at least MIN_HIST exist, else unavailable.
    """

    def __init__(self, feats, extra):
        self.feats = feats
        self.extra = extra
        self.hist = defaultdict(list)          # (div, team) -> [record]
        self.cont = defaultdict(lambda: deque(maxlen=5))
        self.last_starters = {}                # (div, team) -> set
        self.lg = defaultdict(lambda: [0, 0, 0, 0])  # div -> location sums
        self.n_updates = 0
        self.n_skipped_noshotmap = 0

    def _pool(self, div, team, venue):
        recs = self.hist[(div, team)]
        pv = [r for r in recs if r["venue"] == venue]
        if len(pv) >= MIN_HIST:
            return pv[-WINDOW:]
        if len(recs) >= MIN_HIST:
            return recs[-WINDOW:]
        return None

    def trailing(self, div, team, venue):
        """Aggregates for `team` attacking at `venue`, or None."""
        pool = self._pool(div, team, venue)
        if pool is None:
            return None
        sh = sum(r["shots"] for r in pool)
        if sh <= 0:
            return None
        n = len(pool)
        top3s = [r["top3_shot"] for r in pool if r["top3_shot"] is not None]
        top3t = [r["top3_sot"] for r in pool if r["top3_sot"] is not None]
        poss = [r["possession"] for r in pool if r["possession"] is not None]
        conts = self.cont[(div, team)]
        return {
            "shots": sh,
            "sot": sum(r["sot"] for r in pool),
            "xg_shot": sum(r["xg"] for r in pool) / sh,
            "xgot_shot": sum(r["xgot"] for r in pool) / sh,
            "in_share": sum(r["shots_in"] for r in pool) / sh,
            "deep_share": (sum(r["deep"] for r in pool)
                           / max(1, sum(r["xcount"] for r in pool))),
            "blk_share": sum(r["blocked_ot"] for r in pool) / sh,
            "sot_in": sum(r["sot_in"] for r in pool),
            "shots_in": sum(r["shots_in"] for r in pool),
            "top3_shot": (sum(top3s) / len(top3s)) if top3s else None,
            "top3_sot": (sum(top3t) / len(top3t)) if top3t else None,
            "cont": (sum(conts) / len(conts)) if conts else None,
            "big_pm": sum(r["big_for"] for r in pool) / n,
            "big_ag_pm": sum(r["big_ag"] for r in pool) / n,
            "poss": (sum(poss) / len(poss)) if poss else None,
            "n": n,
        }

    def league_loc(self, div):
        si, ni, so, no = self.lg[div]
        tot_in, tot_out = si, so
        if tot_in + tot_out > 0:
            share = tot_in / (tot_in + tot_out)
        else:
            share = 0.45
        rho_in = ni / si if si > 0 else None
        rho_out = no / so if so > 0 else None
        return share, rho_in, rho_out

    def update(self, m):
        key = (m["div"], m["date"], m["home"], m["away"])
        frow = self.feats.get(key)
        if frow is None:
            return
        erow = self.extra.get(key)
        div = m["div"]
        ok = True
        recs = {}
        for s, team, opp, venue in (("h", m["home"], m["away"], "h"),
                                    ("a", m["away"], m["home"], "a")):
            fr = frow[s]
            if fr["shots"] is None or erow is None:
                ok = False
                break
            er = erow[s]
            recs[(team, venue)] = {
                "venue": venue,
                "shots": fr["shots"], "sot": fr["sot"] or 0,
                "xg": fr["xg"] or 0.0,
                "xgot": fr["xgot"] or 0.0,
                "blocked_ot": fr["blocked_ot"] or 0,
                "shots_in": er["shots_in"], "sot_in": er["sot_in"],
                "deep": er["deep"], "xcount": er["xcount"],
                "top3_shot": er["top3_shot"], "top3_sot": er["top3_sot"],
                "possession": fr["possession"],
                "big_for": fr["big_chances"] or 0,
                "big_ag": frow["a" if s == "h" else "h"]["big_chances"] or 0,
                "_starters": er["starters"],
            }
        if not ok:
            self.n_skipped_noshotmap += 1
            return
        for (team, venue), rec in recs.items():
            starters = rec.pop("_starters")
            prev = self.last_starters.get((div, team))
            if prev is not None and starters:
                inter = len(set(starters) & prev)
                self.cont[(div, team)].append(inter / len(starters))
            if starters:
                self.last_starters[(div, team)] = set(starters)
            self.hist[(div, team)].append(rec)
            self.lg[div][0] += rec["shots_in"]
            self.lg[div][1] += rec["sot_in"]
            self.lg[div][2] += rec["shots"] - rec["shots_in"]
            self.lg[div][3] += rec["sot"] - rec["sot_in"]
        self.n_updates += 1


def flag_coverage():
    """Share of shots with isFromInsideBox set, by season — the
    flag's feed coverage is NOT constant over time (see report)."""
    agg = defaultdict(lambda: [0.0, 0.0])
    with open(FEATURES_CSV, newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            for s in ("h", "a"):
                sh, ib = _f(r[f"shots_{s}"]), _f(r[f"inside_box_{s}"])
                if sh:
                    agg[r["season"]][0] += ib or 0.0
                    agg[r["season"]][1] += sh
    return sorted((s, v[0] / v[1]) for s, v in agg.items() if v[1] > 0)


# ------------------------------------------------------------- v5 reference
def v5_pieces(sot, shots, naive, reg, m):
    """Production v5's pieces for one match, in run_sot_v5.pass_eval's
    exact order/formulas. Returns per-team blended expectations th/ta
    plus everything the feature layer needs."""
    day, div = m["day"], m["div"]
    home, away = m["home"], m["away"]
    (eh, ea, seh, sea, imp_h, imp_a, lam1,
     lam_n) = slim_components(sot, shots, naive, div, home, away, day)
    ib_h = seh * bb_ratio(shots, div, home, "h", day, FROZEN_P)
    ib_a = sea * bb_ratio(shots, div, away, "a", day, FROZEN_P)
    reh, rea = reg.predict(div, home, away, day, FROZEN_LAM)
    rmu_h, rmu_a = reg.league_mu(div, day, FROZEN_LAM)
    nh_r, na_r = naive.predict(div, home, away, rmu_h, rmu_a)
    return {"th": 0.5 * (reh + ib_h), "ta": 0.5 * (rea + ib_a),
            "reh": reh, "rea": rea, "ib_h": ib_h, "ib_a": ib_a,
            "seh": seh, "sea": sea, "lam_n_r": nh_r + na_r}


def update_model(sot, shots, naive, m):
    sot.update(m["div"], m["home"], m["away"], m["day"], m["hst"], m["ast"])
    shots.update(m["div"], m["home"], m["away"], m["day"], m["hs"], m["as"],
                 sot_h=m["hst"], sot_a=m["ast"])
    naive.update(m["div"], m["home"], m["away"], m["hst"], m["ast"])


def team_components(fs, m):
    """Raw trailing components for both teams of match m, or None if
    the feature layer is unavailable for either team."""
    div = m["div"]
    th_ = fs.trailing(div, m["home"], "h")
    ta_ = fs.trailing(div, m["away"], "a")
    if th_ is None or ta_ is None:
        return None
    lg_share, lg_rho_in, lg_rho_out = fs.league_loc(div)
    out = {}
    for tag, agg, opp in (("h", th_, ta_), ("a", ta_, th_)):
        out[tag] = {
            "xg_shot": agg["xg_shot"], "xgot_shot": agg["xgot_shot"],
            "in_share": agg["in_share"], "deep_share": agg["deep_share"],
            "blk_share": agg["blk_share"],
            "top3_shot": agg["top3_shot"], "top3_sot": agg["top3_sot"],
            "cont": agg["cont"], "big_pm": agg["big_pm"],
            "poss": agg["poss"], "opp_big_ag_pm": opp["big_ag_pm"],
            # G2 raw sums
            "S_in": agg["shots_in"], "S_out": agg["shots"] - agg["shots_in"],
            "N_in": agg["sot_in"], "N_out": agg["sot"] - agg["sot_in"],
            "S": agg["shots"],
            "lg_share_in": lg_share, "lg_rho_in": lg_rho_in,
            "lg_rho_out": lg_rho_out,
        }
    return out


def g2_ib_loc(comp, exp_shots):
    """Location-aware shots-implied SOT for one team from its trailing
    component dict. Falls back to None if league ratios are not yet
    defined (first matches of 2022/23)."""
    if comp["lg_rho_in"] is None or comp["lg_rho_out"] is None:
        return None
    share_in = (comp["S_in"] + G2_PRIOR * comp["lg_share_in"]) \
        / (comp["S"] + G2_PRIOR)
    ratio_in = (comp["N_in"] + G2_PRIOR * comp["lg_rho_in"]) \
        / (comp["S_in"] + G2_PRIOR)
    ratio_out = (comp["N_out"] + G2_PRIOR * comp["lg_rho_out"]) \
        / (comp["S_out"] + G2_PRIOR)
    return exp_shots * (share_in * ratio_in + (1 - share_in) * ratio_out)


# ------------------------------------------------------------- tuning pass
def pass_tune(matches, feats, extra):
    """Chronological pass over pre-test data. Records, for every
    2022/23 top-5 features match with the feature layer available, the
    v5 pieces and the raw trailing components (standardisation +
    grids are scored offline from these records)."""
    sot = Ratings(BASE_HL, BASE_K, "sot")
    shots = Ratings(BASE_HL, BASE_K, "shots", track_ratio=True)
    naive = NaiveTracker()
    reg = RegressionStore(matches, [FROZEN_LAM])
    fs = FeatureState(feats, extra)
    records = []
    n_tune_matches = n_unavail = 0
    for m in matches:
        if m["season"] in TEST_SEASONS:
            break
        if m["season"] == TUNE_SEASON and m["div"] in TOP5:
            key = (m["div"], m["date"], m["home"], m["away"])
            if key in feats:
                n_tune_matches += 1
                comp = team_components(fs, m)
                pieces = v5_pieces(sot, shots, naive, reg, m)
                if comp is None:
                    n_unavail += 1
                else:
                    records.append({
                        "div": m["div"], "total": m["hst"] + m["ast"],
                        "pieces": pieces, "comp": comp})
        update_model(sot, shots, naive, m)
        fs.update(m)
    return records, n_tune_matches, n_unavail


def component_stats(records):
    vals = {c: [] for c in COMPONENTS}
    for r in records:
        for tag in ("h", "a"):
            for c in COMPONENTS:
                v = r["comp"][tag][c]
                if v is not None:
                    vals[c].append(v)
    mu, sd = {}, {}
    for c in COMPONENTS:
        a = np.array(vals[c], dtype=float)
        mu[c] = float(a.mean()) if len(a) else 0.0
        s = float(a.std()) if len(a) else 0.0
        sd[c] = s if s > 1e-9 else 1.0
    return mu, sd


def z_of(comp, group, mu, sd):
    zs = []
    for c in GROUP_COMPONENTS[group]:
        v = comp[c]
        if v is not None:
            zs.append((v - mu[c]) / sd[c])
    return sum(zs) / len(zs) if zs else 0.0


def tune_grids(records, mu, sd, nb_r):
    """Score every group's grid on the recorded 2022/23 matches.
    Returns (tune_table, params, survivors)."""
    def ll_of(prob_fn):
        n, s = 0, 0.0
        for r in records:
            y = 1.0 if r["total"] > MAIN_LINE else 0.0
            s += logloss(prob_fn(r), y)
            n += 1
        return s / n if n else float("nan")

    def p_v5(r):
        p = r["pieces"]
        return 0.5 * nb_over(p["th"] + p["ta"], nb_r, MAIN_LINE) \
            + 0.5 * nb_over(p["lam_n_r"], nb_r, MAIN_LINE)

    base_ll = ll_of(p_v5)
    table = {"v5": base_ll}
    params = {}
    survivors = []

    for g in ("G1", "G3", "G4"):
        scored = {}
        for beta in BETA_GRID:
            def pf(r, beta=beta, g=g):
                p = r["pieces"]
                lam1 = math.exp(beta * z_of(r["comp"]["h"], g, mu, sd)) \
                    * p["th"] \
                    + math.exp(beta * z_of(r["comp"]["a"], g, mu, sd)) \
                    * p["ta"]
                return 0.5 * nb_over(lam1, nb_r, MAIN_LINE) \
                    + 0.5 * nb_over(p["lam_n_r"], nb_r, MAIN_LINE)
            scored[beta] = ll_of(pf)
        best = min(scored, key=lambda b: (scored[b], abs(b)))
        table[g] = scored
        params[g] = best
        if best != 0.0 and scored[best] < base_ll - 1e-9:
            survivors.append(g)

    scored_w = {}
    for w in W_GRID:
        def pf(r, w=w):
            p = r["pieces"]
            th, ta = p["th"], p["ta"]
            if w > 0.0:
                lh = g2_ib_loc(r["comp"]["h"], p["seh"])
                la = g2_ib_loc(r["comp"]["a"], p["sea"])
                if lh is not None:
                    th = 0.5 * (p["reh"] + (1 - w) * p["ib_h"] + w * lh)
                if la is not None:
                    ta = 0.5 * (p["rea"] + (1 - w) * p["ib_a"] + w * la)
            lam1 = th + ta
            return 0.5 * nb_over(lam1, nb_r, MAIN_LINE) \
                + 0.5 * nb_over(p["lam_n_r"], nb_r, MAIN_LINE)
        scored_w[w] = ll_of(pf)
    best_w = min(scored_w, key=lambda w: (scored_w[w], w))
    table["G2"] = scored_w
    params["G2"] = best_w
    if best_w != 0.0 and scored_w[best_w] < base_ll - 1e-9:
        survivors.append("G2")

    return table, params, sorted(survivors), base_ll


# ---------------------------------------------------------------- eval pass
def new_acc(lines):
    return {L: [0, 0.0, 0.0, 0.0, 0.0] for L in lines}


def add(acc, line, p, y):
    a = acc[line]
    a[0] += 1
    a[1] += (p - y) ** 2
    a[2] += logloss(p, y)
    a[3] += p
    a[4] += y


def stats(acc, L=MAIN_LINE):
    n, brier, ll, sp, sy = acc[L]
    return {"n": n, "brier": brier / n, "ll": ll / n,
            "calib": abs(sp - sy) / n * 100, "pred": 100 * sp / n,
            "act": 100 * sy / n}


VARIANTS = ["v5", "G1", "G2", "G3", "G4", "ALL"]


def variant_probs(pieces, comp, mu, sd, params, survivors, nb_r):
    """{variant: (p_line9.5, lam1)} for one same-set match. comp None
    -> every variant is plain v5 (counted fallback by the caller)."""
    th0, ta0 = pieces["th"], pieces["ta"]
    lam_n = pieces["lam_n_r"]

    def prob(lam1):
        return 0.5 * nb_over(lam1, nb_r, MAIN_LINE) \
            + 0.5 * nb_over(lam_n, nb_r, MAIN_LINE)

    out = {"v5": (prob(th0 + ta0), th0 + ta0)}
    if comp is None:
        for v in VARIANTS[1:]:
            out[v] = out["v5"]
        return out

    def adjusted(groups, use_g2_w):
        th, ta = th0, ta0
        if use_g2_w:
            w = params["G2"]
            lh = g2_ib_loc(comp["h"], pieces["seh"])
            la = g2_ib_loc(comp["a"], pieces["sea"])
            if lh is not None:
                th = 0.5 * (pieces["reh"] + (1 - w) * pieces["ib_h"]
                            + w * lh)
            if la is not None:
                ta = 0.5 * (pieces["rea"] + (1 - w) * pieces["ib_a"]
                            + w * la)
        e_h = e_a = 0.0
        for g in groups:
            e_h += params[g] * z_of(comp["h"], g, mu, sd)
            e_a += params[g] * z_of(comp["a"], g, mu, sd)
        return math.exp(e_h) * th + math.exp(e_a) * ta

    for g in ("G1", "G3", "G4"):
        lam1 = adjusted([g], False)
        out[g] = (prob(lam1), lam1)
    lam1 = adjusted([], True)
    out["G2"] = (prob(lam1), lam1)
    surv_adj = [g for g in survivors if g != "G2"]
    lam1 = adjusted(surv_adj, "G2" in survivors)
    out["ALL"] = (prob(lam1), lam1)
    return out


def pass_eval(matches, feats, extra, mu, sd, params, survivors, nb_r):
    sot = Ratings(BASE_HL, BASE_K, "sot")
    shots = Ratings(BASE_HL, BASE_K, "shots", track_ratio=True)
    naive = NaiveTracker()
    reg = RegressionStore(matches, [FROZEN_LAM])
    fs = FeatureState(feats, extra)

    full_v5 = new_acc(LINES)                       # v5, ALL test matches
    pooled = {v: new_acc(LINES) for v in VARIANTS}  # same set
    div_acc = {v: {d: new_acc([MAIN_LINE]) for d in TOP5} for v in VARIANTS}
    season_acc = {v: {s: new_acc([MAIN_LINE]) for s in TEST_SEASONS}
                  for v in VARIANTS}
    mae = {v: [0, 0.0] for v in ("v5", "ALL")}
    n_same = n_fallback = n_missing = n_top5_test = 0

    for m in matches:
        if m["season"] in TEST_SEASONS:
            total = m["hst"] + m["ast"]
            ys = {L: (1.0 if total > L else 0.0) for L in LINES}
            pieces = v5_pieces(sot, shots, naive, reg, m)
            p9 = 0.5 * nb_over(pieces["th"] + pieces["ta"], nb_r,
                               MAIN_LINE) \
                + 0.5 * nb_over(pieces["lam_n_r"], nb_r, MAIN_LINE)
            for L in LINES:
                pl = 0.5 * nb_over(pieces["th"] + pieces["ta"], nb_r, L) \
                    + 0.5 * nb_over(pieces["lam_n_r"], nb_r, L)
                add(full_v5, L, pl, ys[L])
            if m["div"] in TOP5:
                n_top5_test += 1
                key = (m["div"], m["date"], m["home"], m["away"])
                if key not in feats:
                    n_missing += 1
                else:
                    n_same += 1
                    comp = team_components(fs, m)
                    if comp is None:
                        n_fallback += 1
                    probs = variant_probs(pieces, comp, mu, sd, params,
                                          survivors, nb_r)
                    for v in VARIANTS:
                        pv, lam1 = probs[v]
                        add(pooled[v], MAIN_LINE, pv, ys[MAIN_LINE])
                        add(div_acc[v][m["div"]], MAIN_LINE, pv,
                            ys[MAIN_LINE])
                        add(season_acc[v][m["season"]], MAIN_LINE, pv,
                            ys[MAIN_LINE])
                        if v in mae:
                            mae[v][0] += 1
                            mae[v][1] += abs(lam1 - total)
                    # other lines for v5 + ALL on the same set
                    for v in ("v5", "ALL"):
                        lam1 = probs[v][1]
                        for L in LINES:
                            if L == MAIN_LINE:
                                continue
                            pl = 0.5 * nb_over(lam1, nb_r, L) \
                                + 0.5 * nb_over(pieces["lam_n_r"], nb_r, L)
                            add(pooled[v], L, pl, ys[L])
        update_model(sot, shots, naive, m)
        fs.update(m)

    return {"full_v5": full_v5, "pooled": pooled, "div": div_acc,
            "season": season_acc, "mae": mae, "n_same": n_same,
            "n_fallback": n_fallback, "n_missing": n_missing,
            "n_top5_test": n_top5_test}


# --------------------------------------------------------------------- gate
def evaluate_gate(ev):
    ref = stats(ev["pooled"]["v5"])
    res = {}
    for v in VARIANTS[1:]:
        sv = stats(ev["pooled"][v])
        deltas = {d: stats(ev["div"][v][d])["ll"]
                  - stats(ev["div"]["v5"][d])["ll"] for d in TOP5}
        worst = max(deltas.values())
        res[v] = {"ll": sv["ll"], "calib": sv["calib"],
                  "dll": sv["ll"] - ref["ll"],
                  "dcalib": sv["calib"] - ref["calib"],
                  "div_deltas": deltas, "worst_div": worst,
                  "beats_ll": sv["ll"] < ref["ll"],
                  "calib_ok": sv["calib"] - ref["calib"] <= 0.0,
                  "div_ok": worst <= 0.003}
        res[v]["adoptable"] = (res[v]["beats_ll"] and res[v]["calib_ok"]
                               and res[v]["div_ok"])
    return res


# --------------------------------------------------------------------- main
def main():
    t0 = time.time()
    matches = load_matches()
    feats = load_features()
    extra, from_cache = build_extra()

    # QC: store extraction vs the flat CSV (inside-box counts, SOT)
    qc = {"in": [0, 0], "sot": [0, 0]}
    for key, frow in feats.items():
        erow = extra.get(key)
        if erow is None:
            continue
        for s in ("h", "a"):
            if frow[s]["inside_box"] is not None:
                qc["in"][0] += 1
                qc["in"][1] += int(int(frow[s]["inside_box"])
                                   == erow[s]["shots_in"])
            if frow[s]["sot"] is not None:
                qc["sot"][0] += 1
                qc["sot"][1] += int(int(frow[s]["sot"]) == erow[s]["sot"])

    # coverage of the features file over the model's match universe
    n_joined = sum(1 for m in matches
                   if (m["div"], m["date"], m["home"], m["away"]) in feats)

    # v5's own warm-up: NB size estimated exactly as run_sot_v5 does
    _ll_r, _ll_bb, nb_r, _resid = pass_warmup(matches)

    records, n_tune_matches, n_tune_unavail = pass_tune(matches, feats,
                                                        extra)
    mu, sd = component_stats(records)
    tune_table, params, survivors, tune_base_ll = tune_grids(records, mu,
                                                             sd, nb_r)

    ev = pass_eval(matches, feats, extra, mu, sd, params, survivors, nb_r)
    runtime = time.time() - t0

    full = stats(ev["full_v5"])
    anchor_ok = abs(full["ll"] - REF_V5_LL) < 5e-4
    gate = evaluate_gate(ev) if anchor_ok else {}
    ref = stats(ev["pooled"]["v5"])

    write_report(matches, feats, nb_r, records, n_tune_matches,
                 n_tune_unavail, mu, sd, tune_table, params, survivors,
                 tune_base_ll, ev, full, anchor_ok, gate, runtime,
                 qc=qc, n_joined=n_joined, flag_cov=flag_coverage())

    print(f"NB r (v5 warm-up estimate): {nb_r:.2f}")
    print(f"tuning records: {len(records)} (2022/23 features matches "
          f"{n_tune_matches}, unavailable {n_tune_unavail})")
    print(f"tuned params: " + ", ".join(
        f"{g}={params[g]:g}" for g in GROUPS)
        + f" | survivors: {survivors or 'none'}")
    print(f"anchor v5 full-set LL: {full['ll']:.4f} vs {REF_V5_LL} -> "
          f"{'OK' if anchor_ok else 'MISMATCH — INVALID'}")
    print(f"same set: n={ev['n_same']} (fallback {ev['n_fallback']}, "
          f"missing from features {ev['n_missing']} of "
          f"{ev['n_top5_test']} top-5 test matches)")
    print(f"{'variant':10s} {'LL@9.5':>8s} {'calib':>6s} {'dLL':>8s} "
          f"{'dCalib':>7s} {'worstDiv':>9s}  gate")
    for v in VARIANTS:
        s = stats(ev["pooled"][v])
        if v == "v5":
            print(f"{v:10s} {s['ll']:8.4f} {s['calib']:5.1f}p")
        else:
            g = gate.get(v)
            print(f"{v:10s} {s['ll']:8.4f} {s['calib']:5.1f}p "
                  f"{g['dll']:+8.4f} {g['dcalib']:+6.1f}p "
                  f"{g['worst_div']:+9.4f}  "
                  f"{'ADOPTABLE' if g and g['adoptable'] else 'no'}")
    print(f"runtime: {runtime:.0f}s")
    print(f"wrote {OUT}")


def _fmt_grid(scored, param_name):
    items = sorted(scored.items(), key=lambda kv: abs(kv[0]))
    return ", ".join(f"{param_name}={k:g}: {v:.4f}" for k, v in items)


def write_report(matches, feats, nb_r, records, n_tune_matches,
                 n_tune_unavail, mu, sd, tune_table, params, survivors,
                 tune_base_ll, ev, full, anchor_ok, gate, runtime,
                 qc, n_joined, flag_cov):
    ref = stats(ev["pooled"]["v5"])
    out = []
    out.append("# Shots-on-Target (SOT) Model — v7: FotMob Shot/Lineup "
               "Features on v5")
    out.append("")
    # ------------------------------------------------ Indonesian summary
    out.append("## Ringkasan (Bahasa Indonesia)")
    out.append("")
    if not anchor_ok:
        out.append("**RUN TIDAK VALID** — referensi v5 tidak mereproduksi "
                   "angka patokannya (lihat di bawah), jadi tidak ada "
                   "kesimpulan yang boleh diambil dari putaran ini.")
    else:
        winners = [v for v in VARIANTS[1:] if gate[v]["adoptable"]]
        if winners:
            best = min(winners, key=lambda v: gate[v]["ll"])
            out.append(f"Putaran ini menguji empat grup fitur baru dari "
                       f"data FotMob (kualitas tembakan, rasio on-target "
                       f"per lokasi, konsentrasi penembak & kontinuitas "
                       f"lineup, statistik laga) di atas model produksi "
                       f"v5. Hasilnya: **{LABELS[best]} LOLOS gerbang** "
                       f"(log loss {gate[best]['ll']:.4f} vs v5 "
                       f"{ref['ll']:.4f} pada set laga yang sama, "
                       f"n={ref['n']:,}). Rincian per grup ada di tabel "
                       f"di bawah. Produksi TIDAK diubah — keputusan "
                       f"adopsi ada di tangan user.")
        else:
            parts = []
            for v in ("G1", "G2", "G3", "G4"):
                g = gate[v]
                if g["dll"] < -0.0005:
                    word = "membantu sedikit tapi gagal di kaki gerbang lain"
                elif g["dll"] > 0.0005:
                    word = "memperburuk"
                else:
                    word = "tidak berpengaruh nyata (noise)"
                parts.append(f"{v} {word} (ΔLL {g['dll']:+.4f})")
            out.append("Putaran ini menguji empat grup fitur baru dari "
                       "data FotMob di atas model produksi v5. Hasilnya: "
                       "**tidak ada grup yang lolos gerbang** — "
                       + "; ".join(parts)
                       + f". Kombinasi grup yang selamat dari penyetelan "
                       f"({', '.join(survivors) if survivors else 'tidak ada'}"
                       f") juga tidak lolos. **Produksi tetap v5, tidak "
                       f"diubah.** Angka patokan pada set yang sama: v5 "
                       f"log loss {ref['ll']:.4f}, kalibrasi "
                       f"{ref['calib']:.1f}pp (n={ref['n']:,}). Satu "
                       f"catatan data penting: uji G2 (dan satu komponen "
                       f"G1) memakai flag isFromInsideBox dari FotMob "
                       f"yang cakupannya tidak merata antar-musim "
                       f"(hampir kosong di 2022/23, penuh baru dari "
                       f"2024/25), jadi ide lokasi tembakannya belum "
                       f"teruji bersih — tindak lanjut yang wajar adalah "
                       f"membagi lokasi dari koordinat x/y tembakan, "
                       f"bukan dari flag itu.")
    out.append("")
    out.append("## Setup")
    out.append("")
    out.append("Script: `run_sot_v7.py` (re-runnable; reuses "
               "`run_sot_v2.py` data loading/ratings and "
               "`run_sot_v5.py`'s regression store / slim components "
               "unchanged). Reference: production v5 = slim + R + NB + "
               f"BB with ridge lam = {FROZEN_LAM:g} and BB prior "
               f"P = {FROZEN_P:g} (production's frozen constants) and "
               f"NB r = {nb_r:.2f} estimated in-pass by v5's own "
               "warm-up procedure (production froze 79.94).")
    out.append("")
    out.append(f"- Features file: {len(feats):,} matches (top-5, "
               f"seasons >= 2022/23); joined "
               f"{n_joined:,} of the model's match rows.")
    out.append(f"- Extra store extraction (location splits, shooter "
               f"shares, starter sets) cross-checked against the flat "
               f"CSV: inside-box counts agree on {qc['in'][1]:,}/"
               f"{qc['in'][0]:,} team-matches, SOT totals on "
               f"{qc['sot'][1]:,}/{qc['sot'][0]:,}.")
    out.append(f"- Same evaluation set: {ev['n_same']:,} top-5 test "
               f"matches present in the features file (of "
               f"{ev['n_top5_test']:,} top-5 test matches; "
               f"{ev['n_missing']} missing from the file). Feature "
               f"layer unavailable (fallback to plain v5, counted) "
               f"for {ev['n_fallback']} of them.")
    out.append(f"- Tuning set: {len(records):,} recorded 2022/23 "
               f"matches (of {n_tune_matches} top-5 features matches "
               f"that season; {n_tune_unavail} without enough trailing "
               f"history). Minimum trailing history: {MIN_HIST} "
               f"matches; window: last {WINDOW}.")
    out.append("")
    out.append("## Sanity anchor — v5 on the FULL standard test set")
    out.append("")
    out.append(f"v5 recomputed over all {full['n']:,} test matches "
               f"(2023/24–2025/26, all divisions): pooled line-9.5 log "
               f"loss **{full['ll']:.4f}** (RESULTS_V5.md: 0.6304), "
               f"Brier {full['brier']:.4f}, calib err "
               f"{full['calib']:.1f}pp → "
               f"**{'MATCH — run valid' if anchor_ok else 'MISMATCH — RUN INVALID'}**.")
    out.append("")
    out.append("## Frozen choices (2022/23 only)")
    out.append("")
    out.append(f"- v5 tuning-set log loss (line 9.5, recorded matches): "
               f"{tune_base_ll:.4f}.")
    for g in ("G1", "G3", "G4"):
        out.append(f"- {g} coefficient beta (grid over the tuning "
                   f"set): {_fmt_grid(tune_table[g], 'b')} → chosen "
                   f"**beta = {params[g]:g}**"
                   + (" (survivor)" if g in survivors else
                      " (not a survivor — no tuning gain)"))
    out.append(f"- G2 blend weight w: {_fmt_grid(tune_table['G2'], 'w')} "
               f"→ chosen **w = {params['G2']:g}**"
               + (" (survivor)" if "G2" in survivors else
                  " (not a survivor — no tuning gain)"))
    out.append("- Standardisation constants (mu/sd of trailing "
               "components, pooled over both teams at recorded "
               "2022/23 matches): "
               + ", ".join(f"{c} {mu[c]:.3f}/{sd[c]:.3f}"
                           for c in COMPONENTS) + ".")
    out.append("")
    out.append("## Headline — pooled line 9.5, same evaluation set")
    out.append("")
    out.append("| Variant | n | LogLoss | Brier | Calib err (pp) | "
               "ΔLL vs v5 | Δcalib (pp) | Worst div ΔLL | Gate |")
    out.append("|---|---|---|---|---|---|---|---|---|")
    for v in VARIANTS:
        s = stats(ev["pooled"][v])
        if v == "v5":
            out.append(f"| {LABELS[v]} | {s['n']:,} | {s['ll']:.4f} | "
                       f"{s['brier']:.4f} | {s['calib']:.1f} | — | — | "
                       f"— | reference |")
        else:
            g = gate.get(v)
            if g:
                out.append(f"| {LABELS[v]} | {s['n']:,} | {s['ll']:.4f} "
                           f"| {s['brier']:.4f} | {s['calib']:.1f} | "
                           f"{g['dll']:+.4f} | {g['dcalib']:+.1f} | "
                           f"{g['worst_div']:+.4f} | "
                           f"{'ADOPTABLE' if g['adoptable'] else 'no'} |")
            else:
                out.append(f"| {LABELS[v]} | {s['n']:,} | {s['ll']:.4f} "
                           f"| {s['brier']:.4f} | {s['calib']:.1f} | "
                           f"— | — | — | run invalid |")
    mae_v5 = ev["mae"]["v5"][1] / ev["mae"]["v5"][0]
    mae_all = ev["mae"]["ALL"][1] / ev["mae"]["ALL"][0]
    out.append("")
    out.append(f"MAE (same set): v5 {mae_v5:.2f}, combined "
               f"{mae_all:.2f}.")
    out.append("")
    out.append("## v5 vs combined at every line (same set)")
    out.append("")
    out.append("| Variant | 7.5 | 8.5 | 9.5 | 10.5 |")
    out.append("|---|---|---|---|---|")
    for v in ("v5", "ALL"):
        cells = " | ".join(f"{stats(ev['pooled'][v], L)['ll']:.4f}"
                           for L in LINES)
        out.append(f"| {LABELS[v]} | {cells} |")
    out.append("")
    out.append("## By division (top-5) — line 9.5 log loss, same set")
    out.append("")
    out.append("| Div | n | " + " | ".join(LABELS[v] for v in VARIANTS)
               + " |")
    out.append("|---|" + "---|" * (len(VARIANTS) + 1))
    for d in TOP5:
        cells = " | ".join(f"{stats(ev['div'][v][d])['ll']:.4f}"
                           for v in VARIANTS)
        out.append(f"| {d} | {stats(ev['div']['v5'][d])['n']:,} | "
                   f"{cells} |")
    out.append("")
    out.append("## Combined by season — line 9.5 (v5 alongside)")
    out.append("")
    out.append("| Season | n | Combined LogLoss | Combined calib (pp) "
               "| v5 LogLoss |")
    out.append("|---|---|---|---|---|")
    for sname in TEST_SEASONS:
        sa = stats(ev["season"]["ALL"][sname])
        sb = stats(ev["season"]["v5"][sname])
        out.append(f"| {sname} | {sa['n']:,} | {sa['ll']:.4f} | "
                   f"{sa['calib']:.1f} | {sb['ll']:.4f} |")
    out.append("")
    out.append("## Gate verdict")
    out.append("")
    if not anchor_ok:
        out.append("**RUN INVALID** — the v5 anchor did not reproduce; "
                   "no gate was evaluated and nothing may be adopted "
                   "from this run.")
    else:
        for v in VARIANTS[1:]:
            g = gate[v]
            out.append(f"- {LABELS[v]}: ΔLL {g['dll']:+.4f} (must be "
                       f"< 0: {'ok' if g['beats_ll'] else 'NO'}); "
                       f"calib {g['calib']:.1f}pp, Δcalib "
                       f"{g['dcalib']:+.1f}pp (must be <= 0: "
                       f"{'ok' if g['calib_ok'] else 'NO'}); worst "
                       f"top-5 division ΔLL {g['worst_div']:+.4f} "
                       f"(limit +0.003: {'ok' if g['div_ok'] else 'NO'}) "
                       f"→ **{'ADOPTABLE' if g['adoptable'] else 'not adoptable'}**.")
        adoptable = [v for v in VARIANTS[1:] if gate[v]["adoptable"]]
        if adoptable:
            best = min(adoptable, key=lambda v: gate[v]["ll"])
            out.append(f"- **Adopt-worthy: {LABELS[best]}** — the "
                       f"report carries this verdict; production "
                       f"changes only on the user's decision.")
        else:
            out.append("- **No variant is adopt-worthy — production "
                       "stays on v5 unchanged.**")
    out.append("")
    out.append("## Data caveat — isFromInsideBox feed coverage")
    out.append("")
    out.append("The inside-box flag behind the CSV's `inside_box` "
               "column (and therefore behind G1's inside-share "
               "component and ALL of G2's location split) is not "
               "populated uniformly over time. Share of shots flagged "
               "inside the box, by season: "
               + ", ".join(f"{s}: {v:.1%}" for s, v in flag_cov)
               + ". A real inside-box share is ~65% (the level seen "
               "once the flag is fully populated, 2024/25 on); in "
               "2022/23 — the tuning season — the flag is essentially "
               "absent, and 2023/24 is transitional. Consequences: "
               "(i) G2's verdict is CONFOUNDED — the location idea "
               "was tuned and partly tested on a missingness pattern, "
               "not on football; a coordinate-based split (shot x/y "
               "are populated for nearly every shot) is the clean "
               "follow-up test, as its own pre-registered round. "
               "(ii) G1 carries the same contamination in one of its "
               "five components; its other four (xG/shot, xGOT/shot, "
               "deep share, blocked share) do not use the flag. "
               "(iii) G3 and G4 do not use the flag at all — their "
               "reads are clean.")
    out.append("")
    out.append("## Method notes and caveats")
    out.append("")
    out.append("- Integration is a machine change, not a slice patch: "
               "G1/G3/G4 multiply each team's v5 blended expectation "
               "by exp(beta * z) with ONE tuned coefficient per group "
               "(z = mean of standardised trailing components); G2 "
               "rebuilds the ratio stage with location-specific "
               "on-target ratios and blends it with the BB ratio at "
               "the tuned weight. The naive ensemble member and the "
               "NB size are never touched.")
    out.append("- Trailing pools are venue-first (last 10 at the same "
               "venue when >= 5 exist, else last 10 overall when >= 5 "
               "exist). Feature state updates in the same sequential "
               "match order as the ratings machinery, including its "
               "within-day ordering — parity with the house "
               "walk-forward discipline, documented rather than "
               "hidden.")
    out.append("- G2/G3 raw material (location splits, shooter "
               "shares, starter identities) is extracted from the "
               "FotMob store JSONs because the flat features CSV "
               "carries only starter counts; counting rules mirror "
               "the CSV extractor exactly (QC above). The cache is "
               "`v7_extra_features.csv` next to this script.")
    out.append("- G1 uses the attack side only (a team's own shot "
               "quality); the opponent's conceded quality is not "
               "modelled — the ratings/defence terms already carry "
               "opponent strength. G4 does use the opponent's "
               "trailing big-chances-conceded, which is a matchup "
               "property, not a slice correction.")
    out.append("- Post-match fields in the features file "
               "(team_rating, same-match unavailable counts, the "
               "match's own stats) are never used; lineup continuity "
               "uses only starter sets of strictly earlier matches.")
    out.append("- Fallback matches (feature layer unavailable) are "
               "scored as plain v5 for every variant, so all variants "
               "share one n and the comparison is apples-to-apples; "
               "the dilution is symmetric.")
    out.append("- No odds anywhere: predictive accuracy/calibration "
               "only, not betting value (no SOT odds in our data).")
    out.append(f"- Script runtime (this run, incl. data load and "
               f"store extraction): {runtime:.0f}s.")

    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write("\n".join(out) + "\n")


if __name__ == "__main__":
    main()
