"""EDA for HR-HNL: levels, trait reliability (split-half), halves constants
+ noise test, referee trait, cards stats-vs-events artefact check, X2
entrants, primary-line scan. Writes eda_summary.json + inventory_summary.json.
The in-progress 2026/2027 season is inventoried but excluded from every
fitting-relevant quantity (dev/virgin windows end at 2025/2026)."""
import csv, json, math, statistics
from collections import defaultdict
from pathlib import Path
HERE=Path(__file__).resolve().parent
M=list(csv.DictReader(open(HERE.parent/"data"/"hr_matches.csv")))
def f(v):
    try: return float(v)
    except (TypeError,ValueError): return None
STRKEYS={"match_id","league","season","date","round","phase","league_name","home_team","away_team","cards_source","ht_source","referee"}
for r in M:
    for k in list(r):
        if k not in STRKEYS:
            r[k]=f(r[k]) if r[k] not in ("",None) else None
SEASONS=sorted(set(r["season"] for r in M))
COMPLETE=["2021/2022","2022/2023","2023/2024","2024/2025","2025/2026"]
WARMUP=["2021/2022"]; DEV=["2022/2023","2023/2024","2024/2025"]; VIRGIN="2025/2026"
out={"seasons":SEASONS,"n":len(M)}
def mean(vals):
    v=[x for x in vals if x is not None]; return round(statistics.mean(v),3) if v else None
lev={}
for s in SEASONS:
    sub=[r for r in M if r["season"]==s]
    st=[r for r in sub if r["has_stats_all"]==1]
    lev[s]={"n":len(sub),"stats_n":len(st),"splits_n":sum(1 for r in sub if r["has_stats_half"]==1),
      "referee_named":sum(1 for r in sub if r["referee"]),
      "league_names":sorted(set(r["league_name"] for r in sub)),
      "teams_n":len(set([int(r["home_team_id"]) for r in sub]+[int(r["away_team_id"]) for r in sub])),
      "goals":mean([r["home_goals"]+r["away_goals"] for r in sub]),
      "home_goals":mean([r["home_goals"] for r in sub]),
      "away_goals":mean([r["away_goals"] for r in sub]),
      "sot":mean([r["ShotsOnTarget_home"]+r["ShotsOnTarget_away"] for r in st]),
      "corners":mean([r["corners_home"]+r["corners_away"] for r in st]),
      "shots":mean([r["total_shots_home"]+r["total_shots_away"] for r in st]),
      "yellows_stats":mean([r["stats_yellow_home"]+r["stats_yellow_away"] for r in st]),
      "yellows_events":mean([r["ev_yellow_home"]+r["ev_yellow_away"] for r in sub]),
      "reds_stats":mean([r["stats_red_home"]+r["stats_red_away"] for r in st]),
      "sot_share_of_shots": None}
    if st:
        sh=sum(r["total_shots_home"]+r["total_shots_away"] for r in st); so=sum(r["ShotsOnTarget_home"]+r["ShotsOnTarget_away"] for r in st)
        lev[s]["sot_share_of_shots"]=round(so/sh,4) if sh else None
out["levels"]=lev
# trait reliability: split-half by alternating team matches (career pooled)
def trait(col_h, col_a, seasons, col_b_h=None, col_b_a=None):
    per=defaultdict(lambda: [[],[]])
    rows=[r for r in M if r["season"] in seasons and r[col_h] is not None]
    rows.sort(key=lambda r:(r["date"],r["match_id"]))
    cnt=defaultdict(int)
    for r in rows:
        for tid,val in ((r["home_team_id"],r[col_h]),(r["away_team_id"],r[col_a])):
            h=cnt[tid]%2; per[tid][h].append(val); cnt[tid]+=1
    xs=[];ys=[]
    for tid,(a,b) in per.items():
        if len(a)>=8 and len(b)>=8: xs.append(statistics.mean(a)); ys.append(statistics.mean(b))
    if len(xs)<8: return {"n_teams":len(xs),"r":None}
    mx,my=statistics.mean(xs),statistics.mean(ys)
    cov=sum((x-mx)*(y-my) for x,y in zip(xs,ys)); vx=sum((x-mx)**2 for x in xs); vy=sum((y-my)**2 for y in ys)
    return {"n_teams":len(xs),"r":round(cov/math.sqrt(vx*vy),3) if vx>0 and vy>0 else None}
def trait_against(col_h, col_a, seasons):
    # trait of CONCEDED values: swap home/away roles
    return trait(col_a, col_h, seasons)
ALLC=COMPLETE
out["traits"]={
 "goals_for":trait("home_goals","away_goals",ALLC),
 "goals_against":trait_against("home_goals","away_goals",ALLC),
 "sot_for":trait("ShotsOnTarget_home","ShotsOnTarget_away",ALLC),
 "sot_against":trait_against("ShotsOnTarget_home","ShotsOnTarget_away",ALLC),
 "corners_for":trait("corners_home","corners_away",ALLC),
 "corners_against":trait_against("corners_home","corners_away",ALLC),
 "shots_for":trait("total_shots_home","total_shots_away",ALLC),
 "shots_against":trait_against("total_shots_home","total_shots_away",ALLC),
 "yellows_for":trait("yellow_home","yellow_away",ALLC),
 "yellows_against":trait_against("yellow_home","yellow_away",ALLC),
 "possession":trait("BallPossesion_home","BallPossesion_away",ALLC),
 "touches_for":trait("touches_opp_box_home","touches_opp_box_away",ALLC),
 "touches_against":trait_against("touches_opp_box_home","touches_opp_box_away",ALLC),
 "big_chance_for":trait("big_chance_home","big_chance_away",ALLC),
 "big_chance_against":trait_against("big_chance_home","big_chance_away",ALLC),
 "fouls_for":trait("fouls_home","fouls_away",ALLC)}
# per-match corr touches vs corners, big_chance vs corners (All period)
def pcorr(pairs):
    xs=[a for a,b in pairs]; ys=[b for a,b in pairs]
    mx,my=statistics.mean(xs),statistics.mean(ys)
    cov=sum((x-mx)*(y-my) for x,y in pairs); vx=sum((x-mx)**2 for x in xs); vy=sum((y-my)**2 for y in ys)
    return round(cov/math.sqrt(vx*vy),3)
tc=[(r["touches_opp_box_home"]+r["touches_opp_box_away"], r["corners_home"]+r["corners_away"]) for r in M if r["season"] in ALLC and r["touches_opp_box_home"] is not None]
pc=[(r["BallPossesion_home"], r["corners_home"]+r["corners_away"]) for r in M if r["season"] in ALLC and r["BallPossesion_home"] is not None]
out["corr_touches_corners"]={"n":len(tc),"r":pcorr(tc)}
out["corr_possession_corners"]={"n":len(pc),"r":pcorr(pc)}
# referee trait: split-half over referees' matches (stats yellows total)
ref=defaultdict(lambda: [[],[]]); rcnt=defaultdict(int)
rows=[r for r in M if r["season"] in ALLC and r["referee"] and r["stats_yellow_home"] is not None]
rows.sort(key=lambda r:(r["date"],r["match_id"]))
for r in rows:
    h=rcnt[r["referee"]]%2; ref[r["referee"]][h].append(r["stats_yellow_home"]+r["stats_yellow_away"]); rcnt[r["referee"]]+=1
xs=[];ys=[]
for nm,(a,b) in ref.items():
    if len(a)>=5 and len(b)>=5: xs.append(statistics.mean(a)); ys.append(statistics.mean(b))
if len(xs)>=8:
    mx,my=statistics.mean(xs),statistics.mean(ys)
    cov=sum((x-mx)*(y-my) for x,y in zip(xs,ys)); vx=sum((x-mx)**2 for x in xs); vy=sum((y-my)**2 for y in ys)
    out["referee_trait"]={"n_refs":len(xs),"r":round(cov/math.sqrt(vx*vy),3),"refs_total":len(ref),
      "mean_yellows":round(statistics.mean([r["stats_yellow_home"]+r["stats_yellow_away"] for r in rows]),3)}
else:
    out["referee_trait"]={"n_refs":len(xs),"r":None,"refs_total":len(ref)}
out["referee_coverage"]={s:{"named":sum(1 for r in M if r["season"]==s and r["referee"]),"n":sum(1 for r in M if r["season"]==s)} for s in SEASONS}
# halves: event-based shares (goals, yellows) over dev era (warmup+dev)
def halves(num_fn, den_fn, seasons):
    shares=[]; tot=0; num=0
    for r in M:
        if r["season"] not in seasons: continue
        d=den_fn(r)
        if d and d>0:
            n1=num_fn(r); shares.append(n1/d); num+=n1; tot+=d
    p=num/tot
    ds=[den_fn(r) for r in M if r["season"] in seasons and den_fn(r)]
    exp_var=p*(1-p)/(tot/len(ds)); obs_var=statistics.variance(shares)
    return {"share":round(p,4),"n_matches":len(shares),"obs_var":round(obs_var,5),"binom_var":round(exp_var,5),"excess_var":round(obs_var-exp_var,5)}
DEVERA=WARMUP+DEV
out["halves_goals_dev"]=halves(lambda r: r["goals_1h_total"], lambda r: r["home_goals"]+r["away_goals"], DEVERA)
out["halves_yellows_events_dev"]=halves(lambda r: r["ev_yellow_1h"], lambda r: r["ev_yellow_home"]+r["ev_yellow_away"], DEVERA)
# halves: period-split shares pooled over dev seasons that carry splits
def split_share(key, seasons):
    sub=[r for r in M if r["season"] in seasons and r[f"fh_{key}_home"] is not None and (r[f"{key}_home"] or 0)+(r[f"{key}_away"] or 0)>0]
    num=sum(r[f"fh_{key}_home"]+r[f"fh_{key}_away"] for r in sub); den=sum(r[f"{key}_home"]+r[f"{key}_away"] for r in sub)
    return {"share":round(num/den,4),"n_matches":len(sub)} if den else {"share":None,"n_matches":0}
SPLITDEV=["2022/2023","2023/2024","2024/2025"]
out["halves_splits_dev"]={k:split_share(k,SPLITDEV) for k in ("total_shots","ShotsOnTarget","corners","yellow_cards")}
out["halves_splits_by_season"]={s:{k:split_share(k,[s]) for k in ("total_shots","ShotsOnTarget","corners","yellow_cards")} for s in SPLITDEV+[VIRGIN]}
# splits consistency All == 1H+2H
bad=defaultdict(int); tot=defaultdict(int)
for r in M:
    if r["has_stats_half"]==1:
        for k in ("corners","ShotsOnTarget","total_shots","yellow_cards"):
            tot[k]+=1
            if abs((r[f"fh_{k}_home"]+r[f"sh_{k}_home"])-r[f"{k}_home"])>0.01 or abs((r[f"fh_{k}_away"]+r[f"sh_{k}_away"])-r[f"{k}_away"])>0.01: bad[k]+=1
out["splits_consistency"]={k:{"n":tot[k],"mismatch":bad[k]} for k in tot}
# cards artefact: stats vs events per season (stats keys exist everywhere)
art={}
for s in SEASONS:
    sub=[r for r in M if r["season"]==s and r["stats_yellow_home"] is not None]
    if not sub: continue
    ev=[r["ev_yellow_home"]+r["ev_yellow_away"] for r in sub]
    st=[r["stats_yellow_home"]+r["stats_yellow_away"] for r in sub]
    art[s]={"n":len(sub),"exact":round(statistics.mean([1 if a==b else 0 for a,b in zip(ev,st)]),3),
      "mean_ev":round(statistics.mean(ev),3),"mean_stats":round(statistics.mean(st),3),
      "mean_stats_minus_ev":round(statistics.mean([b-a for a,b in zip(ev,st)]),3),
      "ev_gt_stats":sum(1 for a,b in zip(ev,st) if a>b),"stats_gt_ev":sum(1 for a,b in zip(ev,st) if b>a)}
out["cards_stats_vs_events"]=art
# X2 entrants (tier 1: absent from HNL previous season)
sup_teams=defaultdict(set); name_of={}
for r in M:
    sup_teams[r["season"]].add(int(r["home_team_id"])); sup_teams[r["season"]].add(int(r["away_team_id"]))
    name_of[int(r["home_team_id"])]=r["home_team"]; name_of[int(r["away_team_id"])]=r["away_team"]
entrants=[]
for i,s in enumerate(COMPLETE):
    if i==0: continue
    prev=COMPLETE[i-1]
    for tid in sup_teams[s]:
        if tid not in sup_teams.get(prev,()): entrants.append((s,tid))
out["x2_entrants"]=[{"season":s,"team_id":t,"team":name_of.get(t)} for s,t in entrants]
diffs=[]
for s,tid in entrants:
    sub=[r for r in M if r["season"]==s and tid in (r["home_team_id"],r["away_team_id"])]
    gf=statistics.mean([(r["home_goals"] if r["home_team_id"]==tid else r["away_goals"]) for r in sub])
    ga=statistics.mean([(r["away_goals"] if r["home_team_id"]==tid else r["home_goals"]) for r in sub])
    lg=statistics.mean([r["home_goals"]+r["away_goals"] for r in M if r["season"]==s])/2
    diffs.append((round(gf-lg,3), round(ga-lg,3)))
out["x2_entrant_gf_ga_diff"]={"n":len(diffs),"gf_diff":round(statistics.mean([d[0] for d in diffs]),3) if diffs else None,
  "ga_diff":round(statistics.mean([d[1] for d in diffs]),3) if diffs else None}
# primary-line scan on dev scored seasons
dev=[r for r in M if r["season"] in DEV]
devst=[r for r in dev if r["has_stats_all"]==1]
def over_rate(rows, fn, lines): return {str(L):round(statistics.mean([1 if fn(r)>L else 0 for r in rows]),3) for L in lines}
out["dev_over_rates"]={
 "sot":over_rate(devst, lambda r: r["ShotsOnTarget_home"]+r["ShotsOnTarget_away"], [7.5,8.5,9.5]),
 "corners":over_rate(devst, lambda r: r["corners_home"]+r["corners_away"], [8.5,9.5,10.5]),
 "shots":over_rate(devst, lambda r: r["total_shots_home"]+r["total_shots_away"], [23.5,24.5,25.5,26.5]),
 "yellows_stats":over_rate(devst, lambda r: r["stats_yellow_home"]+r["stats_yellow_away"], [3.5,4.5,5.5]),
 "goals_o25_dev":round(statistics.mean([1 if r["home_goals"]+r["away_goals"]>2.5 else 0 for r in dev]),3),
 "home_win_rate_dev":round(statistics.mean([1 if r["home_goals"]>r["away_goals"] else 0 for r in dev]),3)}
out["dev_medians"]={"sot":statistics.median([r["ShotsOnTarget_home"]+r["ShotsOnTarget_away"] for r in devst]),
 "corners":statistics.median([r["corners_home"]+r["corners_away"] for r in devst]),
 "shots":statistics.median([r["total_shots_home"]+r["total_shots_away"] for r in devst]),
 "yellows":statistics.median([r["stats_yellow_home"]+r["stats_yellow_away"] for r in devst])}
# team id/name stability
idnames=defaultdict(set)
for r in M: idnames[int(r["home_team_id"])].add(r["home_team"]); idnames[int(r["away_team_id"])].add(r["away_team"])
out["team_ids_multi_name"]={str(k):sorted(v) for k,v in idnames.items() if len(v)>1}
out["team_ids_total"]=len(idnames)
inv={"by_season":{s:{"n":sum(1 for r in M if r["season"]==s),
  "stats_n":sum(1 for r in M if r["season"]==s and r["has_stats_all"]==1),
  "splits_n":sum(1 for r in M if r["season"]==s and r["has_stats_half"]==1),
  "referee_named":sum(1 for r in M if r["season"]==s and r["referee"]),
  "shotmap_n":sum(1 for r in M if r["season"]==s and r["has_shotmap"]==1),
  "rounds":sorted(set(int(r["round"]) for r in M if r["season"]==s))} for s in SEASONS},
 "team_ids_total":len(idnames)}
json.dump(out, open(HERE/"eda_summary.json","w"), indent=1)
json.dump(inv, open(HERE/"inventory_summary.json","w"), indent=1)
print(json.dumps(out, indent=1)); print(json.dumps(inv, indent=1))
