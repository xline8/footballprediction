"""EDA computations for ENG-Championship -> eda_numbers.json (for EDA.md)."""
import csv, json, math, statistics as st
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROWS = list(csv.DictReader(open(HERE.parent / "data" / "engl1_matches.csv")))

def f(r, k):
    v = r.get(k)
    return None if v in (None, "", "None") else float(v)

def split_half(vals_by_team):
    """vals_by_team: team -> list of per-match values; odd/even split-half corr of team means."""
    xs, ys = [], []
    for t, vs in vals_by_team.items():
        if len(vs) >= 10:
            xs.append(st.mean(vs[0::2])); ys.append(st.mean(vs[1::2]))
    if len(xs) < 5: return None, len(xs)
    mx, my = st.mean(xs), st.mean(ys)
    num = sum((a-mx)*(b-my) for a, b in zip(xs, ys))
    den = math.sqrt(sum((a-mx)**2 for a in xs) * sum((b-my)**2 for b in ys))
    return (num/den if den else None), len(xs)

def team_series(key_for, key_against=None):
    d = defaultdict(list)
    for r in ROWS:
        for side in ("home", "away"):
            v = f(r, f"{key_for}_{side}")
            if v is not None: d[r[f"{side}_team"]].append(v)
    return d

out = {}
out["n"] = len(ROWS)
seasons = sorted(set(r["season"] for r in ROWS))
out["seasons"] = seasons
# coverage + levels per season
per = {}
for s in seasons:
    rs = [r for r in ROWS if r["season"] == s]
    def cov(k): return round(100*sum(1 for r in rs if f(r, k) is not None)/len(rs), 1)
    def tot(k): 
        vals = [f(r, f"{k}_home") + f(r, f"{k}_away") for r in rs if f(r, f"{k}_home") is not None]
        return round(st.mean(vals), 3) if vals else None
    per[s] = {
        "n": len(rs),
        "goals": round(st.mean(r["home_goals"] and 0 or 0) if False else st.mean([int(r["home_goals"])+int(r["away_goals"]) for r in rs]), 3),
        "home_goals": round(st.mean([int(r["home_goals"]) for r in rs]), 3),
        "away_goals": round(st.mean([int(r["away_goals"]) for r in rs]), 3),
        "sot": tot("ShotsOnTarget"), "corners": tot("corners"), "shots": tot("total_shots"),
        "yellows_stats": tot("yellow_cards"), "yellows_events": round(st.mean([r["ev_yellow_home"] and 0 or 0 for r in rs]), 3) if False else round(st.mean([int(r["ev_yellow_home"])+int(r["ev_yellow_away"]) for r in rs]), 3),
        "reds": tot("red_cards"),
        "xg": tot("expected_goals"),
        "cov_stats": round(100*st.mean([int(r["has_stats_all"]) for r in rs]), 1),
        "cov_half": round(100*st.mean([int(r["has_stats_half"]) for r in rs]), 1),
        "cov_shotmap": round(100*st.mean([int(r["has_shotmap"]) for r in rs]), 1),
        "cov_ref": round(100*sum(1 for r in rs if r["referee"])/len(rs), 1),
        "cov_touches": cov("touches_opp_box_home"),
        "cov_xg": cov("expected_goals_home"),
        "phases": {p: sum(1 for r in rs if r["phase"] == p) for p in ("regular", "playoff")},
    }
out["per_season"] = per
# stats-vs-events yellows agreement (complete seasons)
agree = [r for r in ROWS if f(r, "yellow_cards_home") is not None]
out["yellows_stats_vs_events_exact"] = round(100*sum(1 for r in agree if f(r,"yellow_cards_home")+f(r,"yellow_cards_away") == int(r["ev_yellow_home"])+int(r["ev_yellow_away"]))/len(agree), 1)
# xG calibration: goals/xG per season
out["goals_per_xg"] = {s: round(sum(int(r["home_goals"])+int(r["away_goals"]) for r in ROWS if r["season"]==s) / sum(f(r,"expected_goals_home")+f(r,"expected_goals_away") for r in ROWS if r["season"]==s and f(r,"expected_goals_home") is not None), 3) for s in seasons}
# reliabilities (career-pooled split-half)
rel = {}
for name, key in [("goals_for","goals"), ("sot_for","ShotsOnTarget"), ("corners_for","corners"),
                  ("shots_for","total_shots"), ("yellows_for","yellow_cards"),
                  ("xg_for","expected_goals"), ("touches_for","touches_opp_box"),
                  ("bigchance_for","big_chance"), ("possession","BallPossesion")]:
    if key == "goals":
        d = defaultdict(list)
        for r in ROWS:
            d[r["home_team"]].append(int(r["home_goals"])); d[r["away_team"]].append(int(r["away_goals"]))
    else:
        d = team_series(key)
    rel[name] = split_half(d)
out["reliability"] = {k: (round(v[0],3) if v[0] is not None else None, v[1]) for k, v in rel.items()}
# set-play share reliability + xg/shot + xgot (2025 era: seasons 2025/2026+)
def ratio_series(num, den, seasons_filter=None):
    d = defaultdict(lambda: [0.0, 0.0, 0])  # handled below via per-match ratio of sums on halves
    per_team_matches = defaultdict(list)
    for r in ROWS:
        if seasons_filter and r["season"] not in seasons_filter: continue
        for side in ("home", "away"):
            n_, d_ = f(r, f"{num}_{side}"), f(r, f"{den}_{side}")
            if n_ is not None and d_ is not None: per_team_matches[r[f"{side}_team"]].append((n_, d_))
    xs, ys = [], []
    for t, ms in per_team_matches.items():
        if len(ms) >= 10:
            for half, acc in ((ms[0::2], xs), (ms[1::2], ys)):
                sn = sum(a for a, b in half); sd = sum(b for a, b in half)
                acc.append(sn/sd if sd else 0)
    if len(xs) < 5: return None, len(xs)
    mx, my = st.mean(xs), st.mean(ys)
    num_ = sum((a-mx)*(b-my) for a, b in zip(xs, ys)); den_ = math.sqrt(sum((a-mx)**2 for a in xs)*sum((b-my)**2 for b in ys))
    return (round(num_/den_, 3) if den_ else None), len(xs)
out["sp_share_rel"] = ratio_series("expected_goals_set_play", "expected_goals")
out["xg_per_shot_rel"] = ratio_series("sm_xg", "sm_shots")
era = [s for s in seasons if s >= "2025/2026"]
out["xgot_rel_era"] = ratio_series("sm_xgot", "sm_xgot_n", seasons_filter=set(era))
out["xgot_coverage"] = {s: round(100*sum(1 for r in ROWS if r["season"]==s for side in ("home","away") if f(r,f"sm_shots_{side}") and f(r,f"sm_xgot_n_{side}")==f(r,f"sm_shots_{side}"))/ (2*len([r for r in ROWS if r["season"]==s])),1) for s in seasons}
# half shares + true variance (ANOVA-style: observed var of per-match share minus binomial noise var)
def half_share(num1h, den_all, label):
    shares, weights = [], []
    for r in ROWS:
        a1 = f(r, f"fh_{num1h}_home"); a2 = f(r, f"fh_{num1h}_away")
        b1 = f(r, f"{den_all}_home"); b2 = f(r, f"{den_all}_away")
        if None in (a1, a2, b1, b2) or (b1+b2) == 0: continue
        shares.append((a1+a2)/(b1+b2)); weights.append(b1+b2)
    n = len(shares); m = st.mean(shares)
    obs_var = st.variance(shares)
    noise = st.mean([m*(1-m)/w for w in weights])
    return {"n": n, "share": round(m, 4), "obs_sd": round(math.sqrt(obs_var), 4), "true_sd": round(math.sqrt(max(obs_var-noise, 0.0)), 4)}
out["half_shares"] = {
    "goals": half_share("total_shots", "total_shots", "x") if False else None,
}
# goals half share from HT events (all matches have events) + stats fh goals not a stat key; use events HT
gshares = []
for r in ROWS:
    tot = int(r["home_goals"])+int(r["away_goals"])
    if tot and r["ht_home_goals"] not in (None, ""):
        gshares.append((int(r["ht_home_goals"])+int(r["ht_away_goals"]))/tot)
m = st.mean(gshares); obs = st.variance(gshares)
out["half_shares"]["goals_events"] = {"n": len(gshares), "share": round(m,4), "obs_sd": round(math.sqrt(obs),4)}
out["half_shares"]["sot"] = half_share("ShotsOnTarget", "ShotsOnTarget", "sot")
out["half_shares"]["corners"] = half_share("corners", "corners", "c")
out["half_shares"]["shots"] = half_share("total_shots", "total_shots", "s")
out["half_shares"]["yellows"] = half_share("yellow_cards", "yellow_cards", "y")
del out["half_shares"]["goals"]
# referee reliability
ref_matches = defaultdict(list)
for r in ROWS:
    if r["referee"] and f(r, "yellow_cards_home") is not None:
        ref_matches[r["referee"]].append(f(r,"yellow_cards_home")+f(r,"yellow_cards_away"))
out["ref_rel"] = split_half(ref_matches)
out["n_refs_ge10"] = sum(1 for v in ref_matches.values() if len(v) >= 10)
# Team strength spread (parachute-club distortion check): team goal diff per match
gd = defaultdict(list)
for r in ROWS:
    gd[r["home_team"]].append(int(r["home_goals"])-int(r["away_goals"]))
    gd[r["away_team"]].append(int(r["away_goals"])-int(r["home_goals"]))
means = {t: round(st.mean(v),3) for t, v in gd.items() if len(v) >= 50}
out["team_gd_means"] = dict(sorted(means.items(), key=lambda kv: -kv[1]))
out["team_gd_spread_sd"] = round(st.stdev(list(means.values())), 3)
# home advantage pooled complete seasons
comp = [r for r in ROWS if r["season"] != "2026/2027"]
out["home_edge_complete"] = round(st.mean([int(r["home_goals"]) for r in comp]) - st.mean([int(r["away_goals"]) for r in comp]), 3)
out["ou25_rate_complete"] = round(100*st.mean([1 if int(r["home_goals"])+int(r["away_goals"]) > 2 else 0 for r in comp]), 1)
out["home_win_rate_complete"] = round(100*st.mean([1 if int(r["home_goals"]) > int(r["away_goals"]) else 0 for r in comp]), 1)

# --- Mover analysis (X2): teams entering League One from the Championship (id 48)
# or promoted from League Two (NOT in the warehouse; inferred = new clubs that were
# not in the Championship the previous season) ---
import csv as _csv
_idx = list(_csv.DictReader(open("/home/hatch/workspace/footballprediction/data_enrichment/fotmob_world_index.csv")))
def _teams(lid, s):
    t = set()
    for r in _idx:
        if r["league_id"] == lid and r["season"] == s: t.add(r["home"]); t.add(r["away"])
    return t
_seasons_all = sorted(set(r["season"] for r in ROWS))
movers = {}
for i, s in enumerate(_seasons_all):
    if i == 0: continue
    prev = _seasons_all[i-1]
    cur, prv = _teams("108", s), _teams("108", prev)
    ch_prev = _teams("48", prev)
    new = cur - prv
    entry = {"from_PL": sorted(new & ch_prev), "from_L1": sorted(new - ch_prev), "other": []}
    perf = {}
    for grp, teams in (("from_PL", entry["from_PL"]), ("from_L1", entry["from_L1"])):
        gd_, gf_, n_ = [], [], 0
        for r in ROWS:
            if r["season"] != s: continue
            for side, opp in (("home","away"),("away","home")):
                if r[f"{side}_team"] in teams:
                    gd_.append(int(r[f"{side}_goals"]) - int(r[f"{opp}_goals"])); gf_.append(int(r[f"{side}_goals"])); n_ += 1
        if n_: perf[grp] = {"teams": len(teams), "team_matches": n_, "gd_per_match": round(st.mean(gd_),3), "gf_per_match": round(st.mean(gf_),3)}
    entry["perf"] = perf
    movers[s] = entry
out["movers"] = movers
for grp in ("from_PL","from_L1"):
    gd_, gf_ = [], []
    for s, e in movers.items():
        teams = e[grp]
        for r in ROWS:
            if r["season"] != s: continue
            for side, opp in (("home","away"),("away","home")):
                if r[f"{side}_team"] in teams:
                    gd_.append(int(r[f"{side}_goals"]) - int(r[f"{opp}_goals"])); gf_.append(int(r[f"{side}_goals"]))
    out[f"mover_perf_{grp}"] = {"team_matches": len(gd_), "gd_per_match": round(st.mean(gd_),3) if gd_ else None, "gf_per_match": round(st.mean(gf_),3) if gf_ else None}


# mover GF/GA deltas vs league mu (X2 magnitudes, J1 F4 style)
mu_all = st.mean([int(r["home_goals"])+int(r["away_goals"]) for r in ROWS if r["season"] != "2026/2027"]) / 2
md = {}
for grp in ("from_PL", "from_L1"):
    gf_, ga_ = [], []
    for s, e in movers.items():
        teams = e[grp]
        for r in ROWS:
            if r["season"] != s: continue
            for side, opp in (("home","away"),("away","home")):
                if r[f"{side}_team"] in teams:
                    gf_.append(int(r[f"{side}_goals"])); ga_.append(int(r[f"{opp}_goals"]))
    md[grp] = {"n_team_matches": len(gf_), "gf": round(st.mean(gf_),3), "ga": round(st.mean(ga_),3),
               "gf_delta_vs_mu": round(st.mean(gf_)-mu_all,3), "ga_delta_vs_mu": round(st.mean(ga_)-mu_all,3)}
out["league_mu_complete"] = round(mu_all,3)
out["mover_deltas"] = md

json.dump(out, open(HERE / "eda_numbers.json", "w"), indent=1, default=str)
print(json.dumps(out, indent=1, default=str))
