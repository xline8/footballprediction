"""NLTD goals data loading, walk-forward evaluation, virgin metrics, and outputs."""
import csv, json, math
from datetime import date
from pathlib import Path
from dc import DC
from arms import mover_ids, adjusted_lambdas, match_counts

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data" / "nl_tweede_matches.csv"
OUT = Path(__file__).resolve().parent
DEV_SEASONS = ("2021/2022", "2022/2023", "2023/2024", "2024/2025")
ARMS = ("gate_zero", "shrink", "x2")

def _num(value):
    if value is None or value.strip().lower() in ("", "nan", "na", "null"): return None
    return float(value)

def load(path, allowed=None):
    rows = []
    with open(path, newline="", encoding="utf-8") as f:
        for raw in csv.DictReader(f):
            if allowed is not None and raw["season"] not in allowed: continue
            row = {"match_id": raw["match_id"], "season": raw["season"], "date": date.fromisoformat(raw["date"]),
                   "hi": int(raw["home_team_id"]), "ai": int(raw["away_team_id"]), "home": raw["home_team"], "away": raw["away_team"],
                   "yh": int(raw["home_goals"]), "ya": int(raw["away_goals"]),
                   "xgh": _num(raw.get("expected_goals_home")), "xga": _num(raw.get("expected_goals_away"))}
            rows.append(row)
    assert all(r["xgh"] is None and r["xga"] is None for r in rows)
    return sorted(rows, key=lambda r: (r["date"], r["match_id"]))

def _fit_predict(train, target, arm, all_rows):
    cutoff = min(r["date"] for r in target); fit_rows = [r for r in train if r["date"] < cutoff]
    model = DC().fit(fit_rows, cutoff)
    movers = mover_ids(target[0]["season"], all_rows)
    return model, movers, match_counts(fit_rows)

def _scores(rows, probs):
    ll = rps = oull = 0.0
    for r, p in zip(rows, probs):
        y = (1,0,0) if r["yh"] > r["ya"] else ((0,1,0) if r["yh"] == r["ya"] else (0,0,1)); pp = [p["ph"],p["pd"],p["pa"]]
        ll -= math.log(max(pp[y.index(1)], 1e-12))
        rps += 0.5*((pp[0]-y[0])**2 + (pp[0]+pp[1]-y[0]-y[1])**2)
        over = r["yh"] + r["ya"] > 2.5; oull -= math.log(max(p["over25"] if over else 1-p["over25"], 1e-12))
    n = len(rows); return {"n":n,"ll_1x2":ll/n,"rps":rps/n,"oull_2_5":oull/n}

def _clim(train):
    n = len(train); hw = sum(r["yh"] > r["ya"] for r in train)/n; dr = sum(r["yh"] == r["ya"] for r in train)/n
    return [hw,dr,1-hw-dr], sum(r["yh"]+r["ya"] > 2.5 for r in train)/n

def run_dev():
    rows = load(DATA, set(DEV_SEASONS))
    assert {r["season"] for r in rows} == set(DEV_SEASONS)
    assert not any(r["season"] in ("2025/2026", "2026/2027") for r in rows)
    result = []
    for arm in ARMS:
        model_rows = []; clim_rows = []
        for season in DEV_SEASONS[1:]:
            target = [r for r in rows if r["season"] == season]; train = [r for r in rows if r["date"] < min(x["date"] for x in target)]
            model, movers, counts = _fit_predict(train, target, arm, rows)
            probs = [model.probs(*adjusted_lambdas(model,r["hi"],r["ai"],arm,movers,counts)) for r in target]
            met = _scores(target, probs); met.update({"arm":arm,"season":season,"kind":"model"}); result.append(met); model_rows += list(zip(target,probs))
            cp, co = _clim(train); cprobs = [{"ph":cp[0],"pd":cp[1],"pa":cp[2],"over25":co} for _ in target]
            met = _scores(target,cprobs); met.update({"arm":arm,"season":season,"kind":"climatology"}); result.append(met); clim_rows += list(zip(target,cprobs))
        for kind, pairs in (("model",model_rows),("climatology",clim_rows)):
            met = _scores([x[0] for x in pairs],[x[1] for x in pairs]); met.update({"arm":arm,"season":"pooled","kind":kind}); result.append(met)
    _write_dev(result); _print_table(result); return result

def _write_dev(result):
    (OUT/"results_dev.json").write_text(json.dumps(result,indent=2)+"\n")
    fields = ["arm","season","kind","n","ll_1x2","rps","oull_2_5"]
    with open(OUT/"results_dev.csv","w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows({k:r.get(k) for k in fields} for r in result)

def virgin_metrics(arms):
    rows = load(DATA, set(DEV_SEASONS) | {"2025/2026"}); train = [r for r in rows if r["season"] != "2025/2026"]; target = [r for r in rows if r["season"] == "2025/2026"]
    cp, co = _clim(train); result = {}
    for arm in arms:
        model, movers, counts = _fit_predict(train,target,arm,rows); preds=[]
        for r in target:
            lh,la=adjusted_lambdas(model,r["hi"],r["ai"],arm,movers,counts); p=model.probs(lh,la); p.update({"lh":lh,"la":la}); preds.append(p)
        def se(vals):
            m=sum(vals)/len(vals); return math.sqrt(sum((x-m)**2 for x in vals)/(len(vals)-1))/math.sqrt(len(vals))
        met=_scores(target,preds); actual_hw=[int(r["yh"]>r["ya"]) for r in target]; actual_ou=[int(r["yh"]+r["ya"]>2.5) for r in target]
        hw_res=[y-p["ph"] for y,p in zip(actual_hw,preds)]; ou_res=[y-p["over25"] for y,p in zip(actual_ou,preds)]
        met.update({"climatology":_scores(target,[{"ph":cp[0],"pd":cp[1],"pa":cp[2],"over25":co} for _ in target]),"calibration":{"home_win_diff":sum(hw_res)/len(hw_res),"home_win_se":se(hw_res),"over25_diff":sum(ou_res)/len(ou_res),"over25_se":se(ou_res)},"params":{"a":dict(model.a),"d":dict(model.d),"h":model.h,"rho":model.rho,"mu":model.mu,"movers":sorted(movers)}})
        result[arm]=met
    (OUT/"results_virgin.json").write_text(json.dumps(result,indent=2)+"\n"); return result

def write_predictions(arm):
    rows=load(DATA,set(DEV_SEASONS)|{"2025/2026"}); train=[r for r in rows if r["season"]!="2025/2026"]; target=[r for r in rows if r["season"]=="2025/2026"]
    model,movers,counts=_fit_predict(train,target,arm,rows); out=[]; c=0.436
    fields=["match_id","date","home_team","away_team","lam_h","lam_a","rho","ph","pd","pa","p_over_1_5","p_over_2_5","p_over_3_5","p_btts","lam_h_1h","lam_a_1h","p_over_1h_0_5","p_over_1h_1_5","p_over_1h_2_5","lam_h_2h","lam_a_2h","p_over_2h_1_5","p_over_2h_2_5","p_over_2h_3_5","arm"]
    for r in target:
        lh,la=adjusted_lambdas(model,r["hi"],r["ai"],arm,movers,counts); p=model.probs(lh,la); q1=model.probs(lh*c,la*c); q2=model.probs(lh*(1-c),la*(1-c))
        out.append({"match_id":r["match_id"],"date":r["date"].isoformat(),"home_team":r["home"],"away_team":r["away"],"lam_h":lh,"lam_a":la,"rho":model.rho,"ph":p["ph"],"pd":p["pd"],"pa":p["pa"],"p_over_1_5":p["over15"],"p_over_2_5":p["over25"],"p_over_3_5":p["over35"],"p_btts":p["btts"],"lam_h_1h":lh*c,"lam_a_1h":la*c,"p_over_1h_0_5":model.over(lh*c,la*c,.5),"p_over_1h_1_5":q1["over15"],"p_over_1h_2_5":q1["over25"],"lam_h_2h":lh*(1-c),"lam_a_2h":la*(1-c),"p_over_2h_1_5":q2["over15"],"p_over_2h_2_5":q2["over25"],"p_over_2h_3_5":q2["over35"],"arm":arm})
    dest=ROOT/"predictions"; dest.mkdir(exist_ok=True)
    with open(dest/"g_nltd_virgin_predictions.csv","w",newline="",encoding="utf-8") as f: w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(out)
    (OUT/"fitted_params_virgin.json").write_text(json.dumps({"a":dict(model.a),"d":dict(model.d),"h":model.h,"rho":model.rho,"mu":model.mu,"arm":arm,"movers":sorted(movers)},indent=2)+"\n")

def _print_table(result):
    print("dev\narm season kind n ll_1x2 rps oull_2_5")
    for r in result: print(f'{r["arm"]} {r["season"]} {r["kind"]} {r["n"]} {r["ll_1x2"]:.6f} {r["rps"]:.6f} {r["oull_2_5"]:.6f}')
