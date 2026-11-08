"""EDA for SE-Superettan: levels, trait reliability (split-half), halves
constants + noise test, X2 mover measurement vs the Allsvenskan corpus.
Writes eda_summary.json + inventory_summary.json next to this file."""
import csv, json, math, random, statistics
from collections import defaultdict
from pathlib import Path
HERE=Path(__file__).resolve().parent
M=list(csv.DictReader(open(HERE.parent/"data"/"se2_matches.csv")))
def f(v):
    try: return float(v)
    except (TypeError,ValueError): return None
for r in M:
    for k in list(r):
        if k not in ("match_id","league","season","date","round","phase","home_team","away_team","cards_source","ht_source","referee"):
            r[k]=f(r[k]) if r[k] not in ("",None) else None
SEASONS=sorted(set(r["season"] for r in M))
out={"seasons":SEASONS,"n":len(M)}
# levels per season
lev={}
for s in SEASONS:
    sub=[r for r in M if r["season"]==s]
    st=[r for r in sub if r["has_stats_all"]==1]
    def mean(key, rows): 
        v=[r[key] for r in rows if r[key] is not None]; return round(statistics.mean(v),3) if v else None
    lev[s]={"n":len(sub),"stats_n":len(st),
      "goals":mean("home_goals",sub) if False else round(statistics.mean([r["home_goals"]+r["away_goals"] for r in sub]),3),
      "home_goals":round(statistics.mean([r["home_goals"] for r in sub]),3),
      "away_goals":round(statistics.mean([r["away_goals"] for r in sub]),3),
      "sot":round(statistics.mean([r["ShotsOnTarget_home"]+r["ShotsOnTarget_away"] for r in st]),3) if st else None,
      "corners":round(statistics.mean([r["corners_home"]+r["corners_away"] for r in st]),3) if st else None,
      "shots":round(statistics.mean([r["total_shots_home"]+r["total_shots_away"] for r in st]),3) if st else None,
      "yellows":round(statistics.mean([r["yellow_home"]+r["yellow_away"] for r in sub]),3)}
out["levels"]=lev
# trait reliability: split-half by team-season halves (odd/even rounds pooled careers)
def trait(col_h, col_a, seasons):
    per=defaultdict(lambda: [[],[]])
    rows=[r for r in M if r["season"] in seasons and r[col_h] is not None]
    rows.sort(key=lambda r:(r["date"],r["match_id"]))
    cnt=defaultdict(int)
    for r in rows:
        for tid,val,opp in ((r["home_team_id"],r[col_h],r[col_a]),(r["away_team_id"],r[col_a],r[col_h])):
            h=cnt[tid]%2; per[tid][0].append(val) if h==0 else per[tid][1].append(val); cnt[tid]+=1
    xs=[];ys=[]
    for tid,(a,b) in per.items():
        if len(a)>=8 and len(b)>=8: xs.append(statistics.mean(a)); ys.append(statistics.mean(b))
    if len(xs)<8: return {"n_teams":len(xs),"r":None}
    mx,my=statistics.mean(xs),statistics.mean(ys)
    cov=sum((x-mx)*(y-my) for x,y in zip(xs,ys)); vx=sum((x-mx)**2 for x in xs); vy=sum((y-my)**2 for y in ys)
    return {"n_teams":len(xs),"r":round(cov/math.sqrt(vx*vy),3) if vx>0 and vy>0 else None}
stats_seasons=[s for s in SEASONS if s>="2022"]
out["traits"]={
 "sot_for":trait("ShotsOnTarget_home","ShotsOnTarget_away",stats_seasons),
 "corners_for":trait("corners_home","corners_away",stats_seasons),
 "shots_for":trait("total_shots_home","total_shots_away",stats_seasons),
 "yellows_for":trait("yellow_home","yellow_away",SEASONS),
 "goals_for":trait("home_goals","away_goals",SEASONS),
 "possession":trait("BallPossesion_home","BallPossesion_away",stats_seasons)}
# halves: goals + yellows event shares, variance vs binomial noise
def halves(num_key, den_fn, seasons, label):
    shares=[]; tot=0; num=0
    for r in M:
        if r["season"] not in seasons: continue
        d=den_fn(r)
        if d and d>0:
            n1=r[num_key]; shares.append(n1/d); num+=n1; tot+=d
    p=num/tot
    # observed var of share vs binomial expectation p(1-p)/E[d]
    ds=[den_fn(r) for r in M if r["season"] in seasons and den_fn(r)]
    exp_var=p*(1-p)/(tot/len(ds))
    obs_var=statistics.variance(shares) if len(shares)>2 else None
    return {"share":round(p,4),"n_matches":len(shares),"obs_var":round(obs_var,5),"binom_var":round(exp_var,5),
            "excess_var":round(obs_var-exp_var,5)}
out["halves_goals_all"]=halves("goals_1h_total", lambda r: r["home_goals"]+r["away_goals"], SEASONS, "goals")
out["halves_goals_dev"]=halves("goals_1h_total", lambda r: r["home_goals"]+r["away_goals"], [s for s in SEASONS if s<="2025"], "goals")
out["halves_yellows_dev"]=halves("ev_yellow_1h", lambda r: r["yellow_home"]+r["yellow_away"], [s for s in SEASONS if s<="2025"], "yellows")
# medians for primary lines (stats era dev seasons 2022-2025; cards/goals all dev)
def med(vals): return statistics.median(vals)
dev_stats=[r for r in M if r["season"] in ("2022","2023","2024","2025") and r["has_stats_all"]==1]
out["dev_medians"]={"sot":med([r["ShotsOnTarget_home"]+r["ShotsOnTarget_away"] for r in dev_stats]),
 "corners":med([r["corners_home"]+r["corners_away"] for r in dev_stats]),
 "shots":med([r["total_shots_home"]+r["total_shots_away"] for r in dev_stats]),
 "yellows":med([r["yellow_home"]+r["yellow_away"] for r in M if r["season"]<="2025"]),
 "goals_over25_rate":round(statistics.mean([1 if r["home_goals"]+r["away_goals"]>2.5 else 0 for r in M if r["season"]<="2025"]),3)}
# X2 movers: teams in Superettan season S whose previous season was Allsvenskan (parent corpus)
PARENT=list(csv.DictReader(open(Path("/home/hatch/workspace/footballprediction/league/SE-Allsvenskan/data/se_matches.csv"))))
par_teams=defaultdict(set)
for r in PARENT: par_teams[r["season"]].add(int(r["home_team_id"])); par_teams[r["season"]].add(int(r["away_team_id"]))
sup_teams=defaultdict(set)
for r in M: sup_teams[r["season"]].add(int(r["home_team_id"])); sup_teams[r["season"]].add(int(r["away_team_id"]))
movers=[]
for s in SEASONS[1:]:
    prev=str(int(s)-1)
    for tid in sup_teams[s]:
        if tid in par_teams.get(prev,()) and tid not in sup_teams.get(prev,()):
            movers.append((s,tid))
out["x2_relegated_entrants"]=[{"season":s,"team_id":t} for s,t in movers]
# their Superettan GF/GA per match vs league mean that season
diffs=[]
for s,tid in movers:
    sub=[r for r in M if r["season"]==s and tid in (r["home_team_id"],r["away_team_id"])]
    gf=statistics.mean([(r["home_goals"] if r["home_team_id"]==tid else r["away_goals"]) for r in sub])
    ga=statistics.mean([(r["away_goals"] if r["home_team_id"]==tid else r["home_goals"]) for r in sub])
    lg=statistics.mean([r["home_goals"]+r["away_goals"] for r in M if r["season"]==s])/2
    diffs.append((round(gf-lg,3), round(ga-lg,3)))
out["x2_entrant_gf_ga_diff_vs_league_team_mean"]={"n":len(diffs),
  "gf_diff":round(statistics.mean([d[0] for d in diffs]),3) if diffs else None,
  "ga_diff":round(statistics.mean([d[1] for d in diffs]),3) if diffs else None}
# promoted entrants (from Division 1, no corpus) count
prom=[]
for s in SEASONS[1:]:
    prev=str(int(s)-1)
    for tid in sup_teams[s]:
        if tid not in sup_teams.get(prev,()) and tid not in par_teams.get(prev,()): prom.append((s,tid))
out["promoted_entrants_no_corpus"]=len(prom)
inv={"by_season":{s:{"n":sum(1 for r in M if r["season"]==s),
  "stats_keys_n":sum(1 for r in M if r["season"]==s and r["has_stats_all"]==1),
  "referee_named":sum(1 for r in M if r["season"]==s and r["referee"]),
  "shotmap_n":sum(1 for r in M if r["season"]==s and r["has_shotmap"]==1)} for s in SEASONS},
 "team_ids_total":len(set([r["home_team_id"] for r in M]+[r["away_team_id"] for r in M]))}
json.dump(out, open(HERE/"eda_summary.json","w"), indent=1)
json.dump(inv, open(HERE/"inventory_summary.json","w"), indent=1)
print(json.dumps(out, indent=1)); print(json.dumps(inv, indent=1))
