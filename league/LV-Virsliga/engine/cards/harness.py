import argparse,csv,json,math
from datetime import date
from pathlib import Path
from model import Online,estimate_r,nb_over
HERE=Path(__file__).resolve().parent; DATA=HERE.parents[1]/"data"/"lv_virsliga_matches.csv"; LINES=(3.5,4.5,5.5); PRIMARY=4.5
def load(seasons):
 out=[]
 with DATA.open(newline="",encoding="utf-8") as f:
  for r in csv.DictReader(f):
   if r["season"] not in seasons or not r["yellow_home"] or not r["yellow_away"]: continue
   d=date.fromisoformat(r["date"]); out.append({"match_id":r["match_id"],"season":r["season"],"date":r["date"],"kickoff_utc":r["date"]+"T00:00:00Z","key":(r["date"],r["match_id"]),"day":d.toordinal(),"home_id":int(r["home_team_id"]),"away_id":int(r["away_team_id"]),"home":r["home_team"],"away":r["away_team"],"yh":int(float(r["yellow_home"])),"ya":int(float(r["yellow_away"])),"y":int(float(r["yellow_home"]))+int(float(r["yellow_away"])),"referee":""})
 return sorted(out,key=lambda x:x["key"])
def ll(p,y): p=max(min(p,1-1e-12),1e-12); return -(y*math.log(p)+(1-y)*math.log(1-p))
def walk(rows,start):
 o=Online(); out=[]; i=0
 while i<len(rows):
  j=i+1
  while j<len(rows) and rows[j]["date"]==rows[i]["date"]: j+=1
  ps=[(r,o.prediction(r,"gate_zero")) for r in rows[i:j]]
  if rows[i]["date"]>=start: out.extend(ps)
  for r,p in ps:o.update(r)
  i=j
 return out
def metric(vals,kind,rs):
 return {"n":len(vals),**{f"ll_{L}":sum(ll(nb_over(p[kind],rs,L),r["y"]>L) for r,p in vals)/len(vals) for L in LINES},"mean_mu":sum(p[kind] for r,p in vals)/len(vals),"actual_mean_total":sum(r["y"] for r,p in vals)/len(vals),"mean_p_4.5":sum(nb_over(p[kind],rs,PRIMARY) for r,p in vals)/len(vals),"actual_over_4.5":sum(r["y"]>PRIMARY for r,p in vals)/len(vals)}
def run_dev():
 rows=load({"2025"}); warm=[r for r in rows if r["date"]<"2025-05-01"]; scored=walk(rows,"2025-05-01"); assert len(warm)==47 and len(scored)==133 and all(r["season"]!="2026" for r in rows)
 o=Online(); wr=[]
 for r in rows:
  p=o.prediction(r,"gate_zero");
  if r["date"]<"2025-05-01": wr.append({**p,"y":r["y"]})
  o.update(r)
 rs=estimate_r(wr,"model"); base=sum(r["y"] for r in warm)/len(warm); vals=[(r,{**p,"base":base,"league":base}) for r,p in scored]; out={"protocol":{"league":"LV-Virsliga","warmup":"2025-03-05..2025-04-30","window":"2025-05-01..2025-11-09","scored_n":133,"primary_line":PRIMARY,"sign_convention":"actual_minus_predicted"},"arms":{"gate_zero":metric(vals,"model",rs)},"baselines":{"league_base_rate":metric(vals,"league",rs),"naive":metric(vals,"naive",rs)}}; (HERE/"results_dev.json").write_text(json.dumps(out,indent=2)+"\n")
 with (HERE/"predictions_dev.csv").open("w",newline="") as f:
  fs=["match_id","date","season","arm","actual_target","predicted_mean"]+[f"p_over_{str(L).replace('.','_')}" for L in LINES]; w=csv.DictWriter(f,fieldnames=fs); w.writeheader()
  for r,p in scored:w.writerow({"match_id":r["match_id"],"date":r["date"],"season":r["season"],"arm":"gate_zero","actual_target":r["y"],"predicted_mean":p["model"],**{f"p_over_{str(L).replace('.','_')}":nb_over(p["model"],rs,L) for L in LINES}})
 (HERE/"fitted_params.json").write_text(json.dumps({"market":"cards","target":"yellow_home + yellow_away","primary_line":PRIMARY},indent=2)+"\n"); print(json.dumps(out,indent=2)); return out
def _virgin_metric(vals,kind,rs):
 ps=[nb_over(p[kind],rs,PRIMARY) for r,p in vals]; ys=[int(r["y"]>PRIMARY) for r,p in vals]; res=[y-p for y,p in zip(ys,ps)]; mean=sum(res)/len(res)
 return {"n":len(vals),**{f"ll_{L}":sum(ll(nb_over(p[kind],rs,L),r["y"]>L) for r,p in vals)/len(vals) for L in LINES},"mean_mu":sum(p[kind] for r,p in vals)/len(vals),"actual_mean_total":sum(r["y"] for r,p in vals)/len(vals),"mean_p_4.5":sum(ps)/len(ps),"actual_over_4.5":sum(ys)/len(ys),"calibration":mean,"calibration_se":(sum((x-mean)**2 for x in res)/(len(res)-1))**.5/(len(res)**.5)}
def run_virgin(predict_arm=None):
 """Virgin metrics for Gate Zero (dev-passing arms only).

 UNTESTED — K-LV failed its dev gate, so this function must NOT be
 run. It is completed here (mirror of the tested dev construction:
 same walk, same estimate_r, same model-r baselines) so the engine
 is not left with a metrics stub. Metrics are written by every
 call; predictions + fitted_params_virgin.json only when
 predict_arm names the shipped arm (after the virgin gate).
 """
 rows=load({"2025","2026"}); assert len([r for r in rows if r["season"]=="2026"])==179
 o=Online(); wr=[]
 for r in rows:
  p=o.prediction(r,"gate_zero")
  if r["season"]=="2025": wr.append({**p,"y":r["y"]})
  o.update(r)
 rs=estimate_r(wr,"model"); base=sum(r["y"] for r in rows if r["season"]=="2025")/180
 ps=[x for x in walk(rows,"2026-01-01") if x[0]["season"]=="2026"]; vals=[(r,{**p,"base":base,"league":base}) for r,p in ps]
 out={"protocol":{"league":"LV-Virsliga","virgin_season":"2026","scored_n":179,"primary_line":PRIMARY,"sign_convention":"actual_minus_predicted"},"arms":{"gate_zero":_virgin_metric(vals,"model",rs)},"baselines":{"league_base_rate":_virgin_metric(vals,"league",rs),"naive":_virgin_metric(vals,"naive",rs)}}
 if predict_arm=="gate_zero":
  (HERE/"predictions").mkdir(exist_ok=True)
  with (HERE/"predictions"/"k_lv_virgin_predictions.csv").open("w",newline="") as f:
   fs=["match_id","date","season","arm","actual_target","predicted_mean","predicted_mean_1h","predicted_mean_2h"]+[f"p_over_{str(L).replace('.','_')}" for L in LINES]; w=csv.DictWriter(f,fieldnames=fs); w.writeheader()
   for r,p in ps:w.writerow({"match_id":r["match_id"],"date":r["date"].isoformat(),"season":r["season"],"arm":"gate_zero","actual_target":r["y"],"predicted_mean":p["model"],"predicted_mean_1h":p["model"]*.3306,"predicted_mean_2h":p["model"]*.6694,**{f"p_over_{str(L).replace('.','_')}":nb_over(p["model"],rs,L) for L in LINES}})
  (HERE/"fitted_params_virgin.json").write_text(json.dumps({"market":"cards","target":"yellow_home + yellow_away","primary_line":PRIMARY,"arm":"gate_zero","r":rs,"league_base_mu":base},indent=2)+"\n")
 (HERE/"results_virgin.json").write_text(json.dumps(out,indent=2)+"\n"); print(json.dumps(out,indent=2)); return out
if __name__=="__main__":
 p=argparse.ArgumentParser(); sub=p.add_subparsers(dest="command",required=True)
 sub.add_parser("dev")
 v=sub.add_parser("virgin"); v.add_argument("--arm",nargs="?",default="gate_zero",choices=("gate_zero",))
 q=sub.add_parser("virgin-predict"); q.add_argument("--arm",required=True,choices=("gate_zero",))
 a=p.parse_args()
 if a.command=="dev": run_dev()
 elif a.command=="virgin": run_virgin()
 else: run_virgin(predict_arm=a.arm)
