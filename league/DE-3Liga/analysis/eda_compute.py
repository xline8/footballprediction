"""Measured EDA inventory for DE-3Liga; no model fitting."""
import csv, json, math, random, statistics as st
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
R = list(csv.DictReader(open(HERE.parent / "data/de3_matches.csv")))
S = sorted({x["season"] for x in R}); DEV = S[:4]
def f(r,k):
    v=r.get(k); return None if v in (None,"","None") else float(v)
def tot(r,k):
    a,b=f(r,k+"_home"),f(r,k+"_away")
    return None if a is None or b is None else a+b
def cor(a,b):
    ma,mb=st.mean(a),st.mean(b); den=math.sqrt(sum((x-ma)**2 for x in a)*sum((y-mb)**2 for y in b))
    return sum((x-ma)*(y-mb) for x,y in zip(a,b))/den if den else None
def rel(d, minimum=20):
    d={k:v for k,v in d.items() if len(v)>=minimum}; rng=random.Random(42); z=[]
    for _ in range(60):
        a=[];b=[]
        for v in d.values():
            ix=list(range(len(v)));rng.shuffle(ix);h=len(ix)//2
            a.append(st.mean(v[i] for i in ix[:h]));b.append(st.mean(v[i] for i in ix[h:]))
        z.append(cor(a,b))
    return round(st.mean(z),3),len(d)
def series(k, against=False):
    d=defaultdict(list)
    for r in R:
        for side,opp in (("home","away"),("away","home")):
            v=f(r,k+"_"+(opp if against else side))
            if v is not None:d[r[side+"_team_id"]].append(v)
    return d

out={"n":len(R),"seasons":S,"team_ids":len({x["home_team_id"] for x in R}|{x["away_team_id"] for x in R})}
per={}
for s in S:
    q=[x for x in R if x["season"]==s]
    def avg(k):
        v=[tot(x,k) for x in q];v=[x for x in v if x is not None]
        return round(st.mean(v),3) if v else None
    per[s]={"n":len(q),"goals":round(st.mean([int(x["home_goals"])+int(x["away_goals"]) for x in q]),3),"home_goals":round(st.mean([int(x["home_goals"]) for x in q]),3),"away_goals":round(st.mean([int(x["away_goals"]) for x in q]),3),"sot":avg("ShotsOnTarget"),"corners":avg("corners"),"yellows":avg("yellow"),"shots":avg("total_shots"),"half_pct":round(100*st.mean([int(x["has_stats_half"]) for x in q]),1),"ref_pct":round(100*sum(bool(x["referee"]) for x in q)/len(q),1),"touch_pct":round(100*sum(f(x,"touches_opp_box_home") is not None for x in q)/len(q),1),"phases":{p:sum(x["phase"]==p for x in q) for p in sorted({x["phase"] for x in q})}}
out["per_season"]=per

# Stats-feed cards versus event-derived cards.
q=[x for x in R if f(x,"yellow_cards_home") is not None]
d=[f(x,"yellow_cards_home")+f(x,"yellow_cards_away")-float(x["ev_yellow_home"])-float(x["ev_yellow_away"]) for x in q]
d2=[v-float(x["ev_yellowred_home"])-float(x["ev_yellowred_away"]) for v,x in zip(d,q)]
out["cards_check"]={"n_stats":len(q),"exact_pct":round(100*sum(v==0 for v in d)/len(d),1),"mean_stats_minus_events":round(st.mean(d),3),"stats_lower_pct":round(100*sum(v<0 for v in d)/len(d),1),"stats_higher_pct":round(100*sum(v>0 for v in d)/len(d),1),"max_abs":int(max(map(abs,d))),"exact_pct_incl_yellowred":round(100*sum(v==0 for v in d2)/len(d2),1),"mean_diff_incl_yellowred":round(st.mean(d2),3)}

rel_out={}
for name,k,ag in [("goals_for","goals",False),("goals_against","goals",True),("sot_for","ShotsOnTarget",False),("sot_against","ShotsOnTarget",True),("corners_for","corners",False),("corners_against","corners",True),("shots_for","total_shots",False),("shots_against","total_shots",True),("touches_for","touches_opp_box",False),("touches_against","touches_opp_box",True),("possession_for","BallPossesion",False),("possession_against","BallPossesion",True),("big_chance_for","big_chance",False),("big_chance_against","big_chance",True)]:
    if k=="goals":
        z=defaultdict(list)
        for x in R:
            z[x["home_team_id"]].append(int(x["away_goals"] if ag else x["home_goals"]));z[x["away_team_id"]].append(int(x["home_goals"] if ag else x["away_goals"]))
    else:z=series(k,ag)
    rel_out[name]=rel(z)
z=defaultdict(list)
for x in R:
    if x["referee"]:z[x["referee"]].append(float(x["yellow_home"])+float(x["yellow_away"]))
out["reliability"]={k:v[0] for k,v in rel_out.items()};out["reliability_nteams"]={k:v[1] for k,v in rel_out.items()};out["ref_reliability"],out["ref_n_ge20"]=rel(z)

HS=[s for s in S if s!="2026/2027" and per[s]["half_pct"]>90];out["half_complete_seasons"]=HS
def half(k):
    sh=[];wt=[];n=d=0
    for x in R:
        if x["season"] not in HS:continue
        a,b,c,e=f(x,"fh_"+k+"_home"),f(x,"fh_"+k+"_away"),f(x,k+"_home"),f(x,k+"_away")
        if None not in (a,b,c,e) and c+e:sh.append((a+b)/(c+e));wt.append(c+e);n+=a+b;d+=c+e
    m=st.mean(sh);return {"n":len(sh),"share":round(n/d,4),"true_var":round(st.variance(sh)-st.mean([m*(1-m)/w for w in wt]),4)}
out["half_shares"]={k:half(k) for k in ("ShotsOnTarget","corners","total_shots","yellow_cards")}
sh=[];wt=[];n=d=0
for x in R:
    if x["season"] in HS:
        t=int(x["home_goals"])+int(x["away_goals"]);h=int(x["ht_home_goals"])+int(x["ht_away_goals"])
        if t:sh.append(h/t);wt.append(t);n+=h;d+=t
m=st.mean(sh);out["half_shares"]["goals"]={"n":len(sh),"share":round(n/d,4),"true_var":round(st.variance(sh)-st.mean([m*(1-m)/w for w in wt]),4)}

C=[x for x in R if x["season"]!="2026/2027"]
out["pooled"]={"n":len(C),"goals":round(st.mean([int(x["home_goals"])+int(x["away_goals"]) for x in C]),3),"home_goals":round(st.mean([int(x["home_goals"]) for x in C]),3),"away_goals":round(st.mean([int(x["away_goals"]) for x in C]),3),"hw":round(100*sum(int(x["home_goals"])>int(x["away_goals"]) for x in C)/len(C),1),"draw":round(100*sum(int(x["home_goals"])==int(x["away_goals"]) for x in C)/len(C),1),"aw":round(100*sum(int(x["home_goals"])<int(x["away_goals"]) for x in C)/len(C),1),"over25":round(100*sum(int(x["home_goals"])+int(x["away_goals"])>2 for x in C)/len(C),1),"btts":round(100*sum(int(x["home_goals"])>0 and int(x["away_goals"])>0 for x in C)/len(C),1)}
out["dev_rates"]={}
for k,lines in (("ShotsOnTarget",(8.5,9.5,10.5)),("corners",(9.5,10.5,11.5)),("yellow",(3.5,4.5,5.5)),("total_shots",(25.5,26.5,27.5))):
    v=[]
    for x in R:
        if x["season"] not in DEV:continue
        y=float(x["yellow_home"])+float(x["yellow_away"]) if k=="yellow" else tot(x,k)
        if y is not None:v.append(y)
    out["dev_rates"][k]={str(a):round(sum(y>a for y in v)/len(v),3) for a in lines};out["dev_rates"][k+"_n"]=len(v)
out["virgin_n"]=per["2025/2026"]["n"];out["dev_scored_n"]=sum(per[s]["n"] for s in DEV[1:])
out["movers"]={};ids={s:{y for x in R if x["season"]==s for y in (x["home_team_id"],x["away_team_id"])} for s in S[:-1]}
for prev,cur in zip(S[:-2],S[1:-1]):
    e=ids[cur]-ids[prev];gf=[];ga=[]
    for x in R:
        if x["season"]==cur:
            if x["home_team_id"] in e:gf.append(int(x["home_goals"]));ga.append(int(x["away_goals"]))
            if x["away_team_id"] in e:gf.append(int(x["away_goals"]));ga.append(int(x["home_goals"]))
    lg=[int(x["home_goals"]) for x in R if x["season"]==cur]+[int(x["away_goals"]) for x in R if x["season"]==cur]
    out["movers"][cur]={"entrants":len(e),"entrant_matches":len(gf),"gf":round(st.mean(gf),3),"ga":round(st.mean(ga),3),"league_gf":round(st.mean(lg),3),"delta_gf":round(st.mean(gf)-st.mean(lg),3),"delta_ga":round(st.mean(ga)-st.mean(lg),3)}
(HERE/"eda_numbers.json").write_text(json.dumps(out,indent=1));print(json.dumps(out,indent=1))
