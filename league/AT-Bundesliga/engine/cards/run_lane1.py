"""Lane 1 (K-AT-L1) dev + single sealed read for the AT-Bundesliga cards engine.

Stages:
  dev    — recompute the dev legs on dev data only (the dev loader's
           season set excludes the sealed seasons in code, and
           gate_lib.assert_no_sealed_rows double-checks), evaluate
           the arm of record (X8) against both baselines with
           league/gate_lib, and record the dev-pass token.
  sealed — load the sealed window ONCE through gate_lib's fail-closed
           load_sealed_rows (which asserts the recorded dev-pass token
           before reading), then compute every sealed leg per
           PREREG_L1_K_AT.md. Never run this stage before `dev`.

Run from the repository root with the project interpreter:
  python league/AT-Bundesliga/engine/cards/run_lane1.py dev
  python league/AT-Bundesliga/engine/cards/run_lane1.py sealed
"""
import csv, json, math, sys
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT))

import harness
from model import Online, nb_over
from league.gate_lib import (
    assert_no_sealed_rows, calibration, calibration_band, load_sealed_rows,
    parse_prereg, pooled_ll, record_dev_pass, sign_check,
)

CANDIDATE = "K-AT-L1"
SEALED_SEASON = "2025/2026"
REGISTRY = HERE / "lane1_dev_pass_registry.json"
CSV_PATH = HERE.parents[1] / "data" / "at_matches.csv"
PREREG = HERE.parents[1] / "prereg" / "PREREG_L1_K_AT.md"
DOCUMENTED = {  # original verdict, pooled dev LL@4.5
    "gate_zero": 0.6654, "x8": 0.6561, "base": 0.6803, "naive": 0.6636,
}


def _season_lls(arm_block):
    return {
        s: arm_block["seasons"][s]["model"]["4.5"]["ll"]
        for s in harness.SCORED
    }


def dev_stage():
    spec = parse_prereg(PREREG)
    assert spec.primary_line == 4.5 and not spec.missing_tokens, spec
    rows = harness.load(harness.DEV_SEASONS)
    assert_no_sealed_rows(rows, {SEALED_SEASON, "2026/2027"})
    out = harness.dev()  # writes results_dev.json / results_dev.csv

    legs = {}
    for arm in ("gate_zero", "x8"):
        block = out["arms"][arm]
        pooled = {
            m: pooled_ll([{"ll": block["seasons"]["pooled"][m]["4.5"]["ll"],
                           "n": block["seasons"]["pooled"][m]["4.5"]["n"]}])
            for m in ("model", "base", "naive")
        }
        legs[arm] = {"pooled_ll_4_5": pooled,
                     "per_season_ll_4_5": _season_lls(block)}
    x8 = legs["x8"]["pooled_ll_4_5"]
    dev_pass = x8["model"] < x8["base"] and x8["model"] < x8["naive"]
    wins, n_seasons, sign_ok = sign_check(
        [legs["x8"]["per_season_ll_4_5"][s] for s in harness.SCORED],
        [legs["gate_zero"]["per_season_ll_4_5"][s] for s in harness.SCORED],
    )
    reproduced = {
        arm: abs(legs[arm]["pooled_ll_4_5"]["model"] - DOCUMENTED[arm]) < 1e-4
        for arm in ("gate_zero", "x8")
    }
    reproduced["base"] = abs(x8["base"] - DOCUMENTED["base"]) < 1e-4
    reproduced["naive"] = abs(x8["naive"] - DOCUMENTED["naive"]) < 1e-4
    record = {
        "candidate": CANDIDATE,
        "stage": "dev",
        "dev_pass_arm_of_record_x8": dev_pass,
        "legs": legs,
        "sign_check_x8_vs_gate_zero": {"wins": wins, "of": n_seasons, "pass": sign_ok},
        "documented_pooled_ll_4_5": DOCUMENTED,
        "reproduced_within_artefact_rounding": reproduced,
        "referee_coverage": out["referee_coverage"],
    }
    (HERE / "results_dev_lane1.json").write_text(json.dumps(record, indent=2) + "\n")
    if dev_pass and all(reproduced.values()):
        record_dev_pass(str(REGISTRY), CANDIDATE, True, str(HERE / "results_dev.json"))
    print(json.dumps(record, indent=2))
    if not (dev_pass and all(reproduced.values())):
        print("STOP: dev pass not reproduced — no sealed read is authorised.")
    return record


def _virgin_records(raw_rows):
    out = []
    for r in raw_rows:
        if r["season"] != SEALED_SEASON:
            continue
        key = datetime.fromisoformat(r["kickoff_utc"].replace("Z", "+00:00"))
        yh = int(float(r["yellow_home"])); ya = int(float(r["yellow_away"]))
        out.append({"match_id": r["match_id"], "season": r["season"], "date": r["date"],
                    "kickoff_utc": r["kickoff_utc"], "key": (r["kickoff_utc"], r["match_id"]),
                    "day": key.date().toordinal(), "home_id": int(r["home_team_id"]),
                    "away_id": int(r["away_team_id"]), "home": r["home_team"],
                    "away": r["away_team"], "yh": yh, "ya": ya, "y": yh + ya,
                    "referee": (r.get("referee") or "").strip()})
    out.sort(key=lambda x: x["key"])
    return out


def sealed_stage():
    # THE single sealed read: the loader asserts the dev-pass token
    # for K-AT-L1 before it reads a single row.
    raw = load_sealed_rows(str(CSV_PATH), CANDIDATE, str(REGISTRY))
    virgin_rows = _virgin_records(raw)
    assert len(virgin_rows) == 195, f"virgin n={len(virgin_rows)}"

    dev_rows = harness.load(harness.DEV_SEASONS)
    assert_no_sealed_rows(dev_rows, {SEALED_SEASON, "2026/2027"})
    rows = sorted(dev_rows + virgin_rows, key=lambda x: x["key"])

    online = Online()
    arms = ("x8", "gate_zero")
    fit = {a: [] for a in arms}
    virgin = {a: [] for a in arms}
    coverage = [0, 0]
    for row in rows:
        for a in arms:
            p = online.prediction(row, a)
            rec = {"y": row["y"], "model": p["model"], "base": p["base"],
                   "naive": p["naive"], "row": row, "p": p}
            (virgin if row["season"] == SEALED_SEASON else fit)[a].append(rec)
        if row["season"] == SEALED_SEASON:
            coverage[1] += 1; coverage[0] += bool(row["referee"])
        online.update(row)

    result = {"candidate": CANDIDATE, "stage": "sealed",
              "protocol": {"virgin_season": SEALED_SEASON, "n": len(virgin_rows),
                           "single_read_via": "gate_lib.load_sealed_rows"},
              "referee_coverage": {"known": coverage[0], "n": coverage[1],
                                   "fraction": coverage[0] / coverage[1]},
              "arms": {}}
    for a in arms:
        rmap = harness._rmap(fit[a])
        rr = [{"y": x["y"], "model": x["model"], "base": x["base"], "naive": x["naive"]}
              for x in virgin[a]]
        metric = harness.scored(rr, rmap)
        ps = [nb_over(x["model"], rmap["model"], 4.5) for x in virgin[a]]
        ys = [int(x["y"] > 4.5) for x in virgin[a]]
        diff_pp, se_pp = calibration(ps, ys)
        result["arms"][a] = {"r": rmap, "metrics": metric,
                             "calibration": {"diff_pp": diff_pp, "se_pp": se_pp,
                                             "band": calibration_band(diff_pp, se_pp)},
                             "x8_fallbacks": harness._fallback([x["p"] for x in virgin[a]])}
    (HERE / "results_virgin_lane1.json").write_text(json.dumps(result, indent=2) + "\n")

    # Sealed predictions of the arm of record (X8), per the prereg outputs.
    rmap = result["arms"]["x8"]["r"]
    pred_path = HERE.parents[1] / "predictions" / "k_at_lane1_virgin_predictions.csv"
    pred_path.parent.mkdir(exist_ok=True)
    fields = ["match_id", "date", "home_team", "away_team", "actual_yellows",
              "exp_yellows_total", "referee", "p_over_3_5", "p_over_4_5", "p_over_5_5",
              "p_over_1h_0_5", "p_over_1h_1_5", "p_over_1h_2_5",
              "p_over_2h_1_5", "p_over_2h_2_5", "p_over_2h_3_5", "arm"]
    with open(pred_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields); w.writeheader()
        for x in virgin["x8"]:
            row, p, mu, r = x["row"], x["p"], x["model"], rmap["model"]
            q = {"match_id": row["match_id"], "date": row["date"], "home_team": row["home"],
                 "away_team": row["away"], "actual_yellows": row["y"],
                 "exp_yellows_total": mu, "referee": p["referee"], "arm": "x8"}
            for line in (3.5, 4.5, 5.5):
                q[f"p_over_{str(line).replace('.', '_')}"] = nb_over(mu, r, line)
            for line in (0.5, 1.5, 2.5):
                q[f"p_over_1h_{str(line).replace('.', '_')}"] = nb_over(mu * .316, r, line)
            for line in (1.5, 2.5, 3.5):
                q[f"p_over_2h_{str(line).replace('.', '_')}"] = nb_over(mu * .684, r, line)
            w.writerow(q)
    print(json.dumps(result, indent=2))
    return result


if __name__ == "__main__":
    stage = sys.argv[1] if len(sys.argv) > 1 else ""
    if stage == "dev":
        dev_stage()
    elif stage == "sealed":
        sealed_stage()
    else:
        raise SystemExit("usage: run_lane1.py dev|sealed")
