"""Shared harness utilities for IQ-StarsLeague engines."""
import csv
import json
import math
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "iqsl_matches.csv"
VIRGIN = "2025/2026"


def load(seasons):
    out = []
    with DATA.open(newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["season"] not in seasons or r["phase"] != "regular":
                continue
            d = date.fromisoformat(r["date"])
            out.append({
                "match_id": r["match_id"], "date": d, "day": d.toordinal(),
                "season": r["season"], "round": r["round"], "phase": r["phase"],
                "home_id": int(r["home_team_id"]), "away_id": int(r["away_team_id"]),
                "home": r["home_team"], "away": r["away_team"],
                "gh": int(float(r["home_goals"])), "ga": int(float(r["away_goals"])),
            })
    return sorted(out, key=lambda m: (m["date"], int(m["match_id"])))


def bll(p, y):
    p = min(max(p, 1e-12), 1 - 1e-12)
    return -(y * math.log(p) + (1 - y) * math.log(1 - p))


def agg(pairs):
    """Return average log loss, rates, and calibration for (prediction, outcome)."""
    n = len(pairs)
    ps = [p for p, _ in pairs]
    ys = [y for _, y in pairs]
    diffs = [p - y for p, y in pairs]
    mean_d = sum(diffs) / n
    sd = (sum((d - mean_d) ** 2 for d in diffs) / (n - 1)) ** 0.5 if n > 1 else 0.0
    return {"n": n, "ll": sum(bll(p, y) for p, y in pairs) / n,
            "mean_pred": sum(ps) / n, "actual_rate": sum(ys) / n,
            "calibration_pp": mean_d * 100,
            "calibration_se_pp": sd / math.sqrt(n) * 100}


def calib_verdict(a):
    breach = abs(a["calibration_pp"])
    se = a["calibration_se_pp"]
    if breach <= 1.0:
        return "PASS"
    if breach <= 1.0 + se:
        return "PROVISIONAL"
    return "FAIL"


def write_json(path, obj):
    Path(path).write_text(json.dumps(obj, indent=2) + "\n")
