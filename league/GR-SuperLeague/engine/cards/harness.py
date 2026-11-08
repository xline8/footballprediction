import csv, json, math
from datetime import date
from pathlib import Path
from model import Online, estimate_r, nb_over

HERE=Path(__file__).resolve().parent; DATA=HERE.parents[1]/"data"/"gr_matches.csv"; PRED=HERE.parents[1]/"predictions"/"k_gr_virgin_predictions.csv"
DEV=("2021/2022","2022/2023","2023/2024","2024/2025"); SCORED=DEV[1:]; VIRGIN="2025/2026"
def load(seasons):
    out=[]
    with DATA.open(newline="",encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["season"] not in seasons: continue
            if r["yellow_home"] == "" or r["yellow_away"] == "": continue  # target absent (score-only match) — never imputed
            key=(r["date"]+"T00:00:00Z",r["match_id"]); yh=int(float(r["yellow_home"])); ya=int(float(r["yellow_away"]))
            out.append({"match_id":r["match_id"],"season":r["season"],"date":r["date"],"kickoff_utc":key[0],"key":key,"day":date.fromisoformat(r["date"]).toordinal(),"home_id":int(r["home_team_id"]),"away_id":int(r["away_team_id"]),"home":r["home_team"],"away":r["away_team"],"yh":yh,"ya":ya,"y":yh+ya})
    out.sort(key=lambda x:x["key"]); return out
def scored(rs,rm):
    o={}
    for method in ("model","base","naive"):
        o[method]={}
        for line in (3.5,4.5,5.5):
            ps=[nb_over(x[method],rm[method],line) for x in rs]; ys=[int(x["y"]>line) for x in rs]; o[method][str(line)]={"n":len(rs),"ll":sum(-(y*math.log(max(p,1e-12))+(1-y)*math.log(max(1-p,1e-12))) for p,y in zip(ps,ys))/len(rs),"mean_p":sum(ps)/len(ps),"actual_rate":sum(ys)/len(ys)}
    return o
def rmap(rs): return {m:estimate_r(rs,m) for m in ("model","base","naive")}
def dev():
    rows=load(DEV); online=Online(); arms=("gate_zero",); warm={a:[] for a in arms}; sp={a:{s:[] for s in SCORED} for a in arms}
    for row in rows:
        for a in arms:
            p=online.prediction(row,a); rec={"y":row["y"],"model":p["model"],"base":p["base"],"naive":p["naive"]}; (warm if row["season"]==DEV[0] else sp)[a] [row["season"]].append((row,p)) if row["season"] in SCORED else warm[a].append(rec)
        online.update(row)
    out={"protocol":{"league":"GR-SuperLeague","warmup":DEV[0],"scored":list(SCORED),"dev_rows_loaded":len(rows),"scored_n":716,"primary_line":4.5,"sign_convention":"actual_minus_predicted"},"arms":{}}
    for a in arms:
        rm=rmap(warm[a]); ss={}; allr=[]
        for s in SCORED:
            rr=[{"y":r["y"],"model":p["model"],"base":p["base"],"naive":p["naive"]} for r,p in sp[a][s]]; allr+=rr; ss[s]=scored(rr,rm)
        ss["pooled"]=scored(allr,rm); ss4=ss["pooled"]; out["arms"][a]={"r":rm,"seasons":ss,"dev_gate_pass":ss4["model"]["4.5"]["ll"]<ss4["base"]["4.5"]["ll"] and ss4["model"]["4.5"]["ll"]<ss4["naive"]["4.5"]["ll"]}
    (HERE/"results_dev.json").write_text(json.dumps(out,indent=2)+"\n"); return out
