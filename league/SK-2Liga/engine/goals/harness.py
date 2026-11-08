"""G-SK2 development and virgin harness."""
import csv
import json
import math
from datetime import date
from pathlib import Path

from dc import DC
from arms import MOVERS, OFFSETS, adjusted_lambdas, match_counts

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data" / "sk2_matches.csv"
OUT = Path(__file__).resolve().parent
SEED = "2021/2022"
DEV_SEASONS = ("2022/2023", "2023/2024", "2024/2025")
VIRGIN = "2025/2026"
HALVES_1H = 0.4940
HALVES_2H = 0.5060
ARMS = ("gate_zero", "shrink", "x2")


def _check_movers(path):
    """Every frozen mover ID must occur in its target season in this CSV."""
    seen = {s: set() for s in MOVERS}
    with path.open(newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            if r["season"] in seen:
                seen[r["season"]].update((int(r["home_team_id"]), int(r["away_team_id"])))
    for season, ids in MOVERS.items():
        assert ids <= seen[season], (season, ids - seen[season])


_check_movers(DATA)


def load(path=DATA, allowed=None):
    rows = []
    with open(path, newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            if allowed is not None and r["season"] not in allowed:
                continue
            rows.append({
                "match_id": r["match_id"], "season": r["season"],
                "date": date.fromisoformat(r["date"]),
                "hi": int(r["home_team_id"]), "ai": int(r["away_team_id"]),
                "home": r["home_team"], "away": r["away_team"],
                "yh": int(r["home_goals"]), "ya": int(r["away_goals"]),
            })
    assert all(r["season"] in allowed for r in rows) if allowed is not None else True
    return sorted(rows, key=lambda r: (r["date"], r["match_id"]))


def _fit_predict(train, target, arm):
    cutoff = min(r["date"] for r in target)
    fit = [r for r in train if r["date"] < cutoff]
    model = DC().fit(fit, cutoff)
    target_season = target[0]["season"]
    movers = MOVERS.get(target_season, set()) & {r["hi"] for r in target} | (MOVERS.get(target_season, set()) & {r["ai"] for r in target})
    if arm != "x2":
        movers = set()
    multipliers = OFFSETS.get(target_season, (0.0, 0.0)) if arm == "x2" else (0.0, 0.0)
    return model, movers, multipliers, match_counts(fit)


def _scores(rows, probs):
    ll = rps = oull = 0.0
    for r, p in zip(rows, probs):
        y = (1, 0, 0) if r["yh"] > r["ya"] else ((0, 1, 0) if r["yh"] == r["ya"] else (0, 0, 1))
        pp = [p["ph"], p["pd"], p["pa"]]
        ll -= math.log(max(pp[y.index(1)], 1e-12))
        rps += 0.5 * ((pp[0] - y[0]) ** 2 + (pp[0] + pp[1] - y[0] - y[1]) ** 2)
        over = r["yh"] + r["ya"] > 2.5
        oull -= math.log(max(p["over25"] if over else 1 - p["over25"], 1e-12))
    n = len(rows)
    return {"n": n, "ll_1x2": ll / n, "rps": rps / n, "oull_2_5": oull / n}


def _clim(train):
    n = len(train)
    hw = sum(r["yh"] > r["ya"] for r in train) / n
    dr = sum(r["yh"] == r["ya"] for r in train) / n
    return [hw, dr, 1 - hw - dr], sum(r["yh"] + r["ya"] > 2.5 for r in train) / n


def _trailing_probs(train, row):
    prior = [r for r in train if r["date"] < row["date"]]
    all_h = [r["yh"] for r in prior]; all_a = [r["ya"] for r in prior]
    mean_h = sum(all_h) / len(all_h); mean_a = sum(all_a) / len(all_a)
    def stats(team):
        games = [r for r in prior if r["hi"] == team or r["ai"] == team][-10:]
        if len(games) < 6:
            return None
        gf = [r["yh"] if r["hi"] == team else r["ya"] for r in games]
        ga = [r["ya"] if r["hi"] == team else r["yh"] for r in games]
        return sum(gf) / len(gf), sum(ga) / len(ga)
    hs, aws = stats(row["hi"]), stats(row["ai"])
    lh = mean_h if hs is None or aws is None else hs[0] * aws[1] / max(mean_a, 1e-9)
    la = mean_a if hs is None or aws is None else aws[0] * hs[1] / max(mean_h, 1e-9)
    model = DC(); model.rho = 0.0
    return model.probs(lh, la)


def _row(met, arm, season, kind):
    return dict(met, arm=arm, season=season, kind=kind)


def _gate(rows, arm):
    get = lambda kind: next(x for x in rows if x["arm"] == arm and x["season"] == "pooled" and x["kind"] == kind)
    model, clim = get("model"), get("climatology")
    return {"ll_1x2": model["ll_1x2"] < clim["ll_1x2"],
            "rps": model["rps"] < clim["rps"],
            "oull_2_5": model["oull_2_5"] < clim["oull_2_5"]}


def run_dev():
    allowed = {SEED, *DEV_SEASONS}
    rows = load(DATA, allowed)
    assert not any(r["season"] in (VIRGIN, "2026/2027") for r in rows)
    result_rows, bites = [], {}
    for arm in ARMS:
        pooled = {"model": [], "climatology": [], "naive_trailing10": []}
        for season in DEV_SEASONS:
            target = [r for r in rows if r["season"] == season]
            train = [r for r in rows if r["date"] < min(x["date"] for x in target)]
            model, movers, mult, counts = _fit_predict(train, target, arm)
            cp, co = _clim(train)
            mp, cprobs, nprobs = [], [], []
            changed = 0; bite_teams = set()
            for r in target:
                gz = model.lambdas(r["hi"], r["ai"])
                lh, la = adjusted_lambdas(model, r["hi"], r["ai"], arm, movers, mult, counts, model.mu)
                if arm == "shrink" and (abs(lh - gz[0]) > 1e-15 or abs(la - gz[1]) > 1e-15):
                    changed += 1
                if 1 <= counts.get(r["hi"], 0) <= 5: bite_teams.add(r["hi"])
                if 1 <= counts.get(r["ai"], 0) <= 5: bite_teams.add(r["ai"])
                mp.append(model.probs(lh, la))
                cprobs.append({"ph": cp[0], "pd": cp[1], "pa": cp[2], "over25": co})
                nprobs.append(_trailing_probs(train, r))
            # bites is recorded from the SHRINK pass only: the dict is
            # shared across arms and later passes would overwrite it
            # with changed_rows=0 (the check below is arm-gated).
            if arm == "shrink":
                bites[season] = {"changed_rows": changed, "target_teams_1_5": len(bite_teams)}
            for kind, probs in (("model", mp), ("climatology", cprobs), ("naive_trailing10", nprobs)):
                result_rows.append(_row(_scores(target, probs), arm, season, kind))
                pooled[kind].extend(zip(target, probs))
        for kind, pairs in pooled.items():
            result_rows.append(_row(_scores([x[0] for x in pairs], [x[1] for x in pairs]), arm, "pooled", kind))
    gates = {arm: _gate(result_rows, arm) for arm in ARMS}
    result = {"protocol": {"league": "SK-2Liga", "seed": SEED, "dev_seasons": list(DEV_SEASONS),
                            "scored_n": sum(sum(r["season"] == s for r in rows) for s in DEV_SEASONS),
                            "primary_line": "OU2.5", "naive_rule": "trailing 10; <6 matches for either team falls back to league mean"},
              "rows": result_rows, "dev_gate": gates,
              "dev_pass": {arm: all(gates[arm].values()) for arm in ARMS}, "shrink_bites": bites}
    _write_dev(result)
    _print_table(result, "dev")
    print("dev_gate", json.dumps(gates, sort_keys=True))
    print("dev_pass", json.dumps(result["dev_pass"], sort_keys=True))
    print("shrink_bites", json.dumps(bites, sort_keys=True))
    return result


def _write_dev(result):
    (OUT / "results_dev.json").write_text(json.dumps(result, indent=2) + "\n")
    fields = ["arm", "season", "kind", "n", "ll_1x2", "rps", "oull_2_5"]
    with (OUT / "results_dev.csv").open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields); writer.writeheader()
        writer.writerows({k: r.get(k) for k in fields} for r in result["rows"])


def _calibration(rows, preds):
    def diff_se(values):
        mean = sum(values) / len(values)
        return mean, (sum((x - mean) ** 2 for x in values) / (len(values) - 1)) ** 0.5 / math.sqrt(len(values))
    hw = [p["ph"] - (r["yh"] > r["ya"]) for r, p in zip(rows, preds)]
    ov = [p["over25"] - (r["yh"] + r["ya"] > 2.5) for r, p in zip(rows, preds)]
    dh, seh = diff_se(hw); do, seo = diff_se(ov)
    return {"home_win_diff": dh, "home_win_se": seh, "over25_diff": do, "over25_se": seo}


def _prediction_rows(rows, preds, model, arm):
    fields = ["match_id", "date", "home_team", "away_team", "home_goals", "away_goals", "lam_h", "lam_a", "rho", "ph", "pd", "pa", "p_over_1_5", "p_over_2_5", "p_over_3_5", "p_btts", "lam_h_1h", "lam_a_1h", "p_over_1h_0_5", "p_over_1h_1_5", "p_over_1h_2_5", "lam_h_2h", "lam_a_2h", "p_over_2h_1_5", "p_over_2h_2_5", "p_over_2h_3_5", "arm"]
    output = []
    for r, p in zip(rows, preds):
        lh, la = p["lh"], p["la"]
        q1 = model.probs(lh * HALVES_1H, la * HALVES_1H)
        q2 = model.probs(lh * HALVES_2H, la * HALVES_2H)
        output.append({"match_id": r["match_id"], "date": r["date"].isoformat(), "home_team": r["home"], "away_team": r["away"], "home_goals": r["yh"], "away_goals": r["ya"], "lam_h": lh, "lam_a": la, "rho": model.rho, "ph": p["ph"], "pd": p["pd"], "pa": p["pa"], "p_over_1_5": p["over15"], "p_over_2_5": p["over25"], "p_over_3_5": p["over35"], "p_btts": p["btts"], "lam_h_1h": lh * HALVES_1H, "lam_a_1h": la * HALVES_1H, "p_over_1h_0_5": model.over(lh * HALVES_1H, la * HALVES_1H, .5), "p_over_1h_1_5": q1["over15"], "p_over_1h_2_5": q1["over25"], "lam_h_2h": lh * HALVES_2H, "lam_a_2h": la * HALVES_2H, "p_over_2h_1_5": q2["over15"], "p_over_2h_2_5": q2["over25"], "p_over_2h_3_5": q2["over35"], "arm": arm})
    return fields, output


def virgin_metrics(arms=ARMS, write_predictions_arm=None):
    rows = load(DATA, {SEED, *DEV_SEASONS, VIRGIN})
    train = [r for r in rows if r["season"] != VIRGIN]
    target = [r for r in rows if r["season"] == VIRGIN]
    cp, co = _clim(train)
    result = {"protocol": {"league": "SK-2Liga", "virgin_season": VIRGIN, "n": len(target), "training_rows": len(train), "halves_constant_1h": HALVES_1H}, "arms": {}, "climatology": None, "naive_trailing10": None, "dev_sign_check": {}}
    cprobs = [{"ph": cp[0], "pd": cp[1], "pa": cp[2], "over25": co} for _ in target]
    naive_probs = [_trailing_probs(train, r) for r in target]
    for arm in arms:
        model, movers, mult, counts = _fit_predict(train, target, arm)
        preds = []
        for r in target:
            lh, la = adjusted_lambdas(model, r["hi"], r["ai"], arm, movers, mult, counts, model.mu)
            p = model.probs(lh, la); p.update({"lh": lh, "la": la}); preds.append(p)
        met = _scores(target, preds)
        met["climatology"] = _scores(target, cprobs)
        met["naive_trailing10"] = _scores(target, naive_probs)
        met["calibration"] = _calibration(target, preds)
        met["params"] = {"a": dict(model.a), "d": dict(model.d), "h": model.h, "rho": model.rho, "mu": model.mu, "movers": sorted(movers), "offsets": list(mult)}
        result["arms"][arm] = met
        if arm != "gate_zero":
            dev_rows = json.loads((OUT / "results_dev.json").read_text())["rows"]
            checks = {s: next(x for x in dev_rows if x["arm"] == arm and x["season"] == s and x["kind"] == "model")["ll_1x2"] <= next(x for x in dev_rows if x["arm"] == "gate_zero" and x["season"] == s and x["kind"] == "model")["ll_1x2"] for s in DEV_SEASONS}
            result["dev_sign_check"][arm] = {"seasons": checks, "count": sum(checks.values()), "required": 2}
        if arm == write_predictions_arm:
            fields, output = _prediction_rows(target, preds, model, arm)
            dest = ROOT / "predictions"; dest.mkdir(exist_ok=True)
            with (dest / "g_sk2_virgin_predictions.csv").open("w", newline="") as fh:
                writer = csv.DictWriter(fh, fieldnames=fields); writer.writeheader(); writer.writerows(output)
            (OUT / "fitted_params_virgin.json").write_text(json.dumps({"a": dict(model.a), "d": dict(model.d), "h": model.h, "rho": model.rho, "mu": model.mu, "arm": arm, "movers": sorted(movers), "offsets": list(mult), "match_counts": dict(counts)}, indent=2) + "\n")
    result["climatology"] = _scores(target, cprobs)
    result["naive_trailing10"] = _scores(target, naive_probs)
    (OUT / "results_virgin.json").write_text(json.dumps(result, indent=2) + "\n")
    return result


def _print_table(data, label):
    print(label)
    print("arm season kind n ll_1x2 rps oull_2_5")
    for r in data["rows"]:
        print(f'{r["arm"]} {r["season"]} {r["kind"]} {r["n"]} {r["ll_1x2"]:.6f} {r["rps"]:.6f} {r["oull_2_5"]:.6f}')
