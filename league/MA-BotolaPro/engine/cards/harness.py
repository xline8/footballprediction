import csv,json,math
from datetime import date
from pathlib import Path
from model import Online,estimate_r,nb_over
HERE=Path(__file__).resolve().parent; DATA=HERE.parents[1]/"data"/"ma_botola_matches.csv"; LINES=(3.5,4.5,5.5)
def load():
    out=[]
    with DATA.open(newline="",encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["season"]!="2024/2025" or not(date(2024,11,1)<=date.fromisoformat(r["date"])<=date(2025,5,12)): continue
            y,h=int(float(r["yellow_home"])),int(float(r["yellow_away"])); key=(r["date"]+"T00:00:00Z",r["match_id"])
            out.append({"match_id":r["match_id"],"season":r["season"],"date":r["date"],"kickoff_utc":key[0],"key":key,"day":date.fromisoformat(r["date"]).toordinal(),"home_id":int(r["home_team_id"]),"away_id":int(r["away_team_id"]),"home":r["home_team"],"away":r["away_team"],"yh":h,"ya":y,"y":h+y,"referee":""})
    return sorted(out,key=lambda x:x["key"])
def ll(p,y): p=max(min(p,1-1e-12),1e-12); return -(y*math.log(p)+(1-y)*math.log(1-p))
def dev():
    rows=load(); warm=[r for r in rows if r["date"]<"2025-01-01"]; scored=[]; o=Online()
    for r in rows:
        p=o.prediction(r,"gate_zero");
        if r["date"]>="2025-01-01": scored.append((r,p))
        o.update(r)
    assert len(warm)==64 and len(scored)==112
    rm={k:estimate_r([{**p,"y":r["y"]} for r,p in [(x[0],x[1]) for x in scored]],k) for k in ("model","base","naive")}
    # Fixed estimate_r is the seed harness construction; estimate from warm-up predictions.
    o=Online(); wr=[]
    for r in rows:
        p=o.prediction(r,"gate_zero");
        if r["date"]<"2025-01-01": wr.append({**p,"y":r["y"]})
        o.update(r)
    rm={k:estimate_r(wr,k) for k in ("model","base","naive")}
    base_mu=sum(r["y"] for r in warm)/len(warm)
    def met(kind):
        vals=[(p["model" if kind=="model" else kind],r) for r,p in scored]; rr=rm["model" if kind=="model" else kind]
        return {"n":len(vals),**{f"ll_{L}":sum(ll(nb_over(mu,rr,L),r["y"]>L) for mu,r in vals)/len(vals) for L in LINES},"mean_mu":sum(mu for mu,_ in vals)/len(vals),"actual_mean_total":sum(r["y"] for _,r in vals)/len(vals),"mean_p_4.5":sum(nb_over(mu,rr,4.5) for mu,_ in vals)/len(vals),"actual_over_4.5":sum(r["y"]>4.5 for _,r in vals)/len(vals)}
    out={"protocol":{"league":"MA-BotolaPro","warmup":"2024-11-01..2024-12-31","window":"2025-01-01..2025-05-12","scored_n":112,"primary_line":4.5,"sign_convention":"actual_minus_predicted"},"arms":{"gate_zero":met("model")},"baselines":{"league_base_rate":met("base"),"naive":met("naive")}}
    (HERE/"results_dev.json").write_text(json.dumps(out,indent=2)+"\n")
    with (HERE/"predictions_dev.csv").open("w",newline="") as f:
        fs=["match_id","date","season","arm","actual_target","predicted_mean","p_over_3_5","p_over_4_5","p_over_5_5"]; w=csv.DictWriter(f,fieldnames=fs); w.writeheader()
        for r,p in scored:
            w.writerow({"match_id":r["match_id"],"date":r["date"],"season":r["season"],"arm":"gate_zero","actual_target":r["y"],"predicted_mean":p["model"],**{"p_over_"+str(L).replace(".","_"):nb_over(p["model"],rm["model"],L) for L in LINES}})
    print(json.dumps(out,indent=2)); return out
