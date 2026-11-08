"""Development-only, season-blocked goals walk-forward."""
import csv, json, math
from datetime import date
from pathlib import Path
from dc import DC
from arms import adjusted_lambdas, match_counts

HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[1]; DATA=ROOT/"data"/"sco_league_one_matches.csv"
SEASONS=("2021/2022","2022/2023","2023/2024","2024/2025"); SCORED=SEASONS[1:]; FUTURE={"2025/2026","2026/2027"}

def load():
    rows=[]
    with DATA.open(newline="",encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["season"] in FUTURE: continue
            if r["season"] not in SEASONS: continue
            rows.append({"match_id":r["match_id"],"season":r["season"],"date":date.fromisoformat(r["date"]),"hi":int(r["home_team_id"]),"ai":int(r["away_team_id"]),"home":r["home_team"],"away":r["away_team"],"yh":int(r["home_goals"]),"ya":int(r["away_goals"]),"xgh":None,"xga":None})
    rows.sort(key=lambda x:(x["date"],x["match_id"]))
    assert all(sum(x["season"]==s for x in rows)==180 for s in SEASONS)
    return rows

def movers_for(target_season, prior, mu):
    table=json.loads((ROOT/"analysis"/"movers.json").read_text())["by_season"]
    target=table[target_season]; result={}; details={}
    mu=max(mu,.1)
    for direction,key in (("down","down_from_championship"),("up_other","up_other")):
        vals=[]; historical=[]
        for season,entry in table.items():
            if season >= target_season or season not in SEASONS: continue
            ids=[int(x) for x in entry[key]["team_ids"]]
            sg=[g for g in prior if g["season"]==season]
            league=sum(g["yh"]+g["ya"] for g in sg)/(2*len(sg)) if sg else 0
            for team in ids:
                tg=[g for g in sg if g["hi"]==team or g["ai"]==team]
                if tg: vals.append((sum(g["yh"] if g["hi"]==team else g["ya"] for g in tg)/len(tg)-league, sum(g["ya"] if g["hi"]==team else g["yh"] for g in tg)/len(tg)-league)); historical.append(team)
        dg,da=(sum(x[0] for x in vals)/len(vals),sum(x[1] for x in vals)/len(vals)) if len(historical)>=2 else (0.,0.)
        lg,la=math.log(max(mu+dg,.1)/mu),math.log(max(mu+da,.1)/mu)
        ids=[int(x) for x in target[key]["team_ids"]]
        for team in ids: result[team]=(lg,la)
        details[direction]={"team_ids":ids,"log_attack":lg,"log_defence":la,"delta_gf":dg,"delta_ga":da,"history_clubs":len(historical)}
    return result,details

def score(rows, probs):
    ll=rps=ou=0.
    for g,p in zip(rows,probs):
        y=[1,0,0] if g["yh"]>g["ya"] else ([0,1,0] if g["yh"]==g["ya"] else [0,0,1]); q=[p["ph"],p["pd"],p["pa"]]
        ll-=math.log(max(q[y.index(1)],1e-12)); rps+=.5*((q[0]-y[0])**2+(q[0]+q[1]-y[0]-y[1])**2)
        over=int(g["yh"]+g["ya"]>2.5); ou-=math.log(max(p["over25"] if over else 1-p["over25"],1e-12))
    n=len(rows); return {"n":n,"ll_1x2":ll/n,"rps":rps/n,"oull_2_5":ou/n}

def clim(train):
    n=len(train); h=sum(g["yh"]>g["ya"] for g in train)/n; d=sum(g["yh"]==g["ya"] for g in train)/n
    return (h,d,1-h-d),sum(g["yh"]+g["ya"]>2.5 for g in train)/n

def run_dev():
    rows=load(); all_metrics=[]; pred=[]; offsets={}
    for season in SCORED:
        target=[g for g in rows if g["season"]==season]; train=[g for g in rows if g["date"]<min(x["date"] for x in target)]
        cp,co=clim(train); fit=DC().fit(train,min(x["date"] for x in target)); xoff,detail=movers_for(season,train,fit.mu); offsets[season]=detail
        models={}
        for arm in ("gate_zero","shrink","x2"):
            model=fit; counts=match_counts(train)
            ps=[]
            for g in target:
                lh,la=adjusted_lambdas(model,g["hi"],g["ai"],arm,xoff,counts); p=model.probs(lh,la); ps.append(p)
                pred.append({"match_id":g["match_id"],"season":season,"date":g["date"].isoformat(),"home_team_id":g["hi"],"away_team_id":g["ai"],"actual_home_goals":g["yh"],"actual_away_goals":g["ya"],"arm":arm,"lambda_home":lh,"lambda_away":la,"p_home":p["ph"],"p_draw":p["pd"],"p_away":p["pa"],"p_over_2_5":p["over25"],"baseline_p_home":cp[0],"baseline_p_draw":cp[1],"baseline_p_away":cp[2],"baseline_p_over_2_5":co})
            models[arm]=(target,ps); all_metrics.append({"arm":arm,"season":season,"kind":"model",**score(target,ps)})
            all_metrics.append({"arm":arm,"season":season,"kind":"climatology",**score(target,[{"ph":cp[0],"pd":cp[1],"pa":cp[2],"over25":co} for _ in target])})
    for arm in ("gate_zero","shrink","x2"):
        rr=[r for r in pred if r["arm"]==arm]; all_metrics.append({"arm":arm,"season":"pooled","kind":"model",**score(rows=[g for g in rows if g["season"] in SCORED],probs=[{"ph":r["p_home"],"pd":r["p_draw"],"pa":r["p_away"],"over25":r["p_over_2_5"]} for r in rr])})
        cr=[]; cpairs=[]
        for s in SCORED:
            t=[g for g in rows if g["season"]==s]; tr=[g for g in rows if g["date"]<min(x["date"] for x in t)]; c,o=clim(tr); cr+=t; cpairs += [{"ph":c[0],"pd":c[1],"pa":c[2],"over25":o} for _ in t]
        all_metrics.append({"arm":arm,"season":"pooled","kind":"climatology",**score(cr,cpairs)})
    for r in all_metrics: r.pop("kind",None) if False else None
    gate={a:(next(x for x in all_metrics if x["arm"]==a and x["season"]=="pooled" and x["kind"]=="model")["ll_1x2"]<next(x for x in all_metrics if x["arm"]==a and x["season"]=="pooled" and x["kind"]=="climatology")["ll_1x2"] and next(x for x in all_metrics if x["arm"]==a and x["season"]=="pooled" and x["kind"]=="model")["rps"]<next(x for x in all_metrics if x["arm"]==a and x["season"]=="pooled" and x["kind"]=="climatology")["rps"] and next(x for x in all_metrics if x["arm"]==a and x["season"]=="pooled" and x["kind"]=="model")["oull_2_5"]<next(x for x in all_metrics if x["arm"]==a and x["season"]=="pooled" and x["kind"]=="climatology")["oull_2_5"]) for a in ("gate_zero","shrink","x2")}
    result={"protocol":{"league":"SCO-LeagueOne","dev_seasons_loaded":list(SEASONS),"scored_n":540,"primary_line":"OU2.5","sign_convention":"actual_minus_predicted"},"metrics":all_metrics,"baselines":{"type":"expanding_climatology","pooled":next(x for x in all_metrics if x["season"]=="pooled" and x["kind"]=="climatology")},"dev_gate_pass":gate,"x2_offsets":offsets}
    (HERE/"results_dev.json").write_text(json.dumps(result,indent=2)+"\n")
    fields=["match_id","season","date","home_team_id","away_team_id","actual_home_goals","actual_away_goals","arm","lambda_home","lambda_away","p_home","p_draw","p_away","p_over_2_5","baseline_p_home","baseline_p_draw","baseline_p_away","baseline_p_over_2_5"]
    with (HERE/"results_dev.csv").open("w",newline="",encoding="utf-8") as f: w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(pred)
    print(json.dumps({"dev_gate_pass":gate,"pooled":[x for x in all_metrics if x["season"]=="pooled"]},indent=2)); return result
