"""T-MA adapter; model.py is the literal T-RU seed mechanics."""
import csv,json,math
from datetime import date
from pathlib import Path
from model import ShotsRegressionStore,NaiveTracker,BaseRateTracker,LevelLayer,TrailingR,nb_over,poisson_over,logloss,BASE_HL,M_BAR
HERE=Path(__file__).resolve().parent; DATA=HERE.parents[1]/"data"/"ma_botola_matches.csv"; LINES=(15.5,16.5,17.5); START=date(2024,11,1); CUT=date(2025,1,1); END=date(2025,5,12); LAM_GRID=[3.0,10.0,30.0,100.0,300.0]; CELLS=[(hl,s,k) for hl in (30.,60.,120.) for s in (.5,1.) for k in (20.,50.)]
def load():
    out=[]
    with DATA.open(newline="",encoding="utf-8") as f:
        for r in csv.DictReader(f):
            d=date.fromisoformat(r["date"])
            if r["season"]!="2024/2025" or not(START<=d<=END) or r.get("has_stats_all")!="1" or r["total_shots_home"]=="" or r["total_shots_away"]=="": continue
            out.append({"match_id":r["match_id"],"season":r["season"],"date":r["date"],"day":d.toordinal(),"home_id":int(r["home_team_id"]),"away_id":int(r["away_team_id"]),"home":r["home_team"],"away":r["away_team"],"shots_h":float(r["total_shots_home"]),"shots_a":float(r["total_shots_away"])})
    return sorted(out,key=lambda x:(x["day"],int(x["match_id"])))
def choose(rows):
    warm=[m for m in rows if m["day"]<CUT.toordinal()]; best=None
    for lam in LAM_GRID:
        reg=ShotsRegressionStore(rows,[lam]); vals=[]
        for m in warm:
            h,a=reg.predict(m["home_id"],m["away_id"],m["day"],lam); vals.append(logloss(poisson_over(h+a,16.5),h+a>16.5))
        x=sum(vals)/len(vals); best=min(best,(x,lam),key=lambda z:(z[0],-z[1])) if best else (x,lam)
    lam=best[1]; reg=ShotsRegressionStore(rows,[lam]); res=[]
    for m in warm:
        h,a=reg.predict(m["home_id"],m["away_id"],m["day"],lam); res.append((h+a,m["shots_h"]+m["shots_a"]))
    den=sum((y-mu)**2-mu for mu,y in res); r=max(1.,min(1e6,sum(mu*mu for mu,y in res)/den)) if den>0 else 1e6
    return lam,r
def run_dev():
    rows=load(); warm=[m for m in rows if m["day"]<CUT.toordinal()]; target=[m for m in rows if m["day"]>=CUT.toordinal()]; assert len(warm)==55 and len(target)==109
    lam,r_a=choose(rows); reg=ShotsRegressionStore(rows,[lam]); naive=NaiveTracker(); base=BaseRateTracker(); layer=LevelLayer([CELLS[0]]); trail=TrailingR(r_a); rec=[]
    for m in rows:
        total=m["shots_h"]+m["shots_a"]; lt,la=reg.predict(m["home_id"],m["away_id"],m["day"],lam); rh,ra=reg.league_mu(m["day"],lam); nh,na=naive.predict(m["home_id"],m["away_id"],rh,ra); bh,ba=base.predict(m["day"]); ens=(lt+la+nh+na)/2; f=layer.factor(0,m["day"]); rc=trail.value(m["day"])
        if m in target: rec.append((m,{"A":(ens,r_a),"B":(ens*f,r_a),"C":(ens,rc),"baseline_league":(bh+ba,None),"baseline_naive":(nh+na,None)}))
        naive.update(m["home_id"],m["away_id"],m["shots_h"],m["shots_a"]); base.update(m["day"],m["shots_h"],m["shots_a"]); layer.update(0,m["day"],total,ens); trail.update(m["day"],total)
    def metric(a):
        vals=[(m,v[a]) for m,v in rec]; out={"n":len(vals)}
        for L in LINES: out[f"ll_{L}"]=sum(logloss(nb_over(mu,rr,L),m["shots_h"]+m["shots_a"]>L) if rr is not None else logloss(poisson_over(mu,L),m["shots_h"]+m["shots_a"]>L) for m,(mu,rr) in vals)/len(vals)
        out["mean_mu"]=sum(x[0] for _,x in vals)/len(vals); out["actual_mean_total"]=sum(m["shots_h"]+m["shots_a"] for m,_ in vals)/len(vals); out["mean_p_16.5"]=sum((nb_over(x[0],x[1],16.5) if x[1] is not None else poisson_over(x[0],16.5)) for _,x in vals)/len(vals); out["actual_over_16.5"]=sum(m["shots_h"]+m["shots_a"]>16.5 for m,_ in vals)/len(vals); return out
    out={"protocol":{"league":"MA-BotolaPro","warmup":"2024-11-01..2024-12-31","window":"2025-01-01..2025-05-12","scored_n":109,"primary_line":16.5,"sign_convention":"actual_minus_predicted"},"arms":{a:metric(a) for a in ("A","B","C")},"baselines":{"league_base_rate":metric("baseline_league"),"naive":metric("baseline_naive")},"fitted_params":{"lambda":lam,"r_A":r_a,"level_cell":list(CELLS[0]),"trailing_r_window":200}}
    (HERE/"results_dev.json").write_text(json.dumps(out,indent=2)+"\n")
    with (HERE/"predictions_dev.csv").open("w",newline="") as f:
        fs=["match_id","date","season","arm","actual_target","predicted_mean","p_over_15_5","p_over_16_5","p_over_17_5"]; w=csv.DictWriter(f,fieldnames=fs); w.writeheader()
        for m,v in rec:
            for a in ("A","B","C"):
                mu,rr=v[a]; w.writerow({"match_id":m["match_id"],"date":m["date"],"season":m["season"],"arm":a,"actual_target":m["shots_h"]+m["shots_a"],"predicted_mean":mu,**{"p_over_"+str(L).replace(".","_"):nb_over(mu,rr,L) for L in LINES}})
    print(json.dumps(out,indent=2)); return out
def load_virgin_rows():
    out=[]
    with DATA.open(newline="",encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["season"] not in ("2024/2025","2025/2026") or r.get("has_stats_all")!="1" or r["total_shots_home"]=="" or r["total_shots_away"]=="": continue
            d=date.fromisoformat(r["date"])
            out.append({"match_id":r["match_id"],"season":r["season"],"date":r["date"],"day":d.toordinal(),"home_id":int(r["home_team_id"]),"away_id":int(r["away_team_id"]),"home":r["home_team"],"away":r["away_team"],"shots_h":float(r["total_shots_home"]),"shots_a":float(r["total_shots_away"])})
    return sorted(out,key=lambda x:(x["day"],int(x["match_id"])))

def fit_virgin_params(pre):
    best=None
    for lam in LAM_GRID:
        reg=ShotsRegressionStore(pre,[lam]); vals=[]
        for m in pre:
            h,a=reg.predict(m["home_id"],m["away_id"],m["day"],lam); vals.append(logloss(poisson_over(h+a,16.5),h+a>16.5))
        cand=(sum(vals)/len(vals),-lam,lam); best=cand if best is None or cand<best else best
    lam=best[2]; reg=ShotsRegressionStore(pre,[lam]); res=[]
    for m in pre:
        h,a=reg.predict(m["home_id"],m["away_id"],m["day"],lam); res.append((h+a,m["shots_h"]+m["shots_a"]))
    den=sum((y-mu)**2-mu for mu,y in res); r=max(1.,min(1e6,sum(mu*mu for mu,y in res)/den)) if den>0 else 1e6
    return lam,r

def virgin_metric(records, distribution):
    n=len(records); out={"n":n}
    for line in LINES:
        out[f"ll_{line}"]=sum(logloss((nb_over(mu,r,line) if distribution=="nb" else poisson_over(mu,line)),y>line) for y,mu,r in records)/n
    ps=[nb_over(mu,r,16.5) if distribution=="nb" else poisson_over(mu,16.5) for y,mu,r in records]; ys=[int(y>16.5) for y,mu,r in records]; ds=[y-p for y,p in zip(ys,ps)]; d=sum(ds)/n
    out.update({"mean_mu":sum(mu for y,mu,r in records)/n,"actual_mean_total":sum(y for y,mu,r in records)/n,"mean_p_over_16.5":sum(ps)/n,"actual_over_rate_16.5":sum(ys)/n,"calibration":d,"calibration_se":(sum((x-d)**2 for x in ds)/n)**0.5/(n**0.5)})
    return out

def run_virgin():
    rows=load_virgin_rows(); pre=[m for m in rows if m["season"]=="2024/2025"]; target=[m for m in rows if m["season"]=="2025/2026"]
    assert len(pre)==172 and len(target)==226
    assert all(m["season"]=="2025/2026" for m in target) and not any(m["season"]=="2026/2027" for m in rows)
    lam,r_a=fit_virgin_params(pre); reg=ShotsRegressionStore(rows,[lam]); naive=NaiveTracker(); base_mu=sum(m["shots_h"]+m["shots_a"] for m in pre)/len(pre); rec=[]
    for m in rows:
        h,a=reg.predict(m["home_id"],m["away_id"],m["day"],lam); rh,ra=reg.league_mu(m["day"],lam); nh,na=naive.predict(m["home_id"],m["away_id"],rh,ra)
        if m["season"]=="2025/2026": rec.append((m,(h+a+nh+na)/2,nh+na,m["shots_h"]+m["shots_a"]))
        naive.update(m["home_id"],m["away_id"],m["shots_h"],m["shots_a"])
    arm=[(y,mu,r_a) for m,mu,nmu,y in rec]; base=[(y,base_mu,None) for m,mu,nmu,y in rec]; nrec=[(y,nmu,None) for m,mu,nmu,y in rec]
    out={"protocol":{"league":"MA-BotolaPro","virgin_season":"2025/2026","pre_virgin_rows":len(pre),"scored_n":len(target),"primary_line":16.5,"sign_convention":"actual_minus_predicted"},"arms":{"A":virgin_metric(arm,"nb")},"baselines":{"league_base_rate":virgin_metric(base,"poisson"),"naive":virgin_metric(nrec,"poisson")},"fitted_params":{"lambda":lam,"r_A":r_a}}
    fields=["match_id","date","season","arm","actual_target","predicted_mean"]+["p_over_"+str(x).replace(".","_") for x in LINES]
    with (HERE/"predictions_virgin.csv").open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader()
        for m,mu,nmu,y in rec: w.writerow({"match_id":m["match_id"],"date":m["date"],"season":m["season"],"arm":"A","actual_target":y,"predicted_mean":mu,**{"p_over_"+str(x).replace(".","_"):nb_over(mu,r_a,x) for x in LINES}})
    shipped=HERE.parents[1]/"predictions"/"t_ma_virgin_predictions.csv"; shipped.parent.mkdir(exist_ok=True); shipped.write_text((HERE/"predictions_virgin.csv").read_text())
    (HERE/"fitted_params_virgin.json").write_text(json.dumps({"market":"total_shots","arm":"A","lambda":lam,"r_A":r_a,"pre_virgin_fit_rows":len(pre),"league_base_mu":base_mu,"primary_line":16.5,"ladder":list(LINES)},indent=2)+"\n")
    (HERE/"results_virgin.json").write_text(json.dumps(out,indent=2)+"\n"); print(json.dumps(out,indent=2)); return out

if __name__=="__main__":
    import sys
    (run_virgin if len(sys.argv)>1 and sys.argv[1]=="virgin" else run_dev)()
