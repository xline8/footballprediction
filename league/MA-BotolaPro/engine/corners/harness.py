import csv,json,math
from datetime import date
from pathlib import Path
from core import FeatureBuilder,attach_naive,load,fit_params,model_prediction,over_prob,binary_ll
HERE=Path(__file__).resolve().parent; DATA=HERE.parents[1]/"data"/"ma_botola_matches.csv"; LINES=(7.5,8.5,9.5)
def dev():
    rows=attach_naive(FeatureBuilder(load(DATA,{"2024/2025"})).build()); rows=[r for r in rows if date(2024,11,1)<=r["date"]<=date(2025,5,12)]
    warm=[r for r in rows if r["date"]<date(2025,1,1)]; target=[r for r in rows if r["date"]>=date(2025,1,1)]; assert len(warm)==55 and len(target)==109
    params=fit_params(warm,"gate_zero")
    def mp(r):
        mu,rr=model_prediction(r,params,"gate_zero"); return mu,rr,{L:over_prob(mu,rr,L) for L in LINES}
    base_mu=sum(r["y"] for r in warm)/len(warm); base_r=max(1.02,min(5.0,sum((r["y"]-base_mu)**2 for r in warm)/max(sum(base_mu for _ in warm),1e-12)))
    hist={}; preds=[]
    for r in target:
        mu,rr,pp=mp(r); naive=(r["naive_home"]+r["naive_away"])/2; preds.append((r,mu,rr,pp,naive))
    def metric(kind):
        vals=[]
        for r,mu,rr,pp,n in preds:
            x=mu if kind=="model" else (base_mu if kind=="league_base_rate" else n); q=rr if kind=="model" else (base_r if kind=="league_base_rate" else r["season_r_base"]); vals.append((r,x,q))
        return {"n":len(vals),**{f"ll_{L}":sum(-(int(r["y"]>L)*math.log(max(over_prob(x,q,L),1e-12))+(1-int(r["y"]>L))*math.log(max(1-over_prob(x,q,L),1e-12))) for r,x,q in vals)/len(vals) for L in LINES},"mean_mu":sum(x for _,x,_ in vals)/len(vals),"actual_mean_total":sum(r["y"] for r,_,_ in vals)/len(vals),"mean_p_8.5":sum(over_prob(x,q,8.5) for _,x,q in vals)/len(vals),"actual_over_8.5":sum(r["y"]>8.5 for r,_,_ in vals)/len(vals)}
    out={"protocol":{"league":"MA-BotolaPro","warmup":"2024-11-01..2024-12-31","window":"2025-01-01..2025-05-12","scored_n":109,"primary_line":8.5,"sign_convention":"actual_minus_predicted","beta_grid":[-0.01,-0.0075,-0.005,-0.0025,0,0.0025,0.005,0.0075,0.01]},"arms":{"gate_zero":metric("model")},"baselines":{"league_base_rate":metric("league_base_rate"),"naive":metric("naive_trailing_10")},"fitted_params":params}
    (HERE/"results_dev.json").write_text(json.dumps(out,indent=2)+"\n")
    with (HERE/"predictions_dev.csv").open("w",newline="") as f:
        fs=["match_id","date","season","arm","actual_target","predicted_mean"]+[f"p_over_{str(L).replace('.','_')}" for L in LINES]; w=csv.DictWriter(f,fieldnames=fs); w.writeheader()
        for r,mu,rr,pp,n in preds: w.writerow({"match_id":r["match_id"],"date":r["date"].isoformat(),"season":r["season"],"arm":"gate_zero","actual_target":r["y"],"predicted_mean":mu,**{f"p_over_{str(L).replace('.','_')}":pp[L] for L in LINES}})
    print(json.dumps(out,indent=2)); return out


def _metric(records):
    out = {"n": len(records)}
    for line in LINES:
        out[f"ll_{line}"] = sum(binary_ll(over_prob(mu, r, line), int(y > line))
                                 for y, mu, r in records) / len(records)
    ps = [over_prob(mu, r, 8.5) for y, mu, r in records]
    ys = [int(y > 8.5) for y, mu, r in records]
    residuals = [y - p for y, p in zip(ys, ps)]
    mean_resid = sum(residuals) / len(residuals)
    out.update({"mean_mu": sum(mu for y, mu, r in records) / len(records),
                "actual_mean_total": sum(y for y, mu, r in records) / len(records),
                "mean_p_over_8.5": sum(ps) / len(ps),
                "actual_over_rate_8.5": sum(ys) / len(ys),
                "calibration": mean_resid,
                "calibration_se": (sum((x - mean_resid) ** 2 for x in residuals) /
                                    len(residuals)) ** 0.5 / (len(residuals) ** 0.5)})
    return out


def virgin():
    """Read the authorized 2025/2026 virgin window exactly once."""
    pre = attach_naive(FeatureBuilder(load(DATA, {"2024/2025"})).build())
    virgin_rows = FeatureBuilder(load(DATA, {"2024/2025", "2025/2026"})).build()
    virgin_rows = attach_naive(virgin_rows)
    pre = [r for r in pre if r["season"] == "2024/2025"]
    target = [r for r in virgin_rows if r["season"] == "2025/2026"]
    assert len(pre) == 172, len(pre)
    assert len(target) == 226, len(target)
    assert all(r["season"] == "2025/2026" for r in target)
    assert not any(r["season"] == "2026/2027" for r in virgin_rows)

    params = fit_params(pre, "gate_zero")
    base_mu = sum(r["y"] for r in pre) / len(pre)
    base_r = max(1.02, min(5.0, sum((r["y"] - base_mu) ** 2 for r in pre) /
                              max(sum(base_mu for _ in pre), 1e-12)))
    records = []
    for r in target:
        mu, rr = model_prediction(r, params, "gate_zero")
        records.append((r["y"], mu, rr))
    # The virgin FeatureBuilder was built over pre-virgin + virgin rows, so all
    # features and the naive tracker above are strictly prior-date state.
    metrics = {"gate_zero": _metric(records)}
    base_records = [(r["y"], base_mu, base_r) for r in target]
    naive_records = [(r["y"], (r["naive_home"] + r["naive_away"]) / 2.0,
                      r["season_r_base"]) for r in target]
    metrics["league_base_rate"] = _metric(base_records)
    metrics["naive"] = _metric(naive_records)
    out = {"protocol": {"league": "MA-BotolaPro", "virgin_season": "2025/2026",
                         "pre_virgin_rows": len(pre), "scored_n": len(target),
                         "primary_line": 8.5, "sign_convention": "actual_minus_predicted"},
           "arms": metrics, "baselines": {"league_base_rate": metrics["league_base_rate"],
                                             "naive": metrics["naive"]},
           "fitted_params": params}
    fields = ["match_id", "date", "season", "arm", "actual_target", "predicted_mean"] + [f"p_over_{str(x).replace('.', '_')}" for x in LINES]
    with (HERE / "predictions_virgin.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields); w.writeheader()
        for r, (_, mu, rr) in zip(target, records):
            w.writerow({"match_id": r["match_id"], "date": r["date"].isoformat(),
                        "season": r["season"], "arm": "gate_zero", "actual_target": r["y"],
                        "predicted_mean": mu, **{f"p_over_{str(x).replace('.', '_')}": over_prob(mu, rr, x) for x in LINES}})
    shipped = HERE.parents[1] / "predictions" / "c_ma_virgin_predictions.csv"
    shipped.parent.mkdir(exist_ok=True)
    shipped.write_text((HERE / "predictions_virgin.csv").read_text())
    fitted = {**params, "market": "corners", "arm": "gate_zero", "pre_virgin_fit_rows": len(pre),
              "league_base_mu": base_mu, "league_base_r": base_r}
    (HERE / "fitted_params_virgin.json").write_text(json.dumps(fitted, indent=2) + "\n")
    (HERE / "results_virgin.json").write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(out, indent=2))
    return out
