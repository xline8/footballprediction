"""Shared harness utilities for the MX-ExpansionMX engines.

Rows come from the league CSV when it exists; otherwise they are
built in memory through data/build_data.py's load_rows() (identical
code path — the CSV is a cache of exactly those rows).
"""
import csv, json, math, sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_CSV = ROOT / "data" / "mxe_matches.csv"
BLOCKS = ["2021/2022 - Apertura", "2021/2022 - Clausura",
          "2022/2023 - Apertura", "2022/2023 - Clausura",
          "2023/2024 - Apertura", "2023/2024 - Clausura",
          "2024/2025 - Apertura", "2024/2025 - Clausura",
          "2025/2026 - Apertura", "2025/2026 - Clausura"]


def load(blocks):
    """Modelling-population rows (finished, regular) for the given blocks."""
    if DATA_CSV.exists() and DATA_CSV.stat().st_size > 0:
        raw = []
        with DATA_CSV.open(newline="", encoding="utf-8") as f:
            for r in csv.DictReader(f):
                if r["block"] not in blocks or r["finished"] != "1" or r["phase"] != "regular":
                    continue
                raw.append({"match_id": r["match_id"], "block": r["block"],
                            "block_idx": int(r["block_idx"]), "date": date.fromisoformat(r["date"]),
                            "home_id": int(r["home_team_id"]), "away_id": int(r["away_team_id"]),
                            "home": r["home_team"], "away": r["away_team"],
                            "gh": int(float(r["home_goals"])), "ga": int(float(r["away_goals"])),
                            "yh": int(float(r["yellow_home"])), "ya": int(float(r["yellow_away"]))})
    else:
        sys.path.insert(0, str(ROOT / "data"))
        import build_data as bd
        raw = [{"match_id": r["match_id"], "block": r["block"], "block_idx": r["block_idx"],
                "date": date.fromisoformat(r["date"]), "home_id": r["home_team_id"],
                "away_id": r["away_team_id"], "home": r["home_team"], "away": r["away_team"],
                "gh": r["home_goals"], "ga": r["away_goals"],
                "yh": r["yellow_home"], "ya": r["yellow_away"]}
               for r in bd.load_rows()
               if r["block"] in blocks and r["finished"] == 1 and r["phase"] == "regular"]
    return sorted(raw, key=lambda m: (m["date"], int(m["match_id"])))


def agg(pairs):
    n = len(pairs)
    ps = [p for p, _ in pairs]; ys = [y for _, y in pairs]
    diffs = [y - p for p, y in pairs]; mean_d = sum(diffs) / n
    sd = (sum((d - mean_d) ** 2 for d in diffs) / (n - 1)) ** 0.5 if n > 1 else 0.0
    return {"n": n, "ll": sum(-math.log(min(max(p, 1e-12), 1 - 1e-12)) if y else -math.log(1 - min(max(p, 1e-12), 1 - 1e-12)) for p, y in pairs) / n,
            "mean_pred": sum(ps) / n, "actual_rate": sum(ys) / n,
            "calibration_pp": mean_d * 100, "calibration_se_pp": sd / math.sqrt(n) * 100}


def calib_verdict(a):
    b = abs(a["calibration_pp"]); se = a["calibration_se_pp"]
    if b <= 1.0:
        return "PASS"
    if b <= 1.0 + se:
        return "PROVISIONAL"
    return "FAIL"


def write_json(path, obj):
    try:
        Path(path).write_text(json.dumps(obj, indent=2) + "\n")
    except OSError as e:
        print(f"WRITE_FAILED {path}: {e}", file=sys.stderr)
