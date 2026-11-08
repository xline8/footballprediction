"""Pre-registered, goals-only Dixon-Coles engine for J3."""

import csv
import json
import math
import sys
from collections import defaultdict
from datetime import datetime


ROOT = "."
J3_FILE = "league/J3/data/j3_matches.csv"
J2_FILE = "league/J2/data/j2_matches.csv"
RESULTS = "league/J3/engine/goals/results"
PREDICTIONS = "league/J3/predictions/g_j3_virgin_predictions.csv"
RHO_GRID = (0.0, -0.05, -0.10, -0.15)
MAX_GOALS = 10
HALF_LIFE = 270


def pois(k, lam):
    return math.exp(-lam + k * math.log(max(lam, 1e-12)) - math.lgamma(k + 1))


def tau(x, y, lh, la, rho):
    if x == 0 and y == 0:
        return max(0.0, 1.0 - lh * la * rho)
    if x == 0 and y == 1:
        return max(0.0, 1.0 + lh * rho)
    if x == 1 and y == 0:
        return max(0.0, 1.0 + la * rho)
    if x == 1 and y == 1:
        return max(0.0, 1.0 - rho)
    return 1.0


def read_matches(path, league):
    rows = []
    with open(path, encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            if not row.get("season") or not row.get("date"):
                continue
            try:
                home_goals = int(row["home_goals"])
                away_goals = int(row["away_goals"])
                date = datetime.strptime(row["date"][:10], "%Y-%m-%d").date()
                season = str(row["season"])
            except (KeyError, TypeError, ValueError):
                continue
            rows.append({
                "match_id": row.get("match_id", ""), "league": league,
                "season": season, "date": date,
                "home_id": row["home_team_id"], "home": row.get("home_team", ""),
                "away_id": row["away_team_id"], "away": row.get("away_team", ""),
                "yh": home_goals, "ya": away_goals,
            })
    return sorted(rows, key=lambda item: (item["date"], item["match_id"]))


def season_number(season):
    return int(str(season)[:4])


class DC:
    def __init__(self, initial=None):
        self.a = defaultdict(float)
        self.d = defaultdict(float)
        if initial:
            for team, values in initial.items():
                self.a[team], self.d[team] = values
        self.h = 0.28
        self.rho = 0.0

    def fit(self, games, cutoff):
        # The production fit uses exactly these multiplicative updates.
        for _ in range(14):
            obs_att = defaultdict(float)
            exp_att = defaultdict(float)
            obs_def = defaultdict(float)
            exp_def = defaultdict(float)
            sum_obs = sum_exp = 0.0
            for game in games:
                weight = 0.5 ** ((cutoff - game["date"]).days / HALF_LIFE)
                lh, la = self.lambdas(game["home_id"], game["away_id"])
                yh, ya = game["yh"], game["ya"]
                obs_att[game["home_id"]] += weight * yh
                exp_att[game["home_id"]] += weight * lh
                obs_att[game["away_id"]] += weight * ya
                exp_att[game["away_id"]] += weight * la
                obs_def[game["away_id"]] += weight * yh
                exp_def[game["away_id"]] += weight * lh
                obs_def[game["home_id"]] += weight * ya
                exp_def[game["home_id"]] += weight * la
                sum_obs += weight * yh
                sum_exp += weight * lh
            for team in set(obs_att) | set(exp_att):
                self.a[team] += 0.7 * math.log((obs_att[team] + 0.25) /
                                               (exp_att[team] + 0.25))
            for team in set(obs_def) | set(exp_def):
                self.d[team] += 0.7 * math.log((obs_def[team] + 0.25) /
                                               (exp_def[team] + 0.25))
            self.h += 0.7 * math.log((sum_obs + 0.25) / (sum_exp + 0.25))

        best_rho, best_ll = RHO_GRID[0], None
        for rho in RHO_GRID:
            ll = 0.0
            for game in games:
                if game["yh"] <= 1 or game["ya"] <= 1:
                    weight = 0.5 ** ((cutoff - game["date"]).days / HALF_LIFE)
                    lh, la = self.lambdas(game["home_id"], game["away_id"])
                    correction = tau(game["yh"], game["ya"], lh, la, rho)
                    if correction > 0:
                        ll += weight * math.log(correction)
            if best_ll is None or ll > best_ll:
                best_ll, best_rho = ll, rho
        self.rho = best_rho

    def lambdas(self, home, away):
        return (math.exp(self.a[home] + self.d[away] + self.h),
                math.exp(self.a[away] + self.d[home]))

    def probabilities(self, home, away):
        lh, la = self.lambdas(home, away)
        matrix = [[pois(x, lh) * pois(y, la) * tau(x, y, lh, la, self.rho)
                   for y in range(MAX_GOALS + 1)]
                  for x in range(MAX_GOALS + 1)]
        total = sum(sum(row) for row in matrix)
        home_win = sum(matrix[x][y] for x in range(11) for y in range(11) if x > y) / total
        draw = sum(matrix[x][x] for x in range(11)) / total
        over = sum(matrix[x][y] for x in range(11) for y in range(11)
                   if x + y > 2) / total
        return {"p_home": home_win, "p_draw": draw, "p_away": 1.0 - home_win - draw,
                "p_over25": over, "lam_home": lh, "lam_away": la}


def training_and_target(j3, target_season):
    train = [m for m in j3 if season_number(m["season"]) < int(target_season)]
    target = [m for m in j3 if m["season"] == str(target_season)]
    assert all(m["season"] != "2025" for m in train), "dev training leaked virgin season"
    assert str(target_season) != "2025", "dev path cannot evaluate virgin season"
    cutoff = min(m["date"] for m in target)
    return train, target, cutoff


def mover_initials(train, target_season, j2):
    mean_goals = sum(m["yh"] + m["ya"] for m in train) / (2.0 * len(train))
    previous = str(int(target_season) - 1)
    j2_games = [m for m in j2 if m["season"] == previous]
    appearances = defaultdict(int)
    gf = defaultdict(int)
    ga = defaultdict(int)
    for match in j2_games:
        appearances[match["home_id"]] += 1
        appearances[match["away_id"]] += 1
        gf[match["home_id"]] += match["yh"]
        gf[match["away_id"]] += match["ya"]
        ga[match["home_id"]] += match["ya"]
        ga[match["away_id"]] += match["yh"]
    return mean_goals, {team: (gf[team], ga[team], appearances[team])
                        for team in appearances}


def make_initials(train, target, target_season, j2, x2):
    teams = {m["home_id"] for m in train} | {m["away_id"] for m in train}
    teams |= {m["home_id"] for m in target} | {m["away_id"] for m in target}
    initials = {team: (0.0, 0.0) for team in teams}
    if not x2:
        return initials
    mean_goals = sum(m["yh"] + m["ya"] for m in train) / (2.0 * len(train))
    previous = str(int(target_season) - 1)
    j2_games = [m for m in j2 if m["season"] == previous]
    stats = defaultdict(lambda: [0, 0, 0])
    for match in j2_games:
        for team, scored, conceded in ((match["home_id"], match["yh"], match["ya"]),
                                       (match["away_id"], match["ya"], match["yh"])):
            stats[team][0] += 1
            stats[team][1] += scored
            stats[team][2] += conceded
    target_teams = set(initials)
    for team in target_teams:
        games, goals_for, goals_against = stats.get(team, (0, 0, 0))
        if games >= 10:
            gf = max(0.30, goals_for / games + 0.496)
            ga = max(0.30, goals_against / games - 0.353)
            initials[team] = (math.log(gf / mean_goals), math.log(ga / mean_goals))
    return initials


def fit_arm(train, target, target_season, j2, x2):
    cutoff = min(m["date"] for m in target)
    model = DC(make_initials(train, target, target_season, j2, x2))
    model.fit(train, cutoff)
    return model


def baseline(train):
    n = float(len(train))
    home = sum(m["yh"] > m["ya"] for m in train) / n
    draw = sum(m["yh"] == m["ya"] for m in train) / n
    over = sum(m["yh"] + m["ya"] > 2 for m in train) / n
    return (home, draw, 1.0 - home - draw), over


def logloss(p, actual):
    return -math.log(max(p[actual], 1e-15))


def rps(p, actual):
    observed = [1.0 if actual == i else 0.0 for i in range(3)]
    return 0.5 * sum((sum(p[:k + 1]) - sum(observed[:k + 1])) ** 2 for k in range(2))


def evaluate(predictions, matches):
    ll = []
    rps_values = []
    ou = []
    home_diffs = []
    over_diffs = []
    for prediction, match in zip(predictions, matches):
        actual = 0 if match["yh"] > match["ya"] else 1 if match["yh"] == match["ya"] else 2
        p = [prediction["p_home"], prediction["p_draw"], prediction["p_away"]]
        over_actual = 1 if match["yh"] + match["ya"] > 2 else 0
        ll.append(logloss(p, actual))
        rps_values.append(rps(p, actual))
        ou.append(-math.log(max(prediction["p_over25"], 1e-15)) if over_actual
                  else -math.log(max(1.0 - prediction["p_over25"], 1e-15)))
        home_diffs.append(prediction["p_home"] - (1.0 if actual == 0 else 0.0))
        over_diffs.append(prediction["p_over25"] - over_actual)
    return {"n": len(matches), "ll": sum(ll) / len(ll), "rps": sum(rps_values) / len(rps_values),
            "ou_ll": sum(ou) / len(ou), "home_calibration": calibration(home_diffs, predictions, matches, 0),
            "ou_calibration": calibration(over_diffs, predictions, matches, 1)}


def calibration(diffs, predictions, matches, kind):
    n = len(diffs)
    actual = sum((m["yh"] > m["ya"]) if kind == 0 else (m["yh"] + m["ya"] > 2)
                 for m in matches) / n
    predicted = sum((p["p_home"] if kind == 0 else p["p_over25"]) for p in predictions) / n
    mean = sum(diffs) / n
    variance = sum((value - mean) ** 2 for value in diffs) / (n - 1) if n > 1 else 0.0
    return {"mean_pred": predicted, "actual": actual, "diff_pp": 100.0 * mean,
            "se_pp": 100.0 * math.sqrt(variance / n)}


def fit_predict(train, target, target_season, j2, x2):
    model = fit_arm(train, target, target_season, j2, x2)
    predictions = [model.probabilities(m["home_id"], m["away_id"]) for m in target]
    return model, predictions


def run_dev(j3, j2):
    arms = {"gate_zero": [], "x2": []}
    baselines = []
    seasons = ["2022", "2023", "2024"]
    for season in seasons:
        train, target, cutoff = training_and_target(j3, season)
        base_1x2, base_over = baseline(train)
        base_predictions = [{"p_home": base_1x2[0], "p_draw": base_1x2[1],
                             "p_away": base_1x2[2], "p_over25": base_over}
                            for _ in target]
        base_metrics = evaluate(base_predictions, target)
        baselines.append({"season": season, "n": len(target), "ll": base_metrics["ll"],
                          "rps": base_metrics["rps"], "ou_ll": base_metrics["ou_ll"]})
        for name, x2 in (("gate_zero", False), ("x2", True)):
            _, predictions = fit_predict(train, target, season, j2, x2)
            metrics = evaluate(predictions, target)
            arms[name].append({"season": season, **metrics})
    for name in arms:
        all_rows = []
        for season in seasons:
            train, target, _ = training_and_target(j3, season)
            _, predictions = fit_predict(train, target, season, j2, name == "x2")
            all_rows.extend(zip(predictions, target))
        arms[name].append({"season": "pooled", **evaluate([p for p, _ in all_rows],
                                                            [m for _, m in all_rows])})
    pooled_base = {"n": sum(b["n"] for b in baselines),
                   "ll": sum(b["ll"] * b["n"] for b in baselines) / sum(b["n"] for b in baselines),
                   "rps": sum(b["rps"] * b["n"] for b in baselines) / sum(b["n"] for b in baselines),
                   "ou_ll": sum(b["ou_ll"] * b["n"] for b in baselines) / sum(b["n"] for b in baselines)}
    for name in arms:
        for row in arms[name][:-1]:
            row["sign_vs_climatology"] = row["ll"] < next(b["ll"] for b in baselines if b["season"] == row["season"])
        arms[name][-1]["sign_check_count"] = sum(row["sign_vs_climatology"] for row in arms[name][:-1])
    return {"arms": arms, "climatology": baselines + [{"season": "pooled", **pooled_base}]}


def write_csv(rows):
    fields = ["match_id", "date", "home_team_id", "home_team", "away_team_id", "away_team",
              "home_goals", "away_goals"]
    for prefix in ("gz", "x2"):
        fields += [prefix + "_" + key for key in
                   ("p_home", "p_draw", "p_away", "p_over25", "lam_home", "lam_away")]
    with open(PREDICTIONS, "w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main(mode):
    j3 = read_matches(J3_FILE, "J3")
    j2 = read_matches(J2_FILE, "J2")
    dev = run_dev(j3, j2)
    with open(RESULTS + "/dev_results.json", "w", encoding="utf-8") as handle:
        json.dump(dev, handle, indent=2)
    print("arm       season  n     LL       RPS      OU2.5 LL")
    for arm in ("gate_zero", "x2"):
        for row in dev["arms"][arm]:
            print("%-9s %-7s %4d  %.5f  %.5f  %.5f" %
                  (arm, row["season"], row["n"], row["ll"], row["rps"], row["ou_ll"]))
    for row in dev["climatology"]:
        print("%-9s %-7s %4d  %.5f  %.5f  %.5f" %
              ("climatology", row["season"], row["n"], row["ll"], row["rps"], row["ou_ll"]))
    if mode == "dev":
        return

    target = [m for m in j3 if m["season"] == "2025"]
    train = [m for m in j3 if season_number(m["season"]) in {2021, 2022, 2023, 2024}]
    assert not any(season_number(m["season"]) in {2026, 2027} for m in train + target)
    predictions_by_arm = {}
    models = {}
    for name, x2 in (("gate_zero", False), ("x2", True)):
        models[name], predictions_by_arm[name] = fit_predict(train, target, "2025", j2, x2)
    virgin = {}
    rows = []
    for i, match in enumerate(target):
        row = {"match_id": match["match_id"], "date": match["date"].isoformat(),
               "home_team_id": match["home_id"], "home_team": match["home"],
               "away_team_id": match["away_id"], "away_team": match["away"],
               "home_goals": match["yh"], "away_goals": match["ya"]}
        for name, prefix in (("gate_zero", "gz"), ("x2", "x2")):
            prediction = predictions_by_arm[name][i]
            row.update({prefix + "_" + key: value for key, value in prediction.items()})
        rows.append(row)
    write_csv(rows)
    for name in ("gate_zero", "x2"):
        virgin[name] = evaluate(predictions_by_arm[name], target)
    base_1x2, _ = baseline(train)
    climatology_predictions = [{"p_home": base_1x2[0], "p_draw": base_1x2[1],
                                "p_away": base_1x2[2], "p_over25": 0.5} for _ in target]
    virgin["climatology_virgin_ll"] = evaluate(climatology_predictions, target)["ll"]
    with open(RESULTS + "/virgin_results.json", "w", encoding="utf-8") as handle:
        json.dump(virgin, handle, indent=2)
    fitted = {}
    for name, model in models.items():
        fitted[name] = {"rho": model.rho, "h": model.h,
                        "teams": {team: {"a": model.a[team], "d": model.d[team]}
                                  for team in sorted(set(model.a) | set(model.d))}}
    with open(RESULTS + "/fitted_params_virgin.json", "w", encoding="utf-8") as handle:
        json.dump(fitted, handle, indent=2)
    print("\nvirgin arm       n     LL       RPS      OU2.5 LL")
    for name in ("gate_zero", "x2"):
        row = virgin[name]
        print("%-15s %4d  %.5f  %.5f  %.5f" % (name, row["n"], row["ll"], row["rps"], row["ou_ll"]))


if __name__ == "__main__":
    argument = sys.argv[1] if len(sys.argv) > 1 else "--virgin"
    if argument not in ("--dev", "--virgin"):
        raise SystemExit("usage: g_j3.py [--dev|--virgin]")
    main(argument[2:])
