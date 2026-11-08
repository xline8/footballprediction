"""EDA computations for SA-ProLeague -> eda_numbers.json (for EDA.md).

Regime frame: PRE = 2021/2022+2022/2023 (16 teams, no shotmap/xG feed),
POST = 2023/2024+ (18 teams, foreign-star influx, full shotmap/xG).
Virgin 2025/2026 numbers are reported for the inventory only; design
decisions use dev-era (<=2024/2025) evidence.
"""
import csv, json, math, statistics as st
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROWS = list(csv.DictReader(open(HERE.parent / "data" / "sa_matches.csv")))
PRE = ["2021/2022", "2022/2023"]
POST_DEV = ["2023/2024", "2024/2025"]
POST_ALL = ["2023/2024", "2024/2025", "2025/2026"]
SEASONS = sorted(set(r["season"] for r in ROWS))

def f(r, k):
    v = r.get(k)
    return None if v in (None, "", "None") else float(v)

def corr(xs, ys):
    if len(xs) < 5: return None
    mx, my = st.mean(xs), st.mean(ys)
    num = sum((a-mx)*(b-my) for a, b in zip(xs, ys))
    den = math.sqrt(sum((a-mx)**2 for a in xs) * sum((b-my)**2 for b in ys))
    return round(num/den, 3) if den else None

def split_half(vals_by_team, min_n=10):
    xs, ys = [], []
    for t, vs in vals_by_team.items():
        if len(vs) >= min_n:
            xs.append(st.mean(vs[0::2])); ys.append(st.mean(vs[1::2]))
    return corr(xs, ys), len(xs)

def team_series(key, seasons=None):
    d = defaultdict(list)
    for r in ROWS:
        if seasons and r["season"] not in seasons: continue
        for side in ("home", "away"):
            v = f(r, f"{key}_{side}")
            if v is not None: d[r[f"{side}_team"]].append(v)
    return d

def goals_series(seasons=None, against=False):
    d = defaultdict(list)
    for r in ROWS:
        if seasons and r["season"] not in seasons: continue
        d[r["home_team"]].append(int(r["away_goals"] if against else r["home_goals"]))
        d[r["away_team"]].append(int(r["home_goals"] if against else r["away_goals"]))
    return d

out = {"n": len(ROWS), "seasons": SEASONS}
per = {}
for s in SEASONS:
    rs = [r for r in ROWS if r["season"] == s]
    def tot(k):
        vals = [f(r, f"{k}_home") + f(r, f"{k}_away") for r in rs if f(r, f"{k}_home") is not None]
        return round(st.mean(vals), 3) if vals else None
    per[s] = {
        "n": len(rs),
        "goals": round(st.mean([int(r["home_goals"])+int(r["away_goals"]) for r in rs]), 3),
        "home_goals": round(st.mean([int(r["home_goals"]) for r in rs]), 3),
        "away_goals": round(st.mean([int(r["away_goals"]) for r in rs]), 3),
        "xg": tot("expected_goals"), "sot": tot("ShotsOnTarget"), "corners": tot("corners"),
        "shots": tot("total_shots"),
        "yellows_stats": tot("yellow_cards"),
        "yellows_unified_events": round(st.mean([f(r, "yellow_home")+f(r, "yellow_away") for r in rs]), 3),
        "reds": tot("red_cards"),
        "cov_half": round(100*st.mean([int(r["has_stats_half"]) for r in rs]), 1),
        "cov_shotmap": round(100*st.mean([int(r["has_shotmap"]) for r in rs]), 1),
        "cov_xg": round(100*sum(1 for r in rs if f(r, "expected_goals_home") is not None)/len(rs), 1),
        "cov_touches": round(100*sum(1 for r in rs if f(r, "touches_opp_box_home") is not None)/len(rs), 1),
        "cov_ref": round(100*sum(1 for r in rs if r["referee"])/len(rs), 1),
        "teams": len(set([r["home_team"] for r in rs] + [r["away_team"] for r in rs])),
    }
out["per_season"] = per

# cards agreement, DEV-ERA ONLY (seasons <= 2024/2025) for the feed decision
dev_rows = [r for r in ROWS if r["season"] in PRE + POST_DEV]
agree = {}
for s in PRE + POST_DEV:
    rs = [r for r in dev_rows if r["season"] == s]
    ex = sum(1 for r in rs if f(r, "yellow_cards_home")+f(r, "yellow_cards_away") == f(r, "yellow_home")+f(r, "yellow_away"))
    low = sum(1 for r in rs if f(r, "yellow_cards_home")+f(r, "yellow_cards_away") < f(r, "yellow_home")+f(r, "yellow_away"))
    high = sum(1 for r in rs if f(r, "yellow_cards_home")+f(r, "yellow_cards_away") > f(r, "yellow_home")+f(r, "yellow_away"))
    agree[s] = {"exact_pct": round(100*ex/len(rs), 1), "stats_low": low, "stats_high": high,
                "mean_diff_stats_minus_events": round(st.mean([f(r, "yellow_cards_home")+f(r, "yellow_cards_away")-f(r, "yellow_home")-f(r, "yellow_away") for r in rs]), 3)}
out["cards_agreement_dev_era"] = agree

# regime break: pooled levels pre vs post-dev, and post incl virgin for inventory
def pooled(seasons):
    rs = [r for r in ROWS if r["season"] in seasons]
    g = lambda fn: round(st.mean([fn(r) for r in rs]), 3)
    return {"n": len(rs), "goals": g(lambda r: int(r["home_goals"])+int(r["away_goals"])),
            "sot": g(lambda r: f(r, "ShotsOnTarget_home")+f(r, "ShotsOnTarget_away")),
            "corners": g(lambda r: f(r, "corners_home")+f(r, "corners_away")),
            "shots": g(lambda r: f(r, "total_shots_home")+f(r, "total_shots_away")),
            "yellows_events": g(lambda r: f(r, "yellow_home")+f(r, "yellow_away")),
            "home_edge": round(st.mean([int(r["home_goals"]) for r in rs]) - st.mean([int(r["away_goals"]) for r in rs]), 3),
            "home_win_pct": round(100*st.mean([1 if int(r["home_goals"]) > int(r["away_goals"]) else 0 for r in rs]), 1),
            "ou25_pct": round(100*st.mean([1 if int(r["home_goals"])+int(r["away_goals"]) > 2 else 0 for r in rs]), 1)}
out["levels_pre"] = pooled(PRE); out["levels_post_dev"] = pooled(POST_DEV); out["levels_post_all"] = pooled(POST_ALL)

# cross-era trait stability: per-team means pre vs post (teams in both eras, >=15 matches each era)
def era_means(key_fn, seasons):
    d = defaultdict(list)
    for r in ROWS:
        if r["season"] not in seasons: continue
        for side, oside in (("home", "away"), ("away", "home")):
            v = key_fn(r, side, oside)
            if v is not None: d[r[f"{side}_team"]].append(v)
    return {t: st.mean(v) for t, v in d.items() if len(v) >= 15}
stab = {}
for name, fn in [("goals_for", lambda r, s, o: int(r[f"{s}_goals"])),
                 ("goals_against", lambda r, s, o: int(r[f"{o}_goals"])),
                 ("sot_for", lambda r, s, o: f(r, f"ShotsOnTarget_{s}")),
                 ("corners_for", lambda r, s, o: f(r, f"corners_{s}")),
                 ("shots_for", lambda r, s, o: f(r, f"total_shots_{s}"))]:
    a = era_means(fn, PRE); b = era_means(fn, POST_ALL)
    common = sorted(set(a) & set(b))
    stab[name] = {"r_pre_post": corr([a[t] for t in common], [b[t] for t in common]), "n_teams": len(common)}
out["trait_stability_pre_post"] = stab
# team GD spread per era (dominance)
def gd_spread(seasons):
    d = defaultdict(list)
    for r in ROWS:
        if r["season"] not in seasons: continue
        d[r["home_team"]].append(int(r["home_goals"])-int(r["away_goals"]))
        d[r["away_team"]].append(int(r["away_goals"])-int(r["home_goals"]))
    means = {t: round(st.mean(v), 3) for t, v in d.items() if len(v) >= 20}
    return {"sd": round(st.stdev(list(means.values())), 3), "top": sorted(means.items(), key=lambda kv: -kv[1])[:3], "bottom": sorted(means.items(), key=lambda kv: kv[1])[:2]}
out["gd_pre"] = gd_spread(PRE); out["gd_post"] = gd_spread(POST_ALL)

# reliabilities: career-pooled and POST-era only
rel_all, rel_post = {}, {}
for name, key in [("sot_for", "ShotsOnTarget"), ("corners_for", "corners"), ("shots_for", "total_shots"),
                  ("yellows_for", "yellow_cards"), ("xg_for", "expected_goals"), ("touches_for", "touches_opp_box"),
                  ("bigchance_for", "big_chance"), ("possession", "BallPossesion")]:
    rel_all[name] = split_half(team_series(key))
    rel_post[name] = split_half(team_series(key, seasons=set(POST_ALL)))
rel_all["goals_for"] = split_half(goals_series()); rel_post["goals_for"] = split_half(goals_series(seasons=set(POST_ALL)))
rel_all["yellows_events_for"] = split_half(team_series("yellow")); rel_post["yellows_events_for"] = split_half(team_series("yellow", seasons=set(POST_ALL)))
out["reliability_career"] = {k: v[0] for k, v in rel_all.items()}
out["reliability_post_era"] = {k: v[0] for k, v in rel_post.items()}
out["reliability_n_post"] = {k: v[1] for k, v in rel_post.items()}

def ratio_series(num, den, seasons):
    per_team = defaultdict(list)
    for r in ROWS:
        if r["season"] not in seasons: continue
        for side in ("home", "away"):
            n_, d_ = f(r, f"{num}_{side}"), f(r, f"{den}_{side}")
            if n_ is not None and d_ is not None: per_team[r[f"{side}_team"]].append((n_, d_))
    xs, ys = [], []
    for t, ms in per_team.items():
        if len(ms) >= 10:
            for half, acc in ((ms[0::2], xs), (ms[1::2], ys)):
                sn = sum(a for a, b in half); sd = sum(b for a, b in half)
                acc.append(sn/sd if sd else 0)
    return corr(xs, ys), len(xs)
out["sp_share_rel_post"] = ratio_series("expected_goals_set_play", "expected_goals", set(POST_ALL))
out["xg_per_shot_rel_post"] = ratio_series("sm_xg", "sm_shots", set(POST_ALL))
out["xgot_rel_2425plus"] = ratio_series("sm_xgot", "sm_xgot_n", {"2024/2025", "2025/2026", "2026/2027"})
out["xg_calibration"] = {s: (round(sum(int(r["home_goals"])+int(r["away_goals"]) for r in ROWS if r["season"] == s) /
    sum(f(r, "expected_goals_home")+f(r, "expected_goals_away") for r in ROWS if r["season"] == s and f(r, "expected_goals_home") is not None), 3)
    if any(f(r, "expected_goals_home") is not None for r in ROWS if r["season"] == s) else None) for s in SEASONS}

# referee reliability (post-era; virgin season has ~no referee names)
ref = defaultdict(list)
for r in ROWS:
    if r["season"] in POST_DEV and r["referee"]:
        ref[r["referee"]].append(f(r, "yellow_home")+f(r, "yellow_away"))
out["ref_rel_post_dev"] = split_half(ref); out["n_refs_ge10_post_dev"] = sum(1 for v in ref.values() if len(v) >= 10)

# half shares on the complete-splits era 2023/2024-2025/2026
def half_share(num1h, den, seasons):
    shares, weights = [], []
    for r in ROWS:
        if r["season"] not in seasons: continue
        a1, a2 = f(r, f"fh_{num1h}_home"), f(r, f"fh_{num1h}_away")
        b1, b2 = f(r, f"{den}_home"), f(r, f"{den}_away")
        if None in (a1, a2, b1, b2) or (b1+b2) == 0: continue
        shares.append((a1+a2)/(b1+b2)); weights.append(b1+b2)
    m = st.mean(shares); obs = st.variance(shares)
    noise = st.mean([m*(1-m)/w for w in weights])
    return {"n": len(shares), "share": round(m, 4), "obs_sd": round(math.sqrt(obs), 4), "true_sd": round(math.sqrt(max(obs-noise, 0.0)), 4)}
era = set(POST_ALL)
hs = {"sot": half_share("ShotsOnTarget", "ShotsOnTarget", era), "corners": half_share("corners", "corners", era),
      "shots": half_share("total_shots", "total_shots", era)}
gs = [(int(r["ht_home_goals"])+int(r["ht_away_goals"]))/(int(r["home_goals"])+int(r["away_goals"]))
      for r in ROWS if r["season"] in era and int(r["home_goals"])+int(r["away_goals"]) > 0]
hs["goals_events"] = {"n": len(gs), "share": round(st.mean(gs), 4), "obs_sd": round(math.sqrt(st.variance(gs)), 4)}
ys = []
for r in ROWS:
    if r["season"] not in era: continue
    t = f(r, "yellow_home")+f(r, "yellow_away")
    if t > 0: ys.append((f(r, "fh_ev_yellow_home")+f(r, "fh_ev_yellow_away"))/t)
hs["yellows_events"] = {"n": len(ys), "share": round(st.mean(ys), 4), "obs_sd": round(math.sqrt(st.variance(ys)), 4)}
out["half_shares_post_era"] = hs

# climate check: highland home venues (Abha / Khamis Mushait, ~2,000 m+) vs lowland
HIGH = {"Abha", "Khamis Mushait"}
def home_edge(rows):
    return round(st.mean([int(r["home_goals"]) for r in rows]) - st.mean([int(r["away_goals"]) for r in rows]), 3), len(rows)
hi = [r for r in ROWS if r["season"] in POST_ALL and (r["stadium_city"] or "") in HIGH]
lo = [r for r in ROWS if r["season"] in POST_ALL and (r["stadium_city"] or "") not in HIGH and r["stadium_city"]]
out["climate_highland_home_edge"] = home_edge(hi); out["climate_lowland_home_edge"] = home_edge(lo)
out["climate_cities_highland"] = sorted(set(r["stadium_city"] for r in hi))

# dev-window over-rates for primary lines (dev = POST_DEV pooled, n=612)
devr = [r for r in ROWS if r["season"] in POST_DEV]
def over_rate(vals, line): return round(st.mean([1 if v > line else 0 for v in vals]), 3)
lines = {}
for name, fn in [("sot", lambda r: f(r, "ShotsOnTarget_home")+f(r, "ShotsOnTarget_away")),
                 ("corners", lambda r: f(r, "corners_home")+f(r, "corners_away")),
                 ("shots", lambda r: f(r, "total_shots_home")+f(r, "total_shots_away")),
                 ("yellows", lambda r: f(r, "yellow_home")+f(r, "yellow_away"))]:
    vals = [fn(r) for r in devr]
    cands = [x+0.5 for x in range(int(min(vals)), int(max(vals)))]
    best = min(cands, key=lambda L: abs(over_rate(vals, L)-0.5))
    lines[name] = {"mean": round(st.mean(vals), 3), "primary_line": best, "over_rate": over_rate(vals, best),
                   "ladder": {str(L): over_rate(vals, L) for L in (best-1, best, best+1)}}
lines["goals_ou25_dev"] = over_rate([int(r["home_goals"])+int(r["away_goals"]) for r in devr], 2.5)
out["dev_lines"] = lines
json.dump(out, open(HERE / "eda_numbers.json", "w"), indent=1, default=str)
print(json.dumps(out, indent=1, default=str))
