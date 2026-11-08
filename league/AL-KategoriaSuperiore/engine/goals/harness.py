"""G-AL development and virgin harness."""
import csv, json, math
from collections import defaultdict
from datetime import date
from pathlib import Path

from arms import adjusted_lambdas, match_counts
from dc import DC

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data" / "al_matches.csv"
OUT = Path(__file__).resolve().parent
PREDICTIONS = ROOT / "predictions"
SEASONS = ("2021/2022", "2022/2023", "2023/2024", "2024/2025", "2025/2026")
DEV_SCORED = SEASONS[1:]
VIRGIN_SEASON = "2026/2027"
HALF_SPLIT = 0.4267


def load(path=DATA, allowed=None):
    rows = []
    with open(path, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if allowed is not None and r["season"] not in allowed:
                continue
            if r["awarded"].strip().lower() == "true":
                continue
            if r["playoff"].strip().lower() == "true":
                continue
            rows.append({"match_id": r["match_id"], "season": r["season"], "date": date.fromisoformat(r["date"]),
                "hi": int(r["home_team_id"]), "ai": int(r["away_team_id"]), "home": r["home_team"], "away": r["away_team"],
                "yh": int(r["home_goals"]), "ya": int(r["away_goals"]), "xgh": None, "xga": None})
    return sorted(rows, key=lambda r: (r["date"], r["match_id"]))


def _fit(train, target):
    cutoff = min(r["date"] for r in target)
    history = [r for r in train if r["date"] < cutoff]
    return DC().fit(history, cutoff), history, cutoff


def _probs(model, row, arm, counts):
    lh, la = adjusted_lambdas(model, row["hi"], row["ai"], arm, counts=counts)
    return lh, la, model.probs(lh, la)


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


def _trailing10(train, row):
    before = [r for r in train if r["date"] < row["date"]]
    by_team = defaultdict(list)
    for r in before:
        by_team[r["hi"]].append((r["yh"], r["ya"]))
        by_team[r["ai"]].append((r["ya"], r["yh"]))
    mean_g = sum(r["yh"] + r["ya"] for r in before) / max(1, 2 * len(before))
    def means(t):
        vals = by_team.get(t, [])[-10:]
        if len(vals) < 6:
            return mean_g, mean_g
        return sum(x[0] for x in vals) / len(vals), sum(x[1] for x in vals) / len(vals)
    hf, ha = means(row["hi"]); af, aa = means(row["ai"])
    return max(1e-9, (hf + aa) / 2), max(1e-9, (af + ha) / 2)


def _record(arm, season, kind, rows, probs):
    return {"arm": arm, "season": season, "kind": kind, **_scores(rows, probs)}


def _poisson_probs(lh, la):
    model = DC()
    return model.probs(lh, la)


def _pooled(rs):
    n = sum(r["n"] for r in rs)
    return {"n": n, "ll_1x2": sum(r["ll_1x2"] * r["n"] for r in rs) / n,
        "rps": sum(r["rps"] * r["n"] for r in rs) / n,
        "oull_2_5": sum(r["oull_2_5"] * r["n"] for r in rs) / n}


def run_dev():
    rows = load(allowed=set(SEASONS))
    assert not any(r["season"] == VIRGIN_SEASON for r in rows)
    result, pred_rows = [], []
    for season in DEV_SCORED:
        target = [r for r in rows if r["season"] == season]
        train = [r for r in rows if r["date"] < min(x["date"] for x in target)]
        cp, co = _clim(train)
        cprobs = [{"ph": cp[0], "pd": cp[1], "pa": cp[2], "over25": co} for _ in target]
        # Naive trailing-10 uses EVERY match strictly before the target
        # match's date, including earlier matches of the target season
        # itself (the causality contract); `train` above holds only
        # prior seasons and would leave it stale. `_trailing10`
        # filters by date internally, so passing `rows` is safe.
        naive = [_poisson_probs(*_trailing10(rows, r)) for r in target]
        for arm in ("gate_zero", "shrink"):
            result.append(_record(arm, season, "climatology", target, cprobs))
            result.append(_record(arm, season, "naive", target, naive))
        for arm in ("gate_zero", "shrink"):
            model, history, _ = _fit(rows, target); counts = match_counts(history); probs = []
            for r in target:
                lh, la, p = _probs(model, r, arm, counts); probs.append(p)
                pred_rows.append({"match_id": r["match_id"], "season": season, "date": r["date"].isoformat(),
                    "home_team_id": r["hi"], "home_team": r["home"], "away_team_id": r["ai"], "away_team": r["away"],
                    "actual_home_goals": r["yh"], "actual_away_goals": r["ya"], "arm": arm, "lambda_home": lh, "lambda_away": la,
                    "p_home": p["ph"], "p_draw": p["pd"], "p_away": p["pa"], "p_over_2_5": p["over25"],
                    "climatology_p_home": cp[0], "climatology_p_draw": cp[1], "climatology_p_away": cp[2], "climatology_p_over_2_5": co})
            result.append(_record(arm, season, "model", target, probs))
    scored_n = sum(r["n"] for r in result if r["kind"] == "model") // 2
    assert scored_n == 720, f"expected scored n=720, got {scored_n}"
    for arm in ("gate_zero", "shrink"):
        result.append({"arm": arm, "season": "pooled", "kind": "model", **_pooled([r for r in result if r["arm"] == arm and r["kind"] == "model"])})
    for arm in ("gate_zero", "shrink"):
        for kind in ("climatology", "naive"):
            result.append({"arm": arm, "season": "pooled", "kind": kind, **_pooled([r for r in result if r["arm"] == arm and r["kind"] == kind])})
    out = {"protocol": {"league": "AL-KategoriaSuperiore", "dev_seasons_loaded": list(SEASONS), "scored_seasons": list(DEV_SCORED),
        "scored_n": scored_n, "awarded_excluded": True, "playoff_excluded": True, "half_life": 270, "half_split": HALF_SPLIT,
        "sign_convention": "predicted_minus_actual"}, "rows": result}
    _write_dev(out, pred_rows); _print_table(result); return out


def _write_dev(out, pred_rows):
    (OUT / "results_dev.json").write_text(json.dumps(out, indent=2) + "\n")
    fields = ["match_id", "season", "date", "home_team_id", "home_team", "away_team_id", "away_team", "actual_home_goals", "actual_away_goals", "arm", "lambda_home", "lambda_away", "p_home", "p_draw", "p_away", "p_over_2_5", "climatology_p_home", "climatology_p_draw", "climatology_p_away", "climatology_p_over_2_5"]
    with (OUT / "results_dev.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(pred_rows)


def _diff_se(pred, actual):
    e = [p - y for p, y in zip(pred, actual)]; d = sum(e) / len(e)
    return d, (sum((x - d) ** 2 for x in e) / (len(e) - 1)) ** 0.5 / math.sqrt(len(e))


def _leg(status, **values):
    return {"status": status, **values}


def virgin():
    dev = json.loads((OUT / "results_dev.json").read_text())
    def row(arm, season="pooled", kind="model"):
        return next(x for x in dev["rows"] if x["arm"] == arm and x["season"] == season and x["kind"] == kind)
    gz, cl = row("gate_zero"), row("gate_zero", kind="climatology")
    gz_pass = gz["ll_1x2"] < cl["ll_1x2"] and gz["rps"] < cl["rps"] and gz["oull_2_5"] < cl["oull_2_5"]
    if not gz_pass:
        out = {"virgin_read": False, "reason": "gate_zero_failed_dev", "shipped_arm": None, "protocol": {"league": "AL-KategoriaSuperiore", "virgin_season": VIRGIN_SEASON, "n": 55}}
        (OUT / "results_virgin.json").write_text(json.dumps(out, indent=2) + "\n"); return out
    rows = load(allowed=set(SEASONS) | {VIRGIN_SEASON}); target = [r for r in rows if r["season"] == VIRGIN_SEASON]
    assert len(target) == 55, len(target)
    cutoff = min(r["date"] for r in target); train = [r for r in rows if r["date"] < cutoff]; cp, co = _clim(train)
    cprobs = [{"ph": cp[0], "pd": cp[1], "pa": cp[2], "over25": co} for _ in target]; cmet = _scores(target, cprobs)
    passing = [a for a in ("gate_zero", "shrink") if (lambda r: r["ll_1x2"] < cl["ll_1x2"] and r["rps"] < cl["rps"] and r["oull_2_5"] < cl["oull_2_5"])(row(a))]
    out = {"virgin_read": True, "protocol": {"league": "AL-KategoriaSuperiore", "virgin_season": VIRGIN_SEASON, "n": 55, "cutoff": cutoff.isoformat(), "scored_arms": passing}, "arms": {}, "climatology": cmet}
    predsets = {}
    for arm in passing:
        model = DC().fit(train, cutoff); counts = match_counts(train); preds = []; raw = []
        for r in target:
            lh, la, p = _probs(model, r, arm, counts); preds.append(p); raw.append((r, lh, la, p))
        met = _scores(target, preds); hw, hwse = _diff_se([p["ph"] for p in preds], [int(r["yh"] > r["ya"]) for r in target]); ov, ovse = _diff_se([p["over25"] for p in preds], [int(r["yh"] + r["ya"] > 2.5) for r in target])
        sc = sum(row(arm, s)["ll_1x2"] <= row("gate_zero", s)["ll_1x2"] for s in DEV_SCORED)
        def cal(x, se): return "PASS" if abs(x) <= .01 else ("PROVISIONAL PASS" if abs(x) <= .01 + se else "FAIL")
        out["arms"][arm] = {**met, "climatology_ll_1x2": cmet["ll_1x2"], "calibration": {"home_win_diff": hw, "home_win_se": hwse, "over25_diff": ov, "over25_se": ovse}, "dev_sign_count": sc,
            "legs": {"dev_gate": _leg("PASS", pooled=row(arm)), "virgin_ll_vs_gatezero": _leg("PENDING", arm_ll=met["ll_1x2"]), "virgin_ll_vs_climatology": _leg("PASS" if met["ll_1x2"] <= cmet["ll_1x2"] else "FAIL", arm_ll=met["ll_1x2"], climatology_ll=cmet["ll_1x2"]), "calibration_hw": _leg(cal(hw, hwse), diff=hw, se=hwse), "calibration_ou": _leg(cal(ov, ovse), diff=ov, se=ovse), "sign_check": _leg("PASS" if arm == "gate_zero" or sc >= 2 else "FAIL", count=sc, out_of=4)}}
        predsets[arm] = (model, raw)
    for arm in passing:
        leg = out["arms"][arm]["legs"]["virgin_ll_vs_gatezero"]; gll = out["arms"].get("gate_zero", {}).get("ll_1x2"); leg.update({"status": "PASS" if gll is not None and out["arms"][arm]["ll_1x2"] <= gll else ("PENDING" if gll is None else "FAIL"), "gate_zero_ll": gll})
    eligible = [a for a in passing if all(out["arms"][a]["legs"][x]["status"] in ("PASS", "PROVISIONAL PASS") for x in ("dev_gate", "virgin_ll_vs_gatezero", "virgin_ll_vs_climatology", "calibration_hw", "calibration_ou", "sign_check"))]
    shipped = min(eligible, key=lambda a: (out["arms"][a]["ll_1x2"], 0 if a == "gate_zero" else 1)) if eligible else None; out["shipped_arm"] = shipped
    chosen = shipped or "gate_zero"
    if chosen not in predsets:
        model = DC().fit(train, cutoff); counts = match_counts(train); predsets[chosen] = (model, [(r, *_probs(model, r, chosen, counts)) for r in target])
    _write_virgin_predictions(predsets[chosen][0], predsets[chosen][1], chosen, shipped is None)
    model, _ = predsets[chosen]; params = {"arm": chosen, "h": model.h, "rho": model.rho, "mu": model.mu, "cutoff_date": cutoff.isoformat(), "training_n": len(train), "teams": [{"team_id": t, "team_name": model.team_names.get(t) or next((r["home"] if r["hi"] == t else r["away"] for r in target if r["hi"] == t or r["ai"] == t), None), "a": model.a[t], "d": model.d[t], "training_n": counts.get(t, 0)} for t in sorted(set(model.team_names) | {r["hi"] for r in target} | {r["ai"] for r in target})]}
    (OUT / "fitted_params_virgin.json").write_text(json.dumps(params, indent=2) + "\n"); (OUT / "results_virgin.json").write_text(json.dumps(out, indent=2) + "\n"); return out


def _write_virgin_predictions(model, raw, arm, fallback):
    PREDICTIONS.mkdir(exist_ok=True); fields = ["match_id", "date", "season", "home_team_id", "home_team", "away_team_id", "away_team", "arm", "lambda_home", "lambda_away", "p_home", "p_draw", "p_away", "p_over_15", "p_over_25", "p_over_35", "p_btts", "lambda_home_1h", "lambda_away_1h", "p_over_1h_0_5", "p_over_1h_1_5", "p_over_1h_2_5", "lambda_home_2h", "lambda_away_2h", "p_over_2h_1_5", "p_over_2h_2_5", "p_over_2h_3_5", "actual_home_goals", "actual_away_goals"]
    with (PREDICTIONS / "g_al_virgin_predictions.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields); w.writeheader()
        for r, lh, la, p in raw:
            l1h, l1a = HALF_SPLIT * lh, HALF_SPLIT * la; l2h, l2a = (1 - HALF_SPLIT) * lh, (1 - HALF_SPLIT) * la; q1, q2 = model.probs(l1h, l1a), model.probs(l2h, l2a)
            w.writerow({"match_id": r["match_id"], "date": r["date"].isoformat(), "season": r["season"], "home_team_id": r["hi"], "home_team": r["home"], "away_team_id": r["ai"], "away_team": r["away"], "arm": "gate_zero_fallback" if fallback else arm, "lambda_home": lh, "lambda_away": la, "p_home": p["ph"], "p_draw": p["pd"], "p_away": p["pa"], "p_over_15": p["over15"], "p_over_25": p["over25"], "p_over_35": p["over35"], "p_btts": p["btts"], "lambda_home_1h": l1h, "lambda_away_1h": l1a, "p_over_1h_0_5": model.over(l1h, l1a, .5), "p_over_1h_1_5": q1["over15"], "p_over_1h_2_5": q1["over25"], "lambda_home_2h": l2h, "lambda_away_2h": l2a, "p_over_2h_1_5": q2["over15"], "p_over_2h_2_5": q2["over25"], "p_over_2h_3_5": q2["over35"], "actual_home_goals": r["yh"], "actual_away_goals": r["ya"]})


def _print_table(rows):
    print("dev\narm season kind n ll_1x2 rps oull_2_5")
    for r in rows: print(f'{r["arm"]} {r["season"]} {r["kind"]} {r["n"]} {r["ll_1x2"]:.6f} {r["rps"]:.6f} {r["oull_2_5"]:.6f}')
