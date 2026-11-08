"""G-PY goals engine: chronological Dixon-Coles evaluation and outputs."""
import csv, json, math
from datetime import date
from pathlib import Path
from dc import DC
from arms import adjusted_lambdas, match_counts

ROOT=Path(__file__).resolve().parents[2]; DATA=ROOT/"data"/"py_matches.csv"; OUT=Path(__file__).resolve().parent
SEED={"2021 - Apertura","2021 - Clausura"}; DEV=tuple(f"{y} - {p}" for y in range(2022,2026) for p in ("Apertura","Clausura")); VIRGIN="2026 - Apertura"

def load(seasons):
    out=[]
    with DATA.open(newline="",encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["season"] in seasons:
                out.append({"match_id":r["match_id"],"season":r["season"],"date":date.fromisoformat(r["date"]),"hi":r["home_team_id"],"ai":r["away_team_id"],"home":r["home_team"],"away":r["away_team"],"yh":int(float(r["home_goals"])),"ya":int(float(r["away_goals"])),"xgh":None,"xga":None})
    return sorted(out,key=lambda x:(x["date"],x["match_id"]))

def scores(rows,probs):
    ll=rps=ou=0.0
    for r,p in zip(rows,probs):
        y=(1,0,0) if r["yh"]>r["ya"] else ((0,1,0) if r["yh"]==r["ya"] else (0,0,1)); q=[p["ph"],p["pd"],p["pa"]]; ll-=math.log(max(q[y.index(1)],1e-12)); rps+=.5*((q[0]-y[0])**2+(q[0]+q[1]-y[0]-y[1])**2); z=r["yh"]+r["ya"]>2.5; ou-=math.log(max(p["over25"] if z else 1-p["over25"],1e-12))
    return {"n":len(rows),"ll_1x2":ll/len(rows),"rps":rps/len(rows),"oull_2_5":ou/len(rows)}

def clim(rows):
    n=len(rows); h=sum(r["yh"]>r["ya"] for r in rows)/n; d=sum(r["yh"]==r["ya"] for r in rows)/n; return [h,d,1-h-d],sum(r["yh"]+r["ya"]>2.5 for r in rows)/n
def fit_predict(train,target,arm):
    cutoff=min(r["date"] for r in target); prior=[r for r in train if r["date"]<cutoff]; return DC().fit(prior,cutoff),match_counts(prior)

def run_dev():
    rows=load(SEED|set(DEV)); assert not any(r["season"].startswith("2026") for r in rows)
    result=[]
    for arm in ("gate_zero","shrink"):
        pairs=[]; cpairs=[]
        for s in DEV:
            target=[r for r in rows if r["season"]==s]; train=[r for r in rows if r["date"]<min(x["date"] for x in target)]; m,c=fit_predict(train,target,arm); ps=[m.probs(*adjusted_lambdas(m,r["hi"],r["ai"],arm,c)) for r in target]; x=scores(target,ps); x.update(arm=arm,season=s,kind="model"); result.append(x); pairs.extend(zip(target,ps)); p,o=clim(train); x=scores(target,[{"ph":p[0],"pd":p[1],"pa":p[2],"over25":o} for _ in target]); x.update(arm=arm,season=s,kind="climatology"); result.append(x); cpairs.extend((r,{"ph":p[0],"pd":p[1],"pa":p[2],"over25":o}) for r in target)
        x=scores([r for r,_ in pairs],[p for _,p in pairs]); x.update(arm=arm,season="pooled",kind="model"); result.append(x); x=scores([r for r,_ in cpairs],[p for _,p in cpairs]); x.update(arm=arm,season="pooled",kind="climatology"); result.append(x)
    (OUT/"results_dev.json").write_text(json.dumps(result,indent=2)+"\n"); print_table(result,"dev"); return result

def se(v):
    a=sum(v)/len(v); return (sum((x-a)**2 for x in v)/(len(v)-1))**.5/len(v)**.5
def print_table(data,label):
    print(label); print("arm season kind n ll_1x2 rps oull_2_5")
    if label=="dev":
        for x in data: print(x["arm"],x["season"],x["kind"],x["n"],f'{x["ll_1x2"]:.6f}',f'{x["rps"]:.6f}',f'{x["oull_2_5"]:.6f}')
    else:
        for a,x in data.items():
            if "ll_1x2" in x: print(a,x["n"],f'{x["ll_1x2"]:.6f}',f'{x["rps"]:.6f}',f'{x["oull_2_5"]:.6f}',f'{x["climatology"]["ll_1x2"]:.6f}',f'{x["calibration"]["home_win_diff"]:.6f}',f'{x["calibration"]["over25_diff"]:.6f}')

def virgin_metrics(arms):
    dev=json.loads((OUT/"results_dev.json").read_text()); get=lambda a,k:next(x for x in dev if x["arm"]==a and x["season"]=="pooled" and x["kind"]==k); base=get("gate_zero","climatology"); gates={a:get(a,"model")["ll_1x2"]<base["ll_1x2"] and get(a,"model")["rps"]<base["rps"] and get(a,"model")["oull_2_5"]<base["oull_2_5"] for a in ("gate_zero","shrink")}
    if not gates["gate_zero"]:
        out={"verdict":"FAIL","shipped_arm":None,"legs":{"dev_gate":gates,"virgin_read":False}}; (OUT/"results_virgin.json").write_text(json.dumps(out,indent=2)+"\n"); print("virgin not read: Gate Zero failed dev gate"); return out
    rows=load(SEED|set(DEV)|{VIRGIN}); assert not any(r["season"]=="2026 - Clausura" for r in rows); target=[r for r in rows if r["season"]==VIRGIN]; train=[r for r in rows if r["season"]!=VIRGIN]; p,o=clim(train); result={}
    for arm in arms:
        if not gates[arm]: continue
        m,c=fit_predict(train,target,arm); ps=[]
        for r in target:
            h,a=adjusted_lambdas(m,r["hi"],r["ai"],arm,c); q=m.probs(h,a); q.update(lh=h,la=a); ps.append(q)
        cal={"home_win_diff":sum(q["ph"]-(r["yh"]>r["ya"]) for q,r in zip(ps,target))/len(target),"over25_diff":sum(q["over25"]-(r["yh"]+r["ya"]>2.5) for q,r in zip(ps,target))/len(target)}; cal.update(home_win_se=se([q["ph"]-(r["yh"]>r["ya"]) for q,r in zip(ps,target)]),over25_se=se([q["over25"]-(r["yh"]+r["ya"]>2.5) for q,r in zip(ps,target)])); result[arm]=dict(scores(target,ps),arm=arm,climatology=scores(target,[{"ph":p[0],"pd":p[1],"pa":p[2],"over25":o} for _ in target]),calibration=cal,params={"a":dict(m.a),"d":dict(m.d),"h":m.h,"rho":m.rho,"mu":m.mu,"arm":arm,"match_counts":dict(c)})
    legs={"dev_gate":gates,"arms":{}}
    for a,x in result.items():
        c=x["calibration"]; i=x["ll_1x2"]<=result["gate_zero"]["ll_1x2"] and x["ll_1x2"]<=x["climatology"]["ll_1x2"]; ii=abs(c["home_win_diff"])<=.01+c["home_win_se"] and abs(c["over25_diff"])<=.01+c["over25_se"]; iii=True
        if a=="shrink": iii=sum(get("shrink","model")["ll_1x2"]<=get("gate_zero","model")["ll_1x2"] for _ in DEV)>=4
        legs["arms"][a]={"dev":gates[a],"i":i,"ii":ii,"iii":iii}
    eligible=[a for a,l in legs["arms"].items() if all(l[k] for k in ("dev","i","ii","iii"))]; ship=min(eligible,key=lambda a:(result[a]["ll_1x2"],a!="gate_zero")) if eligible else None; out={**result,"verdict":"PASS" if ship else "FAIL","shipped_arm":ship,"legs":legs}; (OUT/"results_virgin.json").write_text(json.dumps(out,indent=2)+"\n"); print_table(result,"virgin"); print("verdict",out["verdict"],"shipped",ship)
    if ship:
        m,c=fit_predict(train,target,ship); ps=[]
        for r in target:
            h,a=adjusted_lambdas(m,r["hi"],r["ai"],ship,c); q=m.probs(h,a); q.update(lh=h,la=a); ps.append(q)
        dest=ROOT/"predictions"; dest.mkdir(exist_ok=True); fields=["match_id","date","home_team","away_team","home_goals","away_goals","lam_h","lam_a","rho","ph","pd","pa","p_over_1_5","p_over_2_5","p_over_3_5","mean_1h","mean_2h","arm"]
        with (dest/"g_py_virgin_predictions.csv").open("w",newline="",encoding="utf-8") as f:
            w=csv.DictWriter(f,fieldnames=fields); w.writeheader()
            for r,q in zip(target,ps): w.writerow({"match_id":r["match_id"],"date":r["date"].isoformat(),"home_team":r["home"],"away_team":r["away"],"home_goals":r["yh"],"away_goals":r["ya"],"lam_h":q["lh"],"lam_a":q["la"],"rho":m.rho,"ph":q["ph"],"pd":q["pd"],"pa":q["pa"],"p_over_1_5":q["over15"],"p_over_2_5":q["over25"],"p_over_3_5":q["over35"],"mean_1h":.418*(q["lh"]+q["la"]),"mean_2h":.582*(q["lh"]+q["la"]),"arm":ship})
        (OUT/"fitted_params_virgin.json").write_text(json.dumps(result[ship]["params"],indent=2)+"\n")
    return out
