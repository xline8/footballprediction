"""G-QASD Dixon-Coles engine and frozen dev/virgin harness."""
import json
import os
from collections import deque
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy.stats import poisson

MAXG = 10
RHO_GRID = (0.0, -0.05, -0.10, -0.15)
ATT_SHIFT = -0.2391
DEF_SHIFT = 0.1947
DEV_SEASON = "2024/2025"
VIRGIN_SEASON = "2025/2026"


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
    if not sol.success:
        raise RuntimeError(f"Dixon-Coles fit failed: {sol.message}")
    att, dfc, home = unpack(sol.x)

    def tau_ll(rho):
        lh = np.exp(att[hi] - dfc[ai] + home)
        la = np.exp(att[ai] - dfc[hi])
        ll = 0.0
        for xg, yg, l1, l2 in zip(hg, ag, lh, la):
            tau = 1.0
            if xg == 0 and yg == 0:
                tau = 1 - l1 * l2 * rho
            elif xg == 0 and yg == 1:
                tau = 1 + l1 * rho
            elif xg == 1 and yg == 0:
                tau = 1 + l2 * rho
            elif xg == 1 and yg == 1:
                tau = 1 - rho
            ll += np.log(max(tau, 1e-9)) + xg * np.log(l1) - l1 + yg * np.log(l2) - l2
        return ll

    rho = max(RHO_GRID, key=tau_ll)
    return {"teams": teams, "att": att, "def": dfc, "home": float(home),
            "rho": float(rho), "train_ll": float(tau_ll(rho))}


def predict_matrix(model, h_id, a_id, ah=None, dh=None, aa=None, da=None):
    idx = {t: i for i, t in enumerate(model["teams"])}
    att, dfc, home, rho = model["att"], model["def"], model["home"], model["rho"]
    ah = float(att[idx[h_id]]) if ah is None and h_id in idx else (0.0 if ah is None else ah)
    dh = float(dfc[idx[h_id]]) if dh is None and h_id in idx else (0.0 if dh is None else dh)
    aa = float(att[idx[a_id]]) if aa is None and a_id in idx else (0.0 if aa is None else aa)
    da = float(dfc[idx[a_id]]) if da is None and a_id in idx else (0.0 if da is None else da)
    lh, la = np.exp(ah - da + home), np.exp(aa - dh)
    ks = np.arange(MAXG + 1)
    m = np.outer(poisson.pmf(ks, lh), poisson.pmf(ks, la))
    m[0, 0] *= 1 - lh * la * rho
    m[0, 1] *= 1 + lh * rho
    m[1, 0] *= 1 + la * rho
    m[1, 1] *= 1 - rho
    m = np.clip(m, 0, None)
    return m / m.sum()


def probs_1x2_ou(m):
    p_h = float(np.tril(m, -1).sum())
    p_d = float(np.trace(m))
    p_a = float(np.triu(m, 1).sum())
    ks = np.arange(MAXG + 1)
    p_o = float(m[(ks[:, None] + ks[None, :]) > 2.5].sum())
    return p_h, p_d, p_a, p_o


def metrics(rows):
    ll = rps = oull = 0.0
    for r in rows:
        y = 0 if r["hg"] > r["ag"] else (1 if r["hg"] == r["ag"] else 2)
        p = np.array([r["pH"], r["pD"], r["pA"]])
        ll -= np.log(max(p[y], 1e-12))
        obs = np.zeros(3); obs[y] = 1
        rps += 0.5 * np.sum((np.cumsum(p)[:2] - np.cumsum(obs)[:2]) ** 2)
        over = float(r["hg"] + r["ag"] > 2.5)
        oull -= over * np.log(max(r["p_over"], 1e-12)) + (1 - over) * np.log(max(1 - r["p_over"], 1e-12))
    n = len(rows)
    return {"n": n, "ll_1x2": ll / n, "rps": rps / n, "ll_ou25": oull / n}


def _row(r, p):
    return {"match_id": int(r.match_id), "date": str(r.date.date()),
            "home_team_id": int(r.home_team_id), "home_team": r.home_team,
            "away_team_id": int(r.away_team_id), "away_team": r.away_team,
            "hg": int(r.home_goals), "ag": int(r.away_goals),
            "pH": p[0], "pD": p[1], "pA": p[2], "p_over": p[3]}


def season_rows(model, df_season, prev_season_teams, arm):
    rows = []
    for _, r in df_season.iterrows():
        kw = {}
        if arm == "ENTRANT" and prev_season_teams is not None and r.home_team_id not in prev_season_teams:
            idx = {t: i for i, t in enumerate(model["teams"])}
            kw.update(ah=float(model["att"][idx[r.home_team_id]]) + ATT_SHIFT if r.home_team_id in idx else ATT_SHIFT,
                      dh=float(model["def"][idx[r.home_team_id]]) - DEF_SHIFT if r.home_team_id in idx else -DEF_SHIFT)
        if arm == "ENTRANT" and prev_season_teams is not None and r.away_team_id not in prev_season_teams:
            idx = {t: i for i, t in enumerate(model["teams"])}
            kw.update(aa=float(model["att"][idx[r.away_team_id]]) + ATT_SHIFT if r.away_team_id in idx else ATT_SHIFT,
                      da=float(model["def"][idx[r.away_team_id]]) - DEF_SHIFT if r.away_team_id in idx else -DEF_SHIFT)
        rows.append(_row(r, probs_1x2_ou(predict_matrix(model, r.home_team_id, r.away_team_id, **kw))))
    return rows


def climatology_rows(train, df_season):
    y = np.where(train.home_goals > train.away_goals, 0, np.where(train.home_goals == train.away_goals, 1, 2))
    rates = np.array([(y == k).mean() for k in range(3)])
    po = float(((train.home_goals + train.away_goals) > 2.5).mean())
    return [_row(r, (*rates, po)) for _, r in df_season.iterrows()]


class Trailing10:
    def __init__(self, league_mean):
        self.hist, self.league_mean = {}, league_mean

    def feed(self, df):
        for _, r in df.iterrows():
            self.hist.setdefault(r.home_team_id, deque(maxlen=10)).append(float(r.home_goals))
            self.hist.setdefault(r.away_team_id, deque(maxlen=10)).append(float(r.away_goals))

    def rows_for(self, df_season):
        rows = []
        for _, r in df_season.iterrows():
            lh = float(np.mean(self.hist.get(r.home_team_id, []))) if self.hist.get(r.home_team_id) else self.league_mean
            la = float(np.mean(self.hist.get(r.away_team_id, []))) if self.hist.get(r.away_team_id) else self.league_mean
            ks = np.arange(MAXG + 1)
            m = np.outer(poisson.pmf(ks, lh), poisson.pmf(ks, la)); m /= m.sum()
            rows.append(_row(r, probs_1x2_ou(m)))
        return rows


def _groups(df):
    return [(d, g.sort_values("match_id")) for d, g in df.groupby("date", sort=True)]


def _prediction_columns(row, arm, baseline):
    return {"arm": arm, "match_id": row["match_id"], "date": row["date"],
            "home_team": row["home_team"], "away_team": row["away_team"],
            "actual_home_goals": row["hg"], "actual_away_goals": row["ag"],
            "lambda_home": row.get("lambda_home"), "lambda_away": row.get("lambda_away"),
            "p_home": row["pH"], "p_draw": row["pD"], "p_away": row["pA"],
            "p_over_2_5": row["p_over"], **{f"baseline_{k}": v for k, v in baseline.items()}}


def _dc_group_rows(model, group, prev_teams, arm):
    rows = season_rows(model, group, prev_teams, arm)
    for row, (_, original) in zip(rows, group.iterrows()):
        idx = {t: i for i, t in enumerate(model["teams"])}
        ah = float(model["att"][idx[original.home_team_id]]) if original.home_team_id in idx else 0.0
        da = float(model["def"][idx[original.away_team_id]]) if original.away_team_id in idx else 0.0
        aa = float(model["att"][idx[original.away_team_id]]) if original.away_team_id in idx else 0.0
        dh = float(model["def"][idx[original.home_team_id]]) if original.home_team_id in idx else 0.0
        if arm == "ENTRANT" and prev_teams is not None:
            if original.home_team_id not in prev_teams: ah += ATT_SHIFT; dh -= DEF_SHIFT
            if original.away_team_id not in prev_teams: aa += ATT_SHIFT; da -= DEF_SHIFT
        row["lambda_home"], row["lambda_away"] = float(np.exp(ah - da + model["home"])), float(np.exp(aa - dh))
    return rows


def _calibration(rows):
    out = {}
    for name, pkey, y in (("home_win", "pH", np.array([r["hg"] > r["ag"] for r in rows], float)),
                          ("ou25", "p_over", np.array([r["hg"] + r["ag"] > 2.5 for r in rows], float))):
        p = np.array([r[pkey] for r in rows])
        gap = float(np.mean(y) - np.mean(p)) * 100
        se = float(np.std(y - p, ddof=1) / np.sqrt(len(rows))) * 100
        out[name] = {"actual_minus_predicted_pp": gap, "se_pp": se,
                     "leg": "PASS clean" if abs(gap) <= 1 else ("PASS provisional" if abs(gap) <= 1 + se else "FAIL")}
    return out


def run_goals(out_dir):
    out_dir = Path(out_dir)
    data_path = Path(__file__).parents[2] / "data" / "qasd_matches.csv"
    data = pd.read_csv(data_path, parse_dates=["date", "kickoff_utc"])
    # The dev loader is deliberately restricted before any fitting or metric work.
    data = data[data.season == DEV_SEASON].copy().sort_values(["date", "match_id"])
    assert set(data.season) == {DEV_SEASON}
    warm = data[data["round"].astype(str).astype(int).between(1, 7)].copy()
    scored = data[data["round"].astype(str).astype(int).between(8, 14)].copy()
    assert len(data) == 56 and len(warm) == 28 and len(scored) == 28
    arms = ["GateZero", "ENTRANT"]
    prev_teams = None  # No preceding season exists in the corpus for dev.
    t10 = Trailing10(float((warm.home_goals.sum() + warm.away_goals.sum()) / (2 * len(warm))))
    t10.feed(warm)
    collected = {a: [] for a in arms}; clim_rows = []; naive_rows = []; pred_rows = []
    history = warm.copy()
    for date, group in _groups(scored):
        train = history[history.date < date]
        assert len(train) == len(history)
        model = fit_dc(train)
        day = {}
        for a in arms:
            day[a] = _dc_group_rows(model, group, prev_teams, a)
            collected[a].extend(day[a])
        assert all(a == b for a, b in zip(day["GateZero"], day["ENTRANT"]) for a, b in [(a["pH"], b["pH"])])
        cday = climatology_rows(train, group); nday = t10.rows_for(group)
        clim_rows.extend(cday); naive_rows.extend(nday)
        for i, (_, rr) in enumerate(group.iterrows()):
            base = {"p_home": cday[i]["pH"], "p_draw": cday[i]["pD"], "p_away": cday[i]["pA"], "p_over_2_5": cday[i]["p_over"]}
            for a in arms: pred_rows.append(_prediction_columns(day[a][i], a, base | {"naive_p_home": nday[i]["pH"], "naive_p_draw": nday[i]["pD"], "naive_p_away": nday[i]["pA"], "naive_p_over_2_5": nday[i]["p_over"]}))
        history = pd.concat([history, group], ignore_index=True)
        t10.feed(group)
    # Entrant has no preceding season and must be numerically identical on every scored row.
    max_diff = max(abs(a[k] - b[k]) for a, b in zip(collected["GateZero"], collected["ENTRANT"]) for k in ("pH", "pD", "pA", "p_over"))
    assert max_diff == 0
    pooled = {a: metrics(collected[a]) for a in arms}
    bases = {"climatology": metrics(clim_rows), "naive_trailing_10": metrics(naive_rows)}
    gate = {a: bool(all(pooled[a][k] < bases[b][k] for b in bases for k in ("ll_1x2", "rps", "ll_ou25"))) for a in arms}
    dev_res = {"arms": {a: {"pooled": pooled[a], "gate_dev_pass": gate[a]} for a in arms}, **bases,
               "protocol": {"league": "QA-SecondDivision", "dev_season": DEV_SEASON, "warm_up_matches": 28,
                            "scored_matches": 28, "primary_line": "OU2.5", "sign_convention": "actual_minus_predicted",
                            "date_grouped": True, "entrant_dev_identical": True, "entrant_max_abs_diff": max_diff}}
    (out_dir / "results_dev.json").write_text(json.dumps(dev_res, indent=1))
    result_rows = [{"model": a, **pooled[a], "gate_dev_pass": gate[a]} for a in arms]
    result_rows += [{"model": k, **v, "gate_dev_pass": None} for k, v in bases.items()]
    pd.DataFrame(result_rows).to_csv(out_dir / "results_dev.csv", index=False)
    pd.DataFrame(pred_rows).to_csv(out_dir / "predictions_dev.csv", index=False)
    result = {"dev": dev_res, "virgin": None}
    if os.environ.get("QASD_DEV_ONLY", "1") == "1" or os.environ.get("QASD_RUN_VIRGIN") != "1" or not gate["GateZero"]:
        return result
    all_data = pd.read_csv(data_path, parse_dates=["date", "kickoff_utc"]).sort_values(["date", "match_id"])
    train = all_data[all_data.season == DEV_SEASON].copy(); virgin = all_data[all_data.season == VIRGIN_SEASON].copy()
    assert len(train) == 56 and len(virgin) == 56
    train0 = train.copy(); model = fit_dc(train0)
    prev_teams = set(train0.home_team_id) | set(train0.away_team_id)
    t10v = Trailing10(float((train0.home_goals.sum() + train0.away_goals.sum()) / (2 * len(train0)))); t10v.feed(train0)
    vrows = {}; vclim = []; vnaive = []
    for date, group in _groups(virgin):
        c = climatology_rows(train0, group); n = t10v.rows_for(group)
        vclim.extend(c); vnaive.extend(n)
        for a in arms:
            if gate[a]: vrows.setdefault(a, []).extend(season_rows(model, group, prev_teams, a))
        t10v.feed(group)
    vres = {a: {"metrics": metrics(rows), "calibration": _calibration(rows), "rows_file_rows": len(rows)} for a, rows in vrows.items()}
    vres["climatology"] = metrics(vclim); vres["naive_trailing_10"] = metrics(vnaive)
    (out_dir / "results_virgin.json").write_text(json.dumps(vres, indent=1))
    (out_dir / "fitted_params_virgin.json").write_text(json.dumps({"teams": [int(t) for t in model["teams"]], "att": model["att"].tolist(), "def": model["def"].tolist(), "home": model["home"], "rho": model["rho"], "fit_on": DEV_SEASON}, indent=1))
    for a, rows in vrows.items(): pd.DataFrame(rows).to_csv(out_dir / f"virgin_rows_{a}.csv", index=False)
    result["virgin"] = vres
    return result
