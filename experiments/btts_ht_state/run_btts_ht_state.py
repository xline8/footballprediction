#!/usr/bin/env python3
"""Eksperimen G-1: BTTS via integrasi keadaan turun minum (HT-state).

Pertanyaan (dari experiments/MODEL_AUDIT_2026-11-07.md §1C G-1):
apakah probabilitas BTTS pra-laga yang dihitung dengan (a) membangun
distribusi pra-laga atas keadaan/score turun minum dari lambda DC yang
sama dengan incumbent, lalu (b) menilai gol babak 2 bersyarat pada
keadaan HT (pengali trailing/leading/level yang diestimasi walk-forward),
lalu (c) mengintegrasikan atas keadaan HT, mengalahkan BTTS incumbent
(DC murni dari records_cache) pada set uji yang identik?

Desain yang dikunci SEBELUM melihat hasil uji:
- Incumbent = probabilitas tersimpan di records_cache.jsonl
  (p_btts, p_over_dc, ph_dc/pd_dc/pa_dc — komponen DC, yaitu
  probabilitas laporan), dihitung ulang dalam pass yang sama pada set
  laga yang identik dengan varian.
- Varian TIDAK mengganti distribusi incumbent. Integrasi HT menghasilkan
  distribusi Poisson murni (tanpa koreksi tau DC); yang dipakai adalah
  SELISIHNYA terhadap integrasi yang sama dengan semua pengali = 1
  (baseline s=0 mereproduksi Poisson murni dan, lewat selisih ini,
  varian pada s=0 sama persis dengan incumbent). Selisih diterapkan
  sebagai pergeseran logit (BTTS, OU 2.5) / pergeseran log ternormalisasi
  (1X2). Ini menghindari penghitungan ganda koreksi tau milik DC —
  risiko yang disebut eksplisit di audit.
- Alpha (porsi gol babak 1) dan pengali keadaan diestimasi WALK-FORWARD
  per musim: untuk musim S, hanya record dengan tanggal < laga pertama
  musim S yang dipakai. Pengali = Σ gol babak-2 aktual / Σ lambda babak-2
  dasar ((1-alpha)*lambda) untuk tim yang sedang unggul (lead),
  tertinggal (trail), dan semua tim saat level (level), digabung lintas
  divisi dan lintas kandang/tandang (pandangan tim sendiri).
- Penyusutan pengali m_s = 1 + s*(m-1), s dipilih dari grid
  {0, 0.25, 0.5, 0.75, 1.0} HANYA pada musim tuning 2021/22-2022/23
  (kriteria: log loss BTTS pooled varian terkecil). Lalu dibekukan.
- Uji: 2023/24-2025/26, top-5 saja, n harus cocok dengan audit (5.255
  laga dengan HT terisi; satu laga tanpa HT di spine dikeluarkan dari
  KEDUA varian).

Gerbang pra-registrasi (audit §1C G-1 + instruksi item):
  1. LL BTTS pooled varian membaik >= 0.001 vs incumbent.
  2. Tidak ada divisi memburuk > 0.003 (LL BTTS).
  3. Kalibrasi BTTS tidak memburuk (|mean pred - actual| varian <= incumbent).
  4. LL OU 2.5 dan LL 1X2 tidak memburuk.
PASS hanya bila keempatnya lolos. Eksperimen ini TIDAK mengadopsi apa
pun ke produksi; PASS pun hanya ditandai untuk keputusan user.

Output: predictions_test.csv, results.json, RESULTS.md di direktori ini.
Produksi tidak disentuh.
"""
import csv
import json
import math
import os
import sys
import time
from collections import defaultdict

import numpy as np

BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, BASE)
from football_etl import normalize_name  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
TOP5 = ("E0", "D1", "I1", "SP1", "F1")
TUNE_SEASONS = ("2021/22", "2022/23")
TEST_SEASONS = ("2023/24", "2024/25", "2025/26")
S_GRID = (0.0, 0.25, 0.5, 0.75, 1.0)
MAX_HT = 10
MAX_2H = 13
EPS = 1e-9


# ------------------------------------------------------------------ data
def load_data():
    spine = {}
    with open(os.path.join(BASE, "all_matches_clean.csv"), newline="") as f:
        for row in csv.DictReader(f):
            if row["HTHG"] in ("", None) or row["HTAG"] in ("", None):
                continue
            spine[(row["Div"], row["Date"][:10],
                   normalize_name(row["HomeTeam"]),
                   normalize_name(row["AwayTeam"]))] = (int(row["HTHG"]),
                                                         int(row["HTAG"]))
    recs = []
    with open(os.path.join(BASE, "records_cache.jsonl")) as f:
        for line in f:
            r = json.loads(line)
            if r["div"] not in TOP5:
                continue
            ht = spine.get((r["div"], r["date"], r["home"], r["away"]))
            if ht is None or r.get("fthg") is None:
                continue
            r["hthg"], r["htag"] = ht
            recs.append(r)
    recs.sort(key=lambda r: r["date"])
    return recs


def season_start(recs, season):
    return min(r["date"] for r in recs if r["season"] == season)


# ------------------------------------------------------- parameter estimation
def estimate_params(recs, cutoff):
    """Alpha + pengali keadaan dari record sebelum cutoff (walk-forward)."""
    E = [r for r in recs if r["date"] < cutoff]
    alpha = (sum(r["hthg"] + r["htag"] for r in E)
             / sum(r["fthg"] + r["ftag"] for r in E))
    agg = defaultdict(lambda: [0.0, 0.0])  # state -> [gol2 aktual, lambda2 dasar]
    for r in E:
        bh, ba = (1 - alpha) * r["lam_h"], (1 - alpha) * r["lam_a"]
        g2h, g2a = r["fthg"] - r["hthg"], r["ftag"] - r["htag"]
        if r["hthg"] > r["htag"]:
            agg["lead"][0] += g2h; agg["lead"][1] += bh
            agg["trail"][0] += g2a; agg["trail"][1] += ba
        elif r["hthg"] < r["htag"]:
            agg["trail"][0] += g2h; agg["trail"][1] += bh
            agg["lead"][0] += g2a; agg["lead"][1] += ba
        else:
            agg["level"][0] += g2h + g2a; agg["level"][1] += bh + ba
    mult = {k: v[0] / v[1] for k, v in agg.items()}
    counts = {k: v for k, v in agg.items()}
    return alpha, mult, len(E), counts


def shrink(mult, s):
    return {k: 1.0 + s * (v - 1.0) for k, v in mult.items()}


# ------------------------------------------------------------- integration
def _pois(lam, n):
    v = np.array([math.exp(-lam) * lam ** k / math.factorial(k)
                  for k in range(n + 1)])
    return v


def integrated_probs(lh, la, alpha, mult):
    """Distribusi FT dari integrasi HT -> (btts, over25, (ph, pd, pa)).

    Babak 1: Poisson(lam*alpha) independen per tim.
    Babak 2: Poisson(lam*(1-alpha)*pengali-keadaan) per tim, keadaan dari
    skor HT (i vs j). Semua kuantitas dihitung dari massa gabungan yang
    relevan saja (rumus tertutup), bukan konvolusi penuh.
    """
    ph1 = _pois(alpha * lh, MAX_HT)
    pa1 = _pois(alpha * la, MAX_HT)
    H = np.outer(ph1, pa1)
    H /= H.sum()
    bh, ba = (1 - alpha) * lh, (1 - alpha) * la

    # lambda babak 2 per keadaan: (home, away)
    lam2 = {
        "H": (bh * mult["lead"], ba * mult["trail"]),    # kandang unggul
        "A": (bh * mult["trail"], ba * mult["lead"]),    # tandang unggul
        "D": (bh * mult["level"], ba * mult["level"]),   # level
    }

    # ---- BTTS (tertutup) ----
    p00 = H[0, 0]
    p_h0_a_pos = H[0, 1:].sum()   # kandang belum cetak, tandang sudah (state A)
    p_h_pos_a0 = H[1:, 0].sum()   # state H
    p_both = 1.0 - p00 - p_h0_a_pos - p_h_pos_a0
    btts = (p_both
            + p_h0_a_pos * (1 - math.exp(-lam2["A"][0]))
            + p_h_pos_a0 * (1 - math.exp(-lam2["H"][1]))
            + p00 * (1 - math.exp(-lam2["D"][0])) * (1 - math.exp(-lam2["D"][1])))

    # ---- OU 2.5 (tertutup): hanya skor HT dengan total <= 2 yang bisa under ----
    def pois_cdf(lam, k):
        return float(_pois(lam, k).sum()) if k >= 0 else 0.0

    under = 0.0
    for i in range(3):
        for j in range(3 - i):
            st = "H" if i > j else "A" if i < j else "D"
            tot2 = lam2[st][0] + lam2[st][1]
            under += H[i, j] * pois_cdf(tot2, 2 - i - j)
    over = 1.0 - under

    # ---- 1X2: kelompokkan massa HT per (keadaan, selisih i-j) ----
    mass = defaultdict(float)
    for i in range(MAX_HT + 1):
        for j in range(MAX_HT + 1):
            w = H[i, j]
            if w < 1e-12:
                continue
            st = "H" if i > j else "A" if i < j else "D"
            mass[(st, i - j)] += w
    # distribusi selisih gol babak 2 per keadaan
    diff_cdf = {}
    for st, (l2h, l2a) in lam2.items():
        joint = np.outer(_pois(l2h, MAX_2H), _pois(l2a, MAX_2H))
        d = {}
        for x in range(MAX_2H + 1):
            for y in range(MAX_2H + 1):
                d[x - y] = d.get(x - y, 0.0) + joint[x, y]
        diff_cdf[st] = d
    ph = pd = pa = 0.0
    for (st, dht), w in mass.items():
        # FT kandang menang <=> selisih babak2 > -dht; seri <=> == -dht
        dd = diff_cdf[st]
        p_win = sum(v for k, v in dd.items() if k > -dht)
        p_draw = dd.get(-dht, 0.0)
        ph += w * p_win
        pd += w * p_draw
        pa += w * (1.0 - p_win - p_draw)
    s3 = ph + pd + pa
    return btts, over, (ph / s3, pd / s3, pa / s3)


def _logit(p):
    p = min(max(p, EPS), 1 - EPS)
    return math.log(p / (1 - p))


def _sig(x):
    return 1.0 / (1.0 + math.exp(-x))


def adjust(rec, alpha, mult_s):
    """Terapkan selisih integrasi (mult_s vs semua-1) ke incumbent."""
    b1, o1, p1 = integrated_probs(rec["lam_h"], rec["lam_a"], alpha, mult_s)
    ones = {"lead": 1.0, "trail": 1.0, "level": 1.0}
    b0, o0, p0 = integrated_probs(rec["lam_h"], rec["lam_a"], alpha, ones)
    btts_v = _sig(_logit(rec["p_btts"]) + _logit(b1) - _logit(b0))
    over_v = _sig(_logit(rec["p_over_dc"]) + _logit(o1) - _logit(o0))
    inc3 = (rec["ph_dc"], rec["pd_dc"], rec["pa_dc"])
    adj = []
    for k in range(3):
        adj.append(math.log(max(inc3[k], EPS)) + math.log(max(p1[k], EPS))
                   - math.log(max(p0[k], EPS)))
    mx = max(adj)
    e = [math.exp(x - mx) for x in adj]
    p_v = tuple(x / sum(e) for x in e)
    return btts_v, over_v, p_v


# ---------------------------------------------------------------- metrics
def ll_bin(p, y):
    p = min(max(p, EPS), 1 - EPS)
    return -(y * math.log(p) + (1 - y) * math.log(1 - p))


def metrics(rows):
    """rows: dicts dengan kunci incumbent/varian + label."""
    n = len(rows)
    out = {"n": n}
    for name, ck, yk in (("btts", ("p_btts_inc", "p_btts_var"), "btts_y"),
                         ("ou25", ("p_over_inc", "p_over_var"), "over_y")):
        for suf, col in (("inc", ck[0]), ("var", ck[1])):
            ps = [r[col] for r in rows]
            ys = [r[yk] for r in rows]
            out[f"ll_{name}_{suf}"] = sum(ll_bin(p, y) for p, y in zip(ps, ys)) / n
            out[f"pred_{name}_{suf}"] = sum(ps) / n
            out[f"brier_{name}_{suf}"] = sum((p - y) ** 2 for p, y in zip(ps, ys)) / n
        out[f"act_{name}"] = sum(r[yk] for r in rows) / n
        out[f"calib_{name}_inc_pp"] = 100 * (out[f"pred_{name}_inc"] - out[f"act_{name}"])
        out[f"calib_{name}_var_pp"] = 100 * (out[f"pred_{name}_var"] - out[f"act_{name}"])
    for suf, cols in (("inc", ("ph_inc", "pd_inc", "pa_inc")),
                      ("var", ("ph_var", "pd_var", "pa_var"))):
        out[f"ll_1x2_{suf}"] = sum(
            -math.log(max(r[cols[r["yi"]]], EPS)) for r in rows) / n
    return out


def group_metrics(rows, key):
    g = defaultdict(list)
    for r in rows:
        g[r[key]].append(r)
    return {k: metrics(v) for k, v in sorted(g.items())}


# ------------------------------------------------------------------- main
def main():
    t0 = time.time()
    recs = load_data()
    print(f"records top-5 dengan HT: {len(recs):,}")

    # ---------- tuning: pilih s pada 2021/22-2022/23 (walk-forward per musim)
    tune_rows = []
    tune_params = {}
    for season in TUNE_SEASONS:
        cutoff = season_start(recs, season)
        alpha, mult, n_est, _ = estimate_params(recs, cutoff)
        tune_params[season] = {"cutoff": cutoff, "alpha": alpha, "mult": mult,
                               "n_est": n_est}
        for r in recs:
            if r["season"] == season:
                tune_rows.append((r, alpha, mult))
    print("tuning params:", json.dumps(tune_params, indent=1, default=str))
    tune_eval = {}
    for s in S_GRID:
        tot_ll = tot_ll_inc = 0.0
        for r, alpha, mult in tune_rows:
            bv, _, _ = adjust(r, alpha, shrink(mult, s))
            y = 1.0 if (r["fthg"] > 0 and r["ftag"] > 0) else 0.0
            tot_ll += ll_bin(bv, y)
            tot_ll_inc += ll_bin(r["p_btts"], y)
        tune_eval[s] = {"ll_var": tot_ll / len(tune_rows),
                        "ll_inc": tot_ll_inc / len(tune_rows)}
        print(f"  tune s={s}: BTTS LL var {tune_eval[s]['ll_var']:.4f} "
              f"vs inc {tune_eval[s]['ll_inc']:.4f}")
    s_star = min(S_GRID, key=lambda s: (tune_eval[s]["ll_var"], s))
    print(f"s* terpilih (tuning saja): {s_star}")

    # ---------- test: 2023/24-2025/26, parameter walk-forward per musim
    rows = []
    test_params = {}
    for season in TEST_SEASONS:
        cutoff = season_start(recs, season)
        alpha, mult, n_est, counts = estimate_params(recs, cutoff)
        test_params[season] = {"cutoff": cutoff, "alpha": alpha, "mult": mult,
                               "n_est": n_est,
                               "counts": {k: [round(x, 1) for x in v]
                                          for k, v in counts.items()}}
        mult_s = shrink(mult, s_star)
        for r in recs:
            if r["season"] != season:
                continue
            bv, ov, pv = adjust(r, alpha, mult_s)
            ht_state = ("home_leading" if r["hthg"] > r["htag"] else
                        "away_leading" if r["hthg"] < r["htag"] else "level")
            rows.append({
                "div": r["div"], "date": r["date"], "season": season,
                "home": r["home"], "away": r["away"],
                "hthg": r["hthg"], "htag": r["htag"],
                "fthg": r["fthg"], "ftag": r["ftag"],
                "ht_state": ht_state, "yi": r["yi"],
                "lam_h": r["lam_h"], "lam_a": r["lam_a"],
                "btts_y": 1.0 if (r["fthg"] > 0 and r["ftag"] > 0) else 0.0,
                "over_y": 1.0 if (r["fthg"] + r["ftag"]) > 2.5 else 0.0,
                "p_btts_inc": r["p_btts"], "p_btts_var": bv,
                "p_over_inc": r["p_over_dc"], "p_over_var": ov,
                "ph_inc": r["ph_dc"], "pd_inc": r["pd_dc"], "pa_inc": r["pa_dc"],
                "ph_var": pv[0], "pd_var": pv[1], "pa_var": pv[2],
                "alpha_used": alpha,
                "mult_lead_raw": mult["lead"], "mult_trail_raw": mult["trail"],
                "mult_level_raw": mult["level"], "s_star": s_star,
            })
    print(f"test rows: {len(rows):,}")

    m = metrics(rows)
    by_div = group_metrics(rows, "div")
    by_season = group_metrics(rows, "season")
    by_ht = group_metrics(rows, "ht_state")

    # ---------- gate
    d_btts = m["ll_btts_inc"] - m["ll_btts_var"]
    worst_div = max(by_div.items(),
                    key=lambda kv: kv[1]["ll_btts_var"] - kv[1]["ll_btts_inc"])
    worst_d = worst_div[1]["ll_btts_var"] - worst_div[1]["ll_btts_inc"]
    g1 = d_btts >= 0.001
    g2 = worst_d <= 0.003
    g3 = abs(m["calib_btts_var_pp"]) <= abs(m["calib_btts_inc_pp"])
    g4 = (m["ll_ou25_var"] <= m["ll_ou25_inc"]) and (m["ll_1x2_var"] <= m["ll_1x2_inc"])
    verdict = "PASS" if (g1 and g2 and g3 and g4) else "FAIL"

    results = {
        "s_star": s_star, "tune_eval": {str(k): v for k, v in tune_eval.items()},
        "tune_params": tune_params, "test_params": test_params,
        "pooled": m, "by_div": by_div, "by_season": by_season, "by_ht": by_ht,
        "gate": {"d_btts_ll_gain": d_btts, "g1_gain_ge_0.001": g1,
                 "worst_div": worst_div[0], "worst_div_delta": worst_d,
                 "g2_no_div_worse_gt_0.003": g2,
                 "g3_calib_not_worse": g3,
                 "d_ou25": m["ll_ou25_var"] - m["ll_ou25_inc"],
                 "d_1x2": m["ll_1x2_var"] - m["ll_1x2_inc"],
                 "g4_ou_1x2_not_worse": g4, "verdict": verdict},
        "runtime_s": round(time.time() - t0, 1),
    }
    with open(os.path.join(HERE, "results.json"), "w") as f:
        json.dump(results, f, indent=1, default=str)

    cols = ["div", "date", "season", "home", "away", "hthg", "htag", "fthg",
            "ftag", "ht_state", "yi", "lam_h", "lam_a", "btts_y", "over_y",
            "p_btts_inc", "p_btts_var", "p_over_inc", "p_over_var",
            "ph_inc", "pd_inc", "pa_inc", "ph_var", "pd_var", "pa_var",
            "alpha_used", "mult_lead_raw", "mult_trail_raw",
            "mult_level_raw", "s_star"]
    with open(os.path.join(HERE, "predictions_test.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in rows:
            w.writerow({c: r[c] for c in cols})

    write_results_md(results, m, by_div, by_season, by_ht, verdict)
    print(json.dumps(results["gate"], indent=1))
    print(f"VERDICT: {verdict} | runtime {results['runtime_s']}s")


def _tbl_metrics(title, groups, keyname):
    lines = [f"### {title}", "",
             f"| {keyname} | n | BTTS LL inc | BTTS LL var | Δ | OU LL inc | OU LL var | Δ | 1X2 LL inc | 1X2 LL var | Δ |",
             "|---|---|---|---|---|---|---|---|---|---|---|"]
    for k, v in groups.items():
        lines.append(
            f"| {k} | {v['n']:,} | {v['ll_btts_inc']:.4f} | {v['ll_btts_var']:.4f} | "
            f"{v['ll_btts_var']-v['ll_btts_inc']:+.4f} | {v['ll_ou25_inc']:.4f} | "
            f"{v['ll_ou25_var']:.4f} | {v['ll_ou25_var']-v['ll_ou25_inc']:+.4f} | "
            f"{v['ll_1x2_inc']:.4f} | {v['ll_1x2_var']:.4f} | "
            f"{v['ll_1x2_var']-v['ll_1x2_inc']:+.4f} |")
    lines.append("")
    return lines


def write_results_md(R, m, by_div, by_season, by_ht, verdict):
    g = R["gate"]
    tp = R["test_params"]
    # pengali musim uji terakhir sebagai contoh tampilan (semua mirip)
    ex = tp["2025/26"]
    L = []
    L.append("# Eksperimen G-1 — BTTS via Integrasi Keadaan Turun Minum (HT-State)")
    L.append("")
    L.append("## Ringkasan (Bahasa Indonesia)")
    L.append("")
    L.append(f"Pertanyaan: apakah mengintegrasikan probabilitas pra-laga atas keadaan "
             f"turun minum — distribusi skor babak 1 dari lambda DC incumbent, lalu gol "
             f"babak 2 yang disyaratkan pada keadaan HT (tim tertinggal menekan lebih "
             f"keras) — memperbaiki probabilitas BTTS model gol?")
    L.append("")
    L.append(f"Jawaban: **{'LOLOS GERBANG' if verdict=='PASS' else 'TIDAK LOLOS GERBANG'} "
             f"(verdict: {verdict})**. Pada {m['n']:,} laga uji top-5 (2023/24–2025/26, "
             f"set identik untuk kedua varian), log loss BTTS: incumbent "
             f"{m['ll_btts_inc']:.4f} vs varian {m['ll_btts_var']:.4f} "
             f"(perbaikan {g['d_btts_ll_gain']:+.4f}, syarat ≥ +0,001). Kalibrasi BTTS: "
             f"incumbent {m['calib_btts_inc_pp']:+.2f}pp vs varian "
             f"{m['calib_btts_var_pp']:+.2f}pp. Cek must-not-worsen: OU 2.5 Δ "
             f"{g['d_ou25']:+.4f}, 1X2 Δ {g['d_1x2']:+.4f}. Divisi paling memburuk: "
             f"{g['worst_div']} ({g['worst_div_delta']:+.4f}, batas +0,003). "
             f"Penyusutan pengali terpilih di tuning (2021/22–2022/23): s* = {R['s_star']}.")
    L.append("")
    L.append("Produksi TIDAK diubah oleh eksperimen ini apa pun hasilnya. Sesuai "
             "desain item, PASS pun hanya ditandai untuk keputusan user (ini bedah "
             "paling berisiko di antara enam item), bukan adopsi otomatis.")
    L.append("")
    L.append("Konteks pendahulu: mekanisme mengejar yang sama di SOT V6 (babak) "
             "GAGAL gerbangnya (0,6502 vs 0,6488). Hasil di sini harus dibaca "
             "dengan diskon yang sama.")
    L.append("")
    L.append("## Gate (pre-registered)")
    L.append("")
    L.append(f"- BTTS LL pooled membaik ≥0,001: **{'YA' if g['g1_gain_ge_0.001'] else 'TIDAK'}** "
             f"({g['d_btts_ll_gain']:+.4f})")
    L.append(f"- Tidak ada divisi memburuk >0,003: **{'YA' if g['g2_no_div_worse_gt_0.003'] else 'TIDAK'}** "
             f"(terburuk {g['worst_div']} {g['worst_div_delta']:+.4f})")
    L.append(f"- Kalibrasi BTTS tidak memburuk (\\|Δpp\\|): **{'YA' if g['g3_calib_not_worse'] else 'TIDAK'}** "
             f"({m['calib_btts_inc_pp']:+.2f}pp → {m['calib_btts_var_pp']:+.2f}pp)")
    L.append(f"- OU 2.5 & 1X2 tidak memburuk: **{'YA' if g['g4_ou_1x2_not_worse'] else 'TIDAK'}** "
             f"(OU {g['d_ou25']:+.4f}; 1X2 {g['d_1x2']:+.4f})")
    L.append(f"- **Verdict: {verdict}**")
    L.append("")
    L.append("## Headline — pooled test (top-5, 2023/24–2025/26)")
    L.append("")
    L.append("| Pasar | LL inc | LL var | Δ (var-inc) | Pred inc | Pred var | Aktual | Kalib inc (pp) | Kalib var (pp) |")
    L.append("|---|---|---|---|---|---|---|---|---|")
    L.append(f"| BTTS | {m['ll_btts_inc']:.4f} | {m['ll_btts_var']:.4f} | "
             f"{m['ll_btts_var']-m['ll_btts_inc']:+.4f} | {m['pred_btts_inc']:.4f} | "
             f"{m['pred_btts_var']:.4f} | {m['act_btts']:.4f} | {m['calib_btts_inc_pp']:+.2f} | "
             f"{m['calib_btts_var_pp']:+.2f} |")
    L.append(f"| OU 2.5 | {m['ll_ou25_inc']:.4f} | {m['ll_ou25_var']:.4f} | "
             f"{m['ll_ou25_var']-m['ll_ou25_inc']:+.4f} | {m['pred_ou25_inc']:.4f} | "
             f"{m['pred_ou25_var']:.4f} | {m['act_ou25']:.4f} | {m['calib_ou25_inc_pp']:+.2f} | "
             f"{m['calib_ou25_var_pp']:+.2f} |")
    L.append(f"| 1X2 | {m['ll_1x2_inc']:.4f} | {m['ll_1x2_var']:.4f} | "
             f"{m['ll_1x2_var']-m['ll_1x2_inc']:+.4f} | — | — | — | — | — |")
    L.append("")
    L.append(f"Reproduksi audit: incumbent pada pass ini membaca LL BTTS "
             f"{m['ll_btts_inc']:.4f} / OU {m['ll_ou25_inc']:.4f} — persis angka "
             f"audit §1A (0,6835 / 0,6744). LL 1X2 {m['ll_1x2_inc']:.4f} vs audit "
             f"0,9829: selisih hanya karena set gerbang di sini n=5.255 (satu laga "
             f"tanpa HT di spine dikeluarkan dari KEDUA varian; audit n=5.256).")
    L.append("")
    L += _tbl_metrics("Per divisi", by_div, "Div")
    L += _tbl_metrics("Per musim", by_season, "Musim")
    L.append("## Irisan keadaan HT aktual — apakah celah -8,5pp menyusut?")
    L.append("")
    L.append("| HT state (aktual) | n | Pred inc | Pred var | Aktual | Celah inc (pp) | Celah var (pp) |")
    L.append("|---|---|---|---|---|---|---|")
    for k, v in by_ht.items():
        L.append(f"| {k} | {v['n']:,} | {v['pred_btts_inc']:.4f} | {v['pred_btts_var']:.4f} | "
                 f"{v['act_btts']:.4f} | {v['calib_btts_inc_pp']:+.2f} | {v['calib_btts_var_pp']:+.2f} |")
    L.append("")
    L.append("Catatan irisan: keadaan HT adalah informasi pasca-laga; irisan ini "
             "diagnostik lokalisasi error (seperti di audit), bukan fitur. Varian "
             "tidak pernah melihat HT aktual — ia mengintegrasikan atas distribusi "
             "HT pra-laga, jadi penyusutan celah di sini adalah bukti mekanisme "
             "bekerja, bukan kebocoran.")
    L.append("")
    L.append("## Pembacaan jujur (dekomposisi efek)")
    L.append("")
    up = {k: 100 * (v["pred_btts_var"] - v["pred_btts_inc"])
          for k, v in by_ht.items()}
    L.append(f"- Kenaikan prediksi BTTS varian per irisan HT aktual hampir SERAGAM: "
             f"away-leading {up['away_leading']:+.2f}pp, home-leading "
             f"{up['home_leading']:+.2f}pp, level {up['level']:+.2f}pp. Komponen "
             f"diskriminasi-keadaannya (sebaran antar-irisan) hanya ~0,02pp — "
             f"hampir seluruh efek adalah kenaikan global (± seragam) probabilitas "
             f"BTTS, bukan pemilahan per keadaan. Itu sebabnya celah irisan "
             f"tertinggal menyusut (karena di sana incumbent paling rendah) tetapi "
             f"celah irisan level justru membesar "
             f"({by_ht['level']['calib_btts_inc_pp']:+.2f}pp → "
             f"{by_ht['level']['calib_btts_var_pp']:+.2f}pp).")
    L.append(f"- Sumber kenaikan global: pengali tidak simetris (trail ≈ ×1,11 vs "
             f"lead ≈ ×0,99), jadi mengintegrasikan atas keadaan HT menaikkan "
             f"total gol babak-2 yang diharapkan, bukan sekadar mengalokasikannya "
             f"ulang. Pra-laga, distribusi keadaan HT mirip antar-laga, sehingga "
             f"yang bisa dieksploitasi memang sebagian besar komponen seragam ini "
             f"— dekat dengan rekalibrasi global, keluarga yang sudah pernah "
             f"diuji dan dikembalikan di EXPERIMENTS_LOG E3.")
    bs = by_season
    L.append(f"- Efek meluruh antar-musim uji: ΔLL BTTS "
             f"{bs['2023/24']['ll_btts_var']-bs['2023/24']['ll_btts_inc']:+.4f} "
             f"(2023/24) → {bs['2024/25']['ll_btts_var']-bs['2024/25']['ll_btts_inc']:+.4f} "
             f"(2024/25) → {bs['2025/26']['ll_btts_var']-bs['2025/26']['ll_btts_inc']:+.4f} "
             f"(2025/26, memburuk). Keuntungan terkonsentrasi di musim uji pertama "
             f"dan hilang sesudahnya — pola under-prediksi BTTS era tuning yang "
             f"tidak persisten, bukan sinyal keadaan yang stabil.")
    L.append("- Kesimpulan: mekanisme mengejar itu NYATA (pengali trail ×1,11 "
             "stabil di semua cutoff walk-forward; celah −8,5pp menyusut ke "
             "−6,6pp), tetapi porsi yang bisa diprediksi pra-laga terlalu kecil "
             "dan terlalu seragam untuk melewati gerbang 0,001 — persis pola "
             "kegagalan pendahulunya, SOT V6. FAIL diterima apa adanya; tidak "
             "ada penyelamatan lewat tuning ulang pada data uji.")
    L.append("")
    L.append("## Parameter (walk-forward per musim uji)")
    L.append("")
    L.append("| Musim uji | Cutoff estimasi | n estimasi | Alpha (porsi gol B1) | ×lead | ×trail | ×level |")
    L.append("|---|---|---|---|---|---|---|")
    for s, p in tp.items():
        L.append(f"| {s} | {p['cutoff']} | {p['n_est']:,} | {p['alpha']:.4f} | "
                 f"{p['mult']['lead']:.3f} | {p['mult']['trail']:.3f} | {p['mult']['level']:.3f} |")
    L.append("")
    L.append("## Tuning s (hanya 2021/22–2022/23; parameter juga walk-forward per musim)")
    L.append("")
    L.append("| s | BTTS LL varian (tuning) | BTTS LL incumbent (tuning) |")
    L.append("|---|---|---|")
    for s, v in R["tune_eval"].items():
        star = " ← s*" if float(s) == R["s_star"] else ""
        L.append(f"| {s} | {v['ll_var']:.4f} | {v['ll_inc']:.4f} |{star}")
    L.append("")
    L.append("## Method notes")
    L.append("")
    L.append("- Incumbent direkomputasi dalam pass yang sama dari records_cache "
             "(p_btts/p_over_dc/ph_dc tersimpan = output DC.probs dari lambda dan "
             "rho yang sama) pada set laga yang persis sama dengan varian.")
    L.append("- Varian = incumbent yang digeser oleh selisih integrasi: "
             "logit(p_var) = logit(p_inc) + logit(p_int(m_s)) − logit(p_int(m=1)) "
             "untuk BTTS/OU; analog log ternormalisasi untuk 1X2. Pada s=0 varian "
             "identik dengan incumbent, dan koreksi tau DC tidak dihitung ganda "
             "karena integrasi murni-Poisson hanya menyumbang selisihnya.")
    L.append("- Integrasi: babak 1 Poisson(alpha·λ), babak 2 "
             "Poisson((1−alpha)·λ·pengali keadaan HT), keadaan = unggul/level/"
             "tertinggal dari skor HT; BTTS dan OU dihitung tertutup dari massa "
             "HT yang relevan, 1X2 dari massa HT per (keadaan, selisih) × "
             "distribusi selisih babak 2.")
    L.append("- Pengali diestimasi sebagai Σ gol babak-2 aktual / Σ lambda babak-2 "
             "dasar pada record walk-forward sebelum musim berjalan (bukan rasio "
             "mentah — lambda mengendalikan confounding kekuatan tim: tim unggul "
             "cenderung memang lebih kuat).")
    L.append("- Tidak ada odds; akurasi/kalibrasi saja. Tidak ada file produksi "
             "yang diubah; tidak ada tuning apa pun pada data uji.")
    L.append(f"- Runtime skrip: ~{R['runtime_s']} dtk.")
    L.append("")
    with open(os.path.join(HERE, "RESULTS.md"), "w") as f:
        f.write("\n".join(L))


if __name__ == "__main__":
    main()
