"""Reproducible Phase A inventory and EDA; deliberately performs no fitting."""
import csv, json, math, random, statistics as st
from collections import defaultdict
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROWS = list(csv.DictReader((HERE.parent / "data/ru_matches.csv").open()))
random.seed(42)

def f(r, k):
    try: return None if r.get(k) in (None, "", "None") else float(r[k])
    except (TypeError, ValueError): return None
def avg(v): return round(st.mean(v), 3) if v else None
def corr(x, y):
    if len(x) < 5: return None
    mx, my = st.mean(x), st.mean(y)
    den = math.sqrt(sum((z-mx)**2 for z in x) * sum((z-my)**2 for z in y))
    return round(sum((a-mx)*(b-my) for a,b in zip(x,y))/den, 3) if den else None
def split(series, min_n=20, reps=100):
    elig = {k:v for k,v in series.items() if len(v) >= min_n}; out = []
    for _ in range(reps):
        a=[]; b=[]
        for v in elig.values():
            ix=list(range(len(v))); random.shuffle(ix); cut=len(ix)//2
            a.append(st.mean([v[i] for i in ix[:cut]])); b.append(st.mean([v[i] for i in ix[cut:]]))
        q=corr(a,b)
        if q is not None: out.append(q)
    return (round(st.mean(out),3),len(elig)) if out else (None,0)
def team_series(key, against=False, seasons=None):
    out=defaultdict(list)
    for r in ROWS:
        if seasons and r["season"] not in seasons: continue
        for side,other in (("home","away"),("away","home")):
            v=f(r,f"{key}_{other if against else side}")
            if v is not None: out[r[f"{side}_team_id"]].append(v)
    return out
def total(r,k):
    a,b=f(r,f"{k}_home"),f(r,f"{k}_away")
    return a+b if a is not None and b is not None else None
def half(rows,k,poisson=False):
    shares=[]; weights=[]; n=d=0
    for r in rows:
        first,full=total(r,f"fh_{k}"),total(r,k)
        if first is None or full is None or full<=0: continue
        shares.append(first/full); weights.append(full); n+=first; d+=full
    if len(shares)<30:return {"n":len(shares)}
    p=st.mean(shares); noise=st.mean([(1/w if poisson else p*(1-p)/w) for w in weights]); obs=st.variance(shares)
    return {"n":len(shares),"share_ratio_of_sums":round(n/d,4),"observed_var":round(obs,5),"noise_expectation":round(noise,5),"true_var":round(obs-noise,5),"noise_ratio":round(obs/noise,3) if noise else None}

seasons=sorted({r["season"] for r in ROWS}); per={}
for s in seasons:
    rs=[r for r in ROWS if r["season"]==s]
    def cov(k): return round(100*sum(f(r,k) is not None for r in rs)/len(rs),1)
    per[s]={"n":len(rs),"teams":len({r[f'{z}_team_id'] for r in rs for z in ('home','away')}),
            "goals":avg([int(r["home_goals"])+int(r["away_goals"]) for r in rs]),
            "home_goals":avg([int(r["home_goals"]) for r in rs]),"away_goals":avg([int(r["away_goals"]) for r in rs]),
            "sot":avg([total(r,"ShotsOnTarget") for r in rs if total(r,"ShotsOnTarget") is not None]),
            "corners":avg([total(r,"corners") for r in rs if total(r,"corners") is not None]),
            "total_shots":avg([total(r,"total_shots") for r in rs if total(r,"total_shots") is not None]),
            "cards_stats":avg([total(r,"yellow_cards") for r in rs if total(r,"yellow_cards") is not None]),
            "cards_events":avg([int(r["ev_yellow_home"])+int(r["ev_yellow_away"]) for r in rs]),
            "xg":avg([total(r,"expected_goals") for r in rs if total(r,"expected_goals") is not None]),
            "coverage":{"stats_all":round(100*sum(r["has_stats_all"]=="1" for r in rs)/len(rs),1),
                        "period_splits":round(100*sum(r["has_stats_half"]=="1" for r in rs)/len(rs),1),
                        "referee":round(100*sum(bool(r["referee"]) for r in rs)/len(rs),1),
                        "xg":cov("expected_goals_home"),"set_play_xg":cov("expected_goals_set_play_home"),
                        "box_touches":cov("touches_opp_box_home"),"shotmap":round(100*sum(r["has_shotmap"]=="1" for r in rs)/len(rs),1),
                        "possession":cov("BallPossesion_home"),"big_chance":cov("big_chance_home"),
                        "sot":cov("ShotsOnTarget_home"),"corners":cov("corners_home"),
                        "total_shots":cov("total_shots_home"),"yellow_stats":cov("yellow_cards_home")}}

pairs=[(f(r,"yellow_cards_home")+f(r,"yellow_cards_away"),int(r["ev_yellow_home"])+int(r["ev_yellow_away"])) for r in ROWS if f(r,"yellow_cards_home") is not None and r["has_events"]=="1"]
diffs=[a-b for a,b in pairs]
cards={"n":len(pairs),"exact_match_pct":round(100*sum(d==0 for d in diffs)/len(diffs),1),
       "mean_stats_minus_events":round(st.mean(diffs),3),"stats_lower_pct":round(100*sum(d<0 for d in diffs)/len(diffs),1),
       "stats_higher_pct":round(100*sum(d>0 for d in diffs)/len(diffs),1),"max_abs_diff":max(abs(d) for d in diffs),
       "yellowred_in_event_yellow":True}

spec=[("goals_for",None,False),("goals_against",None,True),("sot_for","ShotsOnTarget",False),("sot_against","ShotsOnTarget",True),
      ("corners_for","corners",False),("corners_against","corners",True),("yellows_stats_for","yellow_cards",False),
      ("yellows_stats_against","yellow_cards",True),("yellows_events_for","ev_yellow",False),("yellows_events_against","ev_yellow",True),
      ("shots_for","total_shots",False),("shots_against","total_shots",True),("possession","BallPossesion",False),
      ("big_chance_for","big_chance",False),("touches_opp_box_for","touches_opp_box",False),("touches_opp_box_against","touches_opp_box",True)]
rel={}; rel_n={}
for name,key,against in spec:
    if key is None:
        vals=defaultdict(list)
        for r in ROWS:
            vals[r["home_team_id"]].append(int(r["away_goals"]) if against else int(r["home_goals"]))
            vals[r["away_team_id"]].append(int(r["home_goals"]) if against else int(r["away_goals"]))
    else: vals=team_series(key,against)
    rel[name],rel_n[name]=split(vals)
xg_era={s for s in seasons if per[s]["coverage"]["xg"]>0}
rel["xg_for"],rel_n["xg_for"]=split(team_series("expected_goals",seasons=xg_era))

refs=defaultdict(list)
for r in ROWS:
    if r["referee"]: refs[r["referee"]].append(int(r["ev_yellow_home"])+int(r["ev_yellow_away"]))
ref_r,ref_n=split(refs,8); ref_season={}
for s in seasons:
    x=defaultdict(list)
    for r in ROWS:
        if r["season"]==s and r["referee"]: x[r["referee"]].append(int(r["ev_yellow_home"])+int(r["ev_yellow_away"]))
    a=[];b=[]
    for v in x.values():
        if len(v)>=8:
            q=len(v)//2; a.append(avg(v[:q])); b.append(avg(v[q:]))
    ref_season[s]=corr(a,b)

teams={s:{r[f"{z}_team_id"] for r in ROWS if r["season"]==s for z in ("home","away")} for s in seasons}
movers=[]
for i,s in enumerate(seasons[1:],1):
    for t in sorted(teams[s]-teams[seasons[i-1]]):
        vals=[(int(r["home_goals"]),int(r["away_goals"])) if r["home_team_id"]==t else (int(r["away_goals"]),int(r["home_goals"])) for r in ROWS if r["season"]==s and t in (r["home_team_id"],r["away_team_id"])]
        movers.append({"season":s,"team_id":t,"n":len(vals),"gf":avg([v[0] for v in vals]),"ga":avg([v[1] for v in vals])})

complete=[r for r in ROWS if r["season"] in ("2023/2024","2024/2025","2025/2026") and r["has_stats_half"]=="1"]
half_rows={k:half(complete,k) for k in ("ShotsOnTarget","corners","total_shots","yellow_cards")}
goal_values=[r for r in complete if int(r["home_goals"])+int(r["away_goals"])>0]
half_rows["goals"]={"n":len(goal_values),"share_ratio_of_sums":round(sum(int(r["ht_home_goals"])+int(r["ht_away_goals"]) for r in goal_values)/sum(int(r["home_goals"])+int(r["away_goals"]) for r in goal_values),4)}
inv=[r for r in ROWS if r["season"]=="2021/2022"]; before=[r for r in inv if r["date"]<"2022-02-24"]; after=[r for r in inv if r["date"]>="2022-02-24"]
def levels(rs,k):
    if k == "goals": return avg([int(r["home_goals"])+int(r["away_goals"]) for r in rs])
    return avg([total(r,k) for r in rs if total(r,k) is not None])
invasion={"before_n":len(before),"after_n":len(after),"before":{k:levels(before,k) for k in ("goals","ShotsOnTarget","corners","total_shots","yellow_cards")},"after":{k:levels(after,k) for k in ("goals","ShotsOnTarget","corners","total_shots","yellow_cards")}}
dev=[r for r in ROWS if r["season"] in seasons[:4]]
def line_for(k,lines):
    vals=([int(r["home_goals"])+int(r["away_goals"]) for r in dev] if k=="goals" else [total(r,k) for r in dev if total(r,k) is not None])
    z=min((abs(sum(v>x for v in vals)/len(vals)-.5),x,round(sum(v>x for v in vals)/len(vals),3)) for x in lines)
    return {"line":z[1],"over_rate":z[2]}
out={"n":len(ROWS),"seasons":seasons,"per_season":per,"cards_check":cards,"reliability":rel,"reliability_nteams":rel_n,
     "stats_xg_era":sorted(xg_era),"referee_reliability":ref_r,"referee_reliability_nrefs":ref_n,"referee_by_season":ref_season,
     "referee_count":len(refs),"movers":movers,"format":{"teams_per_season":{s:len(teams[s]) for s in seasons},
     "matches_per_team":{s:round(2*per[s]["n"]/len(teams[s]),1) for s in seasons},"phase_values":sorted({r["phase"] for r in ROWS}),
     "extra_phase_fields":False},"half_complete_seasons":sorted({r["season"] for r in complete}),"half_shares":half_rows,
     "invasion_check":invasion,"dev_lines":{"goals":line_for("goals",[1.5,2.5,3.5]),"sot":line_for("ShotsOnTarget",[7.5,8.5,9.5,10.5]),
     "corners":line_for("corners",[8.5,9.5,10.5,11.5]),"cards":line_for("yellow_cards",[3.5,4.5,5.5]),
     "total_shots":line_for("total_shots",[23.5,25.5,27.5,29.5])},"dev_n":len(dev),"virgin_n":per["2025/2026"]["n"],"confirmatory_n":per["2026/2027"]["n"]}
out["newcomer_gaps"]={"n":len(movers),"gf":avg([m["gf"] for m in movers]),"ga":avg([m["ga"] for m in movers]),
                     "league_gf":avg([int(r[f"{z}_goals"]) for r in ROWS for z in ("home","away")]),
                     "league_ga":avg([int(r[f"{'away' if z=='home' else 'home'}_goals"]) for r in ROWS for z in ("home","away")])}
out["newcomer_gaps"]["gf_gap"]=round(out["newcomer_gaps"]["gf"]-out["newcomer_gaps"]["league_gf"],3)
out["newcomer_gaps"]["ga_gap"]=round(out["newcomer_gaps"]["ga"]-out["newcomer_gaps"]["league_ga"],3)
(HERE/"eda_numbers.json").write_text(json.dumps(out,indent=2)+"\n")
(HERE/"inventory_summary.json").write_text(json.dumps(out,indent=2)+"\n")
print(json.dumps(out,indent=2))

