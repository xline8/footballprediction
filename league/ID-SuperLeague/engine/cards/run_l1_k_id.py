"""Lane 1 runner for L1-K-ID (ID-SuperLeague cards, X5 arm of record).

Prereg: league/ID-SuperLeague/prereg/PREREG_L1_K_ID.md (committed before
any sealed access). All gate arithmetic goes through league/gate_lib/:
prereg tokens are parsed mechanically, dev loading asserts no sealed
rows, the dev-pass token is recorded before any sealed load, and the
sealed window is loaded exactly once through load_sealed_rows.

The frozen engine mechanics are reused verbatim from model.py
(Online, estimate_r, nb_over); this runner only controls WHICH rows
reach them and WHEN. The original harness's count_gate writer is NOT
used: its virgin legs are gated on a Gate Zero dev pass, which is
exactly the gate-architecture defect this Lane 1 entry corrects.

Usage:
  python3 run_l1_k_id.py dev     # dev evaluation + reproduction check
  python3 run_l1_k_id.py sealed  # the single sealed read (needs dev pass)
"""
import csv
import json
import sys
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(HERE))

from league.gate_lib import (  # noqa: E402
    assert_no_sealed_rows,
    load_sealed_rows,
    parse_prereg,
    record_dev_pass,
)
from league.gate_lib.metrics import calibration as gl_calibration  # noqa: E402
from league.gate_lib.metrics import calibration_band, log_loss, sign_check  # noqa: E402
from model import Online, estimate_r, nb_over  # noqa: E402  (frozen engine)

DATA = HERE.parents[1] / "data" / "id_matches.csv"
PREREG = HERE.parents[1] / "prereg" / "PREREG_L1_K_ID.md"
REGISTRY = HERE / "dev_pass_registry_l1.json"
DEV_OUT = HERE / "results_dev_l1.json"
VIRGIN_OUT = HERE / "results_virgin_l1.json"
CANDIDATE_ID = "L1-K-ID"
SEED = "2021/2022"
SCORED = ("2022/2023", "2023/2024", "2024/2025")
VIRGIN = "2025/2026"
LINE = 4.5
ARMS = ("gate_zero", "x5")
ALL_ARMS = ARMS + ("__base", "__naive")
SEALED_SEASONS = {VIRGIN, "2026/2027"}

# Documented dev numbers (K_ID_VERDICT.md / results_dev.json / cohort
# report section 1.2), pooled LL@4.5, dev n = 731. Reproduction
# tolerance: artefact rounding (documented values are the full-precision
# results_dev.json values; the verdict rounds to 4 decimal places).
DOCUMENTED = {
    "gate_zero": 0.7002559025824814,
    "x5": 0.6940411289690254,
    "__base": 0.6959160842013207,
    "__naive": 0.6977851350849587,
}
ROUND_TOL = 5e-5 + 1e-9


def rows_from(raw_rows, seasons):
    """Mirror common_id.load() + run_k_id.to_rows() exactly, sourced
    from an explicit raw-row list (so the caller controls provenance:
    dev-filtered rows, or the gate_lib sealed loader). Only `regular`
    rows; only events_complete rows carry a cards target (yellow_home /
    yellow_away are empty otherwise) and only those rows score or
    update the online state."""
    out = []
    for r in raw_rows:
        if r["season"] not in seasons or r["phase"] != "regular":
            continue
        ch, ca = r.get("yellow_home"), r.get("yellow_away")
        if ch in ("", None) or ca in ("", None):
            continue
        d = date.fromisoformat(r["date"])
        out.append({
            "home_id": int(r["home_team_id"]), "away_id": int(r["away_team_id"]),
            "day": d.toordinal(), "kickoff_utc": r["date"] + "T00:00:00Z",
            "yh": int(float(ch)), "ya": int(float(ca)),
            "y": int(float(ch)) + int(float(ca)),
            "referee": r.get("referee") or "", "season": r["season"],
            "match_id": r["match_id"], "date": d,
        })
    return sorted(out, key=lambda m: (m["date"], int(m["match_id"])))


def read_raw_csv():
    with DATA.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def check_prereg_tokens():
    spec = parse_prereg(PREREG)
    assert spec.primary_line == 4.5, spec
    assert spec.ladder == [3.5, 4.5, 5.5], spec
    assert spec.calibration_tolerance_pp == 1.0, spec
    assert spec.sign_convention_stated == "predicted_minus_actual", spec
    assert str(spec.virgin_season) == "2025/2026", spec
    assert not spec.missing_tokens, spec
    return spec


def agg_gate_lib(pairs):
    """pairs: list of (p, y). Headline metrics via gate_lib only."""
    ps = [p for p, _ in pairs]
    ys = [y for _, y in pairs]
    diff_pp, se_pp = gl_calibration(ps, ys)
    return {
        "n": len(pairs),
        "ll": sum(log_loss(p, y) for p, y in pairs) / len(pairs) if pairs else None,
        "mean_pred": sum(ps) / len(ps) if ps else None,
        "actual_rate": sum(ys) / len(ys) if ys else None,
        "calibration_pp": diff_pp,
        "calibration_se_pp": se_pp,
    }


def dev_pass(rows):
    """One chronological online pass over seed + scored rows, exactly
    as run_k_id.run(): r per method estimated on the seed season's
    causal residuals and frozen at the first scored row."""
    on = Online()
    seed_recs = []
    rs = {"model": 500.0, "base": 500.0, "naive": 500.0}
    rs_set = False
    res = {a: {} for a in ALL_ARMS}
    for r in rows:
        p = on.prediction(r, "gate_zero")
        if r["season"] == SEED:
            seed_recs.append({"y": r["y"], "model": p["model"],
                              "base": p["base"], "naive": p["naive"]})
        if r["season"] in SCORED and seed_recs and not rs_set:
            rs = {k: estimate_r(seed_recs, k) for k in rs}
            rs_set = True
        if r["season"] in SCORED:
            y = 1 if r["y"] > LINE else 0
            vals = {
                "gate_zero": nb_over(p["model"], rs["model"], LINE),
                "x5": nb_over(0.5 * p["model"] + 0.5 * p["naive"], rs["model"], LINE),
                "__base": nb_over(p["base"], rs["base"], LINE),
                "__naive": nb_over(p["naive"], rs["naive"], LINE),
            }
            for a, pv in vals.items():
                res[a].setdefault(r["season"], []).append((pv, y))
        on.update(r)
    out = {}
    for a, bys in res.items():
        out[a] = {s: agg_gate_lib(v) for s, v in bys.items()}
        out[a]["pooled"] = agg_gate_lib([x for v in bys.values() for x in v])
    return out, rs


def dev():
    check_prereg_tokens()
    raw = read_raw_csv()
    kept_raw = [r for r in raw if r["season"] in (SEED,) + SCORED]
    # P2 design seal / P5 guard: the dev loader must contain no sealed rows.
    assert_no_sealed_rows(kept_raw, SEALED_SEASONS)
    rows = rows_from(kept_raw, (SEED,) + SCORED)
    res, rs = dev_pass(rows)

    repro = {a: abs(res[a]["pooled"]["ll"] - DOCUMENTED[a]) for a in ALL_ARMS}
    reproduced = all(v <= ROUND_TOL for v in repro.values())
    base_ll = res["__base"]["pooled"]["ll"]
    naive_ll = res["__naive"]["pooled"]["ll"]
    x5_pass = res["x5"]["pooled"]["ll"] < base_ll and res["x5"]["pooled"]["ll"] < naive_ll
    gz_pass = res["gate_zero"]["pooled"]["ll"] < base_ll and res["gate_zero"]["pooled"]["ll"] < naive_ll
    wins, n_seas, sign_ok = sign_check(
        [res["x5"][s]["ll"] for s in SCORED],
        [res["gate_zero"][s]["ll"] for s in SCORED],
    )
    out = {
        "protocol": {
            "candidate": CANDIDATE_ID, "seed": SEED, "scored": list(SCORED),
            "line": LINE, "r": rs, "virgin_read": False,
            "dev_rows_loaded": len(rows),
            "dev_pass_token_recorded": False,
        },
        "arms": {a: res[a] for a in ARMS},
        "baselines": {b: res[b] for b in ("__base", "__naive")},
        "documented_pooled_ll": DOCUMENTED,
        "reproduction_abs_diff": repro,
        "reproduced_within_rounding": reproduced,
        "x5_dev_gate_pass": bool(x5_pass),
        "gate_zero_dev_gate_pass": bool(gz_pass),
        "sign_check_x5_vs_gate_zero": {"wins": wins, "n": n_seas, "pass": bool(sign_ok)},
    }
    DEV_OUT.write_text(json.dumps(out, indent=2) + "\n")
    print("dev pooled LL@4.5:", {a: res[a]["pooled"]["ll"] for a in ALL_ARMS})
    print("reproduction abs diffs:", repro, "reproduced:", reproduced)
    print("x5 dev gate pass:", x5_pass, "| gate_zero dev gate pass:", gz_pass,
          "| sign check:", wins, "/", n_seas)
    if not (reproduced and x5_pass):
        print("STOP: dev reproduction failed or X5 dev gate failed; NO sealed read.")
        return 2
    record_dev_pass(REGISTRY, CANDIDATE_ID, True, str(DEV_OUT))
    out["protocol"]["dev_pass_token_recorded"] = True
    DEV_OUT.write_text(json.dumps(out, indent=2) + "\n")
    print("dev-pass token recorded for", CANDIDATE_ID)
    return 0


def sealed():
    if VIRGIN_OUT.exists():
        raise SystemExit("results_virgin_l1.json already exists: the single "
                         "sealed read has already happened; refusing a second read.")
    check_prereg_tokens()
    dev_data = json.loads(DEV_OUT.read_text())
    assert dev_data["x5_dev_gate_pass"] is True and dev_data["reproduced_within_rounding"] is True

    # THE SINGLE SEALED READ: rows enter only through the gate_lib
    # sealed loader, which refuses unless the dev-pass token exists.
    all_raw = load_sealed_rows(DATA, CANDIDATE_ID, REGISTRY)
    keep = [r for r in all_raw if r["season"] in (SEED,) + SCORED + (VIRGIN,)]
    rows = rows_from(keep, (SEED,) + SCORED + (VIRGIN,))
    assert "2026/2027" not in {r["season"] for r in rows}
    virgin_rows = [r for r in rows if r["season"] == VIRGIN]
    pre_rows = [r for r in rows if r["season"] != VIRGIN]

    # Virgin protocol, exactly as the original harness: causal warm-up
    # over all pre-virgin rows, r re-estimated on those residuals, then
    # the virgin season scored continuing from the warm-up end state.
    on = Online()
    warm = []
    for r in pre_rows:
        p = on.prediction(r, "gate_zero")
        warm.append({"y": r["y"], "model": p["model"], "base": p["base"], "naive": p["naive"]})
        on.update(r)
    rs_v = {k: estimate_r(warm, k) for k in ("model", "base", "naive")}

    res = {a: [] for a in ALL_ARMS}
    preds = []
    for r in virgin_rows:
        p = on.prediction(r, "gate_zero")
        y = 1 if r["y"] > LINE else 0
        mu_x5 = 0.5 * p["model"] + 0.5 * p["naive"]
        vals = {
            "gate_zero": nb_over(p["model"], rs_v["model"], LINE),
            "x5": nb_over(mu_x5, rs_v["model"], LINE),
            "__base": nb_over(p["base"], rs_v["base"], LINE),
            "__naive": nb_over(p["naive"], rs_v["naive"], LINE),
        }
        for a, pv in vals.items():
            res[a].append((pv, y))
        preds.append((r, vals["x5"], mu_x5))
        on.update(r)
    met = {a: agg_gate_lib(v) for a, v in res.items()}

    x5, gz = met["x5"], met["gate_zero"]
    leg_i = (x5["ll"] <= gz["ll"] and x5["ll"] <= met["__base"]["ll"]
             and x5["ll"] <= met["__naive"]["ll"])
    band = calibration_band(x5["calibration_pp"], x5["calibration_se_pp"], 1.0)
    leg_ii_ok = band in ("PASS", "PROVISIONAL")
    sc = dev_data["sign_check_x5_vs_gate_zero"]
    leg_iii = bool(sc["pass"])
    passed = bool(leg_i and leg_ii_ok and leg_iii)
    if passed and band == "PASS":
        verdict = "CLEAN PASS"
    elif passed:
        verdict = "PROVISIONAL PASS"
    else:
        verdict = "FAIL"
    shipped = "x5" if passed else None

    out = {
        "protocol": {
            "candidate": CANDIDATE_ID, "virgin_read": True, "virgin": VIRGIN,
            "virgin_rows_loaded": len(virgin_rows), "r_virgin": rs_v,
        },
        "arms": {a: met[a] for a in ARMS},
        "baselines": {b: met[b] for b in ("__base", "__naive")},
        "legs": {
            "dev_gate_x5": dev_data["x5_dev_gate_pass"],
            "leg_i_ll": bool(leg_i),
            "leg_ii_calibration_band": band,
            "leg_iii_sign_check": sc,
        },
        "verdict": verdict,
        "shipped_arm": shipped,
    }
    VIRGIN_OUT.write_text(json.dumps(out, indent=2) + "\n")
    print("virgin pooled:", {a: met[a] for a in ALL_ARMS})
    print("legs: (i)", leg_i, "(ii) band", band, "(iii)", sc)
    print("verdict", verdict, "shipped", shipped)
    if shipped:
        pdir = HERE.parents[1] / "predictions"
        pdir.mkdir(exist_ok=True)
        with (pdir / "k_id_lane1_virgin_predictions.csv").open("w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["match_id", "date", "home_id", "away_id", "arm",
                        "pred_total_ft", "p_over_4.5", "pred_total_1h",
                        "pred_total_2h", "actual_total"])
            for r, pv, mu in preds:
                w.writerow([r["match_id"], r["date"].isoformat(), r["home_id"],
                            r["away_id"], shipped, round(mu, 3), round(pv, 4),
                            round(mu * 0.385, 3), round(mu * 0.615, 3), int(r["y"])])
        (HERE / "fitted_params_virgin_l1.json").write_text(json.dumps(
            {"market": "cards", "arm": shipped, "r": rs_v,
             "halves_share_1h": 0.385}, indent=2) + "\n")
        print("virgin predictions + fitted params written for arm", shipped)
    return 0


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "dev":
        sys.exit(dev())
    elif cmd == "sealed":
        sys.exit(sealed())
    else:
        raise SystemExit("usage: run_l1_k_id.py dev|sealed")
