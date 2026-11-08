"""Lane 1 G-TZ-L1 evaluation: dev recomputation, then the single sealed read.

Usage (from the repo root, project python):
    python league/TZ-PremierLeague/engine/goals/run_lane1.py dev
    python league/TZ-PremierLeague/engine/goals/run_lane1.py sealed

`dev` recomputes the season-blocked expanding walk-forward on dev-era
rows only (seed 2021/2022 + 2022/2023-2024/2025), checks the arm of
record (SHRINK) against the persisted original dev artefact via
league/gate_lib, and records the gate_lib dev-pass token only if the
documented dev pass reproduces on all three legs. `sealed` loads the
virgin window (2025/2026) ONCE through the gate_lib fail-closed sealed
loader and computes every sealed leg per PREREG_L1_G_TZ.md. The two
phases are separate invocations on purpose: no sealed row is touched
by the dev phase.
"""
import csv
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]  # repo root
LEAGUE = ROOT / "league" / "TZ-PremierLeague"
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT))

from dc import DC  # noqa: E402
from arms import adjusted_lambdas, match_counts  # noqa: E402
from harness import _scores, _clim, _fit_predict, _trailing_probs, load, DATA, SEED, DEV_FOLDS  # noqa: E402

from league.gate_lib import (  # noqa: E402
    assert_no_sealed_rows,
    calibration,
    calibration_band,
    load_sealed_rows,
    normalise_goals_dev,
    parse_prereg,
    record_dev_pass,
    sign_check,
)

CANDIDATE = "G-TZ-L1"
REGISTRY = HERE / "dev_pass_registry_l1.json"
VIRGIN_SEASON = "2025/2026"
SEALED_SEASONS = {"2025/2026", "2026/2027"}
DOCUMENTED_SHRINK = {"ll_1x2": 0.925501, "rps": 0.180158, "oull_2_5": 0.689404}
DOCUMENTED_CLIM = {"ll_1x2": 1.069080, "rps": 0.223944, "oull_2_5": 0.692720}


def run_dev():
    spec = parse_prereg(LEAGUE / "prereg" / "PREREG_L1_G_TZ.md")
    assert spec.virgin_season == VIRGIN_SEASON, spec
    assert spec.primary_line == 2.5 and not spec.missing_tokens, spec

    # Dev load: raw CSV rows for dev-era seasons only, gate_lib-sealed-checked.
    with open(DATA, newline="", encoding="utf-8") as f:
        raw = list(csv.DictReader(f))
    dev_raw = [r for r in raw if r["season"] in {SEED, *DEV_FOLDS}]
    assert_no_sealed_rows(dev_raw, SEALED_SEASONS)
    assert_no_sealed_rows(raw, set())  # trivially true; loader guard exercised below on dev rows

    rows = load(DATA, {SEED, *DEV_FOLDS})
    result_rows, predictions = [], []
    bites = {}
    for arm in ("gate_zero", "shrink"):
        pooled = {"model": [], "climatology": [], "naive_trailing10": []}
        for season in DEV_FOLDS:
            target = [r for r in rows if r["season"] == season]
            cutoff = min(r["date"] for r in target)
            train = [r for r in rows if r["date"] < cutoff]
            model, counts, _fit = _fit_predict(train, target, arm)
            cp, co = _clim(train)
            mp, np_ = [], []
            changed = 0
            for r in target:
                lh, la = adjusted_lambdas(model, r["hi"], r["ai"], arm, counts=counts)
                p = model.probs(lh, la)
                base = model.probs(*model.lambdas(r["hi"], r["ai"]))
                if any(abs(p[k] - base[k]) > 1e-15 for k in ("ph", "pd", "pa")):
                    changed += 1
                mp.append(p)
                np_.append(_trailing_probs(train, r))
                predictions.append({"match_id": r["match_id"], "season": r["season"], "arm": arm})
            bites.setdefault(season, {})[arm] = changed
            for kind, pp in (("model", mp),
                             ("climatology", [{"ph": cp[0], "pd": cp[1], "pa": cp[2], "over25": co} for _ in target]),
                             ("naive_trailing10", np_)):
                met = _scores(target, pp)
                met.update({"arm": arm, "season": season, "kind": kind})
                result_rows.append(met)
                pooled[kind].extend(zip(target, pp))
        for kind, pp in pooled.items():
            met = _scores([x[0] for x in pp], [x[1] for x in pp])
            met.update({"arm": arm, "season": "pooled", "kind": kind})
            result_rows.append(met)

    recomputed = {"protocol": {"league": "TZ-PremierLeague", "candidate": CANDIDATE,
                               "dev_seasons_loaded": [SEED, *DEV_FOLDS], "scored_n": 720},
                  "rows": result_rows, "shrink_bites": bites}
    (HERE / "results_dev_l1.json").write_text(json.dumps(recomputed, indent=2) + "\n")

    # gate_lib cross-check against the persisted original artefact.
    persisted = normalise_goals_dev(str(HERE / "results_dev.json"))
    fresh = normalise_goals_dev(recomputed)
    max_diff = 0.0
    for key, item in persisted.items():
        other = fresh[key]
        for season, vals in item["seasons"].items():
            for m in ("ll_1x2", "rps", "oull_2_5"):
                max_diff = max(max_diff, abs(vals[m] - other["seasons"][season][m]))
        for m in ("ll_1x2", "rps", "oull_2_5"):
            max_diff = max(max_diff, abs(item["pooled"][m] - other["pooled"][m]))

    def pooled(arm, kind, metric):
        return next(r[metric] for r in result_rows
                    if r["arm"] == arm and r["season"] == "pooled" and r["kind"] == kind)

    shrink = {m: pooled("shrink", "model", m) for m in ("ll_1x2", "rps", "oull_2_5")}
    clim = {m: pooled("shrink", "climatology", m) for m in ("ll_1x2", "rps", "oull_2_5")}
    legs = {"ll_1x2_vs_climatology": shrink["ll_1x2"] < clim["ll_1x2"],
            "rps_vs_climatology": shrink["rps"] < clim["rps"],
            "oull_2_5_vs_base_rate": shrink["oull_2_5"] < clim["oull_2_5"]}
    rounding_ok = all(abs(shrink[m] - DOCUMENTED_SHRINK[m]) < 5e-7 for m in shrink) and \
        all(abs(clim[m] - DOCUMENTED_CLIM[m]) < 5e-7 for m in clim)
    dev_pass = all(legs.values()) and rounding_ok and max_diff < 1e-9
    wins, n_seasons, sign_ok = sign_check(
        [next(r["ll_1x2"] for r in result_rows if r["arm"] == "shrink" and r["season"] == s and r["kind"] == "model") for s in DEV_FOLDS],
        [next(r["ll_1x2"] for r in result_rows if r["arm"] == "gate_zero" and r["season"] == s and r["kind"] == "model") for s in DEV_FOLDS])
    summary = {"candidate": CANDIDATE, "max_abs_diff_vs_persisted": max_diff,
               "shrink_pooled": shrink, "climatology_pooled": clim,
               "dev_legs": legs, "rounding_ok": rounding_ok, "dev_pass": dev_pass,
               "sign_check_dev": {"wins": wins, "n": n_seasons, "pass": sign_ok}}
    (HERE / "dev_check_l1.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))
    if dev_pass:
        record_dev_pass(REGISTRY, CANDIDATE, True, str(HERE / "results_dev_l1.json"))
        print(f"dev-pass token recorded for {CANDIDATE} in {REGISTRY.name}")
    return summary


def _sealed_metrics(rows, probs):
    scored = _scores(rows, probs)
    hw_p = [p["ph"] for p in probs]
    hw_y = [int(r["yh"] > r["ya"]) for r in rows]
    ov_p = [p["over25"] for p in probs]
    ov_y = [int(r["yh"] + r["ya"] > 2.5) for r in rows]
    hw_diff, hw_se = calibration(hw_p, hw_y)  # gate_lib: predicted - actual, pp
    ov_diff, ov_se = calibration(ov_p, ov_y)
    return {**scored,
            "calibration_pred_minus_actual": {
                "home_win_diff_pp": hw_diff, "home_win_se_pp": hw_se,
                "home_win_band": calibration_band(hw_diff, hw_se),
                "over25_diff_pp": ov_diff, "over25_se_pp": ov_se,
                "over25_band": calibration_band(ov_diff, ov_se)}}


def run_sealed():
    # THE single sealed read: virgin rows enter only through the guarded loader.
    # gate_lib's guarded entry point: the dev-pass token is the guard.
    # (Its optional virgin_season argument asserts rows are NOT sealed —
    # a dev-loader check — so the sealed call omits it, as in gate_lib's
    # own tests.)
    sealed_raw = load_sealed_rows(DATA, CANDIDATE, REGISTRY)
    target_raw = [r for r in sealed_raw if r["season"] == VIRGIN_SEASON and r["eligible"] == "1"]
    assert len(target_raw) == 239, len(target_raw)

    rows = load(DATA, {SEED, *DEV_FOLDS, VIRGIN_SEASON})
    target = [r for r in rows if r["season"] == VIRGIN_SEASON]
    assert len(target) == 239
    cutoff = min(r["date"] for r in target)
    train = [r for r in rows if r["date"] < cutoff and r["season"] != VIRGIN_SEASON]

    arm = "shrink"
    model, counts, _fit = _fit_predict(train, target, arm)
    pp = []
    for r in target:
        lh, la = adjusted_lambdas(model, r["hi"], r["ai"], arm, counts=counts)
        p = model.probs(lh, la)
        p["_lambdas"] = (lh, la)
        pp.append(p)
    shrink_metrics = _sealed_metrics(target, pp)

    cp, co = _clim(train)
    cprobs = [{"ph": cp[0], "pd": cp[1], "pa": cp[2], "over25": co} for _ in target]
    clim_metrics = _sealed_metrics(target, cprobs)

    dev = json.loads((HERE / "results_dev_l1.json").read_text())
    wins, n_seasons, sign_ok = sign_check(
        [next(r["ll_1x2"] for r in dev["rows"] if r["arm"] == "shrink" and r["season"] == s and r["kind"] == "model") for s in DEV_FOLDS],
        [next(r["ll_1x2"] for r in dev["rows"] if r["arm"] == "gate_zero" and r["season"] == s and r["kind"] == "model") for s in DEV_FOLDS])

    cal = shrink_metrics["calibration_pred_minus_actual"]
    leg_i = shrink_metrics["ll_1x2"] <= clim_metrics["ll_1x2"]
    leg_ii_parts = {"home_win": cal["home_win_band"], "over25": cal["over25_band"]}
    leg_ii = all(b in ("PASS", "PROVISIONAL") for b in leg_ii_parts.values())
    leg_iii = sign_ok
    if leg_i and leg_ii and leg_iii:
        verdict = "CLEAN PASS" if all(b == "PASS" for b in leg_ii_parts.values()) else "PROVISIONAL PASS"
    else:
        verdict = "FAIL"
    out = {"protocol": {"league": "TZ-PremierLeague", "candidate": CANDIDATE,
                        "virgin_season": VIRGIN_SEASON, "n": len(target),
                        "training_rows": len(train),
                        "sign_convention": "predicted_minus_actual",
                        "arm_of_record": arm},
           "arms": {arm: shrink_metrics},
           "baselines": {"climatology": clim_metrics},
           "legs": {"i_ll_vs_climatology": leg_i, "ii_calibration": leg_ii,
                    "ii_calibration_parts": leg_ii_parts, "iii_dev_sign_check": leg_iii,
                    "sign_wins": wins, "sign_n": n_seasons},
           "verdict": verdict}
    (HERE / "results_virgin_l1.json").write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(out, indent=2))

    if verdict in ("CLEAN PASS", "PROVISIONAL PASS"):
        ppath = LEAGUE / "predictions" / "g_tz_virgin_predictions.csv"
        ppath.parent.mkdir(exist_ok=True)
        fields = ["match_id", "date", "home_team", "away_team", "arm",
                  "lambda_home", "lambda_away", "p_home", "p_draw", "p_away",
                  "p_over_1_5", "p_over_2_5", "p_over_3_5", "p_btts",
                  "lambda_home_1h", "lambda_away_1h", "lambda_home_2h", "lambda_away_2h",
                  "p_over_1h_0_5", "p_over_1h_1_5", "p_over_1h_2_5",
                  "p_over_2h_1_5", "p_over_2h_2_5", "p_over_2h_3_5",
                  "actual_home_goals", "actual_away_goals"]
        with ppath.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=fields)
            w.writeheader()
            for r, p in zip(target, pp):
                lh, la = p["_lambdas"]
                p1 = model.probs(0.4867818118 * lh, 0.4867818118 * la)
                p2 = model.probs(0.5132181882 * lh, 0.5132181882 * la)
                w.writerow({"match_id": r["match_id"], "date": r["date"].isoformat(),
                            "home_team": r["home"], "away_team": r["away"], "arm": arm,
                            "lambda_home": lh, "lambda_away": la,
                            "p_home": p["ph"], "p_draw": p["pd"], "p_away": p["pa"],
                            "p_over_1_5": p["over15"], "p_over_2_5": p["over25"],
                            "p_over_3_5": p["over35"], "p_btts": p["btts"],
                            "lambda_home_1h": 0.4867818118 * lh, "lambda_away_1h": 0.4867818118 * la,
                            "lambda_home_2h": 0.5132181882 * lh, "lambda_away_2h": 0.5132181882 * la,
                            "p_over_1h_0_5": model.over(0.4867818118 * lh, 0.4867818118 * la, 0.5),
                            "p_over_1h_1_5": p1["over15"], "p_over_1h_2_5": p1["over25"],
                            "p_over_2h_1_5": p2["over15"], "p_over_2h_2_5": p2["over25"],
                            "p_over_2h_3_5": p2["over35"],
                            "actual_home_goals": r["yh"], "actual_away_goals": r["ya"]})
        (HERE / "fitted_params_virgin_l1.json").write_text(json.dumps(
            {"arm": arm, "training_rows": len(train), "home_advantage": model.h,
             "rho": model.rho, "mu": model.mu,
             "attack": dict(model.a), "defence": dict(model.d)}, indent=2) + "\n")
        print(f"virgin predictions + fitted params written (arm={arm})")
    return out


if __name__ == "__main__":
    phase = sys.argv[1] if len(sys.argv) > 1 else ""
    if phase == "dev":
        run_dev()
    elif phase == "sealed":
        run_sealed()
    else:
        raise SystemExit("usage: run_lane1.py dev|sealed")
