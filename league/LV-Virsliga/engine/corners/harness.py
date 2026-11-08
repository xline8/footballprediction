import argparse,csv,json,math
from datetime import date
from pathlib import Path
from core import FeatureBuilder,attach_naive,load,fit_params,model_prediction,over_prob
HERE=Path(__file__).resolve().parent; DATA=HERE.parents[1]/"data"/"lv_virsliga_matches.csv"; LINES=(8.5,9.5,10.5); PRIMARY=9.5
def metric(vals,kind="model"):
 def p(r,mu,rr,L): return over_prob(mu,rr,L)
 return {"n":len(vals),**{f"ll_{L}":sum(-(int(r["y"]>L)*math.log(max(p(r,mu,rr,L),1e-12))+(1-int(r["y"]>L))*math.log(max(1-p(r,mu,rr,L),1e-12))) for r,mu,rr in vals)/len(vals) for L in LINES},"mean_mu":sum(mu for r,mu,rr in vals)/len(vals),"actual_mean_total":sum(r["y"] for r,mu,rr in vals)/len(vals),"mean_p_9.5":sum(p(r,mu,rr,PRIMARY) for r,mu,rr in vals)/len(vals),"actual_over_9.5":sum(r["y"]>PRIMARY for r,mu,rr in vals)/len(vals)}
def run_dev():
 rows=attach_naive(FeatureBuilder(load(DATA,{"2025"})).build()); warm=[r for r in rows if r["date"]<date(2025,5,1)]; target=[r for r in rows if date(2025,5,1)<=r["date"]<=date(2025,11,9)]; assert len(warm)==47 and len(target)==133 and all(r["season"]!="2026" for r in rows)
 params=fit_params(warm,"gate_zero"); vals=[]; base=sum(r["y"] for r in warm)/len(warm); br=max(1.02,min(5.0,sum((r["y"]-base)**2 for r in warm)/max(sum(base for _ in warm),1e-12)))
 for r in target:
  mu,rr=model_prediction(r,params,"gate_zero"); vals.append((r,mu,rr))
 out={"protocol":{"league":"LV-Virsliga","warmup":"2025-03-05..2025-04-30","window":"2025-05-01..2025-11-09","scored_n":133,"primary_line":PRIMARY,"sign_convention":"actual_minus_predicted","beta_grid":[-.01,-.0075,-.005,-.0025,0,.0025,.005,.0075,.01]},"arms":{"gate_zero":metric(vals)},"baselines":{"league_base_rate":metric([(r,base,br) for r,_,_ in vals]),"naive":metric([(r,(r["naive_home"]+r["naive_away"])/2,r["season_r_base"]) for r,_,_ in vals])},"fitted_params":params}; (HERE/"results_dev.json").write_text(json.dumps(out,indent=2)+"\n"); (HERE/"fitted_params.json").write_text(json.dumps(params,indent=2)+"\n")
 with (HERE/"predictions_dev.csv").open("w",newline="") as f:
  fs=["match_id","date","season","arm","actual_target","predicted_mean"]+[f"p_over_{str(L).replace('.','_')}" for L in LINES]; w=csv.DictWriter(f,fieldnames=fs); w.writeheader()
  for r,mu,rr in vals:w.writerow({"match_id":r["match_id"],"date":r["date"].isoformat(),"season":r["season"],"arm":"gate_zero","actual_target":r["y"],"predicted_mean":mu,**{f"p_over_{str(L).replace('.','_')}":over_prob(mu,rr,L) for L in LINES}})
 print(json.dumps(out,indent=2)); return out
def _virgin_metric(vals):
 ps=[over_prob(mu,rr,PRIMARY) for r,mu,rr in vals]; ys=[int(r["y"]>PRIMARY) for r,mu,rr in vals]; res=[y-p for y,p in zip(ys,ps)]; mean=sum(res)/len(res)
 return {"n":len(vals),**{f"ll_{L}":sum(-(int(r["y"]>L)*math.log(max(over_prob(mu,rr,L),1e-12))+(1-int(r["y"]>L))*math.log(max(1-over_prob(mu,rr,L),1e-12))) for r,mu,rr in vals)/len(vals) for L in LINES},"mean_mu":sum(mu for r,mu,rr in vals)/len(vals),"actual_mean_total":sum(r["y"] for r,mu,rr in vals)/len(vals),"mean_p_9.5":sum(ps)/len(ps),"actual_over_9.5":sum(ys)/len(ys),"calibration":mean,"calibration_se":(sum((x-mean)**2 for x in res)/(len(res)-1))**.5/(len(res)**.5)}
def run_virgin(predict_arm=None):
 """Virgin metrics for Gate Zero (dev-passing arms only).

 UNTESTED — C-LV failed its dev gate, so this function must NOT be
 run. It is completed here (ported from MA's complete virgin, LV
 values) so the engine is not left with a metrics stub. Metrics are
 written by every call; predictions + fitted_params_virgin.json only
 when predict_arm names the shipped arm (after the virgin gate).
 """
 rows=attach_naive(FeatureBuilder(load(DATA,{"2025","2026"})).build()); target=[r for r in rows if r["season"]=="2026"]; assert len(target)==179; pre=[r for r in rows if r["season"]=="2025"]; assert len(pre)==180
 params=fit_params(pre,"gate_zero"); vals=[(r,*model_prediction(r,params,"gate_zero")) for r in target]
 base=sum(r["y"] for r in pre)/len(pre); br=max(1.02,min(5.0,sum((r["y"]-base)**2 for r in pre)/max(sum(base for _ in pre),1e-12)))
 out={"protocol":{"league":"LV-Virsliga","virgin_season":"2026","pre_virgin_rows":len(pre),"scored_n":179,"primary_line":PRIMARY,"sign_convention":"actual_minus_predicted"},"arms":{"gate_zero":_virgin_metric(vals)},"baselines":{"league_base_rate":_virgin_metric([(r,base,br) for r,_,_ in vals]),"naive":_virgin_metric([(r,(r["naive_home"]+r["naive_away"])/2,r["season_r_base"]) for r,_,_ in vals])},"fitted_params":params}
 if predict_arm=="gate_zero":
  (HERE/"predictions").mkdir(exist_ok=True)
  with (HERE/"predictions"/"c_lv_virgin_predictions.csv").open("w",newline="") as f:
   fs=["match_id","date","season","arm","actual_target","predicted_mean","predicted_mean_1h","predicted_mean_2h"]+[f"p_over_{str(L).replace('.','_')}" for L in LINES]; w=csv.DictWriter(f,fieldnames=fs); w.writeheader()
   for r,mu,rr in vals:w.writerow({"match_id":r["match_id"],"date":r["date"].isoformat(),"season":r["season"],"arm":"gate_zero","actual_target":r["y"],"predicted_mean":mu,"predicted_mean_1h":mu*.4816,"predicted_mean_2h":mu*.5184,**{f"p_over_{str(L).replace('.','_')}":over_prob(mu,rr,L) for L in LINES}})
  (HERE/"fitted_params_virgin.json").write_text(json.dumps({**params,"market":"corners","arm":"gate_zero","pre_virgin_fit_rows":len(pre),"league_base_mu":base,"league_base_r":br},indent=2)+"\n")
 (HERE/"results_virgin.json").write_text(json.dumps(out,indent=2)+"\n"); print(json.dumps(out,indent=2)); return out
if __name__=="__main__":
 p=argparse.ArgumentParser(); sub=p.add_subparsers(dest="command",required=True)
 sub.add_parser("dev")
 sub.add_parser("virgin")
 q=sub.add_parser("virgin-predict"); q.add_argument("--arm",required=True,choices=("gate_zero",))
 a=p.parse_args()
 if a.command=="dev": run_dev()
 elif a.command=="virgin": run_virgin()
 else: run_virgin(predict_arm=a.arm)
