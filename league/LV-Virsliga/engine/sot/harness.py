import argparse, csv, json, math
from datetime import date
from pathlib import Path
from model import Engine, load_matches, NB_R, nb_over
HERE=Path(__file__).resolve().parent; DATA=HERE.parents[1]/"data"/"lv_virsliga_matches.csv"
WARM_START,DEV_START,DEV_END=date(2025,3,5),date(2025,5,1),date(2025,11,9); ARMS=("GZ","RS"); LINES=(8.5,9.5,10.5); PRIMARY=9.5
def load(seasons): return [m for m in load_matches(DATA,seasons) if WARM_START<=m["date"]<=(DEV_END if seasons=={"2025"} else date(2026,12,31))]
def actual(m,L=PRIMARY): return int(m["sot_h"]+m["sot_a"]>L)
def ll(p,y): p=max(min(p,1-1e-12),1e-12); return -(y*math.log(p)+(1-y)*math.log(1-p))
def walk(ms,arm,start):
 e=Engine(ms,arm); out=[]; i=0
 while i<len(ms):
  j=i+1
  while j<len(ms) and ms[j]["date"]==ms[i]["date"]: j+=1
  ps=[(m,e.predict(m)) for m in ms[i:j]]
  if ms[i]["date"]>=start: out.extend(ps)
  for m,p in ps: e.update(m)
  i=j
 return out
def metric(ps,fn): return {"n":len(ps),**{f"ll_{L}":sum(ll(fn(m,p,L),actual(m,L)) for m,p in ps)/len(ps) for L in LINES},"mean_mu":sum(p["exp_h"]+p["exp_a"] for m,p in ps)/len(ps),"actual_mean_total":sum(m["sot_h"]+m["sot_a"] for m,p in ps)/len(ps),"mean_p_9.5":sum(fn(m,p,PRIMARY) for m,p in ps)/len(ps),"actual_over_9.5":sum(actual(m) for m,p in ps)/len(ps)}
def run_dev():
 ms=load({"2025"}); warm=[m for m in ms if m["date"]<DEV_START]; assert len(warm)==47 and sum(m["date"]>=DEV_START for m in ms)==133 and all(m["season"]!="2026" for m in ms)
 results={a:walk(ms,a,DEV_START) for a in ARMS}; base=sum(m["sot_h"]+m["sot_a"] for m in warm)/len(warm)
 arms={a:metric(v,lambda m,p,L:p["probs"][L]) for a,v in results.items()}; baselines={"league_base_rate":metric(results["GZ"],lambda m,p,L:nb_over(base,NB_R,L)),"naive":metric(results["GZ"],lambda m,p,L:p["naive_probs"][L])}
 out={"protocol":{"league":"LV-Virsliga","warmup":"2025-03-05..2025-04-30","window":"2025-05-01..2025-11-09","scored_n":133,"primary_line":PRIMARY,"sign_convention":"actual_minus_predicted"},"arms":arms,"baselines":baselines}; (HERE/"results_dev.json").write_text(json.dumps(out,indent=2)+"\n")
 with (HERE/"predictions_dev.csv").open("w",newline="") as f:
  fs=["match_id","date","season","arm","actual_target","predicted_mean"]+[f"p_over_{str(L).replace('.','_')}" for L in LINES]; w=csv.DictWriter(f,fieldnames=fs); w.writeheader()
  for a,ps in results.items():
   for m,p in ps: w.writerow({"match_id":m["match_id"],"date":m["date"].isoformat(),"season":m["season"],"arm":a,"actual_target":m["sot_h"]+m["sot_a"],"predicted_mean":p["exp_h"]+p["exp_a"],**{f"p_over_{str(L).replace('.','_')}":p["probs"][L] for L in LINES}})
 (HERE/"fitted_params.json").write_text(json.dumps({"market":"sot","primary_line":PRIMARY,"ladder":LINES},indent=2)+"\n"); print(json.dumps(out,indent=2)); return out
def run_virgin(arms=("GZ",), predict_arm=None):
 """Virgin metrics for the requested dev-passing arms only (default GZ).

 Metrics are written by every call; the virgin predictions CSV and
 fitted_params_virgin.json are written ONLY when predict_arm names the
 shipped arm (after the virgin gate is judged). Never call with an arm
 that failed the dev gate.
 """
 ms=load({"2025","2026"}); target=[m for m in ms if m["season"]=="2026"]; assert len(target)==179 and sum(m["season"]=="2025" for m in ms)==180
 pre=[m for m in ms if m["season"]=="2025"]; base_mu=sum(m["sot_h"]+m["sot_a"] for m in pre)/len(pre)
 outarms={}
 for a in arms:
  assert a in ARMS, a
  ps=[x for x in walk(ms,a,date(2026,1,1)) if x[0]["season"]=="2026"]; p=[q["probs"][PRIMARY] for m,q in ps]; y=[actual(m) for m,q in ps]; d=[x-z for x,z in zip(y,p)]; mean=sum(d)/len(d)
  outarms[a]={"n":len(ps),"ll_9.5":sum(ll(x,z) for x,z in zip(p,y))/len(p),"mean_p_over_9.5":sum(p)/len(p),"actual_over_rate_9.5":sum(y)/len(y),"calibration":mean,"calibration_se":(sum((x-mean)**2 for x in d)/(len(d)-1))**.5/(len(d)**.5)}
  if a==arms[0]:
   # virgin baselines (same constructions as dev): league base rate =
   # NB(pre-virgin 2025 mean, NB_R); naive = trailing-10 continuing
   # from the dev end state through the virgin.
   pb=[nb_over(base_mu,NB_R,PRIMARY) for m,q in ps]; pn=[q["naive_probs"][PRIMARY] for m,q in ps]
   def _bll(pp):
    dd=[x-z for x,z in zip(y,pp)]; mm=sum(dd)/len(dd)
    return {"n":len(ps),"ll_9.5":sum(ll(x,z) for x,z in zip(pp,y))/len(pp),"mean_p_over_9.5":sum(pp)/len(pp),"actual_over_rate_9.5":sum(y)/len(y),"calibration":mm,"calibration_se":(sum((x-mm)**2 for x in dd)/(len(dd)-1))**.5/(len(dd)**.5)}
   baselines={"league_base_rate":_bll(pb),"naive":_bll(pn)}
  if predict_arm==a:
   (HERE.parents[1]/"predictions").mkdir(exist_ok=True); f=(HERE.parents[1]/"predictions"/"s_lv_virgin_predictions.csv").open("w",newline=""); w=csv.DictWriter(f,fieldnames=["match_id","date","season","arm","actual_target","predicted_mean","predicted_mean_1h","predicted_mean_2h"]+[f"p_over_{str(L).replace('.','_')}" for L in LINES]); w.writeheader()
   for m,q in ps: w.writerow({"match_id":m["match_id"],"date":m["date"].isoformat(),"season":m["season"],"arm":a,"actual_target":m["sot_h"]+m["sot_a"],"predicted_mean":q["exp_h"]+q["exp_a"],"predicted_mean_1h":(q["exp_h"]+q["exp_a"])*.4637,"predicted_mean_2h":(q["exp_h"]+q["exp_a"])*.5363,**{f"p_over_{str(L).replace('.','_')}":q["probs"][L] for L in LINES}})
   f.close()
   (HERE/"fitted_params_virgin.json").write_text(json.dumps({"market":"sot","primary_line":PRIMARY,"arm":a},indent=2)+"\n")
 out={"protocol":{"league":"LV-Virsliga","virgin_season":"2026","scored_n":179,"primary_line":PRIMARY,"sign_convention":"actual_minus_predicted","arms_requested":list(arms)},"arms":outarms,"baselines":baselines}; (HERE/"results_virgin.json").write_text(json.dumps(out,indent=2)+"\n"); print(json.dumps(out,indent=2)); return out
if __name__=="__main__":
 p=argparse.ArgumentParser(); sub=p.add_subparsers(dest="command",required=True)
 sub.add_parser("dev")
 v=sub.add_parser("virgin"); v.add_argument("--arm",required=True,nargs="+",choices=ARMS)
 q=sub.add_parser("virgin-predict"); q.add_argument("--arm",required=True,choices=ARMS)
 a=p.parse_args()
 if a.command=="dev": run_dev()
 elif a.command=="virgin": run_virgin(tuple(a.arm))
 else: run_virgin((a.arm,), predict_arm=a.arm)
