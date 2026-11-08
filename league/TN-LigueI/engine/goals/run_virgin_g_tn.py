"""Virgin read for the preregistered G-TN goals model.

This runner is intentionally separate from the development harness.  It reads
the source data once, fits only on the frozen expanding window, and writes
artifacts only after every assertion and gate calculation has completed.
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

from dc import (
    DEV_SEASONS,
    RESERVE_SEASON,
    VIRGIN_SEASON,
    WARMUP_SEASON,
    _prediction_row,
    climatology_rows,
    fit_dc,
    league_mean_goals,
    match_counts,
    matrix_from_lambdas,
    metrics,
    predict_matrix,
    probs_1x2_ou,
    shrink_factor,
    Trailing10,
)


HERE = Path(__file__).resolve().parent
DATA = HERE.parents[1] / "data" / "tn_matches.csv"
DEV_RESULTS = HERE / "results_dev.json"
PREDICTION_COLUMNS = [
    "match_id", "date", "home_team", "away_team", "home_goals", "away_goals",
    "lam_h", "lam_a", "rho", "ph", "pd", "pa", "p_over_1_5", "p_over_2_5",
    "p_over_3_5", "p_btts", "lam_h_1h", "lam_a_1h", "p_over_1h_0_5",
    "p_over_1h_1_5", "p_over_1h_2_5", "lam_h_2h", "lam_a_2h",
    "p_over_2h_1_5", "p_over_2h_2_5", "p_over_2h_3_5", "arm",
]
SEASONS = {WARMUP_SEASON, *DEV_SEASONS, VIRGIN_SEASON, RESERVE_SEASON}
TRAIN_COUNTS = {WARMUP_SEASON: 156, "2022/2023": 195,
                "2023/2024": 170, "2024/2025": 237}


def _assert_close(actual, expected, label, tol=1e-9):
    a = np.asarray(actual, dtype=float)
    e = np.asarray(expected, dtype=float)
    assert a.shape == e.shape, (label, a.shape, e.shape)
    assert float(np.max(np.abs(a - e))) <= tol, (label, float(np.max(np.abs(a - e))))


def _fit_params(model, cutoff, n_train):
    return {
        "teams": model["teams"], "attack": model["att"].tolist(),
        "defence": model["def"].tolist(), "home_intercept": model["home"],
        "rho": model["rho"], "train_ll": model["train_ll"],
        "fit_cutoff": pd.Timestamp(cutoff).strftime("%Y-%m-%d"),
        "n_train": n_train,
    }


def _model_lambdas(model, row, counts, arm):
    """Use the engine's prediction primitives, including sanctioned SHRINK."""
    kwargs = {}
    h, a = int(row.home_team_id), int(row.away_team_id)
    if arm == "SHRINK":
        idx = {t: i for i, t in enumerate(model["teams"])}
        fh, fa = shrink_factor(counts, h), shrink_factor(counts, a)
        kwargs = {
            "ah": float(model["att"][idx[h]]) * fh if h in idx else 0.0,
            "dh": float(model["def"][idx[h]]) * fh if h in idx else 0.0,
            "aa": float(model["att"][idx[a]]) * fa if a in idx else 0.0,
            "da": float(model["def"][idx[a]]) * fa if a in idx else 0.0,
        }
    idx = {t: i for i, t in enumerate(model["teams"])}
    ah = float(model["att"][idx[h]]) if "ah" not in kwargs and h in idx else kwargs.get("ah", 0.0)
    dh = float(model["def"][idx[h]]) if "dh" not in kwargs and h in idx else kwargs.get("dh", 0.0)
    aa = float(model["att"][idx[a]]) if "aa" not in kwargs and a in idx else kwargs.get("aa", 0.0)
    da = float(model["def"][idx[a]]) if "da" not in kwargs and a in idx else kwargs.get("da", 0.0)
    return float(np.exp(ah - da + model["home"])), float(np.exp(aa - dh))


def _calibration(rows):
    home_delta = np.asarray([r["p_home"] - (r["home_goals"] > r["away_goals"])
                             for r in rows], dtype=float)
    over_delta = np.asarray([r["p_over25"] - (r["home_goals"] + r["away_goals"] > 2)
                             for r in rows], dtype=float)

    def one(delta):
        mean = float(delta.mean())
        se = float(delta.std(ddof=1) / np.sqrt(len(delta)))
        diff_pp = mean * 100.0
        return {"diff_pp": diff_pp, "se_pp": se * 100.0,
                "abs_diff_pp": abs(diff_pp),
                "boundary_gap_pp": abs(diff_pp) - 1.0}

    return {"home_win_rate": one(home_delta), "ou25_over_rate": one(over_delta)}


def _calibration_verdict(item):
    if item["abs_diff_pp"] <= 1.0:
        return "PASS"
    if item["abs_diff_pp"] <= 1.0 + item["se_pp"]:
        return "PROVISIONAL PASS"
    return "FAIL"


def _prediction_record(model, row, counts, arm, scored_row):
    lh, la = _model_lambdas(model, row, counts, arm)
    rho = float(model["rho"])
    matrix = matrix_from_lambdas(lh, la, rho)
    ph, pd_, pa, over25 = probs_1x2_ou(matrix)
    assert abs(ph - scored_row["p_home"]) <= 1e-9
    assert abs(pd_ - scored_row["p_draw"]) <= 1e-9
    assert abs(pa - scored_row["p_away"]) <= 1e-9
    assert abs(over25 - scored_row["p_over25"]) <= 1e-9

    def over(matrix_, line):
        ks = np.arange(11)
        return float(matrix_[(ks[:, None] + ks[None, :]) > line].sum())

    lh1, la1 = 0.4539 * lh, 0.4539 * la
    lh2, la2 = 0.5461 * lh, 0.5461 * la
    m1 = matrix_from_lambdas(lh1, la1, rho)
    m2 = matrix_from_lambdas(lh2, la2, rho)
    return {
        "match_id": int(row.match_id), "date": row.date.strftime("%Y-%m-%d"),
        "home_team": row.home_team, "away_team": row.away_team,
        "home_goals": int(row.home_goals), "away_goals": int(row.away_goals),
        "lam_h": lh, "lam_a": la, "rho": rho, "ph": ph, "pd": pd_, "pa": pa,
        "p_over_1_5": over(matrix, 1), "p_over_2_5": over25,
        "p_over_3_5": over(matrix, 3),
        "p_btts": float(matrix[1:, 1:].sum()),
        "lam_h_1h": lh1, "lam_a_1h": la1,
        "p_over_1h_0_5": over(m1, 0), "p_over_1h_1_5": over(m1, 1),
        "p_over_1h_2_5": over(m1, 2), "lam_h_2h": lh2, "lam_a_2h": la2,
        "p_over_2h_1_5": over(m2, 1), "p_over_2h_2_5": over(m2, 2),
        "p_over_2h_3_5": over(m2, 3), "arm": "gate_zero" if arm == "GateZero" else "shrink",
    }


def main():
    data = pd.read_csv(DATA, parse_dates=["date"])
    data["season"] = data["season"].astype(str)
    assert set(data.season) == SEASONS, (set(data.season), SEASONS)
    assert data["is_awarded"].isin([0, 1]).all()
    model_data = data[data["is_awarded"] == 0].copy()
    model_data = model_data[model_data.season.isin(SEASONS - {RESERVE_SEASON})].copy()
    assert RESERVE_SEASON not in model_data.season.values
    assert model_data[list(["home_goals", "away_goals", "home_team_id", "away_team_id"])].notna().all().all()
    model_data = model_data.sort_values(["date", "match_id"], kind="mergesort").reset_index(drop=True)

    cutoff = model_data.loc[model_data.season == VIRGIN_SEASON, "date"].min()
    assert pd.notna(cutoff)
    train = model_data[model_data.date < cutoff].copy()
    virgin = model_data[model_data.season == VIRGIN_SEASON].copy()
    assert len(train) == 758, len(train)
    assert len(virgin) == 237, len(virgin)
    assert train.season.isin({WARMUP_SEASON, *DEV_SEASONS}).all()
    assert virgin.season.eq(VIRGIN_SEASON).all()
    assert train.groupby("season").size().to_dict() == TRAIN_COUNTS
    assert len(model_data[model_data.season == RESERVE_SEASON]) == 0

    arms = ("GateZero", "SHRINK")
    models = {arm: fit_dc(train, cutoff) for arm in arms}
    model = models["GateZero"]
    assert np.array_equal(model["teams"], models["SHRINK"]["teams"])
    for key in ("att", "def", "home", "rho", "train_ll"):
        _assert_close(model[key], models["SHRINK"][key], f"fit mismatch {key}")
    counts = match_counts(train)

    arm_rows = {}
    fitted = {}
    for arm in arms:
        arm_rows[arm] = [_prediction_row(models[arm], row, counts, arm)
                         for _, row in virgin.iterrows()]
        fitted[arm] = _fit_params(models[arm], cutoff, len(train))
        assert len(arm_rows[arm]) == 237

    clim_rows = climatology_rows(train, virgin)
    t10 = Trailing10(league_mean_goals(train))
    t10.feed(train)
    naive_rows = t10.rows_for(virgin)
    assert len(clim_rows) == len(naive_rows) == 237
    pooled = {arm: metrics(arm_rows[arm]) for arm in arms}
    clim_metrics, naive_metrics = metrics(clim_rows), metrics(naive_rows)

    dev = json.loads(DEV_RESULTS.read_text())
    dev_gate = {arm: bool(dev["arms"][arm]["gate_dev_pass"]) for arm in arms}
    per_season = dev["arms"]["SHRINK"]["per_season"]
    gz_season = dev["arms"]["GateZero"]["per_season"]
    sign = {season: per_season[season]["ll_1x2"] <= gz_season[season]["ll_1x2"]
            for season in DEV_SEASONS}
    sign_leg = {"seasons": sign, "wins": sum(sign.values()), "required": 2,
                "verdict": "PASS" if sum(sign.values()) >= 2 else "FAIL"}

    arms_out = {}
    for arm in arms:
        cal = _calibration(arm_rows[arm])
        for item in cal.values():
            item["verdict"] = _calibration_verdict(item)
        leg_i = {"ll_1x2": pooled[arm]["ll_1x2"],
                 "gate_zero": pooled["GateZero"]["ll_1x2"],
                 "climatology": clim_metrics["ll_1x2"],
                 "pass": pooled[arm]["ll_1x2"] <= pooled["GateZero"]["ll_1x2"] and
                         pooled[arm]["ll_1x2"] <= clim_metrics["ll_1x2"]}
        leg_ii = {"home_win_rate": cal["home_win_rate"],
                  "ou25_over_rate": cal["ou25_over_rate"],
                  "pass": all(x["verdict"] in ("PASS", "PROVISIONAL PASS") for x in cal.values())}
        leg_iii = {"verdict": "EXEMPT"} if arm == "GateZero" else sign_leg
        arms_out[arm] = {"pooled": pooled[arm], "calibration": cal,
                         "gate_legs": {"i_ll": leg_i, "ii_calibration": leg_ii,
                                       "iii_dev_sign": leg_iii},
                         "gate_dev_pass": dev_gate[arm],
                         "pass": dev_gate[arm] and leg_i["pass"] and leg_ii["pass"] and
                                 (arm == "GateZero" or sign_leg["verdict"] == "PASS")}

    passing = [arm for arm in arms if arms_out[arm]["pass"]]
    winner = "NONE" if not passing else min(passing, key=lambda arm: (pooled[arm]["ll_1x2"], arm != "GateZero"))
    result = {
        "arms": arms_out,
        "climatology": {"pooled": clim_metrics},
        "naive_trailing_10": {"pooled": naive_metrics},
        "winner": winner,
        "meta": {"virgin_season": VIRGIN_SEASON, "n": len(virgin),
                 "fit_cutoff": pd.Timestamp(cutoff).strftime("%Y-%m-%d"), "n_train": len(train)},
    }

    if winner != "NONE":
        csv_rows = [_prediction_record(models[winner], row, counts, winner, arm_rows[winner][i])
                    for i, (_, row) in enumerate(virgin.iterrows())]
        assert len(csv_rows) == 237
        pd.DataFrame(csv_rows, columns=PREDICTION_COLUMNS).to_csv(
            HERE.parents[1] / "predictions" / "g_tn_virgin_predictions.csv", index=False)
    (HERE / "results_virgin.json").write_text(json.dumps(result, indent=1) + "\n")
    (HERE / "fitted_params_virgin.json").write_text(json.dumps(fitted, indent=1) + "\n")


if __name__ == "__main__":
    main()
