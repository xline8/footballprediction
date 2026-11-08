"""Development-only G-TN Dixon-Coles engine and harness."""
import json
from collections import defaultdict, deque
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy.stats import poisson

MAXG = 10
RHO_GRID = (0.0, -0.05, -0.10, -0.15)
HALF_LIFE_DAYS = 270
SHRINK_MIN_MATCHES = 6
WARMUP_SEASON = "2021/2022"
DEV_SEASONS = ["2022/2023", "2023/2024", "2024/2025"]
VIRGIN_SEASON = "2025/2026"
RESERVE_SEASON = "2026/2027"
EXPECTED_COUNTS = {WARMUP_SEASON: 156, "2022/2023": 195, "2023/2024": 170, "2024/2025": 237}
DEV_COUNT = 602


def _ordered(df):
    return df.sort_values(["date", "match_id"], kind="mergesort").reset_index(drop=True)


def load_dev_data(path=None):
    """Load warm-up and dev rows only; virgin/reserve rows cannot enter the run."""
    if path is None:
        path = Path(__file__).parents[2] / "data" / "tn_matches.csv"
    data = pd.read_csv(path, parse_dates=["date"])
    data["season"] = data["season"].astype(str)
    required = {WARMUP_SEASON, *DEV_SEASONS, VIRGIN_SEASON, RESERVE_SEASON}
    unknown = set(data.season) - required
    if unknown:
        raise RuntimeError(f"UNKNOWN SEASON LABEL IN DATA: {sorted(unknown)}")
    if not data["is_awarded"].isin([0, 1]).all():
        raise RuntimeError("INVALID AWARDED FLAG")
    # These seasons are deliberately not selected, fitted, or scored.
    dev = data[(data["is_awarded"] == 0) & data.season.isin([WARMUP_SEASON, *DEV_SEASONS])].copy()
    counts = dev.groupby("season").size().to_dict()
    if counts != EXPECTED_COUNTS:
        raise RuntimeError(f"DEV ROW COUNT MISMATCH: got {counts}, expected {EXPECTED_COUNTS}")
    if len(dev[dev.season.isin(DEV_SEASONS)]) != DEV_COUNT:
        raise RuntimeError("DEV POOLED COUNT MISMATCH")
    required_cols = ["home_goals", "away_goals", "home_team_id", "away_team_id"]
    if dev[required_cols].isna().any().any():
        raise RuntimeError("DEV DATA: missing required value")
    return _ordered(dev)


def _model_arrays(df):
    teams = sorted(set(df.home_team_id.astype(int)) | set(df.away_team_id.astype(int)))
    idx = {t: i for i, t in enumerate(teams)}
    return (teams, df.home_team_id.astype(int).map(idx).to_numpy(),
            df.away_team_id.astype(int).map(idx).to_numpy(),
            df.home_goals.to_numpy(dtype=float), df.away_goals.to_numpy(dtype=float))


def fit_dc(df, cutoff):
    teams, hi, ai, hg, ag = _model_arrays(df)
    n = len(teams)
    weights = 0.5 ** ((pd.Timestamp(cutoff) - df.date).dt.days.to_numpy(dtype=float) / HALF_LIFE_DAYS)

    def unpack(x):
        att = np.r_[x[:n - 1], -np.sum(x[:n - 1])]
        defence = np.r_[x[n - 1:2 * n - 2], -np.sum(x[n - 1:2 * n - 2])]
        return att, defence, x[-1]

    def poisson_ll(x):
        att, defence, home = unpack(x)
        lh = np.exp(att[hi] - defence[ai] + home)
        la = np.exp(att[ai] - defence[hi])
        return np.sum(weights * (hg * np.log(lh) - lh + ag * np.log(la) - la))

    def objective(x):
        return -poisson_ll(x) + 1e-3 * np.sum(x ** 2)

    x0 = np.zeros(2 * n - 1)
    x0[-1] = 0.25
    sol = minimize(objective, x0, method="L-BFGS-B", options={"maxiter": 500})
    if not sol.success:
        raise RuntimeError(f"DC fit failed: {sol.message}")
    att, defence, home = unpack(sol.x)
    lh = np.exp(att[hi] - defence[ai] + home)
    la = np.exp(att[ai] - defence[hi])

    def dc_ll(rho):
        total = 0.0
        for xg, yg, l1, l2, w in zip(hg, ag, lh, la, weights):
            tau = 1.0
            if xg == 0 and yg == 0: tau = 1 - l1 * l2 * rho
            elif xg == 0 and yg == 1: tau = 1 + l1 * rho
            elif xg == 1 and yg == 0: tau = 1 + l2 * rho
            elif xg == 1 and yg == 1: tau = 1 - rho
            total += w * (np.log(max(tau, 1e-12)) + xg * np.log(l1) - l1 + yg * np.log(l2) - l2)
        return total

    rho = max(RHO_GRID, key=dc_ll)
    return {"teams": teams, "att": att, "def": defence, "home": float(home),
            "rho": float(rho), "train_ll": float(dc_ll(rho))}


def predict_matrix(model, h_id, a_id, ah=None, dh=None, aa=None, da=None):
    idx = {t: i for i, t in enumerate(model["teams"])}
    ah = float(model["att"][idx[h_id]]) if ah is None and h_id in idx else (0.0 if ah is None else ah)
    dh = float(model["def"][idx[h_id]]) if dh is None and h_id in idx else (0.0 if dh is None else dh)
    aa = float(model["att"][idx[a_id]]) if aa is None and a_id in idx else (0.0 if aa is None else aa)
    da = float(model["def"][idx[a_id]]) if da is None and a_id in idx else (0.0 if da is None else da)
    lh, la = np.exp(ah - da + model["home"]), np.exp(aa - dh)
    ks = np.arange(MAXG + 1)
    matrix = np.outer(poisson.pmf(ks, lh), poisson.pmf(ks, la))
    rho = model["rho"]
    matrix[0, 0] *= 1 - lh * la * rho
    matrix[0, 1] *= 1 + lh * rho
    matrix[1, 0] *= 1 + la * rho
    matrix[1, 1] *= 1 - rho
    matrix = np.clip(matrix, 0, None)
    return matrix / matrix.sum()


def matrix_from_lambdas(lh, la, rho):
    """Return a normalised MAXG score matrix for supplied Dixon-Coles lambdas."""
    ks = np.arange(MAXG + 1)
    matrix = np.outer(poisson.pmf(ks, lh), poisson.pmf(ks, la))
    matrix[0, 0] *= 1 - lh * la * rho
    matrix[0, 1] *= 1 + lh * rho
    matrix[1, 0] *= 1 + la * rho
    matrix[1, 1] *= 1 - rho
    matrix = np.clip(matrix, 0, None)
    return matrix / matrix.sum()


def probs_1x2_ou(matrix):
    home = float(np.tril(matrix, -1).sum())
    draw = float(np.trace(matrix))
    away = float(np.triu(matrix, 1).sum())
    ks = np.arange(MAXG + 1)
    return home, draw, away, float(matrix[(ks[:, None] + ks[None, :]) > 2].sum())


def match_counts(train):
    counts = defaultdict(int)
    for tid in train.home_team_id.astype(int): counts[tid] += 1
    for tid in train.away_team_id.astype(int): counts[tid] += 1
    return dict(counts)


def shrink_factor(counts, tid):
    return min(1.0, counts.get(int(tid), 0) / SHRINK_MIN_MATCHES)


def _prediction_row(model, r, counts, arm):
    kwargs = {}
    if arm == "SHRINK":
        idx = {t: i for i, t in enumerate(model["teams"])}
        h, a = int(r.home_team_id), int(r.away_team_id)
        fh, fa = shrink_factor(counts, h), shrink_factor(counts, a)
        kwargs = {"ah": float(model["att"][idx[h]]) * fh if h in idx else 0.0,
                  "dh": float(model["def"][idx[h]]) * fh if h in idx else 0.0,
                  "aa": float(model["att"][idx[a]]) * fa if a in idx else 0.0,
                  "da": float(model["def"][idx[a]]) * fa if a in idx else 0.0}
    p = probs_1x2_ou(predict_matrix(model, int(r.home_team_id), int(r.away_team_id), **kwargs))
    return {"season": str(r.season), "match_id": int(r.match_id), "date": r.date.strftime("%Y-%m-%d"),
            "home_team": r.home_team, "away_team": r.away_team, "home_goals": int(r.home_goals),
            "away_goals": int(r.away_goals), "p_home": p[0], "p_draw": p[1], "p_away": p[2], "p_over25": p[3]}


def metrics(rows):
    vals = []
    for r in rows:
        outcome = 0 if r["home_goals"] > r["away_goals"] else (1 if r["home_goals"] == r["away_goals"] else 2)
        probs = np.array([r["p_home"], r["p_draw"], r["p_away"]])
        obs = np.eye(3)[outcome]
        over = float(r["home_goals"] + r["away_goals"] > 2)
        vals.append((-np.log(max(probs[outcome], 1e-12)),
                     0.5 * np.sum((np.cumsum(probs)[:2] - np.cumsum(obs)[:2]) ** 2),
                     -(over * np.log(max(r["p_over25"], 1e-12)) + (1 - over) * np.log(max(1 - r["p_over25"], 1e-12)))))
    a = np.asarray(vals)
    return {"n": len(rows), "ll_1x2": float(a[:, 0].mean()), "rps": float(a[:, 1].mean()), "ll_ou25": float(a[:, 2].mean())}


def _baseline_row(r, p):
    return {"season": str(r.season), "match_id": int(r.match_id), "date": r.date.strftime("%Y-%m-%d"),
            "home_team": r.home_team, "away_team": r.away_team, "home_goals": int(r.home_goals),
            "away_goals": int(r.away_goals), "p_home": p[0], "p_draw": p[1], "p_away": p[2], "p_over25": p[3]}


def climatology_rows(train, test):
    out = np.where(train.home_goals > train.away_goals, 0, np.where(train.home_goals == train.away_goals, 1, 2))
    p = [float((out == k).mean()) for k in range(3)]
    p.append(float(((train.home_goals + train.away_goals) > 2).mean()))
    return [_baseline_row(r, p) for _, r in test.iterrows()]


class Trailing10:
    def __init__(self, league_mean):
        self.hist = {}
        self.league_mean = float(league_mean)

    def feed(self, df):
        for _, r in _ordered(df).iterrows():
            self.hist.setdefault(int(r.home_team_id), deque(maxlen=10)).append(float(r.home_goals))
            self.hist.setdefault(int(r.away_team_id), deque(maxlen=10)).append(float(r.away_goals))

    def rows_for(self, df):
        rows = []
        for date, group in _ordered(df).groupby("date", sort=False):
            # All matches on this date see the history strictly before date.
            for _, r in group.iterrows():
                h, a = int(r.home_team_id), int(r.away_team_id)
                lh = float(np.mean(self.hist[h])) if h in self.hist and self.hist[h] else self.league_mean
                la = float(np.mean(self.hist[a])) if a in self.hist and self.hist[a] else self.league_mean
                ks = np.arange(MAXG + 1)
                rows.append(_baseline_row(r, probs_1x2_ou(np.outer(poisson.pmf(ks, lh), poisson.pmf(ks, la)))))
            for _, r in group.iterrows():
                self.hist.setdefault(int(r.home_team_id), deque(maxlen=10)).append(float(r.home_goals))
                self.hist.setdefault(int(r.away_team_id), deque(maxlen=10)).append(float(r.away_goals))
        return rows


def league_mean_goals(train):
    return float((train.home_goals.sum() + train.away_goals.sum()) / (2 * len(train)))


def _diagnostics(rows):
    return {"mean_pred_home_win": float(np.mean([r["p_home"] for r in rows])),
            "actual_home_win_rate": float(np.mean([r["home_goals"] > r["away_goals"] for r in rows])),
            "mean_pred_over25": float(np.mean([r["p_over25"] for r in rows])),
            "actual_over25_rate": float(np.mean([r["home_goals"] + r["away_goals"] > 2 for r in rows]))}


def _gate_legs(arm, pooled, clim, naive):
    return {metric: {"vs_climatology": {"result": "WIN" if pooled[metric] < clim[metric] else "LOSE", "arm": pooled[metric], "baseline": clim[metric]},
                     "vs_naive_trailing_10": {"result": "WIN" if pooled[metric] < naive[metric] else "LOSE", "arm": pooled[metric], "baseline": naive[metric]}}
            for metric in ("ll_1x2", "rps", "ll_ou25")}


def run_goals(out_dir):
    out_dir = Path(out_dir)
    data = load_dev_data()
    arms = ["GateZero", "SHRINK"]
    arm_rows = {a: [] for a in arms}; arm_season = {a: {} for a in arms}; fitted = {}
    clim_rows, clim_season, naive_rows, naive_season = [], {}, [], {}
    warm = data[data.season == WARMUP_SEASON]
    t10 = Trailing10(league_mean_goals(warm)); t10.feed(warm)
    for season in DEV_SEASONS:
        cutoff = data.loc[data.season == season, "date"].min()
        train = data[data.date < cutoff]
        test = data[data.season == season]
        expected_train = {"2022/2023": 156, "2023/2024": 351, "2024/2025": 521}[season]
        expected_test = {"2022/2023": 195, "2023/2024": 170, "2024/2025": 237}[season]
        if len(train) != expected_train or len(test) != expected_test:
            raise RuntimeError(f"DATE CUTOFF TRAINING WINDOW MISMATCH for {season}")
        model = fit_dc(train, cutoff); counts = match_counts(train)
        fitted[season] = {"teams": model["teams"], "attack": model["att"].tolist(), "defence": model["def"].tolist(),
                          "home_intercept": model["home"], "rho": model["rho"], "train_ll": model["train_ll"],
                          "fit_cutoff": cutoff.strftime("%Y-%m-%d"), "n_train": len(train)}
        for arm in arms:
            rows = [_prediction_row(model, r, counts, arm) for _, r in test.iterrows()]
            arm_rows[arm].extend(rows); arm_season[arm][season] = metrics(rows)
        crows = climatology_rows(train, test); clim_rows.extend(crows); clim_season[season] = metrics(crows)
        t10.league_mean = league_mean_goals(train)
        nrows = t10.rows_for(test); naive_rows.extend(nrows); naive_season[season] = metrics(nrows)
    pooled = {a: metrics(arm_rows[a]) for a in arms}; clim_pooled = metrics(clim_rows); naive_pooled = metrics(naive_rows)
    gates = {a: _gate_legs(a, pooled[a], clim_pooled, naive_pooled) for a in arms}
    gate_pass = {a: all(v["result"] == "WIN" for m in gates[a].values() for v in m.values()) for a in arms}
    low_count = {s: sum(1 for n in match_counts(data[data.date < data.loc[data.season == s, "date"].min()]).values() if 1 <= n <= 5) for s in DEV_SEASONS}
    dev_res = {"arms": {a: {"pooled": pooled[a], "per_season": arm_season[a], "gate_dev_pass": gate_pass[a],
                             "gate_legs": gates[a], "diagnostics": _diagnostics(arm_rows[a])} for a in arms},
               "climatology": {"pooled": clim_pooled, "per_season": clim_season},
               "naive_trailing_10": {"pooled": naive_pooled, "per_season": naive_season},
               "shrink_comparison": {"identical": arm_rows["GateZero"] == arm_rows["SHRINK"],
                                     "teams_with_1_to_5_prior_matches": low_count,
                                     "synthetic_check": shrink_factor({123: 3}, 123) == 0.5},
               "meta": {"season_order": [WARMUP_SEASON, *DEV_SEASONS], "warm_up": WARMUP_SEASON,
                        "scored": DEV_SEASONS, "pooled_n": len(arm_rows["GateZero"]),
                        "fit_scope": "all-phase model matches (awarded excluded) dated strictly before target season first match",
                        "awarded_excluded": True, "virgin_and_reserve_excluded": True}}
    predictions = []
    for i in range(len(arm_rows["GateZero"])):
        base = {k: arm_rows["GateZero"][i][k] for k in ("match_id", "season", "date", "home_team", "away_team", "home_goals", "away_goals")}
        for name, rows in [("gate_zero", arm_rows["GateZero"]), ("shrink", arm_rows["SHRINK"]),
                           ("climatology", clim_rows), ("naive", naive_rows)]:
            for key in ("p_home", "p_draw", "p_away", "p_over25"): base[f"{name}_{key}"] = rows[i][key]
        predictions.append(base)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "results_dev.json").write_text(json.dumps(dev_res, indent=1) + "\n")
    (out_dir / "fitted_params_dev.json").write_text(json.dumps(fitted, indent=1) + "\n")
    pd.DataFrame(predictions).to_csv(out_dir / "results_dev.csv", index=False)
    return {"dev": dev_res, "virgin": None}
