import csv, json, math
from collections import defaultdict, deque
from datetime import date
from pathlib import Path
from dc import DC
from arms import adjusted_lambdas, match_counts

HERE = Path(__file__).resolve().parent
DATA = HERE.parents[1] / "data" / "auw_matches.csv"
SEASONS = ("2021/2022", "2022/2023", "2023/2024", "2024/2025")
TARGETS = SEASONS[1:]
LINE = 2.5

def load():
    out=[]
    with DATA.open(newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            if r["season"] not in SEASONS or r["phase"] != "regular": continue
            out.append({"match_id":r["match_id"],"season":r["season"],"date":date.fromisoformat(r["date"]),"hi":int(r["home_team_id"]),"ai":int(r["away_team_id"]),"home":r["home_team"],"away":r["away_team"],"yh":int(float(r["home_goals"])),"ya":int(float(r["away_goals"])),"xgh":None,"xga":None})
    return sorted(out,key=lambda x:(x["date"],x["match_id"]))

def ll(p,y): return -(y*math.log(max(p,1e-12))+(1-y)*math.log(max(1-p,1e-12)))
def metrics(rows, key):
    ys=[(r["actual_total"]>LINE) for r in rows]
    outcomes=[r["actual_outcome"] for r in rows]; idx={"H":2,"D":1,"A":0}
    one_ll=sum(-math.log(max(r[{"H":"p_home_win","D":"p_draw","A":"p_away_win"}[o]],1e-12)) for r,o in zip(rows,outcomes))/len(rows)
    rps=0.0
    for r,o in zip(rows,outcomes):
        p=[r["p_away_win"],r["p_draw"],r["p_home_win"]]; y=[0.0,0.0,0.0]; y[idx[o]]=1.0
        rps += .5*((p[0]-y[0])**2+(p[0]+p[1]-y[0]-y[1])**2)
    return {"n":len(rows),"primary_ll":sum(ll(r[key],y) for r,y in zip(rows,ys))/len(rows),"mean_p_over_primary":sum(r[key] for r in rows)/len(rows),"actual_over_primary":sum(ys)/len(ys),"ll_1x2":one_ll,"rps_1x2":rps/len(rows),"ou2_5_ll":sum(ll(r[key],y) for r,y in zip(rows,ys))/len(rows)}

def predict_rows(all_rows):
    predictions=[]
    for season in TARGETS:
        target=[r for r in all_rows if r["season"]==season]; cutoff=min(r["date"] for r in target); train=[r for r in all_rows if r["date"]<cutoff]
        model=DC().fit(train,cutoff); counts=match_counts(train); hist=defaultdict(lambda:deque(maxlen=10))
        for r in train: hist[r["hi"]].append((r["yh"],r["ya"])); hist[r["ai"]].append((r["ya"],r["yh"]))
        base=sum(r["yh"]+r["ya"] for r in train)/len(train)
        for r in target:
            recent=list(hist[r["hi"]])+list(hist[r["ai"]]); naive=sum(x[0] for x in recent)/len(recent) if recent else base
            actual={"match_id":r["match_id"],"season":season,"date":r["date"].isoformat(),"home":r["home"],"away":r["away"],"actual_total":r["yh"]+r["ya"],"actual_outcome":"H" if r["yh"]>r["ya"] else "D" if r["yh"]==r["ya"] else "A","actual_over_primary":int(r["yh"]+r["ya"]>LINE)}
            for arm in ("gate_zero","shrink"):
                lh,la=adjusted_lambdas(model,r["hi"],r["ai"],arm,set(),{},counts); p=model.probs(lh,la)
                predictions.append({**actual,"arm":arm,"p_over_primary":p["over25"],"p_home_win":p["ph"],"p_draw":p["pd"],"p_away_win":p["pa"]})
            for arm,pv in (("baseline_league",base),("baseline_naive",naive)):
                q=model.probs(pv/2,pv/2); predictions.append({**actual,"arm":arm,"p_over_primary":q["over25"],"p_home_win":q["ph"],"p_draw":q["pd"],"p_away_win":q["pa"]})
    return predictions

def run_dev():
    rows=load(); assert len(rows)==439 and not any(r["season"]>="2025/2026" for r in rows)
    pred=predict_rows(rows); result=[]
    for arm in ("gate_zero","shrink","baseline_league","baseline_naive"):
        for season in TARGETS+("pooled",):
            ps=[p for p in pred if p["arm"]==arm and (season=="pooled" or p["season"]==season)]
            result.append({"arm":arm,"season":season,"primary_line":LINE,**metrics(ps,"p_over_primary")})
    payload={"protocol":{"regular_only":True,"loaded_seasons":list(SEASONS),"dev_seasons":list(TARGETS),"n":369,"primary_line":LINE,"ladder":[1.5,2.5,3.5],"halves":[.459,.541]},"metrics":result,"calibration_inputs":pred}
    (HERE/"results_dev.json").write_text(json.dumps(payload,indent=2)+"\n")
    with (HERE/"results_dev.csv").open("w",newline="",encoding="utf-8") as fh:
        w=csv.DictWriter(fh,fieldnames=list(pred[0])); w.writeheader(); w.writerows(pred)
    return payload
