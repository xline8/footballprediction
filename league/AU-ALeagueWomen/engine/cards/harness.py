import csv,json,math
from datetime import date
from pathlib import Path
from model import Online,nb_over
HERE=Path(__file__).resolve().parent; DATA=HERE.parents[1]/"data"/"auw_matches.csv"; SEASONS=("2021/2022","2022/2023","2023/2024","2024/2025"); TARGETS=SEASONS[1:]; VIRGIN="2025/2026"; LINE=2.5
def load():
 out=[]
 with DATA.open(newline="",encoding="utf-8") as f:
  for r in csv.DictReader(f):
   if r["season"] not in SEASONS or r["phase"]!="regular": continue
   d=date.fromisoformat(r["date"]); out.append({"match_id":r["match_id"],"season":r["season"],"date":r["date"],"day":d.toordinal(),"home_id":int(r["home_team_id"]),"away_id":int(r["away_team_id"]),"home":r["home_team"],"away":r["away_team"],"yh":int(float(r["home_yellow_cards"])),"ya":int(float(r["away_yellow_cards"])),"y":int(float(r["home_yellow_cards"]))+int(float(r["away_yellow_cards"])),"referee":r.get("referee","")})
 return sorted(out,key=lambda x:(x["date"],x["match_id"]))
def ll(p,y): return -(y*math.log(max(p,1e-12))+(1-y)*math.log(max(1-p,1e-12)))
def dev():
 ms=load(); assert len(ms)==439 and not any(m["season"]>="2025/2026" for m in ms); pred=[]
 for s in TARGETS:
  cut=min(m["date"] for m in ms if m["season"]==s); train=[m for m in ms if m["date"]<cut]; target=[m for m in ms if m["season"]==s]
  for arm in ("gate_zero","x8"):
   o=Online()
   for m in train: o.update(m)
   for m in target:
    p=o.prediction(m,arm); pred.append({"match_id":m["match_id"],"season":s,"date":m["date"],"home":m["home"],"away":m["away"],"arm":arm,"p_over_primary":nb_over(p["model"],estimate(train,"model"),LINE),"actual_total":m["y"],"actual_over_primary":int(m["y"]>LINE),"referee_fallback":p["fallback_reason"]})
    o.update(m)
  base=sum(m["y"]>LINE for m in train)/len(train)
  for m in target: pred.append({"match_id":m["match_id"],"season":s,"date":m["date"],"home":m["home"],"away":m["away"],"arm":"baseline_league","p_over_primary":base,"actual_total":m["y"],"actual_over_primary":int(m["y"]>LINE),"referee_fallback":""})
  o=Online()
  for m in train: o.update(m)
  for m in target:
   p=o.prediction(m,"gate_zero"); pred.append({"match_id":m["match_id"],"season":s,"date":m["date"],"home":m["home"],"away":m["away"],"arm":"baseline_naive","p_over_primary":nb_over(p["naive"],estimate(train,"naive"),LINE),"actual_total":m["y"],"actual_over_primary":int(m["y"]>LINE),"referee_fallback":""}); o.update(m)
 metrics=[]
 for a in ("gate_zero","x8","baseline_league","baseline_naive"):
  for s in TARGETS+("pooled",):
   q=[x for x in pred if x["arm"]==a and (s=="pooled" or x["season"]==s)]; metrics.append({"arm":a,"season":s,"n":len(q),"primary_ll":sum(ll(x["p_over_primary"],x["actual_over_primary"]) for x in q)/len(q)})
 payload={"protocol":{"regular_only":True,"dev_n":369,"primary_line":LINE,"ladder":[1.5,2.5,3.5],"halves":[.314,.686]},"metrics":metrics,"calibration_inputs":pred}; (HERE/"results_dev.json").write_text(json.dumps(payload,indent=2)+"\n")
 with (HERE/"results_dev.csv").open("w",newline="") as f: w=csv.DictWriter(f,fieldnames=list(pred[0])); w.writeheader(); w.writerows(pred)
 return payload
def estimate(rows,key):
 vals=[r["y"] for r in rows]; m=sum(vals)/len(vals); v=sum((x-m)**2 for x in vals)/max(1,len(vals)-1); return max(2.0,m*m/max(v-m,1e-9))

def virgin():
 ms=load_all(); target=[m for m in ms if m["season"]==VIRGIN]; train=[m for m in ms if m["date"]<min(x["date"] for x in target)]; assert len(target)==110 and len(train)==439
 pred=[]
 for arm in ("gate_zero","x8"):
  o=Online(); [o.update(m) for m in train]
  for m in target:
   p=o.prediction(m,arm); pred.append({"match_id":m["match_id"],"season":VIRGIN,"date":m["date"],"home":m["home"],"away":m["away"],"arm":arm,"p_over_primary":nb_over(p["model"],estimate(train,"model"),LINE),"actual_total":m["y"],"actual_over_primary":int(m["y"]>LINE)}); o.update(m)
 for kind in ("baseline_league","baseline_naive"):
  o=Online(); [o.update(m) for m in train]; base=sum(m["y"]>LINE for m in train)/len(train)
  for m in target:
   p=o.prediction(m,"gate_zero"); pred.append({"match_id":m["match_id"],"season":VIRGIN,"date":m["date"],"home":m["home"],"away":m["away"],"arm":kind,"p_over_primary":base if kind=="baseline_league" else nb_over(p["naive"],estimate(train,"naive"),LINE),"actual_total":m["y"],"actual_over_primary":int(m["y"]>LINE)}); o.update(m)
 devj=json.load(open(HERE/"results_dev.json")); out=[]
 for arm in ("gate_zero","x8","baseline_league","baseline_naive"):
  q=[x for x in pred if x["arm"]==arm]; e=[x["p_over_primary"]-x["actual_over_primary"] for x in q]; mean=sum(e)/len(e); se=(sum((z-mean)**2 for z in e)/(len(e)-1))**.5/(len(e)**.5); out.append({"arm":arm,"season":VIRGIN,"n":len(q),"primary_ll":sum(ll(x["p_over_primary"],x["actual_over_primary"]) for x in q)/len(q),"mean_p":sum(x["p_over_primary"] for x in q)/len(q),"actual_over_rate":sum(x["actual_over_primary"] for x in q)/len(q),"calibration_diff":mean,"calibration_se":se})
 by={x["arm"]:x for x in out}; gz=by["gate_zero"]["primary_ll"]; best=min(by[a]["primary_ll"] for a in ("baseline_league","baseline_naive")); signs={"gate_zero":True,"x8":sum(next(x for x in devj["metrics"] if x["arm"]=="x8" and x["season"]==s)["primary_ll"]<=next(x for x in devj["metrics"] if x["arm"]=="gate_zero" and x["season"]==s)["primary_ll"] for s in TARGETS)>=2}
 for a in ("gate_zero","x8"):
  by[a]["leg_i"]=bool(by[a]["primary_ll"]<=gz and by[a]["primary_ll"]<=best); by[a]["leg_ii"]=bool(abs(by[a]["calibration_diff"])<=.01+by[a]["calibration_se"]); by[a]["sign_check"]=bool(signs[a]); by[a]["eligible"]=bool(by[a]["leg_i"] and by[a]["leg_ii"] and by[a]["sign_check"])
 eligible=[a for a in ("gate_zero","x8") if by[a]["eligible"]]; ship=min(eligible,key=lambda a:(by[a]["primary_ll"],0 if a=="gate_zero" else 1)) if eligible else None
 payload={"protocol":{"regular_only":True,"train_n":len(train),"virgin_n":len(target),"primary_line":LINE,"ladder":[1.5,2.5,3.5],"halves":[.314,.686]},"metrics":out,"dev_sign_check":signs,"ship_arm":ship,"calibration_inputs":pred}; (HERE/"results_virgin.json").write_text(json.dumps(payload,indent=2)+"\n")
 with (HERE/"results_virgin.csv").open("w",newline="") as f:w=csv.DictWriter(f,fieldnames=list(pred[0]));w.writeheader();w.writerows(pred)
 if ship:
  o=Online(); [o.update(m) for m in train]; rows=[]; rhat=estimate(train,"model")
  for m in target:
   p=o.prediction(m,ship); mu=p["model"]; row={"arm":ship,"match_id":m["match_id"],"date":m["date"],"home_team":m["home"],"away_team":m["away"],"actual_total_yellows":m["y"],"mu":mu}
   for L in (1.5,2.5,3.5):row[f"ft_p_over_{L}"]=nb_over(mu,rhat,L)
   for L in (0.5,1.5,2.5):row[f"1h_p_over_{L}"]=nb_over(.314*mu,rhat,L);row[f"2h_p_over_{L}"]=nb_over(.686*mu,rhat,L)
   rows.append(row);o.update(m)
  path=HERE.parents[1]/"predictions"/"k_auw_virgin_predictions.csv";path.parent.mkdir(exist_ok=True)
  with path.open("w",newline="") as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
  (HERE/"fitted_params_virgin.json").write_text(json.dumps({"arm":ship,"protocol":"fixed pre-virgin training","train_n":len(train)},indent=2)+"\n")

def load_all():
 out=[]
 with DATA.open(newline="",encoding="utf-8") as f:
  for r in csv.DictReader(f):
   if r["season"] not in SEASONS+(VIRGIN,) or r["phase"]!="regular": continue
   d=date.fromisoformat(r["date"]); out.append({"match_id":r["match_id"],"season":r["season"],"date":r["date"],"day":d.toordinal(),"home_id":int(r["home_team_id"]),"away_id":int(r["away_team_id"]),"home":r["home_team"],"away":r["away_team"],"yh":int(float(r["home_yellow_cards"])),"ya":int(float(r["away_yellow_cards"])),"y":int(float(r["home_yellow_cards"]))+int(float(r["away_yellow_cards"])),"referee":r.get("referee","")})
 return sorted(out,key=lambda x:(x["date"],x["match_id"]))
