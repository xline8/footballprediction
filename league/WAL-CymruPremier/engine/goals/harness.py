"""G-WAL development harness; virgin() is coordinator-controlled and not CLI."""
import csv, json, math
from collections import defaultdict
from datetime import date
from pathlib import Path
from dc import DC
from arms import adjusted_lambdas, match_counts

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data" / "wal_matches.csv"
OUT = Path(__file__).resolve().parent
SEED = "2021/2022"
DEV_FOLDS = ("2022/2023", "2023/2024", "2024/2025")
EXPECTED = {SEED: 192, "2022/2023": 192, "2023/2024": 192, "2024/2025": 192, "2025/2026": 192}
VIRGIN_SEASONS = ("2025/2026",)


def load(path, allowed):
    rows = []
    with open(path, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["season"] not in allowed: continue
            if r["eligible"] != "1": continue
            rows.append({"match_id": r["match_id"], "season": r["season"], "date": date.fromisoformat(r["date"]),
                         "hi": r["home_team_id"], "ai": r["away_team_id"], "home": r["home_team"], "away": r["away_team"],
                         "yh": int(r["home_goals"]), "ya": int(r["away_goals"])})
    assert all(r["season"] in allowed for r in rows)
    if allowed == {SEED, *DEV_FOLDS}:
        assert set(r["season"] for r in rows) == {SEED, *DEV_FOLDS}
    for season in allowed:
        assert sum(r["season"] == season for r in rows) == EXPECTED[season], (season, EXPECTED[season])
    return sorted(rows, key=lambda r: (r["date"], r["match_id"]))


def _scores(rows, probs):
    ll = rps = ou = 0.0
    for r, p in zip(rows, probs):
        y = 0 if r["yh"] > r["ya"] else 1 if r["yh"] == r["ya"] else 2
        pp = [p["ph"], p["pd"], p["pa"]]
        ll -= math.log(max(pp[y], 1e-12))
        obs = [int(y == i) for i in range(3)]
        rps += .5 * ((pp[0] - obs[0]) ** 2 + (pp[0] + pp[1] - obs[0] - obs[1]) ** 2)
        over = r["yh"] + r["ya"] > 2.5
        ou -= math.log(max(p["over25"] if over else 1 - p["over25"], 1e-12))
    n = len(rows)
    return {"n": n, "ll_1x2": ll/n, "rps": rps/n, "oull_2_5": ou/n}


def _clim(train):
    n = len(train); h = sum(r["yh"] > r["ya"] for r in train)/n; d = sum(r["yh"] == r["ya"] for r in train)/n
    return [h, d, 1-h-d], sum(r["yh"] + r["ya"] > 2.5 for r in train)/n


def _fit_predict(train, target, arm):
    cutoff = min(r["date"] for r in target)
    fit = [r for r in train if r["date"] < cutoff]
    model = DC().fit(fit, cutoff)
    return model, match_counts(fit), fit


def _trailing_probs(train, row):
    prior = [r for r in train if r["date"] < row["date"]]
    all_h = [r["yh"] for r in prior]; all_a = [r["ya"] for r in prior]
    mean_h = sum(all_h)/len(all_h); mean_a = sum(all_a)/len(all_a)
    def stats(team, home):
        games = [r for r in prior if r["hi"] == team or r["ai"] == team][-10:]
        if len(games) < 6: return None
        gf = [r["yh"] if r["hi"] == team else r["ya"] for r in games]
        ga = [r["ya"] if r["hi"] == team else r["yh"] for r in games]
        return sum(gf)/len(gf), sum(ga)/len(ga)
    hs, aws = stats(row["hi"], True), stats(row["ai"], False)
    lh = mean_h if hs is None or aws is None else hs[0] * aws[1] / max(mean_a, 1e-9)
    la = mean_a if hs is None or aws is None else aws[0] * hs[1] / max(mean_h, 1e-9)
    m = DC(); m.rho = 0.0
    return m.probs(lh, la)


def _gate(result, arm):
    row = lambda kind: next(x for x in result["rows"] if x["arm"] == arm and x["season"] == "pooled" and x["kind"] == kind)
    m, c = row("model"), row("climatology")
    return {"ll_1x2": m["ll_1x2"] < c["ll_1x2"], "rps": m["rps"] < c["rps"], "oull_2_5": m["oull_2_5"] < c["oull_2_5"]}


def _prediction(r, arm, p, lh, la, cp, co):
    return {"match_id": r["match_id"], "season": r["season"], "date": r["date"].isoformat(), "home": r["home"], "away": r["away"],
            "actual_home_goals": r["yh"], "actual_away_goals": r["ya"], "arm": arm, "lambda_home": lh, "lambda_away": la,
            "p_home": p["ph"], "p_draw": p["pd"], "p_away": p["pa"], "p_over_2_5": p["over25"],
            "baseline_p_home": cp[0], "baseline_p_draw": cp[1], "baseline_p_away": cp[2], "baseline_p_over_2_5": co}


def run_dev():
    rows = load(DATA, {SEED, *DEV_FOLDS})
    assert set(r["season"] for r in rows) == {SEED, *DEV_FOLDS}
    for s in (SEED, *DEV_FOLDS): assert sum(r["season"] == s for r in rows) == EXPECTED[s], (s, EXPECTED[s])
    result_rows, predictions = [], []
    bites = {}
    for arm in ("gate_zero", "shrink"):
        pooled_model, pooled_clim, pooled_naive = [], [], []
        for season in DEV_FOLDS:
            target = [r for r in rows if r["season"] == season]; cutoff = min(r["date"] for r in target)
            train = [r for r in rows if r["date"] < cutoff]
            model, counts, fit = _fit_predict(train, target, arm)
            cp, co = _clim(train); mp, np = [], []
            changed = 0; bite_teams = set()
            for r in target:
                gz = model.probs(*model.lambdas(r["hi"], r["ai"]))
                lh, la = adjusted_lambdas(model, r["hi"], r["ai"], arm, counts=counts)
                p = model.probs(lh, la); base = model.probs(*model.lambdas(r["hi"], r["ai"]))
                if any(abs(p[k] - base[k]) > 1e-15 for k in ("ph", "pd", "pa")): changed += 1
                if 1 <= counts.get(r["hi"], 0) <= 5: bite_teams.add(r["hi"])
                if 1 <= counts.get(r["ai"], 0) <= 5: bite_teams.add(r["ai"])
                mp.append(p); np.append(_trailing_probs(train, r)); predictions.append(_prediction(r, arm, p, lh, la, cp, co))
            bites[season] = {"changed_rows": changed, "target_teams_1_5": len(bite_teams)}
            for kind, pp in (("model", mp), ("climatology", [{"ph":cp[0],"pd":cp[1],"pa":cp[2],"over25":co} for _ in target]), ("naive_trailing10", np)):
                met = _scores(target, pp); met.update({"arm": arm, "season": season, "kind": kind}); result_rows.append(met)
                (pooled_model if kind == "model" else pooled_clim if kind == "climatology" else pooled_naive).extend(zip(target, pp))
        for kind, pp in (("model", pooled_model), ("climatology", pooled_clim), ("naive_trailing10", pooled_naive)):
            met = _scores([x[0] for x in pp], [x[1] for x in pp]); met.update({"arm": arm, "season": "pooled", "kind": kind}); result_rows.append(met)
    result = {"protocol": {"league": "WAL-CymruPremier", "dev_seasons_loaded": [SEED, *DEV_FOLDS], "scored_n": 576,
                            "primary_line": "OU2.5", "eligibility": "eligible=1", "naive_rule": "trailing 10; <6 matches for either team falls back to league mean"},
              "rows": result_rows, "dev_gate": {a: _gate({"rows": result_rows}, a) for a in ("gate_zero", "shrink")}, "shrink_bites": bites}
    (OUT / "results_dev.json").write_text(json.dumps(result, indent=2) + "\n")
    with (OUT / "results_dev.csv").open("w", newline="") as f:
        fields = ["arm", "season", "kind", "n", "ll_1x2", "rps", "oull_2_5"]; w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows({k:r.get(k) for k in fields} for r in result_rows)
    with (OUT / "predictions_dev.csv").open("w", newline="") as f:
        fields = list(predictions[0]); w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(predictions)
    _print_table(result, "dev")
    print("dev_gate", json.dumps(result["dev_gate"], sort_keys=True)); print("shrink_bites", json.dumps(bites, sort_keys=True))
    return result


def _print_table(data, label):
    print(label); print("arm season kind n ll_1x2 rps oull_2_5")
    for r in data["rows"]: print(f'{r["arm"]} {r["season"]} {r["kind"]} {r["n"]} {r["ll_1x2"]:.6f} {r["rps"]:.6f} {r["oull_2_5"]:.6f}')


def _virgin_metrics(rows, probs):
    scored = _scores(rows, probs)
    hw = [int(r["yh"] > r["ya"]) for r in rows]; ov = [int(r["yh"] + r["ya"] > 2.5) for r in rows]
    def diff_se(y, p):
        e = [a - b for a, b in zip(y, p)]; d = sum(e) / len(e)
        return d, (sum((x - d) ** 2 for x in e) / (len(e) - 1)) ** 0.5 / (len(e) ** 0.5)
    dh, seh = diff_se(hw, [p["ph"] for p in probs]); do, seo = diff_se(ov, [p["over25"] for p in probs])
    return {**scored, "calibration": {"home_win_diff": dh, "home_win_se": seh, "over25_diff": do, "over25_se": seo}}


def virgin(requested_arms=None):
    # Gate check FIRST: no virgin label is read unless Gate Zero passed dev.
    dev = json.loads((OUT / "results_dev.json").read_text())
    if not all(_gate(dev, "gate_zero").values()):
        raise RuntimeError("Gate Zero failed the dev gate; virgin evaluation is prohibited")
    dev_pass = {a for a in ("gate_zero", "shrink") if all(_gate(dev, a).values())}
    rows = load(DATA, {SEED, *DEV_FOLDS, *VIRGIN_SEASONS})
    target = [r for r in rows if r["season"] in VIRGIN_SEASONS]
    assert len(target) == 192
    cutoff = min(r["date"] for r in target)
    train = [r for r in rows if r["date"] < cutoff and r["season"] not in VIRGIN_SEASONS]
    passing = [a for a in ("gate_zero", "shrink") if a in dev_pass and (requested_arms is None or a in requested_arms)]
    out = {"protocol": {"league": "WAL-CymruPremier", "virgin_seasons": list(VIRGIN_SEASONS), "n": len(target),
                        "scored_arms": passing, "training_rows": len(train),
                        "sign_convention": "actual_minus_predicted",
                        "halves_constant_goals_1h": 0.4444,
                        "halves_constant_goals_2h": 0.5556}, "arms": {}, "baselines": {}}
    predsets = {}
    for arm in passing:
        model, counts, fit = _fit_predict(train, target, arm)
        pp = []
        for r in target:
            lh, la = adjusted_lambdas(model, r["hi"], r["ai"], arm, counts=counts)
            p = model.probs(lh, la)
            p["_lambdas"] = (lh, la)
            pp.append(p)
        predsets[arm] = (pp, model)
        out["arms"][arm] = _virgin_metrics(target, pp)
    cp, co = _clim(train)
    cprobs = [{"ph": cp[0], "pd": cp[1], "pa": cp[2], "over25": co} for _ in target]
    out["baselines"]["climatology"] = _virgin_metrics(target, cprobs)
    gzll = out["arms"].get("gate_zero", {"ll_1x2": float("inf")})["ll_1x2"]
    climll = out["baselines"]["climatology"]["ll_1x2"]
    eligible = []
    for arm in passing:
        v = out["arms"][arm]
        cal = v["calibration"]
        # Leg (iii): variant LL <= Gate Zero LL in at least half the dev seasons (3 folds -> >= 2).
        sign = arm == "gate_zero" or sum(
            next(x for x in dev["rows"] if x["arm"] == arm and x["season"] == s and x["kind"] == "model")["ll_1x2"]
            <= next(x for x in dev["rows"] if x["arm"] == "gate_zero" and x["season"] == s and x["kind"] == "model")["ll_1x2"]
            for s in DEV_FOLDS) >= 2
        ll_pass = v["ll_1x2"] <= gzll and v["ll_1x2"] <= climll
        cal_pass = abs(cal["home_win_diff"]) <= .01 + cal["home_win_se"] and abs(cal["over25_diff"]) <= .01 + cal["over25_se"]
        out["arms"][arm]["eligibility"] = {
            "ll": ll_pass, "calibration": cal_pass, "dev_fold_sign": sign,
            "provisional_home_win": abs(cal["home_win_diff"]) > .01 and abs(cal["home_win_diff"]) <= .01 + cal["home_win_se"],
            "provisional_over25": abs(cal["over25_diff"]) > .01 and abs(cal["over25_diff"]) <= .01 + cal["over25_se"]}
        if ll_pass and cal_pass and sign:
            eligible.append(arm)
    chosen = min(eligible, key=lambda a: (out["arms"][a]["ll_1x2"], ("gate_zero", "shrink").index(a))) if eligible else None
    out["shipped_arm"] = chosen
    if chosen:
        pp, model = predsets[chosen]
        ppath = OUT.parents[1] / "predictions" / "g_wal_virgin_predictions.csv"
        ppath.parent.mkdir(exist_ok=True)
        with ppath.open("w", newline="", encoding="utf-8") as f:
            fields = ["match_id", "date", "home_team", "away_team", "arm",
                      "lambda_home", "lambda_away", "p_home", "p_draw", "p_away",
                      "p_over_1_5", "p_over_2_5", "p_over_3_5", "p_btts",
                      "lambda_home_1h", "lambda_away_1h", "lambda_home_2h", "lambda_away_2h",
                      "p_over_1h_0_5", "p_over_1h_1_5", "p_over_1h_2_5",
                      "p_over_2h_1_5", "p_over_2h_2_5", "p_over_2h_3_5",
                      "actual_home_goals", "actual_away_goals"]
            w = csv.DictWriter(f, fieldnames=fields)
            w.writeheader()
            for r, p in zip(target, pp):
                lh, la = p["_lambdas"]
                p1 = model.probs(0.4444 * lh, 0.4444 * la)
                p2 = model.probs(0.5556 * lh, 0.5556 * la)
                w.writerow({"match_id": r["match_id"], "date": r["date"].isoformat(), "home_team": r["home"],
                            "away_team": r["away"], "arm": chosen, "lambda_home": lh, "lambda_away": la,
                            "p_home": p["ph"], "p_draw": p["pd"], "p_away": p["pa"],
                            "p_over_1_5": p["over15"], "p_over_2_5": p["over25"], "p_over_3_5": p["over35"],
                            "p_btts": p["btts"],
                            "lambda_home_1h": 0.4444 * lh, "lambda_away_1h": 0.4444 * la,
                            "lambda_home_2h": 0.5556 * lh, "lambda_away_2h": 0.5556 * la,
                            "p_over_1h_0_5": model.over(0.4444 * lh, 0.4444 * la, 0.5),
                            "p_over_1h_1_5": p1["over15"], "p_over_1h_2_5": p1["over25"],
                            "p_over_2h_1_5": p2["over15"], "p_over_2h_2_5": p2["over25"], "p_over_2h_3_5": p2["over35"],
                            "actual_home_goals": r["yh"], "actual_away_goals": r["ya"]})
        (OUT / "fitted_params_virgin.json").write_text(json.dumps(
            {"arm": chosen, "training_rows": len(train), "home_advantage": model.h, "rho": model.rho,
             "mu": model.mu, "attack": dict(model.a), "defence": dict(model.d)}, indent=2) + "\n")
    (OUT / "results_virgin.json").write_text(json.dumps(out, indent=2) + "\n")
    return out
