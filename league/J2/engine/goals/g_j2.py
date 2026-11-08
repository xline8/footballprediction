#!/usr/bin/env python3
"""J2 goals model: pure-Python Dixon-Coles walk-forward engine."""

import csv
import json
import math
import os
import sys
from collections import defaultdict
from datetime import date


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.."))
J2_DATA = os.path.join(ROOT, "league/J2/data/j2_matches.csv")
J1_DATA = os.path.join(ROOT, "league/J1/data/j1_matches.csv")
J3_DATA = os.path.join(ROOT, "league/J3/data/j3_matches.csv")
OUT_DIR = os.path.dirname(__file__)
PRED_DIR = os.path.join(ROOT, "league/J2/predictions")

DEV_SEASONS = ("2021", "2022", "2023", "2024")
VIRGIN_SEASONS = ("2025",)
EXCLUDED_SEASON = "2026/2027"
MAX_TRAIN = 4000
MAXG = 10
RHO_GRID = (0.0, -0.05, -0.10, -0.15)


def parse_date(value):
    return date.fromisoformat(str(value)[:10])


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


class DC:
    def __init__(self):
        self.a = {}
        self.d = {}
        self.h = 0.28
        self.rho = -0.07
        self.L = None
        self.n_trained = 0

    def _lam(self, home, away):
        return (math.exp(self.a.get(home, 0.0) + self.d.get(away, 0.0) + self.h),
                math.exp(self.a.get(away, 0.0) + self.d.get(home, 0.0)))

    def fit(self, games, cutoff, hl=270, init_ratings=None):
        games = sorted(games, key=lambda g: g[4])[-MAX_TRAIN:]
        self.n_trained = len(games)
        self.a = {}
        self.d = {}
        if init_ratings:
            self.a.update({int(k): float(v[0]) for k, v in init_ratings.items()})
            self.d.update({int(k): float(v[1]) for k, v in init_ratings.items()})
        self.h = 0.28
        self.rho = -0.07
        if not games:
            return
        self.L = sum(g[2] + g[3] for g in games) / (2.0 * len(games))
        for _ in range(14):
            obs_att = defaultdict(float); exp_att = defaultdict(float)
            obs_def = defaultdict(float); exp_def = defaultdict(float)
            sh_obs = sh_exp = 0.0
            for home, away, yh, ya, dt in games:
                w = 0.5 ** ((cutoff - dt).days / hl)
                lh, la = self._lam(home, away)
                obs_att[home] += w * yh; exp_att[home] += w * lh
                obs_att[away] += w * ya; exp_att[away] += w * la
                obs_def[away] += w * yh; exp_def[away] += w * lh
                obs_def[home] += w * ya; exp_def[home] += w * la
                sh_obs += w * yh; sh_exp += w * lh
            for team in set(obs_att) | set(exp_att):
                self.a[team] = self.a.get(team, 0.0) + 0.7 * math.log(
                    (obs_att[team] + 0.25) / (exp_att[team] + 0.25))
            for team in set(obs_def) | set(exp_def):
                self.d[team] = self.d.get(team, 0.0) + 0.7 * math.log(
                    (obs_def[team] + 0.25) / (exp_def[team] + 0.25))
            self.h += 0.7 * math.log((sh_obs + 0.25) / (sh_exp + 0.25))
        best_rho, best_ll = RHO_GRID[0], None
        for rho in RHO_GRID:
            ll = 0.0
            for home, away, yh, ya, dt in games:
                if yh <= 1 and ya <= 1:
                    w = 0.5 ** ((cutoff - dt).days / hl)
                    lh, la = self._lam(home, away)
                    ll += w * math.log(max(tau(yh, ya, lh, la, rho), 1e-300))
            if best_ll is None or ll > best_ll:
                best_ll, best_rho = ll, rho
        self.rho = best_rho

    def probs(self, lh, la):
        matrix = [[pois(x, lh) * pois(y, la) * tau(x, y, lh, la, self.rho)
                   for y in range(MAXG + 1)] for x in range(MAXG + 1)]
        total = sum(sum(row) for row in matrix)
        ph = sum(matrix[x][y] for x in range(MAXG + 1) for y in range(MAXG + 1)
                 if x > y) / total
        pd = sum(matrix[x][x] for x in range(MAXG + 1)) / total
        over = sum(matrix[x][y] for x in range(MAXG + 1) for y in range(MAXG + 1)
                   if x + y > 2) / total
        return {"p_home": ph, "p_draw": pd, "p_away": 1.0 - ph - pd,
                "p_over25": over}


def load_matches(path, allowed_seasons=None):
    rows = []
    with open(path, newline="") as handle:
        for raw in csv.DictReader(handle):
            season = str(raw["season"])
            if season == EXCLUDED_SEASON or (allowed_seasons and season not in allowed_seasons):
                continue
            try:
                rows.append({
                    "match_id": raw["match_id"], "season": season,
                    "date": parse_date(raw["date"]),
                    "home_team_id": int(raw["home_team_id"]),
                    "away_team_id": int(raw["away_team_id"]),
                    "home_team": raw.get("home_team", ""), "away_team": raw.get("away_team", ""),
                    "home_goals": int(raw["home_goals"]), "away_goals": int(raw["away_goals"]),
                })
            except (KeyError, TypeError, ValueError):
                continue
    return sorted(rows, key=lambda r: (r["date"], r["match_id"]))


def _games(rows):
    return [(r["home_team_id"], r["away_team_id"], r["home_goals"], r["away_goals"], r["date"])
            for r in rows]


def _membership(rows):
    result = defaultdict(set)
    for r in rows:
        result[r["season"]].update((r["home_team_id"], r["away_team_id"]))
    return result


def _prior_ratings(j2_rows, j1_rows, j3_rows, season, cutoff, train_rows):
    try:
        previous = str(int(season) - 1)
    except ValueError:
        return {}
    j2_members = _membership([r for r in j2_rows if r["season"] == season])
    j1_members = _membership(j1_rows)
    j3_members = _membership(j3_rows)
    prior = {}
    L = sum(r["home_goals"] + r["away_goals"] for r in train_rows) / (2.0 * len(train_rows)) if train_rows else None
    if not L:
        return prior
    for team in j2_members.get(season, set()):
        if team in j3_members.get(previous, set()) and team not in j2_members.get(previous, set()):
            source, gf_adj, ga_adj = j3_rows, -0.477, 0.560
        elif team in j1_members.get(previous, set()) and team not in j2_members.get(previous, set()):
            source, gf_adj, ga_adj = j1_rows, 0.485, -0.550
        else:
            continue
        matches = [r for r in source if r["season"] == previous and r["date"] < cutoff
                   and (r["home_team_id"] == team or r["away_team_id"] == team)]
        if not matches:
            continue
        gf = sum(r["home_goals"] if r["home_team_id"] == team else r["away_goals"] for r in matches) / len(matches)
        ga = sum(r["away_goals"] if r["home_team_id"] == team else r["home_goals"] for r in matches) / len(matches)
        gf = min(3.0, max(0.3, gf + gf_adj)); ga = min(3.0, max(0.3, ga + ga_adj))
        prior[team] = (math.log(gf / L), math.log(ga / L))
    return prior


def _baseline(rows):
    if not rows:
        return (1 / 3, 1 / 3, 1 / 3), 0.5
    n = len(rows)
    h = sum(r["home_goals"] > r["away_goals"] for r in rows) / n
    d = sum(r["home_goals"] == r["away_goals"] for r in rows) / n
    over = sum(r["home_goals"] + r["away_goals"] > 2 for r in rows) / n
    return (h, d, 1 - h - d), over


def walk_forward(history_rows, arm, seasons, j1_rows=None, j3_rows=None):
    j1_rows = j1_rows or []; j3_rows = j3_rows or []
    selected = [r for r in history_rows if r["season"] in seasons]
    groups = defaultdict(list)
    for row in selected:
        groups[(row["date"].year, row["date"].month)].append(row)
    predictions = []
    for year_month in sorted(groups):
        month_rows = groups[year_month]
        month_start = date(year_month[0], year_month[1], 1)
        train = [r for r in history_rows if r["date"] < month_start]
        prior = {}
        season = month_rows[0]["season"]
        if arm == "x2":
            prior = _prior_ratings(history_rows, j1_rows, j3_rows, season, month_start, train)
        model = DC()
        model.fit(_games(train), month_start, init_ratings=prior)
        base1x2, base_over = _baseline(train)
        for row in month_rows:
            lh, la = model._lam(row["home_team_id"], row["away_team_id"])
            p = model.probs(lh, la)
            predictions.append(dict(row, arm=arm, month=f"{year_month[0]:04d}-{year_month[1]:02d}",
                                    lam_home=lh, lam_away=la, rho=model.rho,
                                    baseline_1x2=base1x2, baseline_over=base_over, **p,
                                    mover_prior_count=len(prior)))
    return predictions


def _metric(rows):
    if not rows:
        return {"n": 0, "1x2_ll": None, "rps": None, "ou2.5_ll": None}
    ll = rps = ou = 0.0
    for r in rows:
        actual = 0 if r["home_goals"] > r["away_goals"] else 1 if r["home_goals"] == r["away_goals"] else 2
        probs = (r["p_home"], r["p_draw"], r["p_away"])
        ll -= math.log(max(probs[actual], 1e-12))
        cum_p = probs[0]; cum_y = 1.0 if actual == 0 else 0.0
        rps += 0.5 * (cum_p - cum_y) ** 2
        cum_p += probs[1]; cum_y = 1.0 if actual <= 1 else 0.0
        rps += 0.5 * (cum_p - cum_y) ** 2
        y_over = 1.0 if r["home_goals"] + r["away_goals"] > 2 else 0.0
        ou -= math.log(max(r["p_over25"] if y_over else 1 - r["p_over25"], 1e-12))
    n = len(rows)
    return {"n": n, "1x2_ll": ll / n, "rps": rps / n, "ou2.5_ll": ou / n}


def _baseline_metrics(rows):
    converted = []
    for r in rows:
        p = r["baseline_1x2"]
        converted.append(dict(r, p_home=p[0], p_draw=p[1], p_away=p[2], p_over25=r["baseline_over"]))
    return _metric(converted)


def run_dev():
    j2 = load_matches(J2_DATA, DEV_SEASONS)
    j1 = load_matches(J1_DATA); j3 = load_matches(J3_DATA)
    result = {"dev_seasons": list(DEV_SEASONS), "scoring_excluded_month": "2021-02",
              "arms": {}, "baselines": {}, "mover_counts": {}}
    all_baselines = []
    for arm in ("gate_zero", "x2"):
        pred = walk_forward(j2, "x2" if arm == "x2" else "gate_zero", DEV_SEASONS, j1, j3)
        scored = [r for r in pred if r["month"] != "2021-02"]
        result["arms"][arm] = {"pooled": _metric(scored), "per_season": {
            s: _metric([r for r in scored if r["season"] == s]) for s in DEV_SEASONS}}
        if arm == "gate_zero":
            all_baselines = scored
        result["mover_counts"][arm] = {s: max((r["mover_prior_count"] for r in pred if r["season"] == s), default=0)
                                        for s in DEV_SEASONS}
    result["baselines"] = {"pooled": _baseline_metrics(all_baselines), "per_season": {
        s: _baseline_metrics([r for r in all_baselines if r["season"] == s]) for s in DEV_SEASONS}}
    path = os.path.join(OUT_DIR, "dev_results.json")
    with open(path, "w") as handle:
        json.dump(result, handle, indent=2, sort_keys=True)
    print(json.dumps(result, indent=2, sort_keys=True))


def run_virgin():
    history = [r for r in load_matches(J2_DATA) if r["season"] in DEV_SEASONS + VIRGIN_SEASONS]
    j2 = [r for r in history if r["season"] in VIRGIN_SEASONS]
    j1 = load_matches(J1_DATA); j3 = load_matches(J3_DATA)
    rows = []
    for arm in ("gate_zero", "x2"):
        rows.extend(walk_forward(history, "x2" if arm == "x2" else "gate_zero", VIRGIN_SEASONS, j1, j3))
    os.makedirs(PRED_DIR, exist_ok=True)
    fields = ["match_id", "date", "home_team_id", "home_team", "away_team_id", "away_team", "home_goals", "away_goals",
              "arm", "lam_home", "lam_away", "rho", "p_home", "p_draw", "p_away", "p_over25"]
    with open(os.path.join(PRED_DIR, "g_j2_virgin_predictions.csv"), "w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields); writer.writeheader()
        for r in sorted(rows, key=lambda x: (x["date"], x["match_id"], x["arm"])):
            writer.writerow({k: r[k].isoformat() if isinstance(r[k], date) else r[k] for k in fields})
    cutoff = date(2025, 1, 1)
    train = [r for r in history if r["date"] < cutoff and int(r["season"]) <= 2024]
    fitted = {}
    for arm in ("gate_zero", "x2"):
        prior = _prior_ratings(history, j1, j3, "2025", cutoff, train) if arm == "x2" else {}
        model = DC(); model.fit(_games(train), cutoff, init_ratings=prior)
        fitted[arm] = {"h": model.h, "rho": model.rho, "L": model.L,
                       "ratings": {str(t): {"a": model.a.get(t, 0.0), "d": model.d.get(t, 0.0)} for t in sorted(set(model.a) | set(model.d))},
                       "mover_priors_applied": {str(t): {"a": v[0], "d": v[1]} for t, v in prior.items()}}
    with open(os.path.join(OUT_DIR, "fitted_params.json"), "w") as handle:
        json.dump(fitted, handle, indent=2, sort_keys=True)


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "dev"
    if mode == "dev":
        run_dev()
    elif mode == "virgin":
        run_virgin()
    elif mode == "all":
        run_dev(); run_virgin()
    else:
        raise SystemExit("usage: g_j2.py [dev|virgin|all]")
