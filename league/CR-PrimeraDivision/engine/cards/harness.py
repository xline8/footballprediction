"""Dev + virgin harness for K-CR.

Adapted from league/J1/engine/cards/harness.py: single arm (Gate Zero — no referee
data exists in this league), reliable cards era only (2023/2024 onward), dev split
2023/2024 Apertura warm-up / Clausura scored, virgin 2024/2025 regular (n = 262).
Primary line 4.5, secondary 3.5 / 5.5. Prereg:
league/CR-PrimeraDivision/prereg/PREREG_K_CR.md.
"""
import csv, json, math, os, time
from datetime import datetime
from pathlib import Path
from model import Online, estimate_r, nb_over

HERE = Path(__file__).resolve().parent
DATA = HERE.parents[1] / "data" / "cr_matches.csv"
PRED = HERE.parents[1] / "predictions" / "k_cr_virgin_predictions.csv"
DEV_SEASON = "2023/2024"
VIRGIN_SEASON = "2024/2025"
LINES = (4.5, 3.5, 5.5)
PRIMARY = 4.5
HALVES_1H = 0.379


def _safe_write_text(path, text, tries=40):
    data = text.encode("utf-8")
    for _ in range(tries):
        try:
            tmp = str(path) + ".tmp%d" % os.getpid()
            with open(tmp, "wb") as f:
                f.write(data)
                f.flush()
                os.fsync(f.fileno())
            if os.path.getsize(tmp) != len(data):
                raise IOError("size mismatch")
            os.replace(tmp, path)
            if os.path.getsize(path) == len(data):
                return
        except (PermissionError, OSError):
            time.sleep(1.0)
    raise IOError("could not write %s" % path)


def load(seasons):
    out = []
    with open(DATA, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["season"] not in seasons or r["stage"] != "regular":
                continue
            key = datetime.fromisoformat(r["date_utc"] + "T00:00:00+00:00")
            out.append({"match_id": r["match_id"], "season": r["season"],
                        "tournament": r["tournament"], "date": r["date_utc"],
                        "key": (r["date_utc"], r["match_id"]),
                        "day": key.date().toordinal(),
                        "home_id": int(r["home_id"]), "away_id": int(r["away_id"]),
                        "home": r["home_name"], "away": r["away_name"],
                        "yh": int(r["yellow_home"]), "ya": int(r["yellow_away"]),
                        "y": int(r["yellow_total"]),
                        "referee_known": bool(r["referee"])})
    out.sort(key=lambda x: x["key"])
    for a, b in zip(out, out[1:]):
        assert a["key"] < b["key"], "processing order is not strictly chronological"
    return out


def scored(records, rmap):
    result = {}
    for method in ("model", "base", "naive"):
        vals = {}
        for line in LINES:
            ps = [nb_over(x[method], rmap[method], line) for x in records]
            ys = [int(x["y"] > line) for x in records]
            n = len(ys)
            vals[str(line)] = {
                "n": n,
                "ll": sum(-(y * math.log(max(p, 1e-12)) + (1 - y) * math.log(max(1 - p, 1e-12)))
                          for p, y in zip(ps, ys)) / n,
                "mean_p": sum(ps) / n,
                "actual_rate": sum(ys) / n,
            }
        result[method] = vals
    return result


def _rmap(records):
    return {m: estimate_r(records, m) for m in ("model", "base", "naive")}


def dev():
    rows = load((DEV_SEASON,))
    online = Online()
    warm, scored_recs = [], []
    by_split = {"warmup": [], "scored": []}
    for row in rows:
        p = online.prediction(row)
        rec = {"y": row["y"], "model": p["model"], "base": p["base"], "naive": p["naive"]}
        if row["tournament"] == "Apertura":
            warm.append(rec)
            by_split["warmup"].append(rec)
        else:
            scored_recs.append(rec)
            by_split["scored"].append(rec)
        online.update(row)
    rmap = _rmap(warm)
    out = {"protocol": {"warmup": "2023/2024 Apertura (regular, n=%d)" % len(warm),
                        "scored": "2023/2024 Clausura (regular, n=%d)" % len(scored_recs),
                        "dev_rows_loaded": len(rows)},
           "arms": {}}
    met = scored(scored_recs, rmap)
    m = met["model"][str(PRIMARY)]["ll"]
    b = met["base"][str(PRIMARY)]["ll"]
    n = met["naive"][str(PRIMARY)]["ll"]
    out["arms"]["gate_zero"] = {"r": rmap, "seasons": {"scored": met},
                                "dev_gate_pass": bool(m < b and m < n)}
    _safe_write_text(HERE / "results_dev.json", json.dumps(out, indent=2) + "\n")
    fields = ["arm", "season", "method", "n", "ll_4_5", "ll_3_5", "ll_5_5",
              "mean_p_over_4_5", "actual_over_4_5"]
    lines = [",".join(fields)]
    for meth, q in met.items():
        lines.append(",".join(map(str, ["gate_zero", "scored", meth, q[str(PRIMARY)]["n"],
                                       q[str(PRIMARY)]["ll"], q["3.5"]["ll"], q["5.5"]["ll"],
                                       q[str(PRIMARY)]["mean_p"], q[str(PRIMARY)]["actual_rate"]])))
    _safe_write_text(HERE / "results_dev.csv", "\n".join(lines) + "\n")
    print("gate_zero gate", out["arms"]["gate_zero"]["dev_gate_pass"], "r", rmap,
          "LL model/base/naive @4.5:", round(m, 6), round(b, 6), round(n, 6))
    return out


def virgin_metrics():
    devres = json.loads((HERE / "results_dev.json").read_text())
    arms = [a for a, x in devres["arms"].items() if x["dev_gate_pass"]]
    rows = load((DEV_SEASON, VIRGIN_SEASON))
    online = Online()
    fit = {a: [] for a in arms}
    virgin = {a: [] for a in arms}
    coverage = [0, 0]
    for row in rows:
        for a in arms:
            p = online.prediction(row, a)
            rec = {"y": row["y"], "model": p["model"], "base": p["base"], "naive": p["naive"],
                   "row": row, "p": p}
            (fit if row["season"] != VIRGIN_SEASON else virgin)[a].append(rec)
        if row["season"] == VIRGIN_SEASON:
            coverage[1] += 1
            coverage[0] += bool(row["referee_known"])
        online.update(row)
    result = {"protocol": {"rows": coverage[1],
                           "dead_arms_not_read": sorted(set(("gate_zero",)) - set(arms))},
              "arms": {},
              "referee_coverage": {"known": coverage[0], "n": coverage[1],
                                   "fraction": coverage[0] / coverage[1] if coverage[1] else None}}
    for a in arms:
        rmap = _rmap(fit[a])
        rr = [{"y": x["y"], "model": x["model"], "base": x["base"], "naive": x["naive"]}
              for x in virgin[a]]
        metric = scored(rr, rmap)
        vals = [nb_over(x["model"], rmap["model"], PRIMARY) for x in virgin[a]]
        ys = [int(x["y"] > PRIMARY) for x in virgin[a]]
        dif = sum(vals) / len(vals) - sum(ys) / len(ys)
        se = (sum((p - y - dif) ** 2 for p, y in zip(vals, ys)) / (len(vals) - 1)) ** .5 / len(vals) ** .5
        result["arms"][a] = {"r": rmap, "metrics": metric,
                             "calibration": {"diff_4_5": dif, "se_4_5": se}}
    _safe_write_text(HERE / "results_virgin.json", json.dumps(result, indent=2) + "\n")
    for a, x in result["arms"].items():
        print(a, "virgin LL@4.5 model/base/naive:",
              round(x["metrics"]["model"][str(PRIMARY)]["ll"], 6),
              round(x["metrics"]["base"][str(PRIMARY)]["ll"], 6),
              round(x["metrics"]["naive"][str(PRIMARY)]["ll"], 6),
              "cal diff/se:", round(x["calibration"]["diff_4_5"], 6), round(x["calibration"]["se_4_5"], 6))
    print("dead arms not read:", result["protocol"]["dead_arms_not_read"])
    return result


def predict(arm):
    result = json.loads((HERE / "results_virgin.json").read_text())
    assert arm in result["arms"], "arm did not survive dev gate"
    rows = load((DEV_SEASON, VIRGIN_SEASON))
    online = Online()
    fit, targets = [], []
    cutoff_state = None
    for row in rows:
        p = online.prediction(row, arm)
        if row["season"] != VIRGIN_SEASON:
            fit.append({"y": row["y"], "model": p["model"], "base": p["base"], "naive": p["naive"]})
        else:
            if cutoff_state is None:
                cutoff_state = online.state.snapshot(row["day"])
            targets.append((row, p))
        online.update(row)
    rmap = _rmap(fit)
    PRED.parent.mkdir(exist_ok=True)
    fields = ["match_id", "date", "home_team", "away_team", "referee_known",
              "expected_home", "expected_away", "expected_total",
              "p_over_1_5", "p_over_2_5", "p_over_3_5", "p_over_4_5", "p_over_5_5",
              "mean_1h", "mean_2h", "p_over_1h_0_5", "p_over_1h_1_5", "p_over_1h_2_5",
              "p_over_2h_1_5", "p_over_2h_2_5", "p_over_2h_3_5", "arm"]
    import io
    sio = io.StringIO()
    w = csv.DictWriter(sio, fieldnames=fields)
    w.writeheader()
    for row, p in targets:
        q = {"match_id": row["match_id"], "date": row["date"], "home_team": row["home"],
             "away_team": row["away"], "referee_known": row["referee_known"],
             "expected_home": p["eh"], "expected_away": p["ea"], "expected_total": p["model"]}
        for L in (1.5, 2.5, 3.5, 4.5, 5.5):
            q["p_over_%s" % str(L).replace(".", "_")] = nb_over(p["model"], rmap["model"], L)
        q.update({"mean_1h": p["model"] * HALVES_1H, "mean_2h": p["model"] * (1 - HALVES_1H),
                  "p_over_1h_0_5": nb_over(p["model"] * HALVES_1H, rmap["model"], .5),
                  "p_over_1h_1_5": nb_over(p["model"] * HALVES_1H, rmap["model"], 1.5),
                  "p_over_1h_2_5": nb_over(p["model"] * HALVES_1H, rmap["model"], 2.5),
                  "p_over_2h_1_5": nb_over(p["model"] * (1 - HALVES_1H), rmap["model"], 1.5),
                  "p_over_2h_2_5": nb_over(p["model"] * (1 - HALVES_1H), rmap["model"], 2.5),
                  "p_over_2h_3_5": nb_over(p["model"] * (1 - HALVES_1H), rmap["model"], 3.5),
                  "arm": arm})
        w.writerow(q)
    _safe_write_text(PRED, sio.getvalue())
    _safe_write_text(HERE / "fitted_params_virgin.json", json.dumps(
        {"HL": 270, "K_PRIOR": 8, "r": rmap, "arm": arm, "cutoff_state": cutoff_state}, indent=2) + "\n")
    print("wrote", PRED, "rows:", len(targets))
