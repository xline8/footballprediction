"""Strictly isolated DEV harness and separately callable virgin runner."""
import csv, json, math, sys
from datetime import date
from pathlib import Path
from dc import DC
from arms import adjusted_lambdas, mover_tiers, prior_counts

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data" / "il_leumit_matches.csv"
OUT = Path(__file__).resolve().parent
WAREHOUSE = Path("/home/hatch/workspace/footballprediction")
DEV_SEASONS = {"2021/2022", "2022/2023", "2023/2024", "2024/2025"}
ARMS = ("gate_zero", "shrink", "x2")


def load_rows(allowed):
    rows = []
    with DATA.open(newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["season"] not in allowed:
                continue
            rows.append({"match_id": r["match_id"], "season": r["season"], "date": date.fromisoformat(r["date"]),
                         "hi": int(r["home_team_id"]), "ai": int(r["away_team_id"]), "home": r["home_team"], "away": r["away_team"],
                         "yh": int(r["home_goals"]), "ya": int(r["away_goals"])})
    assert {r["season"] for r in rows} <= set(allowed)
    return sorted(rows, key=lambda r: (r["date"], r["match_id"]))


def load_haal(seasons):
    index = WAREHOUSE / "data_enrichment" / "fotmob_world_index.csv"
    result = {s: set() for s in seasons}
    with index.open(newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["league_id"] != "127" or r["season"] not in seasons:
                continue
            with (WAREHOUSE / r["path"]).open(encoding="utf-8") as jf:
                general = json.load(jf)["general"]
            result[r["season"]].update((int(general["homeTeam"]["id"]), int(general["awayTeam"]["id"])))
    return result


def scores(rows, predictions):
    ll = rps = oull = 0.0
    for r, p in zip(rows, predictions):
        y = [1, 0, 0] if r["yh"] > r["ya"] else ([0, 1, 0] if r["yh"] == r["ya"] else [0, 0, 1])
        pp = [p["ph"], p["pd"], p["pa"]]
        ll -= math.log(max(pp[y.index(1)], 1e-12))
        rps += 0.5 * ((pp[0] - y[0]) ** 2 + (pp[0] + pp[1] - y[0] - y[1]) ** 2)
        over = r["yh"] + r["ya"] > 2.5
        oull -= math.log(max(p["over25"] if over else 1.0 - p["over25"], 1e-12))
    n = len(rows)
    return {"n": n, "ll_1x2": ll / n, "rps": rps / n, "oull_2_5": oull / n}


def climatology(train):
    n = len(train)
    hw = sum(r["yh"] > r["ya"] for r in train) / n
    dr = sum(r["yh"] == r["ya"] for r in train) / n
    return (hw, dr, 1.0 - hw - dr), sum(r["yh"] + r["ya"] > 2.5 for r in train) / n


def fit_for(train, target, haal):
    cutoff = min(r["date"] for r in target)
    window = [r for r in train if r["date"] < cutoff]
    membership_rows = train + target
    return DC().fit(window, cutoff), window, mover_tiers(target[0]["season"], membership_rows, haal)


def run_dev():
    rows = load_rows(DEV_SEASONS)
    assert {r["season"] for r in rows} == DEV_SEASONS
    haal = load_haal(DEV_SEASONS)
    result = []
    for arm in ARMS:
        model_rows = []; clim_rows = []
        for season in ("2022/2023", "2023/2024", "2024/2025"):
            target = [r for r in rows if r["season"] == season]
            train = [r for r in rows if r["date"] < min(x["date"] for x in target)]
            model, window, movers = fit_for(train, target, haal)
            counts = prior_counts(window)
            predictions = [model.probs(*adjusted_lambdas(model, r["hi"], r["ai"], arm, counts, movers)) for r in target]
            met = scores(target, predictions); met.update({"arm": arm, "season": season, "kind": "model"}); result.append(met); model_rows.extend(zip(target, predictions))
            cp, co = climatology(train)
            c_preds = [{"ph": cp[0], "pd": cp[1], "pa": cp[2], "over25": co} for _ in target]
            met = scores(target, c_preds); met.update({"arm": arm, "season": season, "kind": "climatology"}); result.append(met); clim_rows.extend(zip(target, c_preds))
        met = scores([r for r, _ in model_rows], [p for _, p in model_rows]); met.update({"arm": arm, "season": "pooled", "kind": "model"}); result.append(met)
        met = scores([r for r, _ in clim_rows], [p for _, p in clim_rows]); met.update({"arm": arm, "season": "pooled", "kind": "climatology"}); result.append(met)
    write_dev(result)
    print_table(result)
    return result


def write_dev(result):
    (OUT / "results_dev.json").write_text(json.dumps(result, indent=2) + "\n")
    fields = ["arm", "season", "kind", "n", "ll_1x2", "rps", "oull_2_5"]
    with (OUT / "results_dev.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields); writer.writeheader(); writer.writerows({k: row[k] for k in fields} for row in result)


def virgin(arms, prediction_path):
    if not arms:
        raise SystemExit("virgin requires at least one arm in --arms")
    unknown = set(arms) - set(ARMS)
    if unknown:
        raise SystemExit(f"unknown arm(s): {', '.join(sorted(unknown))}")
    rows = load_rows(DEV_SEASONS | {"2025/2026"})
    target = [r for r in rows if r["season"] == "2025/2026"]
    train = [r for r in rows if r["date"] < min(r["date"] for r in target)]
    haal = load_haal(DEV_SEASONS | {"2025/2026"})
    result = {}
    for arm in arms:
        model, window, movers = fit_for(train, target, haal); counts = prior_counts(window)
        preds = []
        for r in target:
            lh, la = adjusted_lambdas(model, r["hi"], r["ai"], arm, counts, movers)
            p = model.probs(lh, la); p.update({"lh": lh, "la": la}); preds.append(p)
        result[arm] = scores(target, preds)
        write_predictions(prediction_path, target, preds, arm)
    (OUT / "results_virgin.json").write_text(json.dumps(result, indent=2) + "\n")
    (OUT / "fitted_params_virgin.json").write_text(json.dumps({"a": dict(model.a), "d": dict(model.d), "h": model.h, "rho": model.rho, "mu": model.mu}, indent=2) + "\n")


def write_predictions(path, rows, preds, arm):
    fields = ["match_id", "date", "home_team_id", "away_team_id", "arm", "lam_h", "lam_a", "p_home", "p_draw", "p_away", "p_over15", "p_over25", "p_over35", "p_btts", "home_goals", "away_goals"]
    mode = "w" if not Path(path).exists() else "a"
    with Path(path).open(mode, newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        if mode == "w": writer.writeheader()
        for r, p in zip(rows, preds):
            writer.writerow({"match_id": r["match_id"], "date": r["date"].isoformat(), "home_team_id": r["hi"], "away_team_id": r["ai"], "arm": arm,
                             "lam_h": p["lh"], "lam_a": p["la"], "p_home": p["ph"], "p_draw": p["pd"], "p_away": p["pa"],
                             "p_over15": p["over15"], "p_over25": p["over25"], "p_over35": p["over35"], "p_btts": p["btts"], "home_goals": r["yh"], "away_goals": r["ya"]})


def print_table(result):
    print("arm season kind n ll_1x2 rps oull_2_5")
    for row in result:
        print(f'{row["arm"]} {row["season"]} {row["kind"]} {row["n"]} {row["ll_1x2"]:.6f} {row["rps"]:.6f} {row["oull_2_5"]:.6f}')
