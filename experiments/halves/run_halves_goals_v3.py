"""Halves experiment 3: constant-share goal halves under a production-faithful refit harness.

PRE-REGISTERED GATE (put verbatim in the script docstring BEFORE any numbers):
- pooled per-half O/U log loss (lines 0.5/1.5/2.5) must NOT worsen vs the uncorrected thinned baseline by more than 0.0005 in either half, AND
- per-half Over-1.5 calibration error must be within ~1pp (|err| ≤ 1.0pp) in BOTH halves,
evaluated on the validation window 2023/24–2025/26 (top-5). Both halves must pass.

Context: Experiments 1-2 (RESULTS_HALVES_GOALS.md, RESULTS_HALVES_GOALS_V2.md)
failed their gate. V2's measured diagnosis: the thinned FT lambdas came from a
STATIC goals-only fit (train <=2022/23) whose totals drift low on the test
window (FT Over 2.5 calibration -4.73pp; half means short by 0.072/0.097
goals). Production refits weekly. This experiment (V3) re-tests under a
production-faithful refit harness. The gate does NOT move.

HARNESS (production-faithful):
- Data: all_matches_clean.csv, divisions E0/SP1/I1/D1/F1, dropna HTHG/HTAG;
  2H goals = FT - HT.
- Fits: model_v2.DC exactly as production predict_upcoming_refactored.py
  does it: games as 7-tuples (home, away, FTHG, FTAG, xg_h, xg_a, date)
  with xG from features._load_xg_map() keyed by model_v2.xg_key (None when
  absent -- DC.fit falls back to goals per match), HL = 270
  (v2_config.json), fit on games[-4000:], DC_FIT_MODE left at its
  production default (do not set the env var).
- MONTHLY refits: for each division, fit at every month-start cutoff C
  from 2020-08-01 through 2026-06-01 on that division's games with
  date < C. A match on date d is predicted by the fit at C = first day
  of d's month. (Production refits weekly with cutoff = run date;
  monthly month-start fits are the stated approximation -- they exclude
  same-month earlier matches, a slight conservatism.)
- Frozen shares (do NOT refit): 1H home 0.4419, away 0.4440; 2H =
  complements.
- Baseline per half: thinned lambdas (lh*share_h, la*share_a) with the
  predicting fit's rho applied at thinned scale, over-probs via the V2
  helpers (over_probs, low_cells, nb_over, ll_bin, cell_prob imported
  from run_halves_goals_v2).

Candidates fitted ONLY on tuning predictions (matches
2020-08-01..2023-07-31 predicted by the monthly refits):
(a) none (the baseline itself).
(b) per-half multiplicative scale: closed form
    s_h = sum observed half total goals / sum predicted half total
    lambda, pooled across divisions; apply to both lh and la;
    over-probs with FT rho at scaled lambdas.
(c) per-half rho: grid -0.30..+0.20 step 0.01 maximising
    decay-weighted scoreline log-likelihood of observed half scores
    under thinned lambdas, weights
    w = 0.5**((predicting_cutoff - match_date).days/365)
    (mirror V2 form A).
(d) per-half NB size on half totals: V2's r grid, maximise LL of
    observed half totals under NB(mu = lh+la, r).

Winner selection on tuning: among candidates passing BOTH gate legs
ON TUNING (LL delta vs (a) <= +0.0005 per half AND |Over-1.5 calib|
<= 1.0pp both halves), pick lowest summed pooled OU LL across halves;
tie-break by simplicity order a, b, c, d. If none passes on tuning,
winner = smallest max-|calib| across halves (tie-break lower LL) and
flag "NO TUNING PASSER" in outputs.

Validation (run ONCE): test matches 2023-08-01..2026-06-30. For
baseline (a) and the winner: per-half pooled OU LL and Over-1.5
calibration error. If winner == (a), validation is just the baseline
row. GATE VERDICT per the pre-registered text above.

Experiments only -- no production file is touched.
Run with system python3 from repo root:
    python3 experiments/halves/run_halves_goals_v3.py
"""
import csv
import json
import math
import os
import sys
import time
from datetime import date

import pandas as pd

_START = time.time()

# --- sys.path: script's dir (for V2 helpers) + repo root (for model) ---
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.abspath(os.path.join(_SCRIPT_DIR, "..", ".."))
if _SCRIPT_DIR not in sys.path:
    sys.path.insert(0, _SCRIPT_DIR)
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

# NOTE: DC_FIT_MODE env var is deliberately NOT set; production default stands.
from run_halves_goals_v2 import (  # noqa: E402
    over_probs,
    low_cells,
    nb_over,
    ll_bin,
    cell_prob,
    nb_logpmf,
)
from model_v2 import DC, xg_key  # noqa: E402
import model_v2  # noqa: E402
from features import _load_xg_map  # noqa: E402

TOP5 = ["E0", "SP1", "I1", "D1", "F1"]
EPS = 1e-12
LINES = (0.5, 1.5, 2.5)

# HL from v2_config.json (production value 270)
_cfg_path = os.path.join(_REPO_ROOT, "v2_config.json")
with open(_cfg_path, encoding="utf-8") as _f:
    _cfg = json.load(_f)
HL = _cfg.get("hl", 270)

SHARES = {"1H": (0.4419, 0.4440), "2H": (1 - 0.4419, 1 - 0.4440)}
RHO_GRID = [round(-0.30 + 0.01 * i, 2) for i in range(51)]  # -0.30..+0.20
R_GRID = [3, 4, 5, 6, 8, 10, 13, 16, 20, 25, 32, 40, 50, 65, 80,
          100, 130, 170, 220, 300, 450, 700, 1200]
CAND_ORDER = ["a", "b", "c", "d"]
CAND_LABEL = {
    "a": "none (baseline)",
    "b": "per-half multiplicative scale",
    "c": "per-half rho",
    "d": "per-half NB size",
}


def month_start(d):
    return date(d.year, d.month, 1)


def month_cutoffs(first, last):
    """Inclusive list of month-start dates from first to last."""
    out = []
    y, m = first.year, first.month
    while (y, m) <= (last.year, last.month):
        out.append(date(y, m, 1))
        m += 1
        if m > 12:
            m = 1
            y += 1
    return out


def games_by_div(df, xg_map):
    """Per-division sorted lists of production 7-tuples."""
    by_div = {div: [] for div in TOP5}
    for r in df.itertuples():
        d = r.Date.date() if hasattr(r.Date, "date") else r.Date
        iso = str(d)[:10]
        xgh, xga = xg_map.get(
            xg_key(r.Div, iso, r.HomeTeam, r.AwayTeam), (None, None))
        by_div[r.Div].append(
            (r.HomeTeam, r.AwayTeam, int(r.FTHG), int(r.FTAG),
             xgh, xga, d))
    for div in TOP5:
        by_div[div].sort(key=lambda g: g[6])
    return by_div


def fit_dc(games_filtered, cutoff):
    m = DC()
    m.fit(games_filtered[-4000:], cutoff, HL)
    return m


def build_predictions(df_subset, fits):
    """Predictions for a dataframe subset using monthly fits.

    Each pred dict carries everything candidates/evaluation need.
    """
    preds = []
    for r in df_subset.itertuples():
        d = r.Date.date() if hasattr(r.Date, "date") else r.Date
        cutoff = month_start(d)
        model = fits[(r.Div, cutoff)]
        lh_ft, la_ft = model._lam(r.HomeTeam, r.AwayTeam)
        ft_over = model.probs(lh_ft, la_ft)["over"]
        halves = {}
        for half, yh, ya in (("1H", int(r.HTHG), int(r.HTAG)),
                             ("2H", int(r.H2HG), int(r.H2AG))):
            sh, sa = SHARES[half]
            lh_t, la_t = lh_ft * sh, la_ft * sa
            halves[half] = {
                "lh": lh_t, "la": la_t,
                "cells": low_cells(lh_t, la_t),
                "yh": yh, "ya": ya, "total": yh + ya,
                "pred_total": lh_t + la_t,
            }
        preds.append({
            "div": r.Div, "date": d, "date_iso": str(d)[:10],
            "home": r.HomeTeam, "away": r.AwayTeam,
            "cutoff": cutoff,
            "lh_ft": lh_ft, "la_ft": la_ft, "rho_ft": model.rho,
            "ft_over_refit": ft_over,
            "ft_total": int(r.FTHG) + int(r.FTAG),
            "halves": halves,
        })
    return preds


def candidate_over_probs(pred, half, cand, params):
    h = pred["halves"][half]
    lh, la, cells = h["lh"], h["la"], h["cells"]
    if cand == "a":
        return over_probs(cells, lh, la, pred["rho_ft"])
    if cand == "b":
        s = params[half]["scale"]
        lh_s, la_s = lh * s, la * s
        return over_probs(low_cells(lh_s, la_s), lh_s, la_s, pred["rho_ft"])
    if cand == "c":
        return over_probs(cells, lh, la, params[half]["rho"])
    if cand == "d":
        return nb_over(lh + la, params[half]["r"])
    raise ValueError(cand)


def evaluate(preds, cand, params):
    """Per-half pooled OU LL + Over-1.5 calibration for one candidate."""
    out = {}
    for half in ("1H", "2H"):
        ll_sum = 0.0
        ll_n = 0
        pred15_sum = 0.0
        act15_sum = 0.0
        n = 0
        for pred in preds:
            probs = candidate_over_probs(pred, half, cand, params)
            tot = pred["halves"][half]["total"]
            for line in LINES:
                y = 1.0 if tot > line else 0.0
                ll_sum += ll_bin(probs[line], y)
                ll_n += 1
            pred15_sum += probs[1.5]
            act15_sum += 1.0 if tot > 1 else 0.0
            n += 1
        out[half] = {
            "n": n,
            "pooled_ou_ll": ll_sum / ll_n if ll_n else None,
            "over15_calib_pp": ((pred15_sum / n) - (act15_sum / n)) * 100 if n else None,
            "over15_mean_pred": pred15_sum / n if n else None,
            "over15_actual_rate": act15_sum / n if n else None,
        }
    return out


def passes_gate_legs(eval_cand, eval_base):
    """Both gate legs per half, candidate eval vs baseline eval."""
    per_half = {}
    ok_all = True
    for half in ("1H", "2H"):
        ll_delta = eval_cand[half]["pooled_ou_ll"] - eval_base[half]["pooled_ou_ll"]
        calib = eval_cand[half]["over15_calib_pp"]
        ll_ok = ll_delta <= 0.0005
        calib_ok = abs(calib) <= 1.0
        per_half[half] = {
            "ll_delta_vs_baseline": ll_delta,
            "ll_ok": ll_ok,
            "over15_calib_pp": calib,
            "calib_ok": calib_ok,
            "passes": ll_ok and calib_ok,
        }
        if not (ll_ok and calib_ok):
            ok_all = False
    return ok_all, per_half


def main():
    print("=" * 72)
    print("Halves experiment 3: production-faithful monthly-refit harness")
    print(f"HL={HL}  DC_FIT_MODE={model_v2.DC_FIT_MODE!r} (production default, env not set)")
    print(f"Frozen shares: 1H home {SHARES['1H'][0]} away {SHARES['1H'][1]}; "
          f"2H home {SHARES['2H'][0]:.4f} away {SHARES['2H'][1]:.4f}")
    print("=" * 72)

    # ---- Data ----
    data_path = os.path.join(_REPO_ROOT, "all_matches_clean.csv")
    df = pd.read_csv(data_path,
                     usecols=["Div", "Date", "HomeTeam", "AwayTeam",
                              "FTHG", "FTAG", "HTHG", "HTAG"],
                     parse_dates=["Date"])
    df = df[df.Div.isin(TOP5)].dropna(subset=["HTHG", "HTAG"]).copy()
    df["H2HG"] = df.FTHG - df.HTHG
    df["H2AG"] = df.FTAG - df.HTAG
    df = df.sort_values(["Date", "Div", "HomeTeam"])
    print(f"top-5 rows with HT labels: {len(df)}")

    print("loading xG map...")
    xg_map = _load_xg_map()
    print(f"xG map entries: {len(xg_map)}")

    by_div_games = games_by_div(df, xg_map)
    for div in TOP5:
        n_xg = sum(1 for g in by_div_games[div] if g[4] is not None and g[5] is not None)
        print(f"  {div}: {len(by_div_games[div])} games, xG present {n_xg}")

    # ---- Monthly refits: every month-start 2020-08-01..2026-06-01 ----
    cutoffs = month_cutoffs(date(2020, 8, 1), date(2026, 6, 1))
    print(f"\nmonthly cutoffs: {cutoffs[0]} .. {cutoffs[-1]}  ({len(cutoffs)} per division)")
    fits = {}
    t_fit = time.time()
    for div in TOP5:
        games = by_div_games[div]
        for C in cutoffs:
            filtered = [g for g in games if g[6] < C]
            fits[(div, C)] = fit_dc(filtered, C)
        print(f"  {div}: {len(cutoffs)} monthly fits done")
    print(f"monthly fits: {len(fits)} total in {time.time() - t_fit:.1f}s")

    # ---- Static fits (FT check): one per division on games < 2023-08-01 ----
    static_cutoff = date(2023, 8, 1)
    static_fits = {}
    for div in TOP5:
        filtered = [g for g in by_div_games[div] if g[6] < static_cutoff]
        static_fits[div] = fit_dc(filtered, static_cutoff)
        print(f"  static {div}: rho {static_fits[div].rho:+.2f} on {len(filtered)} games (<2023-08-01)")

    # ---- Windows ----
    tuning_df = df[(df.Date >= "2020-08-01") & (df.Date < "2023-08-01")]
    test_df = df[(df.Date >= "2023-08-01") & (df.Date < "2026-07-01")]
    print(f"\ntuning rows {len(tuning_df)}  test rows {len(test_df)}")

    tuning_preds = build_predictions(tuning_df, fits)
    test_preds = build_predictions(test_df, fits)
    print(f"tuning predictions {len(tuning_preds)}  test predictions {len(test_preds)}")

    # ---- FT-level check (same test matches) ----
    static_probs = []
    refit_probs = []
    ft_actual = []
    for pred, r in zip(test_preds, test_df.itertuples()):
        m = static_fits[pred["div"]]
        lh_s, la_s = m._lam(pred["home"], pred["away"])
        static_probs.append(m.probs(lh_s, la_s)["over"])
        refit_probs.append(pred["ft_over_refit"])
        ft_actual.append(1.0 if pred["ft_total"] > 2 else 0.0)
    n_test = len(test_preds)
    ft_actual_rate = sum(ft_actual) / n_test
    ft_static = {
        "n": n_test,
        "mean_pred_over25": sum(static_probs) / n_test,
        "actual_over25_rate": ft_actual_rate,
        "calib_pp": (sum(static_probs) / n_test - ft_actual_rate) * 100,
    }
    ft_refit = {
        "n": n_test,
        "mean_pred_over25": sum(refit_probs) / n_test,
        "actual_over25_rate": ft_actual_rate,
        "calib_pp": (sum(refit_probs) / n_test - ft_actual_rate) * 100,
    }
    print("\n--- FT Over-2.5 calibration (test window, same matches) ---")
    print(f"  static fit (<2023-08-01): mean pred {ft_static['mean_pred_over25']*100:.2f}% "
          f"vs actual {ft_actual_rate*100:.2f}%  calib {ft_static['calib_pp']:+.2f}pp")
    print(f"  refit harness (monthly):  mean pred {ft_refit['mean_pred_over25']*100:.2f}% "
          f"vs actual {ft_actual_rate*100:.2f}%  calib {ft_refit['calib_pp']:+.2f}pp")

    # ---- Per-half mean residuals under refit harness (test) ----
    residuals = {}
    for half in ("1H", "2H"):
        diffs = [p["halves"][half]["pred_total"] - p["halves"][half]["total"]
                 for p in test_preds]
        residuals[half] = sum(diffs) / len(diffs)
    residuals_tuning = {}
    for half in ("1H", "2H"):
        diffs = [p["halves"][half]["pred_total"] - p["halves"][half]["total"]
                 for p in tuning_preds]
        residuals_tuning[half] = sum(diffs) / len(diffs)
    print("\n--- Per-half mean residuals, refit harness (pred total - actual) ---")
    print(f"  test:   1H {residuals['1H']:+.3f}  2H {residuals['2H']:+.3f}  "
          f"(V2 static: 1H -0.072, 2H -0.097)")
    print(f"  tuning: 1H {residuals_tuning['1H']:+.3f}  2H {residuals_tuning['2H']:+.3f}")

    # ---- Fit candidates ONLY on tuning predictions ----
    print("\n--- Fitting candidates on tuning predictions only ---")
    params = {"a": {"1H": {}, "2H": {}}}

    # (b) per-half multiplicative scale (closed form, pooled)
    params_b = {}
    for half in ("1H", "2H"):
        obs = sum(p["halves"][half]["total"] for p in tuning_preds)
        exp = sum(p["halves"][half]["pred_total"] for p in tuning_preds)
        s = obs / exp if exp else 1.0
        params_b[half] = {"scale": s}
        print(f"  (b) {half}: scale s={s:.4f} (obs {obs} / exp {exp:.1f})")
    params["b"] = params_b

    # (c) per-half rho (decay-weighted scoreline LL, mirror V2 form A)
    params_c = {}
    for half in ("1H", "2H"):
        best_rho, best_ll = None, None
        for rho in RHO_GRID:
            ll = 0.0
            for p in tuning_preds:
                h = p["halves"][half]
                w = 0.5 ** ((p["cutoff"] - p["date"]).days / 365)
                prob = cell_prob(h["cells"], h["lh"], h["la"], rho, h["yh"], h["ya"])
                ll += w * math.log(max(prob, EPS))
            if best_ll is None or ll > best_ll:
                best_ll, best_rho = ll, rho
        params_c[half] = {"rho": best_rho}
        print(f"  (c) {half}: rho={best_rho:+.2f} (weighted LL {best_ll:.1f})")
    params["c"] = params_c

    # (d) per-half NB size on half totals (V2 r grid)
    params_d = {}
    for half in ("1H", "2H"):
        best_r, best_ll = None, None
        for r in R_GRID:
            ll = sum(nb_logpmf(p["halves"][half]["total"],
                               p["halves"][half]["pred_total"], float(r))
                     for p in tuning_preds)
            if best_ll is None or ll > best_ll:
                best_ll, best_r = ll, r
        params_d[half] = {"r": float(best_r)}
        print(f"  (d) {half}: NB r={best_r} (LL {best_ll:.1f})")
    params["d"] = params_d

    # ---- Tuning evaluation + winner selection ----
    print("\n--- Tuning evaluation (all candidates) ---")
    tuning_eval = {c: evaluate(tuning_preds, c, params[c]) for c in CAND_ORDER}
    base_tuning = tuning_eval["a"]
    tuning_table = {}
    for c in CAND_ORDER:
        ev = tuning_eval[c]
        ok, legs = passes_gate_legs(ev, base_tuning)
        summed = ev["1H"]["pooled_ou_ll"] + ev["2H"]["pooled_ou_ll"]
        max_abs_calib = max(abs(ev[h]["over15_calib_pp"]) for h in ("1H", "2H"))
        tuning_table[c] = {
            "label": CAND_LABEL[c],
            "params": params[c],
            "per_half": ev,
            "gate_legs_vs_baseline": legs,
            "passes_tuning_gate": ok,
            "summed_pooled_ou_ll": summed,
            "max_abs_calib_pp": max_abs_calib,
        }
        for half in ("1H", "2H"):
            e = ev[half]
            print(f"  ({c}) {CAND_LABEL[c]:34s} {half}: LL {e['pooled_ou_ll']:.4f} "
                  f"(delta {legs[half]['ll_delta_vs_baseline']:+.4f})  "
                  f"Over-1.5 calib {e['over15_calib_pp']:+.2f}pp")
        print(f"      -> summed LL {summed:.4f}  max|calib| {max_abs_calib:.2f}pp  "
              f"tuning gate {'PASS' if ok else 'FAIL'}")

    passers = [c for c in CAND_ORDER if tuning_table[c]["passes_tuning_gate"]]
    no_tuning_passer = len(passers) == 0
    if passers:
        # lowest summed pooled OU LL; tie-break simplicity order a,b,c,d
        winner = min(passers,
                     key=lambda c: (round(tuning_table[c]["summed_pooled_ou_ll"], 12),
                                    CAND_ORDER.index(c)))
        selection_reason = (
            f"Among tuning passers {passers}, lowest summed pooled OU LL "
            f"({tuning_table[winner]['summed_pooled_ou_ll']:.4f}); "
            f"tie-break simplicity order a,b,c,d.")
    else:
        winner = min(CAND_ORDER,
                     key=lambda c: (tuning_table[c]["max_abs_calib_pp"],
                                    tuning_table[c]["summed_pooled_ou_ll"],
                                    CAND_ORDER.index(c)))
        selection_reason = (
            "NO TUNING PASSER: no candidate passed both gate legs on tuning; "
            f"winner = smallest max-|calib| across halves "
            f"({tuning_table[winner]['max_abs_calib_pp']:.2f}pp), "
            f"tie-break lower summed LL.")
    print(f"\nWINNER: ({winner}) {CAND_LABEL[winner]}")
    print(f"Selection: {selection_reason}")
    if no_tuning_passer:
        print("FLAG: NO TUNING PASSER")

    # ---- Validation (run ONCE) ----
    print("\n--- Validation (test 2023-08-01..2026-06-30, run once) ---")
    val_base = evaluate(test_preds, "a", params["a"])
    validation_table = []
    base_row = {
        "candidate": "a", "label": CAND_LABEL["a"], "params": params["a"],
        "per_half": val_base,
    }
    validation_table.append(base_row)
    for half in ("1H", "2H"):
        e = val_base[half]
        print(f"  (a) baseline {half}: LL {e['pooled_ou_ll']:.4f}  "
              f"Over-1.5 calib {e['over15_calib_pp']:+.2f}pp  n={e['n']}")
    val_winner = val_base
    if winner != "a":
        val_winner = evaluate(test_preds, winner, params[winner])
        validation_table.append({
            "candidate": winner, "label": CAND_LABEL[winner],
            "params": params[winner], "per_half": val_winner,
        })
        for half in ("1H", "2H"):
            e = val_winner[half]
            print(f"  ({winner}) winner   {half}: LL {e['pooled_ou_ll']:.4f}  "
                  f"Over-1.5 calib {e['over15_calib_pp']:+.2f}pp  n={e['n']}")

    gate_ok, gate_legs = passes_gate_legs(val_winner, val_base)
    print("\n--- Gate verdict (validation, winner vs baseline) ---")
    for half in ("1H", "2H"):
        leg = gate_legs[half]
        print(f"  {half}: LL delta {leg['ll_delta_vs_baseline']:+.4f} "
              f"(limit +0.0005, {'ok' if leg['ll_ok'] else 'FAIL'})  "
              f"Over-1.5 calib {leg['over15_calib_pp']:+.2f}pp "
              f"(|err|<=1.0pp, {'ok' if leg['calib_ok'] else 'FAIL'})")
    gate_text = "PASS" if gate_ok else "FAIL"
    print(f"GATE: {gate_text} -- winner ({winner}) {CAND_LABEL[winner]} "
          f"{'clears' if gate_ok else 'does not clear'} the pre-registered gate "
          f"on the validation window 2023/24-2025/26 (both halves must pass).")
    if no_tuning_passer:
        print("NOTE: NO TUNING PASSER was flagged during winner selection.")

    runtime = time.time() - _START

    # ---- Artifacts ----
    aggregates = {
        "experiment": "halves_goals_v3",
        "harness": {
            "description": (
                "Production-faithful monthly-refit harness: model_v2.DC "
                "exactly as predict_upcoming_refactored.py (7-tuples with "
                "xG from features._load_xg_map() keyed by model_v2.xg_key, "
                "None when absent), HL from v2_config.json, fit on "
                "games[-4000:], DC_FIT_MODE at production default. Monthly "
                "refits at every month-start cutoff 2020-08-01..2026-06-01 "
                "per division on games with date < cutoff; a match is "
                "predicted by the fit at the first day of its month. "
                "Monthly month-start fits exclude same-month earlier "
                "matches, a slight conservatism vs production weekly refits."
            ),
            "data": "all_matches_clean.csv, divisions E0/SP1/I1/D1/F1, dropna HTHG/HTAG; 2H = FT - HT",
            "divisions": TOP5,
            "hl": HL,
            "dc_fit_mode": model_v2.DC_FIT_MODE,
            "monthly_cutoffs": [str(c) for c in cutoffs],
            "n_monthly_fits": len(fits),
            "frozen_shares": {"1H": list(SHARES["1H"]), "2H": list(SHARES["2H"])},
            "baseline": ("thinned lambdas (lh*share_h, la*share_a) with the "
                         "predicting fit's rho applied at thinned scale; "
                         "over-probs via V2 helpers"),
            "lines": list(LINES),
        },
        "tuning_window": {"start": "2020-08-01", "end": "2023-07-31", "n": len(tuning_preds)},
        "validation_window": {"start": "2023-08-01", "end": "2026-06-30", "n": len(test_preds)},
        "ft_level_check": {
            "static_fit_games_before": "2023-08-01",
            "static_cutoff_for_fit": str(static_cutoff),
            "static": ft_static,
            "refit_harness": ft_refit,
        },
        "half_mean_residuals_refit_test": {
            "1H": residuals["1H"], "2H": residuals["2H"],
            "definition": "mean predicted half total - mean actual half goals, test window, refit harness",
            "v2_static_comparison": {"1H": -0.072, "2H": -0.097},
        },
        "half_mean_residuals_refit_tuning": {
            "1H": residuals_tuning["1H"], "2H": residuals_tuning["2H"],
        },
        "tuning_table": tuning_table,
        "winner": {
            "candidate": winner,
            "label": CAND_LABEL[winner],
            "params": params[winner],
            "selection_reason": selection_reason,
            "no_tuning_passer": no_tuning_passer,
            "flag": "NO TUNING PASSER" if no_tuning_passer else None,
        },
        "validation_table": validation_table,
        "gate_verdict": {
            "pass": gate_ok,
            "verdict": gate_text,
            "winner_candidate": winner,
            "per_half_legs": gate_legs,
            "gate_text": (
                "pooled per-half O/U log loss (lines 0.5/1.5/2.5) must NOT "
                "worsen vs the uncorrected thinned baseline by more than "
                "0.0005 in either half, AND per-half Over-1.5 calibration "
                "error must be within ~1pp (|err| <= 1.0pp) in BOTH halves, "
                "evaluated on the validation window 2023/24-2025/26 (top-5)."
            ),
        },
        "runtime_seconds": runtime,
    }
    agg_path = os.path.join(_SCRIPT_DIR, "halves_v3_aggregates.json")
    with open(agg_path, "w", encoding="utf-8") as f:
        json.dump(aggregates, f, indent=2, default=str)
    print(f"\nwrote {agg_path}")

    csv_path = os.path.join(_SCRIPT_DIR, "halves_v3_test_permatch.csv")
    fieldnames = [
        "div", "date", "home", "away",
        "actual_1h_total", "actual_2h_total", "actual_ft_total",
        "baseline_1h_p_over_0_5", "baseline_1h_p_over_1_5", "baseline_1h_p_over_2_5",
        "baseline_2h_p_over_0_5", "baseline_2h_p_over_1_5", "baseline_2h_p_over_2_5",
        "winner_1h_p_over_0_5", "winner_1h_p_over_1_5", "winner_1h_p_over_2_5",
        "winner_2h_p_over_0_5", "winner_2h_p_over_1_5", "winner_2h_p_over_2_5",
        "ft_p_over_2_5_refit", "winner_candidate",
    ]
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for pred in test_preds:
            b1 = candidate_over_probs(pred, "1H", "a", params["a"])
            b2 = candidate_over_probs(pred, "2H", "a", params["a"])
            w1 = candidate_over_probs(pred, "1H", winner, params[winner])
            w2 = candidate_over_probs(pred, "2H", winner, params[winner])
            w.writerow({
                "div": pred["div"], "date": pred["date_iso"],
                "home": pred["home"], "away": pred["away"],
                "actual_1h_total": pred["halves"]["1H"]["total"],
                "actual_2h_total": pred["halves"]["2H"]["total"],
                "actual_ft_total": pred["ft_total"],
                "baseline_1h_p_over_0_5": b1[0.5],
                "baseline_1h_p_over_1_5": b1[1.5],
                "baseline_1h_p_over_2_5": b1[2.5],
                "baseline_2h_p_over_0_5": b2[0.5],
                "baseline_2h_p_over_1_5": b2[1.5],
                "baseline_2h_p_over_2_5": b2[2.5],
                "winner_1h_p_over_0_5": w1[0.5],
                "winner_1h_p_over_1_5": w1[1.5],
                "winner_1h_p_over_2_5": w1[2.5],
                "winner_2h_p_over_0_5": w2[0.5],
                "winner_2h_p_over_1_5": w2[1.5],
                "winner_2h_p_over_2_5": w2[2.5],
                "ft_p_over_2_5_refit": pred["ft_over_refit"],
                "winner_candidate": winner,
            })
    print(f"wrote {csv_path} ({len(test_preds)} rows)")
    print(f"\nruntime {runtime:.1f}s")
    print("DONE")


if __name__ == "__main__":
    main()
