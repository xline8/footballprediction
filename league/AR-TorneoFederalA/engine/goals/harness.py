"""Deterministic DEV-ONLY expanding block walk-forward for G-FEDA."""
import csv, json, math
from collections import defaultdict
from datetime import date
from pathlib import Path
from dc import DC
from arms import adjusted_lambdas, newcomer_ids

HERE=Path(__file__).resolve().parent
DATA=HERE.parents[1]/"data"/"feda_matches.csv"
DEV_SEASONS=("2021","2022","2023","2024","2025")
SCORED=("2022","2023","2024","2025")

def load():
    rows=[]
    with DATA.open(newline="",encoding="utf-8") as f:
        for r in csv.DictReader(f):
            # The DEV loader admits only the frozen warm-up/scored seasons.
            if r["season"] not in DEV_SEASONS: continue
            rows.append({"match_id":r["match_id"],"season":r["season"],"date":date.fromisoformat(r["date"]),
                "hi":int(r["home_team_id"]),"ai":int(r["away_team_id"]),"home":r["home_team"],"away":r["away_team"],
                "yh":int(r["home_goals"]),"ya":int(r["away_goals"])})
    assert all(r["season"] in DEV_SEASONS for r in rows)
    return sorted(rows,key=lambda x:(x["date"],x["match_id"]))

def score(rows, ps):
    ll=rps=ou=0.0
    for r,p in zip(rows,ps):
        y=[1,0,0] if r["yh"]>r["ya"] else ([0,1,0] if r["yh"]==r["ya"] else [0,0,1]); q=[p["ph"],p["pd"],p["pa"]]
        ll-=math.log(max(q[y.index(1)],1e-12)); rps += .5*((q[0]-y[0])**2+(q[0]+q[1]-y[0]-y[1])**2)
        z=int(r["yh"]+r["ya"]>2.5); ou-=math.log(max(p["over25"] if z else 1-p["over25"],1e-12))
    n=len(rows); return {"n":n,"ll_1x2":ll/n,"rps":rps/n,"oull_2_5":ou/n}

def climatology(train):
    n=len(train); return {"ph":sum(r["yh"]>r["ya"] for r in train)/n,"pd":sum(r["yh"]==r["ya"] for r in train)/n,
        "pa":sum(r["yh"]<r["ya"] for r in train)/n,"over25":sum(r["yh"]+r["ya"]>2.5 for r in train)/n}

def trailing10(train, cutoff):
    by=defaultdict(list)
    for r in train:
        if r["date"] < cutoff:
            by[r["hi"]].append((r["date"],r["yh"],r["ya"])); by[r["ai"]].append((r["date"],r["ya"],r["yh"]))
    allg=[g for vals in by.values() for _,g,_ in vals]; league=sum(allg)/len(allg)
    means={}
    for t,vals in by.items():
        vals=sorted(vals)[-10:]; means[t]=(sum(x[1] for x in vals)/len(vals),sum(x[2] for x in vals)/len(vals))
    return means,league

def trailing_probs(r, means, league):
    hf,ha=means.get(r["hi"],(league,league)); af,aa=means.get(r["ai"],(league,league))
    lh,la=max(.01,(hf+aa)/2),max(.01,(af+ha)/2); m=DC(); m.rho=0.0
    return m.probs(lh,la)

def run_dev():
    rows=load(); assert len([r for r in rows if r["season"] in SCORED])==2083
    result=[]; pools={a:[] for a in ("gate_zero","x2")}; clim_pool=[]; trail_pool=[]; block_signs=[]; newcomer_example=None
    for season in SCORED:
        target=[r for r in rows if r["season"]==season]; cutoff=min(r["date"] for r in target); train=[r for r in rows if r["date"]<cutoff]
        cp=climatology(train); means,league=trailing10(train,cutoff); clim_ps=[cp]*len(target); trail_ps=[trailing_probs(r,means,league) for r in target]
        clim_pool += list(zip(target,clim_ps)); trail_pool += list(zip(target,trail_ps))
        block_model = {}
        for arm in ("gate_zero","x2"):
            model=DC().fit(train,cutoff); newcomers=newcomer_ids(target,[r for r in rows if r["season"]==str(int(season)-1)]); ps=[]; ex=None
            for r in target:
                (lh,la),offs=adjusted_lambdas(model,r["hi"],r["ai"],arm,newcomers); p=model.probs(lh,la); p.update(lh=lh,la=la); ps.append(p)
                if arm=="x2" and offs and ex is None: ex={"team":r["home"] if r["hi"] in offs else r["away"],"block":season,"mu":model.mu,"offsets":offs.get(r["hi"],offs.get(r["ai"]))}
            if ex and newcomer_example is None: newcomer_example=ex
            z=score(target,ps); z.update({"arm":arm,"block":season,"kind":"model"}); result.append(z); pools[arm]+=list(zip(target,ps))
            block_model[arm] = z
        z=score(target,clim_ps); z.update({"arm":"all","block":season,"kind":"climatology"}); result.append(z)
        z=score(target,trail_ps); z.update({"arm":"all","block":season,"kind":"trailing10"}); result.append(z)
        block_signs.append({"block":season,"x2_ll_minus_gate_zero":block_model["x2"]["ll_1x2"]-block_model["gate_zero"]["ll_1x2"]})
    for arm,pairs in pools.items():
        z=score([x[0] for x in pairs],[x[1] for x in pairs]); z.update({"arm":arm,"block":"pooled","kind":"model"}); result.append(z)
    for kind,pairs in (("climatology",clim_pool),("trailing10",trail_pool)):
        z=score([x[0] for x in pairs],[x[1] for x in pairs]); z.update({"arm":"all","block":"pooled","kind":kind}); result.append(z)
    base=next(x for x in result if x["kind"]=="climatology" and x["block"]=="pooled"); trail=next(x for x in result if x["kind"]=="trailing10" and x["block"]=="pooled")
    gates={}
    for arm in ("gate_zero","x2"):
        p=next(x for x in result if x["arm"]==arm and x["block"]=="pooled")
        gates[arm]={"dev_gate": all(p[k]<base[k] for k in ("ll_1x2","rps")) and p["oull_2_5"]<base["oull_2_5"],
            "margins":{"ll_1x2":base["ll_1x2"]-p["ll_1x2"],"rps":base["rps"]-p["rps"],"oull_2_5":base["oull_2_5"]-p["oull_2_5"]},
            "comparison":{"climatology":base,"trailing10":trail}}
    gates["x2"]["leg_iii"]={"block_signs":block_signs,"wins":sum(x["x2_ll_minus_gate_zero"]<=0 for x in block_signs),"required":2,"pass":sum(x["x2_ll_minus_gate_zero"]<=0 for x in block_signs)>=2}
    out={"protocol":"G-FEDA Phase B DEV ONLY","rows_loaded":len(rows),"scored_n":2083,"results":result,"gate":gates,"newcomer_example":newcomer_example}
    (HERE/"results_dev.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    fields=["arm","block","kind","n","ll_1x2","rps","oull_2_5"]
    with (HERE/"results_dev.csv").open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows({k:x.get(k,"") for k in fields} for x in result)
    return out

if __name__ == "__main__": run_dev()
