#!/usr/bin/env python3
"""Audit Pick Teraman against its archived candidate pools.

The archive stores market odds separately from model predictions. This script
joins each market row to that day's archived prediction snapshot, derives the
same market probabilities used by the picker, and settles against ta/results.csv.
"""
import argparse
import csv
import json
import math
import os
import sys
from collections import defaultdict


WINDOW = [f"2026-11-{day:02d}" for day in range(1, 9)] + ["2026-10-29", "2026-10-30", "2026-10-31"]
WINDOW = sorted(WINDOW)


def fnum(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def norm(value):
    return " ".join((value or "").strip().lower().split())


def key(row):
    return (row.get("game_id", ""), row.get("date", ""),
            norm(row.get("home")), norm(row.get("away")))


def model_probability(pred, market, line, selection):
    ph, pd, pa = (fnum(pred.get(c)) for c in ("ph_dc", "pd_dc", "pa_dc"))
    if None in (ph, pd, pa):
        return None, 0.0
    if market == "1X2":
        return {"1": ph, "X": pd, "2": pa}.get(selection), 0.0
    if market == "DC":
        return {"1X": ph + pd, "X2": pd + pa, "12": ph + pa}.get(selection), 0.0
    if market == "DNB":
        return ({"Dnb1": ph, "Dnb2": pa}.get(selection), pd)
    if market == "BTS":
        return (fnum(pred.get("p_btts")), 0.0) if selection == "Yes" else (1 - fnum(pred.get("p_btts")), 0.0)
    if market == "OU":
        ln = fnum(line)
        col = {1.5: "p_over15_dc", 2.5: "p_over_dc", 3.5: "p_over35_dc"}.get(ln)
        over = fnum(pred.get(col)) if col else None
        if over is None:
            return None, 0.0
        return (over if selection == "Over" else 1 - over), 0.0
    return None, 0.0


def settle(sh, sa, market, line, selection):
    if market == "1X2":
        return "hit" if ((selection == "1" and sh > sa) or
                          (selection == "X" and sh == sa) or
                          (selection == "2" and sa > sh)) else "lose"
    if market == "DC":
        return "hit" if ((selection == "1X" and sh >= sa) or
                          (selection == "X2" and sa >= sh) or
                          (selection == "12" and sh != sa)) else "lose"
    if market == "DNB":
        if sh == sa:
            return "push"
        return "hit" if ((selection == "Dnb1" and sh > sa) or
                          (selection == "Dnb2" and sa > sh)) else "lose"
    if market == "BTS":
        yes = sh > 0 and sa > 0
        return "hit" if yes == (selection == "Yes") else "lose"
    if market == "OU":
        total = sh + sa
        ln = fnum(line)
        if total == ln:
            return "push"
        return "hit" if ((selection == "Over" and total > ln) or
                          (selection == "Under" and total < ln)) else "lose"
    return None


def metrics(rows):
    usable = [r for r in rows if r["status"] in ("hit", "lose")]
    if not usable:
        return {"n": 0, "mean_predicted": None, "hit_rate": None,
                "gap_pp": None, "brier": None, "log_loss": None}
    ys = [1.0 if r["status"] == "hit" else 0.0 for r in usable]
    ps = [r["prob"] for r in usable]
    return {
        "n": len(usable),
        "mean_predicted": sum(ps) / len(ps),
        "hit_rate": sum(ys) / len(ys),
        "gap_pp": 100 * (sum(ys) / len(ys) - sum(ps) / len(ps)),
        "brier": sum((p - y) ** 2 for p, y in zip(ps, ys)) / len(ps),
        "log_loss": -sum(y * math.log(max(p, 1e-15)) +
                           (1 - y) * math.log(max(1 - p, 1e-15))
                           for p, y in zip(ps, ys)) / len(ps),
    }


def grouped(rows, field):
    out = {}
    for value in sorted({r.get(field, "") for r in rows}):
        out[value or "(blank)"] = metrics([r for r in rows if r.get(field, "") == value])
    return out


def read_csv(path):
    with open(path, newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default="/home/hatch/workspace/footballprediction")
    args = parser.parse_args()
    root = os.path.abspath(args.root)
    here = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, root)

    results = {}
    for row in read_csv(os.path.join(root, "ta", "results.csv")):
        results[row.get("game_id", "")] = row
        results[(row.get("date", ""), norm(row.get("home")), norm(row.get("away")))] = row

    candidates = []
    excluded = defaultdict(int)
    for day in WINDOW:
        archive = os.path.join(root, "archive", day)
        pred_rows = []
        for filename in ("predictions_upcoming.csv", "predictions_cups_upcoming.csv"):
            path = os.path.join(archive, filename)
            if os.path.exists(path):
                pred_rows.extend(read_csv(path))
        pred_by_key = {key(r): r for r in pred_rows}
        pred_by_match = {(r.get("date", ""), norm(r.get("home")), norm(r.get("away"))): r
                         for r in pred_rows}
        for row in read_csv(os.path.join(archive, "market_compare.csv")):
            pred = pred_by_key.get(key(row)) or pred_by_match.get(
                (row.get("date", ""), norm(row.get("home")), norm(row.get("away"))))
            if pred is None:
                excluded["missing_prediction"] += 1
                continue
            prob, p_push = model_probability(pred, row["market"], row.get("line", ""), row["selection"])
            if prob is None:
                excluded["missing_model_probability"] += 1
                continue
            result = results.get(row.get("game_id", "")) or results.get(
                (row.get("date", ""), norm(row.get("home")), norm(row.get("away"))))
            if result is None or result.get("status", "").upper() not in ("FT", "FINISHED"):
                excluded["missing_result"] += 1
                continue
            sh, sa = fnum(result.get("score_h")), fnum(result.get("score_a"))
            status = settle(sh, sa, row["market"], row.get("line", ""), row["selection"])
            if status is None:
                excluded["unsupported_market"] += 1
                continue
            # For push markets, compare hit/loss calibration on the conditional basis.
            if p_push < 1:
                prob = prob / (1 - p_push)
            candidates.append({"date": day, "game_id": row.get("game_id", ""),
                              "home": row.get("home", ""), "away": row.get("away", ""),
                              "market": row["market"], "selection": row["selection"],
                              "prob": prob, "p_push": p_push, "status": status})

    ledger = []
    with open(os.path.join(root, "ledger", "daily_pick_grades.jsonl"), encoding="utf-8") as handle:
        for line in handle:
            row = json.loads(line)
            if (row.get("product") == "pick_teraman" and row.get("level") == "leg" and
                    row.get("date") in WINDOW and row.get("status") in ("hit", "lose")):
                ledger.append({"date": row["date"], "market": row.get("market", ""),
                               "tier": row.get("tier", ""), "prob": fnum(row.get("p_model")),
                               "status": row["status"]})

    pool_max = []
    by_match = defaultdict(list)
    for row in candidates:
        by_match[(row["date"], row["game_id"], norm(row["home"]), norm(row["away"]))].append(row)
    for rows in by_match.values():
        pool_max.append(max(rows, key=lambda r: r["prob"]))

    output = {
        "window": [WINDOW[0], WINDOW[-1]],
        "ledger_selection_basis": "product=pick_teraman, level=leg, status in {hit, lose}; p_model from ledger",
        "candidate_probability_basis": "archived prediction snapshots; DNB conditional on no push",
        "selected": {"overall": metrics(ledger), "by_market": grouped(ledger, "market"),
                     "by_tier": grouped(ledger, "tier")},
        "candidate_pool": {"overall": metrics(candidates), "by_market": grouped(candidates, "market")},
        "pool_maximum": {"overall": metrics(pool_max), "by_market": grouped(pool_max, "market")},
        "counts": {"candidate_rows_settled_or_push": len(candidates),
                   "candidate_pushes": sum(r["status"] == "push" for r in candidates),
                   "pool_max_matches": len(pool_max), "selected_rows": len(ledger),
                   "excluded": dict(excluded)},
    }
    json_path = os.path.join(here, "audit_pick_teraman.json")
    csv_path = os.path.join(here, "audit_pick_teraman.csv")
    with open(json_path, "w", encoding="utf-8") as handle:
        json.dump(output, handle, indent=2, sort_keys=True)
    with open(csv_path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["population", "group", "n", "mean_predicted",
                                                     "hit_rate", "gap_pp", "brier", "log_loss"])
        writer.writeheader()
        for population in ("selected", "candidate_pool", "pool_maximum"):
            for group, stat in output[population].items():
                if isinstance(stat, dict) and "n" in stat:
                    writer.writerow({"population": population, "group": group, **stat})
                elif isinstance(stat, dict):
                    for subgroup, substat in stat.items():
                        writer.writerow({"population": population, "group": f"{group}:{subgroup}", **substat})
    print(json_path)
    print(csv_path)


if __name__ == "__main__":
    main()
