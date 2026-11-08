"""Deterministic Phase A EDA for Iceland 1. Deild (descriptive only)."""
import csv, json, math, statistics
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
M = list(csv.DictReader((HERE.parent / "data" / "is1_matches.csv").open()))
for r in M:
    for k, v in list(r.items()):
        if k not in {"match_id","league","season","date","round","league_round_name","phase","league_name","home_team","away_team","ht_source","referee"}:
            if v == "": r[k] = None
            else:
                try: r[k] = float(v)
                except ValueError: pass
SEASONS = [str(x) for x in range(2021, 2027)]
DEV = ["2022","2023","2024","2025"]

def mean(xs): return round(statistics.mean(xs), 4) if xs else None

def pearson(pairs):
    pairs = [(x,y) for x,y in pairs if x is not None and y is not None]
    if len(pairs) < 2: return None
    mx,my = mean([x for x,_ in pairs]), mean([y for _,y in pairs])
    xx = sum((x-mx)**2 for x,_ in pairs); yy = sum((y-my)**2 for _,y in pairs)
    return round(sum((x-mx)*(y-my) for x,y in pairs)/math.sqrt(xx*yy),4) if xx and yy else None

def split_trait(seasons, gf=True):
    team=defaultdict(list)
    for r in M:
        if r["season"] not in seasons: continue
        for side,opp in (("home","away"),("away","home")):
            team[r[f"{side}_team_id"]].append((r["date"],r["match_id"],r[f"{side}_goals"] if gf else r[f"{opp}_goals"]))
    pairs=[]
    for vals in team.values():
        vals.sort(key=lambda x:(x[0],x[1]))
        if len(vals)>=20:
            pairs.append((mean([v[2] for i,v in enumerate(vals) if i%2==0]),mean([v[2] for i,v in enumerate(vals) if i%2==1])))
    return {"r":pearson(pairs),"n_teams":len(pairs)}

def half_team_r():
    team=defaultdict(list)
    for r in M:
        if not r["has_events"] or not r["home_goals"]+r["away_goals"]: continue
        for side in ("home","away"):
            ft=r[f"{side}_goals"]
            if ft: team[r[f"{side}_team_id"]].append((r["date"],r["match_id"],r[f"ht_{side}_goals"]/ft))
    pairs=[]
    for vals in team.values():
        vals.sort(key=lambda x:(x[0],x[1]))
        if len(vals)>=20:
            pairs.append((mean([v[2] for i,v in enumerate(vals) if i%2==0]),mean([v[2] for i,v in enumerate(vals) if i%2==1])))
    return {"r":pearson(pairs),"n_teams":len(pairs)}

def source_membership(league_id, season):
    base=Path("/home/hatch/workspace/footballprediction")
    with (base/"data_enrichment"/"fotmob_world_index.csv").open() as fh:
        rows=[r for r in csv.DictReader(fh) if r["league_id"]==str(league_id) and r["season"]==str(season)]
    out={}
    for ir in rows:
        try: d=json.load((base/ir["path"]).open())
        except (FileNotFoundError,json.JSONDecodeError): continue
        g=d.get("general") or {}
        for side in ("homeTeam","awayTeam"):
            t=g.get(side) or {}
            if t.get("id") is not None: out[t["id"]]=t.get("name")
    return out

levels={}
for s in SEASONS:
    rows=[r for r in M if r["season"]==s]
    levels[s]={"n":len(rows),"score_n":len(rows),"stats_n":sum(r["has_stats_all"] for r in rows),"period_splits_n":sum(r["has_stats_half"] for r in rows),"events_n":sum(r["has_events"] for r in rows),"referee_named":sum(bool(r["referee"]) for r in rows),"shotmap_n":sum(bool(r["sm_shots_home"] or r["sm_shots_away"]) for r in rows),"xg_n":0,"plain_yellow_events_n":0,"has_extra_time_n":sum(r["has_extra_time"] for r in rows),"goals_per_match":mean([r["home_goals"]+r["away_goals"] for r in rows]),"home_goals_per_match":mean([r["home_goals"] for r in rows]),"away_goals_per_match":mean([r["away_goals"] for r in rows]),"home_win_rate":mean([r["home_goals"]>r["away_goals"] for r in rows]),"draw_rate":mean([r["home_goals"]==r["away_goals"] for r in rows]),"away_win_rate":mean([r["home_goals"]<r["away_goals"] for r in rows]),"event_red_home":sum(r["ev_red_home"] for r in rows),"event_red_away":sum(r["ev_red_away"] for r in rows),"event_red_total":sum(r["ev_red_home"]+r["ev_red_away"] for r in rows)}
pooled=[r for r in M if r["season"] in DEV]
def ou(rows): return mean([r["home_goals"]+r["away_goals"]>2.5 for r in rows])
phase_levels={p:{"n":sum(r["phase"]==p for r in M),"goals_per_match":mean([r["home_goals"]+r["away_goals"] for r in M if r["phase"]==p])} for p in ("regular","playoff")}
half_rows=[r for r in M if r["has_events"] and r["home_goals"]+r["away_goals"]>0]
total_ft=sum(r["home_goals"]+r["away_goals"] for r in half_rows); total_1h=sum(r["goals_1h_total"] for r in half_rows); p=total_1h/total_ft
shares=[r["goals_1h_total"]/(r["home_goals"]+r["away_goals"]) for r in half_rows]
noise=[p*(1-p)/(r["home_goals"]+r["away_goals"]) for r in half_rows]
entrant_rows=[]; origin_pools=defaultdict(list)
for s in range(2022,2027):
    season=str(s)
    prior={int(r["home_team_id"]) for r in M if r["season"]==str(s-1)}|{int(r["away_team_id"]) for r in M if r["season"]==str(s-1)}
    ids={int(r["home_team_id"]) for r in M if r["season"]==season}|{int(r["away_team_id"]) for r in M if r["season"]==season}
    besta=source_membership(215,s-1); d2=source_membership(10226,s-1)
    for tid in sorted(ids-prior):
        rows=[r for r in M if r["season"]==season and (int(r["home_team_id"])==tid or int(r["away_team_id"])==tid)]
        name=next(r["home_team"] if int(r["home_team_id"])==tid else r["away_team"] for r in rows)
        origin="Besta deildin" if tid in besta else ("2. Deild" if tid in d2 else "unverified")
        gf=mean([r["home_goals"] if int(r["home_team_id"])==tid else r["away_goals"] for r in rows]); ga=mean([r["away_goals"] if int(r["home_team_id"])==tid else r["home_goals"] for r in rows])
        league_rows=[r for r in M if r["season"]==season]; lgf=mean([r["home_goals"]+r["away_goals"] for r in league_rows])/2
        rec={"season":season,"team_id":tid,"team":name,"origin":origin,"matches":len(rows),"gf_per_match":gf,"ga_per_match":ga,"gf_deviation":round(gf-lgf,4),"ga_deviation":round(ga-lgf,4)}
        entrant_rows.append(rec); origin_pools[origin].append(rec)
summary={"n_matches":len(M),"seasons":SEASONS,"levels":levels,"pooled_outcomes":{"home_win_rate":mean([r["home_goals"]>r["away_goals"] for r in M]),"draw_rate":mean([r["home_goals"]==r["away_goals"] for r in M]),"away_win_rate":mean([r["home_goals"]<r["away_goals"] for r in M])},"dev_over_rate_ou2_5":ou(pooled),"dev_over_rate_ou2_5_by_season":{s:ou([r for r in M if r["season"]==s]) for s in DEV},"phase_levels":phase_levels,"f2":{"goals_for":split_trait(SEASONS,True),"goals_against":split_trait(SEASONS,False),"by_season":{s:{"goals_for":split_trait([s],True),"goals_against":split_trait([s],False)} for s in SEASONS},"not_testable":["sot","corners","shots","cards"]},"f3":{"n_matches_with_events_and_goals":len(half_rows),"total_ft_goals":total_ft,"total_1h_goals":total_1h,"goals_1h_share":round(p,4),"by_season":{},"observed_variance":round(statistics.variance(shares),6),"binomial_noise_floor_mean":round(statistics.mean(noise),6),"team_split_half":half_team_r()},"f4":{"entrants":entrant_rows,"pooled_by_origin":{o:{"n":len(v),"mean_gf_deviation":round(mean([x["gf_deviation"] for x in v]),4),"mean_ga_deviation":round(mean([x["ga_deviation"] for x in v]),4)} for o,v in origin_pools.items()}},"f5_event_red_total_by_season":{s:levels[s]["event_red_total"] for s in SEASONS},"f6_referees_named":sum(bool(r["referee"]) for r in M),"team_id_count":len({r["home_team_id"] for r in M}|{r["away_team_id"] for r in M}),"eventless_match_ids":[r["match_id"] for r in M if not r["has_events"]],"mismatch_match_id":"3794991","mover_source_10226_malformed_payloads":16}
for s in SEASONS:
    rr=[r for r in half_rows if r["season"]==s]; den=sum(r["home_goals"]+r["away_goals"] for r in rr)
    summary["f3"]["by_season"][s]={"n":len(rr),"share":round(sum(r["goals_1h_total"] for r in rr)/den,4) if den else None}
json.dump(summary,(HERE/"eda_summary.json").open("w"),indent=2)
inventory={"index_rows":812,"built_match_rows":len(M),"built_team_match_rows":len(M)*2,"by_season":levels,"phase_counts":dict(Counter(r["phase"] for r in M)),"eventless_match_ids":summary["eventless_match_ids"],"mismatch_match_id":"3794991","variant_ids":{"4661":["Throttur Reykjavik","Thróttur Reykjavík"],"8299":["IBV Vestmannaeyjar","ÍBV Vestmannaeyjar"],"4516":["HK Kopavogs","HK Kópavogs"],"4495":["Njardvik","Njarðvík"],"6683":["Leiknir Reykjavik","Leiknir Reykjavík"],"163250":["IR Reykjavik","ÍR Reykjavík"]},"malformed_10226_payloads":16,"malformed_10226_match_ids":["3703092","3703096","3703178","3703179","3703186","3703188","3703191","3703196","3703204","3703207","3703215","3703217","3703222","3703230","3703253","3703256"]}
json.dump(inventory,(HERE/"inventory_summary.json").open("w"),indent=2)
print(json.dumps(summary,indent=2))

