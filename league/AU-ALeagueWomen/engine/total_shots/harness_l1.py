"""Lane 1 corrected harness for T-AUW (PREREG_L1_T_AUW).

Reproduces the shipped harness.py walk-forward verbatim, with the
sole change that M_BAR is derived from this league's own dev rows
via league/gate_lib (derive_level_prior) and wired into model_l1
(LevelLayer / TrailingR) instead of the copied 24.9.

Modes:
  dev    — dev-era rows only (sealed guard asserted); writes
           results_dev_l1.json + predictions_dev_l1.csv and records
           the dev-pass token in dev_pass_registry_l1.json.
  virgin — ONE sealed read: requires the recorded dev-pass token,
           loads rows through gate_lib load_sealed_rows, continues
           the same walk-forward into 2025/2026 and scores it.
"""
import csv
import json
import math
import sys
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from gate_lib import (  # noqa: E402
    assert_no_sealed_rows,
    calibration,
    calibration_band,
    derive_level_prior,
    load_sealed_rows,
    log_loss,
    record_dev_pass,
    sign_check,
)
import model_l1  # noqa: E402
from model_l1 import (  # noqa: E402
    BaseRateTracker,
    LevelLayer,
    NaiveTracker,
    ShotsRegressionStore,
    TrailingR,
    nb_over,
)

DATA = HERE.parents[1] / "data" / "auw_matches.csv"
SEASONS = ("2021/2022", "2022/2023", "2023/2024", "2024/2025")
TARGETS = SEASONS[1:]
VIRGIN = "2025/2026"
LINE = 27.5
CANDIDATE = "L1-T-AUW"
REGISTRY = HERE / "dev_pass_registry_l1.json"
SHIPPED_M_BAR = 24.9
EXPECTED_M_BAR = 27.678815489749432
ARMS = ("A", "B", "C", "baseline_league", "baseline_naive")


def _parse(r):
    d = date.fromisoformat(r["date"])
    return {
        "match_id": r["match_id"], "season": r["season"], "date": r["date"],
        "day": d.toordinal(), "home_id": int(r["home_team_id"]),
        "away_id": int(r["away_team_id"]), "home": r["home_team"],
        "away": r["away_team"], "shots_h": float(r["home_total_shots"]),
        "shots_a": float(r["away_total_shots"]),
    }


def load_dev():
    out, raw = [], []
    with DATA.open(newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["season"] not in SEASONS or r["phase"] != "regular":
                continue
            if r["home_total_shots"] == "" or r["away_total_shots"] == "":
                continue
            raw.append(r)
            out.append(_parse(r))
    assert_no_sealed_rows(raw, {VIRGIN, "2026/2027"})
    assert_no_sealed_rows(out, {VIRGIN, "2026/2027"})
    out = sorted(out, key=lambda x: (x["day"], x["match_id"]))
    assert len(out) == 439, len(out)
    return out


def walk(rows, scored_seasons):
    """The shipped harness's single walk-forward pass, verbatim logic.

    scores only rows whose season is in scored_seasons.
    """
    model_l1.set_m_bar(derive_level_prior(
        [x["shots_h"] + x["shots_a"] for x in rows
         if x["season"] in SEASONS]))
    # Predictions are computed for every non-warm-up season (the
    # shipped rule for the level layer's update input); only
    # scored_seasons rows are recorded. In dev mode the two sets
    # coincide, reproducing the shipped harness exactly.
    predict_seasons = set(TARGETS) | set(scored_seasons)
    pred = []
    reg = ShotsRegressionStore(rows, [3, 10, 30, 100, 300])
    naive = NaiveTracker()
    base = BaseRateTracker()
    layer = LevelLayer([(60, 1.0, 50)])
    trail = TrailingR(40)
    for m in rows:
        if m["season"] in predict_seasons:
            eh, ea = reg.predict(m["home_id"], m["away_id"], m["day"], 30)
            rh, ra = reg.league_mu(m["day"], 30)
            nh, na = naive.predict(m["home_id"], m["away_id"], rh, ra)
            bh, ba = base.predict(m["day"])
            lt, ln, lb = eh + ea, nh + na, bh + ba
            f = layer.factor(0, m["day"])
            rc = trail.value(m["day"])
            actual = m["shots_h"] + m["shots_a"]
            if m["season"] in scored_seasons:
                vals = {"A": (lt, 40), "B": (lt * f, 40), "C": (lt, rc),
                        "baseline_league": (lb, None),
                        "baseline_naive": (ln, None)}
                for arm, (mu, r) in vals.items():
                    p = nb_over(mu, r, LINE) if r else nb_over(mu, 40, LINE)
                    pred.append({"match_id": m["match_id"],
                                 "season": m["season"], "date": m["date"],
                                 "home": m["home"], "away": m["away"],
                                 "arm": arm, "p_over_primary": p,
                                 "actual_total": actual,
                                 "actual_over_primary": int(actual > LINE)})
        actual = m["shots_h"] + m["shots_a"]
        naive.update(m["home_id"], m["away_id"], m["shots_h"], m["shots_a"])
        base.update(m["day"], m["shots_h"], m["shots_a"])
        layer.update(0, m["day"], actual,
                     (eh + ea + nh + na) / 2 if m["season"] in predict_seasons
                     else actual)
        trail.update(m["day"], actual)
    return pred


def _metrics(pred, seasons):
    metrics = []
    for a in ARMS:
        for s in tuple(seasons) + ("pooled",):
            q = [x for x in pred
                 if x["arm"] == a and (s == "pooled" or x["season"] == s)]
            if not q:
                continue
            metrics.append({
                "arm": a, "season": s, "n": len(q),
                "primary_ll": sum(log_loss(x["p_over_primary"],
                                           x["actual_over_primary"])
                                  for x in q) / len(q)})
    return metrics


def _pooled(metrics, arm):
    return next(m["primary_ll"] for m in metrics
                if m["arm"] == arm and m["season"] == "pooled")


def dev():
    rows = load_dev()
    mbar = derive_level_prior([x["shots_h"] + x["shots_a"] for x in rows])
    assert math.isclose(mbar, EXPECTED_M_BAR, abs_tol=1e-9), mbar
    pred = walk(rows, set(TARGETS))
    metrics = _metrics(pred, TARGETS)
    base_ll = _pooled(metrics, "baseline_league")
    naive_ll = _pooled(metrics, "baseline_naive")
    arm_pass = {a: (_pooled(metrics, a) < base_ll
                    and _pooled(metrics, a) < naive_ll) for a in ("B", "C")}
    dev_pass = bool(arm_pass["B"] or arm_pass["C"])
    payload = {
        "protocol": {"regular_only": True, "dev_n": 369,
                     "primary_line": LINE, "ladder": [26.5, 27.5, 28.5],
                     "halves": [0.467, 0.533], "candidate": CANDIDATE,
                     "M_BAR": mbar, "shipped_M_BAR": SHIPPED_M_BAR,
                     "rows_loaded": len(rows),
                     "arm_dev_pass": arm_pass, "dev_pass": dev_pass},
        "metrics": metrics, "calibration_inputs": pred}
    (HERE / "results_dev_l1.json").write_text(
        json.dumps(payload, indent=2) + "\n")
    with (HERE / "predictions_dev_l1.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(pred[0]))
        w.writeheader()
        w.writerows(pred)
    record_dev_pass(str(REGISTRY), CANDIDATE, dev_pass,
                    str(HERE / "results_dev_l1.json"))
    print(json.dumps({"M_BAR": mbar, "arm_dev_pass": arm_pass,
                      "dev_pass": dev_pass,
                      "pooled": {a: _pooled(metrics, a) for a in ARMS}},
                     indent=2))
    return payload


def virgin():
    # Fail-closed: load_sealed_rows raises unless the recorded token
    # for CANDIDATE is exactly True.
    raw_all = load_sealed_rows(str(DATA), CANDIDATE, str(REGISTRY))
    dev_rows = load_dev()
    sealed, raw_sealed = [], []
    for r in raw_all:
        if r["season"] != VIRGIN or r["phase"] != "regular":
            continue
        if r["home_total_shots"] == "" or r["away_total_shots"] == "":
            continue
        raw_sealed.append(r)
        sealed.append(_parse(r))
    assert len(sealed) == 110, len(sealed)
    rows = sorted(dev_rows + sealed, key=lambda x: (x["day"], x["match_id"]))
    pred = walk(rows, {VIRGIN})
    out = {}
    for a in ARMS:
        q = [x for x in pred if x["arm"] == a]
        ps = [x["p_over_primary"] for x in q]
        ys = [x["actual_over_primary"] for x in q]
        diff, se = calibration(ps, ys)
        out[a] = {"n": len(q),
                  "primary_ll": sum(log_loss(p, y) for p, y in zip(ps, ys))
                  / len(q),
                  "mean_pred": sum(ps) / len(ps),
                  "actual_rate": sum(ys) / len(ys),
                  "calibration_diff_pp": diff, "calibration_se_pp": se,
                  "calibration_band": calibration_band(diff, se)}
    # Sign check (leg iii) from the corrected dev artefact.
    dev_payload = json.loads((HERE / "results_dev_l1.json").read_text())
    dm = {(m["arm"], m["season"]): m["primary_ll"]
          for m in dev_payload["metrics"]}
    signs = {}
    for a in ("B", "C"):
        wins, n, ok = sign_check([dm[(a, s)] for s in TARGETS],
                                 [dm[("A", s)] for s in TARGETS])
        signs[a] = {"wins": wins, "n": n, "pass": ok}
    payload = {"protocol": {"candidate": CANDIDATE, "virgin_season": VIRGIN,
                            "virgin_n": len(sealed), "primary_line": LINE,
                            "M_BAR": EXPECTED_M_BAR,
                            "shipped_M_BAR": SHIPPED_M_BAR},
               "arms": out, "sign_check_dev": signs,
               "calibration_inputs": pred}
    (HERE / "results_virgin_l1.json").write_text(
        json.dumps(payload, indent=2) + "\n")
    with (HERE / "predictions_virgin_l1.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(pred[0]))
        w.writeheader()
        w.writerows(pred)
    print(json.dumps({"arms": out, "sign_check_dev": signs}, indent=2))
    return payload


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "dev"
    if mode == "dev":
        dev()
    elif mode == "virgin":
        virgin()
    else:
        raise SystemExit(f"unknown mode {mode}")
