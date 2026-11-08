"""Audit: why do the SMART halves variants keep failing the gate?

Commissioned 2026-11-08 after the user kept the plain constant-share
goals-halves product live and asked for an audit of the failures:
(1) halves experiment 1 -- per-half DC fits lost to constant-share
    thinning in both halves;
(2) V2 -- shape corrections (per-half rho, NB) fitted to ~nothing and
    moved calibration the wrong way;
(3) V3 -- the tuning winner (per-half scale 1.046/0.999) overshot on
    validation in 1H (+2.24pp) because the tuning window's 1H level
    shortfall did not persist;
(4) SOT V9 -- the modelled SOT share beat the naive trailing team
    share yet lost to the frozen constant share.

This script MEASURES five candidate root causes (A noise floor,
B era drift, C level-vs-shape, D winner's curse, E stable per-match
signal) and writes every number to halves_audit_quantities.json.
Prose verdicts live in AUDIT_WHY_SMART_HALVES_FAIL.md.

Data: all_matches_clean.csv, top-5, seasons 2017/18-2025/26. The
2026/27 season is the untouched confirmation holdout for the shipped
product and is EXCLUDED from every measurement here.
Harness parts (C/D/E) regenerate the V3 monthly-refit predictions by
importing run_halves_goals_v3 and assert they reproduce
halves_v3_aggregates.json before any audit number is computed.

Run with the system python3 (pandas/numpy/scipy live there, not in
.venv):  python3 experiments/halves/run_halves_audit.py
"""
import json
import math
import os
import sys
import time

import numpy as np
import pandas as pd
from scipy import stats as st

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.join(HERE, "..", "..")
sys.path.insert(0, os.path.abspath(REPO))
sys.path.insert(0, HERE)

TOP5 = ["E0", "SP1", "I1", "D1", "F1"]
SEASONS = ["2017/18", "2018/19", "2019/20", "2020/21", "2021/22",
           "2022/23", "2023/24", "2024/25", "2025/26"]
FROZEN_H, FROZEN_A = 0.4419, 0.4440
LINES = (0.5, 1.5, 2.5)
EPS = 1e-12
RNG = np.random.default_rng(20261108)

Q = {"meta": {"script": "run_halves_audit.py",
              "data": "all_matches_clean.csv top-5, HT-labelled, "
                      "seasons 2017/18-2025/26 (2026/27 holdout excluded)"}}


# ----------------------------------------------------------------------
# Raw data
# ----------------------------------------------------------------------
def load_raw():
    df = pd.read_csv(os.path.join(REPO, "all_matches_clean.csv"),
                     usecols=["Div", "Season", "Date", "HomeTeam",
                              "AwayTeam", "FTHG", "FTAG", "HTHG", "HTAG"],
                     parse_dates=["Date"])
    df = df[df.Div.isin(TOP5)].dropna(subset=["HTHG", "HTAG"]).copy()
    df = df[df.Season.isin(SEASONS)].copy()
    df = df.sort_values(["Date", "Div", "HomeTeam"]).reset_index(drop=True)
    for c in ("FTHG", "FTAG", "HTHG", "HTAG"):
        df[c] = df[c].astype(int)
    df["N"] = df.FTHG + df.FTAG
    df["K"] = df.HTHG + df.HTAG
    return df


# ----------------------------------------------------------------------
# A. Noise floor
# ----------------------------------------------------------------------
def share_decomp(K, N, min_n=1):
    """Variance decomposition of an observed share K/N.

    Weights matches by N. Var_obs is split into the binomial sampling
    noise expected if every match shared one true p, and the residual
    'real' variance of the latent per-match share."""
    m = N >= min_n
    K = np.asarray(K, dtype=float)[m]
    N = np.asarray(N, dtype=float)[m]
    p = K.sum() / N.sum()
    s = K / N
    w = N / N.sum()
    var_obs = float(np.sum(w * (s - p) ** 2))
    noise = float(p * (1 - p) * len(K) / N.sum())
    real = max(var_obs - noise, 0.0)
    return {"n_matches": int(len(K)), "goals": int(N.sum()), "p": float(p),
            "var_obs": var_obs, "var_noise": noise, "var_real": real,
            "sd_obs_pp": 100 * math.sqrt(var_obs),
            "sd_noise_pp": 100 * math.sqrt(noise),
            "sd_real_pp": 100 * math.sqrt(real),
            "noise_pct_of_var": 100 * noise / var_obs if var_obs else None,
            "real_pct_of_var": 100 * real / var_obs if var_obs else None}


def part_a(df):
    out = {}
    out["match_total"] = share_decomp(df.K.values, df.N.values)
    out["match_total_Nge3"] = share_decomp(df.K.values, df.N.values, min_n=3)
    out["home"] = share_decomp(df.HTHG.values, df.FTHG.values)
    out["away"] = share_decomp(df.HTAG.values, df.FTAG.values)

    # --- split-half reliability of team-venue 1H shares -------------
    units = {}
    for r in df.itertuples():
        units.setdefault((r.HomeTeam, "H"), []).append((r.HTHG, r.FTHG))
        units.setdefault((r.AwayTeam, "A"), []).append((r.HTAG, r.FTAG))
    units = {k: np.array(v, dtype=float) for k, v in units.items()
             if len(v) >= 30}
    keys = sorted(units)
    full_share, full_goals = {}, {}
    for k in keys:
        a = units[k]
        full_share[k] = a[:, 0].sum() / a[:, 1].sum() if a[:, 1].sum() else np.nan
        full_goals[k] = a[:, 1].sum()
    fs = np.array([full_share[k] for k in keys])
    fg = np.array([full_goals[k] for k in keys])
    ok = fg > 0
    keys = [k for k, o in zip(keys, ok) if o]
    fs, fg = fs[ok], fg[ok]
    p_all = float(np.average(fs, weights=fg))
    var_obs_units = float(np.average((fs - p_all) ** 2, weights=fg))
    noise_units = float(np.average(p_all * (1 - p_all) / fg, weights=fg))
    var_true_units = max(var_obs_units - noise_units, 0.0)

    rs = []
    for rep in range(50):
        s1, s2 = [], []
        for k in keys:
            a = units[k]
            idx = RNG.permutation(len(a))
            h1, h2 = idx[: len(a) // 2], idx[len(a) // 2:]
            g1, g2 = a[h1, 1].sum(), a[h2, 1].sum()
            if g1 > 0 and g2 > 0:
                s1.append(a[h1, 0].sum() / g1)
                s2.append(a[h2, 0].sum() / g2)
        rs.append(np.corrcoef(s1, s2)[0, 1])
    r_half = float(np.mean(rs))
    out["team_venue"] = {
        "n_units_min30_matches": int(len(keys)),
        "split_half_r_mean50": r_half,
        "spearman_brown_R": 2 * r_half / (1 + r_half),
        "sd_obs_pp": 100 * math.sqrt(var_obs_units),
        "sd_noise_pp": 100 * math.sqrt(noise_units),
        "sd_true_pp": 100 * math.sqrt(var_true_units),
        "var_true": var_true_units,
        "league_share": p_all,
    }

    # --- strata by realised FT total --------------------------------
    strata = {}
    p_all_m = out["match_total"]["p"]
    for n in range(1, 9):
        m = df.N.values == n
        if m.sum() < 50:
            continue
        s = df.K.values[m] / n
        strata[str(n)] = {
            "n_matches": int(m.sum()), "mean_share": float(s.mean()),
            "var_obs": float(s.var()),
            "var_binom": float(p_all_m * (1 - p_all_m) / n),
            "ratio": float(s.var() / (p_all_m * (1 - p_all_m) / n))}
    out["strata_by_N"] = strata

    # --- simulation check of the decomposition itself ---------------
    N = df.N.values.astype(float)
    K = df.K.values.astype(float)
    m = N >= 1
    N, K = N[m], K[m]
    w = N / N.sum()
    sim_vars = []
    for _ in range(500):
        Ks = RNG.binomial(N.astype(int), p_all_m)
        sim_vars.append(float(np.sum(w * (Ks / N - p_all_m) ** 2)))
    sim_vars = np.array(sim_vars)
    out["null_simulation_check"] = {
        "sim_var_mean": float(sim_vars.mean()),
        "sim_var_sd": float(sim_vars.std()),
        "observed_var": out["match_total"]["var_obs"],
        "observed_percentile": float(100 * np.mean(
            sim_vars < out["match_total"]["var_obs"])),
        "z": float((out["match_total"]["var_obs"] - sim_vars.mean())
                   / sim_vars.std())}

    # --- cross-check on SOT halves (different market, same test) ----
    sot_path = os.path.join(REPO, "data_enrichment",
                            "sot_halves_combined.csv")
    if os.path.exists(sot_path):
        sd = pd.read_csv(sot_path)
        sd = sd[sd["div"].isin(TOP5) & sd["season"].isin(SEASONS)]
        Ns = sd["sot_ft_halves"].values.astype(float)
        Ks = (sd["sot_1h_h"] + sd["sot_1h_a"]).values.astype(float)
        out["sot_crosscheck"] = share_decomp(Ks, Ns)
    Q["A_noise_floor"] = out
    return out


# ----------------------------------------------------------------------
# B. Era drift
# ----------------------------------------------------------------------
def season_share(d):
    K, N = int(d.K.sum()), int(d.N.sum())
    Kh, Nh = int(d.HTHG.sum()), int(d.FTHG.sum())
    Ka, Na = int(d.HTAG.sum()), int(d.FTAG.sum())
    p = K / N
    return {"n_matches": int(len(d)), "goals": N, "share": p,
            "se_pp": 100 * math.sqrt(p * (1 - p) / N),
            "share_home": Kh / Nh, "share_away": Ka / Na}


def part_b(df):
    per = {}
    for s in SEASONS:
        per[s] = season_share(df[df.Season == s])
    K = np.array([per[s]["goals"] * per[s]["share"] for s in SEASONS])
    N = np.array([per[s]["goals"] for s in SEASONS], dtype=float)
    p_pool = K.sum() / N.sum()
    chi2 = float(np.sum((K - p_pool * N) ** 2 / (p_pool * (1 - p_pool) * N)))
    dof = len(SEASONS) - 1
    shares = np.array([per[s]["share"] for s in SEASONS])
    eras = {"2017/18-2019/20": ["2017/18", "2018/19", "2019/20"],
            "2020/21-2022/23": ["2020/21", "2021/22", "2022/23"],
            "2023/24-2025/26": ["2023/24", "2024/25", "2025/26"]}
    era_out = {}
    for name, ss in eras.items():
        d = df[df.Season.isin(ss)]
        era_out[name] = season_share(d)
    tun = df[(df.Date >= "2020-08-01") & (df.Date < "2023-08-01")]
    val = df[(df.Date >= "2023-08-01") & (df.Date < "2026-07-01")]
    out = {"per_season": per, "pooled_share": float(p_pool),
           "chi2_homogeneity": chi2, "chi2_dof": dof,
           "chi2_p": float(st.chi2.sf(chi2, dof)),
           "range_pp": 100 * float(shares.max() - shares.min()),
           "sd_across_seasons_pp": 100 * float(shares.std(ddof=1)),
           "eras": era_out,
           "v3_tuning_window_share": season_share(tun),
           "v3_validation_window_share": season_share(val)}
    Q["B_era_drift"] = out
    return out


# ----------------------------------------------------------------------
# Vectorised replica of the V2/V3 DC over-probabilities
# ----------------------------------------------------------------------
def _pmf(k, lam):
    from scipy.special import gammaln
    lam = np.maximum(np.asarray(lam, dtype=float), 1e-12)
    k = np.asarray(k, dtype=float)
    return np.exp(-lam + k * np.log(lam) - gammaln(k + 1))


def over_probs_vec(lh, la, rho):
    """Exact numpy replica of run_halves_goals_v2.over_probs."""
    lh = np.asarray(lh, dtype=float)
    la = np.asarray(la, dtype=float)
    rho = np.asarray(rho, dtype=float)
    p00 = _pmf(0, lh) * _pmf(0, la)
    p01 = _pmf(0, lh) * _pmf(1, la)
    p10 = _pmf(1, lh) * _pmf(0, la)
    p11 = _pmf(1, lh) * _pmf(1, la)
    p02 = _pmf(0, lh) * _pmf(2, la)
    p20 = _pmf(2, lh) * _pmf(0, la)
    fh = sum(_pmf(x, lh) for x in range(11))
    fa = sum(_pmf(y, la) for y in range(11))
    s0 = fh * fa
    t00 = np.clip(1.0 - lh * la * rho, 0, None)
    t01 = np.clip(1.0 + lh * rho, 0, None)
    t10 = np.clip(1.0 + la * rho, 0, None)
    t11 = np.clip(1.0 - rho, 0, None)
    s = (s0 + p00 * (t00 - 1) + p01 * (t01 - 1)
         + p10 * (t10 - 1) + p11 * (t11 - 1))
    a00, a01, a10, a11 = p00 * t00, p01 * t01, p10 * t10, p11 * t11
    return {0.5: 1.0 - a00 / s,
            1.5: 1.0 - (a00 + a01 + a10) / s,
            2.5: 1.0 - (a00 + a01 + a10 + p02 + a11 + p20) / s}


def pooled_ou_ll(lh, la, rho, y):
    probs = over_probs_vec(lh, la, rho)
    y = np.asarray(y, dtype=float)
    tot = 0.0
    for line in LINES:
        p = np.clip(probs[line], EPS, 1 - EPS)
        yy = (y > line).astype(float)
        tot += float(np.sum(-(yy * np.log(p) + (1 - yy) * np.log(1 - p))))
    return tot / (len(y) * len(LINES))


def over15_calib_pp(lh, la, rho, y):
    p = over_probs_vec(lh, la, rho)[1.5]
    return 100.0 * (float(np.mean(p)) - float(np.mean(np.asarray(y) > 1)))


def season_of(d):
    y = d.year if d.month >= 7 else d.year - 1
    return f"{y}/{str(y + 1)[-2:]}"


# ----------------------------------------------------------------------
# Harness regeneration (V3 machinery, verification first)
# ----------------------------------------------------------------------
def build_harness():
    from run_halves_goals_v3 import (games_by_div, fit_dc, month_cutoffs,
                                     build_predictions, evaluate)
    from features import _load_xg_map
    from datetime import date

    df = pd.read_csv(os.path.join(REPO, "all_matches_clean.csv"),
                     usecols=["Div", "Date", "HomeTeam", "AwayTeam",
                              "FTHG", "FTAG", "HTHG", "HTAG"],
                     parse_dates=["Date"])
    df = df[df.Div.isin(TOP5)].dropna(subset=["HTHG", "HTAG"]).copy()
    df["H2HG"] = df.FTHG - df.HTHG
    df["H2AG"] = df.FTAG - df.HTAG
    df = df.sort_values(["Date", "Div", "HomeTeam"])
    xg_map = _load_xg_map()
    by_div = games_by_div(df, xg_map)
    cutoffs = month_cutoffs(date(2020, 8, 1), date(2026, 6, 1))
    fits = {}
    for div in TOP5:
        games = by_div[div]
        for C in cutoffs:
            fits[(div, C)] = fit_dc([g for g in games if g[6] < C], C)
    tuning_df = df[(df.Date >= "2020-08-01") & (df.Date < "2023-08-01")]
    test_df = df[(df.Date >= "2023-08-01") & (df.Date < "2026-07-01")]
    tuning = build_predictions(tuning_df, fits)
    test = build_predictions(test_df, fits)
    for p in tuning + test:
        p["season"] = season_of(p["date"])

    # --- verify against the frozen V3 aggregates -------------------
    agg = json.load(open(os.path.join(HERE, "halves_v3_aggregates.json")))
    ev_t = evaluate(tuning, "a", {"1H": {}, "2H": {}})
    ev_v = evaluate(test, "a", {"1H": {}, "2H": {}})
    checks = {
        "tuning_1H_ll": (ev_t["1H"]["pooled_ou_ll"],
                         agg["tuning_table"]["a"]["per_half"]["1H"]["pooled_ou_ll"]),
        "tuning_1H_calib": (ev_t["1H"]["over15_calib_pp"],
                            agg["tuning_table"]["a"]["per_half"]["1H"]["over15_calib_pp"]),
        "val_1H_ll": (ev_v["1H"]["pooled_ou_ll"],
                      agg["validation_table"][0]["per_half"]["1H"]["pooled_ou_ll"]),
        "val_1H_calib": (ev_v["1H"]["over15_calib_pp"],
                         agg["validation_table"][0]["per_half"]["1H"]["over15_calib_pp"]),
        "val_2H_calib": (ev_v["2H"]["over15_calib_pp"],
                         agg["validation_table"][0]["per_half"]["2H"]["over15_calib_pp"]),
    }
    for name, (mine, theirs) in checks.items():
        assert abs(mine - theirs) < 2e-4, (name, mine, theirs)
    # vectorised scorer must agree with the V3 evaluator too
    lh = np.array([p["halves"]["1H"]["lh"] for p in test])
    la = np.array([p["halves"]["1H"]["la"] for p in test])
    rho = np.array([p["rho_ft"] for p in test])
    y = np.array([p["halves"]["1H"]["total"] for p in test])
    vec_ll = pooled_ou_ll(lh, la, rho, y)
    assert abs(vec_ll - ev_v["1H"]["pooled_ou_ll"]) < 1e-9, (vec_ll,
           ev_v["1H"]["pooled_ou_ll"])
    print(f"harness verified vs V3 aggregates "
          f"(tuning n={len(tuning)}, validation n={len(test)})")
    return tuning, test


# ----------------------------------------------------------------------
# A3. Oracle ceiling simulation
# ----------------------------------------------------------------------
def part_a3(test, a):
    """Ceiling on ANY share model's pooled OU log-loss gain.

    Simulate half goals on the real validation fixtures: latent
    per-team 1H shares drawn with the REAL between-match SD measured
    in part A (home/away), goals Poisson at the harness FT lambdas.
    Score the constant-share prediction vs an ORACLE that knows the
    drawn shares. Poisson totals are used for scoring (the same
    simplification V3 candidate (d) uses); R sims, plus a sigma=0
    control that must return ~0."""
    lh = np.array([p["lh_ft"] for p in test])
    la = np.array([p["la_ft"] for p in test])
    n = len(test)

    def run(sd_h, sd_a, R=300):
        gains = {"1H": [], "2H": []}
        for _ in range(R):
            sh = np.clip(RNG.normal(FROZEN_H, sd_h, n), 0.05, 0.95)
            sa = np.clip(RNG.normal(FROZEN_A, sd_a, n), 0.05, 0.95)
            for half, sgn in (("1H", 1), ("2H", -1)):
                if sgn == 1:
                    mu_t = lh * sh + la * sa
                    mu_c = lh * FROZEN_H + la * FROZEN_A
                else:
                    mu_t = lh * (1 - sh) + la * (1 - sa)
                    mu_c = lh * (1 - FROZEN_H) + la * (1 - FROZEN_A)
                y = RNG.poisson(mu_t)
                ll = {}
                for tag, mu in (("c", mu_c), ("o", mu_t)):
                    tot = 0.0
                    for line in LINES:
                        p = np.clip(1 - st.poisson.cdf(int(line), mu),
                                    EPS, 1 - EPS)
                        yy = (y > line).astype(float)
                        tot += float(np.sum(-(yy * np.log(p)
                                              + (1 - yy) * np.log(1 - p))))
                    ll[tag] = tot / (n * len(LINES))
                gains[half].append(ll["c"] - ll["o"])
        return {h: {"mean_gain": float(np.mean(v)),
                    "sd": float(np.std(v))} for h, v in gains.items()}

    sd_h = a["home"]["sd_real_pp"] / 100.0
    sd_a = a["away"]["sd_real_pp"] / 100.0
    mu1h = lh * FROZEN_H + la * FROZEN_A
    share_induced_sd = np.sqrt((lh * sd_h) ** 2 + (la * sd_a) ** 2)
    # sensitivity: the measured sigma is 0, so also price hypothetical
    # latent share SDs -- how large would the true signal have to be
    # before ANY share model could clear even 0.001 of log loss?
    sens = {}
    for spp in (1.0, 2.0, 3.0, 5.0):
        sens[f"sigma_{spp:.0f}pp"] = run(spp / 100.0, spp / 100.0, R=200)
    out = {"sigma_h_pp": 100 * sd_h, "sigma_a_pp": 100 * sd_a,
           "ceiling_gain": run(sd_h, sd_a),
           "control_sigma0_gain": run(0.0, 0.0, R=100),
           "sensitivity_hypothetical_sigma": sens,
           "mean_mu_1h": float(np.mean(mu1h)),
           "mean_share_induced_sd_of_mu_1h": float(np.mean(share_induced_sd)),
           "mean_poisson_sd_of_mu_1h": float(np.mean(np.sqrt(mu1h)))}
    Q["A3_oracle_ceiling"] = out
    return out


# ----------------------------------------------------------------------
# C. Level vs shape (oracle checks, IN-SAMPLE by design, labelled)
# ----------------------------------------------------------------------
def _cell_ll(lh, la, yh, ya, rho):
    """Full-scoreline DC log-likelihood, vectorised replica of V2's
    cell_prob path (used for the oracle rho fit)."""
    base = _pmf(yh, lh) * _pmf(ya, la)
    tau = np.ones_like(base)
    m00 = (yh == 0) & (ya == 0)
    m01 = (yh == 0) & (ya == 1)
    m10 = (yh == 1) & (ya == 0)
    m11 = (yh == 1) & (ya == 1)
    tau = np.where(m00, np.clip(1 - lh * la * rho, 0, None), tau)
    tau = np.where(m01, np.clip(1 + lh * rho, 0, None), tau)
    tau = np.where(m10, np.clip(1 + la * rho, 0, None), tau)
    tau = np.where(m11, np.clip(1 - rho, 0, None), tau)
    fh = sum(_pmf(x, lh) for x in range(11))
    fa = sum(_pmf(y, la) for y in range(11))
    p00 = _pmf(0, lh) * _pmf(0, la)
    p01 = _pmf(0, lh) * _pmf(1, la)
    p10 = _pmf(1, lh) * _pmf(0, la)
    p11 = _pmf(1, lh) * _pmf(1, la)
    s = (fh * fa + p00 * (np.clip(1 - lh * la * rho, 0, None) - 1)
         + p01 * (np.clip(1 + lh * rho, 0, None) - 1)
         + p10 * (np.clip(1 + la * rho, 0, None) - 1)
         + p11 * (np.clip(1 - rho, 0, None) - 1))
    return float(np.sum(np.log(np.clip(base * tau / s, EPS, None))))


def part_c(tuning, test):
    from scipy.special import gammaln
    R_GRID = [3, 4, 5, 6, 8, 10, 13, 16, 20, 25, 32, 40, 50, 65, 80,
              100, 130, 170, 220, 300, 450, 700, 1200, 2500, 6000]
    out = {}
    for wname, preds in (("tuning", tuning), ("validation", test)):
        w = {}
        for half in ("1H", "2H"):
            lh = np.array([p["halves"][half]["lh"] for p in preds])
            la = np.array([p["halves"][half]["la"] for p in preds])
            yh = np.array([p["halves"][half]["yh"] for p in preds],
                          dtype=float)
            ya = np.array([p["halves"][half]["ya"] for p in preds],
                          dtype=float)
            y = yh + ya
            mu = lh + la
            # oracle rho: maximise scoreline LL on THIS window
            rhos = [round(-0.30 + 0.01 * i, 2) for i in range(51)]
            lls = [_cell_ll(lh, la, yh, ya, r) for r in rhos]
            rho_or = rhos[int(np.argmax(lls))]
            # oracle NB size on half totals given the means
            def nb_ll(r):
                return float(np.sum(
                    gammaln(y + r) - gammaln(r) - gammaln(y + 1)
                    + r * np.log(r / (r + mu))
                    + y * np.log(mu / (r + mu))))
            nb = [(r, nb_ll(float(r))) for r in R_GRID]
            r_or = max(nb, key=lambda t: t[1])[0]
            pois_ll = float(np.sum(y * np.log(mu) - mu
                                   - gammaln(y + 1)))
            w[half] = {
                "n": int(len(preds)),
                "mean_pred_total": float(np.mean(mu)),
                "mean_actual_total": float(np.mean(y)),
                "mean_residual": float(np.mean(mu) - np.mean(y)),
                "implied_optimal_scale": float(np.sum(y) / np.sum(mu)),
                "dispersion_ratio": float(np.sum((y - mu) ** 2)
                                          / np.sum(mu)),
                "oracle_rho": rho_or,
                "oracle_nb_r": r_or,
                "nb_oracle_ll_gain_vs_poisson": max(
                    0.0, (max(v for _, v in nb) - pois_ll) / len(preds)),
                "oracle_rho_calib15_pp": over15_calib_pp(
                    lh, la, np.full(len(preds), rho_or), y),
                "ft_rho_calib15_pp": over15_calib_pp(
                    lh, la, np.array([p["rho_ft"] for p in preds]), y),
            }
        out[wname] = w
    Q["C_level_vs_shape_ORACLE_insample"] = out
    return out


# ----------------------------------------------------------------------
# D. Winner's curse in V3
# ----------------------------------------------------------------------
def part_d(tuning, test):
    out = {}
    # arrays per window/half
    def arr(preds, half):
        return (np.array([p["halves"][half]["lh"] for p in preds]),
                np.array([p["halves"][half]["la"] for p in preds]),
                np.array([p["rho_ft"] for p in preds]),
                np.array([p["halves"][half]["total"] for p in preds],
                         dtype=float),
                np.array([p["halves"][half]["pred_total"] for p in preds]))
    SCALE_B = {"1H": 1.0459584801225459, "2H": 0.9991849334675459}

    # --- D1: per-season decomposition inside the tuning window -----
    seasons = {}
    for s in ("2020/21", "2021/22", "2022/23"):
        idx = [i for i, p in enumerate(tuning) if p["season"] == s]
        row = {"n": len(idx)}
        for half in ("1H", "2H"):
            lh, la, rho, y, exp = arr([tuning[i] for i in idx], half)
            s_fit = float(np.sum(y) / np.sum(exp))
            ll_a = pooled_ou_ll(lh, la, rho, y)
            sc = SCALE_B[half]
            ll_b = pooled_ou_ll(lh * sc, la * sc, rho, y)
            row[half] = {
                "own_scale": s_fit,
                "baseline_calib15_pp": over15_calib_pp(lh, la, rho, y),
                "global_b_calib15_pp": over15_calib_pp(
                    lh * sc, la * sc, rho, y),
                "ll_delta_global_b": ll_b - ll_a,
                "mean_residual": float(np.mean(exp) - np.mean(y)),
            }
        seasons[s] = row
    out["tuning_per_season"] = seasons

    # --- D2: bootstrap of the tuning winner -------------------------
    B = 1000
    boot = {"1H": {"scale": [], "ll_gain": [], "calib_b": [],
                   "pass": []},
            "2H": {"scale": [], "ll_gain": [], "calib_b": [],
                   "pass": []}}
    data = {h: arr(tuning, h) for h in ("1H", "2H")}
    n = len(tuning)
    for _ in range(B):
        idx = RNG.integers(0, n, n)
        for half in ("1H", "2H"):
            lh, la, rho, y, exp = data[half]
            s_star = float(np.sum(y[idx]) / np.sum(exp[idx]))
            lh_b = lh[idx] * s_star
            la_b = la[idx] * s_star
            ll_a = pooled_ou_ll(lh[idx], la[idx], rho[idx], y[idx])
            ll_b = pooled_ou_ll(lh_b, la_b, rho[idx], y[idx])
            calib = over15_calib_pp(lh_b, la_b, rho[idx], y[idx])
            boot[half]["scale"].append(s_star)
            boot[half]["ll_gain"].append(ll_a - ll_b)
            boot[half]["calib_b"].append(calib)
            boot[half]["pass"].append(
                bool((ll_b - ll_a) <= 0.0005 and abs(calib) <= 1.0))
    bs = {}
    for half in ("1H", "2H"):
        sc = np.array(boot[half]["scale"])
        lg = np.array(boot[half]["ll_gain"])
        cb = np.array(boot[half]["calib_b"])
        ps = np.array(boot[half]["pass"])
        bs[half] = {
            "scale_mean": float(np.mean(sc)), "scale_sd": float(np.std(sc)),
            "scale_q05": float(np.quantile(sc, 0.05)),
            "scale_q95": float(np.quantile(sc, 0.95)),
            "p_scale_le_1_01": float(np.mean(sc <= 1.01)),
            "p_scale_le_1_00": float(np.mean(sc <= 1.00)),
            "ll_gain_mean": float(np.mean(lg)),
            "ll_gain_q05": float(np.quantile(lg, 0.05)),
            "p_ll_gain_le_0": float(np.mean(lg <= 0)),
            "calib_b_sd_pp": float(np.std(cb)),
            "p_pass_both_legs_this_half": float(np.mean(ps)),
        }
    out["bootstrap_B1000"] = bs

    # --- D3: map tuning parameter uncertainty onto validation ------
    lh, la, rho, y, exp = arr(test, "1H")
    grid = np.round(np.arange(1.000, 1.0801, 0.004), 3)
    cal_grid = [over15_calib_pp(lh * s, la * s, rho, y) for s in grid]
    sc_boot = np.array(boot["1H"]["scale"])
    cal_mapped = np.interp(sc_boot, grid, cal_grid)
    out["validation_calib_under_tuning_uncertainty"] = {
        "grid_scale": [float(x) for x in grid],
        "grid_calib15_pp": [float(x) for x in cal_grid],
        "calib_at_scale_1_000_pp": float(cal_grid[0]),
        "calib_at_fitted_1_046_pp": float(np.interp(1.0459584801225459,
                                                    grid, cal_grid)),
        "mapped_median_pp": float(np.median(cal_mapped)),
        "mapped_q05_pp": float(np.quantile(cal_mapped, 0.05)),
        "mapped_q95_pp": float(np.quantile(cal_mapped, 0.95)),
        "p_within_gate_1pp": float(np.mean(np.abs(cal_mapped) <= 1.0)),
    }
    Q["D_winners_curse"] = out
    return out


# ----------------------------------------------------------------------
# E. Stable per-match signal?
# ----------------------------------------------------------------------
def part_e(df, tuning, test):
    out = {}
    train_mask = df.Date < "2023-08-01"
    p_train = float(df.loc[train_mask, "K"].sum()
                    / df.loc[train_mask, "N"].sum())

    def preds_arrays(preds):
        return {
            "lh_ft": np.array([p["lh_ft"] for p in preds]),
            "la_ft": np.array([p["la_ft"] for p in preds]),
            "rho": np.array([p["rho_ft"] for p in preds]),
            "div": np.array([p["div"] for p in preds]),
            "y1": np.array([p["halves"]["1H"]["total"] for p in preds],
                           dtype=float),
            "y2": np.array([p["halves"]["2H"]["total"] for p in preds],
                           dtype=float),
            "lh1": np.array([p["halves"]["1H"]["lh"] for p in preds]),
            "la1": np.array([p["halves"]["1H"]["la"] for p in preds]),
            "lh2": np.array([p["halves"]["2H"]["lh"] for p in preds]),
            "la2": np.array([p["halves"]["2H"]["la"] for p in preds]),
        }

    va = preds_arrays(test)
    tu = preds_arrays(tuning)

    def total_ll(a, lh1, la1, lh2, la2):
        return (pooled_ou_ll(lh1, la1, a["rho"], a["y1"])
                + pooled_ou_ll(lh2, la2, a["rho"], a["y2"]))

    base_ll = total_ll(va, va["lh1"], va["la1"], va["lh2"], va["la2"])
    out["validation_baseline_ll_sum"] = base_ll

    # E4: venue-split value (venue constants vs one global constant)
    g1h = va["lh_ft"] * p_train
    g1a = va["la_ft"] * p_train
    glob_ll = total_ll(va, g1h, g1a, va["lh_ft"] * (1 - p_train),
                       va["la_ft"] * (1 - p_train))
    out["E4_venue_split"] = {"global_share_train": p_train,
                             "ll_global_constant": glob_ll,
                             "ll_venue_constant": base_ll,
                             "venue_gain": glob_ll - base_ll}

    # E2: per-division constant shares fitted on train era
    div_share = {}
    for d in TOP5:
        dd = df[train_mask & (df.Div == d)]
        div_share[d] = float(dd.K.sum() / dd.N.sum())
    sh_v = np.array([div_share[d] for d in va["div"]])
    div_ll = total_ll(va, va["lh_ft"] * sh_v, va["la_ft"] * sh_v,
                      va["lh_ft"] * (1 - sh_v), va["la_ft"] * (1 - sh_v))
    div_share_val = {}
    for d in TOP5:
        dd = df[(df.Date >= "2023-08-01") & (df.Date < "2026-07-01")
                & (df.Div == d)]
        div_share_val[d] = float(dd.K.sum() / dd.N.sum())
    out["E2_league"] = {"train_shares": div_share,
                        "validation_actual_shares": div_share_val,
                        "ll_division_constant": div_ll,
                        "gain_vs_venue_constant": base_ll - div_ll}

    # E1: FT-lambda level -> share (fit on tuning, judge on validation)
    def obs_share(a, preds):
        K = np.array([p["halves"]["1H"]["total"] for p in preds],
                     dtype=float)
        N = np.array([p["ft_total"] for p in preds], dtype=float)
        return K, N
    Kt, Nt = obs_share(tu, tuning)
    mu_t = tu["lh_ft"] + tu["la_ft"]
    m = Nt >= 1
    w = Nt[m]
    X = np.column_stack([np.ones(m.sum()), mu_t[m]])
    W = np.diag(w)
    beta = np.linalg.solve(X.T @ W @ X, X.T @ W @ (Kt[m] / Nt[m]))
    Kv, Nv = obs_share(va, test)
    mu_v = va["lh_ft"] + va["la_ft"]
    qs = np.quantile(mu_t, [0, .2, .4, .6, .8, 1.0])
    bins = []
    for i in range(5):
        bm = (mu_v >= qs[i]) & (mu_v <= qs[i + 1] if i == 4
                                else mu_v < qs[i + 1])
        bins.append({"mu_mid": float(np.mean(mu_v[bm])),
                     "n": int(bm.sum()),
                     "obs_share": float(Kv[bm].sum() / Nv[bm].sum())
                     if Nv[bm].sum() else None})
    sh_lam = np.clip(beta[0] + beta[1] * mu_v, 0.30, 0.60)
    lam_ll = total_ll(va, va["lh_ft"] * sh_lam, va["la_ft"] * sh_lam,
                      va["lh_ft"] * (1 - sh_lam), va["la_ft"] * (1 - sh_lam))

    def w_slope(x, K, N):
        m = N >= 1
        x, K, N = x[m], K[m], N[m]
        X = np.column_stack([np.ones(m.sum()), x])
        W = np.diag(N)
        b = np.linalg.solve(X.T @ W @ X, X.T @ W @ (K / N))
        return float(b[1])

    Kt2 = np.array([p["halves"]["1H"]["total"] for p in tuning],
                   dtype=float)
    Nt2 = np.array([p["ft_total"] for p in tuning], dtype=float)
    Kv2 = np.array([p["halves"]["1H"]["total"] for p in test],
                   dtype=float)
    Nv2 = np.array([p["ft_total"] for p in test], dtype=float)
    out["E1_lambda_level"] = {
        "fit_on_tuning": {"intercept": float(beta[0]),
                          "slope_per_goal": float(beta[1])},
        "validation_bins_by_tuning_quintiles": bins,
        "ll_lambda_share": lam_ll,
        "gain_vs_venue_constant": base_ll - lam_ll,
        "window_slopes_share_on_pred_mu": {
            "tuning": w_slope(mu_t, Kt2, Nt2),
            "validation": w_slope(mu_v, Kv2, Nv2)},
        "window_slopes_share_on_realised_N": {
            "tuning": w_slope(Nt2, Kt2, Nt2),
            "validation": w_slope(Nv2, Kv2, Nv2)}}

    # E3: trailing team shares (expanding, prior matches only)
    tv = Q["A_noise_floor"]["team_venue"]
    var_true = tv["var_true"]
    p_pool = tv["league_share"]
    trail = {}
    hist = {}
    for r in df.itertuples():
        for team, k, nn in ((r.HomeTeam, r.HTHG, r.FTHG),
                            (r.AwayTeam, r.HTAG, r.FTAG)):
            h = hist.setdefault(team, [0, 0, 0])
            if h[2] >= 5 and h[1] > 0:
                raw = h[0] / h[1]
                wgt = var_true / (var_true + p_pool * (1 - p_pool) / h[1])
                shrunk = wgt * raw + (1 - wgt) * p_pool
            else:
                raw, shrunk = None, p_pool
            trail.setdefault((r.Div, str(r.Date.date()), r.HomeTeam,
                              r.AwayTeam), {})[team] = (raw, shrunk)
            h[0] += k
            h[1] += nn
            h[2] += 1
    raw_h, raw_a, shr_h, shr_a = [], [], [], []
    for p in test:
        e = trail[(p["div"], p["date_iso"], p["home"], p["away"])]
        rh, sh_ = e[p["home"]]
        ra, sa_ = e[p["away"]]
        raw_h.append(rh if rh is not None else p_pool)
        raw_a.append(ra if ra is not None else p_pool)
        shr_h.append(sh_)
        shr_a.append(sa_)
    raw_h, raw_a = np.array(raw_h), np.array(raw_a)
    shr_h, shr_a = np.array(shr_h), np.array(shr_a)
    raw_ll = total_ll(va, va["lh_ft"] * raw_h, va["la_ft"] * raw_a,
                      va["lh_ft"] * (1 - raw_h), va["la_ft"] * (1 - raw_a))
    shr_ll = total_ll(va, va["lh_ft"] * shr_h, va["la_ft"] * shr_a,
                      va["lh_ft"] * (1 - shr_h), va["la_ft"] * (1 - shr_a))
    out["E3_team_trailing"] = {
        "var_true_used": var_true,
        "mean_abs_raw_share_dev_pp": float(
            100 * np.mean(np.abs(np.concatenate(
                [raw_h, raw_a]) - p_pool))),
        "mean_abs_shrunk_share_dev_pp": float(
            100 * np.mean(np.abs(np.concatenate(
                [shr_h, shr_a]) - p_pool))),
        "ll_naive_trailing": raw_ll,
        "ll_shrunk_trailing": shr_ll,
        "gain_naive_vs_venue": base_ll - raw_ll,
        "gain_shrunk_vs_venue": base_ll - shr_ll}
    Q["E_stable_signal"] = out
    return out


# ----------------------------------------------------------------------
def main():
    t0 = time.time()
    df = load_raw()
    print(f"raw top-5 labelled 2017/18-2025/26: {len(df)} matches")
    a = part_a(df)
    print("A done:", json.dumps(a["match_total"], default=float)[:200])
    part_b(df)
    print("B done")
    tuning, test = build_harness()
    part_a3(test, a)
    print("A3 done")
    part_c(tuning, test)
    print("C done")
    part_d(tuning, test)
    print("D done")
    part_e(df, tuning, test)
    print("E done")
    Q["meta"]["runtime_seconds"] = round(time.time() - t0, 1)
    with open(os.path.join(HERE, "halves_audit_quantities.json"), "w") as f:
        json.dump(Q, f, indent=1, default=float)
    print(f"wrote halves_audit_quantities.json in {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
