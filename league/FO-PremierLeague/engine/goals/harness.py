import csv, json, math
from datetime import date
from pathlib import Path
from dc import DC
from arms import adjusted_lambdas

HERE = Path(__file__).resolve().parent
DATA = HERE.parents[1] / "data" / "fo_premier_league_matches.csv"
SEASONS = ("2021","2022","2023","2024","2025")
SCORED = ("2022","2023","2024","2025")

def load(seasons=SEASONS):
    out=[]
    with open(DATA, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["season"] not in seasons: continue
            if r["season"] == "2026": raise AssertionError("2026 row entered dev goals harness")
            if r["excluded"] == "1" or not r["home_goals"] or not r["away_goals"]: continue
            out.append({"match_id":r["match_id"],"season":r["season"],"date":date.fromisoformat(r["date"]),"hi":int(r["home_team_id"]),"ai":int(r["away_team_id"]),"home":r["home"],"away":r["away"],"yh":int(r["home_goals"]),"ya":int(r["away_goals"])})
    out.sort(key=lambda x:(x["date"],x["match_id"]))
    assert len(out) == 674 and not any(x["season"]=="2026" for x in out)
    return out

def metrics(rows, ps):
    ll=rps=ou=0.0
    for r,p in zip(rows,ps):
        y=[1,0,0] if r["yh"]>r["ya"] else ([0,1,0] if r["yh"]==r["ya"] else [0,0,1]); q=[p["ph"],p["pd"],p["pa"]]
        ll -= math.log(max(q[y.index(1)],1e-15)); rps += .5*((q[0]-y[0])**2+(q[0]+q[1]-y[0]-y[1])**2)
        z=int(r["yh"]+r["ya"]>2.5); ou -= math.log(max(p["over25"] if z else 1-p["over25"],1e-15))
    n=len(rows); return {"n":n,"ll_1x2":ll/n,"rps":rps/n,"oull_2_5":ou/n}

def clim(train):
    n=len(train); return ([sum(r["yh"]>r["ya"] for r in train)/n,sum(r["yh"]==r["ya"] for r in train)/n,sum(r["yh"]<r["ya"] for r in train)/n],sum(r["yh"]+r["ya"]>2.5 for r in train)/n)

def run_dev():
    rows=load(); result=[]; csv_rows=[]
    for season in SCORED:
        target=[r for r in rows if r["season"]==season]; first=min(r["date"] for r in target); train=[r for r in rows if r["date"]<first]
        assert max(r["date"] for r in train)<first
        cp,co=clim(train); models={a:DC().fit(train,first) for a in ("gate_zero","shrink")}; preds={a:[] for a in models}; cprobs=[]
        for r in target:
            for a,m in models.items():
                lh,la=adjusted_lambdas(m,r["hi"],r["ai"],a); p=m.probs(lh,la); preds[a].append(p)
                if a=="gate_zero": csv_rows.append({"match_id":r["match_id"],"season":season,"date":r["date"].isoformat(),"home_team_id":r["hi"],"away_team_id":r["ai"],"home_goals":r["yh"],"away_goals":r["ya"],"p_home_gate_zero":p["ph"],"p_draw_gate_zero":p["pd"],"p_away_gate_zero":p["pa"],"p_over25_gate_zero":p["over25"]})
                else: csv_rows[-1].update({"p_home_shrink":p["ph"],"p_draw_shrink":p["pd"],"p_away_shrink":p["pa"],"p_over25_shrink":p["over25"]})
            cprobs.append({"ph":cp[0],"pd":cp[1],"pa":cp[2],"over25":co})
        for a in models: result.append({"arm":a,"season":season,"kind":"model","metrics":metrics(target,preds[a]),"fit":{"h":models[a].h,"rho":models[a].rho}})
        result.append({"arm":"climatology","season":season,"kind":"baseline","metrics":metrics(target,cprobs),"fit":{}})
    for a in ("gate_zero","shrink"):
        allr=[r for r in rows if r["season"] in SCORED]; ps=[]
        for season in SCORED:
            target=[r for r in rows if r["season"]==season]; first=min(r["date"] for r in target); m=DC().fit([r for r in rows if r["date"]<first],first)
            ps += [m.probs(*adjusted_lambdas(m,r["hi"],r["ai"],a)) for r in target]
        result.append({"arm":a,"season":"pooled","kind":"model","metrics":metrics(allr,ps),"fit":{}})
    # Pooled climatology remains the season-specific expanding climatology score.
    cp=[]; allr=[]
    for season in SCORED:
        target=[r for r in rows if r["season"]==season]; first=min(r["date"] for r in target); c=clim([r for r in rows if r["date"]<first]); cp += [{"ph":c[0][0],"pd":c[0][1],"pa":c[0][2],"over25":c[1]} for _ in target]; allr += target
    result.append({"arm":"climatology","season":"pooled","kind":"baseline","metrics":metrics(allr,cp),"fit":{}})
    by={(x["arm"],x["season"]):x for x in result}; gates={}
    base=by[("climatology","pooled")]["metrics"]
    for a in ("gate_zero","shrink"):
        m=by[(a,"pooled")]["metrics"]; gates[a]={"dev_gate_pass":m["ll_1x2"]<base["ll_1x2"] and m["rps"]<base["rps"] and m["oull_2_5"]<base["oull_2_5"],"pooled":m,"climatology":base}
    out={"protocol":{"loaded_rows":len(rows),"scored_rows":sum(by[("gate_zero",s)]["metrics"]["n"] for s in SCORED),"seasons":list(SCORED)},"metrics":result,"dev_gate":gates}
    (HERE/"results_dev.json").write_text(json.dumps(out,indent=2)+"\n")
    fields=["match_id","season","date","home_team_id","away_team_id","home_goals","away_goals","p_home_gate_zero","p_draw_gate_zero","p_away_gate_zero","p_over25_gate_zero","p_home_shrink","p_draw_shrink","p_away_shrink","p_over25_shrink","p_home_climatology","p_draw_climatology","p_away_climatology","p_over25_climatology"]
    # Add climatology probabilities to each row without changing match order.
    for r in csv_rows:
        first=min(x["date"] for x in rows if x["season"]==r["season"]); c=clim([x for x in rows if x["date"]<first]); r.update({"p_home_climatology":c[0][0],"p_draw_climatology":c[0][1],"p_away_climatology":c[0][2],"p_over25_climatology":c[1]})
    with open(HERE/"results_dev.csv","w",newline="",encoding="utf-8") as f: w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(csv_rows)
    print("goals pooled"); [print(a,gates[a]["pooled"]) for a in gates]; print("climatology",base)
    return out
