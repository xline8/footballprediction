"""G-PL-II development-only walk-forward evaluation; virgin data is out of scope."""
import csv
import json
import math
from datetime import date
from pathlib import Path

from arms import adjusted_lambdas, match_counts
from dc import DC

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data" / "plii_matches.csv"
if not DATA.exists():
    DATA = ROOT.parent.parent / "footballprediction" / "league" / "PL-IILiga" / "data" / "plii_matches.csv"
OUT = Path(__file__).resolve().parent

SEED = "2021/2022"
DEV_SEASONS = ("2021/2022", "2022/2023", "2023/2024", "2024/2025")
TARGET_SEASONS = DEV_SEASONS[1:]
FORBIDDEN_SEASONS = frozenset(("2025/2026", "2026/2027"))


def load(path, allowed):
    rows = []
    with open(path, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            season = r["season"]
            if season not in allowed:
                continue
            assert season not in FORBIDDEN_SEASONS, f"forbidden season reached: {season}"
            rows.append({"match_id": r["match_id"], "season": season, "date": date.fromisoformat(r["date"]),
                         "hi": int(r["home_team_id"]), "ai": int(r["away_team_id"]), "home": r["home_team"], "away": r["away_team"],
                         "yh": int(r["home_goals"]), "ya": int(r["away_goals"]), "xgh": None, "xga": None})
    assert all(r["season"] in DEV_SEASONS for r in rows)
    return sorted(rows, key=lambda r: (r["date"], r["match_id"]))


def _fit_predict(train, target):
    cutoff = min(r["date"] for r in target)
    prior = [r for r in train if r["date"] < cutoff]
    return DC().fit(prior, cutoff), match_counts(prior)


def _scores(rows, probs):
    ll = rps = oull = 0.0
    for r, p in zip(rows, probs):
        y = (1, 0, 0) if r["yh"] > r["ya"] else ((0, 1, 0) if r["yh"] == r["ya"] else (0, 0, 1))
        pp = [p["ph"], p["pd"], p["pa"]]
        ll -= math.log(max(pp[y.index(1)], 1e-12))
        rps += 0.5 * ((pp[0] - y[0]) ** 2 + (pp[0] + pp[1] - y[0] - y[1]) ** 2)
        over = int(r["yh"] + r["ya"] > 2.5)
        oull -= math.log(max(p["over25"] if over else 1 - p["over25"], 1e-12))
    n = len(rows)
    return {"n": n, "ll_1x2": ll / n, "rps": rps / n, "oull_2_5": oull / n}


def _clim(train):
    n = len(train)
    hw = sum(r["yh"] > r["ya"] for r in train) / n
    dr = sum(r["yh"] == r["ya"] for r in train) / n
    return [hw, dr, 1 - hw - dr], sum(r["yh"] + r["ya"] > 2.5 for r in train) / n


def _band_counts(target, counts):
    teams = {r[side] for r in target for side in ("hi", "ai")}
    return {"teams_1_to_5": sum(1 for t in teams if 1 <= counts.get(t, 0) <= 5),
            "teams_0": sum(1 for t in teams if counts.get(t, 0) == 0)}


def _gate_legs(model, baseline):
    return {name: {"model": model[name], "baseline": baseline[name],
                   "delta_model_minus_baseline": model[name] - baseline[name],
                   "pass": model[name] < baseline[name]}
            for name in ("ll_1x2", "rps", "oull_2_5")}


def run_dev():
    rows = load(DATA, set(DEV_SEASONS))
    assert len(rows) == 1236, f"expected 1236 dev rows, got {len(rows)}"
    result_rows = []
    bands = {}
    for arm in ("gate_zero", "shrink"):
        all_model = []
        all_clim = []
        for season in TARGET_SEASONS:
            target = [r for r in rows if r["season"] == season]
            assert len(target) == 309, f"expected 309 rows for {season}, got {len(target)}"
            cutoff = min(r["date"] for r in target)
            train = [r for r in rows if r["date"] < cutoff]
            model, counts = _fit_predict(train, target)
            bands.setdefault(season, _band_counts(target, counts))
            probs = [model.probs(*adjusted_lambdas(model, r["hi"], r["ai"], arm, counts=counts)) for r in target]
            met = _scores(target, probs); met.update({"arm": arm, "season": season, "kind": "model"}); result_rows.append(met); all_model += list(zip(target, probs))
            cp, co = _clim(train)
            cprobs = [{"ph": cp[0], "pd": cp[1], "pa": cp[2], "over25": co} for _ in target]
            met = _scores(target, cprobs); met.update({"arm": arm, "season": season, "kind": "climatology"}); result_rows.append(met); all_clim += list(zip(target, cprobs))
        assert len(all_model) == 927
        met = _scores([x[0] for x in all_model], [x[1] for x in all_model]); met.update({"arm": arm, "season": "pooled", "kind": "model"}); result_rows.append(met)
        met = _scores([x[0] for x in all_clim], [x[1] for x in all_clim]); met.update({"arm": arm, "season": "pooled", "kind": "climatology"}); result_rows.append(met)

    pooled = {arm: next(r for r in result_rows if r["arm"] == arm and r["season"] == "pooled" and r["kind"] == "model") for arm in ("gate_zero", "shrink")}
    baseline = next(r for r in result_rows if r["arm"] == "gate_zero" and r["season"] == "pooled" and r["kind"] == "climatology")
    gates = {arm: _gate_legs(pooled[arm], baseline) for arm in pooled}
    result = {"protocol": {"league": "PL-IILiga", "candidate": "G-PL-II", "dev_seasons_loaded": list(DEV_SEASONS), "scored_n": 927, "primary_line": "OU2.5", "sign_convention": "actual_minus_predicted", "forbidden_seasons_not_loaded": sorted(FORBIDDEN_SEASONS)},
              "rows": result_rows, "dev_gate": gates, "shrink_band_counts": bands}
    _write_dev(result)
    _print_table(result)
    return result


def _write_dev(result):
    (OUT / "results_dev.json").write_text(json.dumps(result, indent=2) + "\n")
    fields = ["arm", "season", "kind", "n", "ll_1x2", "rps", "oull_2_5"]
    with open(OUT / "results_dev.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows({k: r.get(k) for k in fields} for r in result["rows"])


def _print_table(data):
    print("dev")
    print("arm season kind n ll_1x2 rps oull_2_5")
    for r in data["rows"]:
        print(f'{r["arm"]} {r["season"]} {r["kind"]} {r["n"]} {r["ll_1x2"]:.6f} {r["rps"]:.6f} {r["oull_2_5"]:.6f}')
    print("dev_gate")
    for arm, legs in data["dev_gate"].items():
        print(arm, " ".join(f"{k}={v['model']:.6f}<{v['baseline']:.6f}:{v['pass']}" for k, v in legs.items()))
    print("shrink_band_counts")
    for season, counts in data["shrink_band_counts"].items():
        print(season, counts)
