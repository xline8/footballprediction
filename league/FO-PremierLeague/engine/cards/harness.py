import csv,json,math
from datetime import date
from pathlib import Path
from model import Online,estimate_r,nb_over
HERE=Path(__file__).resolve().parent; DATA=HERE.parents[1]/"data"/"fo_premier_league_matches.csv"; SCORED=("2022","2023","2024","2025")
def load():
    out=[]
    with open(DATA,newline="",encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["season"] not in ("2021",)+SCORED: continue
            if r["season"]=="2026": raise AssertionError("2026 row entered dev cards harness")
            if r["excluded"]=="1" or not r["yellow_home"] or not r["yellow_away"]: continue
            yh,ya=int(r["yellow_home"]),int(r["yellow_away"])
            out.append({"match_id":r["match_id"],"season":r["season"],"date":date.fromisoformat(r["date"]),"day":date.fromisoformat(r["date"]).toordinal(),"home_id":int(r["home_team_id"]),"away_id":int(r["away_team_id"]),"home":r["home"],"away":r["away"],"yh":yh,"ya":ya,"y":yh+ya})
    out.sort(key=lambda x:(x["date"],x["match_id"])); assert len(out)==674 and not any(x["season"]=="2026" for x in out); return out
def score(rows,rmap):
    z={}
    for method in ("model","base","naive"):
        z[method]={}
        for line in (3.5,4.5):
            ps=[nb_over(x[method],rmap[method],line) for x in rows]; ys=[int(x["y"]>line) for x in rows]; n=len(rows)
            z[method][str(line)]={"n":n,"ll":sum(-(y*math.log(max(p,1e-15))+(1-y)*math.log(max(1-p,1e-15))) for p,y in zip(ps,ys))/n,"mean_p":sum(ps)/n,"actual_rate":sum(ys)/n}
    return z
def dev():
    rows=load(); ons={"gate_zero":Online(8),"shrink":Online(16)}; warm={a:[] for a in ons}; scored={a:{s:[] for s in SCORED} for a in ons}; csvrows=[]
    for r in rows:
        before=[o.n_updates for o in ons.values()]
        preds={a:o.predict(r) for a,o in ons.items()}
        assert before == [o.n_updates for o in ons.values()], "cards state changed during prediction"
        for a,p in preds.items():
            rec={"y":r["y"],**{k:p[k] for k in ("model","base","naive")}}
            (warm[a] if r["season"]=="2021" else scored[a][r["season"]]).append(rec)
        if r["season"] in SCORED:
            z={"match_id":r["match_id"],"season":r["season"],"date":r["date"].isoformat(),"home_team_id":r["home_id"],"away_team_id":r["away_id"],"yellows_total":r["y"]}
            for a,p in preds.items(): z.update({f"mu_{a}":p["model"],f"p_over35_{a}":nb_over(p["model"],0,3.5),f"p_over45_{a}":nb_over(p["model"],0,4.5)})
            csvrows.append(z)
        for o,b in zip(ons.values(), before): o.update(r); assert o.n_updates == b+1, "cards state did not update after prediction"
    # r is estimated from warm-up residuals, then applied to the frozen predictions.
    rmap={a:{m:estimate_r(warm[a],m) for m in ("model","base","naive")} for a in ons}
    out={"protocol":{"loaded_rows":len(rows),"scored_rows":sum(len(scored["gate_zero"][s]) for s in SCORED),"warmup":"2021","scored":list(SCORED)},"arms":{}}
    allr={}
    for a in ons:
        seasons={}; allr[a]=sum((scored[a][s] for s in SCORED),[])
        for s in SCORED: seasons[s]=score(scored[a][s],rmap[a])
        seasons["pooled"]=score(allr[a],rmap[a]); out["arms"][a]={"r":rmap[a],"seasons":seasons}
    for i,z in enumerate(csvrows):
        # probabilities are filled after the causal r estimates; each row retains its predictions.
        a="gate_zero"; z["p_over35_gate_zero"]=nb_over(z["mu_gate_zero"],rmap[a]["model"],3.5); z["p_over45_gate_zero"]=nb_over(z["mu_gate_zero"],rmap[a]["model"],4.5); z["p_over35_shrink"]=nb_over(z["mu_shrink"],rmap["shrink"]["model"],3.5); z["p_over45_shrink"]=nb_over(z["mu_shrink"],rmap["shrink"]["model"],4.5)
        # These are identical across arms and use the corresponding arm's frozen r.
        # Base/naive means are retained in a side map below while writing CSV.
    # Rebuild scored prediction rows for complete CSV fields from the stored causal records.
    idx=0
    for s in SCORED:
        for j in range(len(scored["gate_zero"][s])):
            for a in ons:
                rec=scored[a][s][j]; csvrows[idx][f"mu_base_rate"] = rec["base"]; csvrows[idx][f"p_over35_base_rate"]=nb_over(rec["base"],rmap[a]["base"],3.5); csvrows[idx][f"p_over45_base_rate"]=nb_over(rec["base"],rmap[a]["base"],4.5); csvrows[idx][f"mu_naive"]=rec["naive"]; csvrows[idx][f"p_over35_naive"]=nb_over(rec["naive"],rmap[a]["naive"],3.5); csvrows[idx][f"p_over45_naive"]=nb_over(rec["naive"],rmap[a]["naive"],4.5); break
            idx+=1
    for a in ons:
        p=out["arms"][a]["seasons"]["pooled"]["model"]["3.5"]["ll"]; b=out["arms"][a]["seasons"]["pooled"]["base"]["3.5"]["ll"]; n=out["arms"][a]["seasons"]["pooled"]["naive"]["3.5"]["ll"]; out["arms"][a]["dev_gate_pass"]=p<b and p<n
    (HERE/"results_dev.json").write_text(json.dumps(out,indent=2)+"\n")
    fields=["match_id","season","date","home_team_id","away_team_id","yellows_total","mu_gate_zero","p_over35_gate_zero","p_over45_gate_zero","mu_shrink","p_over35_shrink","p_over45_shrink","mu_base_rate","p_over35_base_rate","p_over45_base_rate","mu_naive","p_over35_naive","p_over45_naive"]
    with open(HERE/"results_dev.csv","w",newline="",encoding="utf-8") as f: w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(csvrows)
    print("cards pooled"); [print(a,out["arms"][a]["r"],out["arms"][a]["seasons"]["pooled"]) for a in ons]; return out
