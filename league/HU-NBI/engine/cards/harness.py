"""HU-NBI cards dev harness; event_yellow_* is Yellow + YellowRed."""
import csv,json,math
from datetime import datetime
from pathlib import Path
from model import Online, estimate_r, nb_over

HERE=Path(__file__).resolve().parent; DATA=HERE.parents[1]/"data"/"hu_nbi.csv"
DEV=("2021/2022","2022/2023","2023/2024","2024/2025"); SCORED=DEV[1:]; LINE=4.5
def load(seasons):
    seasons=set(seasons); assert seasons <= set(DEV), "HU loader allow-list blocks virgin seasons"; out=[]
    with DATA.open(newline="",encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            if r["season"] not in seasons: continue
            kickoff=r["date"]+"T00:00:00Z"
            out.append({"match_id":r["match_id"],"season":r["season"],"date":r["date"],"kickoff_utc":kickoff,"key":(kickoff,r["match_id"]),"day":datetime.fromisoformat(r["date"]).date().toordinal(),"home_id":int(r["home_id"]),"away_id":int(r["away_id"]),"home":r["home_team"],"away":r["away_team"],"yh":int(float(r["event_yellow_h"])),"ya":int(float(r["event_yellow_a"])),"y":int(float(r["event_yellow_h"]))+int(float(r["event_yellow_a"])),"referee":(r.get("referee") or "").strip()})
    return sorted(out,key=lambda x:x["key"])
def ll(p,y): return -(y*math.log(max(p,1e-12))+(1-y)*math.log(max(1-p,1e-12)))
def metric(xs):
    return {"n":len(xs),"ll_4.5":sum(ll(nb_over(x["p"],x["r"],LINE),x["y"]>LINE) for x in xs)/len(xs),"per_season":{s:{"n":len(z),"ll_4.5":sum(ll(nb_over(x["p"],x["r"],LINE),x["y"]>LINE) for x in z)/len(z)} for s in SCORED for z in [[x for x in xs if x["season"]==s]]}}
def run_dev():
    rows=load(DEV); out={"protocol":{"league":"HU-NBI","dev_seasons_loaded":list(DEV),"virgin_seasons_forbidden":["2025/2026","2026/2027"],"cards_target_mapping":"event_yellow_h + event_yellow_a"},"primary_line":LINE,"arms":{},"baselines":{},"gate":{}}
    allp={}; warm={a:[] for a in ("gate_zero","x8")}; preds={a:[] for a in warm}; online=Online()
    for row in rows:
        for arm in warm:
            p=online.prediction(row,arm); rec={"season":row["season"],"row":row,"y":row["y"],"p":p["model"],"r":None,"out":p}; (warm if row["season"]==DEV[0] else preds)[arm].append(rec)
        online.update(row)
    for arm in preds:
        r=estimate_r(warm[arm],"p"); allp[arm]=[{**x,"r":r} for x in preds[arm]]; out["arms"][arm]=metric(allp[arm])
    for name,key in (("base_rate","base"),("naive_trailing_10","naive")):
        xs=[]; online=Online(); warmx=[]
        for row in rows:
            p=online.prediction(row,"gate_zero")
            if row["season"]==DEV[0]: warmx.append({"y":row["y"],"p":p[key]})
            else: xs.append({"season":row["season"],"y":row["y"],"p":p[key],"r":None})
            online.update(row)
        r=estimate_r(warmx,"p"); out["baselines"][name]=metric([{**x,"r":r} for x in xs])
    for arm in allp: out["gate"][arm]={"pooled_beats_base_rate":out["arms"][arm]["ll_4.5"]<out["baselines"]["base_rate"]["ll_4.5"],"pooled_beats_naive_trailing_10":out["arms"][arm]["ll_4.5"]<out["baselines"]["naive_trailing_10"]["ll_4.5"]}
    (HERE/"results_dev.json").write_text(json.dumps(out,indent=2)+"\n")
    for arm,xs in allp.items():
        with (HERE/f"dev_predictions_{arm}.csv").open("w",newline="",encoding="utf-8") as fh:
            fields=["match_id","season","date","home_id","away_id","expected","p_over","actual"]
            w=csv.DictWriter(fh,fieldnames=fields); w.writeheader()
            for x in xs:
                p=x["out"]; w.writerow({"match_id":x["row"]["match_id"],"season":x["season"],"date":x["row"]["date"],"home_id":x["row"]["home_id"],"away_id":x["row"]["away_id"],"expected":p["model"],"p_over":nb_over(x["p"],x["r"],LINE),"actual":x["y"]})
    return out
