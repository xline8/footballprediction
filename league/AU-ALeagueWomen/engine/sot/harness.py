import csv,json,math
from datetime import date
from pathlib import Path
from model import Engine, nb_over, NB_R
HERE=Path(__file__).resolve().parent; DATA=HERE.parents[1]/"data"/"auw_matches.csv"; SEASONS=("2021/2022","2022/2023","2023/2024","2024/2025"); TARGETS=SEASONS[1:]; VIRGIN="2025/2026"; LINE=10.5
def load():
 out=[]
 with DATA.open(newline="",encoding="utf-8") as f:
  for r in csv.DictReader(f):
   if r["season"] not in SEASONS or r["phase"]!="regular" or r["home_ShotsOnTarget"]=="" or r["away_ShotsOnTarget"]=="": continue
   d=date.fromisoformat(r["date"]); out.append({"match_id":r["match_id"],"season":r["season"],"date":d,"day":d.toordinal(),"div":"AUW","home":r["home_team_id"],"away":r["away_team_id"],"home_name":r["home_team"],"away_name":r["away_team"],"shots_h":float(r["home_total_shots"]),"shots_a":float(r["away_total_shots"]),"sot_h":float(r["home_ShotsOnTarget"]),"sot_a":float(r["away_ShotsOnTarget"]),"xg_home":None,"xg_away":None})
 return sorted(out,key=lambda x:(x["date"],x["match_id"]))
def ll(p,y): return -(y*math.log(max(p,1e-12))+(1-y)*math.log(max(1-p,1e-12)))
def record(m,arm,p): return {"match_id":m["match_id"],"season":m["season"],"date":m["date"].isoformat(),"home":m["home_name"],"away":m["away_name"],"arm":arm,"p_over_primary":p,"actual_total":m["sot_h"]+m["sot_a"],"actual_over_primary":int(m["sot_h"]+m["sot_a"]>LINE)}
def run_dev():
 ms=load(); assert len(ms)==439 and not any(m["season"]>="2025/2026" for m in ms); pred=[]
 for s in TARGETS:
  cut=min(m["date"] for m in ms if m["season"]==s); train=[m for m in ms if m["date"]<cut]; target=[m for m in ms if m["season"]==s]
  for arm in ("GZ","RS"):
   eng=Engine(train,arm)
   for m in target:
    p=eng.predict(m); pred.append(record(m,arm,p["probs"][LINE])); eng.update(m)
  eng=Engine(train,"GZ")
  for m in target:
   p=eng.predict(m); pred.append(record(m,"baseline_naive",p["naive_probs"][LINE])); eng.update(m)
  base=sum(m["sot_h"]+m["sot_a"]>LINE for m in train)/len(train)
  for m in target: pred.append(record(m,"baseline_league",base))
 metrics=[]
 for a in ("GZ","RS","baseline_league","baseline_naive"):
  for s in TARGETS+("pooled",):
   q=[x for x in pred if x["arm"]==a and (s=="pooled" or x["season"]==s)]; metrics.append({"arm":a,"season":s,"n":len(q),"primary_ll":sum(ll(x["p_over_primary"],x["actual_over_primary"]) for x in q)/len(q)})
 payload={"protocol":{"regular_only":True,"loaded_seasons":list(SEASONS),"dev_n":369,"primary_line":LINE,"ladder":[8.5,9.5,10.5],"halves":[.469,.531]},"metrics":metrics,"calibration_inputs":pred}; (HERE/"results_dev.json").write_text(json.dumps(payload,indent=2)+"\n")
 with (HERE/"results_dev.csv").open("w",newline="") as f: w=csv.DictWriter(f,fieldnames=list(pred[0])); w.writeheader(); w.writerows(pred)
 return payload

def load_all():
 out=[]
 with DATA.open(newline="",encoding="utf-8") as f:
  for r in csv.DictReader(f):
   if r["season"] not in SEASONS+(VIRGIN,) or r["phase"]!="regular" or r["home_ShotsOnTarget"]=="" or r["away_ShotsOnTarget"]=="": continue
   d=date.fromisoformat(r["date"]); out.append({"match_id":r["match_id"],"season":r["season"],"date":d,"day":d.toordinal(),"div":"AUW","home":r["home_team_id"],"away":r["away_team_id"],"home_name":r["home_team"],"away_name":r["away_team"],"shots_h":float(r["home_total_shots"]),"shots_a":float(r["away_total_shots"]),"sot_h":float(r["home_ShotsOnTarget"]),"sot_a":float(r["away_ShotsOnTarget"]),"xg_home":None,"xg_away":None})
 return sorted(out,key=lambda x:(x["date"],x["match_id"]))

def virgin():
 ms=load_all(); target=[m for m in ms if m["season"]==VIRGIN]; train=[m for m in ms if m["date"]<min(x["date"] for x in target)]
 assert len(target)==110 and len(train)==439
 pred=[]
 for arm in ("GZ","RS"):
  eng=Engine(train,arm)
  for m in target:
   p=eng.predict(m); pred.append(record(m,arm,p["probs"][LINE])); eng.update(m)
 for kind in ("baseline_league","baseline_naive"):
  eng=Engine(train,"GZ"); base=sum(x["sot_h"]+x["sot_a"]>LINE for x in train)/len(train)
  for m in target:
   p=eng.predict(m); pred.append(record(m,kind,base if kind=="baseline_league" else p["naive_probs"][LINE])); eng.update(m)
 metrics=[]
 for arm in ("GZ","RS","baseline_league","baseline_naive"):
  q=[x for x in pred if x["arm"]==arm]; e=[x["p_over_primary"]-x["actual_over_primary"] for x in q]; mean=sum(e)/len(e); se=(sum((z-mean)**2 for z in e)/(len(e)-1))**.5/(len(e)**.5)
  metrics.append({"arm":arm,"season":VIRGIN,"n":len(q),"primary_ll":sum(ll(x["p_over_primary"],x["actual_over_primary"]) for x in q)/len(q),"mean_p":sum(x["p_over_primary"] for x in q)/len(q),"actual_over_rate":sum(x["actual_over_primary"] for x in q)/len(q),"calibration_diff":mean,"calibration_se":se})
 dev=json.load(open(HERE/"results_dev.json")); sign={"GZ":True,"RS":sum(next(x for x in dev["metrics"] if x["arm"]=="RS" and x["season"]==s)["primary_ll"]<=next(x for x in dev["metrics"] if x["arm"]=="GZ" and x["season"]==s)["primary_ll"] for s in TARGETS)>=2}; by={x["arm"]:x for x in metrics}; best=min(by[a]["primary_ll"] for a in ("baseline_league","baseline_naive")); gz=by["GZ"]["primary_ll"]
 for a in ("GZ","RS"):
  by[a]["leg_i"]=bool(by[a]["primary_ll"]<=gz and by[a]["primary_ll"]<=best); by[a]["leg_ii"]=bool(abs(by[a]["calibration_diff"])<=.01+by[a]["calibration_se"]); by[a]["sign_check"]=bool(sign[a]); by[a]["eligible"]=bool(by[a]["leg_i"] and by[a]["leg_ii"] and by[a]["sign_check"])
 eligible=[a for a in ("GZ","RS") if by[a]["eligible"]]; ship=min(eligible,key=lambda a:(by[a]["primary_ll"],0 if a=="GZ" else 1)) if eligible else None
 payload={"protocol":{"regular_only":True,"loaded_seasons":list(SEASONS)+[VIRGIN],"train_n":len(train),"virgin_n":len(target),"primary_line":LINE,"ladder":[8.5,9.5,10.5],"halves":[.469,.531]},"metrics":metrics,"dev_sign_check":sign,"ship_arm":ship,"calibration_inputs":pred}
 (HERE/"results_virgin.json").write_text(json.dumps(payload,indent=2)+"\n")
 with (HERE/"results_virgin.csv").open("w",newline="") as f: w=csv.DictWriter(f,fieldnames=list(pred[0])); w.writeheader(); w.writerows(pred)
 if ship:
  eng=Engine(train,ship); rows=[]
  for m in target:
   p=eng.predict(m); total=p["exp_h"]+p["exp_a"]; row={"arm":ship,"match_id":m["match_id"],"date":m["date"].isoformat(),"home_team":m["home_name"],"away_team":m["away_name"],"actual_total_sot":m["sot_h"]+m["sot_a"],"exp_sot_home":p["exp_h"],"exp_sot_away":p["exp_a"],"exp_sot_total":total}
   for L in (8.5,9.5,10.5): row[f"ft_p_over_{L}"]=p["probs"][L]
   for L in (3.5,4.5,5.5): row[f"1h_p_over_{L}"]=nb_over(.469*total,NB_R,L)
   for L in (4.5,5.5,6.5): row[f"2h_p_over_{L}"]=nb_over(.531*total,NB_R,L)
   rows.append(row); eng.update(m)
  path=HERE.parents[1]/"predictions"/"s_auw_virgin_predictions.csv"; path.parent.mkdir(exist_ok=True)
  with path.open("w",newline="") as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
  (HERE/"fitted_params_virgin.json").write_text(json.dumps({"arm":ship,"protocol":"fixed pre-virgin training","train_n":len(train)},indent=2)+"\n")
