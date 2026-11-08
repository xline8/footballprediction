"""Shared trait-rate Negative Binomial engine for CH count candidates
(S/C/K/T), implementing PREREG_*_CH exactly:
- per-match chronological walk-forward (date, match_id), date-grouped
  predict-then-update, target-present rows only;
- team traits: decay-weighted (HL=365d) for/against sums, shrunk to the
  decay-weighted league per-team mean with prior K=8;
  lambda_team = for_rate(team) * against_rate(opp) / league_side_mean;
- NB size r fitted on DEV scored rows only (grid, max NB loglik);
- baselines: league base rate (pre-window over-rate, constant p) and
  naive trailing-10 through the same NB r.
No sklearn; numpy/scipy only.
"""
import json
from collections import deque
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.special import gammaln

HL_DAYS = 365.0
K_PRIOR = 8.0
R_GRID = list(range(2, 61)) + [80, 100]


def nb_pmf(y, mu, r):
    y = np.asarray(y, dtype=float)
    mu = np.asarray(mu, dtype=float)
    p = r / (r + mu)
    return np.exp(gammaln(y + r) - gammaln(r) - gammaln(y + 1)
                  + r * np.log(p) + y * np.log1p(-p))


def nb_p_over(mu, r, line):
    ks = np.arange(0, int(np.floor(line)) + 1)
    cdf = nb_pmf(ks[:, None], np.atleast_1d(mu)[None, :], r).sum(axis=0)
    return 1.0 - cdf


def bern_ll(p, y):
    p = np.clip(np.asarray(p, dtype=float), 1e-9, 1 - 1e-9)
    y = np.asarray(y, dtype=float)
    return float(-np.mean(y * np.log(p) + (1 - y) * np.log(1 - p)))


def fit_r(y, mu):
    best, best_ll = None, -np.inf
    for r in R_GRID:
        ll = float(np.sum(np.log(np.clip(nb_pmf(y, mu, r), 1e-300, None))))
        if ll > best_ll:
            best, best_ll = r, ll
    return best


def walk_forward(df, target_cols, score_seasons):
    """df: matches sorted by (date, match_id) with target columns.
    Simulates ALL rows in df (state), scores rows whose season is in
    score_seasons. Returns scored rows DataFrame with mu_model and
    mu_naive (trailing-10 mean total before the match)."""
    hc, ac = target_cols
    d = df[df[hc].notna() & df[ac].notna()].copy()
    d["total"] = d[hc] + d[ac]
    teams = {}
    league = {"w": 0.0, "x": 0.0}  # per-team-match decayed sums
    last_date = None
    trail = deque(maxlen=10)
    out = []

    def state(tid):
        return teams.setdefault(tid, {"wf": 0.0, "xf": 0.0, "wa": 0.0, "xa": 0.0})

    for date, group in d.groupby("date", sort=True):
        date = pd.Timestamp(date)
        if last_date is not None:
            f = 0.5 ** ((date - last_date).days / HL_DAYS)
            if f < 1.0:
                for s in teams.values():
                    for k in s:
                        s[k] *= f
                league["w"] *= f; league["x"] *= f
        last_date = date
        mu_side = league["x"] / league["w"] if league["w"] > 0 else np.nan
        preds = []
        for _, r in group.iterrows():
            sh, sa = state(r.home_team_id), state(r.away_team_id)
            if league["w"] > 0:
                fr_h = (sh["xf"] + K_PRIOR * mu_side) / (sh["wf"] + K_PRIOR)
                ar_h = (sh["xa"] + K_PRIOR * mu_side) / (sh["wa"] + K_PRIOR)
                fr_a = (sa["xf"] + K_PRIOR * mu_side) / (sa["wf"] + K_PRIOR)
                ar_a = (sa["xa"] + K_PRIOR * mu_side) / (sa["wa"] + K_PRIOR)
                lam_h = fr_h * ar_a / mu_side
                lam_a = fr_a * ar_h / mu_side
                mu = float(lam_h + lam_a)
            else:
                mu = np.nan
            preds.append((r, mu, float(np.mean(trail)) if len(trail) == 10 else np.nan))
        for r, mu, mu_naive in preds:
            if r.season in score_seasons:
                out.append({"match_id": int(r.match_id), "season": r.season,
                            "date": str(r.date)[:10], "total": float(r.total),
                            "mu_model": mu, "mu_naive": mu_naive})
        for _, r in group.iterrows():
            sh, sa = state(r.home_team_id), state(r.away_team_id)
            hv, av = float(r[hc]), float(r[ac])
            sh["wf"] += 1; sh["xf"] += hv; sh["wa"] += 1; sh["xa"] += av
            sa["wf"] += 1; sa["xf"] += av; sa["wa"] += 1; sa["xa"] += hv
            league["w"] += 2; league["x"] += hv + av
            trail.append(hv + av)
    return pd.DataFrame(out)


def evaluate(scored, r, primary, ladder):
    y = scored["total"].to_numpy()
    res = {"n": int(len(scored)), "nb_r": r, "primary_line": primary}
    for name, mu_col in (("model", "mu_model"), ("naive10", "mu_naive")):
        sub = scored[scored[mu_col].notna()]
        yy = sub["total"].to_numpy()
        entry = {"n": int(len(sub))}
        for L in ladder:
            p = nb_p_over(sub[mu_col].to_numpy(), r, L)
            entry[f"ll_{L}"] = bern_ll(p, (yy > L).astype(float))
        p = nb_p_over(sub[mu_col].to_numpy(), r, primary)
        entry[f"calib_{primary}"] = float(np.mean(p) - np.mean(yy > primary))
        entry[f"calib_se_{primary}"] = float(np.std(p - (yy > primary), ddof=1) / np.sqrt(len(sub)))
        res[name] = entry
    return res


def run_candidate(market, target_cols, primary, ladder, warmup_seasons,
                  dev_seasons, virgin_season, out_dir):
    out_dir = Path(out_dir)
    data = pd.read_csv(Path(__file__).parent.parent / "data" / "ch_matches.csv",
                       parse_dates=["date"])
    data = data.sort_values(["date", "match_id"])
    hc, ac = target_cols
    # ---- DEV RUN: virgin rows are dropped before anything is computed ----
    dev_df = data[data.season_start <= 2024].copy()
    pre = dev_df[dev_df.season.isin(warmup_seasons)]
    base_rate_dev = float((pre[hc] + pre[ac] > primary).mean())
    scored_dev = walk_forward(dev_df, target_cols, set(dev_seasons))
    r = fit_r(scored_dev["total"].to_numpy(), scored_dev["mu_model"].to_numpy())
    dev_res = evaluate(scored_dev, r, primary, ladder)
    y_dev = (scored_dev["total"] > primary).astype(float)
    dev_res["base_rate"] = {"p": base_rate_dev,
                            f"ll_{primary}": bern_ll(np.full(len(y_dev), base_rate_dev), y_dev)}
    dev_res["gate_dev_pass"] = bool(
        dev_res["model"][f"ll_{primary}"] < dev_res["base_rate"][f"ll_{primary}"]
        and dev_res["model"][f"ll_{primary}"] < dev_res["naive10"][f"ll_{primary}"])
    scored_dev.assign(p_over=nb_p_over(scored_dev.mu_model.to_numpy(), r, primary)).to_csv(
        out_dir / "results_dev.csv", index=False)
    (out_dir / "results_dev.json").write_text(json.dumps(
        {"market": market, **dev_res}, indent=1))
    result = {"market": market, "dev": dev_res, "virgin": None}
    if not dev_res["gate_dev_pass"]:
        return result
    import os
    if os.environ.get("CH_DEV_ONLY") == "1":
        return result
    # ---- VIRGIN RUN: 2025/2026 read once, only because dev passed ----
    full_df = data[data.season_start <= 2025].copy()
    pre_v = full_df[full_df.season.isin(list(warmup_seasons) + list(dev_seasons))]
    base_rate_v = float((pre_v[hc] + pre_v[ac] > primary).mean())
    scored_v = walk_forward(full_df, target_cols, {virgin_season})
    v_res = evaluate(scored_v, r, primary, ladder)
    y_v = (scored_v["total"] > primary).astype(float)
    v_res["base_rate"] = {"p": base_rate_v,
                          f"ll_{primary}": bern_ll(np.full(len(y_v), base_rate_v), y_v)}
    best_base = min(v_res["base_rate"][f"ll_{primary}"], v_res["naive10"][f"ll_{primary}"])
    calib = abs(v_res["model"][f"calib_{primary}"]) * 100
    se_pp = v_res["model"][f"calib_se_{primary}"] * 100
    leg_i = bool(v_res["model"][f"ll_{primary}"] <= best_base)
    if calib <= 1.0:
        leg_ii = "PASS clean"
    elif calib <= 1.0 + se_pp:
        leg_ii = "PASS provisional"
    else:
        leg_ii = "FAIL"
    v_res.update({"leg_i_ll_pass": leg_i, "leg_ii_calibration": leg_ii,
                  "calib_pp": calib, "calib_se_pp": se_pp,
                  "verdict": "PASS" if (leg_i and leg_ii != "FAIL") else "FAIL"})
    scored_v.assign(p_over=nb_p_over(scored_v.mu_model.to_numpy(), r, primary)).to_csv(
        out_dir / "results_virgin.csv", index=False)
    (out_dir / "results_virgin.json").write_text(json.dumps(
        {"market": market, **v_res}, indent=1))
    (out_dir / "fitted_params_virgin.json").write_text(json.dumps(
        {"nb_r": r, "hl_days": HL_DAYS, "k_prior": K_PRIOR,
         "fit_on": "dev scored rows only (2024/2025)"}, indent=1))
    result["virgin"] = v_res
    return result
