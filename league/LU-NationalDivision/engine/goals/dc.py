"""Dev-only G-LU Dixon-Coles goals engine."""
import json
from collections import deque
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy.stats import poisson

MAXG = 10
RHO_GRID = (0.0, -0.05, -0.10, -0.15)
SEASONS = ["2021/2022", "2022/2023", "2023/2024", "2024/2025", "2025/2026", "2026/2027"]
WARMUP_SEASON = "2021/2022"
DEV_SEASONS = ["2022/2023", "2023/2024", "2024/2025"]
EXPECTED_COUNTS = {s: 240 for s in SEASONS[:5]} | {"2026/2027": 96}
DEV_COUNTS = {s: 240 for s in SEASONS[:4]}
SHRINK_MIN_MATCHES = 6
HALF_LIFE_DAYS = 270


def _ordered(df):
    return df.sort_values(["date", "match_id"], kind="mergesort").reset_index(drop=True)


def load_dev_data(path=None):
    """Load only the warm-up and scored dev seasons, with hard guards."""
    if path is None:
        path = Path(__file__).parent.parent.parent / "data" / "lu_matches.csv"
    data = pd.read_csv(path, parse_dates=["date"])
    data["season"] = data["season"].astype(str)
    if not set(data.season).issubset(set(SEASONS)):
        raise RuntimeError("UNKNOWN SEASON LABEL IN DATA")
    dev = data[data.season.isin(DEV_COUNTS)].copy()
    if dev.empty or set(dev.season) != set(DEV_COUNTS):
        raise RuntimeError("DEV FILTER BREACH: missing required dev season")
    if bool(dev.season.isin(("2025/2026", "2026/2027")).any()):
        raise RuntimeError("DEV FILTER BREACH: virgin/reserve row survived")
    counts = dev.groupby("season").size().to_dict()
    if counts != DEV_COUNTS:
        raise RuntimeError(f"DEV ROW COUNT MISMATCH: got {counts}, expected {DEV_COUNTS}")
    if dev[["home_goals", "away_goals", "home_id", "away_id"]].isna().any().any():
        raise RuntimeError("DEV DATA: missing required value")
    return _ordered(dev)


def _model_arrays(df):
    teams = sorted(set(df.home_id.astype(int)) | set(df.away_id.astype(int)))
    idx = {t: i for i, t in enumerate(teams)}
    hi = df.home_id.astype(int).map(idx).to_numpy()
    ai = df.away_id.astype(int).map(idx).to_numpy()
    hg = df.home_goals.to_numpy(dtype=float)
    ag = df.away_goals.to_numpy(dtype=float)
    return teams, hi, ai, hg, ag


def fit_dc(df, cutoff):
    teams, hi, ai, hg, ag = _model_arrays(df)
    n = len(teams)
    age = (pd.Timestamp(cutoff) - df.date).dt.days.to_numpy(dtype=float)
    weights = 0.5 ** (age / HALF_LIFE_DAYS)

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

    def tau_ll(rho):
        lh = np.exp(att[hi] - defence[ai] + home)
        la = np.exp(att[ai] - defence[hi])
        total = 0.0
        for xg, yg, l1, l2, w in zip(hg, ag, lh, la, weights):
            tau = 1.0
            if xg == 0 and yg == 0: tau = 1 - l1 * l2 * rho
            elif xg == 0 and yg == 1: tau = 1 + l1 * rho
            elif xg == 1 and yg == 0: tau = 1 + l2 * rho
            elif xg == 1 and yg == 1: tau = 1 - rho
            total += w * (np.log(max(tau, 1e-12)) + xg * np.log(l1) - l1 + yg * np.log(l2) - l2)
        return total

    rho = max(RHO_GRID, key=tau_ll)
    return {"teams": teams, "att": att, "def": defence, "home": float(home),
            "rho": float(rho), "train_ll": float(tau_ll(rho))}


def predict_matrix(model, h_id, a_id, ah=None, dh=None, aa=None, da=None):
    idx = {t: i for i, t in enumerate(model["teams"])}
    if ah is None: ah = float(model["att"][idx[h_id]]) if h_id in idx else 0.0
    if dh is None: dh = float(model["def"][idx[h_id]]) if h_id in idx else 0.0
    if aa is None: aa = float(model["att"][idx[a_id]]) if a_id in idx else 0.0
    if da is None: da = float(model["def"][idx[a_id]]) if a_id in idx else 0.0
    lh, la = np.exp(ah - da + model["home"]), np.exp(aa - dh)
    ks = np.arange(MAXG + 1)
    matrix = np.outer(poisson.pmf(ks, lh), poisson.pmf(ks, la))
    rho = model["rho"]
    matrix[0, 0] *= 1 - lh * la * rho
    matrix[0, 1] *= 1 + lh * rho
    matrix[1, 0] *= 1 + la * rho
    matrix[1, 1] *= 1 - rho
    return np.clip(matrix, 0, None) / np.clip(matrix, 0, None).sum()


def probs_1x2_ou(matrix):
    p_home = float(np.tril(matrix, -1).sum())
    p_draw = float(np.trace(matrix))
    p_away = float(np.triu(matrix, 1).sum())
    ks = np.arange(MAXG + 1)
    total = ks[:, None] + ks[None, :]
    return p_home, p_draw, p_away, float(matrix[total > 2.5].sum())


def match_counts(train):
    counts = {}
    for tid in train.home_id.astype(int): counts[tid] = counts.get(tid, 0) + 1
    for tid in train.away_id.astype(int): counts[tid] = counts.get(tid, 0) + 1
    return counts


def shrink_factor(counts, tid):
    return min(1.0, counts.get(int(tid), 0) / SHRINK_MIN_MATCHES)


def _prediction_row(model, r, counts, arm):
    kwargs = {}
    if arm == "SHRINK":
        idx = {t: i for i, t in enumerate(model["teams"])}
        h, a = int(r.home_id), int(r.away_id)
        fh, fa = shrink_factor(counts, h), shrink_factor(counts, a)
        kwargs = {"ah": float(model["att"][idx[h]]) * fh if h in idx else 0.0,
                  "dh": float(model["def"][idx[h]]) * fh if h in idx else 0.0,
                  "aa": float(model["att"][idx[a]]) * fa if a in idx else 0.0,
                  "da": float(model["def"][idx[a]]) * fa if a in idx else 0.0}
    p = probs_1x2_ou(predict_matrix(model, int(r.home_id), int(r.away_id), **kwargs))
    return {"season": str(r.season), "match_id": int(r.match_id), "date": r.date.strftime("%Y-%m-%d"),
            "home_id": int(r.home_id), "away_id": int(r.away_id), "home_goals": int(r.home_goals),
            "away_goals": int(r.away_goals), "p_home": p[0], "p_draw": p[1], "p_away": p[2], "p_over25": p[3]}


def metrics(rows):
    losses = []
    for r in rows:
        outcome = 0 if r["home_goals"] > r["away_goals"] else (1 if r["home_goals"] == r["away_goals"] else 2)
        probs = np.array([r["p_home"], r["p_draw"], r["p_away"]])
        obs = np.eye(3)[outcome]
        over = float(r["home_goals"] + r["away_goals"] > 2.5)
        losses.append((-np.log(max(probs[outcome], 1e-12)),
                       0.5 * np.sum((np.cumsum(probs)[:2] - np.cumsum(obs)[:2]) ** 2),
                       -(over * np.log(max(r["p_over25"], 1e-12)) + (1 - over) * np.log(max(1 - r["p_over25"], 1e-12)))))
    a = np.asarray(losses)
    return {"n": len(rows), "ll_1x2": float(a[:, 0].mean()), "rps": float(a[:, 1].mean()), "ll_ou25": float(a[:, 2].mean())}


def _baseline_row(r, p):
    return {"season": str(r.season), "match_id": int(r.match_id), "date": r.date.strftime("%Y-%m-%d"),
            "home_id": int(r.home_id), "away_id": int(r.away_id), "home_goals": int(r.home_goals),
            "away_goals": int(r.away_goals), "p_home": p[0], "p_draw": p[1], "p_away": p[2], "p_over25": p[3]}


def climatology_rows(train, test):
    outcomes = np.where(train.home_goals > train.away_goals, 0, np.where(train.home_goals == train.away_goals, 1, 2))
    p = (np.array([(outcomes == k).mean() for k in range(3)]).tolist() + [float(((train.home_goals + train.away_goals) > 2.5).mean())])
    return [_baseline_row(r, p) for _, r in test.iterrows()]


class Trailing10:
    def __init__(self, league_mean): self.hist, self.league_mean = {}, float(league_mean)

    def feed(self, df):
        for _, r in _ordered(df).iterrows():
            self.hist.setdefault(int(r.home_id), deque(maxlen=10)).append(float(r.home_goals))
            self.hist.setdefault(int(r.away_id), deque(maxlen=10)).append(float(r.away_goals))

    def rows_for(self, df):
        rows = []
        for _, r in _ordered(df).iterrows():
            h, a = int(r.home_id), int(r.away_id)
            lh = float(np.mean(self.hist[h])) if h in self.hist else self.league_mean
            la = float(np.mean(self.hist[a])) if a in self.hist else self.league_mean
            ks = np.arange(MAXG + 1)
            p = probs_1x2_ou(np.outer(poisson.pmf(ks, lh), poisson.pmf(ks, la)))
            rows.append(_baseline_row(r, p))
            self.hist.setdefault(h, deque(maxlen=10)).append(float(r.home_goals))
            self.hist.setdefault(a, deque(maxlen=10)).append(float(r.away_goals))
        return rows


def league_mean_goals(train):
    return float((train.home_goals.sum() + train.away_goals.sum()) / (2 * len(train)))


def _diagnostics(rows):
    return {"mean_pred_home_win": float(np.mean([r["p_home"] for r in rows])),
            "actual_home_win_rate": float(np.mean([r["home_goals"] > r["away_goals"] for r in rows])),
            "mean_pred_over25": float(np.mean([r["p_over25"] for r in rows])),
            "actual_over25_rate": float(np.mean([r["home_goals"] + r["away_goals"] > 2.5 for r in rows]))}


def run_goals(out_dir):
    out_dir = Path(out_dir)
    data = load_dev_data()
    arms = ["GateZero", "SHRINK"]
    arm_rows = {a: [] for a in arms}; arm_season = {a: {} for a in arms}
    clim_rows, clim_season, naive_rows, naive_season, fitted = [], {}, [], {}, {}
    warm = data[data.season == WARMUP_SEASON]
    t10 = Trailing10(league_mean_goals(warm)); t10.feed(warm)
    for season in DEV_SEASONS:
        cutoff = data.loc[data.season == season, "date"].min()
        train = data[data.date < cutoff]
        test = data[data.season == season]
        if len(train) != sum(DEV_COUNTS[s] for s in SEASONS[:SEASONS.index(season)]):
            raise RuntimeError("DATE CUTOFF TRAINING WINDOW MISMATCH")
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
    pooled = {a: metrics(arm_rows[a]) for a in arms}
    clim_pooled, naive_pooled = metrics(clim_rows), metrics(naive_rows)
    gate = {a: all(pooled[a][k] < clim_pooled[k] and pooled[a][k] < naive_pooled[k]
                   for k in ("ll_1x2", "rps", "ll_ou25")) for a in arms}
    dev_res = {"arms": {a: {"pooled": pooled[a], "per_season": arm_season[a], "gate_dev_pass": gate[a],
                             "gate_zero_diagnostics": {s: _diagnostics([r for r in arm_rows[a] if r["season"] == s]) for s in DEV_SEASONS}}
                        for a in arms},
               "climatology": {"pooled": clim_pooled, "per_season": clim_season},
               "naive_trailing_10": {"pooled": naive_pooled, "per_season": naive_season},
               "meta": {"season_order": SEASONS, "warm_up": WARMUP_SEASON, "scored": DEV_SEASONS,
                        "pooled_n": len(arm_rows["GateZero"]), "fit_scope": "date strictly before target season first match"}}
    predictions = []
    for i in range(len(arm_rows["GateZero"])):
        row = {k: arm_rows["GateZero"][i][k] for k in ("season", "match_id", "date", "home_id", "away_id", "home_goals", "away_goals")}
        for arm in arms:
            for key in ("p_home", "p_draw", "p_away", "p_over25"): row[f"{arm}_{key}"] = arm_rows[arm][i][key]
        for name, rows in (("climatology", clim_rows), ("naive_trailing_10", naive_rows)):
            for key in ("p_home", "p_draw", "p_away", "p_over25"): row[f"{name}_{key}"] = rows[i][key]
        predictions.append(row)
    # Per-match predictions live in results_dev.csv only. The JSON stays
    # summary-only (programme precedent: SE-Ettan) — the embedded copy
    # was removed after the dev-freeze review.
    (out_dir / "results_dev.json").write_text(json.dumps(dev_res, indent=1))
    (out_dir / "fitted_params_dev.json").write_text(json.dumps(fitted, indent=1))
    pd.DataFrame(predictions).to_csv(out_dir / "results_dev.csv", index=False)
    return {"dev": dev_res, "virgin": None}
