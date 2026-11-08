"""Development-only date-grouped cards walk-forward."""
import csv,json,math
from datetime import date
from pathlib import Path
from model import Online,estimate_r,nb_over
HERE=Path(__file__).resolve().parent; DATA=HERE.parents[1]/"data"/"sco_league_one_matches.csv"
SEASONS=("2021/2022","2022/2023","2023/2024","2024/2025"); SCORED=SEASONS[1:]; VIRGIN_SEASON="2025/2026"; LINES=(2.5,3.5,4.5); HALF_1H=0.3141
def load(seasons=SEASONS):
    out=[]
    with DATA.open(newline="",encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["season"] == "2026/2027": continue
            if r["season"] not in seasons: continue
            key=(r["date"],r["match_id"]); yh=int(float(r["yellow_home"])); ya=int(float(r["yellow_away"]))
            out.append({"match_id":r["match_id"],"season":r["season"],"date":r["date"],"key":key,"day":date.fromisoformat(r["date"]).toordinal(),"home_id":int(r["home_team_id"]),"away_id":int(r["away_team_id"]),"home":r["home_team"],"away":r["away_team"],"yh":yh,"ya":ya,"y":yh+ya,"referee":r["referee"]})
    out.sort(key=lambda x:x["key"]); assert all(sum(x["season"]==s for x in out)==180 for s in SEASONS); assert all(not x["referee"] for x in out); return out
def metric(pairs,r,line=3.5):
    ps=[nb_over(x["pred"],r,line) for x in pairs]; ys=[int(x["row"]["y"]>line) for x in pairs]; return {"n":len(ps),"ll":sum(-(y*math.log(max(p,1e-12))+(1-y)*math.log(max(1-p,1e-12))) for p,y in zip(ps,ys))/len(ps),"mean_p":sum(ps)/len(ps),"actual_rate":sum(ys)/len(ys)}
def run_dev():
    rows=load(); online=Online(); warm=[]; scored=[]
    i=0
    while i<len(rows):
        j=i
        while j<len(rows) and rows[j]["date"]==rows[i]["date"]: j+=1
        group=rows[i:j]; preds=[online.prediction(x) for x in group]
        for row,p in zip(group,preds):
            rec={"row":row,"pred":p}; (warm if row["season"]==SEASONS[0] else scored).append(rec)
        for row in group: online.update(row)
        i=j
    rm={m:estimate_r([{"y":x["row"]["y"],m:x["pred"][m]} for x in warm],m) for m in ("model","base","naive")}
    seasons={};
    for s in SCORED+ ("pooled",):
        pairs=scored if s=="pooled" else [x for x in scored if x["row"]["season"]==s]
        seasons[s]={m:metric([{ "row":x["row"],"pred":x["pred"][m]} for x in pairs],rm[m]) for m in ("model","base","naive")}
    gate=seasons["pooled"]["model"]["ll"]<seasons["pooled"]["base"]["ll"] and seasons["pooled"]["model"]["ll"]<seasons["pooled"]["naive"]["ll"]
    result={"protocol":{"league":"SCO-LeagueOne","dev_seasons_loaded":list(SEASONS),"scored_n":540,"primary_line":3.5,"target":"yellow_home + yellow_away","sign_convention":"actual_minus_predicted"},"arms":{"gate_zero":{"r":rm,"seasons":seasons,"dev_gate_pass":gate}},"baselines":{"base":seasons["pooled"]["base"],"naive":seasons["pooled"]["naive"]}}
    (HERE/"results_dev.json").write_text(json.dumps(result,indent=2)+"\n")
    fields=["match_id","season","date","home","away","actual_target","arm","predicted_mean","p_over_2_5","p_over_3_5","p_over_4_5","baseline_base_p_over_3_5","baseline_naive_p_over_3_5"]
    with (HERE/"results_dev.csv").open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader()
        for x in scored:
            p=x["pred"]; w.writerow({"match_id":x["row"]["match_id"],"season":x["row"]["season"],"date":x["row"]["date"],"home":x["row"]["home"],"away":x["row"]["away"],"actual_target":x["row"]["y"],"arm":"gate_zero","predicted_mean":p["model"],"p_over_2_5":nb_over(p["model"],rm["model"],2.5),"p_over_3_5":nb_over(p["model"],rm["model"],3.5),"p_over_4_5":nb_over(p["model"],rm["model"],4.5),"baseline_base_p_over_3_5":nb_over(p["base"],rm["base"],3.5),"baseline_naive_p_over_3_5":nb_over(p["naive"],rm["naive"],3.5)})
    print(json.dumps({"dev_gate_pass":gate,"pooled":seasons["pooled"]},indent=2)); return result

def virgin():
    dev=json.loads((HERE/"results_dev.json").read_text())
    if not dev["arms"]["gate_zero"]["dev_gate_pass"]:
        raise SystemExit("virgin refused: Gate Zero failed the K-SCO-L1 dev gate")
    rows=load(SEASONS+(VIRGIN_SEASON,))
    assert len(rows)==900
    assert sum(x["season"]==VIRGIN_SEASON for x in rows)==180
    assert all(sum(x["season"]==s for x in rows)==180 for s in SEASONS)
    assert not any(x["season"]=="2026/2027" for x in rows)
    online=Online(); warm=[]; target=[]
    i=0
    while i<len(rows):
        j=i
        while j<len(rows) and rows[j]["date"]==rows[i]["date"]: j+=1
        group=rows[i:j]; preds=[online.prediction(x) for x in group]
        for row,p in zip(group,preds):
            rec={"row":row,"p":p,"y":row["y"],"model":p["model"],"base":p["base"],"naive":p["naive"]}
            (target if row["season"]==VIRGIN_SEASON else warm).append(rec)
        for row in group: online.update(row)
        i=j
    rm={m:estimate_r(warm,m) for m in ("model","base","naive")}
    def metrics(method):
        out={}
        for line in LINES:
            ps=[nb_over(x[method],rm[method],line) for x in target]; ys=[int(x["y"]>line) for x in target]
            out[str(line)]={"n":len(ys),"ll":sum(-(y*math.log(max(p,1e-12))+(1-y)*math.log(max(1-p,1e-12))) for p,y in zip(ps,ys))/len(ys),"mean_p":sum(ps)/len(ps),"actual_rate":sum(ys)/len(ys)}
        return out
    arms={m:metrics(m) for m in ("model","base","naive")}
    d=[int(x["y"]>3.5)-nb_over(x["model"],rm["model"],3.5) for x in target]
    breach=sum(d)/len(d); se=(sum((x-breach)**2 for x in d)/(len(d)-1))**.5/(len(d)**.5)
    ll_pass=arms["model"]["3.5"]["ll"]<=min(arms["base"]["3.5"]["ll"],arms["naive"]["3.5"]["ll"])
    cal_status="PASS" if abs(breach)<=.01 else ("PROVISIONAL PASS" if abs(breach)<=.01+se else "FAIL")
    cal_pass=cal_status!="FAIL"; shipped="gate_zero" if ll_pass and cal_pass else None
    out={"protocol":{"league":"SCO-LeagueOne","virgin_season":VIRGIN_SEASON,"n":len(target),"primary_line":3.5,"sign_convention":"actual_minus_predicted","r_handling":"estimate_r once from all pre-virgin warm-up predictions for model, base, and naive; Online state continues and updates through virgin"},"arms":{"gate_zero":{"r":rm,"metrics":{"model":arms["model"],"base":arms["base"],"naive":arms["naive"]},"calibration":{"breach_pp":100*breach,"se_pp":100*se,"status":cal_status},"legs":{"ll_le_best_baseline":ll_pass,"calibration":cal_pass}}},"baselines":{"base":arms["base"],"naive":arms["naive"]},"shipped_arm":shipped}
    (HERE/"results_virgin.json").write_text(json.dumps(out,indent=2)+"\n")
    fields=["match_id","date","home_team","away_team","actual_target","arm","predicted_mean","r","p_over_2_5","p_over_3_5","p_over_4_5"]
    with (HERE/"predictions_virgin.csv").open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader()
        for x in target:
            w.writerow({"match_id":x["row"]["match_id"],"date":x["row"]["date"],"home_team":x["row"]["home"],"away_team":x["row"]["away"],"actual_target":x["y"],"arm":"gate_zero","predicted_mean":x["model"],"r":rm["model"],**{"p_over_"+str(line).replace(".","_"):nb_over(x["model"],rm["model"],line) for line in LINES}})
    (HERE/"fitted_params_virgin.json").write_text(json.dumps({"arm":"gate_zero","shipped_arm":shipped,"r":rm} if shipped else {},indent=2)+"\n")
    if shipped:
        pred_dir=HERE.parents[1]/"predictions"; pred_dir.mkdir(exist_ok=True)
        fields=["arm","match_id","date","home_team","away_team","actual_total_yellows","ft_mean","ft_p_over_2_5","ft_p_over_3_5","ft_p_over_4_5","mean_1h","mean_2h","p_over_1h_0_5","p_over_1h_1_5","p_over_1h_2_5","p_over_2h_1_5","p_over_2h_2_5","p_over_2h_3_5"]
        with (pred_dir/"k_sco_l1_virgin_predictions.csv").open("w",newline="",encoding="utf-8") as f:
            w=csv.DictWriter(f,fieldnames=fields); w.writeheader()
            for x in target:
                ft=x["model"]; h1=ft*HALF_1H; h2=ft*(1-HALF_1H)
                w.writerow({"arm":"gate_zero","match_id":x["row"]["match_id"],"date":x["row"]["date"],"home_team":x["row"]["home"],"away_team":x["row"]["away"],"actual_total_yellows":x["y"],"ft_mean":ft,**{"ft_p_over_"+str(line).replace(".","_"):nb_over(ft,rm["model"],line) for line in LINES},"mean_1h":h1,"mean_2h":h2,"p_over_1h_0_5":nb_over(h1,rm["model"],.5),"p_over_1h_1_5":nb_over(h1,rm["model"],1.5),"p_over_1h_2_5":nb_over(h1,rm["model"],2.5),"p_over_2h_1_5":nb_over(h2,rm["model"],1.5),"p_over_2h_2_5":nb_over(h2,rm["model"],2.5),"p_over_2h_3_5":nb_over(h2,rm["model"],3.5)})
    print(json.dumps({"virgin_n":len(target),"ll_3.5":{"model":arms["model"]["3.5"]["ll"],"base":arms["base"]["3.5"]["ll"],"naive":arms["naive"]["3.5"]["ll"]},"calibration":out["arms"]["gate_zero"]["calibration"],"shipped_arm":shipped},indent=2))
    return out
