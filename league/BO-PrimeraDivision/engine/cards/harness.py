"""K-BO cards engine: online walk-forward evaluation (BO adaptation of K-PY).

Differences, all frozen in league/BO-PrimeraDivision/prereg/PREREG_K_BO.md:
target is event-unified yellows; primary line 6.5 (secondary 5.5/7.5);
seed = 2025 rounds 1-10, dev scored = 2025 rounds 11-30 in four expanding
5-round blocks, virgin = 2026 regular (transitional). Calibration is
actual - predicted. Virgin leg (i) compares against BOTH baselines
(the PY harness compared against the league base rate only; the BO
prereg requires both, so this harness implements the prereg).
"""
import csv, json, math
from datetime import date
from pathlib import Path
from model import Online, estimate_r, nb_over

HERE = Path(__file__).resolve().parent
DATA = HERE.parents[1] / "data" / "bo_matches.csv"
PRED = HERE.parents[1] / "predictions" / "k_bo_virgin_predictions.csv"
LINES = (5.5, 6.5, 7.5)
PRIMARY = 6.5
BLOCKS = ("r11-15", "r16-20", "r21-25", "r26-30")
VIRGIN = "2026"
HALF = 0.3739


def block_of(season, rnd):
    if season == "2025":
        if rnd <= 10:
            return "seed"
        if rnd <= 15:
            return "r11-15"
        if rnd <= 20:
            return "r16-20"
        if rnd <= 25:
            return "r21-25"
        return "r26-30"
    return season


def load(seasons):
    out = []
    with DATA.open(newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["season"] not in seasons or r["phase"] != "regular":
                continue
            missing = r["event_yellow_unified_home"] in (None, "") or r["event_yellow_unified_away"] in (None, "")
            yh, ya = (None, None) if missing else (int(float(r["event_yellow_unified_home"])), int(float(r["event_yellow_unified_away"])))
            rnd = int(float(r["round"]))
            key = (r["date"] + "T00:00:00Z", r["match_id"])
            out.append({"match_id": r["match_id"], "season": r["season"], "date": r["date"], "kickoff_utc": key[0], "key": key, "day": date.fromisoformat(r["date"]).toordinal(), "round": rnd, "block": block_of(r["season"], rnd), "home_id": r["home_team_id"], "away_id": r["away_team_id"], "home": r["home_team"], "away": r["away_team"], "yh": yh, "ya": ya, "y": None if missing else yh + ya, "referee": "" if (r.get("referee") or "") in ("", "null") else r["referee"]})
    return sorted(out, key=lambda x: x["key"])


def scored(rs, rm):
    out = {}
    for method in ("model", "base", "naive"):
        out[method] = {}
        for line in LINES:
            pairs = [x for x in rs if x["y"] is not None]
            ps = [nb_over(x[method], rm[method], line) for x in pairs]
            ys = [int(x["y"] > line) for x in pairs]
            out[method][str(line)] = {"n": len(pairs), "ll": sum(-(y * math.log(max(p, 1e-12)) + (1 - y) * math.log(max(1 - p, 1e-12))) for p, y in zip(ps, ys)) / len(ps), "mean_p": sum(ps) / len(ps), "actual_rate": sum(ys) / len(ys)}
    return out


def rmap(rs):
    return {m: estimate_r(rs, m) for m in ("model", "base", "naive")}


def dev():
    rows = load({"2025"})
    assert not any(r["season"] == VIRGIN for r in rows)
    online = Online()
    warm = []
    sp = {s: [] for s in BLOCKS}
    for row in rows:
        p = online.prediction(row, "gate_zero")
        rec = {"y": row["y"], "model": p["model"], "base": p["base"], "naive": p["naive"]}
        (warm if row["block"] == "seed" else sp[row["block"]]).append(rec if row["block"] == "seed" else (row, p))
        if row["y"] is not None:
            online.update(row)
    rm = rmap([{**x, "model": x["model"]} for x in warm])
    seasons = {}
    allr = []
    for s in BLOCKS:
        rr = [{"y": r["y"], "model": p["model"], "base": p["base"], "naive": p["naive"]} for r, p in sp[s]]
        allr += rr
        seasons[s] = scored(rr, rm)
    seasons["pooled"] = scored(allr, rm)
    pk = str(PRIMARY)
    gate = seasons["pooled"]["model"][pk]["ll"] < seasons["pooled"]["base"][pk]["ll"] and seasons["pooled"]["model"][pk]["ll"] < seasons["pooled"]["naive"][pk]["ll"]
    out = {"protocol": {"warmup": "2025 rounds 1-10", "scored": list(BLOCKS), "dev_rows_loaded": len(rows), "primary_line": PRIMARY}, "arms": {"gate_zero": {"r": rm, "seasons": seasons, "dev_gate_pass": gate}}, "referee_coverage": {s: {"known": sum(1 for r in rows if r["season"] == s and r["referee"]), "n": len([r for r in rows if r["season"] == s]), "fraction": sum(1 for r in rows if r["season"] == s and r["referee"]) / max(1, len([r for r in rows if r["season"] == s]))} for s in ("2025",)}}
    (HERE / "results_dev.json").write_text(json.dumps(out, indent=2) + "\n")
    print_table(out, "dev")
    return out


def virgin_metrics(arms=("gate_zero",)):
    d = json.loads((HERE / "results_dev.json").read_text())
    if not d["arms"]["gate_zero"]["dev_gate_pass"]:
        out = {"verdict": "FAIL", "shipped_arm": None, "legs": {"dev_gate": False, "virgin_read": False}}
        (HERE / "results_virgin.json").write_text(json.dumps(out, indent=2) + "\n")
        print("virgin not read: Gate Zero failed dev gate")
        return out
    rows = load({"2025", VIRGIN})
    online = Online()
    fit = []
    tar = []
    for row in rows:
        p = online.prediction(row, "gate_zero")
        (tar if row["season"] == VIRGIN else fit).append((row, p))
        if row["y"] is not None:
            online.update(row)
    rm = rmap([{"y": r["y"], "model": p["model"], "base": p["base"], "naive": p["naive"]} for r, p in fit if r["y"] is not None])
    rr = [{"y": r["y"], "model": p["model"], "base": p["base"], "naive": p["naive"]} for r, p in tar]
    met = scored(rr, rm)
    scored_tar = [(r, p) for r, p in tar if r["y"] is not None]
    vals = [nb_over(p["model"], rm["model"], PRIMARY) for _, p in scored_tar]
    ys = [int(r["y"] > PRIMARY) for r, _ in scored_tar]
    dif = sum(y - p for p, y in zip(vals, ys)) / len(vals)  # actual - predicted
    se = (sum((y - p - dif) ** 2 for p, y in zip(vals, ys)) / (len(vals) - 1)) ** .5 / len(vals) ** .5
    pk = str(PRIMARY)
    ll = met["model"][pk]["ll"]
    leg1 = ll <= met["base"][pk]["ll"] and ll <= met["naive"][pk]["ll"]
    leg2 = abs(dif) <= .01 + se
    status = "PASS" if abs(dif) <= .01 else ("PROVISIONAL" if leg2 else "FAIL")
    verdict = "PASS" if leg1 and leg2 else "FAIL"
    out = {"arms": {"gate_zero": {"r": rm, "metrics": met, "calibration": {"diff_6_5": dif, "se_6_5": se}}}, "verdict": verdict, "shipped_arm": "gate_zero" if verdict == "PASS" else None, "legs": {"dev_gate": True, "i": leg1, "ii": leg2, "calibration_status": status}}
    (HERE / "results_virgin.json").write_text(json.dumps(out, indent=2) + "\n")
    print_table(out, "virgin")
    print("verdict", verdict, "shipped", out["shipped_arm"])
    if verdict == "PASS":
        predict(tar, fit, rm)
    return out


def predict(tar, fit, rm):
    PRED.parent.mkdir(exist_ok=True)
    fields = ["match_id", "date", "home_team", "away_team", "referee", "referee_known", "n_prior", "multiplier", "fallback", "fallback_reason", "expected_home", "expected_away", "expected_total", "p_over_5_5", "p_over_6_5", "p_over_7_5", "mean_1h", "mean_2h", "arm"]
    with PRED.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for row, p in tar:
            q = {"match_id": row["match_id"], "date": row["date"], "home_team": row["home"], "away_team": row["away"], "referee": row["referee"], "referee_known": bool(row["referee"]), "n_prior": 0, "multiplier": 1.0, "fallback": False, "fallback_reason": "", "expected_home": p["eh"], "expected_away": p["ea"], "expected_total": p["model"], "mean_1h": p["model"] * HALF, "mean_2h": p["model"] * (1 - HALF), "arm": "gate_zero"}
            q.update({f"p_over_{str(l).replace('.', '_')}": nb_over(p["model"], rm["model"], l) for l in LINES})
            w.writerow(q)
    (HERE / "fitted_params_virgin.json").write_text(json.dumps({"arm": "gate_zero", "r": rm}, indent=2) + "\n")


def print_table(out, label):
    print(label)
    pk = str(PRIMARY)
    if label == "dev":
        for s, x in out["arms"]["gate_zero"]["seasons"].items():
            print("gate_zero", s, "model", x["model"][pk]["n"], f'{x["model"][pk]["ll"]:.6f}', f'{x["model"][pk]["mean_p"]:.6f}', f'{x["model"][pk]["actual_rate"]:.6f}')
    else:
        x = out["arms"]["gate_zero"]["metrics"]
        print("gate_zero", x["model"][pk]["n"], f'{x["model"][pk]["ll"]:.6f}', f'{x["model"][pk]["mean_p"]:.6f}', f'{x["model"][pk]["actual_rate"]:.6f}')
