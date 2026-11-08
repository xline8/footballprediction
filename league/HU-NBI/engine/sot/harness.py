import csv, json, math
from pathlib import Path
from model import Engine, load_matches

HERE = Path(__file__).resolve().parent
DATA = HERE.parents[1] / "data" / "hu_nbi.csv"
DEV = ("2021/2022", "2022/2023", "2023/2024", "2024/2025")
SCORED = DEV[1:]
PRIMARY = 8.5

def ll(p, y): return -(y*math.log(max(p,1e-12))+(1-y)*math.log(max(1-p,1e-12)))
def actual(m): return int(m["sot_h"]+m["sot_a"] > PRIMARY)
def metrics(rows, fn):
    return {"n": len(rows), "ll_8.5": sum(ll(fn(m,p), actual(m)) for m,p in rows)/len(rows),
            "per_season": {s: {"n": len(z), "ll_8.5": sum(ll(fn(m,p), actual(m)) for m,p in z)/len(z)} for s in SCORED for z in [[x for x in rows if x[0]["season"] == s]]},
            "mean_predicted_over_rate": sum(fn(m,p) for m,p in rows)/len(rows), "actual_over_rate": sum(actual(m) for m,p in rows)/len(rows)}

def run_dev():
    ms = load_matches(DATA, set(DEV)); assert all(m["season"] in DEV for m in ms)
    out = {"protocol": {"league":"HU-NBI", "dev_seasons_loaded": list(DEV), "virgin_seasons_forbidden":["2025/2026","2026/2027"]}, "primary_line": PRIMARY, "arms": {}, "baselines": {}, "gate": {}}
    allrows = {}
    for arm in ("GZ", "RS"):
        eng = Engine(ms, arm); rows = []
        for m in ms:
            if m["season"] in SCORED: rows.append((m, eng.predict(m)))
            eng.update(m)
        allrows[arm] = rows; out["arms"][arm] = metrics(rows, lambda m,p:p["probs"][PRIMARY])
    rates = {s: sum(actual(x) for x in ms if DEV.index(x["season"]) < DEV.index(s))/sum(DEV.index(x["season"]) < DEV.index(s) for x in ms) for s in SCORED}
    out["baselines"]["base_rate"] = metrics(allrows["GZ"], lambda m,p: rates[m["season"]])
    out["baselines"]["naive_trailing_10"] = metrics(allrows["GZ"], lambda m,p:p["naive_probs"][PRIMARY])
    for arm in allrows:
        out["gate"][arm] = {"pooled_beats_base_rate": out["arms"][arm]["ll_8.5"] < out["baselines"]["base_rate"]["ll_8.5"], "pooled_beats_naive_trailing_10": out["arms"][arm]["ll_8.5"] < out["baselines"]["naive_trailing_10"]["ll_8.5"]}
    (HERE/"results_dev.json").write_text(json.dumps(out, indent=2)+"\n")
    for arm, rows in allrows.items():
        with (HERE/f"dev_predictions_{arm}.csv").open("w",newline="",encoding="utf-8") as fh:
            fields=["match_id","season","date","home_id","away_id","expected","p_over","actual"]
            w=csv.DictWriter(fh,fieldnames=fields); w.writeheader()
            for m,p in rows: w.writerow({"match_id":m["match_id"],"season":m["season"],"date":m["date"].isoformat(),"home_id":m["home"],"away_id":m["away"],"expected":p["exp_h"]+p["exp_a"],"p_over":p["probs"][PRIMARY],"actual":m["sot_h"]+m["sot_a"]})
    return out
