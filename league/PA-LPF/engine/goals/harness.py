"""Season-blocked PA-LPF development harness and guarded virgin runner."""
import csv, json, math
from collections import defaultdict
from datetime import date
from pathlib import Path

from arms import adjusted_lambdas, match_counts
from dc import DC

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data" / "pa_lpf_matches.csv"
OUT = Path(__file__).resolve().parent
PREDICTIONS = ROOT / "predictions"
SEASONS = ("2023", "2024", "2025")
DEV_SCORED = ("2024", "2025")
VIRGIN_SEASON = "2026"
HALF_SPLIT = 0.449173
AWARDED = {"4399534", "4845610"}


def load(path=DATA, allowed=None):
    rows = []
    with open(path, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if allowed is not None and r["season"] not in allowed:
                continue
            if r["awarded"].strip().lower() == "true" or r["playoff"].strip().lower() == "true":
                continue
            rows.append({"match_id": r["match_id"], "season": r["season"], "date": date.fromisoformat(r["date"]),
                "hi": int(r["home_team_id"]), "ai": int(r["away_team_id"]), "home": r["home_team"], "away": r["away_team"],
                "yh": int(r["home_goals"]), "ya": int(r["away_goals"]), "xgh": None, "xga": None})
    return sorted(rows, key=lambda r: (r["date"], r["match_id"]))


def _scores(rows, probs):
    ll = rps = oull = 0.0
    for r, p in zip(rows, probs):
        outcome = 0 if r["yh"] > r["ya"] else (1 if r["yh"] == r["ya"] else 2)
        pp = [p["ph"], p["pd"], p["pa"]]
        ll -= math.log(max(pp[outcome], 1e-12))
        y0, y1 = (1, 0) if outcome == 0 else ((0, 1) if outcome == 1 else (0, 0))
        rps += 0.5 * ((pp[0] - y0) ** 2 + (pp[0] + pp[1] - y0 - y1) ** 2)
        over = r["yh"] + r["ya"] > 2.5
        oull -= math.log(max(p["over25"] if over else 1 - p["over25"], 1e-12))
    n = len(rows)
    return {"n": n, "ll_1x2": ll / n, "rps": rps / n, "oull_2_5": oull / n}


def _clim(train):
    n = len(train)
    hw = sum(r["yh"] > r["ya"] for r in train) / n
    draw = sum(r["yh"] == r["ya"] for r in train) / n
    return [hw, draw, 1 - hw - draw], sum(r["yh"] + r["ya"] > 2.5 for r in train) / n


def _trailing10(all_rows, row):
    before = [r for r in all_rows if r["date"] < row["date"]]
    by_team = defaultdict(list)
    for r in before:
        by_team[r["hi"]].append((r["yh"], r["ya"]))
        by_team[r["ai"]].append((r["ya"], r["yh"]))
    league_mean = sum(r["yh"] + r["ya"] for r in before) / max(1, 2 * len(before))
    def means(team):
        vals = by_team.get(team, [])[-10:]
        return (league_mean, league_mean) if len(vals) < 6 else (sum(x[0] for x in vals) / len(vals), sum(x[1] for x in vals) / len(vals))
    hf, ha = means(row["hi"]); af, aa = means(row["ai"])
    return max(1e-9, (hf + aa) / 2), max(1e-9, (af + ha) / 2)


def _row_probs(model, row, arm, counts):
    lh, la = adjusted_lambdas(model, row["hi"], row["ai"], arm, counts)
    return lh, la, model.probs(lh, la)


def _pooled(items):
    n = sum(x["n"] for x in items)
    return {"n": n, "ll_1x2": sum(x["ll_1x2"] * x["n"] for x in items) / n,
            "rps": sum(x["rps"] * x["n"] for x in items) / n,
            "oull_2_5": sum(x["oull_2_5"] * x["n"] for x in items) / n}


def _record(arm, season, kind, rows, probs):
    return {"arm": arm, "season": season, "kind": kind, **_scores(rows, probs)}


def run_dev():
    rows = load(allowed=set(SEASONS))
    assert {r["season"] for r in rows} <= set(SEASONS), "DEV loaded a non-DEV season"
    assert not any(r["match_id"] in AWARDED for r in rows)
    result, pred_rows, folds = [], [], []
    for season in DEV_SCORED:
        target = [r for r in rows if r["season"] == season]
        cutoff = min(r["date"] for r in target)
        history = [r for r in rows if r["date"] < cutoff]
        expected_n = {"2024": 120, "2025": 311}[season]
        assert len(history) == expected_n, (season, len(history))
        cp, co = _clim(history)
        clim = [{"ph": cp[0], "pd": cp[1], "pa": cp[2], "over25": co} for _ in target]
        naive = [DC().probs(*_trailing10(rows, r)) for r in target]
        model = DC().fit(history, cutoff)
        counts = match_counts(history)
        target_teams = {r["hi"]: r["home"] for r in target} | {r["ai"]: r["away"] for r in target}
        folds.append({"season": season, "cutoff_date": cutoff.isoformat(), "training_n": len(history), "h": model.h, "rho": model.rho, "mu": model.mu,
                      "prior_count_audit": {str(k): {"team": target_teams[k], "n": counts.get(k, 0)}
                                             for k in sorted(target_teams) if counts.get(k, 0) < 6}})
        for arm in ("gate_zero", "shrink"):
            result.extend((_record(arm, season, "climatology", target, clim), _record(arm, season, "naive", target, naive)))
            probs = []
            for idx, r in enumerate(target):
                lh, la, p = _row_probs(model, r, arm, counts); probs.append(p)
                pred_rows.append({"match_id": r["match_id"], "season": season, "date": r["date"].isoformat(),
                    "home_team_id": r["hi"], "home_team": r["home"], "away_team_id": r["ai"], "away_team": r["away"],
                    "actual_home_goals": r["yh"], "actual_away_goals": r["ya"], "arm": arm, "lam_h": lh, "lam_a": la,
                    "p_home": p["ph"], "p_draw": p["pd"], "p_away": p["pa"], "p_over_2_5": p["over25"],
                    "climatology_p_home": cp[0], "climatology_p_draw": cp[1], "climatology_p_away": cp[2], "climatology_p_over_2_5": co,
                    "naive_p_home": naive[idx]["ph"], "naive_p_draw": naive[idx]["pd"], "naive_p_away": naive[idx]["pa"], "naive_p_over_2_5": naive[idx]["over25"]})
            result.append(_record(arm, season, "model", target, probs))
    scored_n = sum(x["n"] for x in result if x["kind"] == "model") // 2
    assert scored_n == 382, f"expected scored_n == 382, got {scored_n}"
    assert len(pred_rows) == 764
    for arm in ("gate_zero", "shrink"):
        for kind in ("model", "climatology", "naive"):
            result.append({"arm": arm, "season": "pooled", "kind": kind, **_pooled([x for x in result if x["arm"] == arm and x["kind"] == kind])})
    def row(arm, kind):
        return next(x for x in result if x["arm"] == arm and x["season"] == "pooled" and x["kind"] == kind)
    gates = {}
    for arm in ("gate_zero", "shrink"):
        m, c = row(arm, "model"), row(arm, "climatology")
        gates[arm] = {"ll_1x2": {"status": "PASS" if m["ll_1x2"] < c["ll_1x2"] else "FAIL", "model": m["ll_1x2"], "climatology": c["ll_1x2"]},
                      "rps": {"status": "PASS" if m["rps"] < c["rps"] else "FAIL", "model": m["rps"], "climatology": c["rps"]},
                      "ou2_5": {"status": "PASS" if m["oull_2_5"] < c["oull_2_5"] else "FAIL", "model": m["oull_2_5"], "climatology": c["oull_2_5"]}}
    out = {"protocol": {"league": "PA-LPF", "dev_seasons_loaded": list(SEASONS), "scored_seasons": list(DEV_SCORED), "scored_n": scored_n,
        "awarded_excluded": True, "playoff_excluded": True, "half_life": 270, "half_split": HALF_SPLIT, "sign_convention": "predicted_minus_actual"},
        "folds": folds, "rows": result, "dev_gate": gates,
        "shrink_degeneracy": {"equivalent": all(a == b for a, b in zip(
            [{k: v for k, v in x.items() if k != "arm"} for x in pred_rows if x["arm"] == "gate_zero"],
            [{k: v for k, v in x.items() if k != "arm"} for x in pred_rows if x["arm"] == "shrink"])),
            "reason": "all sub-6 prior-count teams are n=0 newcomers"}}
    _write_dev(out, pred_rows)
    for x in result:
        print(f'{x["arm"]} {x["season"]} {x["kind"]} {x["n"]} {x["ll_1x2"]:.6f} {x["rps"]:.6f} {x["oull_2_5"]:.6f}')
    return out


def _write_dev(out, pred_rows):
    (OUT / "results_dev.json").write_text(json.dumps(out, indent=2) + "\n")
    fields = ["match_id", "season", "date", "home_team_id", "home_team", "away_team_id", "away_team", "actual_home_goals", "actual_away_goals", "arm", "lam_h", "lam_a", "p_home", "p_draw", "p_away", "p_over_2_5", "climatology_p_home", "climatology_p_draw", "climatology_p_away", "climatology_p_over_2_5", "naive_p_home", "naive_p_draw", "naive_p_away", "naive_p_over_2_5"]
    with (OUT / "results_dev.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(pred_rows)
    assert (OUT / "results_dev.json").stat().st_size > 0 and (OUT / "results_dev.csv").stat().st_size > 0


def virgin():
    dev = json.loads((OUT / "results_dev.json").read_text())
    gz = next(x for x in dev["rows"] if x["arm"] == "gate_zero" and x["season"] == "pooled" and x["kind"] == "model")
    cl = next(x for x in dev["rows"] if x["arm"] == "gate_zero" and x["season"] == "pooled" and x["kind"] == "climatology")
    if not all(gz[k] < cl[k] for k in ("ll_1x2", "rps", "oull_2_5")):
        marker = {"virgin_read": False, "reason": "gate_zero_failed_dev", "shipped_arm": None}
        (OUT / "results_virgin.json").write_text(json.dumps(marker, indent=2) + "\n")
        return marker
    # This branch is intentionally not run in Phase B. It is the preregistered
    # one-read virgin protocol for the coordinator after DEV verification.
    rows = load(allowed=set(SEASONS) | {VIRGIN_SEASON})
    target = [r for r in rows if r["season"] == VIRGIN_SEASON]
    assert len(target) == 186, len(target)
    cutoff = min(r["date"] for r in target)
    history = [r for r in rows if r["date"] < cutoff]
    cp, co = _clim(history)
    clim = [{"ph": cp[0], "pd": cp[1], "pa": cp[2], "over25": co} for _ in target]
    clim_metrics = _scores(target, clim)
    arm_data, params = {}, {}
    for arm in ("gate_zero", "shrink"):
        model = DC().fit(history, cutoff); counts = match_counts(history)
        raw = [(r, *_row_probs(model, r, arm, counts)) for r in target]
        probs = [x[3] for x in raw]
        metrics = _scores(target, probs)
        hw, hwse = _diff_se([p["ph"] for p in probs], [int(r["yh"] > r["ya"]) for r in target])
        ov, ovse = _diff_se([p["over25"] for p in probs], [int(r["yh"] + r["ya"] > 2.5) for r in target])
        arm_data[arm] = {**metrics, "calibration": {"home_win_diff": hw, "home_win_se": hwse, "over25_diff": ov, "over25_se": ovse},
                         "ll_vs_gate_zero": None, "ll_vs_climatology": metrics["ll_1x2"] <= clim_metrics["ll_1x2"]}
        params[arm] = {"h": model.h, "rho": model.rho, "mu": model.mu, "training_n": len(history), "raw": raw, "model": model, "counts": counts}
    for arm in arm_data:
        arm_data[arm]["ll_vs_gate_zero"] = arm_data[arm]["ll_1x2"] <= arm_data["gate_zero"]["ll_1x2"]
        # Calibration leg per prereg: |diff| <= 1.0pp clean PASS; a breach
        # within 1 SE of the boundary is a PROVISIONAL PASS (counts as pass).
        def _leg(diff, se):
            if abs(diff) <= .01:
                return True, False
            if abs(diff) - .01 <= se:
                return True, True
            return False, False
        hw_ok, hw_prov = _leg(arm_data[arm]["calibration"]["home_win_diff"], arm_data[arm]["calibration"]["home_win_se"])
        ov_ok, ov_prov = _leg(arm_data[arm]["calibration"]["over25_diff"], arm_data[arm]["calibration"]["over25_se"])
        arm_data[arm]["calibration_pass"] = hw_ok and ov_ok
        arm_data[arm]["calibration_provisional"] = (hw_ok and ov_ok) and (hw_prov or ov_prov)
    eligible = [a for a in arm_data if arm_data[a]["ll_vs_gate_zero"] and arm_data[a]["ll_vs_climatology"] and arm_data[a]["calibration_pass"] and (a == "gate_zero" or sum(arm_data[a]["ll_1x2"] <= next(x["ll_1x2"] for x in dev["rows"] if x["arm"] == "gate_zero" and x["season"] == s and x["kind"] == "model") for s in DEV_SCORED) >= 1)]
    shipped = min(eligible, key=lambda a: (arm_data[a]["ll_1x2"], 0 if a == "gate_zero" else 1)) if eligible else None
    chosen = shipped or "gate_zero"
    selected = params[chosen]; _write_virgin_predictions(selected["model"], selected["raw"], chosen)
    fitted = {k: v for k, v in selected.items() if k not in ("raw", "model", "counts")}
    fitted.update({"arm": chosen, "cutoff_date": cutoff.isoformat(), "teams": [{"team_id": t, "a": selected["model"].a[t], "d": selected["model"].d[t], "training_n": selected["counts"].get(t, 0)} for t in sorted(set(selected["model"].team_names) | {r["hi"] for r in target} | {r["ai"] for r in target})]})
    (OUT / "fitted_params_virgin.json").write_text(json.dumps(fitted, indent=2) + "\n")
    out = {"virgin_read": True, "protocol": {"league": "PA-LPF", "virgin_season": VIRGIN_SEASON, "n": len(target), "cutoff": cutoff.isoformat(), "training_n": len(history)},
           "climatology": clim_metrics, "arms": arm_data, "shipped_arm": shipped}
    (OUT / "results_virgin.json").write_text(json.dumps(out, indent=2, default=str) + "\n")
    return out


def _diff_se(pred, actual):
    errors = [p - y for p, y in zip(pred, actual)]
    mean = sum(errors) / len(errors)
    se = (sum((x - mean) ** 2 for x in errors) / (len(errors) - 1)) ** 0.5 / math.sqrt(len(errors))
    return mean, se


def _write_virgin_predictions(model, raw, arm):
    PREDICTIONS.mkdir(exist_ok=True)
    fields = ["match_id", "date", "season", "home_team_id", "home_team", "away_team_id", "away_team", "arm", "lambda_home", "lambda_away", "p_home", "p_draw", "p_away", "p_over_15", "p_over_25", "p_over_35", "p_btts", "lambda_home_1h", "lambda_away_1h", "p_over_1h_0_5", "p_over_1h_1_5", "p_over_1h_2_5", "lambda_home_2h", "lambda_away_2h", "p_over_2h_1_5", "p_over_2h_2_5", "p_over_2h_3_5", "actual_home_goals", "actual_away_goals"]
    path = PREDICTIONS / "g_pa_lpf_virgin_predictions.csv"
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields); w.writeheader()
        for r, lh, la, p in raw:
            l1h, l1a = HALF_SPLIT * lh, HALF_SPLIT * la; l2h, l2a = (1 - HALF_SPLIT) * lh, (1 - HALF_SPLIT) * la
            q1, q2 = model.probs(l1h, l1a), model.probs(l2h, l2a)
            w.writerow({"match_id": r["match_id"], "date": r["date"].isoformat(), "season": r["season"], "home_team_id": r["hi"], "home_team": r["home"], "away_team_id": r["ai"], "away_team": r["away"], "arm": arm, "lambda_home": lh, "lambda_away": la, "p_home": p["ph"], "p_draw": p["pd"], "p_away": p["pa"], "p_over_15": p["over15"], "p_over_25": p["over25"], "p_over_35": p["over35"], "p_btts": p["btts"], "lambda_home_1h": l1h, "lambda_away_1h": l1a, "p_over_1h_0_5": model.over(l1h, l1a, .5), "p_over_1h_1_5": q1["over15"], "p_over_1h_2_5": q1["over25"], "lambda_home_2h": l2h, "lambda_away_2h": l2a, "p_over_2h_1_5": q2["over15"], "p_over_2h_2_5": q2["over25"], "p_over_2h_3_5": q2["over35"], "actual_home_goals": r["yh"], "actual_away_goals": r["ya"]})
