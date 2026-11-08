"""Season-blocked development harness; it never loads virgin rows."""
import csv
import json
import math
from datetime import date
from pathlib import Path

from arms import adjusted_lambdas, match_counts
from dc import DC

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data" / "nz_matches.csv"
OUT = Path(__file__).resolve().parent
SEASONS = ("2022", "2023", "2024")
TARGETS = ("2023", "2024")
ARMS = ("gate_zero", "shrink")
BASE_OVER_RATE = 0.75


def load(path=DATA):
    rows = []
    with Path(path).open(newline="", encoding="utf-8") as fh:
        for x in csv.DictReader(fh):
            if x["season"] not in SEASONS:
                continue
            if x["season"] in ("2025", "2026"):
                raise AssertionError("dev harness loaded a forbidden later-season row")
            rows.append({"match_id": x["match_id"], "season": x["season"],
                         "date": date.fromisoformat(x["date"]), "phase": x["phase"],
                         "home": x["home_team"], "away": x["away_team"],
                         "hi": int(x["home_team_id"]), "ai": int(x["away_team_id"]),
                         "yh": int(x["home_goals"]), "ya": int(x["away_goals"])})
    rows.sort(key=lambda r: (r["date"], r["match_id"]))
    assert all(r["season"] not in ("2025", "2026") for r in rows)
    return rows


def score(rows, probs):
    ll = rps = ou = 0.0
    for r, p in zip(rows, probs):
        y = (1, 0, 0) if r["yh"] > r["ya"] else ((0, 1, 0) if r["yh"] == r["ya"] else (0, 0, 1))
        pp = [p["ph"], p["pd"], p["pa"]]
        ll -= math.log(max(pp[y.index(1)], 1e-12))
        rps += 0.5 * ((pp[0] - y[0]) ** 2 + (pp[0] + pp[1] - y[0] - y[1]) ** 2)
        over = r["yh"] + r["ya"] > 2.5
        ou -= math.log(max(p["over25"] if over else 1 - p["over25"], 1e-12))
    return {"n": len(rows), "ll_1x2": ll / len(rows), "rps": rps / len(rows), "oull_2_5": ou / len(rows)}


def clim(train):
    n = len(train)
    h = sum(r["yh"] > r["ya"] for r in train) / n
    d = sum(r["yh"] == r["ya"] for r in train) / n
    o = sum(r["yh"] + r["ya"] > 2.5 for r in train) / n
    return [h, d, 1 - h - d], o


def rec(r, arm, lh, la, p):
    return {"match_id": r["match_id"], "season": r["season"], "date": r["date"].isoformat(),
            "phase": r["phase"], "home_team_id": r["hi"], "away_team_id": r["ai"],
            "home_goals": r["yh"], "away_goals": r["ya"], "arm": arm, "lam_h": lh,
            "lam_a": la, "ph": p["ph"], "pd": p["pd"], "pa": p["pa"],
            "over25": p["over25"], "over15": p["over15"], "over35": p["over35"], "btts": p["btts"]}


def run_dev():
    rows = load()
    summaries, per_match = [], []
    diagnostics = {a: {} for a in ARMS}
    signs, pooled, pooled_c = [], {a: [] for a in ARMS}, {a: [] for a in ARMS}
    for season in TARGETS:
        target = [r for r in rows if r["season"] == season]
        cutoff = min(r["date"] for r in target)
        train = [r for r in rows if r["date"] < cutoff]
        model = DC().fit(train, cutoff)
        counts = match_counts(train)
        lambdas, preds_by = {}, {}
        for arm in ARMS:
            lambdas[arm], preds = [], []
            for r in target:
                lh, la = adjusted_lambdas(model, r["hi"], r["ai"], arm, counts)
                p = model.probs(lh, la)
                lambdas[arm].append((lh, la)); preds.append(p)
                per_match.append(rec(r, arm, lh, la, p))
            preds_by[arm] = preds
            pooled[arm].extend(zip(target, preds))
            m = score(target, preds); m.update({"arm": arm, "season": season, "kind": "model"}); summaries.append(m)
            cp, co = clim(train)
            cprobs = [{"ph": cp[0], "pd": cp[1], "pa": cp[2], "over25": co} for _ in target]
            pooled_c[arm].extend(zip(target, cprobs))
            cm = score(target, cprobs); cm.update({"arm": arm, "season": season, "kind": "climatology"}); summaries.append(cm)
            diagnostics[arm][season] = {"n": len(target), "matches_differing": 0, "lambda_components_differing": 0}
        diagnostics["shrink"][season]["matches_differing"] = sum(
            any(abs(x - y) > 1e-12 for x, y in zip(g, s))
            for g, s in zip(lambdas["gate_zero"], lambdas["shrink"]))
        diagnostics["shrink"][season]["lambda_components_differing"] = sum(
            abs(x - y) > 1e-12
            for g, s in zip(lambdas["gate_zero"], lambdas["shrink"])
            for x, y in zip(g, s))
        z = next(x for x in summaries if x["arm"] == "gate_zero" and x["season"] == season and x["kind"] == "model")
        v = next(x for x in summaries if x["arm"] == "shrink" and x["season"] == season and x["kind"] == "model")
        signs.append({"arm": "shrink", "season": season, "ll_1x2": v["ll_1x2"],
                      "gate_zero_ll_1x2": z["ll_1x2"], "passes": v["ll_1x2"] <= z["ll_1x2"]})
    dev = [r for r in rows if r["season"] in TARGETS]
    over_count = sum(r["yh"] + r["ya"] > 2.5 for r in dev)
    assert over_count == 69 and len(dev) == 92, (len(dev), over_count)
    for arm in ARMS:
        m = score([x[0] for x in pooled[arm]], [x[1] for x in pooled[arm]])
        m.update({"arm": arm, "season": "pooled", "kind": "model"}); summaries.append(m)
        c = score([x[0] for x in pooled_c[arm]], [x[1] for x in pooled_c[arm]])
        c.update({"arm": arm, "season": "pooled", "kind": "climatology"}); summaries.append(c)
    baseline_ll = -sum(math.log(BASE_OVER_RATE if r["yh"] + r["ya"] > 2.5 else 1 - BASE_OVER_RATE) for r in dev) / len(dev)
    baseline = {"n": len(dev), "oull_2_5": baseline_ll, "over_rate": BASE_OVER_RATE,
                "arm": "base_rate", "season": "pooled", "kind": "ou2_5_base_rate"}
    sign = {"rows": signs, "passes": sum(x["passes"] for x in signs) * 2 >= len(signs)}
    gate = {}
    for arm in ARMS:
        m = next(x for x in summaries if x["arm"] == arm and x["season"] == "pooled" and x["kind"] == "model")
        c = next(x for x in summaries if x["arm"] == arm and x["season"] == "pooled" and x["kind"] == "climatology")
        gate[arm] = {"pooled_model": m, "pooled_climatology": c, "passes":
                     m["ll_1x2"] < c["ll_1x2"] and m["rps"] < c["rps"] and m["oull_2_5"] < baseline_ll}
    result = {"rows": summaries, "ou25_base_rate_baseline": baseline, "sign_check": sign,
              "lambda_differences_vs_gate_zero": diagnostics, "dev_gate": gate}
    (OUT / "results_dev.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    fields = ["match_id", "season", "date", "phase", "home_team_id", "away_team_id", "home_goals", "away_goals", "arm", "lam_h", "lam_a", "ph", "pd", "pa", "over25", "over15", "over35", "btts"]
    with (OUT / "results_dev.csv").open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields); writer.writeheader(); writer.writerows(per_match)
    return result
