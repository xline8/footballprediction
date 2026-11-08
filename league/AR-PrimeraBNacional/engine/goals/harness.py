"""Expanding, block-blocked BNAC goals dev evaluation. This module has no virgin path."""
import csv, json, math
from datetime import date
from pathlib import Path
from dc import DC
from arms import mover_ids, adjusted_lambdas

HERE = Path(__file__).resolve().parent; DATA = HERE.parents[1]/"data"/"bnac_matches.csv"
DEV = ("2021","2022","2023","2024","2025"); SCORED = DEV[1:]

def load():
    out=[]
    with DATA.open(newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["season"] not in DEV: continue
            out.append({"match_id":r["match_id"],"season":r["season"],"date":date.fromisoformat(r["date"]),"hi":int(r["home_id"]),"ai":int(r["away_id"]),"home":r["home_name"],"away":r["away_name"],"yh":int(r["hg"]),"ya":int(r["ag"])})
    out.sort(key=lambda r:(r["date"],r["match_id"])); assert all(r["season"] != "2026" for r in out)
    return out

def metrics(rows, ps):
    ll=rps=ou=0.0
    for r,p in zip(rows,ps):
        y=(1,0,0) if r["yh"]>r["ya"] else ((0,1,0) if r["yh"]==r["ya"] else (0,0,1)); q=(p["ph"],p["pd"],p["pa"]); i=y.index(1)
        ll-=math.log(max(q[i],1e-15)); rps += .5*((q[0]-y[0])**2+(q[0]+q[1]-y[0]-y[1])**2)
        z=int(r["yh"]+r["ya"]>2.5); po=p["over25"]; ou-=math.log(max(po if z else 1-po,1e-15))
    n=len(rows); return {"n":n,"ll_1x2":ll/n,"rps":rps/n,"oull_2_5":ou/n}

def run_dev():
    rows=load(); assert len(rows)==3226 and not any(r["season"]=="2026" for r in rows)
    result=[]; pools={a:[] for a in ("gate_zero","x2")}; clim_pool=[]
    for s in SCORED:
        target=[r for r in rows if r["season"]==s]; cut=min(r["date"] for r in target); train=[r for r in rows if r["date"]<cut]
        cp=[sum(r["yh"]>r["ya"] for r in train)/len(train),sum(r["yh"]==r["ya"] for r in train)/len(train)]; cp.append(1-cp[0]-cp[1]); co=sum(r["yh"]+r["ya"]>2.5 for r in train)/len(train)
        clim=[{"ph":cp[0],"pd":cp[1],"pa":cp[2],"over25":co} for _ in target]; clim_pool += list(zip(target,clim))
        for arm in pools:
            m=DC().fit(train,cut); movers=mover_ids(s,rows); ps=[]
            for r in target:
                lh,la=adjusted_lambdas(m,r["hi"],r["ai"],arm,movers); p=m.probs(lh,la); p.update(lh=lh,la=la); ps.append(p)
            z=metrics(target,ps); z.update({"arm":arm,"season":s,"kind":"model","gate_zero_sign":None}); result.append(z); pools[arm] += list(zip(target,ps))
        z=metrics(target,clim); z.update({"arm":"baseline","season":s,"kind":"climatology","gate_zero_sign":None}); result.append(z)
    for arm,pairs in pools.items():
        z=metrics([r for r,_ in pairs],[p for _,p in pairs]); z.update({"arm":arm,"season":"pooled","kind":"model","gate_zero_sign":None}); result.append(z)
    z=metrics([r for r,_ in clim_pool],[p for _,p in clim_pool]); z.update({"arm":"baseline","season":"pooled","kind":"climatology","gate_zero_sign":None}); result.append(z)
    gz={r["season"]:r["ll_1x2"] for r in result if r["arm"]=="gate_zero" and r["kind"]=="model"}
    for r in result:
        if r["arm"] in ("gate_zero","x2") and r["season"] in SCORED: r["gate_zero_sign"]={"arm_ll":r["ll_1x2"],"gate_zero_ll":gz[r["season"]],"ll_le_gate_zero":r["ll_1x2"]<=gz[r["season"]]}
    pooled={a:next(r for r in result if r["arm"]==a and r["season"]=="pooled") for a in ("gate_zero","x2")}; base=next(r for r in result if r["arm"]=="baseline" and r["season"]=="pooled")
    gate={a:{"ll_beats_climatology":pooled[a]["ll_1x2"]<base["ll_1x2"],"rps_beats_climatology":pooled[a]["rps"]<base["rps"],"oull_beats_climatology":pooled[a]["oull_2_5"]<base["oull_2_5"]} for a in pooled}
    for a in gate: gate[a]["pass"]=all(gate[a].values()); gate[a]["margins"]={"ll":base["ll_1x2"]-pooled[a]["ll_1x2"],"rps":base["rps"]-pooled[a]["rps"],"oull":base["oull_2_5"]-pooled[a]["oull_2_5"]}
    out={"protocol":{"loaded_seasons":list(DEV),"scored_seasons":list(SCORED),"loaded_n":len(rows),"scored_n":next(x["n"] for x in result if x["arm"]=="gate_zero" and x["season"]=="pooled")},"arms":gate,"rows":result}
    (HERE/"results_dev.json").write_text(json.dumps(out,indent=2)+"\n")
    fields=["arm","season","kind","n","ll_1x2","rps","oull_2_5","gate_zero_sign"]
    with (HERE/"results_dev.csv").open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows({k:r.get(k) for k in fields} for r in result)
    return out
