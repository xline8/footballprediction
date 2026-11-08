"""Lane 1 runner for L1-K-FO (FO-PremierLeague cards, SHRINK arm of record).

Prereg: league/FO-PremierLeague/prereg/PREREG_L1_K_FO.md (committed
before any sealed access). All gate arithmetic goes through
league/gate_lib/: prereg tokens are parsed mechanically, dev loading
asserts no sealed rows, the dev-pass token is recorded before any
sealed load, and the sealed window is loaded exactly once through
load_sealed_rows.

The frozen engine mechanics are reused verbatim from model.py
(Online / estimate_r / nb_over, Gate Zero Online(8), SHRINK
Online(16)); this runner only controls WHICH rows reach them and
WHEN, and how the gate legs are computed (gate_lib).

Usage:
  python3 run_l1_k_fo.py dev     # dev evaluation + reproduction check
  python3 run_l1_k_fo.py sealed  # the single sealed read (needs dev pass)
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

DATA = HERE.parents[1] / "data" / "fo_premier_league_matches.csv"
PREREG = HERE.parents[1] / "prereg" / "PREREG_L1_K_FO.md"
REGISTRY = HERE / "dev_pass_registry_l1.json"
DEV_OUT = HERE / "results_dev_l1.json"
VIRGIN_OUT = HERE / "results_virgin_l1.json"
FITTED_OUT = HERE / "fitted_params_virgin_l1.json"
PRED_OUT = HERE.parents[1] / "predictions" / "k_fo_virgin_predictions.csv"
CANDIDATE_ID = "L1-K-FO"
WARMUP = "2021"
SCORED = ("2022", "2023", "2024", "2025")
DEV_SEASONS = (WARMUP,) + SCORED
VIRGIN = "2026"
SEALED_SEASONS = {VIRGIN}
ARMS = {"gate_zero": 8, "shrink": 16}
HALVES_SHARE_1H = 0.348

# Documented dev numbers (K_FO_VERDICT.md / cohort report section 1.2,
# full precision from the persisted results_dev.json), pooled LL@3.5,
# dev n = 539. Reproduction tolerance: artefact rounding.
DOCUMENTED = {
    "gate_zero": 0.6847357883037525,
    "shrink": 0.6810001160073882,
    "base": 0.6824203648810964,
    "naive": 0.6930443087223409,
}
ROUND_TOL = 1e-6


def rows_from(raw_rows, seasons):
    """Mirror harness.load() row construction/filtering exactly, but
    sourced from an explicit raw-row list (so the caller controls the
    provenance: dev-filtered rows, or the gate_lib sealed loader)."""
    allowed = set(seasons)
    out = []
    for r in raw_rows:
        if r["season"] not in allowed:
            continue
        if r["excluded"] == "1" or not r["yellow_home"] or not r["yellow_away"]:
            continue
        yh, ya = int(r["yellow_home"]), int(r["yellow_away"])
        out.append({
            "match_id": r["match_id"], "season": r["season"],
            "date": date.fromisoformat(r["date"]),
            "day": date.fromisoformat(r["date"]).toordinal(),
            "home_id": int(r["home_team_id"]), "away_id": int(r["away_team_id"]),
            "home": r["home"], "away": r["away"],
            "yh": yh, "ya": ya, "y": yh + ya,
        })
    out.sort(key=lambda x: (x["date"], x["match_id"]))
    return out


def read_raw_csv():
    with DATA.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def check_prereg_tokens():
    spec = parse_prereg(PREREG)
    assert spec.primary_line == 3.5, spec
    assert spec.ladder == [1.5, 2.5, 3.5, 4.5], spec
    assert spec.calibration_tolerance_pp == 1.0, spec
    assert spec.sign_convention_stated == "predicted_minus_actual", spec
    assert str(spec.virgin_season) == "2026", spec
    assert not spec.missing_tokens, spec
    return spec


def score(records, rmap):
    """Per-method LL/mean/actual at 3.5 and 4.5; LL via gate_lib."""
    z = {}
    for method in ("model", "base", "naive"):
        z[method] = {}
        for line in (3.5, 4.5):
            ps = [nb_over(x[method], rmap[method], line) for x in records]
            ys = [int(x["y"] > line) for x in records]
            n = len(records)
            z[method][str(line)] = {
                "n": n,
                "ll": sum(log_loss(p, y) for p, y in zip(ps, ys)) / n,
                "mean_p": sum(ps) / n,
                "actual_rate": sum(ys) / n,
            }
    return z


def walk(rows, scored_seasons, r_source_seasons):
    """One chronological online pass for both arms.

    Predictions are collected for every row; the NB size r per arm /
    method is estimated (frozen discipline) from the causal records
    of `r_source_seasons` only. Returns per-arm r maps, per-season
    scored records, snapshots at the first scored-season cutoff of
    the second phase (used by the virgin phase), and the virgin-phase
    raw predictions keyed by (arm, match_id).
    """
    ons = {a: Online(k) for a, k in ARMS.items()}
    records = {a: [] for a in ons}          # every row, in order
    by_season = {a: {} for a in ons}
    snapshots = {}
    for r in rows:
        if r["season"] in scored_seasons and "cutoff" not in snapshots:
            day = r["day"]
            snapshots["cutoff"] = {a: o.state.snapshot(day) for a, o in ons.items()}
            snapshots["cutoff_date"] = r["date"].isoformat()
        preds = {a: o.predict(r) for a, o in ons.items()}
        for a, p in preds.items():
            rec = {"y": r["y"], "row": r,
                   **{k: p[k] for k in ("model", "base", "naive")},
                   "eh": p["eh"], "ea": p["ea"]}
            records[a].append(rec)
            by_season[a].setdefault(r["season"], []).append(rec)
        for o in ons.values():
            o.update(r)
    rmap = {}
    for a in ons:
        src = [rec for rec in records[a] if rec["row"]["season"] in r_source_seasons]
        rmap[a] = {m: estimate_r(src, m) for m in ("model", "base", "naive")}
    return ons, records, by_season, rmap, snapshots


def dev():
    check_prereg_tokens()
    raw = read_raw_csv()
    kept_raw = [r for r in raw if r["season"] in DEV_SEASONS]
    # P2 design seal / P5 guard: the dev loader must contain no sealed rows.
    assert_no_sealed_rows(kept_raw, SEALED_SEASONS)
    rows = rows_from(kept_raw, DEV_SEASONS)
    assert len(rows) == 674 and not any(x["season"] == VIRGIN for x in rows)

    # Frozen discipline: r from the 2021 warm-up causal records only.
    _, _, by_season, rmap, _ = walk(rows, SCORED, (WARMUP,))

    arms = {}
    for a in ARMS:
        seasons = {s: score(by_season[a][s], rmap[a]) for s in SCORED}
        pooled_records = sum((by_season[a][s] for s in SCORED), [])
        seasons["pooled"] = score(pooled_records, rmap[a])
        pooled = seasons["pooled"]
        arms[a] = {
            "r": rmap[a],
            "seasons": seasons,
            "pooled_ll_3_5": {
                "model": pooled["model"]["3.5"]["ll"],
                "base": pooled["base"]["3.5"]["ll"],
                "naive": pooled["naive"]["3.5"]["ll"],
            },
            "per_season_ll_3_5": {s: seasons[s]["model"]["3.5"]["ll"] for s in SCORED},
            "dev_gate_pass": (pooled["model"]["3.5"]["ll"] < pooled["base"]["3.5"]["ll"]
                              and pooled["model"]["3.5"]["ll"] < pooled["naive"]["3.5"]["ll"]),
        }

    shrink = arms["shrink"]["pooled_ll_3_5"]
    repro = {
        "shrink": abs(shrink["model"] - DOCUMENTED["shrink"]),
        "gate_zero": abs(arms["gate_zero"]["pooled_ll_3_5"]["model"] - DOCUMENTED["gate_zero"]),
        "base": abs(shrink["base"] - DOCUMENTED["base"]),
        "naive": abs(shrink["naive"] - DOCUMENTED["naive"]),
    }
    reproduced = all(v <= ROUND_TOL for v in repro.values())
    shrink_pass = bool(arms["shrink"]["dev_gate_pass"]
                       and shrink["model"] < shrink["base"] and shrink["model"] < shrink["naive"])
    wins, n_seasons, sign_ok = sign_check(
        [arms["shrink"]["per_season_ll_3_5"][s] for s in SCORED],
        [arms["gate_zero"]["per_season_ll_3_5"][s] for s in SCORED],
    )
    out = {
        "protocol": {
            "candidate": CANDIDATE_ID,
            "warmup": WARMUP, "scored": list(SCORED),
            "dev_rows_loaded": len(rows), "seasons_loaded": list(DEV_SEASONS),
            "primary_line": 3.5, "dev_pass_token_recorded": False,
        },
        "arms": arms,
        "documented_dev_ll_3_5": DOCUMENTED,
        "reproduction_abs_diff": repro,
        "reproduced_within_rounding": reproduced,
        "shrink_dev_gate_pass": shrink_pass,
        "sign_check_shrink_vs_gate_zero": {"wins": wins, "n": n_seasons, "pass": bool(sign_ok)},
    }
    DEV_OUT.write_text(json.dumps(out, indent=2) + "\n")
    print("dev shrink model/base/naive", shrink["model"], shrink["base"], shrink["naive"])
    print("dev gate_zero model", arms["gate_zero"]["pooled_ll_3_5"]["model"],
          "gate_zero dev_gate_pass", arms["gate_zero"]["dev_gate_pass"])
    print("sign check shrink vs gate_zero:", wins, "/", n_seasons, sign_ok)
    print("reproduction abs diffs", repro, "reproduced:", reproduced)
    if not (reproduced and shrink_pass):
        print("STOP: dev reproduction failed or SHRINK dev gate failed; NO sealed read.")
        return 2
    record_dev_pass(REGISTRY, CANDIDATE_ID, True, str(DEV_OUT))
    out["protocol"]["dev_pass_token_recorded"] = True
    DEV_OUT.write_text(json.dumps(out, indent=2) + "\n")
    print("dev-pass token recorded for", CANDIDATE_ID)
    return 0


def sealed():
    if VIRGIN_OUT.exists():
        raise SystemExit("results_virgin_l1.json already exists: the single sealed "
                         "read has already happened; refusing a second read.")
    check_prereg_tokens()
    dev_data = json.loads(DEV_OUT.read_text())
    assert dev_data["shrink_dev_gate_pass"] is True and dev_data["reproduced_within_rounding"] is True

    # THE SINGLE SEALED READ: rows enter only through the gate_lib
    # sealed loader, which refuses unless the dev-pass token exists.
    all_raw = load_sealed_rows(DATA, CANDIDATE_ID, REGISTRY)
    rows = rows_from(all_raw, DEV_SEASONS + (VIRGIN,))
    virgin_rows = [r for r in rows if r["season"] == VIRGIN]
    assert len(virgin_rows) == 135, len(virgin_rows)

    # Frozen discipline: r re-estimated from causal predictions over
    # 2021-2025 only, then frozen for 2026.
    _, _, by_season, rmap, snapshots = walk(rows, (VIRGIN,), DEV_SEASONS)

    outarms = {}
    virgin_preds = {}
    for a in ARMS:
        recs = by_season[a][VIRGIN]
        met = score(recs, rmap[a])
        ps = [nb_over(x["model"], rmap[a]["model"], 3.5) for x in recs]
        ys = [int(x["y"] > 3.5) for x in recs]
        diff_pp, se_pp = gl_calibration(ps, ys)  # predicted - actual, gate_lib
        outarms[a] = {
            "r": rmap[a],
            "metrics": met,
            "ll_3_5": met["model"]["3.5"]["ll"],
            "base_ll_3_5": met["base"]["3.5"]["ll"],
            "naive_ll_3_5": met["naive"]["3.5"]["ll"],
            "calibration_pred_minus_actual_pp": diff_pp,
            "calibration_se_pp": se_pp,
            "calibration_band": calibration_band(diff_pp, se_pp, 1.0),
        }
        virgin_preds[a] = recs

    sh, gz = outarms["shrink"], outarms["gate_zero"]
    best_baseline = min(sh["base_ll_3_5"], sh["naive_ll_3_5"])
    leg_i = (sh["ll_3_5"] <= gz["ll_3_5"] and sh["ll_3_5"] <= best_baseline)
    band = sh["calibration_band"]
    leg_ii_clean = band == "PASS"
    leg_ii_ok = band in ("PASS", "PROVISIONAL")
    wins = dev_data["sign_check_shrink_vs_gate_zero"]["wins"]
    n_seasons = dev_data["sign_check_shrink_vs_gate_zero"]["n"]
    sign_ok = dev_data["sign_check_shrink_vs_gate_zero"]["pass"]
    passed = bool(leg_i and leg_ii_ok and sign_ok)
    if passed and leg_ii_clean:
        verdict = "CLEAN PASS"
    elif passed:
        verdict = "PROVISIONAL PASS"
    else:
        verdict = "FAIL"
    shipped = "shrink" if passed else None

    out = {
        "protocol": {
            "candidate": CANDIDATE_ID, "virgin_read": True,
            "virgin_window": VIRGIN,
            "virgin_rows_loaded": len(virgin_rows),
            "virgin_n_scored": outarms["shrink"]["metrics"]["model"]["3.5"]["n"],
        },
        "arms": outarms,
        "legs": {
            "dev_gate_shrink": dev_data["shrink_dev_gate_pass"],
            "leg_i_ll": bool(leg_i),
            "leg_ii_calibration_band": band,
            "leg_ii_clean": bool(leg_ii_clean),
            "leg_iii_sign_check": {"wins": wins, "n": n_seasons, "pass": bool(sign_ok)},
        },
        "verdict": verdict,
        "shipped_arm": shipped,
    }
    VIRGIN_OUT.write_text(json.dumps(out, indent=2) + "\n")
    print("virgin shrink ll/base/naive", sh["ll_3_5"], sh["base_ll_3_5"], sh["naive_ll_3_5"])
    print("virgin gate_zero ll", gz["ll_3_5"])
    print("shrink calibration (pred-actual) pp/se:", sh["calibration_pred_minus_actual_pp"],
          sh["calibration_se_pp"], "band:", band)
    print("legs: (i)", leg_i, "(iii)", wins, "/", n_seasons, sign_ok)
    print("verdict", verdict, "shipped", shipped)
    if shipped:
        # Fitted params at the 2026 cutoff (snapshot taken before the
        # first virgin prediction, after every pre-2026 update).
        fitted = {
            "arm": shipped, "hl": 270.0, "k_prior": ARMS[shipped],
            "r": rmap[shipped],
            "cutoff_date": snapshots.get("cutoff_date"),
            "snapshot": snapshots["cutoff"][shipped],
        }
        FITTED_OUT.write_text(json.dumps(fitted, indent=2) + "\n")
        # Virgin predictions for the shipped arm (SHRINK), FT ladder +
        # halves via the frozen cards constant 0.348 (presentation only).
        PRED_OUT.parent.mkdir(parents=True, exist_ok=True)
        r_model = rmap[shipped]["model"]
        fields = ["match_id", "season", "date", "home_team_id", "away_team_id", "home", "away",
                  "yellows_total", "expected_home", "expected_away", "expected_total",
                  "p_over_1_5", "p_over_2_5", "p_over_3_5", "p_over_4_5",
                  "mean_1h", "mean_2h",
                  "p_1h_over_0_5", "p_1h_over_1_5", "p_1h_over_2_5",
                  "p_2h_over_1_5", "p_2h_over_2_5", "p_2h_over_3_5", "arm"]
        with PRED_OUT.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=fields)
            w.writeheader()
            for rec in virgin_preds[shipped]:
                r = rec["row"]
                mu, m1, m2 = rec["model"], HALVES_SHARE_1H * rec["model"], (1 - HALVES_SHARE_1H) * rec["model"]
                row = {"match_id": r["match_id"], "season": r["season"], "date": r["date"].isoformat(),
                       "home_team_id": r["home_id"], "away_team_id": r["away_id"],
                       "home": r["home"], "away": r["away"], "yellows_total": r["y"],
                       "expected_home": rec["eh"], "expected_away": rec["ea"], "expected_total": mu,
                       "mean_1h": m1, "mean_2h": m2, "arm": shipped}
                row.update({f"p_over_{str(l).replace('.', '_')}": nb_over(mu, r_model, l)
                            for l in (1.5, 2.5, 3.5, 4.5)})
                row.update({f"p_1h_over_{str(l).replace('.', '_')}": nb_over(m1, r_model, l)
                            for l in (0.5, 1.5, 2.5)})
                row.update({f"p_2h_over_{str(l).replace('.', '_')}": nb_over(m2, r_model, l)
                            for l in (1.5, 2.5, 3.5)})
                w.writerow(row)
        print("virgin predictions + fitted params written for arm", shipped)
    return 0


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "dev":
        sys.exit(dev())
    elif cmd == "sealed":
        sys.exit(sealed())
    else:
        raise SystemExit("usage: run_l1_k_fo.py dev|sealed")
