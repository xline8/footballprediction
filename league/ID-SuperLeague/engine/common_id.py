"""Shared harness utilities for ID-SuperLeague engines (direct implementation).

Protocol (frozen preregs): season-blocked walk-forward. Count markets:
seed season 2022/2023 (first season whose target exists) warms state and
tunes parameters; scored dev seasons 2023/2024 + 2024/2025; virgin
2025/2026 read once, only if Gate Zero passes dev. Goals: seed
2021/2022, scored 2022/2023-2024/2025. 2026/2027 is never loaded.
"""
import csv, json, math
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "id_matches.csv"
VIRGIN = "2025/2026"

def num(x):
    return None if x in ("", None) else float(x)

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
                "sot_h": num(r.get("ShotsOnTarget_home")), "sot_a": num(r.get("ShotsOnTarget_away")),
                "cor_h": num(r.get("corners_home")), "cor_a": num(r.get("corners_away")),
                "shots_h": num(r.get("total_shots_home")), "shots_a": num(r.get("total_shots_away")),
                "cards_h": num(r.get("yellow_home")),
                "cards_a": num(r.get("yellow_away")),
                "bt_h": num(r.get("touches_opp_box_home")), "bt_a": num(r.get("touches_opp_box_away")),
                "referee": r.get("referee", "") or "",
            })
    return sorted(out, key=lambda m: (m["date"], int(m["match_id"])))

def bll(p, y):
    p = min(max(p, 1e-12), 1 - 1e-12)
    return -(y * math.log(p) + (1 - y) * math.log(1 - p))

def agg(pairs):
    """pairs: list of (p, y). Returns headline metrics incl. calibration."""
    n = len(pairs)
    ps = [p for p, _ in pairs]; ys = [y for _, y in pairs]
    diffs = [p - y for p, y in pairs]
    mean_d = sum(diffs) / n
    sd = (sum((d - mean_d) ** 2 for d in diffs) / (n - 1)) ** 0.5 if n > 1 else 0.0
    return {"n": n, "ll": sum(bll(p, y) for p, y in pairs) / n,
            "mean_pred": sum(ps) / n, "actual_rate": sum(ys) / n,
            "calibration_pp": mean_d * 100, "calibration_se_pp": sd / math.sqrt(n) * 100}

def calib_verdict(a):
    b = abs(a["calibration_pp"]); se = a["calibration_se_pp"]
    if b <= 1.0: return "PASS"
    if b <= 1.0 + se: return "PROVISIONAL"
    return "FAIL"

def write_json(path, obj):
    Path(path).write_text(json.dumps(obj, indent=2) + "\n")

def count_gate(dev, virgin_res, arms, line):
    """Mechanical gate application for count markets.
    dev/virgin_res: {arm_or_baseline: {season: agg, 'pooled': agg}}.
    Returns (shipped_arm_or_None, per-arm leg dict)."""
    legs = {}
    base_ll = dev["__base"]["pooled"]["ll"]; naive_ll = dev["__naive"]["pooled"]["ll"]
    gz_pass = dev["gate_zero"]["pooled"]["ll"] < base_ll and dev["gate_zero"]["pooled"]["ll"] < naive_ll
    for a in arms:
        legs[a] = {"dev_pass": dev[a]["pooled"]["ll"] < base_ll and dev[a]["pooled"]["ll"] < naive_ll}
    if not gz_pass or virgin_res is None:
        return None, legs, gz_pass
    gz_v = virgin_res["gate_zero"].get("pooled", virgin_res["gate_zero"]); clim_v = virgin_res["__base"].get("pooled", virgin_res["__base"])
    for a in arms:
        v = virgin_res[a].get("pooled", virgin_res[a])
        sign = True
        if a != "gate_zero":
            seasons = [s for s in dev[a] if "/" in s]
            wins = sum(1 for s in seasons if dev[a][s]["ll"] <= dev["gate_zero"][s]["ll"])
            nseas = len(seasons)
            sign = wins * 2 >= nseas
        legs[a].update({
            "virgin_ll": v["ll"],
            "ll_leg": v["ll"] <= gz_v["ll"] and v["ll"] <= clim_v["ll"],
            "calibration": calib_verdict(v), "sign_leg": sign})
        legs[a]["pass"] = legs[a]["ll_leg"] and legs[a]["calibration"] in ("PASS", "PROVISIONAL") and sign
    passing = [a for a in arms if legs[a].get("pass")]
    if not passing:
        return None, legs, gz_pass
    order = {a: i for i, a in enumerate(arms)}
    shipped = min(passing, key=lambda a: (virgin_res[a].get("pooled", virgin_res[a])["ll"], order[a]))
    return shipped, legs, gz_pass
