"""Measured scores/events-only EDA for Poland I Liga."""
import csv, json, math, random, statistics as st
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROWS = list(csv.DictReader((HERE.parent / "data" / "iliga_matches.csv").open()))
INDEX = HERE.parents[2] / "data_enrichment" / "fotmob_world_index.csv"
SHARED = Path("/home/hatch/workspace/footballprediction")
SEASONS = sorted({r["season"] for r in ROWS})
COMPLETE = SEASONS[:-1]

def f(r, k):
    v = r.get(k); return None if v in (None, "", "None") else float(v)
def mean(xs): return round(st.mean(xs), 3) if xs else None
def pct(n, d): return round(100 * n / d, 1) if d else None
def split_half(series, min_n=20, reps=60):
    eligible = {t: v for t, v in series.items() if len(v) >= min_n}; random.seed(42); vals = []
    for _ in range(reps):
        a, b = [], []
        for sample in eligible.values():
            ix = list(range(len(sample))); random.shuffle(ix); cut = len(ix) // 2
            a.append(st.mean([sample[i] for i in ix[:cut]])); b.append(st.mean([sample[i] for i in ix[cut:]]))
        if len(a) >= 5:
            ma, mb = st.mean(a), st.mean(b); den = math.sqrt(sum((x-ma)**2 for x in a)*sum((y-mb)**2 for y in b))
            if den: vals.append(sum((x-ma)*(y-mb) for x,y in zip(a,b))/den)
    return {"r": round(st.mean(vals), 3) if vals else None, "n_teams": len(eligible), "reps": reps, "seed": 42}
def goal_half_stats(rows):
    shares, weights, ht, total = [], [], 0, 0
    for r in rows:
        if r["has_events"] != "1" or f(r,"ht_home_goals") is None: continue
        goals = int(r["home_goals"])+int(r["away_goals"]); first = int(r["ht_home_goals"])+int(r["ht_away_goals"])
        if goals: shares.append(first/goals); weights.append(goals); ht += first; total += goals
    if len(shares) < 30: return {"n": len(shares)}
    p = st.mean(shares); observed = st.variance(shares); noise = st.mean([p*(1-p)/w for w in weights]); true = observed-noise
    return {"n":len(shares), "share_ratio_of_sums":round(ht/total,4), "observed_var":round(observed,4), "true_var":round(true,4), "true_sd":round(math.sqrt(max(0,true)),4)}
def fixture_levels(rs):
    return {"n":len(rs), "n_regular":sum(r["phase"]=="regular" for r in rs), "n_playoff":sum(r["phase"]=="playoff" for r in rs),
            "teams":len({r[k] for r in rs for k in ("home_team_id","away_team_id")}),
            "mean_total_goals":mean([int(r["home_goals"])+int(r["away_goals"]) for r in rs]),
            "mean_home_goals":mean([int(r["home_goals"]) for r in rs]), "mean_away_goals":mean([int(r["away_goals"]) for r in rs]),
            "home_win_pct":pct(sum(int(r["home_goals"])>int(r["away_goals"]) for r in rs),len(rs)),
            "draw_pct":pct(sum(int(r["home_goals"])==int(r["away_goals"]) for r in rs),len(rs)),
            "away_win_pct":pct(sum(int(r["home_goals"])<int(r["away_goals"]) for r in rs),len(rs)),
            "ou2_5_over_rate":round(sum(int(r["home_goals"])+int(r["away_goals"])>2 for r in rs)/len(rs),3),
            "events_coverage_pct":pct(sum(r["has_events"]=="1" for r in rs),len(rs)),
            "ht_goals_coverage_pct":pct(sum(r["has_events"]=="1" for r in rs),len(rs))}

per = {s: fixture_levels([r for r in ROWS if r["season"]==s]) for s in SEASONS}
regular_complete = [r for r in ROWS if r["season"] in COMPLETE and r["phase"]=="regular"]
pooled = fixture_levels(regular_complete); pooled["seasons"] = COMPLETE
series_for, series_against = defaultdict(list), defaultdict(list)
for r in regular_complete:
    series_for[r["home_team_id"]].append(int(r["home_goals"])); series_for[r["away_team_id"]].append(int(r["away_goals"]))
    series_against[r["home_team_id"]].append(int(r["away_goals"])); series_against[r["away_team_id"]].append(int(r["home_goals"]))
dev = [r for r in ROWS if r["season"] in ("2021/2022","2022/2023","2023/2024","2024/2025") and r["phase"]=="regular"]
scored = [r for r in ROWS if r["season"] in ("2022/2023","2023/2024","2024/2025") and r["phase"]=="regular"]
half_rows = [r for r in regular_complete if r["has_events"]=="1"]
out = {"league":"PL-ILiga", "league_id":197, "n":len(ROWS), "seasons":SEASONS, "per_season":per, "pooled_complete_regular":pooled,
       "reliability":{"goals_for":split_half(series_for), "goals_against":split_half(series_against)},
       "half_shares":{"goals":goal_half_stats(half_rows), "source":"events; regular complete seasons"},
       "dev_period":{"seasons":["2021/2022","2022/2023","2023/2024","2024/2025"],"regular_n":len(dev),"scored_seasons":["2022/2023","2023/2024","2024/2025"],"scored_n":len(scored),"ou2_5_over_rate":round(sum(int(r["home_goals"])+int(r["away_goals"])>2 for r in dev)/len(dev),3)},
       "virgin":{"season":"2025/2026","regular_n":sum(r["season"]=="2025/2026" and r["phase"]=="regular" for r in ROWS)}, "confirmatory":{"season":"2026/2027","n":126},
       "card_event_descriptives":{}, "newcomers":[], "newcomer_gaps":{}, "direction_split":{}}
out["dev_period"]["scored_season_ou2_5"] = {s: per[s]["ou2_5_over_rate"] for s in out["dev_period"]["scored_seasons"]}
for s in SEASONS:
    rs=[r for r in ROWS if r["season"]==s]; ev=[r for r in rs if r["has_events"]=="1"]
    out["card_event_descriptives"][s]={"red":sum(int(r["ev_red_home"])+int(r["ev_red_away"])-int(r["ev_yellowred_home"])-int(r["ev_yellowred_away"]) for r in rs),"yellowred":sum(int(r["ev_yellowred_home"])+int(r["ev_yellowred_away"]) for r in rs),"mean_reds_per_match_events":round(sum(int(r["ev_red_home"])+int(r["ev_red_away"]) for r in ev)/len(ev),3) if ev else None,"events_n":len(ev)}
teams={s:{r[k] for r in ROWS if r["season"]==s for k in ("home_team_id","away_team_id")} for s in SEASONS}
team_means=[]
for r in regular_complete: team_means += [(int(r["home_goals"]),int(r["away_goals"])),(int(r["away_goals"]),int(r["home_goals"]))]
for i,s in enumerate(SEASONS[1:],1):
    for team in sorted(teams[s]-teams[SEASONS[i-1]]):
        vals=[(int(r["home_goals"]),int(r["away_goals"])) if r["home_team_id"]==team else (int(r["away_goals"]),int(r["home_goals"])) for r in ROWS if r["season"]==s and r["phase"]=="regular" and team in (r["home_team_id"],r["away_team_id"])]
        out["newcomers"].append({"season":s,"team_id":team,"n":len(vals),"gf":mean([x[0] for x in vals]),"ga":mean([x[1] for x in vals])})
nm=out["newcomers"]; lgf=mean([x[0] for x in team_means]); lga=mean([x[1] for x in team_means]); ngf=mean([x["gf"] for x in nm]); nga=mean([x["ga"] for x in nm])
out["newcomer_gaps"]={"n":len(nm),"expected_per_transition":3,"newcomer_gf":ngf,"newcomer_ga":nga,"league_team_gf":lgf,"league_team_ga":lga,"gf_gap":round(ngf-lgf,3),"ga_gap":round(nga-lga,3)}
out["newcomer_gaps"]["by_transition"]={s:{"n":len(g),"gf":mean([x["gf"] for x in g]),"ga":mean([x["ga"] for x in g]),"gf_gap":round(mean([x["gf"] for x in g])-lgf,3),"ga_gap":round(mean([x["ga"] for x in g])-lga,3)} for s in SEASONS[1:] if (g:=[x for x in nm if x["season"]==s])}
def payload(row):
    p=HERE.parents[2]/row["path"]; return p if p.exists() else SHARED/row["path"]
membership=defaultdict(set)
for ir in csv.DictReader(INDEX.open()):
    if ir["league_id"] not in {"196","197","8935"}: continue
    try: d=json.loads(payload(ir).read_text()); g=d.get("general") or {}
    except FileNotFoundError: continue
    for side in ("homeTeam","awayTeam"):
        tid=(g.get(side) or {}).get("id")
        if tid is not None: membership[(ir["season"],str(tid))].add(ir["league_id"])
for s in SEASONS[1:]:
    prior=SEASONS[SEASONS.index(s)-1]
    for direction,lid in (("from_ekstraklasa","196"),("from_ii_liga","8935")):
        group=[x for x in nm if x["season"]==s and lid in membership.get((prior,str(x["team_id"])),set())]
        if group: out["direction_split"].setdefault(direction,[]).append({"season":s,"n":len(group),"gf":mean([x["gf"] for x in group]),"ga":mean([x["ga"] for x in group]),"gf_gap":round(mean([x["gf"] for x in group])-lgf,3),"ga_gap":round(mean([x["ga"] for x in group])-lga,3)})
for direction, vals in list(out["direction_split"].items()):
    out["direction_split"][direction+"_pooled"]={"n":sum(x["n"] for x in vals),"gf":mean([x["gf"] for x in vals for _ in range(x["n"])]),"ga":mean([x["ga"] for x in vals for _ in range(x["n"])]),"gf_gap":round(mean([x["gf"] for x in vals for _ in range(x["n"])])-lgf,3),"ga_gap":round(mean([x["ga"] for x in vals for _ in range(x["n"])])-lga,3)}
(HERE/"eda_numbers.json").write_text(json.dumps(out,indent=2)+"\n")
inventory={"league_id":197,"n_index_rows":1671,"n_match_rows":len(ROWS),"n_team_match_rows":len(ROWS)*2,"seasons":per,"phase_rule":"regular for matchRound 1–34; playoff for matchRound 1/2 and final; playoff rows retained","coverage":{"stats_pct":0.0,"shotmap_pct":0.0,"referee_pct":0.0,"events_pct":94.4},"cards_note":"Cards are descriptive only: events contain Red and YellowRed; no plain Yellow source exists; target card columns are None with cards_source=none."}
(HERE/"inventory_summary.json").write_text(json.dumps(inventory,indent=2)+"\n")
print(json.dumps(out,indent=2))

