#!/usr/bin/env python3
"""Compute descriptive Liga 3 EDA; no model fitting or virgin read."""
import csv, json, math
from collections import defaultdict
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
CSV = BASE / "data/pt3_matches.csv"
OUT = Path(__file__).resolve().parent / "eda_summary.json"
INDEX = Path("/home/hatch/workspace/footballprediction/data_enrichment/fotmob_world_index.csv")

def num(x):
    try: return float(x) if x not in (None, "") else None
    except (TypeError, ValueError): return None
def mean(xs):
    xs=list(xs); return sum(xs)/len(xs) if xs else None
def flag(x): return str(x).lower() in {"1", "true", "yes"}
def pearson(a,b):
    if len(a)<2: return None
    ma,mb=mean(a),mean(b); da=[x-ma for x in a]; db=[x-mb for x in b]
    den=math.sqrt(sum(x*x for x in da)*sum(x*x for x in db)); return sum(x*y for x,y in zip(da,db))/den if den else None

def split_reliability(rows, metric, min_half=10):
    by_team=defaultdict(list)
    for r in rows:
        for side in ("home","away"):
            v=metric(r,side)
            if v is not None: by_team[r[f"{side}_id"]].append((r["date"],int(r["match_id"]),v))
    first=[]; second=[]
    for vals in by_team.values():
        vals.sort(); mid=len(vals)//2
        if mid<min_half or len(vals)-mid<min_half: continue
        first.append(sum(x[2] for x in vals[:mid])/len(vals[:mid])); second.append(sum(x[2] for x in vals[mid:])/len(vals[mid:]))
    return {"r":pearson(first,second),"n_teams":len(first),"min_half_matches":min_half}

def levels(rows):
    out={}
    for season in sorted({r["season"] for r in rows}):
        rs=[r for r in rows if r["season"]==season]; pairs=[(num(r["home_goals"]),num(r["away_goals"])) for r in rs]; goals=[h+a for h,a in pairs]
        ht=[num(r["ht_home"])+num(r["ht_away"]) for r in rs if num(r["ht_home"]) is not None and num(r["ht_away"]) is not None]
        out[season]={"n":len(rs),"teams":len({r["home_id"] for r in rs}|{r["away_id"] for r in rs}),"mean_home_goals":mean(h for h,a in pairs),"mean_away_goals":mean(a for h,a in pairs),"mean_total_goals":mean(goals),"home_win_rate":sum(h>a for h,a in pairs)/len(rs),"draw_rate":sum(h==a for h,a in pairs)/len(rs),"away_win_rate":sum(h<a for h,a in pairs)/len(rs),"event_yellows_matches":sum((num(r["event_yellows_home"]) or 0)+(num(r["event_yellows_away"]) or 0)>0 for r in rs),"mean_event_yellows_total":mean(num(r["event_yellows_home"])+num(r["event_yellows_away"]) for r in rs),"mean_event_cards_total":mean(num(r["event_cards_total"]) for r in rs),"stats_matches":sum(flag(r["has_stats"]) for r in rs),"shotmap_shots_positive":sum(flag(r["has_shotmap"]) for r in rs),"period_split_matches":sum(flag(r["has_period_splits"]) for r in rs),"expected_goals_matches":sum(flag(r["xg_present"]) for r in rs),"referee_named":sum(flag(r["referee_named"]) for r in rs),"card_event_matches":sum(flag(r["has_card_event"]) for r in rs),"lineup_matches":sum(flag(r["lineup_present"]) for r in rs),"ht_goal_matches":len(ht),"ht_goal_share":sum(ht)/sum(goals) if ht and sum(goals) else None}
    return out

def phase_counts(rows):
    out=defaultdict(lambda:defaultdict(int))
    for r in rows: out[r["season"]][r["phase"]]+=1
    return {s:dict(sorted(v.items())) for s,v in sorted(out.items())}

def load_league_matches(ids):
    result={lg:defaultdict(list) for lg in ids}; root=INDEX.parent.parent
    with open(INDEX,newline="") as fh: index=[r for r in csv.DictReader(fh) if r["league_id"] in ids]
    for ix in index:
        with open(root/ix["path"]) as fh: d=json.load(fh)
        if not (d.get("header") or {}).get("status",{}).get("finished"): continue
        teams=(d.get("header") or {}).get("teams") or [{},{}]
        for side,other in ((0,1),(1,0)):
            result[ix["league_id"]][ix["season"]].append({"team_id":str(teams[side].get("id","")),"gf":num(teams[side].get("score")),"ga":num(teams[other].get("score"))})
    return result

def mover_measurement():
    matches=load_league_matches({"61","185","9112"}); membership={lg:{s:{x["team_id"] for x in rs} for s,rs in seasons.items()} for lg,seasons in matches.items()}; seasons=sorted(set().union(*(set(x) for x in membership.values()))); out={}
    for i in range(1,len(seasons)):
        prior,season=seasons[i-1],seasons[i]; item={}
        for name,old_lg,new_lg in (("PT_to_PT3","61","9112"),("PT3_to_PT","9112","61"),("PT2_to_PT3","185","9112"),("PT3_to_PT2","9112","185")):
            movers=membership[old_lg].get(prior,set()) & membership[new_lg].get(season,set()) - membership[new_lg].get(prior,set()); changes=[]
            for team in sorted(movers):
                old=[x for x in matches[old_lg][prior] if x["team_id"]==team]; new=[x for x in matches[new_lg][season] if x["team_id"]==team]
                changes.append({"team_id":team,"gf_change":mean(x["gf"] for x in new)-mean(x["gf"] for x in old),"ga_change":mean(x["ga"] for x in new)-mean(x["ga"] for x in old)})
            item[name]={"prior_season":prior,"n":len(changes),"mean_gf_change":mean(x["gf_change"] for x in changes),"mean_ga_change":mean(x["ga_change"] for x in changes),"clubs":changes}
        out[season]=item
    return {"method_note":"PT/PT2 CSVs were absent in this worktree; counts and changes use indexed payloads for league IDs 61, 185, and 9112.","transitions":out}

def main():
    with open(CSV,newline="") as fh: rows=list(csv.DictReader(fh))
    seasons=sorted({r["season"] for r in rows}); metrics={"goals_for":lambda r,s:num(r[f"{s}_goals"]),"goals_against":lambda r,s:num(r[f"{'away' if s=='home' else 'home'}_goals"]),"event_yellows_for":lambda r,s:num(r[f"event_yellows_{s}"])}; reliability={}
    for name,metric in metrics.items(): reliability[name]=split_reliability(rows,metric); reliability[name]["valid_team_match_values"]=sum(metric(r,s) is not None for r in rows for s in ("home","away"))
    by_season={name:{s:split_reliability([r for r in rows if r["season"]==s],metric) for s in seasons} for name,metric in metrics.items()}; lev=levels(rows); ht=[r for r in rows if num(r["ht_home"]) is not None and num(r["ht_away"]) is not None]
    summary={"n_matches":len(rows),"seasons":lev,"phase_counts":phase_counts(rows),"trait_reliability":reliability,"trait_reliability_by_season":by_season,"movers":mover_measurement(),"halves":{"ht_goal_matches":len(ht),"n_matches":len(rows),"goals_1h_share":sum(num(r["ht_home"])+num(r["ht_away"]) for r in ht)/sum(num(r["home_goals"])+num(r["away_goals"]) for r in rows),"period_split_matches":sum(flag(r["has_period_splits"]) for r in rows),"frozen_constants":{}},"referee_coverage":{"named":sum(flag(r["referee_named"]) for r in rows),"by_season":{s:lev[s]["referee_named"] for s in seasons}},"cards_stats_vs_events":{"both_stats_and_events":sum(flag(r["has_stats"]) and flag(r["has_card_event"]) for r in rows),"stats_yellow_available":sum(flag(r["stats_yellow_key_present"]) for r in rows),"validation_n":0,"exact_agreement_rate":None,"mean_difference_stats_minus_events":None,"disagreement_at_4_5":None}}
    with open(OUT,"w") as fh: json.dump(summary,fh,indent=2,sort_keys=True)
    print(f"Wrote {OUT}")
    for s,v in lev.items(): print(s,v)
    print("reliability",json.dumps(reliability,sort_keys=True)); print("movers",json.dumps(summary["movers"],sort_keys=True))
if __name__=="__main__": main()
