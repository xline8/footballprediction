"""Reproducible RU-1Division inventory and EDA. Deliberately performs no fitting."""
import csv, importlib.util, json, math, random, statistics as st
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROWS = list(csv.DictReader((HERE.parent / "data/ru1_matches.csv").open()))
random.seed(42)

def f(r, k):
    try: return None if r.get(k) in (None, "", "None") else float(r[k])
    except (TypeError, ValueError): return None
def avg(v): return round(st.mean(v), 3) if v else None
def pct(n, d): return round(100*n/d, 1) if d else None
def corr(x, y):
    if len(x) < 5: return None
    mx, my = st.mean(x), st.mean(y)
    den = math.sqrt(sum((z-mx)**2 for z in x) * sum((z-my)**2 for z in y))
    return round(sum((a-mx)*(b-my) for a,b in zip(x,y))/den, 3) if den else None
def split(series, min_n=20, reps=100):
    eligible={k:v for k,v in series.items() if len(v)>=min_n}; out=[]
    for _ in range(reps):
        a=[]; b=[]
        for v in eligible.values():
            ix=list(range(len(v))); random.shuffle(ix); cut=len(ix)//2
            a.append(st.mean([v[i] for i in ix[:cut]])); b.append(st.mean([v[i] for i in ix[cut:]]))
        q=corr(a,b)
        if q is not None: out.append(q)
    return (round(st.mean(out),3),len(eligible)) if out else (None,0)
def total(r, k):
    a,b=f(r,f"{k}_home"),f(r,f"{k}_away")
    return a+b if a is not None and b is not None else None
def team_series(key, against=False, seasons=None):
    out=defaultdict(list)
    for r in ROWS:
        if seasons and r["season"] not in seasons: continue
        for side,other in (("home","away"),("away","home")):
            v=f(r,f"{key}_{other if against else side}")
            if v is not None: out[r[f"{side}_team_id"]].append(v)
    return out
def goal_series(against=False, rows=ROWS):
    out=defaultdict(list)
    for r in rows:
        for side,other in (("home","away"),("away","home")):
            out[r[f"{side}_team_id"]].append(float(r[f"{other if against else side}_goals"]))
    return out

seasons=sorted({r["season"] for r in ROWS})
teams={s:{r[f"{z}_team_id"] for r in ROWS if r["season"]==s for z in ("home","away")} for s in seasons}
per={}
for s in seasons:
    rs=[r for r in ROWS if r["season"]==s]
    def cov(k): return pct(sum(f(r,k) is not None for r in rs),len(rs))
    per[s]={"matches":len(rs),"teams":len(teams[s]),"matches_per_team":round(2*len(rs)/len(teams[s]),3),
            "goals":avg([int(r["home_goals"])+int(r["away_goals"]) for r in rs]),"home_goals":avg([int(r["home_goals"]) for r in rs]),"away_goals":avg([int(r["away_goals"]) for r in rs]),"home_advantage":avg([int(r["home_goals"])-int(r["away_goals"]) for r in rs]),
            "sot":avg([total(r,"ShotsOnTarget") for r in rs if total(r,"ShotsOnTarget") is not None]),"corners":avg([total(r,"corners") for r in rs if total(r,"corners") is not None]),"total_shots":avg([total(r,"total_shots") for r in rs if total(r,"total_shots") is not None]),"cards_stats":avg([total(r,"yellow_cards") for r in rs if total(r,"yellow_cards") is not None]),"cards_events":avg([int(r["ev_yellow_home"])+int(r["ev_yellow_away"]) for r in rs]),
            "coverage":{"stats_present":pct(sum(r["has_stats_all"]=="1" for r in rs),len(rs)),"period_splits":pct(sum(r["has_period_splits_content"]=="1" for r in rs),len(rs)),"referee":pct(sum(bool(r["referee"]) for r in rs),len(rs)),"shotmap":pct(sum(r["has_shotmap"]=="1" for r in rs),len(rs)),"events":pct(sum(r["has_events"]=="1" for r in rs),len(rs)),"BallPossesion":cov("BallPossesion_home"),"total_shots":cov("total_shots_home"),"ShotsOnTarget":cov("ShotsOnTarget_home"),"corners":cov("corners_home"),"yellow_cards":cov("yellow_cards_home")}}

def pair_key(r): return tuple(sorted((r["home_team_id"],r["away_team_id"])))
rr={}
for s in seasons:
    counts=Counter(pair_key(r) for r in ROWS if r["season"]==s)
    rr[s]={"pairings_once":[list(k) for k,v in sorted(counts.items()) if v==1],"pairings_twice":[list(k) for k,v in sorted(counts.items()) if v==2],"pair_count_histogram":dict(Counter(counts.values()))}
    if s=="2025/2026":
        rr[s]["pairing_home_away_records"]=[{"pairing":list(k),"matches":[{"home_team_id":r["home_team_id"],"away_team_id":r["away_team_id"]} for r in ROWS if r["season"]==s and pair_key(r)==k]} for k in sorted(counts)]
missing=None
s="2025/2026"; rs=[r for r in ROWS if r["season"]==s]
counts=Counter(pair_key(r) for r in rs); missing_pairs=[p for p,n in counts.items() if n==1]
if len(missing_pairs)==1:
    p=missing_pairs[0]; seen={(r["home_team_id"],r["away_team_id"]) for r in rs if pair_key(r)==p}
    names={t:next((r[f"{z}_team"] for r in rs for z in ("home","away") if r[f"{z}_team_id"]==t),t) for t in p}
    missing={"pair_team_ids":list(p),"team_names":names,"played_direction":next(iter(seen),None),"missing_direction":next((list(x) for x in ((p[0],p[1]),(p[1],p[0])) if x not in seen),None)}

stats_cards=[r for r in ROWS if f(r,"yellow_cards_home") is not None and f(r,"yellow_cards_away") is not None]
cards={"stats_rows":len(stats_cards),"comparison":"moot: stats yellow_cards absent in every row; event yellows are the target by construction"}
if stats_cards:
    diffs=[total(r,"yellow_cards")-(int(r["ev_yellow_home"])+int(r["ev_yellow_away"])) for r in stats_cards]
    cards.update({"exact_match_pct":pct(sum(d==0 for d in diffs),len(diffs)),"mean_stats_minus_events":round(st.mean(diffs),3),"max_abs_diff":max(map(abs,diffs))})

spec=[("goals_for",None,False),("goals_against",None,True),("sot_for","ShotsOnTarget",False),("sot_against","ShotsOnTarget",True),("corners_for","corners",False),("corners_against","corners",True),("total_shots_for","total_shots",False),("total_shots_against","total_shots",True),("event_yellows_for","ev_yellow",False),("event_yellows_against","ev_yellow",True),("possession_for","BallPossesion",False),("possession_against","BallPossesion",True)]
reliability={}; reliability_nteams={}
for name,key,against in spec:
    reliability[name],reliability_nteams[name]=split(goal_series(against) if key is None else team_series(key,against))

def level(rs,k):
    return avg([int(r["home_goals"])+int(r["away_goals"]) for r in rs]) if k=="goals" else avg([total(r,k) for r in rs if total(r,k) is not None])
inv=[r for r in ROWS if r["season"]=="2021/2022"]
before=[r for r in inv if r["date"]<"2022-02-24"]; after=[r for r in inv if r["date"]>="2022-02-24"]
invasion={"before_n":len(before),"after_n":len(after),"before":{k:level(before,k) for k in ("goals","ShotsOnTarget","corners","total_shots")},"after":{k:level(after,k) for k in ("goals","ShotsOnTarget","corners","total_shots")},"post_break_by_season":{s:{"goals":per[s]["goals"],"sot":per[s]["sot"],"corners":per[s]["corners"],"total_shots":per[s]["total_shots"]} for s in seasons[1:]}}

dev=[r for r in ROWS if r["season"] in seasons[:4]]
def line_for(k, lines):
    vals=([int(r["home_goals"])+int(r["away_goals"]) for r in dev] if k=="goals" else [int(r["ev_yellow_home"])+int(r["ev_yellow_away"]) if k=="ev_yellow" else total(r,k) for r in dev if k=="ev_yellow" or total(r,k) is not None])
    _,line,rate=min((abs(sum(v>x for v in vals)/len(vals)-.5),x,round(sum(v>x for v in vals)/len(vals),3)) for x in lines)
    return {"line":line,"over_rate":rate,"n":len(vals)}

# Load the parent-tier corpus in memory only; no RU-Premier files are written.
parent_rows=[]
try:
    p=Path(__file__).resolve().parents[2]/"RU-PremierLeague"/"data"/"build_data.py"
    sm=importlib.util.spec_from_file_location("ru_premier_builder",p); mod=importlib.util.module_from_spec(sm); sm.loader.exec_module(mod)
    root=Path.home()/"workspace"/"footballprediction"; idx=root/"data_enrichment"/"fotmob_world_index.csv"
    parent_rows=[mod.build(r,root) for r in csv.DictReader(idx.open()) if r["league_id"]=="63"]
except Exception:
    parent_rows=[]
parent_teams={s:{str(r[f"{z}_team_id"]) for r in parent_rows if r["season"]==s for z in ("home","away")} for s in {r["season"] for r in parent_rows}}
def team_season_stats(rows, season, tid):
    gf=[]; ga=[]
    for r in rows:
        if r["season"]!=season or tid not in (str(r["home_team_id"]),str(r["away_team_id"])): continue
        home=str(r["home_team_id"])==tid; gf.append(int(r["home_goals"] if home else r["away_goals"])); ga.append(int(r["away_goals"] if home else r["home_goals"]))
    return {"matches":len(gf),"gf_per_match":avg(gf),"ga_per_match":avg(ga)}
league_means={s:avg([int(r[z+"_goals"]) for r in ROWS if r["season"]==s for z in ("home","away")]) for s in seasons}
movers=[]
for i,s in enumerate(seasons[1:5],1):
    prev=seasons[i-1]
    for tid in sorted(teams[s]-teams[prev]):
        if tid in parent_teams.get(prev,set()): group="relegated_from_RU-Premier"
        elif tid in set().union(*(teams[x] for x in seasons[:i-1])): group="returning"
        else: group="promoted_second_tier_or_other"
        cur=team_season_stats(ROWS,s,tid)
        name=next((r[f"{z}_team"] for r in ROWS for z in ("home","away") if r["season"]==s and r[f"{z}_team_id"]==tid),tid)
        e={"season":s,"team_id":tid,"team":name,"group":group,"first_ru1":cur,"ru1_gap":{"gf":round(cur["gf_per_match"]-league_means[s],3),"ga":round(cur["ga_per_match"]-league_means[s],3)}}
        if group=="relegated_from_RU-Premier":
            prior=team_season_stats(parent_rows,prev,tid); pm=avg([int(r[z+"_goals"]) for r in parent_rows if r["season"]==prev for z in ("home","away")])
            e["prior_ru_premier"]=prior; e["prior_gap_vs_parent"]={"gf":round(prior["gf_per_match"]-pm,3),"ga":round(prior["ga_per_match"]-pm,3)}
        movers.append(e)
mover_groups={g:{"n":sum(m["group"]==g for m in movers),"gf_gap_mean":avg([m["ru1_gap"]["gf"] for m in movers if m["group"]==g]),"ga_gap_mean":avg([m["ru1_gap"]["ga"] for m in movers if m["group"]==g]),"first_ru1_gf_mean":avg([m["first_ru1"]["gf_per_match"] for m in movers if m["group"]==g]),"first_ru1_ga_mean":avg([m["first_ru1"]["ga_per_match"] for m in movers if m["group"]==g]),"prior_ru_premier_gf_mean":avg([m["prior_ru_premier"]["gf_per_match"] for m in movers if m["group"]==g and "prior_ru_premier" in m]),"prior_ru_premier_ga_mean":avg([m["prior_ru_premier"]["ga_per_match"] for m in movers if m["group"]==g and "prior_ru_premier" in m])} for g in sorted({m["group"] for m in movers})}

half_rows=[r for r in ROWS if r["season"] in seasons[:5]]
shares=[]; first_goals=[]; total_goals=[]
for r in half_rows:
    g=int(r["home_goals"])+int(r["away_goals"]); h=int(r["ht_home_goals"])+int(r["ht_away_goals"])
    if g>0: shares.append(h/g); first_goals.append(h); total_goals.append(g)
p=sum(first_goals)/sum(total_goals); noise=st.mean([p*(1-p)/g for g in total_goals]); obs=st.variance(shares)
half_period={"goals":{"n":len(shares),"share_ratio_of_sums":round(p,4),"observed_var":round(obs,5),"noise_expectation":round(noise,5),"true_var":round(obs-noise,5),"noise_ratio":round(obs/noise,3),"time_rule":"event time <=45 is first half; 45+x uses main time 45 and is first half; 90+x is second half"},"other_markets":"FT presentation only: no period splits exist for SOT, corners, cards, or total shots"}

all_levels={"matches":len(ROWS),"goals":level(ROWS,"goals"),"home_goals":avg([int(r["home_goals"]) for r in ROWS]),"away_goals":avg([int(r["away_goals"]) for r in ROWS]),"home_advantage":avg([int(r["home_goals"])-int(r["away_goals"]) for r in ROWS]),"sot":level(ROWS,"ShotsOnTarget"),"corners":level(ROWS,"corners"),"total_shots":level(ROWS,"total_shots"),"cards_events":level(ROWS,"ev_yellow")}
out={"n":len(ROWS),"seasons":seasons,"pooled":all_levels,"per_season":per,"format":{"teams_per_season":{s:len(teams[s]) for s in seasons},"matches_per_team":{s:round(2*len([r for r in ROWS if r['season']==s])/len(teams[s]),3) for s in seasons},"phase_values":sorted({r["phase"] for r in ROWS}),"single_regular_phase":True,"double_round_robin_expected":{s:len(teams[s])*(len(teams[s])-1) for s in seasons}},"round_robin":rr,"missing_2025_2026_fixture":missing,"cards_check":cards,"reliability":reliability,"reliability_nteams":reliability_nteams,"dev_lines":{"sot":line_for("ShotsOnTarget",[7.5,8.5,9.5]),"corners":line_for("corners",[8.5,9.5,10.5]),"cards":line_for("ev_yellow",[3.5,4.5,5.5]),"total_shots":line_for("total_shots",[13.5,14.5,15.5,16.5]),"goals":line_for("goals",[2.5])},"dev_n":len(dev),"virgin_n":len([r for r in ROWS if r["season"]=="2025/2026"]),"confirmatory_n":len([r for r in ROWS if r["season"]=="2026/2027"]),"half_period":half_period,"invasion_check":invasion,"movers":movers,"mover_groups":mover_groups,"parent_corpus_rows_in_memory":len(parent_rows)}
(HERE/"eda_numbers.json").write_text(json.dumps(out,indent=2)+"\n")
(HERE/"inventory_summary.json").write_text(json.dumps(out,indent=2)+"\n")
print(json.dumps(out,indent=2))
