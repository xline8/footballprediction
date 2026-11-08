"""Deterministic G-VN development harness; virgin reader is not run by dev."""
import csv, json, math
from datetime import date
from pathlib import Path
from dc import DC
from arms import adjusted_lambdas, match_counts

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data" / "vn_vleague_matches.csv"
OUT = Path(__file__).resolve().parent
SEED, DEV_SEASONS = "2021", ("2022", "2023", "2023/2024", "2024/2025")
ARMS = ("gate_zero", "shrink")

def load(path=DATA, allowed=None, allow_virgin=False):
    rows = []
    with path.open(newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            season = r["season"]
            if allowed is not None and season not in allowed: continue
            if not allow_virgin:
                assert season != "2025/2026", "season 2025/2026 is forbidden in dev harness"
            rows.append({"match_id": r["match_id"], "season": season,
                         "date": date.fromisoformat(r["date"]), "hi": int(r["home_team_id"]),
                         "ai": int(r["away_team_id"]), "home": r["home_team"], "away": r["away_team"],
                         "yh": int(r["home_goals"]), "ya": int(r["away_goals"])})
    assert all(r["season"] in allowed for r in rows) if allowed is not None else True
    return sorted(rows, key=lambda r: (r["date"], r["match_id"]))

def scores(rows, probs):
    ll = rps = ou = 0.0
    for r, p in zip(rows, probs):
        home = r["yh"] > r["ya"]; draw = r["yh"] == r["ya"]
        pp = [p["ph"], p["pd"], p["pa"]]
        ll -= math.log(max(pp[0 if home else 1 if draw else 2], 1e-12))
        rps += .5 * ((pp[0] - home) ** 2 + (pp[0] + pp[1] - (home or draw)) ** 2)
        over = r["yh"] + r["ya"] > 2.5
        ou -= math.log(max(p["over25"] if over else 1 - p["over25"], 1e-12))
    return {"n": len(rows), "ll_1x2": ll / len(rows), "rps": rps / len(rows), "oull_2_5": ou / len(rows)}

def clim(train):
    n = len(train); hw = sum(r["yh"] > r["ya"] for r in train) / n; dr = sum(r["yh"] == r["ya"] for r in train) / n
    return [hw, dr, 1 - hw - dr], sum(r["yh"] + r["ya"] > 2.5 for r in train) / n

def trailing(train, row):
    prior = [r for r in train if r["date"] < row["date"]]
    mh = sum(r["yh"] for r in prior) / len(prior); ma = sum(r["ya"] for r in prior) / len(prior)
    def stats(team):
        gs = [r for r in prior if r["hi"] == team or r["ai"] == team][-10:]
        if len(gs) < 6: return None
        gf = [r["yh"] if r["hi"] == team else r["ya"] for r in gs]
        ga = [r["ya"] if r["hi"] == team else r["yh"] for r in gs]
        return sum(gf) / len(gs), sum(ga) / len(gs)
    hs, aws = stats(row["hi"]), stats(row["ai"])
    lh = mh if hs is None or aws is None else hs[0] * aws[1] / max(ma, 1e-9)
    la = ma if hs is None or aws is None else aws[0] * hs[1] / max(mh, 1e-9)
    m = DC(); m.rho = 0.0
    return m.probs(lh, la)

def metric(arm, season, kind, rows, probs):
    return dict(scores(rows, probs), arm=arm, season=season, kind=kind)

def run_dev():
    rows = load(DATA, {SEED, *DEV_SEASONS})
    assert not any(r["season"] == "2025/2026" for r in rows)
    metrics, match_rows, bites, fits = [], [], {}, {}
    all_target = []
    for season in DEV_SEASONS:
        target = [r for r in rows if r["season"] == season]; all_target.extend(target)
        cutoff = min(r["date"] for r in target); train = [r for r in rows if r["date"] < cutoff]
        model = DC().fit(train, cutoff); counts = match_counts(train)
        ids = {r["hi"] for r in target} | {r["ai"] for r in target}
        fits[season] = {"cutoff": cutoff.isoformat(), "rho": model.rho, "mu": model.mu,
                        "training_n": len(train)}
        cp, co = clim(train); cprobs = [{"ph": cp[0], "pd": cp[1], "pa": cp[2], "over25": co} for _ in target]
        nprobs = [trailing(train, r) for r in target]
        arm_probs = {a: [] for a in ARMS}; shrink_rows = 0; thin = set()
        for r, cprob, nprob in zip(target, cprobs, nprobs):
            gz = model.lambdas(r["hi"], r["ai"]); out = {"season": season, "date": r["date"].isoformat(), "match_id": r["match_id"],
                "home_team_id": r["hi"], "away_team_id": r["ai"], "home_goals": r["yh"], "away_goals": r["ya"]}
            for arm in ARMS:
                lh, la = adjusted_lambdas(model, r["hi"], r["ai"], arm, counts)
                changed = abs(lh - gz[0]) > 1e-15 or abs(la - gz[1]) > 1e-15
                if arm == "shrink" and changed: shrink_rows += 1
                p = model.probs(lh, la); arm_probs[arm].append(p)
                for k in ("ph", "pd", "pa", "over25"): out[arm + "_" + k] = p[k]
                home = r["yh"] > r["ya"]; draw = r["yh"] == r["ya"]
                out[arm + "_ll_1x2"] = -math.log(max(p["ph"] if home else p["pd"] if draw else p["pa"], 1e-12))
                out[arm + "_rps"] = .5 * ((p["ph"] - home) ** 2 + (p["ph"] + p["pd"] - (home or draw)) ** 2)
                out[arm + "_ll_ou25"] = -math.log(max(p["over25"] if r["yh"] + r["ya"] > 2.5 else 1 - p["over25"], 1e-12))
            if 1 <= counts.get(r["hi"], 0) <= 5: thin.add(r["hi"])
            if 1 <= counts.get(r["ai"], 0) <= 5: thin.add(r["ai"])
            for k in ("ph", "pd", "pa", "over25"): out["climatology_" + k] = cp[0] if k == "ph" else cp[1] if k == "pd" else cp[2] if k == "pa" else co
            home = r["yh"] > r["ya"]; draw = r["yh"] == r["ya"]
            out["climatology_ll_1x2"] = -math.log(max(out["climatology_ph"] if home else out["climatology_pd"] if draw else out["climatology_pa"], 1e-12))
            out["climatology_rps"] = .5 * ((out["climatology_ph"] - home) ** 2 + (out["climatology_ph"] + out["climatology_pd"] - (home or draw)) ** 2)
            out["climatology_ll_ou25"] = -math.log(max(co if r["yh"] + r["ya"] > 2.5 else 1 - co, 1e-12))
            for k in ("ph", "pd", "pa"): out["naive_" + k] = nprob[k]
            out["naive_ll_1x2"] = -math.log(max(nprob["ph"] if home else nprob["pd"] if draw else nprob["pa"], 1e-12))
            out["naive_rps"] = .5 * ((nprob["ph"] - home) ** 2 + (nprob["ph"] + nprob["pd"] - (home or draw)) ** 2)
            out["naive_over25"] = nprob["over25"]
            match_rows.append(out)
        bites[season] = {"shrink_changed_rows": shrink_rows, "shrink_thin_history_teams": len(thin)}
        for arm in ARMS:
            metrics += [metric(arm, season, "model", target, arm_probs[arm]), metric(arm, season, "climatology", target, cprobs), metric(arm, season, "naive_trailing10", target, nprobs)]
    for arm in ARMS:
        for kind in ("model", "climatology", "naive_trailing10"):
            if kind == "model": ps = [{k: r[arm + "_" + k] for k in ("ph", "pd", "pa", "over25")} for r in match_rows]
            elif kind == "climatology": ps = [{k: r["climatology_" + k] for k in ("ph", "pd", "pa", "over25")} for r in match_rows]
            else: ps = [{k: r["naive_" + k] for k in ("ph", "pd", "pa")} | {"over25": r["naive_over25"]} for r in match_rows]
            metrics.append(metric(arm, "pooled", kind, all_target, ps))
    gates = {}
    for arm in ARMS:
        m = next(x for x in metrics if x["arm"] == arm and x["season"] == "pooled" and x["kind"] == "model")
        c = next(x for x in metrics if x["arm"] == arm and x["season"] == "pooled" and x["kind"] == "climatology")
        gates[arm] = {k: {"pass": m[k] < c[k], "arm": m[k], "baseline": c[k]} for k in ("ll_1x2", "rps", "oull_2_5")}
    result = {"protocol": {"league": "VN-VLeague", "seed": SEED, "dev_seasons": list(DEV_SEASONS), "scored_n": len(all_target), "primary_line": "OU2.5", "naive_rule": "trailing 10; <6 matches for either team falls back to league mean"}, "rows": metrics, "dev_gate": gates, "dev_pass": {a: all(x["pass"] for x in gates[a].values()) for a in ARMS}, "fits": fits, "shrink_bites": bites,
              "gate_zero_ou25_vs_climatology": {s: {"gate_zero": next(x for x in metrics if x["arm"] == "gate_zero" and x["season"] == s and x["kind"] == "model")["oull_2_5"], "climatology": next(x for x in metrics if x["arm"] == "gate_zero" and x["season"] == s and x["kind"] == "climatology")["oull_2_5"]} for s in (*DEV_SEASONS, "pooled")}}
    _write(result, match_rows); print(json.dumps({"dev_gate": gates, "bites": bites, "fits": fits}, sort_keys=True)); return result

def _write(result, match_rows):
    def clean(x):
        if isinstance(x, float): return round(x, 4)
        if isinstance(x, dict): return {k: clean(v) for k, v in x.items()}
        if isinstance(x, list): return [clean(v) for v in x]
        return x
    result = clean(result)
    (OUT / "results_dev.json").write_text(json.dumps(result, indent=2) + "\n")
    reason = ("gate zero failed dev gate; virgin not read (variants moot)" if not result["dev_pass"]["gate_zero"]
              else "dev run only; virgin not read")
    (OUT / "results_virgin.json").write_text(json.dumps({"virgin_read": False, "reason": reason}, indent=2) + "\n")
    fields = ["season", "date", "match_id", "home_team_id", "away_team_id", "home_goals", "away_goals"]
    for arm in ARMS: fields += [arm + "_" + k for k in ("ph", "pd", "pa", "over25", "ll_1x2", "rps", "ll_ou25")]
    fields += ["climatology_" + k for k in ("ph", "pd", "pa", "over25", "ll_1x2", "rps", "ll_ou25")]
    fields += ["naive_" + k for k in ("ph", "pd", "pa", "ll_1x2", "rps")]
    with (OUT / "results_dev.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore"); w.writeheader(); w.writerows(clean(match_rows))
    assert all("2025/2026" not in (OUT / name).read_text() for name in ("results_dev.json", "results_dev.csv", "results_virgin.json"))
    assert not any(r["season"] == "2025/2026" for r in match_rows)


def virgin_metrics(arms=("gate_zero", "shrink"), write_predictions_arm=None):
    rows = load(DATA, {SEED, *DEV_SEASONS, "2025/2026"}, allow_virgin=True)
    train = [r for r in rows if r["season"] in {SEED, *DEV_SEASONS}]
    target = [r for r in rows if r["season"] == "2025/2026"]
    assert len(target) == 182, f"prereg mismatch: expected 182 target matches, got {len(target)}"
    cutoff = min(r["date"] for r in target)
    assert cutoff.isoformat() == "2025-08-15", f"prereg mismatch: expected cutoff 2025-08-15, got {cutoff}"
    assert all(r["date"] < cutoff for r in train), "training rows cross the frozen 2025/2026 cutoff"
    cp, co = clim(train)
    cprobs = [{"ph": cp[0], "pd": cp[1], "pa": cp[2], "over25": co} for _ in target]
    result = {"virgin_read": True, "season": "2025/2026", "cutoff": cutoff.isoformat(), "training_n": len(train)}
    for arm in arms:
        model = DC().fit(train, cutoff)
        counts = match_counts(train)
        preds = []
        for r in target:
            lh, la = adjusted_lambdas(model, r["hi"], r["ai"], arm, counts)
            p = model.probs(lh, la); p.update({"lh": lh, "la": la}); preds.append(p)
        met = scores(target, preds)
        cal_hw = sum(p["ph"] for p in preds) / len(preds) - sum(r["yh"] > r["ya"] for r in target) / len(target)
        cal_ou = sum(p["over25"] for p in preds) / len(preds) - sum(r["yh"] + r["ya"] > 2.5 for r in target) / len(target)
        def se(vals):
            m = sum(vals) / len(vals)
            return (sum((x - m) ** 2 for x in vals) / (len(vals) - 1)) ** 0.5 / math.sqrt(len(vals))
        met.update({"climatology": scores(target, cprobs),
                    "calibration": {"home_win_diff": cal_hw, "home_win_se": se([p["ph"] - (r["yh"] > r["ya"]) for p, r in zip(preds, target)]),
                                    "over25_diff": cal_ou, "over25_se": se([p["over25"] - (r["yh"] + r["ya"] > 2.5) for p, r in zip(preds, target)])},
                    "params": {"a": dict(model.a), "d": dict(model.d), "h": model.h, "rho": model.rho, "mu": model.mu}})
        result[arm] = met
        if arm == write_predictions_arm:
            _write_predictions(target, preds, arm, model)
    (OUT / "results_virgin.json").write_text(json.dumps(result, indent=2) + "\n")
    _print_table(result, "virgin")
    return result


def _write_predictions(rows, preds, arm, model):
    dest = ROOT / "predictions"; dest.mkdir(exist_ok=True)
    fields = ["match_id", "date", "home_team", "away_team", "home_goals", "away_goals", "lam_h", "lam_a", "rho", "ph", "pd", "pa", "p_over_1_5", "p_over_2_5", "p_over_3_5", "p_btts", "lam_h_1h", "lam_a_1h", "p_over_1h_0_5", "p_over_1h_1_5", "p_over_1h_2_5", "lam_h_2h", "lam_a_2h", "p_over_2h_1_5", "p_over_2h_2_5", "p_over_2h_3_5", "arm"]
    out = []
    for r, p in zip(rows, preds):
        lh1, la1 = p["lh"] * 0.4468, p["la"] * 0.4468
        lh2, la2 = p["lh"] * 0.5532, p["la"] * 0.5532
        q1, q2 = model.probs(lh1, la1), model.probs(lh2, la2)
        out.append({"match_id": r["match_id"], "date": r["date"].isoformat(), "home_team": r["home"], "away_team": r["away"], "home_goals": r["yh"], "away_goals": r["ya"], "lam_h": p["lh"], "lam_a": p["la"], "rho": model.rho, "ph": p["ph"], "pd": p["pd"], "pa": p["pa"], "p_over_1_5": p["over15"], "p_over_2_5": p["over25"], "p_over_3_5": p["over35"], "p_btts": p["btts"], "lam_h_1h": lh1, "lam_a_1h": la1, "p_over_1h_0_5": model.over(lh1, la1, .5), "p_over_1h_1_5": q1["over15"], "p_over_1h_2_5": q1["over25"], "lam_h_2h": lh2, "lam_a_2h": la2, "p_over_2h_1_5": q2["over15"], "p_over_2h_2_5": q2["over25"], "p_over_2h_3_5": q2["over35"], "arm": arm})
    with (dest / "g_vn_virgin_predictions.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(out)
    (OUT / "fitted_params_virgin.json").write_text(json.dumps({"a": dict(model.a), "d": dict(model.d), "h": model.h, "rho": model.rho, "mu": model.mu, "arm": arm}, indent=2) + "\n")


def _print_table(data, label):
    print(label)
    if label == "dev":
        print("arm season kind n ll_1x2 rps oull_2_5")
        for r in data: print(f'{r["arm"]} {r["season"]} {r["kind"]} {r["n"]} {r["ll_1x2"]:.6f} {r["rps"]:.6f} {r["oull_2_5"]:.6f}')
    else:
        print("arm n ll_1x2 rps oull_2_5 clim_ll calibration_hw calibration_ou")
        for a, r in data.items():
            if a == "virgin_read" or not isinstance(r, dict): continue
            print(f'{a} {r["n"]} {r["ll_1x2"]:.6f} {r["rps"]:.6f} {r["oull_2_5"]:.6f} {r["climatology"]["ll_1x2"]:.6f} {r["calibration"]["home_win_diff"]:.6f} {r["calibration"]["over25_diff"]:.6f}')

if __name__ == "__main__": run_dev()
