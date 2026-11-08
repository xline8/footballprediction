"""S-MA adapter/harness; mechanics are copied from S-RU model.py."""
import csv, json, math
from datetime import date
from pathlib import Path
from model import Engine, load_matches, NB_R, LINES, nb_over
HERE=Path(__file__).resolve().parent; DATA=HERE.parents[1]/"data"/"ma_botola_matches.csv"
WARM_START,SCORE_START,SCORE_END=date(2024,11,1),date(2025,1,1),date(2025,5,12); ARMS=("GZ","RS")
def load_ma():
    rows=load_matches(DATA,{"2024/2025"}); return [m for m in rows if WARM_START<=m["date"]<=SCORE_END]
def actual(m,L): return float(m["sot_h"]+m["sot_a"]>L)
def ll(p,y): p=max(min(p,1-1e-12),1e-12); return -(y*math.log(p)+(1-y)*math.log(1-p))
def score(rows,arm):
    e=Engine(rows,arm); out=[]
    for m in rows:
        p=e.predict(m)
        if m["date"]>=SCORE_START: out.append((m,p))
        e.update(m)
    return out
def metrics(pairs,fn):
    return {"n":len(pairs),**{f"ll_{L}":sum(ll(fn(m,p,L),actual(m,L)) for m,p in pairs)/len(pairs) for L in LINES},"mean_mu":sum(p["exp_h"]+p["exp_a"] for _,p in pairs)/len(pairs),"actual_mean_total":sum(m["sot_h"]+m["sot_a"] for m,_ in pairs)/len(pairs),"mean_p_7.5":sum(fn(m,p,7.5) for m,p in pairs)/len(pairs),"actual_over_7.5":sum(actual(m,7.5) for m,_ in pairs)/len(pairs)}
def run_dev():
    rows=load_ma(); warm=[m for m in rows if m["date"]<SCORE_START]; assert len(warm)==55; assert sum(m["date"]>=SCORE_START for m in rows)==109
    results={a:score(rows,a) for a in ARMS}; base_mu=sum(m["sot_h"]+m["sot_a"] for m in warm)/len(warm)
    arms={a:metrics(v,lambda m,p,L:p["probs"][L]) for a,v in results.items()}; baselines={"league_base_rate":metrics(results["GZ"],lambda m,p,L:nb_over(base_mu,NB_R,L)),"naive":metrics(results["GZ"],lambda m,p,L:p["naive_probs"][L])}
    out={"protocol":{"league":"MA-BotolaPro","window":"2025-01-01..2025-05-12","warmup":"2024-11-01..2024-12-31","scored_n":109,"primary_line":7.5,"sign_convention":"actual_minus_predicted"},"arms":arms,"baselines":baselines}
    (HERE/"results_dev.json").write_text(json.dumps(out,indent=2)+"\n")
    with (HERE/"predictions_dev.csv").open("w",newline="") as f:
        fs=["match_id","date","season","arm","actual_target","predicted_mean"]+[f"p_over_{str(L).replace('.','_')}" for L in LINES]+["baseline_league_p_over_7_5","baseline_naive_p_over_7_5"]; w=csv.DictWriter(f,fieldnames=fs); w.writeheader()
        for a,ps in results.items():
            for m,p in ps:
                q={"match_id":m["match_id"],"date":m["date"].isoformat(),"season":m["season"],"arm":a,"actual_target":m["sot_h"]+m["sot_a"],"predicted_mean":p["exp_h"]+p["exp_a"],"baseline_league_p_over_7_5":nb_over(base_mu,NB_R,7.5),"baseline_naive_p_over_7_5":p["naive_probs"][7.5]}; q.update({f"p_over_{str(L).replace('.','_')}":p["probs"][L] for L in LINES}); w.writerow(q)
    print(json.dumps(out,indent=2)); return out
