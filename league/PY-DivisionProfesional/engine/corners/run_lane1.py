"""Lane 1 dev + sealed runner for C-PY-L1.

The sealed path intentionally reproduces the harness virgin construction
without calling ``harness.virgin``: that function refuses Gate Zero because
its persisted dev gate is false, although Gate Zero is only a reported
baseline under this preregistration.
"""
import csv
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT))

import core
import harness
from league.gate_lib import (
    assert_no_sealed_rows,
    calibration,
    calibration_band,
    load_sealed_rows,
    log_loss,
    parse_prereg,
    pooled_ll,
    record_dev_pass,
    sign_check,
)


CANDIDATE = "C-PY-L1"
SEALED_SEASON = "2026 - Clausura"
FROZEN_N = 112
REGISTRY = HERE / "lane1_dev_pass_registry.json"
CSV_PATH = HERE.parents[1] / "data" / "py_matches.csv"
PREREG = HERE.parents[1] / "prereg" / "PREREG_L1_C_PY.md"
DOCUMENTED = {
    "gate_zero": 0.7211,
    "x7": 0.6918,
    "base": 0.7313,
    "naive": 0.7180,
}


def _feature_rows(seasons):
    rows = core.load(CSV_PATH, set(seasons))
    return core.attach_naive(core.FeatureBuilder(rows).build())


def _prediction(row, kind, params=None, arm=None):
    if kind == "model":
        return harness.make_prediction(row, kind, params, arm)
    return harness.make_prediction(row, kind)


def _metric(rows, predictions, season=None):
    pairs = [(r, p) for r, p in zip(rows, predictions) if r["y"] is not None]
    out = {"n": len(pairs)}
    if season is not None:
        out["season"] = season
    for line in (8.5, 9.5, 10.5):
        probs = [p[line] for _, p in pairs]
        actual = [int(r["y"] > line) for r, _ in pairs]
        out[f"ll_{line}"] = sum(log_loss(p, y) for p, y in zip(probs, actual)) / len(pairs)
        out[f"mean_p_{line}"] = sum(probs) / len(probs)
        out[f"actual_over_{line}"] = sum(actual) / len(actual)
    return out


def _dev_block(rows, season, arm, kind):
    target = [r for r in rows if r["season"] == season]
    train = [r for r in rows if r["season"] < season]
    params = core.fit_params(train, arm)
    predictions = [_prediction(r, kind, params, arm) for r in target]
    return _metric(target, predictions, season)


def dev_stage():
    spec = parse_prereg(PREREG)
    assert spec.primary_line == 8.5
    assert spec.calibration_tolerance_pp == 1.0
    assert spec.sign_convention_stated == "predicted_minus_actual"
    assert "league base rate" in spec.baselines
    assert "naive trailing-10" in spec.baselines
    assert not spec.missing_tokens, spec

    rows = _feature_rows(harness.DEV_SEASONS)
    assert_no_sealed_rows(rows, {SEALED_SEASON})

    legs = {}
    per_block_model = {}
    for arm in ("gate_zero", "x7"):
        blocks = {}
        for season in harness.TARGET_SEASONS:
            blocks[season] = {
                kind: _dev_block(rows, season, arm, kind)
                for kind in ("model", "league_base_rate", "naive_trailing_10")
            }
        pooled = {}
        for kind in ("model", "league_base_rate", "naive_trailing_10"):
            pooled[kind] = pooled_ll([
                {"ll": blocks[s][kind]["ll_8.5"], "n": blocks[s][kind]["n"]}
                for s in harness.TARGET_SEASONS
            ])
        legs[arm] = {
            "pooled_ll_8.5": pooled,
            "per_block_ll_8.5": {
                s: {kind: blocks[s][kind]["ll_8.5"] for kind in blocks[s]}
                for s in harness.TARGET_SEASONS
            },
            "blocks": blocks,
        }
        per_block_model[arm] = [
            legs[arm]["per_block_ll_8.5"][s]["model"]
            for s in harness.TARGET_SEASONS
        ]

    wins, n_blocks, sign_ok = sign_check(
        per_block_model["x7"], per_block_model["gate_zero"]
    )
    x7_pooled = legs["x7"]["pooled_ll_8.5"]
    dev_pass = x7_pooled["model"] < x7_pooled["league_base_rate"] and x7_pooled["model"] < x7_pooled["naive_trailing_10"]
    reproduced = {
        "gate_zero": abs(legs["gate_zero"]["pooled_ll_8.5"]["model"] - DOCUMENTED["gate_zero"]) <= 5e-4,
        "x7": abs(x7_pooled["model"] - DOCUMENTED["x7"]) <= 5e-4,
        "base": abs(x7_pooled["league_base_rate"] - DOCUMENTED["base"]) <= 5e-4,
        "naive": abs(x7_pooled["naive_trailing_10"] - DOCUMENTED["naive"]) <= 5e-4,
    }
    record = {
        "candidate": CANDIDATE,
        "stage": "dev",
        "primary_line": 8.5,
        "legs": legs,
        "sign_check_x7_vs_gate_zero": {"wins": wins, "of": n_blocks, "pass": sign_ok},
        "documented_pooled_ll_8.5": DOCUMENTED,
        "reproduced_within_5e-4": reproduced,
        "dev_pass_arm_of_record_x7": dev_pass,
    }
    (HERE / "results_dev_lane1.json").write_text(json.dumps(record, indent=2) + "\n")
    passed = dev_pass and all(reproduced.values())
    if passed:
        record_dev_pass(str(REGISTRY), CANDIDATE, True, str(HERE / "results_dev_lane1.json"))
    print(json.dumps(record, indent=2))
    if not passed:
        print("STOP: dev pass/reproduction failed — no sealed read is authorised.")
    return passed


def sealed_stage():
    raw = load_sealed_rows(str(CSV_PATH), CANDIDATE, str(REGISTRY))
    sealed_raw = [r for r in raw if r["season"] == SEALED_SEASON]
    assert len(sealed_raw) == FROZEN_N, f"frozen sealed cohort n={len(sealed_raw)}"

    rows = _feature_rows(harness.DEV_SEASONS + (SEALED_SEASON,))
    target = [r for r in rows if r["season"] == SEALED_SEASON]
    train = [r for r in rows if r["season"] != SEALED_SEASON]
    assert len(target) == FROZEN_N, f"feature sealed cohort n={len(target)}"

    result = {
        "candidate": CANDIDATE,
        "stage": "sealed",
        "protocol": {"virgin_season": SEALED_SEASON, "frozen_n": FROZEN_N,
                     "single_read_via": "gate_lib.load_sealed_rows"},
        "arms": {},
        "baselines": {},
    }
    params_by_arm = {}
    predictions_by_arm = {}
    for arm in ("gate_zero", "x7"):
        params = core.fit_params(train, arm)
        predictions = [_prediction(r, "model", params, arm) for r in target]
        metric = _metric(target, predictions, SEALED_SEASON)
        probs = [p[8.5] for r, p in zip(target, predictions) if r["y"] is not None]
        actual = [int(r["y"] > 8.5) for r in target if r["y"] is not None]
        diff_pp, se_pp = calibration(probs, actual)
        metric.update({"calibration_diff_pp": diff_pp, "calibration_se_pp": se_pp,
                       "calibration_band": calibration_band(diff_pp, se_pp),
                       "params": params})
        result["arms"][arm] = metric
        params_by_arm[arm] = params
        predictions_by_arm[arm] = predictions

    for kind in ("league_base_rate", "naive_trailing_10"):
        result["baselines"][kind] = _metric(
            target, [_prediction(r, kind) for r in target], SEALED_SEASON
        )

    x7 = result["arms"]["x7"]
    gz = result["arms"]["gate_zero"]
    base = result["baselines"]["league_base_rate"]
    naive = result["baselines"]["naive_trailing_10"]
    dev_record = json.loads((HERE / "results_dev_lane1.json").read_text())
    sign = dev_record["sign_check_x7_vs_gate_zero"]
    result["legs"] = {
        "ll_8.5_x7_le_gate_zero": x7["ll_8.5"] <= gz["ll_8.5"],
        "ll_8.5_x7_le_league_base_rate": x7["ll_8.5"] <= base["ll_8.5"],
        "ll_8.5_x7_le_naive_trailing_10": x7["ll_8.5"] <= naive["ll_8.5"],
        "calibration": x7["calibration_band"],
        "dev_sign_check": sign,
    }
    (HERE / "results_virgin_lane1.json").write_text(json.dumps(result, indent=2) + "\n")

    pred_path = HERE.parents[1] / "predictions" / "c_py_lane1_virgin_predictions.csv"
    pred_path.parent.mkdir(exist_ok=True)
    fields = [
        "match_id", "date", "home_team", "away_team", "actual_corners_home",
        "actual_corners_away", "actual_corners_total", "arm", "mu", "r",
        "gamma", "beta", "p_over_8.5", "p_over_9.5", "p_over_10.5", "mu_1h",
        "p_1h_over_4.5", "p_1h_over_5.5", "p_1h_over_6.5", "mu_2h",
        "p_2h_over_5.5", "p_2h_over_6.5", "p_2h_over_7.5",
    ]
    params = params_by_arm["x7"]
    with pred_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        for row in target:
            mu, r = core.model_prediction(row, params, "x7")
            mu_1h, mu_2h = 0.492 * mu, 0.508 * mu
            out = {
                "match_id": row["match_id"], "date": row["date"].isoformat(),
                "home_team": row["home"], "away_team": row["away"],
                "actual_corners_home": row["ch"], "actual_corners_away": row["ca"],
                "actual_corners_total": row["y"], "arm": "x7", "mu": mu,
                "r": r, "gamma": params["gamma"],
                "beta": json.dumps(params["beta"], separators=(",", ":")),
                "mu_1h": mu_1h, "mu_2h": mu_2h,
            }
            out.update({f"p_over_{line}": core.over_prob(mu, r, line) for line in (8.5, 9.5, 10.5)})
            out.update({f"p_1h_over_{line}": core.over_prob(mu_1h, r, line) for line in (4.5, 5.5, 6.5)})
            out.update({f"p_2h_over_{line}": core.over_prob(mu_2h, r, line) for line in (5.5, 6.5, 7.5)})
            writer.writerow(out)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    stage = sys.argv[1] if len(sys.argv) > 1 else ""
    if stage == "dev":
        dev_stage()
    elif stage == "sealed":
        sealed_stage()
    else:
        raise SystemExit("usage: run_lane1.py dev|sealed")
