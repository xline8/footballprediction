"""Dixon-Coles goals engine for G-CH (see PREREG_G_CH).
Ratings by direct Poisson log-likelihood maximisation (scipy L-BFGS,
sum-to-zero), rho from grid by training LL, MAXG=10, standard DC tau.
Arms: Gate Zero; SHRINK (n<6 prior in-league matches -> attack/defence
exponents scaled by n/6 at prediction time).
Dev harness drops 2025/2026+ rows before computing anything; the virgin
function is called once, only if Gate Zero passes the dev gate.
"""
import json
import os
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy.stats import poisson

MAXG = 10
RHO_GRID = (0.0, -0.05, -0.10, -0.15)


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


def predict_matrix(model, h_id, a_id, shrink_h=1.0, shrink_a=1.0):
    idx = {t: i for i, t in enumerate(model["teams"])}
    att, dfc, home, rho = model["att"], model["def"], model["home"], model["rho"]
    ah = att[idx[h_id]] * shrink_h if h_id in idx else 0.0
    dh = dfc[idx[h_id]] * shrink_h if h_id in idx else 0.0
    aa = att[idx[a_id]] * shrink_a if a_id in idx else 0.0
    da = dfc[idx[a_id]] * shrink_a if a_id in idx else 0.0
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


def season_rows(model, df_season, prior_counts, arm):
    rows = []
    for _, r in df_season.iterrows():
        sh = sa = 1.0
        if arm == "SHRINK":
            nh = prior_counts.get(r.home_team_id, 0)
            na = prior_counts.get(r.away_team_id, 0)
            sh = min(nh, 6) / 6 if nh < 6 else 1.0
            sa = min(na, 6) / 6 if na < 6 else 1.0
        M = predict_matrix(model, r.home_team_id, r.away_team_id, sh, sa)
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


def run_goals(out_dir):
    out_dir = Path(out_dir)
    data = pd.read_csv(Path(__file__).parent.parent.parent / "data" / "ch_matches.csv",
                       parse_dates=["date"]).sort_values(["date", "match_id"])
    dev_all = data[data.season_start <= 2024].copy()
    seasons_dev = ["2022/2023", "2023/2024", "2024/2025"]
    arms = ["GateZero", "SHRINK"]
    dev = {a: {"per_season": {}, "rows": []} for a in arms}
    clim = {"per_season": {}, "rows": []}
    for s in seasons_dev:
        train = dev_all[dev_all.season_start < int(s[:4])]
        test = dev_all[dev_all.season == s]
        counts = train.groupby("home_team_id").size().add(
            train.groupby("away_team_id").size(), fill_value=0).to_dict()
        model = fit_dc(train)
        for a in arms:
            rows = season_rows(model, test, counts, "SHRINK" if a == "SHRINK" else "GZ")
            dev[a]["per_season"][s] = metrics(rows)
            dev[a]["rows"] += rows
        crows = climatology_rows(train, test)
        clim["per_season"][s] = metrics(crows)
        clim["rows"] += crows
    pooled = {a: metrics(dev[a]["rows"]) for a in arms}
    pooled_clim = metrics(clim["rows"])
    gate = {}
    for a in arms:
        gate[a] = bool(pooled[a]["ll_1x2"] < pooled_clim["ll_1x2"]
                       and pooled[a]["rps"] < pooled_clim["rps"]
                       and pooled[a]["ll_ou25"] < pooled_clim["ll_ou25"])
    dev_res = {"arms": {a: {"pooled": pooled[a], "per_season": dev[a]["per_season"],
                            "gate_dev_pass": gate[a]} for a in arms},
               "climatology": {"pooled": pooled_clim, "per_season": clim["per_season"]}}
    (out_dir / "results_dev.json").write_text(json.dumps(dev_res, indent=1))
    pd.DataFrame(dev["GateZero"]["rows"]).to_csv(out_dir / "results_dev.csv", index=False)
    result = {"dev": dev_res, "virgin": None}
    if not gate["GateZero"] or os.environ.get("CH_DEV_ONLY") == "1":
        return result
    # ---- VIRGIN: read once, only because Gate Zero passed dev ----
    train = data[data.season_start <= 2024]
    test = data[data.season == "2025/2026"]
    counts = train.groupby("home_team_id").size().add(
        train.groupby("away_team_id").size(), fill_value=0).to_dict()
    model = fit_dc(train)
    v = {}
    passing = []
    for a in arms:
        if not gate[a]:
            continue
        rows = season_rows(model, test, counts, "SHRINK" if a == "SHRINK" else "GZ")
        m = metrics(rows)
        ph = np.array([r["pH"] for r in rows]); hw = np.array([r["hg"] > r["ag"] for r in rows], dtype=float)
        po = np.array([r["p_over"] for r in rows]); ov = np.array([r["hg"] + r["ag"] > 2.5 for r in rows], dtype=float)
        cal = {}
        for name, pp, yy in (("home_win", ph, hw), ("ou25", po, ov)):
            gap = float(np.mean(pp) - np.mean(yy)) * 100
            se = float(np.std(pp - yy, ddof=1) / np.sqrt(len(rows))) * 100
            cal[name] = {"gap_pp": gap, "se_pp": se,
                         "leg": "PASS clean" if abs(gap) <= 1.0 else
                                ("PASS provisional" if abs(gap) <= 1.0 + se else "FAIL")}
        v[a] = {"metrics": m, "calibration": cal,
                "rows_file_rows": len(rows)}
        pd.DataFrame(rows).to_csv(out_dir / f"virgin_rows_{a}.csv", index=False)
        if a != "GateZero":
            better_seasons = sum(1 for s in seasons_dev
                                 if dev[a]["per_season"][s]["ll_1x2"] <= dev["GateZero"]["per_season"][s]["ll_1x2"])
            v[a]["sign_check_seasons"] = better_seasons
        passing.append(a)
    crows = climatology_rows(train, test)
    v_clim = metrics(crows)
    v["climatology"] = v_clim
    (out_dir / "results_virgin.json").write_text(json.dumps(v, indent=1))
    (out_dir / "fitted_params_virgin.json").write_text(json.dumps(
        {"teams": [int(t) for t in model["teams"]],
         "att": model["att"].tolist(), "def": model["def"].tolist(),
         "home": model["home"], "rho": model["rho"],
         "fit_on": "all matches <= 2024/2025"}, indent=1))
    result["virgin"] = v
    return result
