"""Pre-fit EDA for FI-Ykkosliiga.  Never loads a model or virgin fit."""
import csv, json, math, statistics
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROWS = list(csv.DictReader(open(HERE.parent / "data" / "yk_matches.csv")))
SEASONS = sorted({r["season"] for r in ROWS})
def fl(v):
    try: return float(v)
    except (TypeError, ValueError): return None
def ints(r):
    for k in r:
        if k not in {"match_id", "season", "date", "phase", "home_team", "away_team", "home_team_id", "away_team_id", "referee", "ht_source"}:
            x = fl(r[k]); r[k] = x if x is not None else r[k]
for r in ROWS: ints(r)
def mean(xs): return round(statistics.mean(xs), 4) if xs else None
def corr(a, b):
    if len(a) < 3: return None
    ma, mb = statistics.mean(a), statistics.mean(b)
    va, vb = sum((x-ma)**2 for x in a), sum((y-mb)**2 for y in b)
    return round(sum((x-ma)*(y-mb) for x,y in zip(a,b))/math.sqrt(va*vb), 4) if va and vb else None
def reliability(for_key, seasons=tuple(s for s in SEASONS if s != "2026")):
    parts = defaultdict(lambda: [[], []]); counts = defaultdict(int)
    for r in sorted((x for x in ROWS if x["season"] in seasons), key=lambda x:(x["date"],x["match_id"])):
        for side in ("home", "away"):
            tid = r[f"{side}_team_id"]
            if for_key == "goals_against": val = r["away_goals"] if side == "home" else r["home_goals"]
            elif for_key == "yellow_against": val = r["yellow_away"] if side == "home" else r["yellow_home"]
            else: val = r.get(for_key.format(side=side))
            if not isinstance(val, (float, int)): continue
            j = counts[tid] % 2; parts[tid][j].append(val); counts[tid] += 1
    def one():
        pairs = [(a,b) for a,b in (parts[t] for t in parts) if len(a) >= 8 and len(b) >= 8]
        return {"n_teams": len(pairs), "r": corr([mean(a) for a,b in pairs], [mean(b) for a,b in pairs])}
    return one()
def halves(num_key, den_key, seasons):
    vals=[]; total_num=total_den=0
    for r in ROWS:
        if r["season"] not in seasons: continue
        n,d=r.get(num_key),r.get(den_key)
        if isinstance(n,(float,int)) and isinstance(d,(float,int)) and d>0:
            vals.append(n/d); total_num += n; total_den += d
    p=total_num/total_den; obs=statistics.variance(vals); avg_d=total_den/len(vals)
    bino=p*(1-p)/avg_d
    return {"share":round(p,6),"n_matches":len(vals),"n_events":int(total_den),"observed_var":round(obs,6),"binomial_noise_var":round(bino,6),"excess_var":round(obs-bino,6)}
def split_share(prefix, season):
    rows=[r for r in ROWS if r["season"]==season and isinstance(r.get(f"fh_{prefix}_home"),(float,int)) and (r.get(f"{prefix}_home") or 0)+(r.get(f"{prefix}_away") or 0)>0]
    n=sum(r[f"fh_{prefix}_home"]+r[f"fh_{prefix}_away"] for r in rows); d=sum(r[f"{prefix}_home"]+r[f"{prefix}_away"] for r in rows)
    return {"share":round(n/d,6),"n_matches":len(rows),"n_events":int(d)} if d else None
levels={}; inventory={}
for s in SEASONS:
    sub=[r for r in ROWS if r["season"]==s]; cards=[r for r in sub if r["ev_card_events"]>0]
    inventory[s]={"matches":len(sub),"date_min":min(r["date"] for r in sub),"date_max":max(r["date"] for r in sub),
        "teams":len({r["home_team_id"] for r in sub}|{r["away_team_id"] for r in sub}),
        "stats_nonnull":sum(r["has_stats_all"] for r in sub),"stats_false_positive_index":sum(r["index_has_stats"] for r in sub),
        "period_splits":sum(r["has_stats_half"] for r in sub),"shotmap_nonempty":sum(r["has_shotmap"] for r in sub),
        "events":sum(r["has_events"] for r in sub),"referee_named":sum(bool(r["referee"]) for r in sub),
        "card_event_matches":len(cards),"card_events":int(sum(r["ev_card_events"] for r in sub))}
    goals=[r["home_goals"]+r["away_goals"] for r in sub]
    levels[s]={"n":len(sub),"goals":mean(goals),"home_goals":mean([r["home_goals"] for r in sub]),"away_goals":mean([r["away_goals"] for r in sub]),
        "home_win_rate":mean([r["home_goals"]>r["away_goals"] for r in sub]),"over_2_5_rate":mean([g>2.5 for g in goals]),
        "ht_goals_share":sum(r["goals_1h_total"] for r in sub)/sum(goals) if sum(goals) else None,
        "card_mean":mean([r["ev_yellow_home"]+r["ev_yellow_away"] for r in sub])}
traits={"goals_for":reliability("{side}_goals"),"goals_against":reliability("goals_against"),
        "yellow_for":reliability("yellow_{side}"),"yellow_against":reliability("yellow_against")}
halves_all=halves("goals_1h_total","goals_1h_total",SEASONS) if False else None
goal_half=[]
for r in ROWS:
    den=r["home_goals"]+r["away_goals"]
    if den: goal_half.append((r["goals_1h_total"],den))
def half_from_pairs(pairs):
    vals=[n/d for n,d in pairs]; n=sum(x for x,d in pairs); d=sum(d for x,d in pairs); p=n/d; noise=p*(1-p)/(d/len(pairs))
    return {"share":round(p,6),"n_matches":len(pairs),"n_goals":int(d),"observed_var":round(statistics.variance(vals),6),"binomial_noise_var":round(noise,6),"excess_var":round(statistics.variance(vals)-noise,6)}
dev_seasons=[s for s in SEASONS if s != "2026"]
goal_half_dev=[(r["goals_1h_total"],r["home_goals"]+r["away_goals"]) for r in ROWS if r["season"] in dev_seasons and r["home_goals"]+r["away_goals"]>0]
out={"seasons":SEASONS,"n":len(ROWS),"levels":levels,"inventory":inventory,
     "traits_odd_even":traits,"halves_goals_pooled":half_from_pairs(goal_half_dev),
     "halves_goals_by_season":{s:half_from_pairs([(r["goals_1h_total"],r["home_goals"]+r["away_goals"]) for r in ROWS if r["season"]==s and r["home_goals"]+r["away_goals"]>0]) for s in dev_seasons},
     "halves_splits_2026":None,
     "cards_coverage":{s:{"matches":inventory[s]["matches"],"card_event_matches":inventory[s]["card_event_matches"],"card_events":inventory[s]["card_events"],"coverage":round(inventory[s]["card_event_matches"]/inventory[s]["matches"],6)} for s in SEASONS},
     "team_ids":len({r["home_team_id"] for r in ROWS}|{r["away_team_id"] for r in ROWS}),
     "team_id_name_changes":[]}
# Cross-corpus entrant inventory for X2.  This is descriptive EDA only.
idx_path=Path("/home/hatch/workspace/footballprediction/data_enrichment/fotmob_world_index.csv")
if idx_path.exists():
    source=list(csv.DictReader(open(idx_path)))
    corp={"51":defaultdict(set),"251":defaultdict(set)}; names={}
    for ir in source:
        if ir["league_id"] not in corp: continue
        d=json.load(open("/home/hatch/workspace/footballprediction/"+ir["path"]))
        g=d.get("general") or {}; s=ir["season"]
        for side in ("homeTeam","awayTeam"):
            t=g.get(side) or {}; corp[ir["league_id"]][s].add(str(t.get("id"))); names[str(t.get("id"))]=t.get("name")
    entrant_rows=[]
    for s in SEASONS[1:]:
        prev=str(int(s)-1)
        for tid in sorted(corp["251"][s]-corp["251"].get(prev,set())):
            entrant_rows.append({"season":s,"team_id":tid,"team":names.get(tid),"from_veikkausliiga":tid in corp["51"].get(prev,set())})
    out["x2_entrants"]=entrant_rows
    out["x2_entrant_counts"]={"all":len(entrant_rows),"from_veikkausliiga":sum(x["from_veikkausliiga"] for x in entrant_rows),"from_tier3_or_unknown":sum(not x["from_veikkausliiga"] for x in entrant_rows)}
    diffs=[]
    for e in entrant_rows:
        sub=[r for r in ROWS if r["season"]==e["season"] and e["team_id"] in (str(r["home_team_id"]),str(r["away_team_id"]))]
        if not sub: continue
        gf=mean([r["home_goals"] if str(r["home_team_id"])==e["team_id"] else r["away_goals"] for r in sub])
        ga=mean([r["away_goals"] if str(r["home_team_id"])==e["team_id"] else r["home_goals"] for r in sub])
        league_team_mean=mean([(r["home_goals"]+r["away_goals"])/2 for r in ROWS if r["season"]==e["season"]])
        diffs.append((gf-league_team_mean,ga-league_team_mean))
    out["x2_entrant_gf_ga_diff_vs_league_team_mean"]={"n":len(diffs),"gf_diff":round(statistics.mean(x[0] for x in diffs),4),"ga_diff":round(statistics.mean(x[1] for x in diffs),4)}
json.dump(out,open(HERE/"eda_summary.json","w"),indent=2)
json.dump({"by_season":inventory,"team_ids_total":out["team_ids"]},open(HERE/"inventory_summary.json","w"),indent=2)
print(json.dumps(out,indent=2))
