"""Shared harness utilities for the CLA goals engine."""
import csv, json, math
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "cla_matches.csv"
PARENT = ROOT.parent / "CL-LigaDePrimera" / "data" / "cl_matches.csv"
VIRGIN = "2025"

def load(seasons):
    out = []
    with DATA.open(newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["season"] not in seasons or r["finished"] != "1" or r["phase"] != "regular":
                continue
            out.append({"match_id": r["match_id"], "date": date.fromisoformat(r["date"]),
                        "season": r["season"], "round": r["round"], "phase": r["phase"],
                        "home_id": int(r["home_team_id"]), "away_id": int(r["away_team_id"]),
                        "home": r["home_team"], "away": r["away_team"],
                        "gh": int(float(r["home_goals"])), "ga": int(float(r["away_goals"]))})
    return sorted(out, key=lambda m: (m["date"], int(m["match_id"])))

def agg(pairs):
    n = len(pairs); ps = [p for p, _ in pairs]; ys = [y for _, y in pairs]
    diffs = [y - p for p, y in pairs]; mean_d = sum(diffs) / n
    sd = (sum((d - mean_d) ** 2 for d in diffs) / (n - 1)) ** 0.5 if n > 1 else 0.0
    return {"n": n, "ll": sum(-math.log(min(max(p, 1e-12), 1 - 1e-12)) if y else -math.log(1 - min(max(p, 1e-12), 1 - 1e-12)) for p, y in pairs) / n,
            "mean_pred": sum(ps) / n, "actual_rate": sum(ys) / n,
            "calibration_pp": mean_d * 100, "calibration_se_pp": sd / math.sqrt(n) * 100}

def calib_verdict(a):
    b = abs(a["calibration_pp"]); se = a["calibration_se_pp"]
    if b <= 1.0: return "PASS"
    if b <= 1.0 + se: return "PROVISIONAL"
    return "FAIL"

def write_json(path, obj):
    Path(path).write_text(json.dumps(obj, indent=2) + "\n")
