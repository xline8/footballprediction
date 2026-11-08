"""Lane 1 runner for L1-K-PE (PE-Liga1 cards, X8 arm of record).

Prereg: league/PE-Liga1/prereg/PREREG_L1_K_PE.md (committed before any
sealed access). All gate arithmetic goes through league/gate_lib/:
prereg tokens are parsed mechanically, dev loading asserts no sealed
rows, the dev-pass token is recorded before any sealed load, and the
sealed window is loaded exactly once through load_sealed_rows.

The frozen engine mechanics are reused verbatim from harness.py /
model.py (run_arm, scored, coverage, predict); this runner only
controls WHICH rows reach them and WHEN.

Usage:
  python3 run_l1_k_pe.py dev     # dev evaluation + reproduction check
  python3 run_l1_k_pe.py sealed  # the single sealed read (needs dev pass)
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
from league.gate_lib.metrics import calibration_band, sign_check  # noqa: E402
import harness  # noqa: E402  (frozen engine harness)
from model import nb_over  # noqa: E402

DATA = HERE.parents[1] / "data" / "pe_liga1_matches.csv"
PREREG = HERE.parents[1] / "prereg" / "PREREG_L1_K_PE.md"
REGISTRY = HERE / "dev_pass_registry_l1.json"
DEV_OUT = HERE / "results_dev_l1.json"
VIRGIN_OUT = HERE / "results_virgin_l1.json"
CANDIDATE_ID = "L1-K-PE"
DEV = harness.DEV
VIRGIN = harness.VIRGIN
SCORED = harness.SCORED
GATE = harness.GATE  # "4.5"
SEALED_YEARS = {"2025", "2026"}

# Documented dev numbers (K_PE_VERDICT.md / cohort report section 1.2),
# pooled LL@4.5, dev n = 475. Reproduction tolerance: artefact rounding.
DOCUMENTED = {
    "gate_zero": 0.712602,
    "x8": 0.687450,
    "base": 0.707846,
    "naive": 0.692826,
}
ROUND_TOL = 1e-6


def rows_from(raw_rows, seasons):
    """Mirror harness.load() row construction/filtering exactly, but
    sourced from an explicit raw-row list (so the caller controls the
    provenance: dev-filtered rows, or the gate_lib sealed loader)."""
    allowed = set(harness.DEV + harness.VIRGIN)
    assert set(seasons) <= allowed
    out = []
    for r in raw_rows:
        if r["block"] not in seasons or r["phase"] != "regular" or r["awarded"] != "0":
            continue
        yh, ya = r["ev_yellow_inc2nd_home"], r["ev_yellow_inc2nd_away"]
        missing = yh in (None, "") or ya in (None, "")
        yh, ya = (None, None) if missing else (int(float(yh)), int(float(ya)))
        key = (r["date"] + "T00:00:00Z", r["match_id"])
        out.append({
            "match_id": r["match_id"], "season": r["block"], "date": r["date"],
            "kickoff_utc": key[0], "key": key,
            "day": date.fromisoformat(r["date"]).toordinal(),
            "home_id": r["home_team_id"], "away_id": r["away_team_id"],
            "home": r["home_team"], "away": r["away_team"],
            "yh": yh, "ya": ya, "y": None if missing else yh + ya,
            "referee": r.get("referee", "").strip(),
        })
    out = sorted(out, key=lambda x: x["key"])
    for a, b in zip(out, out[1:]):
        assert a["key"] < b["key"]
    assert {x["season"] for x in out} <= allowed
    return out


def read_raw_csv():
    with DATA.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def check_prereg_tokens():
    spec = parse_prereg(PREREG)
    assert spec.primary_line == 4.5, spec
    assert spec.calibration_tolerance_pp == 1.0, spec
    assert spec.sign_convention_stated == "predicted_minus_actual", spec
    assert str(spec.virgin_season) == "2025", spec
    assert not spec.missing_tokens, spec
    return spec


def dev():
    check_prereg_tokens()
    raw = read_raw_csv()
    kept_raw = [r for r in raw
                if r["block"] in DEV and r["phase"] == "regular" and r["awarded"] == "0"]
    # P2 design seal / P5 guard: the dev loader must contain no sealed rows.
    assert_no_sealed_rows(kept_raw, SEALED_YEARS)
    rows = rows_from(kept_raw, DEV)
    assert {r["season"] for r in rows} == set(DEV)

    arms = {}
    for arm in harness.ARMS:
        x = harness.run_arm(rows, arm, "dev")
        pooled = x["seasons"]["pooled"]
        arms[arm] = {
            "r": x["r"],
            "seasons": x["seasons"],
            "pooled_ll_4_5": {
                "model": pooled["model"][GATE]["ll"],
                "base": pooled["base"][GATE]["ll"],
                "naive": pooled["naive"][GATE]["ll"],
            },
            "per_block_ll_4_5": {
                s: x["seasons"][s]["model"][GATE]["ll"] for s in SCORED
            },
            "dev_gate_pass": (pooled["model"][GATE]["ll"] < pooled["base"][GATE]["ll"]
                              and pooled["model"][GATE]["ll"] < pooled["naive"][GATE]["ll"]),
        }

    x8 = arms["x8"]["pooled_ll_4_5"]
    repro = {
        "x8": abs(x8["model"] - DOCUMENTED["x8"]),
        "gate_zero": abs(arms["gate_zero"]["pooled_ll_4_5"]["model"] - DOCUMENTED["gate_zero"]),
        "base": abs(x8["base"] - DOCUMENTED["base"]),
        "naive": abs(x8["naive"] - DOCUMENTED["naive"]),
    }
    reproduced = all(v <= ROUND_TOL for v in repro.values())
    x8_pass = arms["x8"]["dev_gate_pass"] and x8["model"] < x8["base"] and x8["model"] < x8["naive"]
    out = {
        "protocol": {
            "candidate": CANDIDATE_ID,
            "warmup": DEV[0], "scored": list(SCORED),
            "dev_rows_loaded": len(rows), "seasons_loaded": list(DEV),
            "primary_line": 4.5, "dev_pass_token_recorded": False,
        },
        "arms": arms,
        "referee_coverage": harness.coverage(rows),
        "documented_dev_ll_4_5": DOCUMENTED,
        "reproduction_abs_diff": repro,
        "reproduced_within_rounding": reproduced,
        "x8_dev_gate_pass": bool(x8_pass),
    }
    DEV_OUT.write_text(json.dumps(out, indent=2) + "\n")
    print("dev x8 model/base/naive", x8["model"], x8["base"], x8["naive"])
    print("dev gate_zero model", arms["gate_zero"]["pooled_ll_4_5"]["model"],
          "gate_zero dev_gate_pass", arms["gate_zero"]["dev_gate_pass"])
    print("reproduction abs diffs", repro, "reproduced:", reproduced)
    if not (reproduced and x8_pass):
        print("STOP: dev reproduction failed or X8 dev gate failed; NO sealed read.")
        return 2
    record_dev_pass(REGISTRY, CANDIDATE_ID, True, str(DEV_OUT))
    out["protocol"]["dev_pass_token_recorded"] = True
    DEV_OUT.write_text(json.dumps(out, indent=2) + "\n")
    print("dev-pass token recorded for", CANDIDATE_ID)
    return 0


def sealed():
    if VIRGIN_OUT.exists():
        raise SystemExit("results_virgin_l1.json already exists: the single sealed read has already happened; refusing a second read.")
    check_prereg_tokens()
    dev_data = json.loads(DEV_OUT.read_text())
    assert dev_data["x8_dev_gate_pass"] is True and dev_data["reproduced_within_rounding"] is True

    # THE SINGLE SEALED READ: rows enter only through the gate_lib
    # sealed loader, which refuses unless the dev-pass token exists.
    all_raw = load_sealed_rows(DATA, CANDIDATE_ID, REGISTRY)
    dev_raw = [r for r in all_raw
               if r["block"] in DEV and r["phase"] == "regular" and r["awarded"] == "0"]
    virgin_raw = [r for r in all_raw
                  if r["block"] in VIRGIN and r["phase"] == "regular" and r["awarded"] == "0"]
    rows = rows_from(dev_raw + virgin_raw, DEV + VIRGIN)
    virgin_rows = [r for r in rows if r["season"] in VIRGIN]

    armdata = {}
    outarms = {}
    for arm in harness.ARMS:
        x = harness.run_arm(rows, arm, "virgin")
        armdata[arm] = x
        met = x["metrics"]
        vals = [nb_over(p["model"], x["r"]["model"], 4.5) for r, p in x["preds"]]
        ys = [int(r["y"] > 4.5) for r, p in x["preds"]]
        diff_pp, se_pp = gl_calibration(vals, ys)  # predicted - actual, gate_lib
        outarms[arm] = {
            "r": x["r"],
            "metrics": met,
            "ll_4_5": met["model"][GATE]["ll"],
            "base_ll_4_5": met["base"][GATE]["ll"],
            "naive_ll_4_5": met["naive"][GATE]["ll"],
            "calibration_pred_minus_actual_pp": diff_pp,
            "calibration_se_pp": se_pp,
            "calibration_band": calibration_band(diff_pp, se_pp, 1.0),
            "referee_fallbacks": {
                "unknown_identity": sum(p["fallback_reason"] == "unknown_identity" for r, p in x["preds"]),
                "thin_history": sum(p["fallback_reason"] == "thin_history" for r, p in x["preds"]),
            },
        }

    x8, gz = outarms["x8"], outarms["gate_zero"]
    leg_i = (x8["ll_4_5"] <= gz["ll_4_5"] and x8["ll_4_5"] <= x8["base_ll_4_5"]
             and x8["ll_4_5"] <= x8["naive_ll_4_5"])
    band = x8["calibration_band"]
    leg_ii_clean = band == "PASS"
    leg_ii_ok = band in ("PASS", "PROVISIONAL")
    wins, n_blocks, sign_ok = sign_check(
        [dev_data["arms"]["x8"]["per_block_ll_4_5"][s] for s in SCORED],
        [dev_data["arms"]["gate_zero"]["per_block_ll_4_5"][s] for s in SCORED],
    )
    passed = bool(leg_i and leg_ii_ok and sign_ok)
    if passed and leg_ii_clean:
        verdict = "CLEAN PASS"
    elif passed:
        verdict = "PROVISIONAL PASS"
    else:
        verdict = "FAIL"
    shipped = "x8" if passed else None

    out = {
        "protocol": {
            "candidate": CANDIDATE_ID, "virgin_read": True,
            "virgin_blocks": list(VIRGIN),
            "virgin_rows_loaded": len(virgin_rows),
            "virgin_n_scored": outarms["x8"]["metrics"]["model"][GATE]["n"],
        },
        "arms": outarms,
        "referee_coverage": {"dev": dev_data["referee_coverage"],
                             "virgin": harness.coverage(virgin_rows)},
        "legs": {
            "dev_gate_x8": dev_data["x8_dev_gate_pass"],
            "leg_i_ll": bool(leg_i),
            "leg_ii_calibration_band": band,
            "leg_ii_clean": bool(leg_ii_clean),
            "leg_iii_sign_check": {"wins": wins, "n": n_blocks, "pass": bool(sign_ok)},
        },
        "verdict": verdict,
        "shipped_arm": shipped,
    }
    VIRGIN_OUT.write_text(json.dumps(out, indent=2) + "\n")
    print("virgin x8 ll/base/naive", x8["ll_4_5"], x8["base_ll_4_5"], x8["naive_ll_4_5"])
    print("virgin gate_zero ll", gz["ll_4_5"])
    print("x8 calibration (pred-actual) pp/se:", x8["calibration_pred_minus_actual_pp"],
          x8["calibration_se_pp"], "band:", band)
    print("legs: (i)", leg_i, "(iii)", wins, "/", n_blocks, sign_ok)
    print("verdict", verdict, "shipped", shipped)
    if shipped:
        harness.predict(armdata[shipped], shipped)
        print("virgin predictions written for arm", shipped)
    return 0


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "dev":
        sys.exit(dev())
    elif cmd == "sealed":
        sys.exit(sealed())
    else:
        raise SystemExit("usage: run_l1_k_pe.py dev|sealed")
