"""Lane 1 (K-NO-OBOS) dev + single sealed evaluation.

Prereg: league/NO-OBOSLigaen/prereg/PREREG_L1_K_NO_OBOS.md
(arm of record = x8; Gate Zero is a comparator/baseline only).

Subcommands (run as separate processes, in this order):
  dev     -- dev data only (2021 warm-up, 2022-2025 scored).
             Asserts no sealed rows enter the dev load, writes
             results_dev_l1.json, and -- only if the arm of
             record reproduces the documented dev pass --
             records the gate_lib dev-pass token.
  sealed  -- the single sealed read. Loads the 2026 rows ONLY
             through league.gate_lib.load_sealed_rows (which
             fails closed without the dev-pass token), walks
             dev + sealed forward, computes every prereg leg,
             writes results_virgin_l1.json and, on PASS, the
             virgin predictions CSV + fitted params.

The scoring mechanics are the frozen harness's own (harness.py /
model.py are imported, not reimplemented).
"""
import argparse
import csv
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT))

from harness import load as harness_load, scored, _rmap, _fallback  # noqa: E402
from model import Online, nb_over  # noqa: E402
from league.gate_lib import (  # noqa: E402
    assert_no_sealed_rows, calibration, calibration_band,
    record_dev_pass, load_sealed_rows, sign_check,
)

LEAGUE_DIR = HERE.parents[1]
DATA_CSV = LEAGUE_DIR / "data" / "no_obos_matches.csv"
DEV_RESULTS = HERE / "results_dev_l1.json"
VIRGIN_RESULTS = HERE / "results_virgin_l1.json"
REGISTRY = HERE / "dev_pass_registry_l1.json"
PRED_CSV = LEAGUE_DIR / "predictions" / "k_no_obos_l1_virgin_predictions.csv"
FITTED = HERE / "fitted_params_virgin_l1.json"

CANDIDATE = "K-NO-OBOS"
DEV_SEASONS = ("2021", "2022", "2023", "2024", "2025")
SCORED = ("2022", "2023", "2024", "2025")
SEALED_SEASON = "2026"
# Documented in reports/K_NO_OBOS_VERDICT.md and
# league/improvement_scratch/LANE1_WAVE1/cohort_report.md S1.2.
DOCUMENTED = {"x8": 0.6553, "gate_zero": 0.6693, "base": 0.6683, "naive": 0.6729}
ROUND_TOL = 5e-5 + 1e-9  # artefact rounding to 4 decimal places


def _parse_raw(raw_rows, seasons):
    """Convert raw CSV dicts to harness row dicts (harness.load's shape)."""
    from datetime import datetime
    out = []
    for r in raw_rows:
        if r["season"] not in seasons:
            continue
        key = datetime.fromisoformat(r["kickoff_utc"].replace("Z", "+00:00"))
        referee = (r.get("referee") or "").strip()
        out.append({
            "match_id": r["match_id"], "season": r["season"], "date": r["date"],
            "kickoff_utc": r["kickoff_utc"], "key": (r["kickoff_utc"], r["match_id"]),
            "day": key.date().toordinal(),
            "home_id": int(r["home_team_id"]), "away_id": int(r["away_team_id"]),
            "home": r["home_team"], "away": r["away_team"],
            "yh": int(float(r["yellow_home"])), "ya": int(float(r["yellow_away"])),
            "y": int(float(r["yellow_home"])) + int(float(r["yellow_away"])),
            "referee": referee,
        })
    out.sort(key=lambda x: x["key"])
    for a, b in zip(out, out[1:]):
        assert a["key"] < b["key"], "processing order is not strictly chronological"
    return out


def _dev_rows():
    rows = harness_load(DEV_SEASONS)
    assert_no_sealed_rows(
        [{"season": r["season"]} for r in rows], {SEALED_SEASON})
    return rows


def dev():
    rows = _dev_rows()
    online = Online()
    by = {a: [] for a in ("gate_zero", "x8")}
    warm = {a: [] for a in by}
    season_preds = {a: {s: [] for s in SCORED} for a in by}
    refs = {s: [0, 0] for s in DEV_SEASONS}
    for row in rows:
        for arm in by:
            p = online.prediction(row, arm)
            rec = {"y": row["y"], "model": p["model"], "base": p["base"], "naive": p["naive"]}
            (warm if row["season"] == "2021" else by)[arm].append(rec)
            if row["season"] in SCORED:
                season_preds[arm][row["season"]].append((row, p))
        refs[row["season"]][1] += 1
        refs[row["season"]][0] += bool(row["referee"])
        online.update(row)
    rmap = {a: _rmap(warm[a]) for a in by}
    out = {
        "candidate": CANDIDATE, "lane": 1, "arm_of_record": "x8",
        "protocol": {"warmup": "2021", "scored": list(SCORED),
                     "dev_rows_loaded": len(rows)},
        "arms": {},
        "referee_coverage": {s: {"known": v[0], "n": v[1], "fraction": v[0] / v[1]}
                             for s, v in refs.items()},
    }
    for arm in by:
        seasons = {}
        allr = []
        for s in SCORED:
            rr = [{"y": r["y"], "model": p["model"], "base": p["base"], "naive": p["naive"]}
                  for r, p in season_preds[arm][s]]
            allr += rr
            seasons[s] = scored(rr, rmap[arm])
        seasons["pooled"] = scored(allr, rmap[arm])
        out["arms"][arm] = {
            "r": rmap[arm], "seasons": seasons,
            "x8_fallbacks": {s: _fallback([p for _, p in season_preds[arm][s]])
                             for s in SCORED},
        }
    for arm in by:
        pooled = out["arms"][arm]["seasons"]["pooled"]
        m = pooled["model"]["3.5"]["ll"]
        b = pooled["base"]["3.5"]["ll"]
        n = pooled["naive"]["3.5"]["ll"]
        out["arms"][arm]["dev_gate_pass"] = m < b and m < n
    # Reproduction check against the documented dev numbers.
    x8 = out["arms"]["x8"]["seasons"]["pooled"]
    gz = out["arms"]["gate_zero"]["seasons"]["pooled"]
    repro = {
        "x8_ll": x8["model"]["3.5"]["ll"], "gate_zero_ll": gz["model"]["3.5"]["ll"],
        "base_ll": x8["base"]["3.5"]["ll"], "naive_ll": x8["naive"]["3.5"]["ll"],
    }
    repro["within_rounding"] = all(
        abs(repro[k] - DOCUMENTED[d]) <= ROUND_TOL
        for k, d in (("x8_ll", "x8"), ("gate_zero_ll", "gate_zero"),
                     ("base_ll", "base"), ("naive_ll", "naive")))
    repro["documented"] = DOCUMENTED
    out["reproduction"] = repro
    DEV_RESULTS.write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(repro, indent=2))
    print("x8 dev_gate_pass:", out["arms"]["x8"]["dev_gate_pass"])
    if not (repro["within_rounding"] and out["arms"]["x8"]["dev_gate_pass"]):
        print("STOP: dev reproduction or dev gate failed; NO token, NO sealed read.")
        return 2
    record_dev_pass(str(REGISTRY), CANDIDATE, True, str(DEV_RESULTS))
    print("dev-pass token recorded:", REGISTRY)
    return 0


def sealed():
    # Fail-closed: raises SealedAccessError without a dev-pass token.
    raw = load_sealed_rows(str(DATA_CSV), CANDIDATE, str(REGISTRY))
    sealed_rows = _parse_raw(raw, (SEALED_SEASON,))
    assert len(sealed_rows) == 240, f"sealed n={len(sealed_rows)} != 240"
    dev_rows = _dev_rows()
    rows = dev_rows + sealed_rows
    rows.sort(key=lambda x: x["key"])

    online = Online()
    arms = ("gate_zero", "x8")
    fit = {a: [] for a in arms}
    virgin = {a: [] for a in arms}
    coverage = [0, 0]
    for row in rows:
        for a in arms:
            p = online.prediction(row, a)
            rec = {"y": row["y"], "model": p["model"], "base": p["base"],
                   "naive": p["naive"], "row": row, "p": p}
            (fit if row["season"] != SEALED_SEASON else virgin)[a].append(rec)
        if row["season"] == SEALED_SEASON:
            coverage[1] += 1
            coverage[0] += bool(row["referee"])
        online.update(row)

    result = {
        "candidate": CANDIDATE, "lane": 1, "arm_of_record": "x8",
        "protocol": {"sealed_season": SEALED_SEASON, "rows": len(sealed_rows),
                     "loader": "league.gate_lib.load_sealed_rows"},
        "arms": {},
        "referee_coverage": {"known": coverage[0], "n": coverage[1],
                             "fraction": coverage[0] / coverage[1]},
    }
    for a in arms:
        rmap = _rmap(fit[a])
        rr = [{"y": x["y"], "model": x["model"], "base": x["base"], "naive": x["naive"]}
              for x in virgin[a]]
        metric = scored(rr, rmap)
        ps = [nb_over(x["model"], rmap["model"], 3.5) for x in virgin[a]]
        ys = [int(x["y"] > 3.5) for x in virgin[a]]
        diff_pp, se_pp = calibration(ps, ys)  # gate_lib: predicted - actual, pp
        result["arms"][a] = {
            "r": rmap, "metrics": metric,
            "calibration": {"diff_pp": diff_pp, "se_pp": se_pp,
                            "diff": diff_pp / 100.0, "se": se_pp / 100.0},
            "x8_fallbacks": _fallback([x["p"] for x in virgin[a]]),
        }

    devres = json.loads(DEV_RESULTS.read_text())
    x8_ll = result["arms"]["x8"]["metrics"]["model"]["3.5"]["ll"]
    gz_ll = result["arms"]["gate_zero"]["metrics"]["model"]["3.5"]["ll"]
    base_ll = result["arms"]["x8"]["metrics"]["base"]["3.5"]["ll"]
    naive_ll = result["arms"]["x8"]["metrics"]["naive"]["3.5"]["ll"]
    best_base = min(base_ll, naive_ll)
    diff_pp = result["arms"]["x8"]["calibration"]["diff_pp"]
    se_pp = result["arms"]["x8"]["calibration"]["se_pp"]
    band = calibration_band(diff_pp, se_pp, 1.0)
    wins, n_seasons, sign_pass = sign_check(
        [devres["arms"]["x8"]["seasons"][s]["model"]["3.5"]["ll"] for s in SCORED],
        [devres["arms"]["gate_zero"]["seasons"][s]["model"]["3.5"]["ll"] for s in SCORED])
    legs = {
        "i_ll_le_gate_zero": x8_ll <= gz_ll,
        "i_ll_le_best_baseline": x8_ll <= best_base,
        "ii_calibration_band": band,
        "iii_sign_check": {"wins": wins, "n": n_seasons, "pass": bool(sign_pass)},
    }
    leg_i = legs["i_ll_le_gate_zero"] and legs["i_ll_le_best_baseline"]
    if leg_i and sign_pass and band == "PASS":
        verdict = "CLEAN PASS"
    elif leg_i and sign_pass and band == "PROVISIONAL":
        verdict = "PROVISIONAL PASS"
    else:
        verdict = "FAIL"
    result["legs"] = legs
    result["verdict"] = verdict
    result["headline"] = {
        "x8_ll_3_5": x8_ll, "gate_zero_ll_3_5": gz_ll,
        "base_ll_3_5": base_ll, "naive_ll_3_5": naive_ll,
        "calibration_diff_pp": diff_pp, "calibration_se_pp": se_pp,
    }
    VIRGIN_RESULTS.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result["headline"], indent=2))
    print("legs:", json.dumps(legs, indent=2))
    print("VERDICT:", verdict)

    if verdict != "FAIL":
        _write_predictions(result, virgin["x8"], fit, rows)
    return 0


def _write_predictions(result, virgin_recs, fit, rows):
    arm = "x8"
    rmap = _rmap(fit[arm])
    # Cutoff state: replay to the first sealed row, as harness.predict does.
    online = Online()
    cutoff_state = None
    targets = []
    for row in rows:
        p = online.prediction(row, arm)
        if row["season"] == SEALED_SEASON:
            if cutoff_state is None:
                cutoff_state = online.state.snapshot(row["day"])
            targets.append((row, p))
        online.update(row)
    assert len(targets) == 240
    PRED_CSV.parent.mkdir(exist_ok=True)
    fields = ["match_id", "date", "home_team", "away_team", "referee",
              "referee_known", "n_prior", "multiplier", "fallback",
              "fallback_reason", "expected_home", "expected_away",
              "expected_total", "p_over_2_5", "p_over_3_5", "p_over_4_5",
              "mean_1h", "mean_2h", "p_over_1h_0_5", "p_over_1h_1_5",
              "p_over_1h_2_5", "p_over_2h_1_5", "p_over_2h_2_5",
              "p_over_2h_3_5", "arm"]
    with open(PRED_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for row, p in targets:
            q = {"match_id": row["match_id"], "date": row["date"],
                 "home_team": row["home"], "away_team": row["away"],
                 "referee": p["referee"], "referee_known": bool(p["referee"]),
                 "n_prior": p["n_prior"], "multiplier": p["multiplier"],
                 "fallback": p["fallback"], "fallback_reason": p["fallback_reason"],
                 "expected_home": p["eh"], "expected_away": p["ea"],
                 "expected_total": p["model"]}
            for line in (2.5, 3.5, 4.5):
                q[f"p_over_{str(line).replace('.', '_')}"] = nb_over(
                    p["model"], rmap["model"], line)
            q.update({
                "mean_1h": p["model"] * .306, "mean_2h": p["model"] * .694,
                "p_over_1h_0_5": nb_over(p["model"] * .306, rmap["model"], .5),
                "p_over_1h_1_5": nb_over(p["model"] * .306, rmap["model"], 1.5),
                "p_over_1h_2_5": nb_over(p["model"] * .306, rmap["model"], 2.5),
                "p_over_2h_1_5": nb_over(p["model"] * .694, rmap["model"], 1.5),
                "p_over_2h_2_5": nb_over(p["model"] * .694, rmap["model"], 2.5),
                "p_over_2h_3_5": nb_over(p["model"] * .694, rmap["model"], 3.5),
                "arm": arm})
            w.writerow(q)
    FITTED.write_text(json.dumps(
        {"HL": 270, "K_PRIOR": 8, "K_REF": 8, "r": rmap, "arm": arm,
         "cutoff_state": cutoff_state}, indent=2) + "\n")
    print("predictions written:", PRED_CSV)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=("dev", "sealed"))
    a = ap.parse_args()
    sys.exit(dev() if a.cmd == "dev" else sealed())
