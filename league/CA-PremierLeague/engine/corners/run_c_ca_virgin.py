import csv
import json
import math
from pathlib import Path

from core import FeatureBuilder, attach_naive, binary_ll, fit_params, load, model_prediction, baseline_prediction, over_prob


HERE = Path(__file__).resolve().parent
DATA = HERE.parents[1] / "data" / "ca_matches.csv"
ALLOWED = {"2021", "2022", "2023", "2024", "2025"}
VIRGIN = "2025"
HALF_FT = 0.466319


def calibration(values, ys):
    diffs = [p - y for p, y in zip(values, ys)]
    mean = sum(diffs) / len(diffs)
    se = math.sqrt(sum((x - mean) ** 2 for x in diffs) / (len(diffs) - 1)) / math.sqrt(len(diffs))
    return mean, se


def run_virgin():
    rows = attach_naive(FeatureBuilder(load(str(DATA), ALLOWED)).build())
    assert all(r["season"] in ALLOWED and int(r["season"]) <= 2025 for r in rows)
    target = [r for r in rows if r["season"] == VIRGIN]
    assert len(target) == 112
    train = [r for r in rows if r["season"] < VIRGIN]
    params = fit_params(train, "gate_zero")
    scored = []
    csv_rows = []
    for r in target:
        mu, rr = model_prediction(r, params, "gate_zero")
        p95 = over_prob(mu, rr, 9.5)
        first = HALF_FT * mu
        second = mu - first
        scored.append((r, p95))
        csv_rows.append({
            "match_id": r["match_id"], "date": r["date"].isoformat(),
            "home_team": r["home"], "away_team": r["away"],
            "actual_corners_home": r["ch"], "actual_corners_away": r["ca"],
            "actual_corners_total": r["y"], "arm": "gate_zero", "mu": mu,
            "r": rr, "gamma": params["gamma"], "beta": params["beta"],
            "p_over_8.5": over_prob(mu, rr, 8.5), "p_over_9.5": p95,
            "p_over_10.5": over_prob(mu, rr, 10.5), "mu_1h": first,
            "p_1h_over_3.5": over_prob(first, rr, 3.5),
            "p_1h_over_4.5": over_prob(first, rr, 4.5),
            "p_1h_over_5.5": over_prob(first, rr, 5.5), "mu_2h": second,
            "p_2h_over_4.5": over_prob(second, rr, 4.5),
            "p_2h_over_5.5": over_prob(second, rr, 5.5),
            "p_2h_over_6.5": over_prob(second, rr, 6.5),
        })

    ys = [int(r["y"] > 9.5) for r, _ in scored]
    base_ps = [over_prob(*baseline_prediction(r, "league_base_rate"), 9.5) for r, _ in scored]
    naive_ps = [over_prob(*baseline_prediction(r, "naive_trailing_10"), 9.5) for r, _ in scored]
    model_ps = [p for _, p in scored]
    results = {"n": len(target), "season": VIRGIN, "arms": {}, "baselines": {}}
    for name, ps in (("gate_zero", model_ps), ("league_base_rate", base_ps), ("naive_trailing_10", naive_ps)):
        cal, se = calibration(ps, ys)
        item = {
            "ll_9.5": sum(binary_ll(p, y) for p, y in zip(ps, ys)) / len(ys),
            "mean_p_over_9.5": sum(ps) / len(ps), "actual_over_9.5": sum(ys) / len(ys),
            "calibration_diff": cal, "calibration_se": se, "n": len(ys),
        }
        if name == "gate_zero":
            item["params"] = params
            results["arms"][name] = item
        else:
            results["baselines"][name] = item

    (HERE / "results_virgin.json").write_text(json.dumps(results, indent=2) + "\n")
    (HERE / "fitted_params_virgin.json").write_text(json.dumps(params, indent=2) + "\n")
    with (HERE / "predictions_virgin_gate_zero.csv").open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(csv_rows[0]))
        writer.writeheader()
        writer.writerows(csv_rows)
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    run_virgin()
