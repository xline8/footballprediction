"""P3 Gate Zero driver: runs all 6 sampled leagues sequentially,
writes results.json, results.csv and per-league detail JSONs into
league/improvement_scratch/P3/.

Usage (from repo root):
  .venv/bin/python league/improvement_scratch/P3/code/run_p3.py
"""
import csv
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from vc_goals import run_goals_league          # noqa: E402
from vc_sot import run_sot_league, EngineVC, load_league_matches, walk_generic, estimate_K  # noqa: E402
from datetime import date  # noqa: E402

OUT = Path(__file__).resolve().parents[1]

GOALS_ORDER = ["MD-NationalDivision", "SG-PremierLeague", "J3", "MX-ExpansionMX"]
SOT_ORDER = ["LV-Virsliga", "SA-FirstDivision"]


def sot_component_snapshot(league):
    """Final-walk estimated K / ratio-prior values for the report."""
    _, ms = load_league_matches(league)
    lines = (8.5, 9.5, 10.5) if league == "LV-Virsliga" else (7.5, 8.5, 9.5)
    eng = EngineVC(ms, lines, "vc")
    if league == "LV-Virsliga":
        sf = lambda m: m["date"] >= date(2025, 5, 1)
    else:
        sf = lambda m: True
    walk_generic(ms, eng.predict, eng.update, sf)
    last_day = ms[-1]["day"]
    div = ms[-1]["div"]
    mh, ma = eng.ratings.league_mu(div, last_day)
    Ks = {}
    for name, group, mu in (("att_h", eng.ratings.att_h, mh), ("def_a", eng.ratings.def_a, mh),
                            ("att_a", eng.ratings.att_a, ma), ("def_h", eng.ratings.def_h, ma)):
        K, info = estimate_K(list(group.values()), last_day)
        Ks[name] = {"K": K, "tau_m": (info or {}).get("tau_m")}
    ratios = {v: {"prior": p, **(i or {})}
              for v, (p, i) in eng.ratings.last_ratio.items()}
    return {"K_final": Ks, "ratio_prior_final": ratios}


def main():
    details = {}
    rows = []
    for lg in GOALS_ORDER:
        o = run_goals_league(lg)
        details[lg] = o
        shipped = o["shipped"]["oull_2_5"]
        repl = o["gz_replication"]["pooled"]["oull_2_5"]
        vc = o["vc"]["pooled"]
        rows.append({"league": lg, "bucket": o["bucket"],
                     "stats_seasons": o["stats_seasons"], "market": "goals",
                     "primary_metric": "OU2.5 LL",
                     "n_dev": vc["n"],
                     "shipped_gz_ll": shipped,
                     "gz_replication_ll": repl,
                     "replication_abs_diff": abs(repl - shipped),
                     "vc_ll": vc["oull_2_5"],
                     "delta_vc_minus_shipped": vc["oull_2_5"] - shipped,
                     "improved": vc["oull_2_5"] < shipped,
                     "secondary_metric": "1X2 LL",
                     "shipped_secondary": o["shipped"]["ll_1x2"],
                     "vc_secondary": vc["ll_1x2"],
                     "delta_secondary": vc["ll_1x2"] - o["shipped"]["ll_1x2"]})
        print(lg, "done", flush=True)
    for lg in SOT_ORDER:
        o = run_sot_league(lg)
        o["vc_components"]["snapshot"] = sot_component_snapshot(lg)
        details[lg] = o
        shipped = o["shipped"]["ll_primary"]
        repl = o["gz_replication"]["ll_primary"]
        vc = o["vc"]
        rows.append({"league": lg, "bucket": o["bucket"],
                     "stats_seasons": o["stats_seasons"], "market": "sot",
                     "primary_metric": f"LL@{o['primary_line']}",
                     "n_dev": vc["n"],
                     "shipped_gz_ll": shipped,
                     "gz_replication_ll": repl,
                     "replication_abs_diff": abs(repl - shipped),
                     "vc_ll": vc["ll_primary"],
                     "delta_vc_minus_shipped": vc["ll_primary"] - shipped,
                     "improved": vc["ll_primary"] < shipped,
                     "secondary_metric": "ladder LLs",
                     "shipped_secondary": None,
                     "vc_secondary": None,
                     "delta_secondary": None})
        print(lg, "done", flush=True)

    n_improved = sum(r["improved"] for r in rows)
    worst = max(r["delta_vc_minus_shipped"] for r in rows)
    verdict_pass = n_improved >= 5 and worst <= 0.002
    summary = {"n_leagues": len(rows), "n_improved": n_improved,
               "worst_delta": worst,
               "rule": "PASS iff pooled dev LL improves in >=5/6 leagues AND no league worse by >0.002",
               "verdict": "PASS" if verdict_pass else "FAIL (P3 dies)"}
    (OUT / "results.json").write_text(json.dumps(
        {"summary": summary, "rows": rows, "details": details}, indent=2) + "\n")
    (OUT / "details").mkdir(exist_ok=True)
    for lg, o in details.items():
        (OUT / "details" / f"{lg}.json").write_text(json.dumps(o, indent=2) + "\n")
    with open(OUT / "results.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(json.dumps(summary, indent=2))
    for r in rows:
        print(f"{r['league']:24s} {r['market']:5s} shipped {r['shipped_gz_ll']:.6f} "
              f"vc {r['vc_ll']:.6f} delta {r['delta_vc_minus_shipped']:+.6f} "
              f"improved={r['improved']}")


if __name__ == "__main__":
    main()
