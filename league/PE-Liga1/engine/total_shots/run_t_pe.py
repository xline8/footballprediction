#!/usr/bin/env python3
import argparse,csv,json,math,os
from datetime import date
import numpy as np
from model import BASE_HL,M_BAR,LevelLayer,NaiveTracker,BaseRateTracker,ShotsRegressionStore,TrailingR,logloss,nb_over,poisson_over

HERE=os.path.dirname(os.path.abspath(__file__)); DATA=os.path.join(HERE,"..","..","data","pe_liga1_matches.csv")
PRED=os.path.join(HERE,"..","..","predictions","t_pe_virgin_predictions.csv")
SEED=("2021 - Fase 1","2021 - Fase 2"); DEV=("2022 - Apertura","2022 - Clausura","2023 - Apertura","2023 - Clausura","2024 - Apertura","2024 - Clausura"); VIRGIN=("2025 - Apertura","2025 - Clausura"); ARMS=("A","B","C")
LINES=(19.5,17.5,18.5,20.5,21.5); CELLS=[(h,s,k) for h in (30.,60.,120.) for s in (.5,1.) for k in (20.,50.)]; HALF=.4662

def load(seasons):
 out=[]
 with open(DATA,newline="",encoding="utf-8") as f:
  for r in csv.DictReader(f):
   if r["block"] not in set(seasons) or r["phase"] != "regular" or r["awarded"] != "0": continue
   sh=(float(r["shotsontarget_home"])+float(r["shotsofftarget_home"])) if r["has_rich_stats"]=="1" and r["shotsofftarget_home"]!="" else (float(r["total_shots_home"]) if r["total_shots_home"]!="" else None)
   sa=(float(r["shotsontarget_away"])+float(r["shotsofftarget_away"])) if r["has_rich_stats"]=="1" and r["shotsofftarget_away"]!="" else (float(r["total_shots_away"]) if r["total_shots_away"]!="" else None)
   if sh is None or sa is None: continue
   d=date.fromisoformat(r["date"]); out.append({"match_id":r["match_id"],"season":r["block"],"date":r["date"],"day":d.toordinal(),"home_id":int(r["home_team_id"]),"away_id":int(r["away_team_id"]),"home":r["home_team"],"away":r["away_team"],"shots_h":sh,"shots_a":sa})
 out.sort(key=lambda x:(x["day"],int(x["match_id"]))); return out
def mom_r(a,b,c):
 d=b-c; return min(1e6,max(1.,a/d if d>0 else 1e6))
def tune(rows):
 reg=ShotsRegressionStore(rows,[3.,10.,30.,100.,300.]); scores={x:[0.,0] for x in (3.,10.,30.,100.,300.)}; res={x:[0.,0.,0.] for x in scores}
 for m in rows:
  y=m["shots_h"]+m["shots_a"]
  for lam in scores:
   h,a=reg.predict(m["home_id"],m["away_id"],m["day"],lam); mu=h+a
   scores[lam][1]+=logloss(poisson_over(mu,19.5),y>19.5); scores[lam][0]+=1
   x=res[lam]; x[0]+=mu*mu; x[1]+=(y-mu)**2; x[2]+=mu
 best=min(scores,key=lambda x:(scores[x][1]/scores[x][0],-x)); return best,mom_r(*res[best]),{str(x):scores[x][1]/scores[x][0] for x in scores}
class Acc:
 def __init__(self): self.n=0; self.ll={str(x):0. for x in LINES}; self.d=[]; self.sy=0.; self.sp=0.
 def add(self,pp,actual):
  self.n+=1
  for x in LINES:self.ll[str(x)]+=logloss(pp[x],actual>x)
  self.sp+=pp[19.5]; self.sy+=actual>19.5; self.d.append(pp[19.5]-(actual>19.5))
 def out(self):
  d=np.array(self.d); return {"n":self.n,"logloss":{k:v/self.n for k,v in self.ll.items()},"calibration_pp":float(d.mean()*100),"calibration_se_pp":float(d.std(ddof=1)/math.sqrt(self.n)*100),"actual_over_rate_pp":float(self.sy/self.n*100),"mean_pred_over_pp":float(self.sp/self.n*100)}
def pp(mu,r): return {x:.5*nb_over(mu,r,x) + .5*nb_over(mu,r,x) for x in LINES}
def score(rows,lam,ra,cell,arms,want_preds=False):
 reg=ShotsRegressionStore(rows,[lam]); naive=NaiveTracker(); base=BaseRateTracker(); layer=LevelLayer([cell]); trail=TrailingR(ra); methods=list(arms)+["baseline_league","baseline_naive"]; by={a:{s:Acc() for s in DEV+VIRGIN+("pooled","virgin_pooled")} for a in methods}; preds=[]
 for m in rows:
  total=m["shots_h"]+m["shots_a"]; eh,ea=reg.predict(m["home_id"],m["away_id"],m["day"],lam); rh,ra0=reg.league_mu(m["day"],lam); nh,na=naive.predict(m["home_id"],m["away_id"],rh,ra0); bh,ba=base.predict(m["day"]); lt=eh+ea; ln=nh+na; lb=bh+ba; ens=(lt+ln)/2; f=layer.factor(0,m["day"]); rc=trail.value(m["day"])
  probs={"A":{x:.5*nb_over(lt,ra,x)+.5*nb_over(ln,ra,x) for x in LINES},"B":{x:.5*nb_over(lt*f,ra,x)+.5*nb_over(ln*f,ra,x) for x in LINES},"C":{x:.5*nb_over(lt,rc,x)+.5*nb_over(ln,rc,x) for x in LINES},"baseline_league":{x:poisson_over(lb,x) for x in LINES},"baseline_naive":{x:.5*nb_over(ln,ra,x)+.5*nb_over(ln,ra,x) for x in LINES}}
  if m["season"] in by[methods[0]]:
   for a in methods:
    by[a][m["season"]].add(probs[a],total)
    if m["season"] in DEV: by[a]["pooled"].add(probs[a],total)
    # The PE virgin is
    # TWO blocks; the ported extraction kept only the last block's dict.
    # virgin_pooled accumulates both 2025 blocks (the prereg's n=280).
    if m["season"] in VIRGIN: by[a]["virgin_pooled"].add(probs[a],total)
   if want_preds and m["season"] in VIRGIN: preds.append((m,lt if True else ens,probs,f,rc))
  naive.update(m["home_id"],m["away_id"],m["shots_h"],m["shots_a"]); base.update(m["day"],m["shots_h"],m["shots_a"]); layer.update(0,m["day"],total,ens); trail.update(m["day"],total)
 return {a:{s:x.out() for s,x in z.items() if x.n} for a,z in by.items()},preds
def dev():
 rows=load(SEED+DEV); assert not any(m["season"] in VIRGIN for m in rows)
 lam,ra,tune_ll=tune(rows); cell=CELLS[0]; best=None; bestll=1e9
 for c in CELLS:
  z,_=score(rows,lam,ra,c,("A",)); x=z["A"]["2022 - Apertura"]["logloss"]["19.5"]
  if x<bestll:bestll=x; best=c
 cell=best; metrics,_=score(rows,lam,ra,cell,ARMS); metrics={a:{s:v for s,v in z.items() if s not in VIRGIN} for a,z in metrics.items()}
 passes={a:metrics[a]["pooled"]["logloss"]["19.5"]<metrics["baseline_league"]["pooled"]["logloss"]["19.5"] and metrics[a]["pooled"]["logloss"]["19.5"]<metrics["baseline_naive"]["pooled"]["logloss"]["19.5"] for a in ARMS}
 p={"lambda":lam,"r_A":ra,"level_cell":list(cell),"primary_line":19.5,"ladder":list(LINES),"half_split":[HALF,1-HALF],"base_half_life":BASE_HL}
 out={"protocol":{"seed":SEED,"dev_seasons_loaded":list(DEV),"virgin_not_loaded":True,"primary_line":19.5,"scored_n_by_block":{s:metrics["A"][s]["n"] for s in DEV}},"tuning":{"lambda_logloss_19_5":tune_ll,"lambda":lam,"r_A":ra},"metrics":metrics,"dev_pass":passes,"fitted_params":p}
 json.dump(out,open(os.path.join(HERE,"results_dev.json"),"w"),indent=2); json.dump(p,open(os.path.join(HERE,"fitted_params.json"),"w"),indent=2); print(json.dumps(out,indent=2)); return out
def virgin(dev):
 if not dev["dev_pass"].get("A"):
  out={"verdict":"FAIL","virgin_read":False,"reason":"arm A failed dev gate; virgin NOT read","read_arms":[],"dev_pass":dev["dev_pass"]}; json.dump(out,open(os.path.join(HERE,"results_virgin.json"),"w"),indent=2); json.dump({"virgin_read":False,"reason":out["reason"]},open(os.path.join(HERE,"fitted_params_virgin.json"),"w"),indent=2); print(json.dumps(out,indent=2)); return out
 passing=[a for a in ARMS if dev["dev_pass"].get(a)]; rows=load(SEED+DEV+VIRGIN); p=dev["fitted_params"]; metrics,preds=score(rows,p["lambda"],p["r_A"],tuple(p["level_cell"]),tuple(passing),True); out={"protocol":{"virgin_seasons":VIRGIN,"transitional":False},"read_arms":passing,"metrics":{a:metrics[a]["virgin_pooled"] for a in passing+["baseline_league","baseline_naive"]},"dev_pass":dev["dev_pass"]}
 eligible=[]; ref="A"; base=min(out["metrics"][x]["logloss"]["19.5"] for x in ("baseline_league","baseline_naive"))
 for a in passing:
  v=out["metrics"][a]
  sign=a=="A" or sum(dev["metrics"][a][s]["logloss"]["19.5"]<=dev["metrics"]["A"][s]["logloss"]["19.5"] for s in DEV)>=3
  v["leg_i"]=v["logloss"]["19.5"]<=out["metrics"][ref]["logloss"]["19.5"] and v["logloss"]["19.5"]<=base; v["leg_ii"]=abs(v["calibration_pp"])<=1.0 or abs(v["calibration_pp"])<=1.0+v["calibration_se_pp"]; v["leg_iii"]=sign
  v["virgin_(i)"]=v["leg_i"]; v["virgin_(ii)"]=v["leg_ii"]; v["virgin_(iii)"]=v["leg_iii"]
  if v["leg_i"] and v["leg_ii"] and v["leg_iii"]:eligible.append(a)
 chosen=min(eligible,key=lambda a:(out["metrics"][a]["logloss"]["19.5"],ARMS.index(a))) if eligible else None; out["shipped_arm"]=chosen; out["verdict"]="PASS" if chosen else "FAIL"; out["calibration_breach_plus_se_pp"]={a:abs(v["calibration_pp"])-1.-v["calibration_se_pp"] for a,v in out["metrics"].items() if a in passing}
 json.dump(out,open(os.path.join(HERE,"results_virgin.json"),"w"),indent=2)
 if chosen: write_predictions(preds,chosen,p["r_A"]); json.dump({"arm":chosen,"r_A":p["r_A"],"level_cell":p["level_cell"],"half_split":[HALF,1-HALF]},open(os.path.join(HERE,"fitted_params_virgin.json"),"w"),indent=2)
 print(json.dumps(out,indent=2)); return out
def write_predictions(preds,arm,ra):
 with open(PRED,"w",newline="") as f:
  fields=["match_id","date","home_team","away_team","arm","pred_total_ft","p_over_19_5","p_over_17_5","p_over_18_5","p_over_20_5","p_over_21_5","pred_total_1h","pred_total_2h","actual_total"]; w=csv.DictWriter(f,fieldnames=fields); w.writeheader()
  for m,mu,probs,f,rc in preds:
   mu_arm=mu*f if arm=="B" else mu
   q={"match_id":m["match_id"],"date":m["date"],"home_team":m["home"],"away_team":m["away"],"arm":arm,"pred_total_ft":mu_arm,"pred_total_1h":mu_arm*HALF,"pred_total_2h":mu_arm*(1-HALF),"actual_total":m["shots_h"]+m["shots_a"]}; q.update({f"p_over_{x}".replace(".","_"):probs[arm][x] for x in LINES}); w.writerow(q)
def main():
 ap=argparse.ArgumentParser(); ap.add_argument("step",choices=("dev","virgin")); a=ap.parse_args(); d=dev()
 if a.step=="virgin":virgin(d)
if __name__=="__main__":main()

