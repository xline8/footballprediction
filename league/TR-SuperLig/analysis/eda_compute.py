"""EDA computations for TR-SuperLig -> eda_numbers.json (measured, not hand-typed).

Method follows the CH/DK convention: split-half reliability = career-pooled per
team, teams with >=20 team-matches, 60 random splits averaged (seed 42).
Ratio traits use ratio-of-sums within each half. Cards feed checked against
the event feed explicitly (program lesson: two leagues had stats-feed card
undercounts).
"""
import csv, json, math, random, statistics as st
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROWS = list(csv.DictReader(open(HERE.parent / "data" / "tr_matches.csv")))
rng = random.Random(42)

def f(r, k):
    v = r.get(k)
    return None if v in (None, "", "None") else float(v)

def corr(xs, ys):
    if len(xs) < 5: return None
    mx, my = st.mean(xs), st.mean(ys)
    num = sum((a-mx)*(b-my) for a, b in zip(xs, ys))
    den = math.sqrt(sum((a-mx)**2 for a in xs) * sum((b-my)**2 for b in ys))
    return num/den if den else None

def split_half_random(series_by_team, min_n=20, reps=60):
    """series_by_team: team -> list of per-match values."""
    teams = {t: v for t, v in series_by_team.items() if len(v) >= min_n}
    rs = []
    for _ in range(reps):
        xs, ys = [], []
        for t, vs in teams.items():
            idx = list(range(len(vs))); rng.shuffle(idx)
            h = len(vs)//2
            xs.append(st.mean([vs[i] for i in idx[:h]])); ys.append(st.mean([vs[i] for i in idx[h:]]))
        c = corr(xs, ys)
        if c is not None: rs.append(c)
    return (round(st.mean(rs), 3) if rs else None), len(teams)

def split_half_ratio(pairs_by_team, min_n=20, reps=60):
    teams = {t: v for t, v in pairs_by_team.items() if len(v) >= min_n}
    rs = []
    for _ in range(reps):
        xs, ys = [], []
        for t, ms in teams.items():
            idx = list(range(len(ms))); rng.shuffle(idx)
            h = len(ms)//2
            for part, acc in ((idx[:h], xs), (idx[h:], ys)):
                sn = sum(ms[i][0] for i in part); sd = sum(ms[i][1] for i in part)
                acc.append(sn/sd if sd else 0.0)
        c = corr(xs, ys)
        if c is not None: rs.append(c)
    return (round(st.mean(rs), 3) if rs else None), len(teams)

def team_series(key, against=False):
    d = defaultdict(list)
    for r in ROWS:
        for side, opp in (("home", "away"), ("away", "home")):
            v = f(r, f"{key}_{opp if against else side}")
            if v is not None: d[r[f"{side}_team_id"]].append(v)
    return d

def ratio_pairs(num, den, seasons_filter=None, side_key="team_id"):
    d = defaultdict(list)
    for r in ROWS:
        if seasons_filter and r["season"] not in seasons_filter: continue
        for side in ("home", "away"):
            n_, d_ = f(r, f"{num}_{side}"), f(r, f"{den}_{side}")
            if n_ is not None and d_ is not None: d[r[f"{side}_{side_key}"]].append((n_, d_))
    return d

out = {}
out["n"] = len(ROWS)
seasons = sorted(set(r["season"] for r in ROWS))
out["seasons"] = seasons
out["team_ids"] = len(set([r["home_team_id"] for r in ROWS] + [r["away_team_id"] for r in ROWS]))

per = {}
for s in seasons:
    rs = [r for r in ROWS if r["season"] == s]
    def cov(k): return round(100*sum(1 for r in rs if f(r, k) is not None)/len(rs), 1)
    def tot(k):
        vals = [f(r, f"{k}_home") + f(r, f"{k}_away") for r in rs if f(r, f"{k}_home") is not None and f(r, f"{k}_away") is not None]
        return round(st.mean(vals), 3) if vals else None
    per[s] = {
        "n": len(rs),
        "goals": round(st.mean([int(r["home_goals"])+int(r["away_goals"]) for r in rs]), 3),
        "home_goals": round(st.mean([int(r["home_goals"]) for r in rs]), 3),
        "away_goals": round(st.mean([int(r["away_goals"]) for r in rs]), 3),
        "sot": tot("ShotsOnTarget"), "corners": tot("corners"), "shots": tot("total_shots"),
        "yellows_stats": tot("yellow_cards"),
        "yellows_events": round(st.mean([int(r["ev_yellow_home"])+int(r["ev_yellow_away"]) for r in rs]), 3),
        "reds_stats": tot("red_cards"),
        "xg": tot("expected_goals"),
        "cov_stats": round(100*st.mean([int(r["has_stats_all"]) for r in rs]), 1),
        "cov_half": round(100*st.mean([int(r["has_stats_half"]) for r in rs]), 1),
        "cov_shotmap": round(100*st.mean([int(r["has_shotmap"]) for r in rs]), 1),
        "cov_events": round(100*st.mean([int(r["has_events"]) for r in rs]), 1),
        "cov_ref": round(100*sum(1 for r in rs if r["referee"])/len(rs), 1),
        "cov_touches": cov("touches_opp_box_home"), "cov_xg": cov("expected_goals_home"),
        "cov_cards_stats": cov("yellow_cards_home"),
        "cards_sources": {src: sum(1 for r in rs if r["cards_source"] == src) for src in ("stats", "events", "none")},
        "phases": {p: sum(1 for r in rs if r["phase"] == p) for p in sorted(set(x["phase"] for x in rs))},
        "teams": len(set([r["home_team_id"] for r in rs] + [r["away_team_id"] for r in rs])),
        "coverage": {k: cov(f"{k}_home") for k in ["ShotsOnTarget", "corners", "total_shots", "yellow_cards",
                                                     "expected_goals", "expected_goals_open_play", "expected_goals_set_play",
                                                     "expected_goals_non_penalty", "touches_opp_box", "big_chance", "BallPossesion"]},
    }
out["per_season"] = per

# cards: stats feed vs event feed (the explicit quirk check)
cards_dev_seasons = {"2021/2022", "2022/2023", "2023/2024", "2024/2025"}
both = [r for r in ROWS if r["season"] in cards_dev_seasons and f(r, "yellow_cards_home") is not None]
diffs = [(f(r, "yellow_cards_home")+f(r, "yellow_cards_away")) - (int(r["ev_yellow_home"])+int(r["ev_yellow_away"])) for r in both]
out["cards_check"] = {
    "n_with_stats": len(both),
    "exact_agree_pct": round(100*sum(1 for d in diffs if d == 0)/len(diffs), 1),
    "mean_stats_minus_events": round(st.mean(diffs), 3),
    "stats_lower_pct": round(100*sum(1 for d in diffs if d < 0)/len(diffs), 1),
    "stats_higher_pct": round(100*sum(1 for d in diffs if d > 0)/len(diffs), 1),
    "max_abs_diff": int(max(abs(d) for d in diffs)),
}
# second-yellow nuance: event feed counts a YellowRed as one event 'YellowRed' (not in ev_yellow);
# stats feed counts it as a yellow too in most feeds -> check diff vs (ev_yellow + ev_yellowred)
diffs2 = [(f(r, "yellow_cards_home")+f(r, "yellow_cards_away")) - (int(r["ev_yellow_home"])+int(r["ev_yellow_away"])+int(r["ev_yellowred_home"])+int(r["ev_yellowred_away"])) for r in both]
out["cards_check"]["exact_agree_pct_incl_yellowred"] = round(100*sum(1 for d in diffs2 if d == 0)/len(diffs2), 1)
out["cards_check"]["mean_diff_incl_yellowred"] = round(st.mean(diffs2), 3)

# SOT stats vs shotmap correlation
import math as _m
sx, sy = [], []
for r in ROWS:
    if f(r, "ShotsOnTarget_home") is not None and int(r["has_shotmap"]):
        sx.append(f(r, "ShotsOnTarget_home")+f(r, "ShotsOnTarget_away")); sy.append(int(r["sm_sot_home"])+int(r["sm_sot_away"]))
out["sot_stats_vs_shotmap_corr"] = round(corr(sx, sy), 3)

out["goals_per_xg"] = {s: round(sum(int(r["home_goals"])+int(r["away_goals"]) for r in ROWS if r["season"] == s and f(r, "expected_goals_home") is not None) /
                        sum(f(r, "expected_goals_home")+f(r, "expected_goals_away") for r in ROWS if r["season"] == s and f(r, "expected_goals_home") is not None), 3)
                        for s in seasons if any(f(r, "expected_goals_home") is not None for r in ROWS if r["season"] == s)}

# reliabilities
rel = {}
gd = defaultdict(list)
for name, key, against in [("goals_for", None, False), ("goals_against", None, True),
                           ("sot_for", "ShotsOnTarget", False), ("corners_for", "corners", False),
                           ("shots_for", "total_shots", False), ("yellows_for", "yellow_cards", False),
                           ("xg_for", "expected_goals", False), ("touches_for", "touches_opp_box", False),
                           ("touches_against", "touches_opp_box", True), ("bigchance_for", "big_chance", False),
                           ("possession", "BallPossesion", False)]:
    if key is None:
        d = defaultdict(list)
        for r in ROWS:
            if not against:
                d[r["home_team_id"]].append(int(r["home_goals"])); d[r["away_team_id"]].append(int(r["away_goals"]))
            else:
                d[r["home_team_id"]].append(int(r["away_goals"])); d[r["away_team_id"]].append(int(r["home_goals"]))
        rel[name] = split_half_random(d)
    else:
        rel[name] = split_half_random(team_series(key, against))
out["reliability"] = {k: v[0] for k, v in rel.items()}
out["reliability_nteams"] = {k: v[1] for k, v in rel.items()}

# Season-blocked reliability table.  This is descriptive only: it is not a
# fitting split and no later season is used to characterize an earlier one.
def season_team_series(season, key, against=False):
    d = defaultdict(list)
    for r in ROWS:
        if r["season"] != season: continue
        for side, opp in (("home", "away"), ("away", "home")):
            v = f(r, f"{key}_{opp if against else side}")
            if v is not None: d[r[f"{side}_team_id"]].append(v)
    return d

out["reliability_by_season"] = {}
for season in seasons:
    sr = {}
    for name, key, against in [("goals_for", "goals", False), ("goals_against", "goals", True),
                                ("sot_for", "ShotsOnTarget", False), ("sot_against", "ShotsOnTarget", True),
                                ("corners_for", "corners", False), ("corners_against", "corners", True),
                                ("cards_for", "yellow_cards", False), ("cards_against", "yellow_cards", True),
                                ("shots_for", "total_shots", False), ("shots_against", "total_shots", True),
                                ("touches_for", "touches_opp_box", False), ("touches_against", "touches_opp_box", True)]:
        if key == "goals":
            d = defaultdict(list)
            for r in ROWS:
                if r["season"] != season: continue
                d[r["home_team_id"]].append(float(r["home_goals"] if not against else r["away_goals"]))
                d[r["away_team_id"]].append(float(r["away_goals"] if not against else r["home_goals"]))
        else: d = season_team_series(season, key, against)
        sr[name] = split_half_random(d)
    sr["set_play_share"] = split_half_ratio(ratio_pairs("expected_goals_set_play", "expected_goals", {season}))
    sr["xg_per_shot"] = split_half_ratio(ratio_pairs("expected_goals", "total_shots", {season}))
    xgots = defaultdict(list)
    for r in ROWS:
        if r["season"] != season: continue
        for side in ("home", "away"):
            n = r[f"sm_xgot_n_{side}"]
            if n not in (None, "") and int(n) > 0: xgots[r[f"{side}_team_id"]].append((f(r, f"sm_xgot_{side}"), int(n)))
    _cov_num = sum((int(r["sm_xgot_n_home"]) if r["sm_xgot_n_home"] not in ("", None) else 0)+(int(r["sm_xgot_n_away"]) if r["sm_xgot_n_away"] not in ("", None) else 0) for r in ROWS if r["season"] == season)
    _cov_den = sum((int(r["sm_shots_home"]) if r["sm_shots_home"] not in ("", None) else 0)+(int(r["sm_shots_away"]) if r["sm_shots_away"] not in ("", None) else 0) for r in ROWS if r["season"] == season)
    sr["xgot_per_shot"] = split_half_ratio(xgots, min_n=10) if _cov_den and 100*_cov_num/_cov_den > 90 else (None, 0)
    ref_season = defaultdict(list)
    for r in ROWS:
        if r["season"] == season and r["referee"] and f(r, "yellow_cards_home") is not None:
            ref_season[r["referee"]].append(f(r, "yellow_cards_home") + f(r, "yellow_cards_away"))
    sr["referee_strictness"] = split_half_random(ref_season, min_n=5)
    sr["referee_coverage_pct"] = per[season]["cov_ref"]
    out["reliability_by_season"][season] = sr
out["sp_share_rel"] = split_half_ratio(ratio_pairs("expected_goals_set_play", "expected_goals"))
out["xg_per_shot_rel"] = split_half_ratio(ratio_pairs("sm_xg", "sm_shots", side_key="team_id") if False else ratio_pairs("expected_goals", "total_shots"))
# on-target rate via shotmap aggregates per team
ot = defaultdict(list)
for r in ROWS:
    for side in ("home", "away"):
        if r["sm_shots_" + side] not in ("", None) and int(r["sm_shots_" + side]) > 0: ot[r[f"{side}_team_id"]].append((int(r["sm_sot_" + side]), int(r["sm_shots_" + side])))
out["on_target_rate_rel"] = split_half_ratio(ot)
# xGOT era: coverage per season + reliability on fully-populated era
def _ism(r, k): return int(r[k]) if r[k] not in ("", None) else 0
out["xgot_cov_pct_of_shots"] = {s: round(100*sum(_ism(r, "sm_xgot_n_home")+_ism(r, "sm_xgot_n_away") for r in ROWS if r["season"] == s) /
                                        max(1, sum(_ism(r, "sm_shots_home")+_ism(r, "sm_shots_away") for r in ROWS if r["season"] == s)), 1) for s in seasons}
xgot_era = [s for s in seasons if out["xgot_cov_pct_of_shots"][s] > 90]
out["xgot_full_era"] = xgot_era
xg = defaultdict(list)
for r in ROWS:
    if r["season"] in xgot_era:
        for side in ("home", "away"):
            if r["sm_xgot_n_" + side] not in ("", None) and int(r["sm_xgot_n_" + side]) > 0: xg[r[f"{side}_team_id"]].append((f(r, "sm_xgot_" + side), int(r["sm_xgot_n_" + side])))
out["xgot_rel_era"] = split_half_ratio(xg, min_n=10)

# referee reliability
refm = defaultdict(list)
for r in ROWS:
    if r["referee"] and f(r, "yellow_cards_home") is not None:
        refm[r["referee"]].append(f(r, "yellow_cards_home")+f(r, "yellow_cards_away"))
out["ref_rel"] = split_half_random(refm, min_n=20)
out["n_refs_ge20"] = sum(1 for v in refm.values() if len(v) >= 20)

# half shares: ratio of sums + true variance of per-match share (complete-splits seasons only)
def half_block(num, den_is_same=True, seasons_filter=None):
    shares, weights, s1, s0 = [], [], 0.0, 0.0
    for r in ROWS:
        if seasons_filter and r["season"] not in seasons_filter: continue
        a1, a2 = f(r, f"fh_{num}_home"), f(r, f"fh_{num}_away")
        b1, b2 = f(r, f"{num}_home"), f(r, f"{num}_away")
        if None in (a1, a2, b1, b2) or (b1+b2) == 0: continue
        shares.append((a1+a2)/(b1+b2)); weights.append(b1+b2); s1 += a1+a2; s0 += b1+b2
    if len(shares) < 30: return {"n": len(shares)}
    m = st.mean(shares); obs = st.variance(shares)
    noise = st.mean([m*(1-m)/w for w in weights])
    return {"n": len(shares), "share_ratio_of_sums": round(s1/s0, 4), "obs_var": round(obs, 4),
            "true_var": round(obs-noise, 4), "true_sd": round(math.sqrt(max(obs-noise, 0.0)), 4)}
# Halves constants are frozen from the complete-splits DEV era only.  The
# complete virgin season is deliberately not used to set them.
half_seasons = [s for s in ("2023/2024", "2024/2025") if s in seasons and per[s]["cov_half"] > 90]
out["half_complete_seasons"] = half_seasons
hs = set(half_seasons)
out["half_shares"] = {
    "sot": half_block("ShotsOnTarget", seasons_filter=hs),
    "corners": half_block("corners", seasons_filter=hs),
    "shots": half_block("total_shots", seasons_filter=hs),
    "yellows": half_block("yellow_cards", seasons_filter=hs),
}
# goals half share from events HT (all seasons + complete era)
for label, filt in (("goals_all", None), ("goals_half_era", hs)):
    sh, wts, s1, s0 = [], [], 0, 0
    for r in ROWS:
        if filt and r["season"] not in filt: continue
        tot = int(r["home_goals"])+int(r["away_goals"])
        if tot and r["ht_home_goals"] not in (None, ""):
            ht = int(r["ht_home_goals"])+int(r["ht_away_goals"])
            sh.append(ht/tot); wts.append(tot); s1 += ht; s0 += tot
    m = st.mean(sh); obs = st.variance(sh); noise = st.mean([m*(1-m)/w for w in wts])
    out["half_shares"][label] = {"n": len(sh), "share_ratio_of_sums": round(s1/s0, 4), "obs_var": round(obs, 4), "true_var": round(obs-noise, 4)}

# dispersion + outcome rates pooled (complete seasons)
comp = [r for r in ROWS if r["season"] != "2026/2027"]
def disp(vals):
    m = st.mean(vals); return round(st.variance(vals)/m, 3)
out["pooled"] = {
    "n_complete": len(comp),
    "goals": round(st.mean([int(r["home_goals"])+int(r["away_goals"]) for r in comp]), 3),
    "home_goals": round(st.mean([int(r["home_goals"]) for r in comp]), 3),
    "away_goals": round(st.mean([int(r["away_goals"]) for r in comp]), 3),
    "hw_pct": round(100*sum(1 for r in comp if int(r["home_goals"]) > int(r["away_goals"]))/len(comp), 1),
    "draw_pct": round(100*sum(1 for r in comp if int(r["home_goals"]) == int(r["away_goals"]))/len(comp), 1),
    "aw_pct": round(100*sum(1 for r in comp if int(r["home_goals"]) < int(r["away_goals"]))/len(comp), 1),
    "over25_pct": round(100*sum(1 for r in comp if int(r["home_goals"])+int(r["away_goals"]) > 2)/len(comp), 1),
    "btts_pct": round(100*sum(1 for r in comp if int(r["home_goals"]) > 0 and int(r["away_goals"]) > 0)/len(comp), 1),
    "disp_goals": disp([int(r["home_goals"])+int(r["away_goals"]) for r in comp]),
    "disp_sot": disp([f(r, "ShotsOnTarget_home")+f(r, "ShotsOnTarget_away") for r in comp if f(r, "ShotsOnTarget_home") is not None]),
    "disp_corners": disp([f(r, "corners_home")+f(r, "corners_away") for r in comp if f(r, "corners_home") is not None]),
    "disp_yellows": disp([f(r, "yellow_cards_home")+f(r, "yellow_cards_away") for r in comp if f(r, "yellow_cards_home") is not None]),
    "disp_shots": disp([f(r, "total_shots_home")+f(r, "total_shots_away") for r in comp if f(r, "total_shots_home") is not None]),
}
# playoff vs regular levels (complete seasons) — evidence for the phase decision
for ph in ("regular", "playoff_championship", "playoff_europe", "playoff_relegation", "playoff_final"):
    rs = [r for r in comp if r["phase"] == ph]
    if len(rs) >= 10:
        out.setdefault("phase_levels", {})[ph] = {
            "n": len(rs),
            "goals": round(st.mean([int(r["home_goals"])+int(r["away_goals"]) for r in rs]), 3),
            "sot": round(st.mean([f(r, "ShotsOnTarget_home")+f(r, "ShotsOnTarget_away") for r in rs if f(r, "ShotsOnTarget_home") is not None]), 3),
            "corners": round(st.mean([f(r, "corners_home")+f(r, "corners_away") for r in rs if f(r, "corners_home") is not None]), 3),
            "yellows": round(st.mean([f(r, "yellow_cards_home")+f(r, "yellow_cards_away") for r in rs if f(r, "yellow_cards_home") is not None]), 3),
            "shots": round(st.mean([f(r, "total_shots_home")+f(r, "total_shots_away") for r in rs if f(r, "total_shots_home") is not None]), 3),
        }
# dev over-rates for primary-line choice: dev scored seasons = 2022/2023..2024/2025 (data through 2024/2025)
dev = [r for r in ROWS if r["season"] in ("2021/2022", "2022/2023", "2023/2024", "2024/2025")]
out["dev_n_all4"] = len(dev)
def over_rate(rs, key, line):
    vals = [f(r, f"{key}_home")+f(r, f"{key}_away") for r in rs if f(r, f"{key}_home") is not None]
    return round(sum(1 for v in vals if v > line)/len(vals), 3), len(vals)
out["dev_over_rates"] = {
    "goals_2.5": over_rate(dev, "x", 2.5) if False else (round(sum(1 for r in dev if int(r["home_goals"])+int(r["away_goals"]) > 2)/len(dev), 3), len(dev)),
    "sot": {str(l): over_rate(dev, "ShotsOnTarget", l) for l in (8.5, 9.5, 10.5)},
    "corners": {str(l): over_rate(dev, "corners", l) for l in (9.5, 10.5, 11.5)},
    "yellows": {str(l): over_rate(dev, "yellow_cards", l) for l in (3.5, 4.5, 5.5)},
    "shots": {str(l): over_rate(dev, "total_shots", l) for l in (25.5, 26.5, 27.5)},
}
out["virgin_n"] = per["2025/2026"]["n"]
out["dev_scored_n"] = sum(per[s]["n"] for s in ("2022/2023", "2023/2024", "2024/2025"))
Path(HERE / "eda_numbers.json").write_text(json.dumps(out, indent=1))
print(json.dumps(out, indent=1))
