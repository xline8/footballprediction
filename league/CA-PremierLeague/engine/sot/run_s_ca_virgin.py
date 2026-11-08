import csv
import json
import math

from harness import DATA, HERE
from model import Engine, LINES, NB_R, load_matches, nb_over


ALLOWED = ("2021", "2022", "2023", "2024", "2025")
VIRGIN = "2025"
HALF_FT = 0.435196


def logloss(p, y):
    p = max(1e-12, min(1.0 - 1e-12, p))
    return -(y * math.log(p) + (1 - y) * math.log(1 - p))


def calibration(values, ys):
    diffs = [p - y for p, y in zip(values, ys)]
    mean = sum(diffs) / len(diffs)
    se = math.sqrt(sum((x - mean) ** 2 for x in diffs) / (len(diffs) - 1)) / math.sqrt(len(diffs))
    return mean, se


def end_state(engine):
    last_day = max(m["day"] for m in engine.matches)
    league = {}
    regression = {}
    for div, dst in engine.reg.divs.items():
        mh, ma = engine.ratings.league_mu(div, last_day)
        league[div] = {"home": mh, "away": ma}
        regression[div] = {
            "teams": dst["teams"],
            "theta": dst["theta"].tolist() if dst["theta"] is not None else None,
        }
    return {"league_means": league, "regression": regression}


def virgin_row(arm, m, p):
    total = p["exp_h"] + p["exp_a"]
    first = HALF_FT * total
    second = total - first
    return {
        "arm": arm,
        "match_id": m["match_id"],
        "date": m["date"].isoformat(),
        "home_team": m["home"],
        "away_team": m["away"],
        "actual_total_sot": m["sot_h"] + m["sot_a"],
        "exp_sot_home": p["exp_h"],
        "exp_sot_away": p["exp_a"],
        "exp_sot_total": total,
        "ft_p_over_7.5": p["probs"][7.5],
        "ft_p_over_8.5": p["probs"][8.5],
        "ft_p_over_9.5": p["probs"][9.5],
        "1h_p_over_2.5": nb_over(first, NB_R, 2.5),
        "1h_p_over_3.5": nb_over(first, NB_R, 3.5),
        "1h_p_over_4.5": nb_over(first, NB_R, 4.5),
        "2h_p_over_3.5": nb_over(second, NB_R, 3.5),
        "2h_p_over_4.5": nb_over(second, NB_R, 4.5),
        "2h_p_over_5.5": nb_over(second, NB_R, 5.5),
    }


def run_virgin():
    rows = load_matches(str(DATA), set(ALLOWED))
    assert all(m["season"] in ALLOWED and int(m["season"]) <= 2025 for m in rows)
    target = [m for m in rows if m["season"] == VIRGIN]
    assert len(target) == 112
    base_rate = sum(m["sot_h"] + m["sot_a"] > 7.5 for m in rows if m["season"] < VIRGIN) / sum(m["season"] < VIRGIN for m in rows)

    results = {"n": len(target), "season": VIRGIN, "arms": {}, "baselines": {}}
    states = {}
    naive_predictions = None
    for arm in ("GZ", "RS"):
        engine = Engine(rows, arm)
        scored = []
        csv_rows = []
        for m in rows:
            p = engine.predict(m)
            if m["season"] == VIRGIN:
                scored.append((m, p))
                csv_rows.append(virgin_row(arm, m, p))
            engine.update(m)
        if arm == "GZ":
            naive_predictions = [(m, p["naive_probs"][7.5]) for m, p in scored]
        states[arm] = end_state(engine)
        ys = [int(m["sot_h"] + m["sot_a"] > 7.5) for m, _ in scored]
        ps = [p["probs"][7.5] for _, p in scored]
        cal, se = calibration(ps, ys)
        results["arms"][arm] = {
            "ll_7.5": sum(logloss(p, y) for p, y in zip(ps, ys)) / len(ys),
            "mean_p_over_7.5": sum(ps) / len(ps),
            "actual_over_7.5": sum(ys) / len(ys),
            "calibration_diff": cal,
            "calibration_se": se,
            "n": len(ys),
        }
        with (HERE / f"predictions_virgin_{arm}.csv").open("w", newline="") as fh:
            fields = list(csv_rows[0])
            writer = csv.DictWriter(fh, fieldnames=fields)
            writer.writeheader()
            writer.writerows(csv_rows)

    ys = [int(m["sot_h"] + m["sot_a"] > 7.5) for m in target]
    base_ps = [base_rate] * len(target)
    naive_ps = [p for _, p in naive_predictions]
    for name, ps in (("league_base_rate", base_ps), ("naive", naive_ps)):
        cal, se = calibration(ps, ys)
        results["baselines"][name] = {
            "ll_7.5": sum(logloss(p, y) for p, y in zip(ps, ys)) / len(ys),
            "mean_p_over_7.5": sum(ps) / len(ps),
            "actual_over_7.5": sum(ys) / len(ys),
            "calibration_diff": cal,
            "calibration_se": se,
            "n": len(ys),
        }

    (HERE / "results_virgin.json").write_text(json.dumps(results, indent=2) + "\n")
    fitted = {
        "arms": ["GZ", "RS"],
        "nb_r": NB_R,
        "league_means": states["GZ"]["league_means"],
        "regression": states["GZ"]["regression"],
        "end_state_by_arm": states,
    }
    (HERE / "fitted_params_virgin.json").write_text(json.dumps(fitted, indent=2) + "\n")
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    run_virgin()
