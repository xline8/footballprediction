"""Phase 3 EDA computations for the J.League corpus.

Prints a full digest and writes eda_summary.json. Reliability checks use
the halves-audit standard: a pattern is a signal candidate only if the
same trait measured on disjoint halves of the same teams' matches
correlates with itself (split-half), and era/within claims are checked
against plain sampling noise.
"""
import csv
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from jleague_lib import events_of, goal_events, iter_files, load

DATA = Path(__file__).parent / "data"
OUT = Path(__file__).parent / "eda_summary.json"
rng = np.random.default_rng(20261109)


def load_csv(name):
    with open(DATA / name) as f:
        return list(csv.DictReader(f))


def num(rows, k):
    return np.array([np.nan if r[k] == "" else float(r[k]) for r in rows])


def b2(rows, k):
    return np.array([r[k] == "True" for r in rows])


def desc(x):
    x = x[~np.isnan(x)]
    if len(x) == 0:
        return {}
    return {"n": int(len(x)), "mean": round(float(x.mean()), 3),
            "sd": round(float(x.std()), 3),
            "var_over_mean": round(float(x.var() / x.mean()), 3) if x.mean() else None,
            "p10": round(float(np.percentile(x, 10)), 2),
            "p50": round(float(np.percentile(x, 50)), 2),
            "p90": round(float(np.percentile(x, 90)), 2)}


def split_half(trait_by_team, min_matches=24, reps=60):
    """trait_by_team: {team: 1d array of per-match values}. Splits each
    team's matches into two halves (odd/even by date + random reps),
    correlates the per-team means across teams. Returns (n_teams, r)."""
    teams = {t: v for t, v in trait_by_team.items() if len(v) >= min_matches}
    if len(teams) < 8:
        return len(teams), None
    rs = []
    for rep in range(reps):
        a, b = [], []
        for v in teams.values():
            idx = np.arange(len(v))
            if rep == 0:
                mask = idx % 2 == 0
            else:
                mask = rng.random(len(v)) < 0.5
                if mask.sum() == 0 or (~mask).sum() == 0:
                    continue
            a.append(v[mask].mean()); b.append(v[~mask].mean())
        if len(a) >= 8 and np.std(a) > 0 and np.std(b) > 0:
            rs.append(np.corrcoef(a, b)[0, 1])
    return len(teams), (round(float(np.mean(rs)), 3) if rs else None)


def split_half_ratio(num_by_team, den_by_team, min_matches=24, reps=60):
    """Split-half for ratio traits (ratio of sums, not mean of ratios)."""
    teams = [t for t in num_by_team if len(num_by_team[t]) >= min_matches]
    if len(teams) < 8:
        return len(teams), None
    rs = []
    for rep in range(reps):
        a, b = [], []
        ok = True
        for t in teams:
            n, d = num_by_team[t], den_by_team[t]
            idx = np.arange(len(n))
            mask = idx % 2 == 0 if rep == 0 else rng.random(len(n)) < 0.5
            if mask.sum() == 0 or (~mask).sum() == 0 or d[mask].sum() == 0 or d[~mask].sum() == 0:
                ok = False; break
            a.append(n[mask].sum() / d[mask].sum()); b.append(n[~mask].sum() / d[~mask].sum())
        if ok and np.std(a) > 0 and np.std(b) > 0:
            rs.append(np.corrcoef(a, b)[0, 1])
    return len(teams), (round(float(np.mean(rs)), 3) if rs else None)


S = {}

# ---------- A. levels per league ----------
S["levels"] = {}
for lg in ("j1", "j2", "j3"):
    m = load_csv(f"{lg}_matches.csv")
    hg, ag = num(m, "home_goals"), num(m, "away_goals")
    tot = hg + ag
    lev = {
        "matches": len(m),
        "goals_total": desc(tot), "goals_home": desc(hg), "goals_away": desc(ag),
        "home_win_pct": round(float(np.mean(hg > ag)) * 100, 1),
        "draw_pct": round(float(np.mean(hg == ag)) * 100, 1),
        "away_win_pct": round(float(np.mean(hg < ag)) * 100, 1),
        "btts_pct": round(float(np.mean((hg > 0) & (ag > 0))) * 100, 1),
        "over25_pct": round(float(np.mean(tot > 2.5)) * 100, 1),
        "home_goal_edge": round(float((hg - ag).mean()), 3),
    }
    for key, cols in (("sot", ("ShotsOnTarget_home", "ShotsOnTarget_away")),
                      ("shots", ("total_shots_home", "total_shots_away")),
                      ("corners", ("corners_home", "corners_away")),
                      ("yellow", ("yellow_home", "yellow_away")),
                      ("red", ("red_home", "red_away")),
                      ("xg", ("expected_goals_home", "expected_goals_away"))):
        x = num(m, cols[0]) + num(m, cols[1])
        lev[key] = desc(x)
    S["levels"][lg] = lev

# ---------- B. era drift (per league-season) ----------
S["seasons"] = {}
for lg in ("j1", "j2", "j3"):
    m = load_csv(f"{lg}_matches.csv")
    per = {}
    for season in sorted({r["season"] for r in m}):
        rows = [r for r in m if r["season"] == season]
        hg, ag = num(rows, "home_goals"), num(rows, "away_goals")
        entry = {"n": len(rows), "goals": round(float((hg + ag).mean()), 2),
                 "home_edge": round(float((hg - ag).mean()), 2),
                 "draw_pct": round(float(np.mean(hg == ag)) * 100, 1)}
        for key, cols in (("sot", ("ShotsOnTarget_home", "ShotsOnTarget_away")),
                          ("shots", ("total_shots_home", "total_shots_away")),
                          ("corners", ("corners_home", "corners_away")),
                          ("yellow", ("yellow_home", "yellow_away")),
                          ("xg", ("expected_goals_home", "expected_goals_away"))):
            x = num(rows, cols[0]) + num(rows, cols[1])
            x = x[~np.isnan(x)]
            entry[key] = round(float(x.mean()), 2) if len(x) >= 30 else None
            entry[key + "_n"] = int(len(x))
        per[season] = entry
    S["seasons"][lg] = per

# ---------- C. halves: levels + team-trait reliability (J1) ----------
j1t = load_csv("j1_team_matches.csv")
S["halves_j1"] = {}
tm = load_csv("j1_matches.csv")
ht_tot = num(tm, "ht_home_goals") + num(tm, "ht_away_goals")
ft_tot = num(tm, "home_goals") + num(tm, "away_goals")
share = ht_tot / np.where(ft_tot > 0, ft_tot, np.nan)
S["halves_j1"]["goal_share_1h"] = desc(share)
# true-variance decomposition of the per-match share (audit method):
# observed var vs binomial noise floor given each match's FT total
p = np.nanmean(share)
excess = np.nanvar(share) - np.nanmean(p * (1 - p) / np.where(ft_tot > 0, ft_tot, np.nan))
S["halves_j1"]["goal_share_true_var"] = round(float(excess), 5)

def trait_map(rows, col, league_filter=None):
    d = defaultdict(list)
    for r in rows:
        v = r[col]
        if v != "":
            d[r["team_id"]].append(float(v))
    return {t: np.array(v) for t, v in d.items()}

def ratio_map(rows, ncol, dcol):
    n, d = defaultdict(list), defaultdict(list)
    for r in rows:
        if r[ncol] != "" and r[dcol] != "":
            n[r["team_id"]].append(float(r[ncol])); d[r["team_id"]].append(float(r[dcol]))
    return ({t: np.array(v) for t, v in n.items()}, {t: np.array(v) for t, v in d.items()})

# team 1H goal share reliability: share per match undefined for 0-goal
# matches -> use ratio-of-sums split-half on ht goals vs ft goals
rows = [r for r in j1t]
n_map, d_map = ratio_map(rows, "ht_goals_for", "goals_for")
# only teams whose matches all have HT (J1 events complete) -- guaranteed
nt, r = split_half_ratio(n_map, d_map, min_matches=24)
S["halves_j1"]["team_1h_goal_share_split_half"] = {"n_teams": nt, "r": r}
for trait, col in (("fh_corners_share", None), ("fh_sot_share", None),
                   ("fh_shots_share", None)):
    pass
half_rows = [r for r in j1t if r["has_stats_half"] == "True"]
for name, n_col, d_col in (("team_1h_corner_share", "fh_corners_for", "corners_for"),
                           ("team_1h_sot_share", "fh_sot_for", "sot_for"),
                           ("team_1h_shots_share", "fh_shots_for", "shots_for"),
                           ("team_1h_xg_share", "fh_xg_for", "xg_for")):
    n_map, d_map = ratio_map(half_rows, n_col, d_col)
    nt, r = split_half_ratio(n_map, d_map, min_matches=24)
    S["halves_j1"][name + "_split_half"] = {"n_teams": nt, "r": r}

# ---------- D. reliability battery: team traits ----------
S["reliability"] = {}
for lg, tfile in (("j1", "j1_team_matches.csv"), ("j2", "j2_team_matches.csv"),
                  ("j3", "j3_team_matches.csv")):
    rows = load_csv(tfile)
    out = {}
    for trait, col in (("goals_for", "goals_for"), ("goals_against", "goals_against"),
                       ("sot_for", "sot_for"), ("shots_for", "shots_for"),
                       ("corners_for", "corners_for"), ("yellow_for", "yellow_for"),
                       ("xg_for", "xg_for")):
        nt, r = split_half(trait_map(rows, col), min_matches=24)
        out[trait] = {"n_teams": nt, "r": r}
    S["reliability"][lg] = out
# J1 ratio traits (ratio of sums)
j1rows = load_csv("j1_team_matches.csv")
sm_rows = [r for r in j1rows if r["has_shotmap"] == "True"]
ratio_traits = {}
for name, nc, dc in (("xg_per_shot", "sm_xg_for", "shots_for"),
                     ("shot_conversion_goals_per_shot", "goals_for", "shots_for"),
                     ("sot_rate", "sm_sot_for", "shots_for"),
                     ("setplay_xg_share", "xg_sp_for", "xg_for")):
    if name == "setplay_xg_share":
        continue  # needs stats split columns not in long table; done below
    n_map, d_map = ratio_map(sm_rows, nc, dc)
    nt, r = split_half_ratio(n_map, d_map, min_matches=24)
    ratio_traits[name] = {"n_teams": nt, "r": r}
# finishing: goals - xg per match (stats feed)
fin = defaultdict(list)
for r in j1rows:
    if r["xg_for"] != "":
        fin[r["team_id"]].append(float(r["goals_for"]) - float(r["xg_for"]))
nt, r = split_half({t: np.array(v) for t, v in fin.items()}, min_matches=24)
ratio_traits["finishing_goals_minus_xg"] = {"n_teams": nt, "r": r}
# set-play xG share from match table (stats feed)
j1m = load_csv("j1_matches.csv")
sp_n, sp_d = defaultdict(list), defaultdict(list)
for r in j1m:
    for side in ("home", "away"):
        if r[f"expected_goals_set_play_{side}"] != "" and r[f"expected_goals_{side}"] != "":
            tid = r[f"{side}_team_id"]
            sp_n[tid].append(float(r[f"expected_goals_set_play_{side}"]))
            sp_d[tid].append(float(r[f"expected_goals_{side}"]))
nt, r = split_half_ratio({t: np.array(v) for t, v in sp_n.items()},
                         {t: np.array(v) for t, v in sp_d.items()}, min_matches=24)
ratio_traits["setplay_xg_share"] = {"n_teams": nt, "r": r}
# xGOT post-shot quality, 2025+ era only (population ~complete):
# mean xGOT per populated shot, ratio of sums over sm_xgot_n
xg_rows = [r for r in j1m if r["season"] in ("2025", "2026", "2026-2027")]
qn, qd = defaultdict(list), defaultdict(list)
for r in xg_rows:
    for side in ("home", "away"):
        if r[f"sm_xgot_{side}"] != "" and r[f"sm_xgot_n_{side}"] not in ("", "0"):
            tid = r[f"{side}_team_id"]
            qn[tid].append(float(r[f"sm_xgot_{side}"])); qd[tid].append(float(r[f"sm_xgot_n_{side}"]))
nt, r = split_half_ratio({t: np.array(v) for t, v in qn.items()},
                         {t: np.array(v) for t, v in qd.items()}, min_matches=20)
ratio_traits["xgot_per_shot_2025plus"] = {"n_teams": nt, "r": r}
# keeper side: xGOT against per shot faced vs goals against per shot faced
ka, kg = defaultdict(list), defaultdict(list)
for r in xg_rows:
    for side, opp in (("home", "away"), ("away", "home")):
        if r[f"sm_xgot_{opp}"] != "" and r[f"sm_xgot_n_{opp}"] not in ("", "0"):
            tid = r[f"{side}_team_id"]
            ka[tid].append(float(r[f"sm_xgot_{opp}"])); kg[tid].append(float(r[f"sm_xgot_n_{opp}"]))
nt, r = split_half_ratio({t: np.array(v) for t, v in ka.items()},
                         {t: np.array(v) for t, v in kg.items()}, min_matches=20)
ratio_traits["xgot_against_per_shot_2025plus"] = {"n_teams": nt, "r": r}
S["reliability"]["j1_ratio_traits"] = ratio_traits

# season-lag correlation for headline traits (teams in consecutive seasons)
S["season_lag"] = {}
for lg, tfile in (("j1", "j1_team_matches.csv"), ("j2", "j2_team_matches.csv")):
    rows = load_csv(tfile)
    per = defaultdict(dict)  # (team, season) -> dict of means
    for r in rows:
        per[(r["team_id"], r["season"])].setdefault("gf", []).append(float(r["goals_for"]))
        if r["sot_for"] != "":
            per[(r["team_id"], r["season"])].setdefault("sot", []).append(float(r["sot_for"]))
        if r["corners_for"] != "":
            per[(r["team_id"], r["season"])].setdefault("cor", []).append(float(r["corners_for"]))
    seasons = sorted({s for _, s in per})
    out = {}
    for trait in ("gf", "sot", "cor"):
        a, b = [], []
        for (t, s), v in per.items():
            i = seasons.index(s)
            if i + 1 < len(seasons) and (t, seasons[i + 1]) in per and trait in v and trait in per[(t, seasons[i + 1])]:
                a.append(np.mean(v[trait])); b.append(np.mean(per[(t, seasons[i + 1])][trait]))
        out[trait] = {"n_pairs": len(a),
                      "r": round(float(np.corrcoef(a, b)[0, 1]), 3) if len(a) > 5 else None}
    S["season_lag"][lg] = out

# halves share true-variance for SOT / corners / shots (stats halves, J1)
for name, fh_h, fh_a, ft_h, ft_a in (
        ("sot_share_1h", "fh_ShotsOnTarget_home", "fh_ShotsOnTarget_away",
         "ShotsOnTarget_home", "ShotsOnTarget_away"),
        ("corner_share_1h", "fh_corners_home", "fh_corners_away",
         "corners_home", "corners_away"),
        ("shots_share_1h", "fh_total_shots_home", "fh_total_shots_away",
         "total_shots_home", "total_shots_away")):
    rows = [r for r in tm if r["has_stats_half"] == "True"]
    fh = num(rows, fh_h) + num(rows, fh_a)
    ft = num(rows, ft_h) + num(rows, ft_a)
    ok = ft > 0
    sh = fh[ok] / ft[ok]
    p = sh.mean()
    excess = sh.var() - np.mean(p * (1 - p) / ft[ok])
    S["halves_j1"][name + "_true_var"] = round(float(excess), 5)
    S["halves_j1"][name + "_mean"] = round(float(p), 3)
# team box-touches trait reliability (territorial proxy for corners)
bt = defaultdict(list)
for r in j1m:
    for side in ("home", "away"):
        if r[f"touches_opp_box_{side}"] != "":
            bt[r[f"{side}_team_id"]].append(float(r[f"touches_opp_box_{side}"]))
nt, r = split_half({t: np.array(v) for t, v in bt.items()}, min_matches=24)
S["reliability"]["j1_ratio_traits"]["opp_box_touches_for"] = {"n_teams": nt, "r": r}
# J1 xG calibration by season (stats feed): sum goals vs sum xG
cal = {}
for season in sorted({r["season"] for r in j1m}):
    rows = [r for r in j1m if r["season"] == season and r["expected_goals_home"] != ""]
    if rows:
        g = sum(float(r["home_goals"]) + float(r["away_goals"]) for r in rows)
        x = sum(float(r["expected_goals_home"]) + float(r["expected_goals_away"]) for r in rows)
        cal[season] = {"n": len(rows), "goals": int(g), "xg": round(x, 1),
                       "goals_per_xg": round(g / x, 3)}
S["xg_calibration_j1"] = cal

# ---------- E. cross-tier gaps via promoted / relegated teams ----------
S["cross_tier"] = {}
tables = {lg: load_csv(f"{lg}_team_matches.csv") for lg in ("j1", "j2", "j3")}
membership = {}
for lg, rows in tables.items():
    for r in rows:
        membership.setdefault(r["season"], {}).setdefault(lg, set()).add(r["team_id"])
def team_season_means(rows, team, season):
    sel = [r for r in rows if r["team_id"] == team and r["season"] == season]
    if not sel:
        return None
    return {"n": len(sel), "gf": float(np.mean([float(x["goals_for"]) for x in sel])),
            "ga": float(np.mean([float(x["goals_against"]) for x in sel])),
            "ppg": float(np.mean([float(x["points"]) for x in sel]))}
for upper, lower in (("j1", "j2"), ("j2", "j3")):
    seasons = sorted(set(membership) & set(membership))
    moves = []
    all_seasons = sorted(membership)
    for i, s in enumerate(all_seasons[:-1]):
        s2 = all_seasons[i + 1]
        up_teams = membership.get(s, {}).get(lower, set()) & membership.get(s2, {}).get(upper, set())
        down_teams = membership.get(s, {}).get(upper, set()) & membership.get(s2, {}).get(lower, set())
        for t in up_teams:
            moves.append(("promoted", t, s, s2,
                          team_season_means(tables[lower], t, s),
                          team_season_means(tables[upper], t, s2)))
        for t in down_teams:
            moves.append(("relegated", t, s, s2,
                          team_season_means(tables[upper], t, s),
                          team_season_means(tables[lower], t, s2)))
    agg = {}
    for kind in ("promoted", "relegated"):
        sel = [mv for mv in moves if mv[0] == kind and mv[4] and mv[5]]
        if sel:
            agg[kind] = {"n": len(sel),
                         "gf_before": round(float(np.mean([mv[4]["gf"] for mv in sel])), 3),
                         "gf_after": round(float(np.mean([mv[5]["gf"] for mv in sel])), 3),
                         "ga_before": round(float(np.mean([mv[4]["ga"] for mv in sel])), 3),
                         "ga_after": round(float(np.mean([mv[5]["ga"] for mv in sel])), 3),
                         "ppg_before": round(float(np.mean([mv[4]["ppg"] for mv in sel])), 3),
                         "ppg_after": round(float(np.mean([mv[5]["ppg"] for mv in sel])), 3)}
    S["cross_tier"][f"{lower}->{upper}"] = agg

# ---------- F. corners vs territorial pressure (J1) ----------
j1m2 = load_csv("j1_matches.csv")
cx, cy, cp = [], [], []
for r in j1m2:
    for side, opp in (("home", "away"), ("away", "home")):
        if r[f"corners_{side}"] != "" and r[f"touches_opp_box_{side}"] != "":
            cx.append(float(r[f"corners_{side}"])); cy.append(float(r[f"touches_opp_box_{side}"]))
            cp.append(float(r[f"BallPossesion_{side}"]))
S["corners_territorial_j1"] = {
    "n_team_matches": len(cx),
    "corr_corners_boxtouches": round(float(np.corrcoef(cx, cy)[0, 1]), 3),
    "corr_corners_possession": round(float(np.corrcoef(cx, cp)[0, 1]), 3),
}

# ---------- G. events pass: timing, first goal, referees ----------
timing = Counter(); first_goal = {"home_first": 0, "away_first": 0,
                                  "home_first_pts": [], "away_first_pts": []}
late = {"goals_76plus": 0, "goals_total": 0}
ref_cards = defaultdict(list)
ref_names = {}
att = []
for lg, season, path in iter_files():
    d = load(path)
    gen, content = d.get("general") or {}, d.get("content") or {}
    info = ((content.get("matchFacts") or {}).get("infoBox") or {})
    ref = info.get("Referee") or {}
    if ref.get("text"):
        ref_names[ref["text"]] = ref["text"]
    if info.get("Attendance"):
        att.append(info["Attendance"])
    goals = sorted(goal_events(content), key=lambda e: (e.get("time") or 0))
    hg = ag = 0
    for e in goals:
        t = e.get("time") or 0
        timing[min(t // 15, 5)] += 1
        if t >= 76:
            late["goals_76plus"] += 1
        late["goals_total"] += 1
        if e.get("isHome"):
            hg += 1
        else:
            ag += 1
    if goals and lg == "J1":
        first = goals[0]
        pts_h = 3 if hg > ag else (1 if hg == ag else 0)
        pts_a = 3 if ag > hg else (1 if ag == hg else 0)
        if first.get("isHome"):
            first_goal["home_first"] += 1; first_goal["home_first_pts"].append(pts_h)
        else:
            first_goal["away_first"] += 1; first_goal["away_first_pts"].append(pts_a)
    if ref.get("text"):
        cards = [e for e in events_of(content) if e.get("type") == "Card"]
        ref_cards[ref["text"]].append(len(cards))
S["goal_timing"] = {"by_15min_block": {str(k): timing[k] for k in sorted(timing)},
                    "share_76plus": round(late["goals_76plus"] / max(late["goals_total"], 1), 4),
                    "total_goals": late["goals_total"]}
S["first_goal_j1"] = {"home_first_n": first_goal["home_first"],
                      "home_first_ppg": round(float(np.mean(first_goal["home_first_pts"])), 3) if first_goal["home_first_pts"] else None,
                      "away_first_n": first_goal["away_first"],
                      "away_first_ppg": round(float(np.mean(first_goal["away_first_pts"])), 3) if first_goal["away_first_pts"] else None}
ref_traits = {k: np.array(v, dtype=float) for k, v in ref_cards.items() if len(v) >= 20}
nt, r = split_half(ref_traits, min_matches=20)
S["referees"] = {"n_referees_seen": len(ref_cards),
                 "card_rate_split_half": {"n_refs_ge20": nt, "r": r},
                 "attendance_n": len(att)}

OUT.write_text(json.dumps(S, indent=1, ensure_ascii=False))
print(json.dumps(S, indent=1, ensure_ascii=False))
