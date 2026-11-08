"""T-LV adapter; model.py is the literal frozen T-J1 seed mechanics."""
import csv,json,math
from datetime import date
from pathlib import Path
from model import ShotsRegressionStore,NaiveTracker,BaseRateTracker,LevelLayer,TrailingR,nb_over,poisson_over,logloss,BASE_HL,M_BAR
HERE=Path(__file__).resolve().parent; DATA=HERE.parents[1]/"data"/"lv_virsliga_matches.csv"; LINES=(25.5,26.5,27.5); START=date(2025,3,5); CUT=date(2025,5,1); END=date(2025,11,9); LAM_GRID=[3.0,10.0,30.0,100.0,300.0]; CELLS=[(hl,s,k) for hl in (30.,60.,120.) for s in (.5,1.) for k in (20.,50.)]
def load():
    out=[]
    with DATA.open(newline="",encoding="utf-8") as f:
        for r in csv.DictReader(f):
            d=date.fromisoformat(r["date"])
            if r["season"]!="2025" or not(START<=d<=END) or r.get("has_stats_all")!="1" or r["total_shots_home"]=="" or r["total_shots_away"]=="": continue
            out.append({"match_id":r["match_id"],"season":r["season"],"date":r["date"],"day":d.toordinal(),"home_id":int(r["home_team_id"]),"away_id":int(r["away_team_id"]),"home":r["home_team"],"away":r["away_team"],"shots_h":float(r["total_shots_home"]),"shots_a":float(r["total_shots_away"])})
    return sorted(out,key=lambda x:(x["day"],int(x["match_id"])))
def choose(rows):
    warm=[m for m in rows if m["day"]<CUT.toordinal()]; best=None
    for lam in LAM_GRID:
        reg=ShotsRegressionStore(rows,[lam]); vals=[]
        for m in warm:
            h,a=reg.predict(m["home_id"],m["away_id"],m["day"],lam); vals.append(logloss(poisson_over(h+a,26.5),h+a>26.5))
        x=sum(vals)/len(vals); best=min(best,(x,lam),key=lambda z:(z[0],-z[1])) if best else (x,lam)
    lam=best[1]; reg=ShotsRegressionStore(rows,[lam]); res=[]
    for m in warm:
        h,a=reg.predict(m["home_id"],m["away_id"],m["day"],lam); res.append((h+a,m["shots_h"]+m["shots_a"]))
    den=sum((y-mu)**2-mu for mu,y in res); r=max(1.,min(1e6,sum(mu*mu for mu,y in res)/den)) if den>0 else 1e6
    return lam,r
def run_dev():
    rows=load(); warm=[m for m in rows if m["day"]<CUT.toordinal()]; target=[m for m in rows if m["day"]>=CUT.toordinal()]; assert len(warm)==47 and len(target)==133
    lam,r_a=choose(rows); reg=ShotsRegressionStore(rows,[lam]); naive=NaiveTracker(); base=BaseRateTracker(); layer=LevelLayer([CELLS[0]]); trail=TrailingR(r_a); rec=[]
    i=0
    while i<len(rows):
        j=i+1
        while j<len(rows) and rows[j]["date"]==rows[i]["date"]: j+=1
        pending=[]
        for m in rows[i:j]:
            total=m["shots_h"]+m["shots_a"]; lt,la=reg.predict(m["home_id"],m["away_id"],m["day"],lam); rh,ra=reg.league_mu(m["day"],lam); nh,na=naive.predict(m["home_id"],m["away_id"],rh,ra); bh,ba=base.predict(m["day"]); ens=(lt+la+nh+na)/2; f=layer.factor(0,m["day"]); rc=trail.value(m["day"]); pending.append((m,total,ens,f,rc,bh,ba,nh,na))
        for m,total,ens,f,rc,bh,ba,nh,na in pending:
            if m in target: rec.append((m,{"A":(ens,r_a),"B":(ens*f,r_a),"C":(ens,rc),"baseline_league":(bh+ba,None),"baseline_naive":(nh+na,None)}))
        for m,total,ens,f,rc,bh,ba,nh,na in pending:
            naive.update(m["home_id"],m["away_id"],m["shots_h"],m["shots_a"]); base.update(m["day"],m["shots_h"],m["shots_a"]); layer.update(0,m["day"],total,ens); trail.update(m["day"],total)
        i=j
    def metric(a):
        vals=[(m,v[a]) for m,v in rec]; out={"n":len(vals)}
        for L in LINES: out[f"ll_{L}"]=sum(logloss(nb_over(mu,rr,L),m["shots_h"]+m["shots_a"]>L) if rr is not None else logloss(poisson_over(mu,L),m["shots_h"]+m["shots_a"]>L) for m,(mu,rr) in vals)/len(vals)
        out["mean_mu"]=sum(x[0] for _,x in vals)/len(vals); out["actual_mean_total"]=sum(m["shots_h"]+m["shots_a"] for m,_ in vals)/len(vals); out["mean_p_26.5"]=sum((nb_over(x[0],x[1],26.5) if x[1] is not None else poisson_over(x[0],26.5)) for _,x in vals)/len(vals); out["actual_over_26.5"]=sum(m["shots_h"]+m["shots_a"]>26.5 for m,_ in vals)/len(vals); return out
    out={"protocol":{"league":"LV-Virsliga","warmup":"2025-03-05..2025-04-30","window":"2025-05-01..2025-11-09","scored_n":133,"primary_line":26.5,"sign_convention":"actual_minus_predicted"},"arms":{a:metric(a) for a in ("A","B","C")},"baselines":{"league_base_rate":metric("baseline_league"),"naive":metric("baseline_naive")},"fitted_params":{"lambda":lam,"r_A":r_a,"level_cell":list(CELLS[0]),"trailing_r_window":200}}
    (HERE/"results_dev.json").write_text(json.dumps(out,indent=2)+"\n")
    (HERE/"fitted_params.json").write_text(json.dumps(out["fitted_params"],indent=2)+"\n")
    with (HERE/"predictions_dev.csv").open("w",newline="") as f:
        fs=["match_id","date","season","arm","actual_target","predicted_mean"]+["p_over_"+str(x).replace(".","_") for x in LINES]; w=csv.DictWriter(f,fieldnames=fs); w.writeheader()
        for m,v in rec:
            for a in ("A","B","C"):
                mu,rr=v[a]; w.writerow({"match_id":m["match_id"],"date":m["date"],"season":m["season"],"arm":a,"actual_target":m["shots_h"]+m["shots_a"],"predicted_mean":mu,**{"p_over_"+str(L).replace(".","_"):nb_over(mu,rr,L) for L in LINES}})
    print(json.dumps(out,indent=2)); return out
def load_virgin_rows():
    out=[]
    with DATA.open(newline="",encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["season"] not in ("2025","2026") or r.get("has_stats_all")!="1" or r["total_shots_home"]=="" or r["total_shots_away"]=="": continue
            d=date.fromisoformat(r["date"])
            out.append({"match_id":r["match_id"],"season":r["season"],"date":r["date"],"day":d.toordinal(),"home_id":int(r["home_team_id"]),"away_id":int(r["away_team_id"]),"home":r["home_team"],"away":r["away_team"],"shots_h":float(r["total_shots_home"]),"shots_a":float(r["total_shots_away"])})
    return sorted(out,key=lambda x:(x["day"],int(x["match_id"])))

def fit_virgin_params(pre):
    best=None
    for lam in LAM_GRID:
        reg=ShotsRegressionStore(pre,[lam]); vals=[]
        for m in pre:
            h,a=reg.predict(m["home_id"],m["away_id"],m["day"],lam); vals.append(logloss(poisson_over(h+a,26.5),h+a>26.5))
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
    ps=[nb_over(mu,r,26.5) if distribution=="nb" else poisson_over(mu,26.5) for y,mu,r in records]; ys=[int(y>26.5) for y,mu,r in records]; ds=[y-p for y,p in zip(ys,ps)]; d=sum(ds)/n
    out.update({"mean_mu":sum(mu for y,mu,r in records)/n,"actual_mean_total":sum(y for y,mu,r in records)/n,"mean_p_over_26.5":sum(ps)/n,"actual_over_rate_26.5":sum(ys)/n,"calibration":d,"calibration_se":(sum((x-d)**2 for x in ds)/(n-1))**.5/(n**.5)})
    return out

def run_virgin(arms=("A","B","C"), predict_arm=None):
    """Virgin metrics for the requested dev-passing arms only.

    Date-grouped walk over 2025+2026 continuing from the dev end
    state (regression store refits on strictly prior days only;
    naive/base/level/trailing state updates per date group, never
    inside one). Metrics are written by every call; the virgin
    predictions CSV and fitted_params_virgin.json are written ONLY
    when predict_arm names the shipped arm (after the virgin gate
    is judged). Never call with an arm that failed the dev gate.
    Baselines are the dev-consistent trackers (BaseRateTracker /
    NaiveTracker, Poisson), NOT MA's constant-mu shortcut.
    """
    rows=load_virgin_rows(); pre=[m for m in rows if m["season"]=="2025"]; target=[m for m in rows if m["season"]=="2026"]
    assert len(pre)==180 and len(target)==179
    assert all(m["season"]=="2026" for m in target) and not any(m["season"] not in ("2025","2026") for m in rows)
    for a in arms: assert a in ("A","B","C"), a
    lam,r_a=fit_virgin_params(pre); reg=ShotsRegressionStore(rows,[lam]); naive=NaiveTracker(); base=BaseRateTracker(); layer=LevelLayer([CELLS[0]]); trail=TrailingR(r_a); rec=[]
    i=0
    while i<len(rows):
        j=i+1
        while j<len(rows) and rows[j]["date"]==rows[i]["date"]: j+=1
        pending=[]
        for m in rows[i:j]:
            total=m["shots_h"]+m["shots_a"]; lt,la=reg.predict(m["home_id"],m["away_id"],m["day"],lam); rh,ra=reg.league_mu(m["day"],lam); nh,na=naive.predict(m["home_id"],m["away_id"],rh,ra); bh,ba=base.predict(m["day"]); ens=(lt+la+nh+na)/2; f=layer.factor(0,m["day"]); rc=trail.value(m["day"]); pending.append((m,total,ens,f,rc,bh,ba,nh,na))
        for m,total,ens,f,rc,bh,ba,nh,na in pending:
            if m["season"]=="2026": rec.append((m,{"A":(ens,r_a),"B":(ens*f,r_a),"C":(ens,rc),"baseline_league":(bh+ba,None),"baseline_naive":(nh+na,None)}))
        for m,total,ens,f,rc,bh,ba,nh,na in pending:
            naive.update(m["home_id"],m["away_id"],m["shots_h"],m["shots_a"]); base.update(m["day"],m["shots_h"],m["shots_a"]); layer.update(0,m["day"],total,ens); trail.update(m["day"],total)
        i=j
    def vrec(a): return [(m["shots_h"]+m["shots_a"],v[a][0],v[a][1]) for m,v in rec]
    out={"protocol":{"league":"LV-Virsliga","virgin_season":"2026","pre_virgin_rows":len(pre),"scored_n":len(target),"primary_line":26.5,"sign_convention":"actual_minus_predicted","arms_requested":list(arms)},"arms":{a:virgin_metric(vrec(a),"nb") for a in arms},"baselines":{"league_base_rate":virgin_metric(vrec("baseline_league"),"poisson"),"naive":virgin_metric(vrec("baseline_naive"),"poisson")},"fitted_params":{"lambda":lam,"r_A":r_a,"level_cell":list(CELLS[0]),"trailing_r_window":200}}
    if predict_arm:
        assert predict_arm in arms
        fields=["match_id","date","season","arm","actual_target","predicted_mean","predicted_mean_1h","predicted_mean_2h"]+["p_over_"+str(x).replace(".","_") for x in LINES]
        with (HERE/"predictions_virgin.csv").open("w",newline="") as f:
            w=csv.DictWriter(f,fieldnames=fields); w.writeheader()
            for m,v in rec:
                mu,rr=v[predict_arm]; y=m["shots_h"]+m["shots_a"]; w.writerow({"match_id":m["match_id"],"date":m["date"],"season":m["season"],"arm":predict_arm,"actual_target":y,"predicted_mean":mu,"predicted_mean_1h":mu*.4685,"predicted_mean_2h":mu*.5315,**{"p_over_"+str(x).replace(".","_"):nb_over(mu,rr,x) for x in LINES}})
        shipped=HERE.parents[1]/"predictions"/"t_lv_virgin_predictions.csv"; shipped.parent.mkdir(exist_ok=True); shipped.write_text((HERE/"predictions_virgin.csv").read_text())
        (HERE/"fitted_params_virgin.json").write_text(json.dumps({"market":"total_shots","arm":predict_arm,"lambda":lam,"r_A":r_a,"pre_virgin_fit_rows":len(pre),"primary_line":26.5,"ladder":list(LINES)},indent=2)+"\n")
    (HERE/"results_virgin.json").write_text(json.dumps(out,indent=2)+"\n"); print(json.dumps(out,indent=2)); return out

if __name__=="__main__":
    import argparse
    p=argparse.ArgumentParser(); sub=p.add_subparsers(dest="command",required=True)
    sub.add_parser("dev")
    v=sub.add_parser("virgin"); v.add_argument("--arm",required=True,nargs="+",choices=("A","B","C"))
    q=sub.add_parser("virgin-predict"); q.add_argument("--arm",required=True,choices=("A","B","C"))
    a=p.parse_args()
    if a.command=="dev": run_dev()
    elif a.command=="virgin": run_virgin(tuple(a.arm))
    else: run_virgin((a.arm,), predict_arm=a.arm)
