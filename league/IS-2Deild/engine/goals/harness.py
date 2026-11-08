"""Dev-only season-blocked walk-forward evaluation for G-IS2."""
import csv
import json
import math
from datetime import date
from pathlib import Path

from dc import DC
from arms import adjusted_lambdas, match_counts, x2_shifts

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data" / "is2_matches.csv"
MOVERS = ROOT / "data" / "mover_teams.json"
OUT = Path(__file__).resolve().parent
ALLOWED = {"2021", "2022", "2023", "2024", "2025"}
DEV_SEASONS = ("2022", "2023", "2024", "2025")


def load(path):
    rows = []
    with open(path, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["season"] not in ALLOWED:
                continue
            rows.append({"match_id": r["match_id"], "season": r["season"], "date": date.fromisoformat(r["date"]),
                         "hi": int(r["home_team_id"]), "ai": int(r["away_team_id"]),
                         "home": r["home_team"], "away": r["away_team"],
                         "yh": int(r["home_goals"]), "ya": int(r["away_goals"]),
                         "xgh": None, "xga": None})
    assert all(r["season"] in ALLOWED for r in rows)
    assert not any(r["season"] == "2026" for r in rows)
    return sorted(rows, key=lambda r: (r["date"], r["match_id"]))


def _scores(rows, probs):
    ll = rps = oull = 0.0
    for r, p in zip(rows, probs):
        y = [1, 0, 0] if r["yh"] > r["ya"] else ([0, 1, 0] if r["yh"] == r["ya"] else [0, 0, 1])
        pp = [p["ph"], p["pd"], p["pa"]]
        ll -= math.log(max(pp[y.index(1)], 1e-12))
        rps += 0.5 * ((pp[0] - y[0]) ** 2 + (pp[0] + pp[1] - y[0] - y[1]) ** 2)
        over = r["yh"] + r["ya"] > 2.5
        oull -= math.log(max(p["over25"] if over else 1 - p["over25"], 1e-12))
    n = len(rows)
    return {"n": n, "ll_1x2": ll / n, "rps": rps / n, "oull_2_5": oull / n}


def _clim(train):
    n = len(train)
    home = sum(r["yh"] > r["ya"] for r in train) / n
    draw = sum(r["yh"] == r["ya"] for r in train) / n
    over = sum(r["yh"] + r["ya"] > 2.5 for r in train) / n
    return [home, draw, 1.0 - home - draw], over


def _entrant_maps(mover_data, season, shifts):
    current = set(mover_data["seasons"][season]["is2deild_team_ids"])
    previous = set(mover_data["seasons"][str(int(season) - 1)]["is2deild_team_ids"])
    sources = {t["team_id"]: t["source"] for t in mover_data["transitions"] if str(t["season"]) == season}
    return {team: shifts[sources[team]] for team in current - previous if team in sources and sources[team] in shifts}


def run_dev():
    rows = load(DATA)
    movers = json.loads(MOVERS.read_text(encoding="utf-8"))
    metric_rows = []
    match_outputs = []
    diagnostics = {a: {"n": 0, "differ_from_gate_zero": 0, "differ_from_shrink": 0} for a in ("gate_zero", "shrink", "x2")}
    x2_used = {}
    for season in DEV_SEASONS:
        target = [r for r in rows if r["season"] == season]
        first = min(r["date"] for r in target)
        train = [r for r in rows if r["date"] < first]
        model = DC().fit(train, first)
        shifts = x2_shifts(movers["transitions"], train, model.mu, season)
        multipliers = _entrant_maps(movers, season, shifts)
        x2_used[season] = {source: {k: v for k, v in value.items() if k in ("att", "def", "n_prior", "dGF", "dGA")}
                           for source, value in shifts.items()}
        per_arm = {}
        lambdas = {}
        prob_by_arm = {}
        for arm in ("gate_zero", "shrink", "x2"):
            probs = []
            lambdas[arm] = []
            for r in target:
                counts = match_counts([q for q in target if q["date"] < r["date"]])
                lh, la = adjusted_lambdas(model, r["hi"], r["ai"], arm, multipliers, counts)
                assert not (math.isnan(lh) or math.isnan(la))
                p = model.probs(lh, la)
                assert abs(p["ph"] + p["pd"] + p["pa"] - 1.0) <= 1e-9
                assert all(0.0 <= p[k] <= 1.0 for k in ("ph", "pd", "pa", "over25"))
                lambdas[arm].append((lh, la)); probs.append(p)
            prob_by_arm[arm] = probs
            per_arm[arm] = _scores(target, probs)
            per_arm[arm].update({"arm": arm, "season": season, "kind": "model"})
            metric_rows.append(per_arm[arm])
        for arm in ("gate_zero", "shrink", "x2"):
            diagnostics[arm]["n"] += len(target)
        for arm in ("shrink", "x2"):
            diagnostics[arm]["differ_from_gate_zero"] += sum(a != b for a, b in zip(lambdas[arm], lambdas["gate_zero"]))
        diagnostics["x2"]["differ_from_shrink"] += sum(a != b for a, b in zip(lambdas["x2"], lambdas["shrink"]))
        for r, pz, ps, px in zip(target, prob_by_arm["gate_zero"], prob_by_arm["shrink"], prob_by_arm["x2"]):
            match_outputs.append({"match_id": r["match_id"], "season": r["season"], "date": r["date"].isoformat(),
                                  "home_team_id": r["hi"], "away_team_id": r["ai"], "home_goals": r["yh"], "away_goals": r["ya"],
                                  "gate_zero_ph": pz["ph"], "gate_zero_pd": pz["pd"], "gate_zero_pa": pz["pa"], "gate_zero_over25": pz["over25"],
                                  "shrink_ph": ps["ph"], "shrink_pd": ps["pd"], "shrink_pa": ps["pa"], "shrink_over25": ps["over25"],
                                  "x2_ph": px["ph"], "x2_pd": px["pd"], "x2_pa": px["pa"], "x2_over25": px["over25"]})
        cp, co = _clim(train)
        cprobs = [{"ph": cp[0], "pd": cp[1], "pa": cp[2], "over25": co} for _ in target]
        cm = _scores(target, cprobs); cm.update({"arm": "climatology", "season": season, "kind": "climatology"}); metric_rows.append(cm)
    for arm in ("gate_zero", "shrink", "x2"):
        model_rows = [r for r in metric_rows if r["arm"] == arm and r["kind"] == "model"]
        all_match = [r for r in match_outputs]
        probs = [{"ph": r[f"{arm}_ph"], "pd": r[f"{arm}_pd"], "pa": r[f"{arm}_pa"], "over25": r[f"{arm}_over25"]} for r in all_match]
        score_rows = [{"yh": r["home_goals"], "ya": r["away_goals"]} for r in all_match]
        pooled = _scores(score_rows, probs); pooled.update({"arm": arm, "season": "pooled", "kind": "model"}); metric_rows.append(pooled)
        clim = [r for r in metric_rows if r["arm"] == "climatology" and r["kind"] == "climatology"]
    clim_rows = [r for r in metric_rows if r["arm"] == "climatology" and r["kind"] == "climatology"]
    # Recompute pooled climatology from the per-season climatology predictions.
    clim_pooled = {"arm": "climatology", "season": "pooled", "kind": "climatology", "n": sum(r["n"] for r in clim_rows)}
    for key in ("ll_1x2", "rps", "oull_2_5"):
        clim_pooled[key] = sum(r[key] * r["n"] for r in clim_rows) / clim_pooled["n"]
    metric_rows.append(clim_pooled)
    for row in metric_rows:
        if row["season"] == "pooled" and row["arm"] == "gate_zero":
            row["diagnostics"] = {"lambda_difference_counts": diagnostics, "x2_shifts": x2_used}
    assert len(match_outputs) == 528
    (OUT / "results_dev.json").write_text(json.dumps(metric_rows, indent=2) + "\n", encoding="utf-8")
    fields = ["match_id", "season", "date", "home_team_id", "away_team_id", "home_goals", "away_goals",
              "gate_zero_ph", "gate_zero_pd", "gate_zero_pa", "gate_zero_over25", "shrink_ph", "shrink_pd", "shrink_pa", "shrink_over25",
              "x2_ph", "x2_pd", "x2_pa", "x2_over25"]
    with open(OUT / "results_dev.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields); writer.writeheader(); writer.writerows(match_outputs)
    print(json.dumps({"lambda_difference_counts": diagnostics, "x2_shifts": x2_used}, indent=2))
    for r in metric_rows:
        print(f'{r["arm"]} {r["season"]} {r["kind"]} {r["n"]} {r["ll_1x2"]:.6f} {r["rps"]:.6f} {r["oull_2_5"]:.6f}')
    return metric_rows
