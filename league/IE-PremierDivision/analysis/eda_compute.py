"""Compute the IE-PremierDivision EDA ledger.  No model fitting occurs here."""
import csv, json, math, statistics as st
from collections import defaultdict, Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROWS = list(csv.DictReader(open(HERE.parent / "data" / "ie_matches.csv")))
DEV = [r for r in ROWS if r["season"] != "2026"]
DEV_SEASONS = ["2021", "2022", "2023", "2024", "2025"]

def f(r, key):
    v = r.get(key)
    return None if v in (None, "", "None") else float(v)

def mean(xs): return st.mean(xs) if xs else None

def corr_halves(series, minimum=10):
    xs, ys = [], []
    for vals in series.values():
        if len(vals) >= minimum:
            xs.append(st.mean(vals[0::2])); ys.append(st.mean(vals[1::2]))
    if len(xs) < 5: return None, len(xs)
    mx, my = st.mean(xs), st.mean(ys)
    den = math.sqrt(sum((x-mx)**2 for x in xs) * sum((y-my)**2 for y in ys))
    return (sum((x-mx)*(y-my) for x, y in zip(xs, ys))/den if den else None), len(xs)

def team_series(key, against=False):
    d = defaultdict(list)
    for r in DEV:
        for side, opp in (("home", "away"), ("away", "home")):
            k = f"{key}_{opp if against else side}"
            v = f(r, k)
            if v is not None: d[r[f"{side}_team"]].append(v)
    return d

def reliability(key, against=False):
    r, n = corr_halves(team_series(key, against))
    return {"r": round(r, 3) if r is not None else None, "n_teams": n}

def half_share(rows, value_fn, weight_fn):
    shares, weights = [], []
    for r in rows:
        one, total = value_fn(r), weight_fn(r)
        if one is not None and total is not None and total > 0:
            shares.append(one / total); weights.append(total)
    if len(shares) < 2: return {"n": len(shares), "share": None, "obs_sd": None, "true_sd": None}
    m, obs_var = st.mean(shares), st.variance(shares)
    noise = st.mean([m*(1-m)/w for w in weights])
    return {"n": len(shares), "share": round(m, 4), "obs_sd": round(math.sqrt(obs_var), 4),
            "true_sd": round(math.sqrt(max(obs_var-noise, 0)), 4)}

def total(r, key):
    a, b = f(r, f"{key}_home"), f(r, f"{key}_away")
    return None if a is None or b is None else a+b

out = {"n": len(ROWS), "seasons": DEV_SEASONS + ["2026"]}
per = {}
for season in DEV_SEASONS:
    rs = [r for r in ROWS if r["season"] == season]
    def cov(key): return round(100 * sum(f(r, key) is not None for r in rs) / len(rs), 1)
    def avg(key): return round(mean([total(r, key) for r in rs if total(r, key) is not None]), 3) if any(total(r, key) is not None for r in rs) else None
    per[season] = {"n": len(rs), "first_date": min(r["date"] for r in rs), "last_date": max(r["date"] for r in rs),
                   "goals": round(mean([int(r["home_goals"])+int(r["away_goals"]) for r in rs]), 3),
                   "home_goals": round(mean([int(r["home_goals"]) for r in rs]), 3),
                   "away_goals": round(mean([int(r["away_goals"]) for r in rs]), 3),
                   "sot": avg("ShotsOnTarget"), "corners": avg("corners"), "shots": avg("total_shots"),
                   "yellows_stats": avg("yellow_cards"), "yellows_events": round(mean([int(r["yellow_home"])+int(r["yellow_away"]) for r in rs]), 3),
                   "reds": avg("red_cards"), "xg": avg("expected_goals"), "cov_stats": round(100*mean([int(r["has_stats_all"]) for r in rs]), 1),
                   "cov_half": round(100*mean([int(r["has_stats_half"]) for r in rs]), 1), "cov_shotmap": round(100*mean([int(r["has_shotmap"]) for r in rs]), 1),
                   "cov_infoBox_referee": round(100*sum(bool(r["referee"] is not None) for r in rs)/len(rs), 1),
                   "cov_named_referee": round(100*sum(bool(r["referee"]) for r in rs)/len(rs), 1),
                   "cov_touches": cov("touches_opp_box_home"), "cov_xg": cov("expected_goals_home")}
rs = [r for r in ROWS if r["season"] == "2026"]
per["2026"] = {"n": len(rs), "first_date": min(r["date"] for r in rs), "last_date": max(r["date"] for r in rs),
               "coverage_inventory_only": {"stats_all": sum(int(r["has_stats_all"]) for r in rs), "stats_half": sum(int(r["has_stats_half"]) for r in rs),
               "shotmap": sum(int(r["has_shotmap"]) for r in rs), "named_referee": sum(bool(r["referee"]) for r in rs)}}
out["per_season"] = per
out["round_distribution"] = {s: dict(sorted(Counter(r["round"] for r in ROWS if r["season"] == s).items(), key=lambda x: int(x[0]) if x[0].isdigit() else 999)) for s in out["seasons"]}
out["phase_distribution"] = {s: dict(Counter(r["phase"] for r in ROWS if r["season"] == s)) for s in out["seasons"]}

agree = [r for r in DEV if f(r, "yellow_cards_home") is not None and f(r, "yellow_cards_away") is not None]
out["yellows_stats_vs_events"] = {"n_matches_with_stats": len(agree), "exact_agreement_pct": round(100*sum(total(r,"yellow_cards") == total(r,"yellow") for r in agree)/len(agree), 1) if agree else None}

rel = {}
for label, key in [("goals", "goals"), ("sot", "ShotsOnTarget"), ("corners", "corners"), ("shots", "total_shots"), ("yellows", "yellow"), ("touches", "touches_opp_box"), ("big_chance", "big_chance"), ("possession", "BallPossesion")]:
    if key == "goals":
        for_against = []
        dfor, dagainst = defaultdict(list), defaultdict(list)
        for r in DEV:
            dfor[r["home_team"]].append(float(r["home_goals"])); dfor[r["away_team"]].append(float(r["away_goals"]))
            dagainst[r["home_team"]].append(float(r["away_goals"])); dagainst[r["away_team"]].append(float(r["home_goals"]))
        a, na = corr_halves(dfor); b, nb = corr_halves(dagainst)
        rel[label] = {"for": {"r": round(a,3) if a is not None else None, "n_teams": na}, "against": {"r": round(b,3) if b is not None else None, "n_teams": nb}}
    else:
        rel[label] = {"for": reliability(key), "against": reliability(key, True)}
out["reliability"] = rel

def named_ref_series():
    d = defaultdict(list)
    for r in DEV:
        if r["referee"]: d[r["referee"]].append(int(r["yellow_home"])+int(r["yellow_away"]))
    return d
rr, nr = corr_halves(named_ref_series())
out["referee_reliability_events"] = {"r": round(rr,3) if rr is not None else None, "n_named_refs_ge10": nr,
                                     "named_referee_matches": sum(bool(r["referee"]) for r in DEV)}

def era_insufficient(label):
    return {"status": "ERA-INSUFFICIENT", "r": None, "dev_seasons_available": ["2025"], "n_dev_seasons": 1, "note": label}
out["era_reliability"] = {"sp_share": era_insufficient("stats xG splits exist only in 2025–2026; 2026 is virgin"),
                           "xg_per_shot": era_insufficient("xG/shot exists only in 2025–2026; 2026 is virgin"),
                           "xgot_per_shot": era_insufficient("shotmap xGOT exists only in 2025–2026; 2026 is virgin")}

def event_goal_one(r): return int(r["ht_home_goals"])+int(r["ht_away_goals"])
def event_goal_total(r): return int(r["home_goals"])+int(r["away_goals"])
def event_yellow_one(r): return int(r["ev_yellow_fh_home"])+int(r["ev_yellow_fh_away"])
def event_yellow_total(r): return int(r["yellow_home"])+int(r["yellow_away"])
split_rows = [r for r in DEV if r["season"] in {"2023", "2024", "2025"}]
event_rows = [r for r in DEV if r["season"] in set(DEV_SEASONS)]
def fh_total(r, key):
    a, b = f(r, f"fh_{key}_home"), f(r, f"fh_{key}_away")
    return None if a is None or b is None else a+b
out["half_shares"] = {
    "goals_events_2021_2025": half_share(event_rows, event_goal_one, event_goal_total),
    "sot_2023_2025": half_share(split_rows, lambda r: fh_total(r, "ShotsOnTarget"), lambda r: total(r,"ShotsOnTarget")),
    "corners_2023_2025": half_share(split_rows, lambda r: fh_total(r, "corners"), lambda r: total(r,"corners")),
    "shots_2023_2025": half_share(split_rows, lambda r: fh_total(r, "total_shots"), lambda r: total(r,"total_shots")),
    "yellows_events_2021_2025": half_share(event_rows, event_yellow_one, event_yellow_total),
    "yellows_stats_crosscheck_2023_2025": half_share([r for r in split_rows if f(r,"fh_yellow_cards_home") is not None and f(r,"fh_yellow_cards_away") is not None], lambda r: f(r,"fh_yellow_cards_home")+f(r,"fh_yellow_cards_away"), lambda r: total(r,"yellow_cards")),
}
out["halves_constants"] = {"goals_1h_share": out["half_shares"]["goals_events_2021_2025"]["share"], "sot_1h_share": out["half_shares"]["sot_2023_2025"]["share"],
                            "corners_1h_share": out["half_shares"]["corners_2023_2025"]["share"], "total_shots_1h_share": out["half_shares"]["shots_2023_2025"]["share"],
                            "yellow_cards_1h_share": out["half_shares"]["yellows_events_2021_2025"]["share"]}

def mover_check():
    transitions, details = [], []
    teams = {s: set(r["home_team_id"] for r in ROWS if r["season"] == s) | set(r["away_team_id"] for r in ROWS if r["season"] == s) for s in out["seasons"]}
    means = {s: mean([int(r["home_goals"])+int(r["away_goals"]) for r in ROWS if r["season"] == s]) for s in out["seasons"]}
    for i, s in enumerate(DEV_SEASONS[1:], 1):
        promoted = teams[s] - teams[DEV_SEASONS[i-1]]
        for tid in promoted:
            rs = [r for r in ROWS if r["season"] == s and (r["home_team_id"] == tid or r["away_team_id"] == tid)]
            gf = sum(int(r["home_goals"] if r["home_team_id"] == tid else r["away_goals"]) for r in rs)/len(rs)
            ga = sum(int(r["away_goals"] if r["home_team_id"] == tid else r["home_goals"]) for r in rs)/len(rs)
            transitions.append({"season": s, "team": rs[0]["home_team"] if rs[0]["home_team_id"] == tid else rs[0]["away_team"], "matches": len(rs), "gf_per_match": round(gf,3), "ga_per_match": round(ga,3), "league_goals_per_match": round(means[s],3)})
    return {"n_transitions": len(transitions), "transitions": transitions}
out["mover_check"] = mover_check()

market_lines = {"goals": ([1.5,2.5,3.5], {"2022","2023","2024","2025"}), "sot": ([7.5,8.5,9.5], {"2023","2024","2025"}),
                "corners": ([9.5,10.5,11.5], {"2023","2024","2025"}), "cards": ([3.5,4.5,5.5], {"2022","2023","2024","2025"}),
                "total_shots": ([23.5,24.5,25.5,26.5], {"2023","2024","2025"})}
keys = {"goals":"goals", "sot":"ShotsOnTarget", "corners":"corners", "cards":"yellow", "total_shots":"total_shots"}
primary = {}
for market, (lines, seasons) in market_lines.items():
    rs = [r for r in ROWS if r["season"] in seasons]
    def market_total(r):
        return int(r["home_goals"])+int(r["away_goals"]) if market == "goals" else total(r, keys[market])
    rates = {str(line): round(100*mean([int(market_total(r) > line) for r in rs if market_total(r) is not None]),1) for line in lines}
    chosen = min(lines, key=lambda x: abs(rates[str(x)]/100-0.5))
    primary[market] = {"dev_seasons": sorted(seasons), "n_matches": len(rs), "over_rates_pct": rates, "primary_line": chosen, "primary_over_rate_pct": rates[str(chosen)]}
out["primary_lines"] = primary

json.dump(out, open(HERE / "eda_numbers.json", "w"), indent=1)
print(json.dumps(out, indent=1))
