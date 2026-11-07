#!/usr/bin/env python3
"""Audit model non-SOT vs gudang data FotMob (2026-11-07).

Read-only terhadap produksi: hanya membaca artefak (records_cache,
predictions_corners_shots.csv, ledger), file gudang (shot_lineup_features,
fotmob_full_index, v7_extra_features), dan spine all_matches_clean.csv.
Output: /tmp/audit_results.json — semua angka di MODEL_AUDIT_2026-11-07.md
berasal dari file ini.
"""
import csv
import glob
import json
import math
import os
import random
import sys
from collections import defaultdict

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE)
from football_etl import normalize_name  # noqa: E402

TOP5 = ["E0", "SP1", "D1", "I1", "F1"]
R = {}


def parse_date(s):
    s = (s or "").strip()
    if "-" in s and len(s) == 10:
        return s
    if "/" in s:
        d, m, y = s.split("/")
        return f"{y}-{m}-{d}"
    return s


def key_of(div, date, home, away):
    return (div, parse_date(date), normalize_name(home), normalize_name(away))


def fl(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def ll(p, y):
    p = min(max(p, 1e-9), 1 - 1e-9)
    return -(y * math.log(p) + (1 - y) * math.log(1 - p))


# ---------------------------------------------------------------- spine
spine = {}
with open(os.path.join(BASE, "all_matches_clean.csv"), newline="") as f:
    for row in csv.DictReader(f):
        spine[key_of(row["Div"], row["Date"], row["HomeTeam"], row["AwayTeam"])] = row

# ---------------------------------------------------------------- features
feats = {}
feat_rows = []
with open(os.path.join(BASE, "data_enrichment/shot_lineup_features.csv"), newline="") as f:
    for row in csv.DictReader(f):
        k = key_of(row["div"], row["date"], row["home"], row["away"])
        feats[k] = row
        feat_rows.append((k, row))

# team-match long table from features (for trailing aggregates)
team_matches = defaultdict(list)  # (div, norm team) -> list of dicts
for k, row in feat_rows:
    div, date, hn, an = k
    for side, tn, opp in (("h", hn, an), ("a", an, hn)):
        os_ = "a" if side == "h" else "h"
        vals = [fl(row[f"xg_{side}"]), fl(row[f"xg_{os_}"]), fl(row[f"sot_{side}"]),
                fl(row[f"possession_{side}"]), fl(row[f"possession_{os_}"]),
                fl(row[f"big_chances_{side}"]), fl(row[f"big_chances_{os_}"])]
        if any(v is None for v in vals):
            continue
        team_matches[(div, tn)].append({
            "date": date, "key": k, "team": tn, "opp": opp, "venue": side,
            "xg_f": vals[0], "xg_a": vals[1], "sot_f": vals[2],
            "poss_f": vals[3], "poss_a": vals[4], "bc_f": vals[5], "bc_a": vals[6],
        })
for v in team_matches.values():
    v.sort(key=lambda d: d["date"])


def trailing(team_key, date, field_f, field_a=None, n=10):
    """Mean of (field_f - field_a) over the team's last n matches before date."""
    rows = [d for d in team_matches.get(team_key, []) if d["date"] < date]
    if len(rows) < 5:
        return None
    rows = rows[-n:]
    if field_a:
        return sum(d[field_f] - d[field_a] for d in rows) / len(rows)
    return sum(d[field_f] for d in rows) / len(rows)


# ================================================================ CORNERS
# 1) FotMob corner totals vs football-data (independent source agreement)
agree = {"n": 0, "exact": 0, "mae_h": 0.0, "mae_a": 0.0, "mae_t": 0.0,
         "by_div": defaultdict(lambda: [0, 0, 0.0])}
for k, row in feat_rows:
    s = spine.get(k)
    if not s or s["HC"] in ("", None) or s["AC"] in ("", None):
        continue
    fh, fa = fl(row["corners_h"]), fl(row["corners_a"])
    if fh is None or fa is None:
        continue
    sh, sa = float(s["HC"]), float(s["AC"])
    agree["n"] += 1
    agree["exact"] += 1 if (fh == sh and fa == sa) else 0
    agree["mae_h"] += abs(fh - sh)
    agree["mae_a"] += abs(fa - sa)
    agree["mae_t"] += abs((fh + fa) - (sh + sa))
    b = agree["by_div"][k[0]]
    b[0] += 1
    b[1] += 1 if (fh == sh and fa == sa) else 0
    b[2] += abs((fh + fa) - (sh + sa))
n = agree["n"]
R["corners_cross_source"] = {
    "n": n, "exact_pct": round(100 * agree["exact"] / n, 1),
    "mae_home": round(agree["mae_h"] / n, 3), "mae_away": round(agree["mae_a"] / n, 3),
    "mae_total": round(agree["mae_t"] / n, 3),
    "by_div": {d: {"n": v[0], "exact_pct": round(100 * v[1] / v[0], 1),
                   "mae_total": round(v[2] / v[0], 3)} for d, v in agree["by_div"].items()},
}

# 2) corner backtest artifact: calibration + LL, CS vs CB
bt = []
with open(os.path.join(BASE, "predictions_corners_shots.csv"), newline="") as f:
    for row in csv.DictReader(f):
        bt.append(row)


def line_metrics(rows, pcol, line):
    tot_ll = 0.0
    pred = 0.0
    act = 0.0
    for r in rows:
        y = 1.0 if float(r["y_total"]) > line else 0.0
        tot_ll += ll(float(r[pcol]), y)
        pred += float(r[pcol])
        act += y
    return {"n": len(rows), "ll": round(tot_ll / len(rows), 4),
            "pred_rate": round(pred / len(rows), 4), "act_rate": round(act / len(rows), 4),
            "diff_pp": round(100 * (pred - act) / len(rows), 2)}


cm = {"all": {}, "by_season": {}}
for line, col in ((8.5, "p_gt_cs_8.5"), (9.5, "p_gt_cs_9.5"), (10.5, "p_gt_cs_10.5")):
    cm["all"][str(line)] = line_metrics(bt, col, line)
cm["all"]["9.5_cb"] = line_metrics(bt, "p_gt_cb_9.5", 9.5)
for s in sorted({r["season"] for r in bt}):
    rows = [r for r in bt if r["season"] == s]
    cm["by_season"][s] = line_metrics(rows, "p_gt_cs_9.5", 9.5)
cm["n"] = len(bt)
R["corner_backtest"] = cm

# 3) corner residuals (y - mu_cs) by NEW trailing warehouse cuts (test >= 2023/24)
resid_buckets = defaultdict(lambda: [0, 0.0])
for r in bt:
    if r["season"] not in ("2023/24", "2024/25", "2025/26"):
        continue
    k = key_of(r["div"], r["date"], r["home"], r["away"])
    if k not in feats:
        continue
    div, date, hn, an = k
    poss_d = None
    ph = trailing((div, hn), date, "poss_f", "poss_a")
    pa = trailing((div, an), date, "poss_f", "poss_a")
    if ph is not None and pa is not None:
        poss_d = ph - pa
    bc_h = trailing((div, hn), date, "bc_f", "bc_a")
    bc_a = trailing((div, an), date, "bc_f", "bc_a")
    bc_d = None if (bc_h is None or bc_a is None) else bc_h - bc_a
    res = float(r["y_total"]) - float(r["mu_shots_cs"])
    for name, val, edges in (("poss_diff", poss_d, (-8, -3, 3, 8)),
                             ("bigchance_diff", bc_d, (-1.5, -0.5, 0.5, 1.5))):
        if val is None:
            continue
        b = 0
        while b < len(edges) and val >= edges[b]:
            b += 1
        cell = resid_buckets[(name, b)]
        cell[0] += 1
        cell[1] += res
R["corner_resid_new_cuts"] = {
    f"{name}|bucket{b}": {"n": v[0], "mean_resid": round(v[1] / v[0], 3)}
    for (name, b), v in sorted(resid_buckets.items()) if v[0] >= 100
}

# 4) corner calibration vs FotMob actuals on the overlap (source swap)
swap = []
for r in bt:
    if r["season"] not in ("2022/23", "2023/24", "2024/25", "2025/26"):
        continue
    k = key_of(r["div"], r["date"], r["home"], r["away"])
    fr = feats.get(k)
    if not fr:
        continue
    ch_, ca_ = fl(fr["corners_h"]), fl(fr["corners_a"])
    if ch_ is None or ca_ is None:
        continue
    y_fm = ch_ + ca_
    swap.append({"p": float(r["p_gt_cs_9.5"]), "y_fd": 1.0 if float(r["y_total"]) > 9.5 else 0.0,
                 "y_fm": 1.0 if y_fm > 9.5 else 0.0})
if swap:
    R["corner_source_swap"] = {
        "n": len(swap),
        "pred_rate": round(sum(x["p"] for x in swap) / len(swap), 4),
        "act_rate_fd": round(sum(x["y_fd"] for x in swap) / len(swap), 4),
        "act_rate_fotmob": round(sum(x["y_fm"] for x in swap) / len(swap), 4),
        "ll_fd": round(sum(ll(x["p"], x["y_fd"]) for x in swap) / len(swap), 4),
        "ll_fotmob": round(sum(ll(x["p"], x["y_fm"]) for x in swap) / len(swap), 4),
    }

# ================================================================ GOALS
records = []
with open(os.path.join(BASE, "records_cache.jsonl")) as f:
    for line in f:
        records.append(json.loads(line))

TEST_S = {"2023/24", "2024/25", "2025/26"}
g = [r for r in records if r["div"] in TOP5 and r["season"] in TEST_S]


def ll_1x2(r):
    p = [r["ph_dc"], r["pd_dc"], r["pa_dc"]][r["yi"]]
    return -math.log(max(p, 1e-9))


def btts_y(r):
    return 1.0 if (r["fthg"] > 0 and r["ftag"] > 0) else 0.0


def over_y(r):
    return 1.0 if (r["fthg"] + r["ftag"]) > 2.5 else 0.0


R["goals_overall"] = {
    "n": len(g),
    "ll_1x2_dc": round(sum(ll_1x2(r) for r in g) / len(g), 4),
    "ll_btts": round(sum(ll(r["p_btts"], btts_y(r)) for r in g) / len(g), 4),
    "ll_ou25": round(sum(ll(r["p_over_dc"], over_y(r)) for r in g) / len(g), 4),
    "btts_pred": round(sum(r["p_btts"] for r in g) / len(g), 4),
    "btts_act": round(sum(btts_y(r) for r in g) / len(g), 4),
    "ou_pred": round(sum(r["p_over_dc"] for r in g) / len(g), 4),
    "ou_act": round(sum(over_y(r) for r in g) / len(g), 4),
}

# lineup continuity per team-match from v7 extra features (starter id sets)
extra = {}
with open(os.path.join(BASE, "experiments/sot_model/v7_extra_features.csv"), newline="") as f:
    for row in csv.DictReader(f):
        extra[key_of(row["div"], row["date"], row["home"], row["away"])] = row
team_starters = defaultdict(list)
for k, row in extra.items():
    div, date, hn, an = k
    for side, tn in (("h", hn), ("a", an)):
        ids = [x for x in row[f"starters_{side}"].split(";") if x]
        team_starters[(div, tn)].append((date, set(ids), k))
continuity = {}  # (match key, side) -> share of this XI that also started prev match
for tk, lst in team_starters.items():
    lst.sort(key=lambda d: d[0])
    prev = None
    for date, ids, k in lst:
        if prev:
            continuity[(k, tk[1])] = len(ids & prev) / max(len(ids), 1)
        prev = ids

cont_rows = []
for r in g:
    k = (r["div"], r["date"], r["home"], r["away"])
    ch = continuity.get((k, r["home"]))
    ca = continuity.get((k, r["away"]))
    if ch is None or ca is None:
        continue
    cont_rows.append((r, (ch + ca) / 2))
cont_rows.sort(key=lambda t: t[1])
third = len(cont_rows) // 3
slices = {}
for name, part in (("low", cont_rows[:third]), ("mid", cont_rows[third:2 * third]),
                   ("high", cont_rows[2 * third:])):
    if part:
        slices[name] = {
            "n": len(part),
            "cont_mean": round(sum(t[1] for t in part) / len(part), 3),
            "ll_1x2_dc": round(sum(ll_1x2(t[0]) for t in part) / len(part), 4),
        }
R["goals_by_continuity"] = {"n_matched": len(cont_rows), "slices": slices}

# BTTS calibration by HT state (mechanism diagnosis; HT state is post-hoc)
ht = defaultdict(lambda: [0, 0.0, 0.0])
for r in g:
    s = spine.get((r["div"], r["date"], r["home"], r["away"]))
    if not s or s["HTHG"] in ("", None):
        continue
    state = "home_leading" if int(s["HTHG"]) > int(s["HTAG"]) else \
        "level" if int(s["HTHG"]) == int(s["HTAG"]) else "away_leading"
    c = ht[state]
    c[0] += 1
    c[1] += r["p_btts"]
    c[2] += btts_y(r)
R["goals_btts_by_htstate"] = {
    k: {"n": v[0], "pred": round(v[1] / v[0], 4), "act": round(v[2] / v[0], 4),
        "diff_pp": round(100 * (v[1] - v[2]) / v[0], 2)} for k, v in ht.items()
}

# OU 2.5 log loss by trailing xG-differential bucket (warehouse-only cut)
ou_rows = []
for r in g:
    xh = trailing((r["div"], r["home"]), r["date"], "xg_f", "xg_a")
    xa = trailing((r["div"], r["away"]), r["date"], "xg_f", "xg_a")
    if xh is None or xa is None:
        continue
    ou_rows.append((r, xh - xa))
ou_rows.sort(key=lambda t: t[1])
third = len(ou_rows) // 3
ou_slices = {}
for name, part in (("away_xg_edge", ou_rows[:third]), ("balanced", ou_rows[third:2 * third]),
                   ("home_xg_edge", ou_rows[2 * third:])):
    if part:
        ou_slices[name] = {
            "n": len(part),
            "diff_mean": round(sum(t[1] for t in part) / len(part), 3),
            "ll_ou25": round(sum(ll(t[0]["p_over_dc"], over_y(t[0])) for t in part) / len(part), 4),
        }
R["goals_ou_by_trail_xgdiff"] = {"n_matched": len(ou_rows), "slices": ou_slices}

# ================================================================ CARDS
cov = defaultdict(lambda: [0, 0, 0])
for row in spine.values():
    if row["Div"] not in TOP5 or row["Season"] < "2017/18":
        continue
    c = cov[row["Season"]]
    c[0] += 1
    if row["HY"] not in ("", None) and row["AY"] not in ("", None):
        c[1] += 1
    if row.get("Referee"):
        c[2] += 1
R["cards_coverage_clean"] = {
    s: {"n": v[0], "cards_pct": round(100 * v[1] / v[0], 1),
        "ref_pct": round(100 * v[2] / v[0], 1)} for s, v in sorted(cov.items())
}

win = [row for row in spine.values()
       if row["Div"] in TOP5 and row["Season"] in
       ("2022/23", "2023/24", "2024/25", "2025/26") and row["HY"] not in ("", None)]
ty = [int(r["HY"]) + int(r["AY"]) for r in win]
tc = [int(r["HY"]) + int(r["AY"]) + int(r["HR"]) + int(r["AR"]) for r in win]
mean_ty = sum(ty) / len(ty)
var_ty = sum((x - mean_ty) ** 2 for x in ty) / len(ty)
by_div_cards = {}
for d in TOP5:
    vals = [int(r["HY"]) + int(r["AY"]) for r in win if r["Div"] == d]
    if vals:
        by_div_cards[d] = {"n": len(vals), "mean_yellows": round(sum(vals) / len(vals), 2)}
ref_map = defaultdict(list)
for r in win:
    if r.get("Referee"):
        ref_map[r["Referee"]].append(int(r["HY"]) + int(r["AY"]))
big_refs = {k: v for k, v in ref_map.items() if len(v) >= 40}
ref_means = [sum(v) / len(v) for v in big_refs.values()]
grand = sum(ref_means) / len(ref_means)
between = sum((m - grand) ** 2 for m in ref_means) / len(ref_means)
within_expected = sum(mean_ty / len(v) for v in big_refs.values()) / len(big_refs)
R["cards_baseline"] = {
    "n": len(win), "mean_yellows": round(mean_ty, 3),
    "var_mean_ratio_yellows": round(var_ty / mean_ty, 3),
    "mean_cards_y_plus_r": round(sum(tc) / len(tc), 3),
    "by_div": by_div_cards,
    "refs_ge40": len(big_refs),
    "ref_between_var": round(between, 4),
    "ref_sampling_var_expected": round(within_expected, 4),
    "ref_true_var_est": round(max(between - within_expected, 0.0), 4),
}

# FotMob discipline vs clean file (independent cross-check)
dc = {"n": 0, "y_exact": 0, "r_exact": 0, "f_exact": 0}
for k, row in feat_rows:
    s = spine.get(k)
    if not s or s["HY"] in ("", None):
        continue
    yv = [fl(row["yellow_h"]), fl(row["yellow_a"]), fl(row["red_h"]), fl(row["red_a"]),
          fl(row["fouls_h"]), fl(row["fouls_a"])]
    if any(v is None for v in yv):
        continue
    dc["n"] += 1
    dc["y_exact"] += 1 if (yv[0] == float(s["HY"]) and yv[1] == float(s["AY"])) else 0
    dc["r_exact"] += 1 if (yv[2] == float(s["HR"]) and yv[3] == float(s["AR"])) else 0
    dc["f_exact"] += 1 if (yv[4] == float(s["HF"]) and yv[5] == float(s["AF"])) else 0
R["cards_cross_source"] = {
    "n": dc["n"],
    "yellow_exact_pct": round(100 * dc["y_exact"] / dc["n"], 1),
    "red_exact_pct": round(100 * dc["r_exact"] / dc["n"], 1),
    "fouls_exact_pct": round(100 * dc["f_exact"] / dc["n"], 1),
}

# ================================================================ STORE PROBE
random.seed(20261107)
idx_paths = []
with open(os.path.join(BASE, "data_enrichment/fotmob_full_index.csv"), newline="") as f:
    for row in csv.DictReader(f):
        idx_paths.append((row["div"], row["season"], row["path"]))
by_group = defaultdict(list)
for d, s, p in idx_paths:
    by_group[(d, s)].append(p)
probe = {}
for (d, s), paths in sorted(by_group.items()):
    sample = random.sample(paths, min(12, len(paths)))
    per = {"n": 0, "has_periods": 0, "has_1h_corners": 0, "has_1h_yellow": 0}
    for p in sample:
        try:
            doc = json.load(open(os.path.join(BASE, p)))
        except Exception:
            continue
        per["n"] += 1
        periods = ((doc.get("content", {}).get("stats") or {}).get("Periods") or {})
        fh = periods.get("FirstHalf") or {}
        if fh:
            per["has_periods"] += 1
            names = set()
            for grp in fh.get("stats", []):
                for st in grp.get("stats", []):
                    nm = st.get("name") or st.get("title")
                    if nm:
                        names.add(nm)
            if "Corners" in names:
                per["has_1h_corners"] += 1
            if "Yellow cards" in names:
                per["has_1h_yellow"] += 1
    if per["n"]:
        probe[f"{d} {s}"] = per
R["store_probe_periods"] = probe

with open("/tmp/audit_results.json", "w") as f:
    json.dump(R, f, indent=1, default=str)
print(json.dumps(R, indent=1, default=str))
