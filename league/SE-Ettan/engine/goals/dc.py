"""Dixon-Coles goals engine for G-SE (see PREREG_G_SE.md).
Ratings by direct Poisson log-likelihood maximisation (scipy L-BFGS,
sum-to-zero), rho from grid by training LL, MAXG=10, standard DC tau.
Arms: Gate Zero; SHRINK (PREREG_G_FI definition, verbatim: at prediction
time a team with n < 6 prior in-league matches in the training data
has a *= n/6, d *= n/6; n >= 6 no change; n = 0 -> exponents 0.0).
NO ENTRANT arm (X2 rejected, EDA F4).
Baselines: climatology (prior-seasons pooled rates) and naive
trailing-10 (per-team trailing-10 goals-for means, independent
Poissons, no home advantage).
DEV ONLY: this module never reads season_start > 2024. The dev loader
raises if any row with season_start > 2024 survives the filter, or if
the frozen dev row counts (2021: 262; 2022/2023/2024: 480 each) do not
match. There is no virgin code path in this engine (Phase 5 owns it).
"""
import json
from collections import deque
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy.stats import poisson

MAXG = 10
RHO_GRID = (0.0, -0.05, -0.10, -0.15)
DEV_SEASONS = [2022, 2023, 2024]
WARMUP_SEASON = 2021
# Frozen dev row counts (PREREG_G_SE / eda_summary.json): warm-up 2021
# partial 262 played matches; scored seasons 2022-2024, 480 each.
EXPECTED_COUNTS = {2021: 262, 2022: 480, 2023: 480, 2024: 480}
SHRINK_MIN_MATCHES = 6


def load_dev_data():
    """Load se_matches.csv and keep ONLY season_start <= 2024.

    Hard guard: fail loudly if any 2025/2026 row survives the filter,
    or if the frozen per-season played counts do not match. The raw
    file contains 2025 (virgin) and 2026 (reserve) rows; they are
    dropped here before any fitting, metric, or count is computed.
    Only the season_start column of those rows is ever inspected, by
    the filter itself.
    """
    path = Path(__file__).parent.parent.parent / "data" / "se_matches.csv"
    data = pd.read_csv(path, parse_dates=["date", "kickoff_utc"])
    data = data.sort_values(["kickoff_utc", "match_id"]).reset_index(drop=True)
    dev = data[data.season_start <= 2024].copy()
    if len(dev) == 0 or int(dev.season_start.max()) > 2024:
        raise RuntimeError("DEV FILTER BREACH: rows with season_start > 2024 "
                           "survived the dev filter")
    counts = dev.groupby("season_start").size().to_dict()
    if counts != EXPECTED_COUNTS:
        raise RuntimeError(f"DEV ROW COUNT MISMATCH: got {counts}, "
                           f"expected frozen {EXPECTED_COUNTS}")
    if "finished" in dev.columns and not bool(dev["finished"].all()):
        raise RuntimeError("DEV DATA: unfinished fixture present in dev rows")
    if dev[["home_goals", "away_goals"]].isna().any().any():
        raise RuntimeError("DEV DATA: missing goals in dev rows")
    return dev


def fit_dc(df):
    teams = sorted(set(df.home_team_id) | set(df.away_team_id))
    idx = {t: i for i, t in enumerate(teams)}
    n = len(teams)
    hi = df.home_team_id.map(idx).to_numpy()
    ai = df.away_team_id.map(idx).to_numpy()
    hg = df.home_goals.to_numpy(dtype=float)
    ag = df.away_goals.to_numpy(dtype=float)

    def unpack(x):
        att = np.concatenate([x[:n - 1], [-x[:n - 1].sum()]])
        dfc = np.concatenate([x[n - 1:2 * n - 2], [-x[n - 1:2 * n - 2].sum()]])
        return att, dfc, x[-1]

    def nll(x):
        att, dfc, home = unpack(x)
        lh = np.exp(att[hi] - dfc[ai] + home)
        la = np.exp(att[ai] - dfc[hi])
        ll = np.sum(hg * np.log(lh) - lh + ag * np.log(la) - la)
        return -ll + 1e-3 * np.sum(x ** 2)

    x0 = np.zeros(2 * n - 1)
    x0[-1] = 0.25
    sol = minimize(nll, x0, method="L-BFGS-B", options={"maxiter": 500})
    att, dfc, home = unpack(sol.x)

    def tau_ll(rho):
        lh = np.exp(att[hi] - dfc[ai] + home)
        la = np.exp(att[ai] - dfc[hi])
        ll = 0.0
        for xg, yg, l1, l2 in zip(hg, ag, lh, la):
            t = 1.0
            if xg == 0 and yg == 0:
                t = 1 - l1 * l2 * rho
            elif xg == 0 and yg == 1:
                t = 1 + l1 * rho
            elif xg == 1 and yg == 0:
                t = 1 + l2 * rho
            elif xg == 1 and yg == 1:
                t = 1 - rho
            ll += np.log(max(t, 1e-9)) + xg * np.log(l1) - l1 + yg * np.log(l2) - l2
        return ll

    rho = max(RHO_GRID, key=tau_ll)
    return {"teams": teams, "att": att, "def": dfc, "home": float(home),
            "rho": float(rho), "train_ll": float(tau_ll(rho))}


def predict_matrix(model, h_id, a_id, ah=None, dh=None, aa=None, da=None):
    """Score matrix. ah/dh/aa/da are (optionally shifted) attack/defence
    exponents; default = fitted rating, or 0.0 league mean if unseen."""
    idx = {t: i for i, t in enumerate(model["teams"])}
    att, dfc, home, rho = model["att"], model["def"], model["home"], model["rho"]
    if ah is None:
        ah = float(att[idx[h_id]]) if h_id in idx else 0.0
    if dh is None:
        dh = float(dfc[idx[h_id]]) if h_id in idx else 0.0
    if aa is None:
        aa = float(att[idx[a_id]]) if a_id in idx else 0.0
    if da is None:
        da = float(dfc[idx[a_id]]) if a_id in idx else 0.0
    lh = np.exp(ah - da + home)
    la = np.exp(aa - dh)
    ks = np.arange(MAXG + 1)
    M = np.outer(poisson.pmf(ks, lh), poisson.pmf(ks, la))
    M[0, 0] *= 1 - lh * la * rho
    M[0, 1] *= 1 + lh * rho
    M[1, 0] *= 1 + la * rho
    M[1, 1] *= 1 - rho
    M = np.clip(M, 0, None)
    return M / M.sum()


def probs_1x2_ou(M):
    pH = float(np.tril(M, -1).sum())
    pD = float(np.trace(M))
    pA = float(np.triu(M, 1).sum())
    ks = np.arange(MAXG + 1)
    tot = ks[:, None] + ks[None, :]
    p_over = float(M[tot > 2.5].sum())
    return pH, pD, pA, p_over


def metrics(rows):
    """rows: list of dicts with pH,pD,pA,p_over,hg,ag."""
    ll = rps = oull = 0.0
    for r in rows:
        y = 0 if r["hg"] > r["ag"] else (1 if r["hg"] == r["ag"] else 2)
        p = np.array([r["pH"], r["pD"], r["pA"]])
        ll += -np.log(max(p[y], 1e-12))
        obs = np.zeros(3); obs[y] = 1
        rps += 0.5 * np.sum((np.cumsum(p)[:2] - np.cumsum(obs)[:2]) ** 2)
        o = 1.0 if r["hg"] + r["ag"] > 2.5 else 0.0
        oull += -(o * np.log(max(r["p_over"], 1e-9)) + (1 - o) * np.log(max(1 - r["p_over"], 1e-9)))
    n = len(rows)
    return {"n": n, "ll_1x2": ll / n, "rps": rps / n, "ll_ou25": oull / n}


def match_counts(train):
    """Matches played per team in the training data (all seasons in the
    expanding fit). Used by SHRINK: n = prior in-league matches."""
    counts = {}
    for tid in train.home_team_id:
        counts[tid] = counts.get(tid, 0) + 1
    for tid in train.away_team_id:
        counts[tid] = counts.get(tid, 0) + 1
    return counts


def shrink_factor(counts, tid):
    """min(1, n/6); n = 0 -> 0.0 (league-mean exponents)."""
    return min(1.0, counts.get(tid, 0) / SHRINK_MIN_MATCHES)


def season_rows(model, df_season, counts, arm):
    """counts: match_counts() of the training data for this scored season.
    SHRINK scales each team's attack AND defence exponent by
    min(1, n/6) at prediction time, home and away alike."""
    idx = {t: i for i, t in enumerate(model["teams"])}
    rows = []
    for _, r in df_season.iterrows():
        kw = {}
        if arm == "SHRINK":
            fh = shrink_factor(counts, r.home_team_id)
            fa = shrink_factor(counts, r.away_team_id)
            ah = float(model["att"][idx[r.home_team_id]]) if r.home_team_id in idx else 0.0
            dh = float(model["def"][idx[r.home_team_id]]) if r.home_team_id in idx else 0.0
            aa = float(model["att"][idx[r.away_team_id]]) if r.away_team_id in idx else 0.0
            da = float(model["def"][idx[r.away_team_id]]) if r.away_team_id in idx else 0.0
            kw = {"ah": ah * fh, "dh": dh * fh, "aa": aa * fa, "da": da * fa}
        M = predict_matrix(model, r.home_team_id, r.away_team_id, **kw)
        pH, pD, pA, po = probs_1x2_ou(M)
        rows.append({"match_id": int(r.match_id), "pH": pH, "pD": pD, "pA": pA,
                     "p_over": po, "hg": int(r.home_goals), "ag": int(r.away_goals)})
    return rows


def climatology_rows(train, df_season):
    y = np.where(train.home_goals > train.away_goals, 0,
                 np.where(train.home_goals == train.away_goals, 1, 2))
    rates = np.array([(y == k).mean() for k in range(3)])
    po = float(((train.home_goals + train.away_goals) > 2.5).mean())
    return [{"match_id": int(r.match_id), "pH": rates[0], "pD": rates[1],
             "pA": rates[2], "p_over": po, "hg": int(r.home_goals),
             "ag": int(r.away_goals)} for _, r in df_season.iterrows()]


class Trailing10:
    """Per-team trailing-10 goals-for means (matches strictly before
    the scored match, chronological by kickoff_utc)."""

    def __init__(self, league_mean):
        self.hist = {}
        self.league_mean = league_mean

    def feed(self, df):
        for _, r in df.iterrows():
            self.hist.setdefault(r.home_team_id, deque(maxlen=10)).append(float(r.home_goals))
            self.hist.setdefault(r.away_team_id, deque(maxlen=10)).append(float(r.away_goals))

    def rows_for(self, df_season):
        rows = []
        for _, r in df_season.iterrows():
            mh = self.hist.get(r.home_team_id, [])
            ma = self.hist.get(r.away_team_id, [])
            lh = float(np.mean(mh)) if len(mh) else self.league_mean
            la = float(np.mean(ma)) if len(ma) else self.league_mean
            ks = np.arange(MAXG + 1)
            M = np.outer(poisson.pmf(ks, lh), poisson.pmf(ks, la))
            pH, pD, pA, po = probs_1x2_ou(M)
            rows.append({"match_id": int(r.match_id), "pH": pH, "pD": pD, "pA": pA,
                         "p_over": po, "hg": int(r.home_goals), "ag": int(r.away_goals)})
            # feed this match so later same-season matches see it
            self.hist.setdefault(r.home_team_id, deque(maxlen=10)).append(float(r.home_goals))
            self.hist.setdefault(r.away_team_id, deque(maxlen=10)).append(float(r.away_goals))
        return rows


def league_mean_goals(train):
    """Pooled training league mean team goals/match (naive fallback)."""
    return float((train.home_goals.sum() + train.away_goals.sum()) / (2 * len(train)))


def run_goals(out_dir):
    """DEV ONLY. Season-blocked expanding fit: warm-up 2021, scored
    2022-2024 (pooled n = 1440). Returns {"dev": dev_res, "virgin": None}
    (no virgin code path exists in this engine)."""
    out_dir = Path(out_dir)
    dev_all = load_dev_data()
    arms = ["GateZero", "SHRINK"]
    dev = {a: {"per_season": {}, "rows": []} for a in arms}
    clim = {"per_season": {}, "rows": []}
    naive = {"per_season": {}, "rows": []}
    fitted = {}
    # warm-up 2021 feeds the trailing-10 history before scored seasons
    t10 = Trailing10(league_mean=league_mean_goals(dev_all[dev_all.season_start == WARMUP_SEASON]))
    t10.feed(dev_all[dev_all.season_start == WARMUP_SEASON])
    for s in DEV_SEASONS:
        train = dev_all[dev_all.season_start < s]
        test = dev_all[dev_all.season_start == s]
        counts = match_counts(train)
        model = fit_dc(train)
        fitted[str(s)] = {"teams": [int(t) for t in model["teams"]],
                          "att": model["att"].tolist(),
                          "def": model["def"].tolist(),
                          "home": model["home"], "rho": model["rho"],
                          "train_ll": model["train_ll"],
                          "fit_on": f"all matches with season_start < {s}",
                          "n_train": int(len(train)),
                          "n_teams": int(len(model["teams"]))}
        for a in arms:
            rows = season_rows(model, test, counts, a)
            dev[a]["per_season"][s] = metrics(rows)
            dev[a]["rows"] += rows
        crows = climatology_rows(train, test)
        clim["per_season"][s] = metrics(crows)
        clim["rows"] += crows
        # naive fallback mean = this season's training league mean
        t10.league_mean = league_mean_goals(train)
        nrows = t10.rows_for(test)
        naive["per_season"][s] = metrics(nrows)
        naive["rows"] += nrows
    pooled = {a: metrics(dev[a]["rows"]) for a in arms}
    pooled_clim = metrics(clim["rows"])
    pooled_naive = metrics(naive["rows"])
    gate = {}
    for a in arms:
        gate[a] = bool(pooled[a]["ll_1x2"] < pooled_clim["ll_1x2"]
                       and pooled[a]["ll_1x2"] < pooled_naive["ll_1x2"]
                       and pooled[a]["rps"] < pooled_clim["rps"]
                       and pooled[a]["rps"] < pooled_naive["rps"]
                       and pooled[a]["ll_ou25"] < pooled_clim["ll_ou25"]
                       and pooled[a]["ll_ou25"] < pooled_naive["ll_ou25"])
    dev_res = {"arms": {a: {"pooled": pooled[a], "per_season": dev[a]["per_season"],
                            "gate_dev_pass": gate[a]} for a in arms},
               "climatology": {"pooled": pooled_clim, "per_season": clim["per_season"]},
               "naive_trailing_10": {"pooled": pooled_naive, "per_season": naive["per_season"]},
               "meta": {"warm_up": WARMUP_SEASON, "scored": DEV_SEASONS,
                        "pooled_n": 1440,
                        "prereg_commit": "2fc8d51c13736643f6156b1c71abb11e21b7de08",
                        "filter": "season_start <= 2024 only; 2025/2026 rows dropped "
                                  "before any fit/metric; hard assert on filter "
                                  "and frozen per-season counts"}}
    (out_dir / "results_dev.json").write_text(json.dumps(dev_res, indent=1))
    (out_dir / "fitted_params_dev.json").write_text(json.dumps(fitted, indent=1))
    all_dev_rows = []
    for a in arms:
        for r in dev[a]["rows"]:
            all_dev_rows.append({"arm": a, "season": None, **r})
    # attach scored season per match_id (dev only)
    season_of = dict(zip(dev_all.match_id, dev_all.season_start))
    for r in all_dev_rows:
        r["season"] = int(season_of[r["match_id"]])
    pd.DataFrame(all_dev_rows).to_csv(out_dir / "results_dev.csv", index=False)
    return {"dev": dev_res, "virgin": None}
