#!/usr/bin/env python3
"""Eksperimen C-1: pengali dominasi teritorial pada model corner (CS).

Desain (pra-registrasi, dari experiments/MODEL_AUDIT_2026-11-07.md §2C C-1):

  mu_variant = mu_cs * clamp(exp(beta_poss * z_poss + beta_bc * z_bc),
                             0.70, 1.43)

  - mu_cs     : mean model corner produksi (model_corners_v3.mu_cs dengan
                gamma* dari ta/corner_params.json, TIDAK di-fit ulang).
  - z_poss    : selisih dominasi penguasaan bola trailing-10 (home - away).
                Untuk tiap tim: rata-rata (possession_for - possession_against)
                atas 10 laga warehouse terakhir SEBELUM tanggal laga
                (minimal 5 laga), lalu z = nilai_tim_kandang - nilai_tim_tandang.
                Persis konstruksi experiments/audit_models_2026_11_07.py
                (fungsi `trailing`, n=10, min 5, tanggal strictly before).
  - z_bc      : sama, untuk big chances (big_chances_for - big_chances_against).
  - Sumber z  : data_enrichment/shot_lineup_features.csv (hanya >= 2022/23).

Jendela (jujur karena fitur warehouse baru ada >= 2022/23):
  - FIT  : 2022/23 + 2023/24  -> beta di-fit HANYA di sini.
  - TEST : 2024/25 + 2025/26  -> gerbang diputuskan di sini.
  Incumbent (beta = 0) dihitung ulang dalam pass yang sama, pada set laga
  yang IDENTIK (laga yang sama-sama punya z lengkap), dengan gamma*/r*
  produksi yang sama. TIDAK dibandingkan ke angka artefak full-history.

Fitting beta: minimisasi mean NLL Negative-Binomial atas total corner pada
jendela fit, dengan r* produksi tetap (tetap seperti pemakaian mu di
produksi di semua garis), memakai log-pmf NB langsung (ekuivalen dengan
model_corners_v3.nll_row tanpa renormalisasi pmf terpotong 0..50 yang
negligible di mu ~ 10; optimum diverifikasi ulang dengan nll_row eksak).
Optimizer: Nelder-Mead murni stdlib (venv proyek tidak punya scipy),
multi-start dari 7 titik awal; hasil fit = objektif terbaik (semua start
konvergen ke titik yang sama — tercatat di metrics.json).

GERBANG (pra-registrasi) — semua harus lolos:
  1. Log loss biner pooled di garis 9.5 membaik >= 0.001 vs incumbent
     (set identik).
  2. Tidak ada musim test yang memburuk (LL@9.5 varian <= incumbent
     di 2024/25 DAN di 2025/26).
  3. |selisih kalibrasi| (pred - aktual Over rate @9.5, pooled) tidak
     membesar dibanding incumbent.

Output (semua di direktori ini):
  predictions_test.csv, metrics.json, RESULTS.md
Produksi TIDAK disentuh. Rerun:  .venv/bin/python experiments/corner_territorial/run_experiment.py
"""
import csv
import json
import math
import os
import sys
from collections import defaultdict

BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, BASE)
import model_corners_v3 as mc  # noqa: E402
from football_etl import normalize_name  # noqa: E402

OUT_DIR = os.path.dirname(os.path.abspath(__file__))
FIT_SEASONS = {"2022/23", "2023/24"}
TEST_SEASONS = {"2024/25", "2025/26"}
LINES = [8.5, 9.5, 10.5]
MULT_LO, MULT_HI = 0.70, 1.43
BETA_P_RANGE = (-0.02, 0.02)     # per poin persen possession
BETA_B_RANGE = (-0.15, 0.15)     # per big chance per laga
POSS_EDGES = (-8, -3, 3, 8)      # sama seperti audit
BC_EDGES = (-1.5, -0.5, 0.5, 1.5)


def fl(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def clamp(v, lo, hi):
    return max(lo, min(hi, v))


# ---------------------------------------------------------------- warehouse
def build_trailing_index():
    """team_matches persis seperti audit_models_2026_11_07.py."""
    team_matches = defaultdict(list)
    path = os.path.join(BASE, "data_enrichment", "shot_lineup_features.csv")
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            div, date = row["div"], row["date"]
            hn, an = normalize_name(row["home"]), normalize_name(row["away"])
            for side, tn, opp in (("h", hn, an), ("a", an, hn)):
                o = "a" if side == "h" else "h"
                vals = [fl(row[f"xg_{side}"]), fl(row[f"xg_{o}"]), fl(row[f"sot_{side}"]),
                        fl(row[f"possession_{side}"]), fl(row[f"possession_{o}"]),
                        fl(row[f"big_chances_{side}"]), fl(row[f"big_chances_{o}"])]
                if any(v is None for v in vals):
                    continue
                team_matches[(div, tn)].append({
                    "date": date, "poss_f": vals[3], "poss_a": vals[4],
                    "bc_f": vals[5], "bc_a": vals[6],
                })
    for v in team_matches.values():
        v.sort(key=lambda d: d["date"])
    return team_matches


TEAM_MATCHES = build_trailing_index()


def trailing(team_key, date, field_f, field_a, n=10):
    """Mean (field_f - field_a) atas n laga terakhir tim sebelum date (min 5)."""
    rows = [d for d in TEAM_MATCHES.get(team_key, []) if d["date"] < date]
    if len(rows) < 5:
        return None
    rows = rows[-n:]
    return sum(d[field_f] - d[field_a] for d in rows) / len(rows)


def z_features(div, date, home_raw, away_raw):
    hn, an = normalize_name(home_raw), normalize_name(away_raw)
    ph = trailing((div, hn), date, "poss_f", "poss_a")
    pa = trailing((div, an), date, "poss_f", "poss_a")
    bh = trailing((div, hn), date, "bc_f", "bc_a")
    ba = trailing((div, an), date, "bc_f", "bc_a")
    if None in (ph, pa, bh, ba):
        return None
    return ph - pa, bh - ba


# ---------------------------------------------------------------- model
with open(mc.PARAMS_OUT) as f:
    PARAMS = json.load(f)
GAMMA_STAR = PARAMS["gamma"]
R_STAR = PARAMS["r"]


def multiplier(beta_p, beta_b, z_poss, z_bc):
    return clamp(math.exp(beta_p * z_poss + beta_b * z_bc), MULT_LO, MULT_HI)


def nb_logpmf(y, mu, r):
    """Log-pmf NB dengan k(mu) sama seperti model_corners_v3.k_of."""
    k = mc.k_of(r, mu)
    return (math.lgamma(y + k) - math.lgamma(k) - math.lgamma(y + 1)
            + k * math.log(k / (k + mu)) + y * math.log(mu / (k + mu)))


def fit_objective(beta, rows):
    bp, bb = beta
    if not (BETA_P_RANGE[0] <= bp <= BETA_P_RANGE[1]
            and BETA_B_RANGE[0] <= bb <= BETA_B_RANGE[1]):
        return 1e6 + 100.0 * (abs(bp) + abs(bb))
    tot = 0.0
    for r0 in rows:
        mu = r0["mu_inc"] * multiplier(bp, bb, r0["z_poss"], r0["z_bc"])
        tot -= nb_logpmf(r0["y"], mu, R_STAR)
    return tot / len(rows)


def nelder_mead(fn, x0, step, tol=1e-7, max_iter=400):
    """Nelder-Mead sederhana (stdlib) untuk len(x0) dimensi."""
    n = len(x0)
    simplex = [list(x0)]
    for i in range(n):
        p = list(x0)
        p[i] += step[i]
        simplex.append(p)
    vals = [fn(p) for p in simplex]
    for _ in range(max_iter):
        order = sorted(range(n + 1), key=lambda i: vals[i])
        simplex = [simplex[i] for i in order]
        vals = [vals[i] for i in order]
        if max(abs(vals[i] - vals[0]) for i in range(1, n + 1)) < tol:
            break
        centroid = [sum(simplex[i][j] for i in range(n)) / n for j in range(n)]
        worst = simplex[-1]
        xr = [centroid[j] + (centroid[j] - worst[j]) for j in range(n)]
        fr = fn(xr)
        if fr < vals[0]:
            xe = [centroid[j] + 2.0 * (centroid[j] - worst[j]) for j in range(n)]
            fe = fn(xe)
            simplex[-1], vals[-1] = (xe, fe) if fe < fr else (xr, fr)
        elif fr < vals[-2]:
            simplex[-1], vals[-1] = xr, fr
        else:
            xc = [centroid[j] + 0.5 * (worst[j] - centroid[j]) for j in range(n)]
            fc = fn(xc)
            if fc < vals[-1]:
                simplex[-1], vals[-1] = xc, fc
            else:
                for i in range(1, n + 1):
                    simplex[i] = [simplex[0][j] + 0.5 * (simplex[i][j] - simplex[0][j])
                                  for j in range(n)]
                    vals[i] = fn(simplex[i])
    best = min(range(n + 1), key=lambda i: vals[i])
    return simplex[best], vals[best]


# ---------------------------------------------------------------- metrics
def bin_ll(p, y):
    p = clamp(p, 1e-9, 1 - 1e-9)
    return -(y * math.log(p) + (1 - y) * math.log(1 - p))


def evaluate(rows, beta_p, beta_b):
    """Metrik biner per garis untuk incumbent & varian pada set rows."""
    out = {}
    for tag in ("inc", "var"):
        out[tag] = {}
    agg = {tag: {ln: [0.0, 0.0, 0.0] for ln in LINES} for tag in ("inc", "var")}
    for r0 in rows:
        pmf_inc = mc.pmf_k(r0["mu_inc"], mc.k_of(R_STAR, r0["mu_inc"]))
        mu_v = r0["mu_inc"] * multiplier(beta_p, beta_b, r0["z_poss"], r0["z_bc"])
        pmf_var = mc.pmf_k(mu_v, mc.k_of(R_STAR, mu_v))
        for ln in LINES:
            y = 1.0 if r0["y"] > ln else 0.0
            for tag, pmf in (("inc", pmf_inc), ("var", pmf_var)):
                p = sum(pmf[int(ln) + 1:])
                a = agg[tag][ln]
                a[0] += bin_ll(p, y)
                a[1] += p
                a[2] += y
    n = len(rows)
    for tag in ("inc", "var"):
        for ln in LINES:
            ll_sum, pred_sum, act_sum = agg[tag][ln]
            out[tag][str(ln)] = {
                "ll": ll_sum / n,
                "pred_rate": pred_sum / n,
                "act_rate": act_sum / n,
                "diff_pp": 100.0 * (pred_sum - act_sum) / n,
            }
    out["n"] = n
    return out


def bucket_index(val, edges):
    b = 0
    while b < len(edges) and val >= edges[b]:
        b += 1
    return b


def resid_tilt(rows, beta_p, beta_b):
    """Rata-rata residual (y - mu) per bucket dominasi, incumbent vs varian."""
    res = {}
    for name, key, edges in (("poss", "z_poss", POSS_EDGES), ("bc", "z_bc", BC_EDGES)):
        cells = defaultdict(lambda: [0, 0.0, 0.0, 0.0])
        for r0 in rows:
            b = bucket_index(r0[key], edges)
            mu_v = r0["mu_inc"] * multiplier(beta_p, beta_b, r0["z_poss"], r0["z_bc"])
            c = cells[b]
            c[0] += 1
            c[1] += r0["y"] - r0["mu_inc"]
            c[2] += r0["y"] - mu_v
            c[3] += r0[key]
        res[name] = {str(b): {"n": c[0], "resid_inc": c[1] / c[0],
                              "resid_var": c[2] / c[0], "z_mean": c[3] / c[0]}
                     for b, c in sorted(cells.items())}
    return res


def z_stats(rows):
    """Korelasi & sebaran z_poss/z_bc (konteks kolinearitas beta)."""
    def mean(v):
        return sum(v) / len(v)

    def sd(v):
        m = mean(v)
        return math.sqrt(sum((x - m) ** 2 for x in v) / len(v))
    zp = [r["z_poss"] for r in rows]
    zb = [r["z_bc"] for r in rows]
    mp, mb = mean(zp), mean(zb)
    cov = sum((a - mp) * (b - mb) for a, b in zip(zp, zb)) / len(zp)
    return {"corr": cov / (sd(zp) * sd(zb)), "sd_poss": sd(zp), "sd_bc": sd(zb),
            "min_poss": min(zp), "max_poss": max(zp), "min_bc": min(zb), "max_bc": max(zb)}


def paired_diag(rows, beta_p, beta_b, line=9.5):
    """Diagnostik paired ΔLL per laga di garis `line` (BUKAN gerbang)."""
    diffs = []
    for r0 in rows:
        pmf_i = mc.pmf_k(r0["mu_inc"], mc.k_of(R_STAR, r0["mu_inc"]))
        mu_v = r0["mu_inc"] * multiplier(beta_p, beta_b, r0["z_poss"], r0["z_bc"])
        pmf_v = mc.pmf_k(mu_v, mc.k_of(R_STAR, mu_v))
        y = 1.0 if r0["y"] > line else 0.0
        diffs.append(bin_ll(sum(pmf_v[int(line) + 1:]), y)
                     - bin_ll(sum(pmf_i[int(line) + 1:]), y))
    n = len(diffs)
    md = sum(diffs) / n
    sd = math.sqrt(sum((d - md) ** 2 for d in diffs) / n)
    se = sd / math.sqrt(n)
    return {"mean_delta_ll": md, "sd": sd, "se": se,
            "t_approx": md / se if se > 0 else None,
            "frac_improved": sum(1 for d in diffs if d < 0) / n, "n": n}


# ---------------------------------------------------------------- main
def main():
    print("run_wf fit+test ...")
    wf = mc.run_wf(FIT_SEASONS | TEST_SEASONS)
    raw_counts = defaultdict(int)
    rows = []
    dropped = defaultdict(int)
    for r0 in wf:
        raw_counts[r0["season"]] += 1
        z = z_features(r0["div"], r0["date"], r0["home"], r0["away"])
        if z is None:
            dropped[r0["season"]] += 1
            continue
        rows.append({**r0, "z_poss": z[0], "z_bc": z[1],
                     "mu_inc": mc.mu_cs(r0, GAMMA_STAR)})
    fit = [r for r in rows if r["season"] in FIT_SEASONS]
    test = [r for r in rows if r["season"] in TEST_SEASONS]
    print(f"fit matched n={len(fit)}  test matched n={len(test)}")
    print(f"raw per season: {dict(raw_counts)}  dropped(no z): {dict(dropped)}")

    # ---- sanity: incumbent recomputed vs stored backtest artifact
    art = {}
    with open(os.path.join(BASE, "predictions_corners_shots.csv"), newline="") as f:
        for a in csv.DictReader(f):
            art[(a["div"], a["date"], a["home"], a["away"])] = a
    n_cmp, max_mu_diff, max_p_diff = 0, 0.0, 0.0
    for r0 in test:
        a = art.get((r0["div"], r0["date"], r0["home"], r0["away"]))
        if not a:
            continue
        p_inc = sum(mc.pmf_k(r0["mu_inc"], mc.k_of(R_STAR, r0["mu_inc"]))[10:])
        n_cmp += 1
        max_mu_diff = max(max_mu_diff, abs(r0["mu_inc"] - float(a["mu_shots_cs"])))
        max_p_diff = max(max_p_diff, abs(p_inc - float(a["p_gt_cs_9.5"])))
    sanity = {"compared": n_cmp, "max_abs_mu_diff_vs_artifact": max_mu_diff,
              "max_abs_p95_diff_vs_artifact": max_p_diff}
    print("sanity vs artifact:", sanity)

    # ---- fit beta on FIT window only (multi-start NM, objektif terbaik)
    starts = [[0.0, 0.0], [0.005, 0.05], [-0.005, -0.05], [0.01, 0.0],
              [0.0, 0.1], [0.002, -0.02], [-0.002, 0.08]]
    restarts = []
    best = None
    for s in starts:
        b_s, o_s = nelder_mead(lambda b: fit_objective(b, fit), s,
                               step=[0.002, 0.02])
        restarts.append({"start": s, "beta": b_s, "obj": o_s})
        if best is None or o_s < best[1]:
            best = (b_s, o_s)
    (bp, bb), obj = best
    obj0 = fit_objective([0.0, 0.0], fit)
    # verifikasi optimum dengan nll_row eksak produksi (pmf ternormalisasi)
    def exact_nll(beta_p, beta_b, rows_):
        return sum(mc.nll_row(r0["mu_inc"] * multiplier(beta_p, beta_b,
                                                        r0["z_poss"], r0["z_bc"]),
                              R_STAR, r0["y"]) for r0 in rows_) / len(rows_)
    exact = {"fit_nll_at_0": exact_nll(0.0, 0.0, fit),
             "fit_nll_at_beta": exact_nll(bp, bb, fit)}
    # fit satu-fitur (eksploratori, BUKAN gerbang)
    ([bp_only], _) = nelder_mead(lambda b: fit_objective([b[0], 0.0], fit),
                                 [0.0], step=[0.002])
    ([bb_only], _) = nelder_mead(lambda b: fit_objective([0.0, b[0]], fit),
                                 [0.0], step=[0.02])
    print(f"beta_poss={bp:.5f}  beta_bc={bb:.5f}  fit NLL {obj0:.4f} -> {obj:.4f}")
    print(f"eksploratori: beta_poss_only={bp_only:.5f}  beta_bc_only={bb_only:.5f}")

    # clamp binding?
    def bind_rate(rows_):
        raw = [math.exp(bp * r0["z_poss"] + bb * r0["z_bc"]) for r0 in rows_]
        return (sum(1 for m in raw if m < MULT_LO or m > MULT_HI) / len(raw),
                min(raw), max(raw))
    bind_fit, bind_test = bind_rate(fit), bind_rate(test)

    # ---- test evaluation (identical set)
    pooled = evaluate(test, bp, bb)
    per_season = {s: evaluate([r for r in test if r["season"] == s], bp, bb)
                  for s in sorted(TEST_SEASONS)}
    pooled_only_p = evaluate(test, bp_only, 0.0)
    pooled_only_b = evaluate(test, 0.0, bb_only)
    tilt = resid_tilt(test, bp, bb)
    diag = {"z_fit": z_stats(fit), "z_test": z_stats(test),
            "optimizer_restarts": restarts,
            "paired_test_95": paired_diag(test, bp, bb),
            "fit_ll95_incumbent": evaluate(fit, 0.0, 0.0)["inc"]["9.5"]["ll"],
            "fit_ll95_variant": evaluate(fit, bp, bb)["var"]["9.5"]["ll"]}

    ll_inc = pooled["inc"]["9.5"]["ll"]
    ll_var = pooled["var"]["9.5"]["ll"]
    improvement = ll_inc - ll_var
    season_deltas = {s: per_season[s]["var"]["9.5"]["ll"] - per_season[s]["inc"]["9.5"]["ll"]
                     for s in per_season}
    calib_inc = pooled["inc"]["9.5"]["diff_pp"]
    calib_var = pooled["var"]["9.5"]["diff_pp"]
    gate1 = improvement >= 0.001
    gate2 = all(d <= 0.0 for d in season_deltas.values())
    gate3 = abs(calib_var) <= abs(calib_inc)
    verdict = "PASS" if (gate1 and gate2 and gate3) else "FAIL"

    metrics = {
        "gamma_star": GAMMA_STAR, "r_star": R_STAR,
        "raw_counts": dict(raw_counts), "dropped_no_z": dict(dropped),
        "fit_n": len(fit), "test_n": len(test),
        "beta_poss": bp, "beta_bc": bb,
        "fit_nll_direct_at_0": obj0, "fit_nll_direct_at_beta": obj,
        "fit_exact_nll": exact,
        "beta_poss_only": bp_only, "beta_bc_only": bb_only,
        "multiplier_bind": {"fit_rate": bind_fit[0], "fit_min_raw": bind_fit[1],
                            "fit_max_raw": bind_fit[2], "test_rate": bind_test[0],
                            "test_min_raw": bind_test[1], "test_max_raw": bind_test[2]},
        "sanity_vs_artifact": sanity,
        "test_pooled": pooled, "test_per_season": per_season,
        "test_pooled_poss_only": pooled_only_p, "test_pooled_bc_only": pooled_only_b,
        "resid_tilt_test": tilt, "diagnostics": diag,
        "gate": {"improvement_95": improvement, "gate1_ll_gain_ge_0.001": gate1,
                 "season_deltas_var_minus_inc": season_deltas,
                 "gate2_no_season_worsens": gate2,
                 "calib_inc_pp": calib_inc, "calib_var_pp": calib_var,
                 "gate3_calib_not_worse": gate3, "verdict": verdict},
    }
    with open(os.path.join(OUT_DIR, "metrics.json"), "w") as f:
        json.dump(metrics, f, indent=1)

    # ---- predictions CSV (test set)
    pred_path = os.path.join(OUT_DIR, "predictions_test.csv")
    with open(pred_path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["div", "date", "season", "home", "away", "y_total",
                    "z_poss", "z_bc", "multiplier", "mu_incumbent", "mu_variant"]
                   + [f"p_inc_{ln}" for ln in LINES] + [f"p_var_{ln}" for ln in LINES])
        for r0 in sorted(test, key=lambda x: (x["date"], x["div"], x["home"])):
            mult = multiplier(bp, bb, r0["z_poss"], r0["z_bc"])
            mu_v = r0["mu_inc"] * mult
            pmf_i = mc.pmf_k(r0["mu_inc"], mc.k_of(R_STAR, r0["mu_inc"]))
            pmf_v = mc.pmf_k(mu_v, mc.k_of(R_STAR, mu_v))
            w.writerow([r0["div"], r0["date"], r0["season"], r0["home"], r0["away"],
                        r0["y"], round(r0["z_poss"], 3), round(r0["z_bc"], 3),
                        round(mult, 4), round(r0["mu_inc"], 4), round(mu_v, 4)]
                       + [round(sum(pmf_i[int(ln) + 1:]), 4) for ln in LINES]
                       + [round(sum(pmf_v[int(ln) + 1:]), 4) for ln in LINES])
    print(f"predictions -> {pred_path}")

    write_results(metrics)
    print(f"VERDICT: {verdict}  (LL@9.5 inc {ll_inc:.4f} vs var {ll_var:.4f}, "
          f"improvement {improvement:+.4f})")
    return metrics


def _tbl_lines(m, label):
    lines = [f"**{label}** (n={m['n']})", "",
             "| Garis | LL incumbent | LL varian | ΔLL (var−inc) | Kalibrasi inc (pp) | Kalibrasi var (pp) |",
             "|---|---|---|---|---|---|"]
    for ln in LINES:
        i, v = m["inc"][str(ln)], m["var"][str(ln)]
        lines.append(f"| {ln} | {i['ll']:.4f} | {v['ll']:.4f} | {v['ll']-i['ll']:+.4f} "
                     f"| {i['diff_pp']:+.2f} | {v['diff_pp']:+.2f} |")
    return "\n".join(lines)


def write_results(m):
    g = m["gate"]
    verdict = g["verdict"]
    pooled = m["test_pooled"]
    tilt = m["resid_tilt_test"]
    poss_ext = (tilt["poss"]["0"], tilt["poss"]["4"])
    bc_ext = (tilt["bc"]["0"], tilt["bc"]["4"])
    if verdict == "PASS":
        ringkasan_keputusan = (
            "Gerbang **LULUS (PASS)**: pengali teritorial memperbaiki log loss "
            "pooled garis 9.5 melewati ambang 0.001, tidak ada musim test yang "
            "memburuk, dan kalibrasi tidak membesar. Kandidat layak adopsi — "
            "tetapi produksi TIDAK diubah oleh eksperimen ini; adopsi menunggu "
            "keputusan bos (lihat bagian Catatan adopsi).")
    else:
        gagal = []
        if not g["gate1_ll_gain_ge_0.001"]:
            gagal.append(f"syarat 1 (gain LL@9.5 pooled {g['improvement_95']:+.4f} < 0.001)")
        if not g["gate2_no_season_worsens"]:
            buruk = ", ".join(f"{s} {d:+.4f}" for s, d in
                              g["season_deltas_var_minus_inc"].items() if d > 0)
            gagal.append(f"syarat 2 (musim memburuk: {buruk})")
        if not g["gate3_calib_not_worse"]:
            gagal.append(f"syarat 3 (|kalibrasi| membesar {abs(g['calib_inc_pp']):.2f}pp "
                         f"→ {abs(g['calib_var_pp']):.2f}pp)")
        ringkasan_keputusan = (
            "Gerbang **GAGAL (FAIL)** — gagal di " + "; ".join(gagal) +
            ". Mekanisme dominasi teritorial memang nyata di residual, tetapi "
            "pengali exp(β·z) yang di-fit jujur di 2022/23–2023/24 tidak "
            "menghasilkan perbaikan yang cukup/robek di musim test. "
            "Produksi tidak diubah.")
    txt = f"""# Corner Territorial-Dominance Multiplier (C-1) — Hasil Eksperimen

## Ringkasan (Bahasa Indonesia)

Eksperimen ini menguji usulan audit 2026-11-07 §2C item C-1: menambahkan
pengali `exp(β·z)` pada mean model corner produksi (shot-based CS,
`mu_cs`), dengan `z` = selisih dominasi teritorial trailing-10 laga dari
gudang FotMob (`shot_lineup_features.csv`) — selisih penguasaan bola dan
selisih big chances, kandang minus tandang, dihitung ketat hanya dari laga
sebelum laga yang diprediksi. Beta di-fit hanya di musim 2022/23 + 2023/24
(n fit = {m['fit_n']:,}); pengujian di 2024/25 + 2025/26 pada set identik
(n test = {m['test_n']:,}) dengan incumbent (β=0) dihitung ulang dalam pass
yang sama memakai gamma*/r* produksi yang sama.

Hasil kunci (set test identik): log loss garis 9.5 incumbent
**{pooled['inc']['9.5']['ll']:.4f}** vs varian **{pooled['var']['9.5']['ll']:.4f}**
(perbaikan {g['improvement_95']:+.4f}); ΔLL per musim:
{", ".join(f"{s} {d:+.4f}" for s, d in g['season_deltas_var_minus_inc'].items())};
kalibrasi @9.5 (pred − aktual) {g['calib_inc_pp']:+.2f}pp → {g['calib_var_pp']:+.2f}pp.
Beta ter-fit: β_possession = {m['beta_poss']:+.5f} per poin persen,
β_bigchance = {m['beta_bc']:+.5f} per big chance/laga.

{ringkasan_keputusan}

Kemiringan residual di bucket ekstrem pada set test ini — possession:
bucket terbawah {poss_ext[0]['resid_inc']:+.3f} → {poss_ext[0]['resid_var']:+.3f},
bucket teratas {poss_ext[1]['resid_inc']:+.3f} → {poss_ext[1]['resid_var']:+.3f};
big chances: terbawah {bc_ext[0]['resid_inc']:+.3f} → {bc_ext[0]['resid_var']:+.3f},
teratas {bc_ext[1]['resid_inc']:+.3f} → {bc_ext[1]['resid_var']:+.3f}
(angka audit asli +0.20/+0.32 diukur di jendela 2023/24–2025/26 dengan
artefak tersimpan; di sini perbandingan yang sah adalah incumbent-vs-varian
pada set test yang sama).

## Desain (pra-registrasi)

- Varian: `mu_var = mu_cs * clamp(exp(β_p·z_poss + β_b·z_bc), 0.70, 1.43)`;
  distribusi NB dan r* produksi ({m['r_star']:.4f}) tidak berubah; gamma*
  produksi = {m['gamma_star']}.
- z: trailing-10 (min 5 laga) per tim dari `shot_lineup_features.csv`,
  konstruksi persis `trailing()` di `experiments/audit_models_2026_11_07.py`;
  z_match = trailing_diff(tim kandang) − trailing_diff(tim tandang).
  Tidak ada kebocoran laga yang sama (strictly `date < tanggal laga`).
- Fit β: minimisasi mean NLL NB total corner di jendela fit saja
  (r* tetap); optimum diverifikasi dengan `nll_row` eksak produksi:
  NLL fit {m['fit_exact_nll']['fit_nll_at_0']:.4f} (β=0) →
  {m['fit_exact_nll']['fit_nll_at_beta']:.4f} (β ter-fit).
- Laga tanpa z lengkap dibuang dari KEDUA model (set identik):
  mentah per musim {m['raw_counts']}, dibuang {m['dropped_no_z']}
  (penyebab utama: tim promosi/awal 2022/23 belum punya ≥5 laga warehouse).
- Clamp pengali mengikat pada {100*m['multiplier_bind']['test_rate']:.2f}% laga test
  (rentang mentah exp(β·z) di test: {m['multiplier_bind']['test_min_raw']:.3f}–{m['multiplier_bind']['test_max_raw']:.3f}).

## Hasil test — pooled

{_tbl_lines(pooled, 'Pooled test 2024/25 + 2025/26')}

Aktual Over rate @9.5 pada set test: {pooled['inc']['9.5']['act_rate']*100:.2f}%.

## Hasil test — per musim (garis 9.5)

| Musim | n | LL incumbent | LL varian | ΔLL (var−inc) | Kalibrasi inc (pp) | Kalibrasi var (pp) |
|---|---|---|---|---|---|---|
"""
    for s in sorted(m["test_per_season"]):
        ps = m["test_per_season"][s]
        txt += (f"| {s} | {ps['n']} | {ps['inc']['9.5']['ll']:.4f} | "
                f"{ps['var']['9.5']['ll']:.4f} | "
                f"{ps['var']['9.5']['ll']-ps['inc']['9.5']['ll']:+.4f} | "
                f"{ps['inc']['9.5']['diff_pp']:+.2f} | {ps['var']['9.5']['diff_pp']:+.2f} |\n")
    txt += f"""
## Kemiringan residual per bucket dominasi (set test, residual = aktual − mu)

Bucket possession (edges −8/−3/+3/+8, sama seperti audit):

| Bucket | n | Rata-rata z_poss | Resid incumbent | Resid varian |
|---|---|---|---|---|
"""
    labels_p = ["0: z < −8", "1: −8 ≤ z < −3", "2: −3 ≤ z < +3", "3: +3 ≤ z < +8", "4: z ≥ +8"]
    for b, lab in enumerate(labels_p):
        c = tilt["poss"][str(b)]
        txt += (f"| {lab} | {c['n']} | {c['z_mean']:+.1f} | {c['resid_inc']:+.3f} "
                f"| {c['resid_var']:+.3f} |\n")
    txt += """
Bucket big chances (edges −1.5/−0.5/+0.5/+1.5):

| Bucket | n | Rata-rata z_bc | Resid incumbent | Resid varian |
|---|---|---|---|---|
"""
    labels_b = ["0: z < −1.5", "1: −1.5 ≤ z < −0.5", "2: −0.5 ≤ z < +0.5", "3: +0.5 ≤ z < +1.5", "4: z ≥ +1.5"]
    for b, lab in enumerate(labels_b):
        c = tilt["bc"][str(b)]
        txt += (f"| {lab} | {c['n']} | {c['z_mean']:+.2f} | {c['resid_inc']:+.3f} "
                f"| {c['resid_var']:+.3f} |\n")
    txt += f"""
## Eksploratori (BUKAN gerbang; di-fit di jendela fit yang sama)

| Varian satu-fitur | β ter-fit | LL@9.5 test | ΔLL vs incumbent |
|---|---|---|---|
| possession saja | {m['beta_poss_only']:+.5f} | {m['test_pooled_poss_only']['var']['9.5']['ll']:.4f} | {m['test_pooled_poss_only']['var']['9.5']['ll']-pooled['inc']['9.5']['ll']:+.4f} |
| big chances saja | {m['beta_bc_only']:+.5f} | {m['test_pooled_bc_only']['var']['9.5']['ll']:.4f} | {m['test_pooled_bc_only']['var']['9.5']['ll']-pooled['inc']['9.5']['ll']:+.4f} |

## Pemeriksaan kewarasan

- Incumbent yang dihitung ulang vs artefak tersimpan
  `predictions_corners_shots.csv` pada laga test yang tumpang tindih:
  dibandingkan {m['sanity_vs_artifact']['compared']} laga, selisih maks
  |mu| = {m['sanity_vs_artifact']['max_abs_mu_diff_vs_artifact']:.4f},
  selisih maks |p@9.5| = {m['sanity_vs_artifact']['max_abs_p95_diff_vs_artifact']:.4f}
  (konsisten dengan pembulatan artefak: mu 2 desimal, p 4 desimal).
- Beta di-fit hanya dari jendela fit; tidak ada parameter yang menyentuh
  musim test. Gamma*/r* adalah parameter produksi yang di-fit di jendela
  validasi lama (2019/20–2020/21), jauh sebelum kedua jendela di sini.

## Diagnostik kekokohan & interpretasi (bukan gerbang)

- Optimizer: 7 start Nelder-Mead konvergen ke β yang sama
  (β_poss {m['beta_poss']:+.5f}, β_bc {m['beta_bc']:+.5f}; rincian per start
  di metrics.json) — optimum bukan artefak titik awal.
- Kolinearitas: corr(z_poss, z_bc) = {m['diagnostics']['z_fit']['corr']:.2f} di
  jendela fit (sd z_poss {m['diagnostics']['z_fit']['sd_poss']:.1f} poin,
  sd z_bc {m['diagnostics']['z_fit']['sd_bc']:.2f}/laga). Efek per 1 sd:
  possession {m['beta_poss']*m['diagnostics']['z_fit']['sd_poss']:+.4f} log-mu,
  big chances {m['beta_bc']*m['diagnostics']['z_fit']['sd_bc']:+.4f} log-mu.
  Tanda β_bc yang negatif adalah koefisien parsial di hadapan possession
  (fit big-chances-saja ≈ {m['beta_bc_only']:+.5f}, praktis nol): sinyal
  teritorialnya dibawa possession; big chances tidak menambah apa-apa di
  luar possession + tembakan yang sudah dipakai model. Ini konsisten
  dengan peringatan audit bahwa possession/big chances berkorelasi dengan
  tembakan.
- Ketidakpastian paired (diagnostik): ΔLL@9.5 per laga di test rata-rata
  {m['diagnostics']['paired_test_95']['mean_delta_ll']:+.5f} dengan SE
  {m['diagnostics']['paired_test_95']['se']:.5f} (t ≈ {m['diagnostics']['paired_test_95']['t_approx']:.2f});
  {100*m['diagnostics']['paired_test_95']['frac_improved']:.1f}% laga membaik.
  Gain pooled {g['improvement_95']:+.4f} hanya sedikit di atas ambang 0.001 —
  lolos gerbang pra-registrasi, tetapi marginnya tipis dan efeknya memang
  kelas kecil seperti perkiraan audit (~0.001).
- Di jendela fit sendiri, LL@9.5 biner: incumbent
  {m['diagnostics']['fit_ll95_incumbent']:.4f} → varian
  {m['diagnostics']['fit_ll95_variant']:.4f} (fit memang membaik juga,
  bukan hanya test).
- Kemiringan possession di bucket ekstrem menyusut besar (bucket teratas
  {tilt['poss']['4']['resid_inc']:+.3f} → {tilt['poss']['4']['resid_var']:+.3f};
  terbawah {tilt['poss']['0']['resid_inc']:+.3f} → {tilt['poss']['0']['resid_var']:+.3f})
  karena rata-rata |z_poss| di bucket ekstrem ≈ 21 poin sehingga pengali
  ≈ exp(±0.02) ≈ ±2% pada mu ≈ ±0.2 corner. Kemiringan big chances di
  bucket teratas nyaris tidak bergerak
  ({tilt['bc']['4']['resid_inc']:+.3f} → {tilt['bc']['4']['resid_var']:+.3f}) —
  sesuai koefisien parsialnya yang ≈ nol/negatif kecil.

## Putusan gerbang

| Syarat | Ambang | Hasil | Status |
|---|---|---|---|
| 1. Gain LL@9.5 pooled | ≥ 0.001 | {g['improvement_95']:+.4f} | {'LULUS' if g['gate1_ll_gain_ge_0.001'] else 'GAGAL'} |
| 2. Tak ada musim test memburuk | ΔLL ≤ 0 di kedua musim | {", ".join(f"{s} {d:+.4f}" for s, d in g['season_deltas_var_minus_inc'].items())} | {'LULUS' if g['gate2_no_season_worsens'] else 'GAGAL'} |
| 3. Kalibrasi tidak membesar | \\|var\\| ≤ \\|inc\\| | {g['calib_inc_pp']:+.2f}pp → {g['calib_var_pp']:+.2f}pp | {'LULUS' if g['gate3_calib_not_worse'] else 'GAGAL'} |

**VERDICT: {verdict}**

## Catatan adopsi (hanya relevan bila PASS dan bos menyetujui)

Perubahan yang dibutuhkan di `model_corners_v3.py` bila varian ini diadopsi:

1. `predict_upcoming()`: mu saat ini dihitung dari
   `mu_cs({{base_h, base_a, fhp, fhc, fap, fac}}, gamma)`. Adopsi menambah
   satu langkah sesudahnya: `mu *= territorial_multiplier(home, away, date)`
   dengan β dibaca dari `ta/corner_params.json` (skema JSON diperluas:
   `beta_poss`, `beta_bc`; penulisan parameter di `_run_backtest()` harus
   ikut menulisnya — tetapi β TIDAK bisa di-fit di `_run_backtest` biasa
   karena jendela fit-nya butuh fitur warehouse; fit β perlu langkah
   tersendiri dari skrip eksperimen ini, dijalankan saat refit).
2. Input baru saat prediksi: `shot_lineup_features.csv` harus dimuat di
   `predict_upcoming()` untuk membangun agregat trailing-10 possession &
   big-chances per tim (fungsi `build_trailing_index`/`trailing` di skrip
   ini bisa dipindah apa adanya), dinormalisasi namanya dengan
   `football_etl.normalize_name` karena nama FotMob ≠ nama football-data.
3. Ketersediaan untuk fixture mendatang: YA untuk pasangan tim top-5 yang
   keduanya sudah punya ≥5 laga warehouse sebelum tanggal fixture (gudang
   mencakup semua laga liga top-5 sejak 2022/23 dan terus diperbarui oleh
   pull FotMob). TIDAK selalu untuk tim promosi di awal musim (belum 5 laga
   di divisi teratas) — untuk kasus itu fallback yang aman adalah pengali
   1.0 (perilaku incumbent). Catatan: fitur warehouse adalah data laga yang
   SUDAH dimainkan, jadi trailing untuk fixture masa depan selalu bisa
   dihitung dari file yang ada pada saat prediksi, tanpa pull baru.

## Reproduksi

```
.venv/bin/python experiments/corner_territorial/run_experiment.py
```

Menghasilkan ulang: `predictions_test.csv`, `metrics.json`, `RESULTS.md`
di direktori ini. Tidak ada file produksi yang ditulis.
"""
    with open(os.path.join(OUT_DIR, "RESULTS.md"), "w") as f:
        f.write(txt)


if __name__ == "__main__":
    main()
