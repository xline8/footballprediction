import csv,json,math
from datetime import date
from pathlib import Path
from model import ShotsRegressionStore,NaiveTracker,BaseRateTracker,LevelLayer,TrailingR,nb_over,M_BAR
HERE=Path(__file__).resolve().parent; DATA=HERE.parents[1]/"data"/"auw_matches.csv"; SEASONS=("2021/2022","2022/2023","2023/2024","2024/2025"); TARGETS=SEASONS[1:]; LINE=27.5
def load():
 out=[]
 with DATA.open(newline="",encoding="utf-8") as f:
  for r in csv.DictReader(f):
   if r["season"] not in SEASONS or r["phase"]!="regular" or r["home_total_shots"]=="" or r["away_total_shots"]=="": continue
   d=date.fromisoformat(r["date"]); out.append({"match_id":r["match_id"],"season":r["season"],"date":r["date"],"day":d.toordinal(),"home_id":int(r["home_team_id"]),"away_id":int(r["away_team_id"]),"home":r["home_team"],"away":r["away_team"],"shots_h":float(r["home_total_shots"]),"shots_a":float(r["away_total_shots"])})
 return sorted(out,key=lambda x:(x["day"],x["match_id"]))
def ll(p,y): return -(y*math.log(max(p,1e-12))+(1-y)*math.log(max(1-p,1e-12)))
def dev():
 ms=load(); assert len(ms)==439 and not any(m["season"]>="2025/2026" for m in ms); pred=[]; reg=ShotsRegressionStore(ms,[3,10,30,100,300]); naive=NaiveTracker(); base=BaseRateTracker(); layer=LevelLayer([(60,1.0,50)]); trail=TrailingR(40)
 for m in ms:
  if m["season"] in TARGETS:
   eh,ea=reg.predict(m["home_id"],m["away_id"],m["day"],30); rh,ra=reg.league_mu(m["day"],30); nh,na=naive.predict(m["home_id"],m["away_id"],rh,ra); bh,ba=base.predict(m["day"]); lt,ln,lb=eh+ea,nh+na,bh+ba; f=layer.factor(0,m["day"]); rc=trail.value(m["day"]); actual=m["shots_h"]+m["shots_a"]
   vals={"A":(lt,40),"B":(lt*f,40),"C":(lt,rc),"baseline_league":(lb,None),"baseline_naive":(ln,None)}
   for arm,(mu,r) in vals.items(): p=nb_over(mu,r,LINE) if r else nb_over(mu,40,LINE); pred.append({"match_id":m["match_id"],"season":m["season"],"date":m["date"],"home":m["home"],"away":m["away"],"arm":arm,"p_over_primary":p,"actual_total":actual,"actual_over_primary":int(actual>LINE)})
  actual=m["shots_h"]+m["shots_a"]; naive.update(m["home_id"],m["away_id"],m["shots_h"],m["shots_a"]); base.update(m["day"],m["shots_h"],m["shots_a"]); layer.update(0,m["day"],actual,(eh+ea+nh+na)/2 if m["season"] in TARGETS else actual); trail.update(m["day"],actual)
 metrics=[]
 for a in ("A","B","C","baseline_league","baseline_naive"):
  for s in TARGETS+("pooled",):
   q=[x for x in pred if x["arm"]==a and (s=="pooled" or x["season"]==s)]; metrics.append({"arm":a,"season":s,"n":len(q),"primary_ll":sum(ll(x["p_over_primary"],x["actual_over_primary"]) for x in q)/len(q)})
 payload={"protocol":{"regular_only":True,"dev_n":369,"primary_line":LINE,"ladder":[26.5,27.5,28.5],"halves":[.467,.533]},"metrics":metrics,"calibration_inputs":pred}; (HERE/"results_dev.json").write_text(json.dumps(payload,indent=2)+"\n")
 with (HERE/"results_dev.csv").open("w",newline="") as f: w=csv.DictWriter(f,fieldnames=list(pred[0])); w.writeheader(); w.writerows(pred)
 return payload
