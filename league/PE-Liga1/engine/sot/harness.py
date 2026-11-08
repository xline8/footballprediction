import csv, json, math, os
import numpy as np
from model import Engine, load_matches, NB_R, LINES, nb_over

ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),"..",".."))
DATA=os.path.join(ROOT,"data","pe_liga1_matches.csv")
OUT=os.path.dirname(__file__); ARMS=("GZ","RS")
SEED={"2021 - Fase 1","2021 - Fase 2"}
DEV=("2022 - Apertura","2022 - Clausura","2023 - Apertura","2023 - Clausura","2024 - Apertura","2024 - Clausura")
VIRGIN=("2025 - Apertura","2025 - Clausura"); HALF=.4611

def ll(p,y):
 p=min(max(p,1e-12),1-1e-12); return -(y*math.log(p)+(1-y)*math.log(1-p))
def actual(m,L): return float(m["sot_h"]+m["sot_a"]>L)
def metric(rows):
 o={"pooled":{},"seasons":{},"n":len(rows)}
 for L in LINES:
  o["pooled"][f"ll_{L}"]=sum(ll(p["probs"][L],actual(m,L)) for m,p in rows)/len(rows)
  for s in sorted({m["season"] for m,_ in rows}):
   z=[ll(p["probs"][L],actual(m,L)) for m,p in rows if m["season"]==s]
   o["seasons"].setdefault(s,{})[f"ll_{L}"]=sum(z)/len(z); o["seasons"][s]["n"]=len(z)
 return o
def baseline(rows,kind):
 vals=[]
 for m,p in rows:
  q=p["naive_probs"][8.5] if kind=="naive" else sum(actual(x,8.5) for x,_ in rows if x["date"]<m["date"])/max(1,sum(x["date"]<m["date"] for x,_ in rows))
  vals.append((m,q))
 return {"pooled":{"ll_8.5":sum(ll(q,actual(m,8.5)) for m,q in vals)/len(vals)},"n":len(vals)}
def run_dev():
 ms=load_matches(DATA,{*SEED,*DEV}); assert not any(m["season"].startswith(("2025","2026")) for m in ms)
 out={"protocol":"S-PE frozen prereg","arms":{},"baselines":{},"scored_n_by_block":{}}
 rb={}
 for a in ARMS:
  e=Engine(ms,a); rows=[]
  for m in ms:
   if m["season"] in DEV: rows.append((m,e.predict(m)))
   e.update(m)
  rb[a]=rows; out["arms"][a]=metric(rows)
 out["n"]=len(rb["GZ"]); out["baselines"]={k:baseline(rb["GZ"],k) for k in ("league_base_rate","naive")}; out["scored_n_by_block"]={s:out["arms"]["GZ"]["seasons"][s]["n"] for s in DEV}
 out["dev_pass"]={a:out["arms"][a]["pooled"]["ll_8.5"]<min(x["pooled"]["ll_8.5"] for x in out["baselines"].values()) for a in ARMS}
 json.dump(out,open(os.path.join(OUT,"results_dev.json"),"w"),indent=2); return out
def vmetrics(rows, key="probs"):
 ps=np.array([p[key][8.5] for _,p in rows]); ys=np.array([actual(m,8.5) for m,_ in rows]); d=ps-ys
 return {"ll_8.5":sum(ll(p,y) for p,y in zip(ps,ys))/len(ps),"calibration_diff":float(d.mean()),"calibration_se":float(d.std(ddof=1)/math.sqrt(len(d))),"n":len(ps)}
def virgin(dev):
 # Prereg short-circuit (PREREG_S_PE gate discipline):
 # if Gate Zero fails its dev gate the virgin is NOT read, variants moot
 # (the ported harness lacked the guard; dormant here since GZ passes dev).
 if not dev["dev_pass"].get("GZ"):
  out={"protocol":{"virgin_read":False},"virgin_read":False,"verdict":"FAIL","shipped_arm":None,"read_arms":[],"dev_gate":dev["dev_pass"]}
  json.dump(out,open(os.path.join(OUT,"results_virgin.json"),"w"),indent=2); json.dump({"virgin_read":False,"shipped_arm":None},open(os.path.join(OUT,"fitted_params_virgin.json"),"w"),indent=2); return out
 passing=[a for a in ARMS if dev["dev_pass"].get(a)]
 ms=load_matches(DATA,{*SEED,*DEV,*VIRGIN}); out={"protocol":{"virgin_season":VIRGIN,"transitional":False},"read_arms":passing,"arms":{},"baselines":{},"dev_gate":dev["dev_pass"]}
 rb={}
 for a in passing:
  e=Engine(ms,a); rows=[]
  for m in ms:
   if m["season"] in VIRGIN: rows.append((m,e.predict(m)))
   e.update(m)
  rb[a]=(rows,e); out["arms"][a]=vmetrics(rows)
 if passing:
  e=Engine(ms,"GZ"); rows=[]
  for m in ms:
   if m["season"] in VIRGIN: rows.append((m,e.predict(m)))
   e.update(m)
  rate=sum(actual(m,8.5) for m in ms if m["season"] not in VIRGIN)/sum(m["season"] not in VIRGIN for m in ms)
  out["baselines"]={"league_base_rate":{"ll_8.5":sum(ll(rate,actual(m,8.5)) for m,_ in rows)/len(rows),"rate":rate},"naive":vmetrics(rows,"naive_probs")}
 gzll=out["arms"].get("GZ",{}).get("ll_8.5",float("inf")); base=min((x["ll_8.5"] for x in out["baselines"].values()),default=float("inf")); eligible=[]
 for a,v in out["arms"].items():
  sign=a=="GZ" or sum(dev["arms"][a]["seasons"][s]["ll_8.5"]<=dev["arms"]["GZ"]["seasons"][s]["ll_8.5"] for s in DEV)>=3
  v["leg_i"]=bool(v["ll_8.5"]<=gzll and v["ll_8.5"]<=base); v["leg_ii"]=bool(abs(v["calibration_diff"])<=.01 or abs(v["calibration_diff"])<=.01+v["calibration_se"]); v["leg_iii"]=bool(sign); v["virgin_(i)"]=v["leg_i"]; v["virgin_(ii)"]=v["leg_ii"]; v["virgin_(iii)"]=v["leg_iii"]
  if v["leg_i"] and v["leg_ii"] and v["leg_iii"]: eligible.append(a)
 chosen=min(eligible,key=lambda a:(out["arms"][a]["ll_8.5"],ARMS.index(a))) if eligible else None
 out["shipped_arm"]=chosen; out["verdict"]="PASS" if chosen else "FAIL"; out["calibration_breach_plus_se_pp"]={a:(abs(v["calibration_diff"])-.01-v["calibration_se"])*100 for a,v in out["arms"].items()}
 json.dump(out,open(os.path.join(OUT,"results_virgin.json"),"w"),indent=2)
 if chosen:
  write_predictions(rb[chosen][0],chosen); json.dump({"arm":chosen,"nb_r":NB_R},open(os.path.join(OUT,"fitted_params_virgin.json"),"w"),indent=2)
 else: json.dump({"virgin_read":bool(passing),"shipped_arm":None},open(os.path.join(OUT,"fitted_params_virgin.json"),"w"),indent=2)
 return out
def write_predictions(rows,arm):
 path=os.path.join(OUT,"..","..","predictions","s_pe_virgin_predictions.csv"); os.makedirs(os.path.dirname(path),exist_ok=True)
 cols=["arm","match_id","date","home_team","away_team","actual_total_sot","exp_sot_home","exp_sot_away","exp_sot_total"]+[f"ft_p_over_{L}" for L in LINES]+[f"1h_p_over_{L}" for L in (2.5,3.5,4.5)]+[f"2h_p_over_{L}" for L in (3.5,4.5,5.5)]
 with open(path,"w",newline="") as f:
  w=csv.DictWriter(f,fieldnames=cols); w.writeheader()
  for m,p in rows:
   total=p["exp_h"]+p["exp_a"]; q={"arm":arm,"match_id":m["match_id"],"date":m["date"],"home_team":m["home"],"away_team":m["away"],"actual_total_sot":m["sot_h"]+m["sot_a"],"exp_sot_home":p["exp_h"],"exp_sot_away":p["exp_a"],"exp_sot_total":total}
   for L in LINES:q[f"ft_p_over_{L}"]=p["probs"][L]
   for L in (2.5,3.5,4.5):q[f"1h_p_over_{L}"]=nb_over(HALF*total,NB_R,L)
   for L in (3.5,4.5,5.5):q[f"2h_p_over_{L}"]=nb_over((1-HALF)*total,NB_R,L)
   w.writerow(q)

