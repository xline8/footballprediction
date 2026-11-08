"""C-UA harness — written for CN per PREREG_C_CN.md.

core.py is the copied production corners_v3 pattern (with the z_bc
trailing-territorial construction restored to the J1 original — see
the coordinator-correction comment in core.py). Protocol:
- era 2023+ only; per scored season, arm params are fit on prior-season
  walk-forward rows only (core.fit_params), season-blocked;
- dev scored 2024+2025 (n=480); virgin 2026 (n=240) read ONCE, only
  for arms recorded as dev-passing in results_dev.json;
- Arm X7 falls back to the Gate Zero prediction on any match where a
  team's trailing touches are inactive (prereg rule), implemented
  here in predict_arm;
- baselines: league base rate and naive trailing-10 (core.attach_naive).
Calibration = actual - predicted.
"""
import csv, json, math
from pathlib import Path
from core import FeatureBuilder, attach_naive, baseline_prediction, load, model_prediction, over_prob, fit_params

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DATA = ROOT / "data" / "ua_matches.csv"
PRED = ROOT / "predictions" / "c_ua_virgin_predictions.csv"
DEV_SEASONS = ("2022/2023", "2023/2024", "2024/2025")
TARGET_SEASONS = ("2023/2024", "2024/2025")
VIRGIN_SEASON = "2025/2026"
ARMS = ("gate_zero",)  # UA prereg: Gate Zero only (X7 data absent)
LINES = (8.5, 9.5, 10.5)
PRIMARY = 8.5
HALVES_CORNERS_1H = 0.4711


def feature_rows(seasons):
    return attach_naive(FeatureBuilder(load(DATA, set(seasons))).build())


def predict_arm(row, arm, params_by_arm):
    """X7 inactivity rule: where trailing touches are inactive, the
    Gate Zero prediction supplies the forecast (prereg)."""
    if arm == "x7" and not row["both_bt_active"]:
        mu, r = model_prediction(row, params_by_arm["gate_zero"], "gate_zero")
        return mu, r, False
    mu, r = model_prediction(row, params_by_arm[arm], arm)
    return mu, r, True if arm == "x7" else row["both_poss_active"]


def ll(p, y):
    p = min(max(p, 1e-12), 1 - 1e-12)
    return -(y * math.log(p) + (1 - y) * math.log(1 - p))


def metrics(rows, probs_list):
    """probs_list: per-row dict line->prob."""
    n = len(rows)
    vals = {"n": n}
    for line in LINES:
        probs = [p[line] for p in probs_list]
        actual = [int(r["y"] > line) for r in rows]
        vals[f"ll_{line}"] = sum(ll(p, y) for p, y in zip(probs, actual)) / n
        vals[f"mean_p_{line}"] = sum(probs) / n
        vals[f"actual_over_{line}"] = sum(actual) / n
    dif = [int(r["y"] > PRIMARY) - p[PRIMARY] for r, p in zip(rows, probs_list)]
    mean_d = sum(dif) / n
    vals["calibration_diff"] = mean_d
    vals["calibration_se"] = (sum((x - mean_d) ** 2 for x in dif) / (n - 1)) ** 0.5 / n ** 0.5 if n > 1 else 0.0
    return vals


def season_fits(all_rows, target_seasons):
    """Return {season: (target_rows, params_by_arm)} with season-blocked fits."""
    out = {}
    for season in target_seasons:
        target = [r for r in all_rows if r["season"] == season]
        train = [r for r in all_rows if r["season"] < season]
        params = {arm: fit_params(train, arm) for arm in ARMS}
        out[season] = (target, params)
    return out


def arm_probs(target, params, arm):
    return [{line: over_prob(mu, r, line) for line in LINES}
            for mu, r, _ in (predict_arm(row, arm, params) for row in target)]


def baseline_probs(target, kind):
    out = []
    for row in target:
        mu, r = baseline_prediction(row, kind)
        out.append({line: over_prob(mu, r, line) for line in LINES})
    return out


def dev():
    all_rows = feature_rows(DEV_SEASONS)
    fits = season_fits(all_rows, TARGET_SEASONS)
    result = {"protocol": {"league": "UA-PremierLeague", "dev_seasons_loaded": list(DEV_SEASONS),
                           "scored": list(TARGET_SEASONS), "primary_line": PRIMARY,
                           "sign_convention": "actual_minus_predicted"},
              "arms": {}, "baselines": {}}
    pooled_rows = {a: ([], []) for a in ARMS}
    pooled_base = {k: ([], []) for k in ("league_base_rate", "naive_trailing_10")}
    pred_rows = []
    for season in TARGET_SEASONS:
        target, params = fits[season]
        for arm in ARMS:
            probs = arm_probs(target, params, arm)
            result["arms"].setdefault(arm, {})[season] = metrics(target, probs)
            pooled_rows[arm][0].extend(target); pooled_rows[arm][1].extend(probs)
        for kind in pooled_base:
            probs = baseline_probs(target, kind)
            result["baselines"].setdefault(kind, {})[season] = metrics(target, probs)
            pooled_base[kind][0].extend(target); pooled_base[kind][1].extend(probs)
        # audit CSV rows (arm rows carry both baselines at the primary line)
        base_p = baseline_probs(target, "league_base_rate")
        naive_p = baseline_probs(target, "naive_trailing_10")
        for arm in ARMS:
            probs = arm_probs(target, params, arm)
            for row, p, bp, np_ in zip(target, probs, base_p, naive_p):
                mu, r, _act = predict_arm(row, arm, params)
                pred_rows.append({"match_id": row["match_id"], "season": row["season"],
                                  "date": row["date"].isoformat(), "home_team_id": row["home_id"],
                                  "away_team_id": row["away_id"], "home": row["home"], "away": row["away"],
                                  "actual_target": row["y"], "arm": arm, "predicted_mean": mu,
                                  "p_over_8_5": p[8.5], "p_over_9_5": p[9.5], "p_over_10_5": p[10.5],
                                  "baseline_league_p_over_8_5": bp[8.5],
                                  "baseline_naive_p_over_8_5": np_[8.5]})
    for arm in ARMS:
        result["arms"][arm]["pooled"] = metrics(*pooled_rows[arm])
    for kind in pooled_base:
        result["baselines"][kind]["pooled"] = metrics(*pooled_base[kind])
    scored_n = result["arms"]["gate_zero"]["pooled"]["n"]
    assert scored_n == 462, scored_n
    best_base = min(result["baselines"][k]["pooled"][f"ll_{PRIMARY}"] for k in pooled_base)
    result["dev_pass"] = {a: bool(result["arms"][a]["pooled"][f"ll_{PRIMARY}"] < best_base
                                  and result["arms"][a]["pooled"][f"ll_{PRIMARY}"]
                                  < result["baselines"]["naive_trailing_10"]["pooled"][f"ll_{PRIMARY}"]
                                  and result["arms"][a]["pooled"][f"ll_{PRIMARY}"]
                                  < result["baselines"]["league_base_rate"]["pooled"][f"ll_{PRIMARY}"])
                          for a in ARMS}
    if not result["dev_pass"]["gate_zero"]:
        result["dev_pass"] = {a: False for a in ARMS}  # Gate Zero dev failure => variants moot
    result["params_dev"] = {s: fits[s][1] for s in TARGET_SEASONS}
    (HERE / "results_dev.json").write_text(json.dumps(result, indent=2) + "\n")
    fields = ["match_id", "season", "date", "home_team_id", "away_team_id", "home", "away",
              "actual_target", "arm", "predicted_mean", "p_over_8_5", "p_over_9_5", "p_over_10_5",
              "baseline_league_p_over_8_5", "baseline_naive_p_over_8_5"]
    with (HERE / "predictions_dev.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields); w.writeheader(); w.writerows(pred_rows)
    return result


def virgin():
    dev_result = json.loads((HERE / "results_dev.json").read_text())
    passing = [a for a in ARMS if dev_result["dev_pass"].get(a)]
    if not passing:
        raise SystemExit("no dev-passing arm; virgin must NOT be read")
    all_rows = feature_rows(DEV_SEASONS + (VIRGIN_SEASON,))
    target = [r for r in all_rows if r["season"] == VIRGIN_SEASON]
    train = [r for r in all_rows if r["season"] != VIRGIN_SEASON]
    assert len(target) == 223, len(target)
    params = {arm: fit_params(train, arm) for arm in ARMS}
    result = {"protocol": {"league": "UA-PremierLeague", "virgin_season": VIRGIN_SEASON,
                           "n": len(target), "scored_arms": passing, "primary_line": PRIMARY,
                           "sign_convention": "actual_minus_predicted"},
              "arms": {}, "baselines": {}}
    all_probs = {}
    for arm in passing:
        probs = arm_probs(target, params, arm)
        all_probs[arm] = probs
        result["arms"][arm] = metrics(target, probs)
    for kind in ("league_base_rate", "naive_trailing_10"):
        result["baselines"][kind] = metrics(target, baseline_probs(target, kind))
    best_base = min(result["baselines"][k][f"ll_{PRIMARY}"] for k in result["baselines"])
    gz_ll = result["arms"]["gate_zero"][f"ll_{PRIMARY}"] if "gate_zero" in result["arms"] else None
    eligible = []
    for arm in passing:
        v = result["arms"][arm]
        leg_i = (gz_ll is None or v[f"ll_{PRIMARY}"] <= gz_ll) and v[f"ll_{PRIMARY}"] <= best_base
        diff = abs(v["calibration_diff"]); se = v["calibration_se"]
        leg_ii = diff <= 0.01 + se
        v["calibration_status"] = "clean" if diff <= 0.01 else ("provisional" if leg_ii else "fail")
        if arm == "gate_zero":
            leg_iii = True
        else:
            leg_iii = sum(1 for s in TARGET_SEASONS
                          if dev_result["arms"][arm][s][f"ll_{PRIMARY}"]
                          <= dev_result["arms"]["gate_zero"][s][f"ll_{PRIMARY}"]) >= 1
        v["legs"] = {"i_ll": bool(leg_i), "ii_calibration": bool(leg_ii), "iii_sign": bool(leg_iii)}
        if leg_i and leg_ii and leg_iii:
            eligible.append(arm)
    chosen = min(eligible, key=lambda a: (result["arms"][a][f"ll_{PRIMARY}"], ARMS.index(a))) if eligible else None
    result["shipped_arm"] = chosen
    (HERE / "results_virgin.json").write_text(json.dumps(result, indent=2) + "\n")
    (HERE / "fitted_params_virgin.json").write_text(json.dumps(params, indent=2) + "\n")
    base_p = baseline_probs(target, "league_base_rate")
    naive_p = baseline_probs(target, "naive_trailing_10")
    fields = ["match_id", "season", "date", "home_team_id", "away_team_id", "home", "away",
              "actual_target", "arm", "predicted_mean", "p_over_8_5", "p_over_9_5", "p_over_10_5",
              "baseline_league_p_over_8_5", "baseline_naive_p_over_8_5"]
    with (HERE / "predictions_virgin.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields); w.writeheader()
        for arm in passing:
            for row, p, bp, np_ in zip(target, all_probs[arm], base_p, naive_p):
                mu, r, _act = predict_arm(row, arm, params)
                w.writerow({"match_id": row["match_id"], "season": row["season"],
                            "date": row["date"].isoformat(), "home_team_id": row["home_id"],
                            "away_team_id": row["away_id"], "home": row["home"], "away": row["away"],
                            "actual_target": row["y"], "arm": arm, "predicted_mean": mu,
                            "p_over_8_5": p[8.5], "p_over_9_5": p[9.5], "p_over_10_5": p[10.5],
                            "baseline_league_p_over_8_5": bp[8.5],
                            "baseline_naive_p_over_8_5": np_[8.5]})
    if chosen is not None:
        PRED.parent.mkdir(parents=True, exist_ok=True)
        fields2 = ["match_id", "date", "home_team", "away_team", "actual_corners_home",
                   "actual_corners_away", "actual_corners_total", "arm", "mu", "r", "gamma", "beta",
                   "p_over_8.5", "p_over_9.5", "p_over_10.5"]  # UA FT-only: no halves source
        with open(PRED, "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=fields2); w.writeheader()
            for row, p in zip(target, all_probs[chosen]):
                mu, r, _act = predict_arm(row, chosen, params)
                w.writerow({"match_id": row["match_id"], "date": row["date"].isoformat(),
                            "home_team": row["home"], "away_team": row["away"],
                            "actual_corners_home": row["ch"], "actual_corners_away": row["ca"],
                            "actual_corners_total": row["y"], "arm": chosen, "mu": mu, "r": r,
                            "gamma": params[chosen]["gamma"],
                            "beta": json.dumps(params[chosen]["beta"], separators=(",", ":")),
                            "p_over_8.5": p[8.5], "p_over_9.5": p[9.5], "p_over_10.5": p[10.5]})
    return result
