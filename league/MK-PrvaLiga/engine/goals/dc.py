"""Development-only G-MK Dixon-Coles engine and walk-forward harness."""
import csv
import json
from collections import defaultdict, deque
from pathlib import Path

import numpy as np
from scipy.optimize import minimize
from scipy.stats import poisson

MAXG = 10
RHO_GRID = (0.0, -0.05, -0.10, -0.15)
HALF_LIFE_DAYS = 270
RIDGE = 1e-3
EPS = 1e-12
SHRINK_MIN_MATCHES = 6
WARMUP_SEASON = "2021/2022"
DEV_SEASONS = ("2022/2023", "2023/2024", "2024/2025")
EXPECTED_COUNTS = {WARMUP_SEASON: 198, "2022/2023": 165, "2023/2024": 198, "2024/2025": 186}
DEV_COUNT = 549


def _ordered(rows):
    return sorted(rows, key=lambda r: (r["date"], r["match_id"]))


def load_dev_data(path=None):
    """Read and materialize only warm-up and dev rows; later seasons are never loaded."""
    if path is None:
        path = Path(__file__).parents[2] / "data" / "mk_prva_liga_matches.csv"
    allowed = {WARMUP_SEASON, *DEV_SEASONS}
    rows = []
    with open(path, encoding="utf-8", newline="") as fh:
        for raw in csv.DictReader(fh):
            if raw["season"] not in allowed or int(raw["is_awarded"]) != 0:
                continue
            rows.append({
                "match_id": int(raw["match_id"]), "season": raw["season"],
                "date": raw["date"], "home_team": raw["home_team"], "away_team": raw["away_team"],
                "home_team_id": int(raw["home_team_id"]), "away_team_id": int(raw["away_team_id"]),
                "home_goals": int(raw["home_goals"]), "away_goals": int(raw["away_goals"]),
            })
    seasons = {r["season"] for r in rows}
    if seasons != allowed:
        raise RuntimeError(f"DEV SEASON SET MISMATCH: got {sorted(seasons)}")
    counts = {s: sum(r["season"] == s for r in rows) for s in allowed}
    if counts != EXPECTED_COUNTS or sum(counts[s] for s in DEV_SEASONS) != DEV_COUNT:
        raise RuntimeError(f"DEV ROW COUNT MISMATCH: got {counts}")
    return _ordered(rows)


def _arrays(rows):
    teams = sorted({r["home_team_id"] for r in rows} | {r["away_team_id"] for r in rows})
    idx = {t: i for i, t in enumerate(teams)}
    return teams, np.array([idx[r["home_team_id"]] for r in rows]), np.array([idx[r["away_team_id"]] for r in rows]), np.array([r["home_goals"] for r in rows], dtype=float), np.array([r["away_goals"] for r in rows], dtype=float)


def _tau(x, y, lh, la, rho):
    if x == 0 and y == 0: return 1 - lh * la * rho
    if x == 0 and y == 1: return 1 + lh * rho
    if x == 1 and y == 0: return 1 + la * rho
    if x == 1 and y == 1: return 1 - rho
    return 1.0


def fit_dc(rows, cutoff):
    teams, hi, ai, hg, ag = _arrays(rows)
    n = len(teams)
    days = np.array([(np.datetime64(cutoff) - np.datetime64(r["date"])) / np.timedelta64(1, "D") for r in rows], dtype=float)
    weights = 0.5 ** (days / HALF_LIFE_DAYS)

    def unpack(x):
        att = np.r_[x[:n - 1], -np.sum(x[:n - 1])]
        defence = np.r_[x[n - 1:2 * n - 2], -np.sum(x[n - 1:2 * n - 2])]
        return att, defence, x[-1]

    def base_ll(x):
        att, defence, home = unpack(x)
        lh = np.exp(att[hi] - defence[ai] + home)
        la = np.exp(att[ai] - defence[hi])
        return np.sum(weights * (hg * np.log(lh) - lh + ag * np.log(la) - la))

    def objective(x):
        return -base_ll(x) + RIDGE * np.sum(x ** 2)

    x0 = np.zeros(2 * n - 1)
    x0[-1] = 0.25
    sol = minimize(objective, x0, method="L-BFGS-B", options={"maxiter": 500})
    if not sol.success:
        raise RuntimeError(f"DC fit failed: {sol.message}")
    att, defence, home = unpack(sol.x)
    lh = np.exp(att[hi] - defence[ai] + home)
    la = np.exp(att[ai] - defence[hi])

    def dc_ll(rho):
        return float(sum(w * (np.log(max(_tau(x, y, a, b, rho), EPS)) + x * np.log(a) - a + y * np.log(b) - b)
                         for x, y, a, b, w in zip(hg, ag, lh, la, weights)))

    rho = max(RHO_GRID, key=dc_ll)
    return {"teams": teams, "att": att, "def": defence, "home": float(home), "rho": float(rho), "train_ll": dc_ll(rho)}


def matrix_from_lambdas(lh, la, rho):
    ks = np.arange(MAXG + 1)
    matrix = np.outer(poisson.pmf(ks, lh), poisson.pmf(ks, la))
    matrix[0, 0] *= _tau(0, 0, lh, la, rho)
    matrix[0, 1] *= _tau(0, 1, lh, la, rho)
    matrix[1, 0] *= _tau(1, 0, lh, la, rho)
    matrix[1, 1] *= _tau(1, 1, lh, la, rho)
    matrix = np.clip(matrix, 0, None)
    return matrix / matrix.sum()


def predict_matrix(model, home_id, away_id, factors=None):
    idx = {t: i for i, t in enumerate(model["teams"])}
    factors = factors or {}
    ah = model["att"][idx[home_id]] * factors.get(home_id, 1.0) if home_id in idx else 0.0
    dh = model["def"][idx[home_id]] * factors.get(home_id, 1.0) if home_id in idx else 0.0
    aa = model["att"][idx[away_id]] * factors.get(away_id, 1.0) if away_id in idx else 0.0
    da = model["def"][idx[away_id]] * factors.get(away_id, 1.0) if away_id in idx else 0.0
    return matrix_from_lambdas(np.exp(ah - da + model["home"]), np.exp(aa - dh), model["rho"])


def probs_1x2_ou(matrix):
    home = float(np.tril(matrix, -1).sum())
    draw = float(np.trace(matrix))
    away = float(np.triu(matrix, 1).sum())
    ks = np.arange(MAXG + 1)
    return home, draw, away, float(matrix[(ks[:, None] + ks[None, :]) > 2].sum())


def match_counts(rows):
    counts = defaultdict(int)
    for r in rows:
        counts[r["home_team_id"]] += 1; counts[r["away_team_id"]] += 1
    return dict(counts)


def shrink_factor(counts, team_id):
    return min(1.0, counts.get(int(team_id), 0) / SHRINK_MIN_MATCHES)


def _row(model, r, counts, arm):
    factors = {}
    if arm == "SHRINK":
        factors = {r["home_team_id"]: shrink_factor(counts, r["home_team_id"]), r["away_team_id"]: shrink_factor(counts, r["away_team_id"])}
    p = probs_1x2_ou(predict_matrix(model, r["home_team_id"], r["away_team_id"], factors))
    return {**r, "p_home": p[0], "p_draw": p[1], "p_away": p[2], "p_over25": p[3], "fitted_h": model["home"], "fitted_rho": model["rho"]}


def metrics(rows):
    vals = []
    for r in rows:
        outcome = 0 if r["home_goals"] > r["away_goals"] else (1 if r["home_goals"] == r["away_goals"] else 2)
        p = np.array([r["p_home"], r["p_draw"], r["p_away"]])
        obs = np.eye(3)[outcome]
        over = float(r["home_goals"] + r["away_goals"] > 2)
        vals.append((-np.log(max(p[outcome], EPS)), 0.5 * np.sum((np.cumsum(p)[:2] - np.cumsum(obs)[:2]) ** 2), -(over * np.log(max(r["p_over25"], EPS)) + (1 - over) * np.log(max(1 - r["p_over25"], EPS)))))
    a = np.asarray(vals)
    return {"n": len(rows), "ll_1x2": float(a[:, 0].mean()), "rps": float(a[:, 1].mean()), "ll_ou25": float(a[:, 2].mean())}


def _base_row(r, p):
    return {**r, "p_home": p[0], "p_draw": p[1], "p_away": p[2], "p_over25": p[3], "fitted_h": None, "fitted_rho": None}


def league_mean_goals(rows):
    return float(sum(r["home_goals"] + r["away_goals"] for r in rows) / (2 * len(rows)))


def climatology_rows(train, test):
    outcomes = np.array([0 if r["home_goals"] > r["away_goals"] else (1 if r["home_goals"] == r["away_goals"] else 2) for r in train])
    p = [float(np.mean(outcomes == k)) for k in range(3)]
    p.append(float(np.mean([r["home_goals"] + r["away_goals"] > 2 for r in train])))
    return [_base_row(r, p) for r in test]


class Trailing10:
    def __init__(self, league_mean): self.hist, self.league_mean = {}, float(league_mean)
    def feed(self, rows):
        for r in _ordered(rows):
            self.hist.setdefault(r["home_team_id"], deque(maxlen=10)).append(r["home_goals"])
            self.hist.setdefault(r["away_team_id"], deque(maxlen=10)).append(r["away_goals"])
    def rows_for(self, rows):
        out = []
        for date in sorted({r["date"] for r in rows}):
            group = [r for r in _ordered(rows) if r["date"] == date]
            for r in group:
                lh = np.mean(self.hist[r["home_team_id"]]) if self.hist.get(r["home_team_id"]) else self.league_mean
                la = np.mean(self.hist[r["away_team_id"]]) if self.hist.get(r["away_team_id"]) else self.league_mean
                out.append(_base_row(r, probs_1x2_ou(matrix_from_lambdas(lh, la, 0.0))))
            self.feed(group)
        return out


def _gate(pooled, baseline):
    return {m: {"result": "WIN" if pooled[m] < baseline[m] else "LOSE", "arm": pooled[m], "baseline": baseline[m]} for m in ("ll_1x2", "rps", "ll_ou25")}


def run_goals(out_dir):
    out_dir = Path(out_dir); data = load_dev_data(); arms = ("GateZero", "SHRINK")
    arm_rows = {a: [] for a in arms}; arm_season = {a: {} for a in arms}; fitted = {}
    clim_rows, clim_season, naive_rows, naive_season = [], {}, [], {}
    t10 = Trailing10(league_mean_goals([r for r in data if r["season"] == WARMUP_SEASON])); t10.feed([r for r in data if r["season"] == WARMUP_SEASON])
    for season in DEV_SEASONS:
        cutoff = min(r["date"] for r in data if r["season"] == season)
        train = [r for r in data if r["date"] < cutoff]; test = [r for r in data if r["season"] == season]
        model = fit_dc(train, cutoff); counts = match_counts(train)
        fitted[season] = {"n_train": len(train), "fit_cutoff": cutoff, "arms": {a: {"teams": model["teams"], "attack": model["att"].tolist(), "defence": model["def"].tolist(), "home_intercept": model["home"], "rho": model["rho"], "train_ll": model["train_ll"]} for a in arms}}
        for arm in arms:
            arm_rows[arm].extend(_row(model, r, counts, arm) for r in test); arm_season[arm][season] = metrics(arm_rows[arm][-len(test):])
        c = climatology_rows(train, test); clim_rows.extend(c); clim_season[season] = metrics(c)
        t10.league_mean = league_mean_goals(train); n = t10.rows_for(test); naive_rows.extend(n); naive_season[season] = metrics(n)
    pooled = {a: metrics(arm_rows[a]) for a in arms}; clim_pooled = metrics(clim_rows); naive_pooled = metrics(naive_rows)
    gates = {a: {"vs_climatology": _gate(pooled[a], clim_pooled), "vs_naive_trailing_10": _gate(pooled[a], naive_pooled)} for a in arms}
    gate_pass = {a: all(leg["result"] == "WIN" for side in gates[a].values() for leg in side.values()) for a in arms}
    low = {s: sum(1 for n in match_counts([r for r in data if r["date"] < min(x["date"] for x in data if x["season"] == s)]).values() if 1 <= n <= 5) for s in DEV_SEASONS}
    max_sum_error = max(abs(sum(r[k] for k in ("p_home", "p_draw", "p_away")) - 1.0) for r in arm_rows["GateZero"] + arm_rows["SHRINK"])
    any_nan = any(not np.isfinite(r[k]) for rows in [*arm_rows.values(), clim_rows, naive_rows] for r in rows for k in ("p_home", "p_draw", "p_away", "p_over25"))
    fitted_summary = {s: {a: {"home_intercept": fitted[s]["arms"][a]["home_intercept"], "rho": fitted[s]["arms"][a]["rho"]} for a in arms} for s in DEV_SEASONS}
    dev = {"arms": {a: {"pooled": pooled[a], "per_season": arm_season[a], "gate_dev_pass": gate_pass[a], "gate_legs": gates[a], "fitted_h_rho_by_season": fitted_summary} for a in arms}, "climatology": {"pooled": clim_pooled, "per_season": clim_season}, "naive_trailing_10": {"pooled": naive_pooled, "per_season": naive_season}, "shrink_comparison": {"identical": arm_rows["GateZero"] == arm_rows["SHRINK"], "teams_with_1_to_5_prior_matches": low, "synthetic_check": shrink_factor({123: 3}, 123) == 0.5, "synthetic_factor": shrink_factor({123: 3}, 123)}, "diagnostics": {"max_abs_1x2_sum_minus_1": max_sum_error, "any_nan_probability": bool(any_nan)}, "meta": {"season_order": [WARMUP_SEASON, *DEV_SEASONS], "warm_up": WARMUP_SEASON, "scored": list(DEV_SEASONS), "pooled_n": DEV_COUNT, "fit_scope": "all permitted model matches dated strictly before target season first match", "awarded_excluded": True, "later_seasons_loaded": False, "metric_probability_epsilon": EPS}}
    csv_rows = []
    for i in range(DEV_COUNT):
        base = {k: arm_rows["GateZero"][i][k] for k in ("match_id", "season", "date", "home_team", "away_team", "home_goals", "away_goals")}
        for a, rows in (("gate_zero", arm_rows["GateZero"]), ("shrink", arm_rows["SHRINK"]), ("climatology", clim_rows), ("naive", naive_rows)):
            for k in ("p_home", "p_draw", "p_away", "p_over25"): base[f"{a}_{k}"] = rows[i][k]
        base["fitted_h"] = arm_rows["GateZero"][i]["fitted_h"]; base["fitted_rho"] = arm_rows["GateZero"][i]["fitted_rho"]; csv_rows.append(base)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "results_dev.json").write_text(json.dumps(dev, indent=1) + "\n")
    (out_dir / "fitted_params_dev.json").write_text(json.dumps(fitted, indent=1) + "\n")
    import pandas as pd
    pd.DataFrame(csv_rows).to_csv(out_dir / "results_dev.csv", index=False)
    return dev
