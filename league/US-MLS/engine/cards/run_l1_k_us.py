"""Lane 1 (L1-K-US) dev + single sealed read for the US-MLS cards engine.

Prereg: league/US-MLS/prereg/PREREG_L1_K_US.md (committed before any
sealed access, branch build/lane1-kus first commit).

Stages:
  dev    — recompute the dev legs on dev data only (harness.load's
           season set excludes the sealed seasons in code, and
           gate_lib.assert_no_sealed_rows double-checks), evaluate
           the arm of record (X8) against both baselines with
           league/gate_lib, and record the dev-pass token.
  sealed — load the sealed window ONCE through gate_lib's fail-closed
           load_sealed_rows (which asserts the recorded dev-pass token
           before reading), then compute every sealed leg per
           PREREG_L1_K_US.md. Never run this stage before `dev`.
           Refuses to run if results_virgin_l1.json already exists.

All leg arithmetic (pooled LL, per-match LL, calibration, calibration
band, sign check) goes through league/gate_lib functions; the frozen
engine mechanics (prediction, NB over-probability, r estimation) are
reused verbatim from harness.py / model.py. The original harness's
own virgin verdict writer is NOT used (known section-5.6-class trap).

Run from the repository root with the project interpreter:
  python league/US-MLS/engine/cards/run_l1_k_us.py dev
  python league/US-MLS/engine/cards/run_l1_k_us.py sealed
"""
import csv
import json
import sys
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT))

import harness  # noqa: E402  (frozen engine harness)
from model import Online, nb_over  # noqa: E402
from league.gate_lib import (  # noqa: E402
    assert_no_sealed_rows,
    load_sealed_rows,
    parse_prereg,
    record_dev_pass,
)
from league.gate_lib.metrics import (  # noqa: E402
    calibration as gl_calibration,
)
from league.gate_lib.metrics import (  # noqa: E402
    calibration_band,
    log_loss as gl_log_loss,
    pooled_ll as gl_pooled_ll,
    sign_check,
)

CANDIDATE = "L1-K-US"
SEALED_SEASON = "2025"
REGISTRY = HERE / "dev_pass_registry_l1.json"
CSV_PATH = HERE.parents[1] / "data" / "us_matches.csv"
PREREG = HERE.parents[1] / "prereg" / "PREREG_L1_K_US.md"
DEV_OUT = HERE / "results_dev_l1.json"
VIRGIN_OUT = HERE / "results_virgin_l1.json"

# Documented dev numbers (K_US_VERDICT.md / cohort report section 1.2),
# pooled LL@4.5, scored dev n = 1529.
DOCUMENTED = {
    "gate_zero": 0.678407,
    "x8": 0.670898,
    "base": 0.677134,
    "naive": 0.682714,
}
ROUND_TOL = 1e-6


def check_prereg_tokens():
    spec = parse_prereg(PREREG)
    assert spec.primary_line == 4.5, spec
    assert spec.calibration_tolerance_pp == 1.0, spec
    assert spec.sign_convention_stated == "predicted_minus_actual", spec
    assert str(spec.virgin_season) == "2025", spec
    assert not spec.missing_tokens, spec
    return spec


def _season_lls(arm_block):
    return {s: arm_block["seasons"][s]["model"]["4.5"]["ll"] for s in harness.SCORED}


def dev_stage():
    check_prereg_tokens()
    rows = harness.load(harness.DEV_SEASONS)
    assert_no_sealed_rows(rows, {SEALED_SEASON, "2026"})

    # harness.dev() overwrites the original results_dev.json/.csv;
    # snapshot and restore them so the original artefacts stay untouched
    # (the Lane 1 record lives in results_dev_l1.json).
    snapshots = {}
    for name in ("results_dev.json", "results_dev.csv"):
        p = HERE / name
        snapshots[name] = p.read_bytes() if p.exists() else None
    try:
        out = harness.dev()
    finally:
        for name, data in snapshots.items():
            p = HERE / name
            if data is not None:
                p.write_bytes(data)

    legs = {}
    for arm in ("gate_zero", "x8"):
        block = out["arms"][arm]
        pooled = {}
        for m in ("model", "base", "naive"):
            per_season = [
                {"ll": block["seasons"][s][m]["4.5"]["ll"],
                 "n": block["seasons"][s][m]["4.5"]["n"]}
                for s in harness.SCORED
            ]
            pooled[m] = gl_pooled_ll(per_season)
            # gate_lib pooled LL over seasons must match the artefact's
            # directly pooled value (same arithmetic, two paths).
            direct = block["seasons"]["pooled"][m]["4.5"]["ll"]
            assert abs(pooled[m] - direct) < 1e-12, (arm, m, pooled[m], direct)
        legs[arm] = {"pooled_ll_4_5": pooled, "per_season_ll_4_5": _season_lls(block)}

    x8 = legs["x8"]["pooled_ll_4_5"]
    dev_pass = x8["model"] < x8["base"] and x8["model"] < x8["naive"]
    wins, n_seasons, sign_ok = sign_check(
        [legs["x8"]["per_season_ll_4_5"][s] for s in harness.SCORED],
        [legs["gate_zero"]["per_season_ll_4_5"][s] for s in harness.SCORED],
    )
    repro_diff = {
        "gate_zero": abs(legs["gate_zero"]["pooled_ll_4_5"]["model"] - DOCUMENTED["gate_zero"]),
        "x8": abs(x8["model"] - DOCUMENTED["x8"]),
        "base": abs(x8["base"] - DOCUMENTED["base"]),
        "naive": abs(x8["naive"] - DOCUMENTED["naive"]),
    }
    reproduced = all(v <= ROUND_TOL for v in repro_diff.values())
    record = {
        "candidate": CANDIDATE,
        "stage": "dev",
        "protocol": {"warmup": "2021", "scored": list(harness.SCORED),
                     "dev_rows_loaded": out["protocol"]["dev_rows_loaded"],
                     "primary_line": 4.5},
        "dev_pass_arm_of_record_x8": bool(dev_pass),
        "legs": legs,
        "sign_check_x8_vs_gate_zero": {"wins": wins, "of": n_seasons, "pass": bool(sign_ok)},
        "documented_pooled_ll_4_5": DOCUMENTED,
        "reproduction_abs_diff": repro_diff,
        "reproduced_within_artefact_rounding": bool(reproduced),
        "referee_coverage": out["referee_coverage"],
        "r": {a: out["arms"][a]["r"] for a in out["arms"]},
        "x8_fallbacks": {a: out["arms"][a]["x8_fallbacks"] for a in out["arms"]},
    }
    DEV_OUT.write_text(json.dumps(record, indent=2) + "\n")
    print(json.dumps(record, indent=2))
    if dev_pass and reproduced:
        record_dev_pass(str(REGISTRY), CANDIDATE, True, str(DEV_OUT))
        print("dev-pass token recorded for", CANDIDATE)
    else:
        print("STOP: dev pass not reproduced — no sealed read is authorised.")
    return record


def _virgin_records(raw_rows):
    """Mirror harness.load() row construction for the sealed season only,
    sourced from the gate_lib sealed loader's rows (provenance control)."""
    out = []
    for r in raw_rows:
        if r["season"] != SEALED_SEASON:
            continue
        # Same missing-target exclusion as harness.load().
        if not r["yellow_home"] or not r["yellow_away"]:
            continue
        key = datetime.fromisoformat(r["kickoff_utc"].replace("Z", "+00:00"))
        yh = int(float(r["yellow_home"]))
        ya = int(float(r["yellow_away"]))
        out.append({"match_id": r["match_id"], "season": r["season"], "date": r["date"],
                    "kickoff_utc": r["kickoff_utc"], "key": (r["kickoff_utc"], r["match_id"]),
                    "day": key.date().toordinal(), "home_id": int(r["home_team_id"]),
                    "away_id": int(r["away_team_id"]), "home": r["home_team"],
                    "away": r["away_team"], "yh": yh, "ya": ya, "y": yh + ya,
                    "referee": (r.get("referee") or "").strip()})
    out.sort(key=lambda x: x["key"])
    return out


def _gate_ll(records, rmap, method, line=4.5):
    """Mean binary log-loss at `line` via gate_lib.log_loss."""
    ps = [nb_over(x[method], rmap[method], line) for x in records]
    ys = [int(x["y"] > line) for x in records]
    return sum(gl_log_loss(p, y) for p, y in zip(ps, ys)) / len(ys), ps, ys


def sealed_stage():
    if VIRGIN_OUT.exists():
        raise SystemExit("results_virgin_l1.json already exists: the single "
                         "sealed read has already happened; refusing a second read.")
    check_prereg_tokens()
    dev_data = json.loads(DEV_OUT.read_text())
    assert dev_data["dev_pass_arm_of_record_x8"] is True
    assert dev_data["reproduced_within_artefact_rounding"] is True

    # THE single sealed read: the loader asserts the dev-pass token
    # for L1-K-US before it reads a single row.
    raw = load_sealed_rows(str(CSV_PATH), CANDIDATE, str(REGISTRY))
    virgin_rows = _virgin_records(raw)
    assert len(virgin_rows) == 540, f"virgin n={len(virgin_rows)} (prereg pins 540)"

    dev_rows = harness.load(harness.DEV_SEASONS)
    assert_no_sealed_rows(dev_rows, {SEALED_SEASON, "2026"})
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
            coverage[1] += 1
            coverage[0] += bool(row["referee"])
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
        # Cross-check: frozen harness scoring vs gate_lib arithmetic.
        harness_metric = harness.scored(rr, rmap)
        ll_model, ps, ys = _gate_ll(rr, rmap, "model")
        ll_base, _, _ = _gate_ll(rr, rmap, "base")
        ll_naive, _, _ = _gate_ll(rr, rmap, "naive")
        for got, want in ((ll_model, harness_metric["model"]["4.5"]["ll"]),
                          (ll_base, harness_metric["base"]["4.5"]["ll"]),
                          (ll_naive, harness_metric["naive"]["4.5"]["ll"])):
            assert abs(got - want) < 1e-9, (a, got, want)
        diff_pp, se_pp = gl_calibration(ps, ys)  # predicted - actual, gate_lib
        result["arms"][a] = {
            "r": rmap,
            "ll_4_5": ll_model, "base_ll_4_5": ll_base, "naive_ll_4_5": ll_naive,
            "metrics": harness_metric,
            "mean_p_over_4_5": sum(ps) / len(ps),
            "actual_over_4_5_rate": sum(ys) / len(ys),
            "calibration": {"diff_pp": diff_pp, "se_pp": se_pp,
                            "band": calibration_band(diff_pp, se_pp)},
            "x8_fallbacks": harness._fallback([x["p"] for x in virgin[a]]),
        }

    # Legs (gate_lib arithmetic throughout).
    x8r, gzr = result["arms"]["x8"], result["arms"]["gate_zero"]
    best_baseline = min(x8r["base_ll_4_5"], x8r["naive_ll_4_5"])
    leg_i = (x8r["ll_4_5"] <= gzr["ll_4_5"]
             and x8r["ll_4_5"] <= x8r["base_ll_4_5"]
             and x8r["ll_4_5"] <= x8r["naive_ll_4_5"])
    band = x8r["calibration"]["band"]
    leg_ii_clean = band == "PASS"
    leg_ii_ok = band in ("PASS", "PROVISIONAL")
    wins, n_seasons, sign_ok = sign_check(
        [dev_data["legs"]["x8"]["per_season_ll_4_5"][s] for s in harness.SCORED],
        [dev_data["legs"]["gate_zero"]["per_season_ll_4_5"][s] for s in harness.SCORED],
    )
    passed = bool(leg_i and leg_ii_ok and sign_ok)
    if passed and leg_ii_clean:
        verdict = "CLEAN PASS"
    elif passed:
        verdict = "PROVISIONAL PASS"
    else:
        verdict = "FAIL"
    result["legs"] = {
        "dev_gate_x8": dev_data["dev_pass_arm_of_record_x8"],
        "leg_i_ll": bool(leg_i),
        "best_baseline_ll_4_5": best_baseline,
        "leg_ii_calibration_band": band,
        "leg_ii_clean": bool(leg_ii_clean),
        "leg_iii_sign_check": {"wins": wins, "n": n_seasons, "pass": bool(sign_ok)},
    }
    result["verdict"] = verdict
    result["shipped_arm"] = "x8" if passed else None
    VIRGIN_OUT.write_text(json.dumps(result, indent=2) + "\n")

    # Sealed predictions of the arm of record (X8): evidence of the read,
    # per the prereg outputs (FT ladder + halves via frozen 0.341).
    rmap = result["arms"]["x8"]["r"]
    pred_path = HERE.parents[1] / "predictions" / "k_us_virgin_predictions.csv"
    pred_path.parent.mkdir(exist_ok=True)
    fields = ["match_id", "date", "home_team", "away_team", "actual_yellows",
              "exp_yellows_total", "referee", "p_over_3_5", "p_over_4_5", "p_over_5_5",
              "p_over_1h_0_5", "p_over_1h_1_5", "p_over_1h_2_5",
              "p_over_2h_1_5", "p_over_2h_2_5", "p_over_2h_3_5", "arm"]
    with open(pred_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for x in virgin["x8"]:
            row, p, mu, r = x["row"], x["p"], x["model"], rmap["model"]
            q = {"match_id": row["match_id"], "date": row["date"], "home_team": row["home"],
                 "away_team": row["away"], "actual_yellows": row["y"],
                 "exp_yellows_total": mu, "referee": p["referee"], "arm": "x8"}
            for line in (3.5, 4.5, 5.5):
                q[f"p_over_{str(line).replace('.', '_')}"] = nb_over(mu, r, line)
            for line in (0.5, 1.5, 2.5):
                q[f"p_over_1h_{str(line).replace('.', '_')}"] = nb_over(mu * .341, r, line)
            for line in (1.5, 2.5, 3.5):
                q[f"p_over_2h_{str(line).replace('.', '_')}"] = nb_over(mu * .659, r, line)
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
        raise SystemExit("usage: run_l1_k_us.py dev|sealed")
